#!/usr/bin/env python3
"""BİLADER AI v1.1 - Python backend."""
from __future__ import annotations

import json
import os
import queue
import re
import sqlite3
import subprocess
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

try:
    import webview
except Exception:  # pragma: no cover
    webview = None

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover
    sr = None

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None

try:
    import serial
    import serial.tools.list_ports
except Exception:  # pragma: no cover
    serial = None

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None


APP_ROOT = Path(__file__).resolve().parent
WEB_ROOT = APP_ROOT / "web"
DB_PATH = APP_ROOT / "bilader_memory.sqlite3"
ENV_PATH = APP_ROOT / ".env"


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


@dataclass
class ResponsePacket:
    answer: str
    spoken: str
    code_blocks: List[str]
    source: str
    ts: str


class MemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db = db_path
        self._ensure_schema()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db)

    def _ensure_schema(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def add_message(self, role: str, content: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO conversations(role, content, created_at) VALUES (?, ?, ?)",
                (role, content, now_iso()),
            )

    def add_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO events(event_type, payload, created_at) VALUES (?, ?, ?)",
                (event_type, json.dumps(payload, ensure_ascii=False), now_iso()),
            )

    def history(self, limit: int = 20) -> List[Dict[str, str]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        rows.reverse()
        return [{"role": role, "content": content} for role, content in rows]


class CodeFilter:
    """Split code-like snippets from model text for TTS safety."""

    patterns = [
        re.compile(r"```[\s\S]*?```", re.IGNORECASE),
        re.compile(r"<script[\s\S]*?</script>", re.IGNORECASE),
        re.compile(r"<\?php[\s\S]*?\?>", re.IGNORECASE),
        re.compile(r"\b(?:def|class|import|from)\b.+", re.IGNORECASE),
        re.compile(r"\bfor\s+\w+\s+in\s+range\(", re.IGNORECASE),
    ]

    def split(self, text: str) -> Tuple[str, List[str]]:
        codes: List[str] = []
        cleaned = text
        for p in self.patterns:
            def _repl(m: re.Match[str]) -> str:
                codes.append(m.group(0).strip())
                return " [KOD] "

            cleaned = p.sub(_repl, cleaned)
        spoken = re.sub(r"\s+", " ", cleaned).strip()
        spoken = spoken.replace("[KOD]", "Kodları ekrana bastım bilader, bir bak istersen")
        return spoken, codes


class Speaker:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled and pyttsx3 is not None
        self.lock = threading.Lock()
        self.engine = None
        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 182)
                self.engine.setProperty("volume", 1.0)
            except Exception:
                self.enabled = False
                self.engine = None

    def speak(self, text: str) -> None:
        if not text or not self.enabled or not self.engine:
            return
        with self.lock:
            self.engine.say(text)
            self.engine.runAndWait()


class GeminiClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.model_name = model
        self.model = None
        if api_key and genai:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model)
            except Exception:
                self.model = None

    def available(self) -> bool:
        return self.model is not None

    def ask(self, prompt: str, history: List[Dict[str, str]]) -> str:
        if not self.model:
            return "Gemini hazır değil bilader. .env içindeki GEMINI_API_KEY değerini kontrol et."
        system = (
            "Sen BİLADER'sin. Türkçe konuş. Cevaplarını kısa, samimi, çözüm odaklı ver. "
            "Kod varsa kısa anlat; uzun kod blokları basma."
        )
        lines = [system]
        lines += [f"{m['role']}: {m['content']}" for m in history[-10:]]
        lines.append(f"user: {prompt}")
        joined = "\n".join(lines)
        try:
            result = self.model.generate_content(joined)
            text = getattr(result, "text", "")
            return text.strip() or "Şu an net bir cevap üretemedim bilader, tekrar deneyelim."
        except Exception as exc:
            return f"Gemini hatası: {exc}"


