from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from typing import Any

import webview

from .config import AppConfig, load_config
from .devices import ArduinoHub, SystemHub
from .filtering import CodeFilter
from .gemini_client import GeminiService
from .memory import ConversationMemory
from .router import CommandRouter
from .voice import TTSService, WakeWordListener


@dataclass(slots=True)
class RuntimeState:
    listening: bool = False
    last_status: str = "BAĞLANTI TAMAMLANDI, BİLADER."


class BiladerApplication:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.state = RuntimeState()

        self.memory = ConversationMemory(config.memory_db)
        self.filter = CodeFilter()
        self.gemini = GeminiService(
            api_key=config.gemini_api_key,
            model=config.gemini_model,
            temperature=config.gemini_temperature,
        )
        self.tts = TTSService(rate=config.tts_rate, volume=config.tts_volume)
        self.wake_listener = WakeWordListener(config.wake_words)
        self.arduino = ArduinoHub(
            default_port=config.arduino_port,
            default_baud=config.arduino_baud,
            timeout=config.arduino_timeout,
        )
        self.system = SystemHub()
        self.router = CommandRouter()

        self.window: webview.Window | None = None
        self._telemetry_thread: threading.Thread | None = None
        self._stop_telemetry = threading.Event()

    def bind_window(self, window: webview.Window) -> None:
        self.window = window

    def emit(self, event: str, payload: dict[str, Any]) -> None:
        if not self.window:
            return
        packet = json.dumps({"event": event, "payload": payload}, ensure_ascii=False)
        self.window.evaluate_js(f"window.Bilader?.onNativeEvent({packet});")

    def set_status(self, text: str) -> None:
        self.state.last_status = text
        self.emit("status", {"text": text})

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        self.set_status("KONUŞUYOR...")
        self.tts.speak(text)
        self.set_status("BAĞLANTI TAMAMLANDI, BİLADER.")

    def handle_ai_chat(self, prompt: str) -> dict:
        self.set_status("DÜŞÜNÜYOR...")
        self.memory.add("user", prompt)

        history = self.memory.latest(limit=12)
        result = self.gemini.ask(prompt, history)
        filtered = self.filter.split(result.text)

        self.memory.add("assistant", result.text)

        if filtered.spoken:
            self.speak(filtered.spoken)

        if filtered.has_code:
            self.speak("Kodları ekrana bastım bilader, bir bak istersen.")

        return {
            "ok": result.ok,
            "model": result.model,
            "reply": filtered.spoken,
            "code": filtered.code,
            "error": result.error,
        }

    def execute_command(self, utterance: str) -> dict:
        routed = self.router.route(utterance)

        if routed.category == "arduino":
            if routed.intent == "toggle":
                return self.arduino.toggle()
            if routed.intent == "light_on":
                return self.arduino.light_on()
            if routed.intent == "light_off":
                return self.arduino.light_off()
            if routed.intent == "temperature":
                return self.arduino.sensor_temperature()

        if routed.category == "system":
            if routed.intent == "stats":
                return self.system.snapshot()
            if routed.intent == "open_app":
                return self.system.open_application(routed.payload)

        return self.handle_ai_chat(utterance)

    def start_wake_listener(self) -> dict:
        if self.state.listening:
            return {"ok": True, "listening": True}

        self.state.listening = True

        def _on_wake(text: str) -> None:
            self.emit("wake", {"text": text})

        self.wake_listener.start(callback=_on_wake)
        self.set_status("DİNLİYOR...")
        return {"ok": True, "listening": True}

    def stop_wake_listener(self) -> dict:
        if not self.state.listening:
            return {"ok": True, "listening": False}

        self.wake_listener.stop()
        self.state.listening = False
        self.set_status("BAĞLANTI TAMAMLANDI, BİLADER.")
        return {"ok": True, "listening": False}

    def poll_voice_events(self) -> list[dict]:
        events: list[dict] = []
        while True:
            evt = self.wake_listener.poll_event()
            if evt is None:
                break
            events.append({"kind": evt.kind, "payload": evt.payload})
        return events

    def start_telemetry(self) -> None:
        if self._telemetry_thread and self._telemetry_thread.is_alive():
            return

        self._stop_telemetry.clear()

        def _worker() -> None:
            while not self._stop_telemetry.is_set():
                snap = self.system.snapshot()
                self.memory.save_metric("cpu", snap["cpu_percent"])
                self.memory.save_metric("ram", snap["ram_percent"])
                self.emit("telemetry", snap)
                time.sleep(self.config.telemetry_interval)

        self._telemetry_thread = threading.Thread(target=_worker, daemon=True)
        self._telemetry_thread.start()

    def stop_telemetry(self) -> None:
        self._stop_telemetry.set()

    def memory_summary(self) -> dict:
        last = self.memory.latest(limit=20)
        return {
            "count": len(last),
            "latest": [m.__dict__ for m in last],
            "cpu_series": self.memory.metric_series("cpu", limit=90),
            "ram_series": self.memory.metric_series("ram", limit=90),
        }


class ApiBridge:
    def __init__(self, app: BiladerApplication) -> None:
        self.app = app

    def ask(self, prompt: str) -> dict:
        return self.app.handle_ai_chat(prompt)

    def run_command(self, utterance: str) -> dict:
        return self.app.execute_command(utterance)

    def toggle_arduino(self) -> dict:
        return self.app.arduino.toggle()

    def arduino_send(self, payload: str) -> dict:
        return self.app.arduino.send(payload)

    def arduino_temperature(self) -> dict:
        return self.app.arduino.sensor_temperature()

    def arduino_light_on(self) -> dict:
        return self.app.arduino.light_on()

    def arduino_light_off(self) -> dict:
        return self.app.arduino.light_off()

    def list_ports(self) -> list[dict]:
        return self.app.arduino.available_ports()

    def system_snapshot(self) -> dict:
        return self.app.system.snapshot()

    def process_table(self) -> list[dict]:
        return self.app.system.process_table()

    def open_application(self, app_name: str) -> dict:
        return self.app.system.open_application(app_name)

    def memory_summary(self) -> dict:
        return self.app.memory_summary()

    def start_listening(self) -> dict:
        return self.app.start_wake_listener()

    def stop_listening(self) -> dict:
        return self.app.stop_wake_listener()

    def poll_voice_events(self) -> list[dict]:
        return self.app.poll_voice_events()


def create_application() -> BiladerApplication:
    return BiladerApplication(load_config())


def run_desktop() -> None:
    app = create_application()
    issues = app.config.validate()
    if issues:
        raise RuntimeError("\n".join(issues))

    bridge = ApiBridge(app)
    window = webview.create_window(
        title=app.config.app_name,
        url=str(app.config.web_dir / "index.html"),
        js_api=bridge,
        width=app.config.app_width,
        height=app.config.app_height,
    )
    app.bind_window(window)
    app.start_telemetry()
    webview.start(debug=True)