class ArduinoHub:
    def __init__(self, port: str = "", baud: int = 9600) -> None:
        self.preferred_port = port
        self.baud = baud
        self.conn = None
        self.lock = threading.Lock()

    def list_ports(self) -> List[str]:
        if not serial:
            return []
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect(self, port: Optional[str] = None) -> Tuple[bool, str]:
        if not serial:
            return False, "pyserial kurulu değil."
        ports = self.list_ports()
        target = port or self.preferred_port or (ports[0] if ports else "")
        if not target:
            return False, "Uygun seri port bulunamadı."
        try:
            with self.lock:
                self.conn = serial.Serial(target, self.baud, timeout=1.5)
            return True, f"Arduino bağlı: {target}"
        except Exception as exc:
            return False, f"Bağlantı hatası: {exc}"

    def disconnect(self) -> str:
        with self.lock:
            if self.conn:
                try:
                    self.conn.close()
                except Exception:
                    pass
            self.conn = None
        return "Arduino bağlantısı kapatıldı."

    def send(self, cmd: str) -> Tuple[bool, str]:
        with self.lock:
            if not self.conn:
                return False, "Arduino bağlı değil."
            try:
                self.conn.write((cmd + "\n").encode("utf-8"))
                time.sleep(0.15)
                out = self.conn.readline().decode("utf-8", errors="ignore").strip()
                return True, out or "ok"
            except Exception as exc:
                return False, f"Seri iletişim hatası: {exc}"


class SystemControl:
    @staticmethod
    def open_app(name: str) -> str:
        try:
            if os.name == "nt":
                if name == "spotify":
                    os.startfile("spotify")  # type: ignore[attr-defined]
                elif name == "calculator":
                    subprocess.Popen(["calc"])
            else:
                if name == "spotify":
                    subprocess.Popen(["spotify"])
                elif name == "calculator":
                    subprocess.Popen(["gnome-calculator"])
            return f"{name} açılıyor bilader."
        except Exception as exc:
            return f"{name} açılamadı: {exc}"

    @staticmethod
    def snapshot() -> Dict[str, Any]:
        if not psutil:
            return {
                "cpu": 0,
                "ram_percent": 0,
                "disk_percent": 0,
                "ram_used_gb": 0,
                "ram_total_gb": 0,
                "disk_used_gb": 0,
                "disk_total_gb": 0,
                "ts": now_iso(),
            }
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return {
            "cpu": psutil.cpu_percent(interval=0.2),
            "ram_percent": vm.percent,
            "disk_percent": disk.percent,
            "ram_used_gb": round(vm.used / 1024**3, 2),
            "ram_total_gb": round(vm.total / 1024**3, 2),
            "disk_used_gb": round(disk.used / 1024**3, 2),
            "disk_total_gb": round(disk.total / 1024**3, 2),
            "ts": now_iso(),
        }


class LocalCommandRouter:
    def __init__(self, arduino: ArduinoHub) -> None:
        self.arduino = arduino

    def route(self, text: str) -> Optional[str]:
        t = text.lower().strip()

        if "arduino" in t and "bağ" in t:
            ok, msg = self.arduino.connect()
            return msg
        if "arduino" in t and ("kes" in t or "kapat" in t):
            return self.arduino.disconnect()
        if "ışığı yak" in t:
            ok, msg = self.arduino.send("L1")
            return "Işık açma komutu gönderildi." if ok else msg
        if "ışığı kapat" in t:
            ok, msg = self.arduino.send("L0")
            return "Işık kapatma komutu gönderildi." if ok else msg
        if "sıcaklık" in t:
            ok, msg = self.arduino.send("T")
            return f"Sıcaklık: {msg}" if ok else msg

        if "spotify" in t and "aç" in t:
            return SystemControl.open_app("spotify")
        if "hesap makinesi" in t and "aç" in t:
            return SystemControl.open_app("calculator")
        if "cpu" in t or "ram" in t or "disk" in t:
            s = SystemControl.snapshot()
            return f"CPU %{s['cpu']:.1f}, RAM %{s['ram_percent']:.1f}, Disk %{s['disk_percent']:.1f}."

        if "bilgisayarı kapat" in t:
            return "Güvenlik nedeniyle kapatma komutu onay olmadan çalıştırılmadı bilader."
        return None


class VoiceLoop(threading.Thread):
    def __init__(self, callback, stop_event: threading.Event) -> None:
        super().__init__(daemon=True)
        self.callback = callback
        self.stop_event = stop_event
        self.active = True

    def run(self) -> None:
        if sr is None:
            return
        rec = sr.Recognizer()
        mic = sr.Microphone()
        wake = ("hey bilader", "bilader")

        with mic as source:
            rec.adjust_for_ambient_noise(source, duration=0.8)

        while not self.stop_event.is_set():
            if not self.active:
                time.sleep(0.2)
                continue
            try:
                with mic as source:
                    audio = rec.listen(source, timeout=2, phrase_time_limit=6)
                heard = rec.recognize_google(audio, language="tr-TR").lower().strip()
                if any(w in heard for w in wake):
                    query = heard
                    for w in wake:
                        query = query.replace(w, "")
                    self.callback(query.strip() or "selam")
            except Exception:
                time.sleep(0.1)


class BiladerCore:
    def __init__(self) -> None:
        load_dotenv(ENV_PATH)
        self.memory = MemoryStore(DB_PATH)
        self.filter = CodeFilter()
        self.speaker = Speaker(enabled=os.getenv("ENABLE_TTS", "1") == "1")
        self.gemini = GeminiClient(
            os.getenv("GEMINI_API_KEY", ""),
            os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        )
        self.arduino = ArduinoHub(
            os.getenv("ARDUINO_PORT", ""), int(os.getenv("ARDUINO_BAUD", "9600"))
        )
        self.router = LocalCommandRouter(self.arduino)
        self.stop_event = threading.Event()
        self.voice = VoiceLoop(self.process_input, self.stop_event)
        self.events: "queue.Queue[Dict[str, Any]]" = queue.Queue()

    def start(self) -> None:
        self.voice.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.arduino.disconnect()

    def process_input(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        if not text:
            return {"ok": False, "error": "Boş komut"}

        self.memory.add_message("user", text)
        self.memory.add_event("user_input", {"text": text})

        response = self.router.route(text)
        source = "local"
        if response is None:
            source = "gemini"
            response = self.gemini.ask(text, self.memory.history(20))

        spoken, code = self.filter.split(response)
        self.speaker.speak(spoken)

        packet = ResponsePacket(
            answer=response,
            spoken=spoken,
            code_blocks=code,
            source=source,
            ts=now_iso(),
        )
        self.memory.add_message("assistant", response)
        payload = asdict(packet)
        self.events.put({"type": "assistant_response", "payload": payload})
        return {"ok": True, **payload}


class ApiBridge:
    def __init__(self, core: BiladerCore):
        self.core = core

    def ask(self, text: str) -> Dict[str, Any]:
        return self.core.process_input(text)

    def get_system_status(self) -> Dict[str, Any]:
        snap = SystemControl.snapshot()
        self.core.memory.add_event("system_status", snap)
        return snap

    def list_devices(self) -> Dict[str, Any]:
        ports = self.core.arduino.list_ports()
        bt = ["Bilader-Headset", "Bilader-Phone"]
        return {"usb": ports, "bluetooth": bt}

    def toggle_arduino(self) -> Dict[str, Any]:
        if self.core.arduino.conn:
            return {"ok": True, "message": self.core.arduino.disconnect(), "connected": False}
        ok, msg = self.core.arduino.connect()
        return {"ok": ok, "message": msg, "connected": ok}

    def get_memory(self) -> List[Dict[str, str]]:
        return self.core.memory.history(30)

    def set_listening(self, active: bool) -> Dict[str, Any]:
        self.core.voice.active = bool(active)
        return {"ok": True, "listening": self.core.voice.active}

    def get_health(self) -> Dict[str, Any]:
        return {
            "gemini": self.core.gemini.available(),
            "tts": self.core.speaker.enabled,
            "stt": sr is not None,
            "arduino_connected": self.core.arduino.conn is not None,
            "ts": now_iso(),
        }


def run_app() -> None:
    if webview is None:
        raise RuntimeError("pywebview kurulu değil. requirements.txt yükleyin.")

    core = BiladerCore()
    api = ApiBridge(core)

    win = webview.create_window(
        title="BİLADER AI v1.1",
        url=str(WEB_ROOT / "index.html"),
        js_api=api,
        width=1460,
        height=920,
        min_size=(1000, 700),
        background_color="#050505",
    )

    def push_events() -> None:
        while not core.stop_event.is_set():
            try:
                event = core.events.get(timeout=0.3)
            except queue.Empty:
                continue
            js = (
                "window.BiladerUI && window.BiladerUI.receivePythonEvent(" +
                json.dumps(event, ensure_ascii=False) +
                ");"
            )
            try:
                win.evaluate_js(js)
            except Exception:
                pass

    threading.Thread(target=push_events, daemon=True).start()
    core.start()

    try:
        webview.start(debug=True)
    finally:
        core.stop()


if __name__ == "__main__":
    run_app()
