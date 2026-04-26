#!/usr/bin/env python3
"""
BİLADER AI v1.0
Jarvis tarzında, yerel dokunuşa sahip Türkçe sesli masaüstü asistan.
"""
from __future__ import annotations

import json
import os
import queue
import random
import re
import sqlite3
import subprocess
import threading
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import webview
except Exception:  # pragma: no cover
    webview = None

try:
    import pyttsx3
except Exception:  # pragma: no cover
    pyttsx3 = None

try:
    import serial
    import serial.tools.list_ports
except Exception:  # pragma: no cover
    serial = None

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None

try:
    import speech_recognition as sr
except Exception:  # pragma: no cover
    sr = None

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None

APP_ROOT = Path(__file__).resolve().parent
WEB_ROOT = APP_ROOT / "web"
DB_PATH = APP_ROOT / "bilader_memory.sqlite3"
ENV_PATH = APP_ROOT / ".env"


def load_env(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


@dataclass
class SystemSnapshot:
    cpu: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    timestamp: str


class MemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._initialize()

    def _initialize(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def append_conversation(self, role: str, content: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO conversations (role, content, created_at) VALUES (?, ?, ?)",
            (role, content, datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()

    def append_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (event_type, payload, created_at) VALUES (?, ?, ?)",
            (event_type, json.dumps(payload, ensure_ascii=False), datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()

    def latest_conversation(self, limit: int = 15) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT role, content, created_at FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        conn.close()
        rows.reverse()
        return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]


class CodeFilter:
    CODE_PATTERNS = [
        r"```[\s\S]*?```",
        r"<script[\s\S]*?</script>",
        r"<\?php[\s\S]*?\?>",
        r"\bfor\s+\w+\s+in\s+range\s*\(",
        r"\bdef\s+\w+\s*\(",
        r"\bclass\s+\w+\s*[:(]",
        r"\bimport\s+\w+",
        r"\bconsole\.log\(",
    ]

    def __init__(self) -> None:
        self.combined = re.compile("|".join(f"({p})" for p in self.CODE_PATTERNS), re.IGNORECASE)

    def split_for_tts(self, text: str) -> Tuple[str, List[str]]:
        blocks: List[str] = []

        def repl(match: re.Match[str]) -> str:
            snippet = match.group(0)
            blocks.append(snippet)
            return " [KOD_BLOĞU] "

        spoken = self.combined.sub(repl, text)
        return spoken, blocks


class Speaker:
    def __init__(self) -> None:
        self.engine = None
        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 185)
                self.engine.setProperty("volume", 1.0)
            except Exception:
                self.engine = None
        self.lock = threading.Lock()

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        if not self.engine:
            print(f"[TTS disabled] {text}")
            return
        with self.lock:
            self.engine.say(text)
            self.engine.runAndWait()


class GeminiBrain:
    def __init__(self, api_key: Optional[str], model_name: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.model = None
        if api_key and genai:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
            except Exception as exc:
                print(f"Gemini başlatılamadı: {exc}")

    def ask(self, prompt: str, history: List[Dict[str, Any]]) -> str:
        if not self.model:
            return (
                "Gemini bağlantısı hazır değil bilader. .env içindeki GEMINI_API_KEY değerini kontrol et. "
                "Bu arada yerel modda çalışıp komutları yine çözebilirim."
            )

        context_lines = [
            "Sen BİLADER'sin. Türkçe konuş, samimi ama profesyonel ol.",
            "Cevapların kısa ve hızlı olsun.",
            "Kod varsa düz metin anlatımı yap, uzun kod dökümü verme.",
        ]
        for item in history[-8:]:
            context_lines.append(f"{item['role']}: {item['content']}")
        context_lines.append(f"kullanıcı: {prompt}")
        joined = "\n".join(context_lines)
        try:
            response = self.model.generate_content(joined)
            text = getattr(response, "text", "")
            return text.strip() or "Kısa bir bağlantı sorunu oldu bilader, tekrar dener misin?"
        except Exception as exc:
            return f"Gemini hatası: {exc}"


class ArduinoManager:
    def __init__(self, preferred_port: Optional[str] = None, baudrate: int = 9600) -> None:
        self.preferred_port = preferred_port
        self.baudrate = baudrate
        self.ser = None
        self.lock = threading.Lock()

    def list_ports(self) -> List[str]:
        if not serial:
            return []
        return [p.device for p in serial.tools.list_ports.comports()]

    def connect(self, explicit_port: Optional[str] = None) -> Tuple[bool, str]:
        if not serial:
            return False, "pyserial kurulu değil."
        port = explicit_port or self.preferred_port
        ports = self.list_ports()
        if not ports:
            return False, "Seri port bulunamadı."
        if not port:
            port = ports[0]
        try:
            with self.lock:
                self.ser = serial.Serial(port, self.baudrate, timeout=2)
            return True, f"Arduino bağlandı: {port}"
        except Exception as exc:
            return False, f"Arduino bağlantı hatası: {exc}"

    def disconnect(self) -> str:
        with self.lock:
            if self.ser:
                try:
                    self.ser.close()
                except Exception:
                    pass
            self.ser = None
        return "Arduino bağlantısı kapatıldı."

    def send(self, payload: str) -> Tuple[bool, str]:
        with self.lock:
            if not self.ser:
                return False, "Arduino bağlı değil."
            try:
                self.ser.write((payload + "\n").encode("utf-8"))
                time.sleep(0.15)
                resp = self.ser.readline().decode("utf-8", errors="ignore").strip()
                return True, resp or "ok"
            except Exception as exc:
                return False, f"Seri yazma hatası: {exc}"


class CommandRouter:
    def __init__(self, arduino: ArduinoManager):
        self.arduino = arduino

    def try_handle(self, text: str) -> Optional[str]:
        normalized = text.lower().strip()
        if "arduino'ya bağlan" in normalized or "arduinoya bağlan" in normalized:
            ok, msg = self.arduino.connect()
            return msg
        if "arduino bağlantısını kes" in normalized:
            return self.arduino.disconnect()
        if "ışığı yak" in normalized:
            ok, msg = self.arduino.send("L1")
            return "Işık komutu gönderildi." if ok else msg
        if "ışığı kapat" in normalized:
            ok, msg = self.arduino.send("L0")
            return "Işık kapatma komutu gönderildi." if ok else msg
        if "sıcaklık" in normalized:
            ok, msg = self.arduino.send("T")
            return f"Oda sıcaklığı: {msg}" if ok else msg
        if "spotify" in normalized and "aç" in normalized:
            return self._open_app("spotify")
        if "hesap makinesi" in normalized and "aç" in normalized:
            return self._open_app("calculator")
        if "ekranı kapat" in normalized:
            return "Ekranı kapatma komutu güvenlik nedeniyle simülasyon modunda işlendi."
        if "bilgisayarı kapat" in normalized:
            return "Bu komut onay gerektirir bilader. Güvenlik için otomatik kapatma yapmadım."
        return None

    def _open_app(self, app_name: str) -> str:
        try:
            if os.name == "nt":
                if app_name == "spotify":
                    os.startfile("spotify")  # type: ignore[attr-defined]
                else:
                    subprocess.Popen(["calc"])
            elif os.name == "posix":
                if app_name == "spotify":
                    subprocess.Popen(["spotify"])
                else:
                    subprocess.Popen(["gnome-calculator"])
            return f"{app_name} açılıyor bilader."
        except Exception as exc:
            return f"{app_name} açılamadı: {exc}"


class VoiceListener(threading.Thread):
    def __init__(self, on_text, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.on_text = on_text
        self.stop_event = stop_event
        self.enabled = sr is not None

    def run(self) -> None:
        if not self.enabled:
            print("SpeechRecognition kurulu değil, sesli dinleme pasif.")
            return
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        wake_words = ("hey bilader", "bilader")

        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)

        while not self.stop_event.is_set():
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=6)
                heard = recognizer.recognize_google(audio, language="tr-TR").lower()
                if any(word in heard for word in wake_words):
                    cleaned = heard.replace("hey bilader", "").replace("bilader", "").strip()
                    self.on_text(cleaned or "selam")
            except Exception:
                time.sleep(0.1)


class BiladerCore:
    def __init__(self) -> None:
        env = load_env(ENV_PATH)
        self.memory = MemoryStore(DB_PATH)
        self.filter = CodeFilter()
        self.speaker = Speaker()
        self.brain = GeminiBrain(env.get("GEMINI_API_KEY"), env.get("GEMINI_MODEL", "gemini-2.5-flash"))
        self.arduino = ArduinoManager(env.get("ARDUINO_PORT"), int(env.get("ARDUINO_BAUD", "9600")))
        self.router = CommandRouter(self.arduino)
        self.stop_event = threading.Event()
        self.voice_listener = VoiceListener(self.process_user_input, self.stop_event)
        self.ui_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()

    def start(self) -> None:
        self.voice_listener.start()

    def shutdown(self) -> None:
        self.stop_event.set()
        self.arduino.disconnect()

    def system_snapshot(self) -> SystemSnapshot:
        if not psutil:
            return SystemSnapshot(0, 0, 0, 0, 0, 0, 0, datetime.utcnow().isoformat())
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        return SystemSnapshot(
            cpu=psutil.cpu_percent(interval=0.2),
            ram_percent=vm.percent,
            ram_used_gb=vm.used / (1024**3),
            ram_total_gb=vm.total / (1024**3),
            disk_percent=disk.percent,
            disk_used_gb=disk.used / (1024**3),
            disk_total_gb=disk.total / (1024**3),
            timestamp=datetime.utcnow().isoformat(),
        )

    def process_user_input(self, user_text: str) -> Dict[str, Any]:
        user_text = user_text.strip()
        if not user_text:
            return {"ok": False, "answer": "Seni duyamadım bilader, tekrar eder misin?"}

        self.memory.append_conversation("user", user_text)
        self.memory.append_event("voice_or_text_input", {"text": user_text})

        local_answer = self.router.try_handle(user_text)
        if local_answer is None:
            history = self.memory.latest_conversation(12)
            local_answer = self.brain.ask(user_text, history)

        spoken, code_blocks = self.filter.split_for_tts(local_answer)
        spoken = spoken.replace("[KOD_BLOĞU]", "Kodları ekrana bastım bilader, bir bak istersen.")
        self.speaker.speak(spoken)

        self.memory.append_conversation("assistant", local_answer)
        payload = {
            "ok": True,
            "answer": local_answer,
            "spoken": spoken,
            "code_blocks": code_blocks,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.ui_queue.put({"type": "assistant_response", "payload": payload})
        return payload


class ApiBridge:
    def __init__(self, core: BiladerCore) -> None:
        self.core = core

    def ask(self, text: str) -> Dict[str, Any]:
        return self.core.process_user_input(text)

    def get_system_status(self) -> Dict[str, Any]:
        snap = self.core.system_snapshot()
        data = asdict(snap)
        self.core.memory.append_event("system_snapshot", data)
        return data

    def toggle_arduino(self) -> Dict[str, Any]:
        if self.core.arduino.ser:
            return {"ok": True, "message": self.core.arduino.disconnect(), "connected": False}
        ok, msg = self.core.arduino.connect()
        return {"ok": ok, "message": msg, "connected": ok}

    def list_devices(self) -> Dict[str, Any]:
        usb = self.core.arduino.list_ports()
        # bluetooth sorgusu platform bağımlı; simüle liste
        bt = ["Bilader-Headset", "Telefonum"]
        return {"usb": usb, "bluetooth": bt}

    def recent_memory(self) -> List[Dict[str, Any]]:
        return self.core.memory.latest_conversation(25)


def build_window(core: BiladerCore) -> None:
    if webview is None:
        print("pywebview kurulu değil. Lütfen requirements.txt kurulumunu yap.")
        return

    api = ApiBridge(core)
    window = webview.create_window(
        "BİLADER AI v1.0",
        url=str(WEB_ROOT / "index.html"),
        js_api=api,
        width=1440,
        height=900,
        min_size=(1000, 700),
        confirm_close=True,
        background_color="#050505",
    )

    def ui_pusher() -> None:
        while not core.stop_event.is_set():
            try:
                event = core.ui_queue.get(timeout=0.3)
            except queue.Empty:
                continue
            if window:
                script = f"window.BiladerUI && window.BiladerUI.receivePythonEvent({json.dumps(event, ensure_ascii=False)});"
                try:
                    window.evaluate_js(script)
                except Exception:
                    pass

    thread = threading.Thread(target=ui_pusher, daemon=True)
    thread.start()

    core.start()
    webview.start(debug=True)
    core.shutdown()


def seed_local_intents() -> Dict[str, List[str]]:
    # Genişletilebilir intent koleksiyonu (yerel fallback)
    intents: Dict[str, List[str]] = {
        "selamlama": [
            "merhaba", "selam", "günaydın", "iyi akşamlar", "nabersin", "orada mısın",
        ],
        "durum": [
            "nasılsın", "iyi misin", "durumun nasıl", "çalışıyor musun", "aktif misin",
        ],
        "sistem": [
            "cpu", "ram", "disk", "sıcaklık", "işlemci", "kaynak", "performans",
        ],
        "iot": [
            "arduino", "ışık", "sıcaklık", "sensör", "röle", "seri port", "bağlantı",
        ],
        "medya": [
            "spotify", "müzik", "video", "oynat", "durdur", "ses aç", "ses kapat",
        ],
    }

# --- Geniş komut sözlüğü ---
COMMAND_ALIASES: Dict[str, List[str]] = {
    'komut_001': ['tetik 1', 'işlem 1', 'aksiyon 1', 'bilader görev 1'],
    'komut_002': ['tetik 2', 'işlem 2', 'aksiyon 2', 'bilader görev 2'],
    'komut_003': ['tetik 3', 'işlem 3', 'aksiyon 3', 'bilader görev 3'],
    'komut_004': ['tetik 4', 'işlem 4', 'aksiyon 4', 'bilader görev 4'],
    'komut_005': ['tetik 5', 'işlem 5', 'aksiyon 5', 'bilader görev 5'],
    'komut_006': ['tetik 6', 'işlem 6', 'aksiyon 6', 'bilader görev 6'],
    'komut_007': ['tetik 7', 'işlem 7', 'aksiyon 7', 'bilader görev 7'],
    'komut_008': ['tetik 8', 'işlem 8', 'aksiyon 8', 'bilader görev 8'],
    'komut_009': ['tetik 9', 'işlem 9', 'aksiyon 9', 'bilader görev 9'],
    'komut_010': ['tetik 10', 'işlem 10', 'aksiyon 10', 'bilader görev 10'],
    'komut_011': ['tetik 11', 'işlem 11', 'aksiyon 11', 'bilader görev 11'],
    'komut_012': ['tetik 12', 'işlem 12', 'aksiyon 12', 'bilader görev 12'],
    'komut_013': ['tetik 13', 'işlem 13', 'aksiyon 13', 'bilader görev 13'],
    'komut_014': ['tetik 14', 'işlem 14', 'aksiyon 14', 'bilader görev 14'],
    'komut_015': ['tetik 15', 'işlem 15', 'aksiyon 15', 'bilader görev 15'],
    'komut_016': ['tetik 16', 'işlem 16', 'aksiyon 16', 'bilader görev 16'],
    'komut_017': ['tetik 17', 'işlem 17', 'aksiyon 17', 'bilader görev 17'],
    'komut_018': ['tetik 18', 'işlem 18', 'aksiyon 18', 'bilader görev 18'],
    'komut_019': ['tetik 19', 'işlem 19', 'aksiyon 19', 'bilader görev 19'],
    'komut_020': ['tetik 20', 'işlem 20', 'aksiyon 20', 'bilader görev 20'],
    'komut_021': ['tetik 21', 'işlem 21', 'aksiyon 21', 'bilader görev 21'],
    'komut_022': ['tetik 22', 'işlem 22', 'aksiyon 22', 'bilader görev 22'],
    'komut_023': ['tetik 23', 'işlem 23', 'aksiyon 23', 'bilader görev 23'],
    'komut_024': ['tetik 24', 'işlem 24', 'aksiyon 24', 'bilader görev 24'],
    'komut_025': ['tetik 25', 'işlem 25', 'aksiyon 25', 'bilader görev 25'],
    'komut_026': ['tetik 26', 'işlem 26', 'aksiyon 26', 'bilader görev 26'],
    'komut_027': ['tetik 27', 'işlem 27', 'aksiyon 27', 'bilader görev 27'],
    'komut_028': ['tetik 28', 'işlem 28', 'aksiyon 28', 'bilader görev 28'],
    'komut_029': ['tetik 29', 'işlem 29', 'aksiyon 29', 'bilader görev 29'],
    'komut_030': ['tetik 30', 'işlem 30', 'aksiyon 30', 'bilader görev 30'],
    'komut_031': ['tetik 31', 'işlem 31', 'aksiyon 31', 'bilader görev 31'],
    'komut_032': ['tetik 32', 'işlem 32', 'aksiyon 32', 'bilader görev 32'],
    'komut_033': ['tetik 33', 'işlem 33', 'aksiyon 33', 'bilader görev 33'],
    'komut_034': ['tetik 34', 'işlem 34', 'aksiyon 34', 'bilader görev 34'],
    'komut_035': ['tetik 35', 'işlem 35', 'aksiyon 35', 'bilader görev 35'],
    'komut_036': ['tetik 36', 'işlem 36', 'aksiyon 36', 'bilader görev 36'],
    'komut_037': ['tetik 37', 'işlem 37', 'aksiyon 37', 'bilader görev 37'],
    'komut_038': ['tetik 38', 'işlem 38', 'aksiyon 38', 'bilader görev 38'],
    'komut_039': ['tetik 39', 'işlem 39', 'aksiyon 39', 'bilader görev 39'],
    'komut_040': ['tetik 40', 'işlem 40', 'aksiyon 40', 'bilader görev 40'],
    'komut_041': ['tetik 41', 'işlem 41', 'aksiyon 41', 'bilader görev 41'],
    'komut_042': ['tetik 42', 'işlem 42', 'aksiyon 42', 'bilader görev 42'],
    'komut_043': ['tetik 43', 'işlem 43', 'aksiyon 43', 'bilader görev 43'],
    'komut_044': ['tetik 44', 'işlem 44', 'aksiyon 44', 'bilader görev 44'],
    'komut_045': ['tetik 45', 'işlem 45', 'aksiyon 45', 'bilader görev 45'],
    'komut_046': ['tetik 46', 'işlem 46', 'aksiyon 46', 'bilader görev 46'],
    'komut_047': ['tetik 47', 'işlem 47', 'aksiyon 47', 'bilader görev 47'],
    'komut_048': ['tetik 48', 'işlem 48', 'aksiyon 48', 'bilader görev 48'],
    'komut_049': ['tetik 49', 'işlem 49', 'aksiyon 49', 'bilader görev 49'],
    'komut_050': ['tetik 50', 'işlem 50', 'aksiyon 50', 'bilader görev 50'],
    'komut_051': ['tetik 51', 'işlem 51', 'aksiyon 51', 'bilader görev 51'],
    'komut_052': ['tetik 52', 'işlem 52', 'aksiyon 52', 'bilader görev 52'],
    'komut_053': ['tetik 53', 'işlem 53', 'aksiyon 53', 'bilader görev 53'],
    'komut_054': ['tetik 54', 'işlem 54', 'aksiyon 54', 'bilader görev 54'],
    'komut_055': ['tetik 55', 'işlem 55', 'aksiyon 55', 'bilader görev 55'],
    'komut_056': ['tetik 56', 'işlem 56', 'aksiyon 56', 'bilader görev 56'],
    'komut_057': ['tetik 57', 'işlem 57', 'aksiyon 57', 'bilader görev 57'],
    'komut_058': ['tetik 58', 'işlem 58', 'aksiyon 58', 'bilader görev 58'],
    'komut_059': ['tetik 59', 'işlem 59', 'aksiyon 59', 'bilader görev 59'],
    'komut_060': ['tetik 60', 'işlem 60', 'aksiyon 60', 'bilader görev 60'],
    'komut_061': ['tetik 61', 'işlem 61', 'aksiyon 61', 'bilader görev 61'],
    'komut_062': ['tetik 62', 'işlem 62', 'aksiyon 62', 'bilader görev 62'],
    'komut_063': ['tetik 63', 'işlem 63', 'aksiyon 63', 'bilader görev 63'],
    'komut_064': ['tetik 64', 'işlem 64', 'aksiyon 64', 'bilader görev 64'],
    'komut_065': ['tetik 65', 'işlem 65', 'aksiyon 65', 'bilader görev 65'],
    'komut_066': ['tetik 66', 'işlem 66', 'aksiyon 66', 'bilader görev 66'],
    'komut_067': ['tetik 67', 'işlem 67', 'aksiyon 67', 'bilader görev 67'],
    'komut_068': ['tetik 68', 'işlem 68', 'aksiyon 68', 'bilader görev 68'],
    'komut_069': ['tetik 69', 'işlem 69', 'aksiyon 69', 'bilader görev 69'],
    'komut_070': ['tetik 70', 'işlem 70', 'aksiyon 70', 'bilader görev 70'],
    'komut_071': ['tetik 71', 'işlem 71', 'aksiyon 71', 'bilader görev 71'],
    'komut_072': ['tetik 72', 'işlem 72', 'aksiyon 72', 'bilader görev 72'],
    'komut_073': ['tetik 73', 'işlem 73', 'aksiyon 73', 'bilader görev 73'],
    'komut_074': ['tetik 74', 'işlem 74', 'aksiyon 74', 'bilader görev 74'],
    'komut_075': ['tetik 75', 'işlem 75', 'aksiyon 75', 'bilader görev 75'],
    'komut_076': ['tetik 76', 'işlem 76', 'aksiyon 76', 'bilader görev 76'],
    'komut_077': ['tetik 77', 'işlem 77', 'aksiyon 77', 'bilader görev 77'],
    'komut_078': ['tetik 78', 'işlem 78', 'aksiyon 78', 'bilader görev 78'],
    'komut_079': ['tetik 79', 'işlem 79', 'aksiyon 79', 'bilader görev 79'],
    'komut_080': ['tetik 80', 'işlem 80', 'aksiyon 80', 'bilader görev 80'],
    'komut_081': ['tetik 81', 'işlem 81', 'aksiyon 81', 'bilader görev 81'],
    'komut_082': ['tetik 82', 'işlem 82', 'aksiyon 82', 'bilader görev 82'],
    'komut_083': ['tetik 83', 'işlem 83', 'aksiyon 83', 'bilader görev 83'],
    'komut_084': ['tetik 84', 'işlem 84', 'aksiyon 84', 'bilader görev 84'],
    'komut_085': ['tetik 85', 'işlem 85', 'aksiyon 85', 'bilader görev 85'],
    'komut_086': ['tetik 86', 'işlem 86', 'aksiyon 86', 'bilader görev 86'],
    'komut_087': ['tetik 87', 'işlem 87', 'aksiyon 87', 'bilader görev 87'],
    'komut_088': ['tetik 88', 'işlem 88', 'aksiyon 88', 'bilader görev 88'],
    'komut_089': ['tetik 89', 'işlem 89', 'aksiyon 89', 'bilader görev 89'],
    'komut_090': ['tetik 90', 'işlem 90', 'aksiyon 90', 'bilader görev 90'],
    'komut_091': ['tetik 91', 'işlem 91', 'aksiyon 91', 'bilader görev 91'],
    'komut_092': ['tetik 92', 'işlem 92', 'aksiyon 92', 'bilader görev 92'],
    'komut_093': ['tetik 93', 'işlem 93', 'aksiyon 93', 'bilader görev 93'],
    'komut_094': ['tetik 94', 'işlem 94', 'aksiyon 94', 'bilader görev 94'],
    'komut_095': ['tetik 95', 'işlem 95', 'aksiyon 95', 'bilader görev 95'],
    'komut_096': ['tetik 96', 'işlem 96', 'aksiyon 96', 'bilader görev 96'],
    'komut_097': ['tetik 97', 'işlem 97', 'aksiyon 97', 'bilader görev 97'],
    'komut_098': ['tetik 98', 'işlem 98', 'aksiyon 98', 'bilader görev 98'],
    'komut_099': ['tetik 99', 'işlem 99', 'aksiyon 99', 'bilader görev 99'],
    'komut_100': ['tetik 100', 'işlem 100', 'aksiyon 100', 'bilader görev 100'],
    'komut_101': ['tetik 101', 'işlem 101', 'aksiyon 101', 'bilader görev 101'],
    'komut_102': ['tetik 102', 'işlem 102', 'aksiyon 102', 'bilader görev 102'],
    'komut_103': ['tetik 103', 'işlem 103', 'aksiyon 103', 'bilader görev 103'],
    'komut_104': ['tetik 104', 'işlem 104', 'aksiyon 104', 'bilader görev 104'],
    'komut_105': ['tetik 105', 'işlem 105', 'aksiyon 105', 'bilader görev 105'],
    'komut_106': ['tetik 106', 'işlem 106', 'aksiyon 106', 'bilader görev 106'],
    'komut_107': ['tetik 107', 'işlem 107', 'aksiyon 107', 'bilader görev 107'],
    'komut_108': ['tetik 108', 'işlem 108', 'aksiyon 108', 'bilader görev 108'],
    'komut_109': ['tetik 109', 'işlem 109', 'aksiyon 109', 'bilader görev 109'],
    'komut_110': ['tetik 110', 'işlem 110', 'aksiyon 110', 'bilader görev 110'],
    'komut_111': ['tetik 111', 'işlem 111', 'aksiyon 111', 'bilader görev 111'],
    'komut_112': ['tetik 112', 'işlem 112', 'aksiyon 112', 'bilader görev 112'],
    'komut_113': ['tetik 113', 'işlem 113', 'aksiyon 113', 'bilader görev 113'],
    'komut_114': ['tetik 114', 'işlem 114', 'aksiyon 114', 'bilader görev 114'],
    'komut_115': ['tetik 115', 'işlem 115', 'aksiyon 115', 'bilader görev 115'],
    'komut_116': ['tetik 116', 'işlem 116', 'aksiyon 116', 'bilader görev 116'],
    'komut_117': ['tetik 117', 'işlem 117', 'aksiyon 117', 'bilader görev 117'],
    'komut_118': ['tetik 118', 'işlem 118', 'aksiyon 118', 'bilader görev 118'],
    'komut_119': ['tetik 119', 'işlem 119', 'aksiyon 119', 'bilader görev 119'],
    'komut_120': ['tetik 120', 'işlem 120', 'aksiyon 120', 'bilader görev 120'],
    'komut_121': ['tetik 121', 'işlem 121', 'aksiyon 121', 'bilader görev 121'],
    'komut_122': ['tetik 122', 'işlem 122', 'aksiyon 122', 'bilader görev 122'],
    'komut_123': ['tetik 123', 'işlem 123', 'aksiyon 123', 'bilader görev 123'],
    'komut_124': ['tetik 124', 'işlem 124', 'aksiyon 124', 'bilader görev 124'],
    'komut_125': ['tetik 125', 'işlem 125', 'aksiyon 125', 'bilader görev 125'],
    'komut_126': ['tetik 126', 'işlem 126', 'aksiyon 126', 'bilader görev 126'],
    'komut_127': ['tetik 127', 'işlem 127', 'aksiyon 127', 'bilader görev 127'],
    'komut_128': ['tetik 128', 'işlem 128', 'aksiyon 128', 'bilader görev 128'],
    'komut_129': ['tetik 129', 'işlem 129', 'aksiyon 129', 'bilader görev 129'],
    'komut_130': ['tetik 130', 'işlem 130', 'aksiyon 130', 'bilader görev 130'],
    'komut_131': ['tetik 131', 'işlem 131', 'aksiyon 131', 'bilader görev 131'],
    'komut_132': ['tetik 132', 'işlem 132', 'aksiyon 132', 'bilader görev 132'],
    'komut_133': ['tetik 133', 'işlem 133', 'aksiyon 133', 'bilader görev 133'],
    'komut_134': ['tetik 134', 'işlem 134', 'aksiyon 134', 'bilader görev 134'],
    'komut_135': ['tetik 135', 'işlem 135', 'aksiyon 135', 'bilader görev 135'],
    'komut_136': ['tetik 136', 'işlem 136', 'aksiyon 136', 'bilader görev 136'],
    'komut_137': ['tetik 137', 'işlem 137', 'aksiyon 137', 'bilader görev 137'],
    'komut_138': ['tetik 138', 'işlem 138', 'aksiyon 138', 'bilader görev 138'],
    'komut_139': ['tetik 139', 'işlem 139', 'aksiyon 139', 'bilader görev 139'],
    'komut_140': ['tetik 140', 'işlem 140', 'aksiyon 140', 'bilader görev 140'],
    'komut_141': ['tetik 141', 'işlem 141', 'aksiyon 141', 'bilader görev 141'],
    'komut_142': ['tetik 142', 'işlem 142', 'aksiyon 142', 'bilader görev 142'],
    'komut_143': ['tetik 143', 'işlem 143', 'aksiyon 143', 'bilader görev 143'],
    'komut_144': ['tetik 144', 'işlem 144', 'aksiyon 144', 'bilader görev 144'],
    'komut_145': ['tetik 145', 'işlem 145', 'aksiyon 145', 'bilader görev 145'],
    'komut_146': ['tetik 146', 'işlem 146', 'aksiyon 146', 'bilader görev 146'],
    'komut_147': ['tetik 147', 'işlem 147', 'aksiyon 147', 'bilader görev 147'],
    'komut_148': ['tetik 148', 'işlem 148', 'aksiyon 148', 'bilader görev 148'],
    'komut_149': ['tetik 149', 'işlem 149', 'aksiyon 149', 'bilader görev 149'],
    'komut_150': ['tetik 150', 'işlem 150', 'aksiyon 150', 'bilader görev 150'],
    'komut_151': ['tetik 151', 'işlem 151', 'aksiyon 151', 'bilader görev 151'],
    'komut_152': ['tetik 152', 'işlem 152', 'aksiyon 152', 'bilader görev 152'],
    'komut_153': ['tetik 153', 'işlem 153', 'aksiyon 153', 'bilader görev 153'],
    'komut_154': ['tetik 154', 'işlem 154', 'aksiyon 154', 'bilader görev 154'],
    'komut_155': ['tetik 155', 'işlem 155', 'aksiyon 155', 'bilader görev 155'],
    'komut_156': ['tetik 156', 'işlem 156', 'aksiyon 156', 'bilader görev 156'],
    'komut_157': ['tetik 157', 'işlem 157', 'aksiyon 157', 'bilader görev 157'],
    'komut_158': ['tetik 158', 'işlem 158', 'aksiyon 158', 'bilader görev 158'],
    'komut_159': ['tetik 159', 'işlem 159', 'aksiyon 159', 'bilader görev 159'],
    'komut_160': ['tetik 160', 'işlem 160', 'aksiyon 160', 'bilader görev 160'],
    'komut_161': ['tetik 161', 'işlem 161', 'aksiyon 161', 'bilader görev 161'],
    'komut_162': ['tetik 162', 'işlem 162', 'aksiyon 162', 'bilader görev 162'],
    'komut_163': ['tetik 163', 'işlem 163', 'aksiyon 163', 'bilader görev 163'],
    'komut_164': ['tetik 164', 'işlem 164', 'aksiyon 164', 'bilader görev 164'],
    'komut_165': ['tetik 165', 'işlem 165', 'aksiyon 165', 'bilader görev 165'],
    'komut_166': ['tetik 166', 'işlem 166', 'aksiyon 166', 'bilader görev 166'],
    'komut_167': ['tetik 167', 'işlem 167', 'aksiyon 167', 'bilader görev 167'],
    'komut_168': ['tetik 168', 'işlem 168', 'aksiyon 168', 'bilader görev 168'],
    'komut_169': ['tetik 169', 'işlem 169', 'aksiyon 169', 'bilader görev 169'],
    'komut_170': ['tetik 170', 'işlem 170', 'aksiyon 170', 'bilader görev 170'],
    'komut_171': ['tetik 171', 'işlem 171', 'aksiyon 171', 'bilader görev 171'],
    'komut_172': ['tetik 172', 'işlem 172', 'aksiyon 172', 'bilader görev 172'],
    'komut_173': ['tetik 173', 'işlem 173', 'aksiyon 173', 'bilader görev 173'],
    'komut_174': ['tetik 174', 'işlem 174', 'aksiyon 174', 'bilader görev 174'],
    'komut_175': ['tetik 175', 'işlem 175', 'aksiyon 175', 'bilader görev 175'],
    'komut_176': ['tetik 176', 'işlem 176', 'aksiyon 176', 'bilader görev 176'],
    'komut_177': ['tetik 177', 'işlem 177', 'aksiyon 177', 'bilader görev 177'],
    'komut_178': ['tetik 178', 'işlem 178', 'aksiyon 178', 'bilader görev 178'],
    'komut_179': ['tetik 179', 'işlem 179', 'aksiyon 179', 'bilader görev 179'],
    'komut_180': ['tetik 180', 'işlem 180', 'aksiyon 180', 'bilader görev 180'],
    'komut_181': ['tetik 181', 'işlem 181', 'aksiyon 181', 'bilader görev 181'],
    'komut_182': ['tetik 182', 'işlem 182', 'aksiyon 182', 'bilader görev 182'],
    'komut_183': ['tetik 183', 'işlem 183', 'aksiyon 183', 'bilader görev 183'],
    'komut_184': ['tetik 184', 'işlem 184', 'aksiyon 184', 'bilader görev 184'],
    'komut_185': ['tetik 185', 'işlem 185', 'aksiyon 185', 'bilader görev 185'],
    'komut_186': ['tetik 186', 'işlem 186', 'aksiyon 186', 'bilader görev 186'],
    'komut_187': ['tetik 187', 'işlem 187', 'aksiyon 187', 'bilader görev 187'],
    'komut_188': ['tetik 188', 'işlem 188', 'aksiyon 188', 'bilader görev 188'],
    'komut_189': ['tetik 189', 'işlem 189', 'aksiyon 189', 'bilader görev 189'],
    'komut_190': ['tetik 190', 'işlem 190', 'aksiyon 190', 'bilader görev 190'],
    'komut_191': ['tetik 191', 'işlem 191', 'aksiyon 191', 'bilader görev 191'],
    'komut_192': ['tetik 192', 'işlem 192', 'aksiyon 192', 'bilader görev 192'],
    'komut_193': ['tetik 193', 'işlem 193', 'aksiyon 193', 'bilader görev 193'],
    'komut_194': ['tetik 194', 'işlem 194', 'aksiyon 194', 'bilader görev 194'],
    'komut_195': ['tetik 195', 'işlem 195', 'aksiyon 195', 'bilader görev 195'],
    'komut_196': ['tetik 196', 'işlem 196', 'aksiyon 196', 'bilader görev 196'],
    'komut_197': ['tetik 197', 'işlem 197', 'aksiyon 197', 'bilader görev 197'],
    'komut_198': ['tetik 198', 'işlem 198', 'aksiyon 198', 'bilader görev 198'],
    'komut_199': ['tetik 199', 'işlem 199', 'aksiyon 199', 'bilader görev 199'],
    'komut_200': ['tetik 200', 'işlem 200', 'aksiyon 200', 'bilader görev 200'],
    'komut_201': ['tetik 201', 'işlem 201', 'aksiyon 201', 'bilader görev 201'],
    'komut_202': ['tetik 202', 'işlem 202', 'aksiyon 202', 'bilader görev 202'],
    'komut_203': ['tetik 203', 'işlem 203', 'aksiyon 203', 'bilader görev 203'],
    'komut_204': ['tetik 204', 'işlem 204', 'aksiyon 204', 'bilader görev 204'],
    'komut_205': ['tetik 205', 'işlem 205', 'aksiyon 205', 'bilader görev 205'],
    'komut_206': ['tetik 206', 'işlem 206', 'aksiyon 206', 'bilader görev 206'],
    'komut_207': ['tetik 207', 'işlem 207', 'aksiyon 207', 'bilader görev 207'],
    'komut_208': ['tetik 208', 'işlem 208', 'aksiyon 208', 'bilader görev 208'],
    'komut_209': ['tetik 209', 'işlem 209', 'aksiyon 209', 'bilader görev 209'],
    'komut_210': ['tetik 210', 'işlem 210', 'aksiyon 210', 'bilader görev 210'],
    'komut_211': ['tetik 211', 'işlem 211', 'aksiyon 211', 'bilader görev 211'],
    'komut_212': ['tetik 212', 'işlem 212', 'aksiyon 212', 'bilader görev 212'],
    'komut_213': ['tetik 213', 'işlem 213', 'aksiyon 213', 'bilader görev 213'],
    'komut_214': ['tetik 214', 'işlem 214', 'aksiyon 214', 'bilader görev 214'],
    'komut_215': ['tetik 215', 'işlem 215', 'aksiyon 215', 'bilader görev 215'],
    'komut_216': ['tetik 216', 'işlem 216', 'aksiyon 216', 'bilader görev 216'],
    'komut_217': ['tetik 217', 'işlem 217', 'aksiyon 217', 'bilader görev 217'],
    'komut_218': ['tetik 218', 'işlem 218', 'aksiyon 218', 'bilader görev 218'],
    'komut_219': ['tetik 219', 'işlem 219', 'aksiyon 219', 'bilader görev 219'],
    'komut_220': ['tetik 220', 'işlem 220', 'aksiyon 220', 'bilader görev 220'],
    'komut_221': ['tetik 221', 'işlem 221', 'aksiyon 221', 'bilader görev 221'],
    'komut_222': ['tetik 222', 'işlem 222', 'aksiyon 222', 'bilader görev 222'],
    'komut_223': ['tetik 223', 'işlem 223', 'aksiyon 223', 'bilader görev 223'],
    'komut_224': ['tetik 224', 'işlem 224', 'aksiyon 224', 'bilader görev 224'],
    'komut_225': ['tetik 225', 'işlem 225', 'aksiyon 225', 'bilader görev 225'],
    'komut_226': ['tetik 226', 'işlem 226', 'aksiyon 226', 'bilader görev 226'],
    'komut_227': ['tetik 227', 'işlem 227', 'aksiyon 227', 'bilader görev 227'],
    'komut_228': ['tetik 228', 'işlem 228', 'aksiyon 228', 'bilader görev 228'],
    'komut_229': ['tetik 229', 'işlem 229', 'aksiyon 229', 'bilader görev 229'],
    'komut_230': ['tetik 230', 'işlem 230', 'aksiyon 230', 'bilader görev 230'],
    'komut_231': ['tetik 231', 'işlem 231', 'aksiyon 231', 'bilader görev 231'],
    'komut_232': ['tetik 232', 'işlem 232', 'aksiyon 232', 'bilader görev 232'],
    'komut_233': ['tetik 233', 'işlem 233', 'aksiyon 233', 'bilader görev 233'],
    'komut_234': ['tetik 234', 'işlem 234', 'aksiyon 234', 'bilader görev 234'],
    'komut_235': ['tetik 235', 'işlem 235', 'aksiyon 235', 'bilader görev 235'],
    'komut_236': ['tetik 236', 'işlem 236', 'aksiyon 236', 'bilader görev 236'],
    'komut_237': ['tetik 237', 'işlem 237', 'aksiyon 237', 'bilader görev 237'],
    'komut_238': ['tetik 238', 'işlem 238', 'aksiyon 238', 'bilader görev 238'],
    'komut_239': ['tetik 239', 'işlem 239', 'aksiyon 239', 'bilader görev 239'],
    'komut_240': ['tetik 240', 'işlem 240', 'aksiyon 240', 'bilader görev 240'],
    'komut_241': ['tetik 241', 'işlem 241', 'aksiyon 241', 'bilader görev 241'],
    'komut_242': ['tetik 242', 'işlem 242', 'aksiyon 242', 'bilader görev 242'],
    'komut_243': ['tetik 243', 'işlem 243', 'aksiyon 243', 'bilader görev 243'],
    'komut_244': ['tetik 244', 'işlem 244', 'aksiyon 244', 'bilader görev 244'],
    'komut_245': ['tetik 245', 'işlem 245', 'aksiyon 245', 'bilader görev 245'],
    'komut_246': ['tetik 246', 'işlem 246', 'aksiyon 246', 'bilader görev 246'],
    'komut_247': ['tetik 247', 'işlem 247', 'aksiyon 247', 'bilader görev 247'],
    'komut_248': ['tetik 248', 'işlem 248', 'aksiyon 248', 'bilader görev 248'],
    'komut_249': ['tetik 249', 'işlem 249', 'aksiyon 249', 'bilader görev 249'],
    'komut_250': ['tetik 250', 'işlem 250', 'aksiyon 250', 'bilader görev 250'],
    'komut_251': ['tetik 251', 'işlem 251', 'aksiyon 251', 'bilader görev 251'],
    'komut_252': ['tetik 252', 'işlem 252', 'aksiyon 252', 'bilader görev 252'],
    'komut_253': ['tetik 253', 'işlem 253', 'aksiyon 253', 'bilader görev 253'],
    'komut_254': ['tetik 254', 'işlem 254', 'aksiyon 254', 'bilader görev 254'],
    'komut_255': ['tetik 255', 'işlem 255', 'aksiyon 255', 'bilader görev 255'],
    'komut_256': ['tetik 256', 'işlem 256', 'aksiyon 256', 'bilader görev 256'],
    'komut_257': ['tetik 257', 'işlem 257', 'aksiyon 257', 'bilader görev 257'],
    'komut_258': ['tetik 258', 'işlem 258', 'aksiyon 258', 'bilader görev 258'],
    'komut_259': ['tetik 259', 'işlem 259', 'aksiyon 259', 'bilader görev 259'],
    'komut_260': ['tetik 260', 'işlem 260', 'aksiyon 260', 'bilader görev 260'],
    'komut_261': ['tetik 261', 'işlem 261', 'aksiyon 261', 'bilader görev 261'],
    'komut_262': ['tetik 262', 'işlem 262', 'aksiyon 262', 'bilader görev 262'],
    'komut_263': ['tetik 263', 'işlem 263', 'aksiyon 263', 'bilader görev 263'],
    'komut_264': ['tetik 264', 'işlem 264', 'aksiyon 264', 'bilader görev 264'],
    'komut_265': ['tetik 265', 'işlem 265', 'aksiyon 265', 'bilader görev 265'],
    'komut_266': ['tetik 266', 'işlem 266', 'aksiyon 266', 'bilader görev 266'],
    'komut_267': ['tetik 267', 'işlem 267', 'aksiyon 267', 'bilader görev 267'],
    'komut_268': ['tetik 268', 'işlem 268', 'aksiyon 268', 'bilader görev 268'],
    'komut_269': ['tetik 269', 'işlem 269', 'aksiyon 269', 'bilader görev 269'],
    'komut_270': ['tetik 270', 'işlem 270', 'aksiyon 270', 'bilader görev 270'],
    'komut_271': ['tetik 271', 'işlem 271', 'aksiyon 271', 'bilader görev 271'],
    'komut_272': ['tetik 272', 'işlem 272', 'aksiyon 272', 'bilader görev 272'],
    'komut_273': ['tetik 273', 'işlem 273', 'aksiyon 273', 'bilader görev 273'],
    'komut_274': ['tetik 274', 'işlem 274', 'aksiyon 274', 'bilader görev 274'],
    'komut_275': ['tetik 275', 'işlem 275', 'aksiyon 275', 'bilader görev 275'],
    'komut_276': ['tetik 276', 'işlem 276', 'aksiyon 276', 'bilader görev 276'],
    'komut_277': ['tetik 277', 'işlem 277', 'aksiyon 277', 'bilader görev 277'],
    'komut_278': ['tetik 278', 'işlem 278', 'aksiyon 278', 'bilader görev 278'],
    'komut_279': ['tetik 279', 'işlem 279', 'aksiyon 279', 'bilader görev 279'],
    'komut_280': ['tetik 280', 'işlem 280', 'aksiyon 280', 'bilader görev 280'],
    'komut_281': ['tetik 281', 'işlem 281', 'aksiyon 281', 'bilader görev 281'],
    'komut_282': ['tetik 282', 'işlem 282', 'aksiyon 282', 'bilader görev 282'],
    'komut_283': ['tetik 283', 'işlem 283', 'aksiyon 283', 'bilader görev 283'],
    'komut_284': ['tetik 284', 'işlem 284', 'aksiyon 284', 'bilader görev 284'],
    'komut_285': ['tetik 285', 'işlem 285', 'aksiyon 285', 'bilader görev 285'],
    'komut_286': ['tetik 286', 'işlem 286', 'aksiyon 286', 'bilader görev 286'],
    'komut_287': ['tetik 287', 'işlem 287', 'aksiyon 287', 'bilader görev 287'],
    'komut_288': ['tetik 288', 'işlem 288', 'aksiyon 288', 'bilader görev 288'],
    'komut_289': ['tetik 289', 'işlem 289', 'aksiyon 289', 'bilader görev 289'],
    'komut_290': ['tetik 290', 'işlem 290', 'aksiyon 290', 'bilader görev 290'],
    'komut_291': ['tetik 291', 'işlem 291', 'aksiyon 291', 'bilader görev 291'],
    'komut_292': ['tetik 292', 'işlem 292', 'aksiyon 292', 'bilader görev 292'],
    'komut_293': ['tetik 293', 'işlem 293', 'aksiyon 293', 'bilader görev 293'],
    'komut_294': ['tetik 294', 'işlem 294', 'aksiyon 294', 'bilader görev 294'],
    'komut_295': ['tetik 295', 'işlem 295', 'aksiyon 295', 'bilader görev 295'],
    'komut_296': ['tetik 296', 'işlem 296', 'aksiyon 296', 'bilader görev 296'],
    'komut_297': ['tetik 297', 'işlem 297', 'aksiyon 297', 'bilader görev 297'],
    'komut_298': ['tetik 298', 'işlem 298', 'aksiyon 298', 'bilader görev 298'],
    'komut_299': ['tetik 299', 'işlem 299', 'aksiyon 299', 'bilader görev 299'],
    'komut_300': ['tetik 300', 'işlem 300', 'aksiyon 300', 'bilader görev 300'],
    'komut_301': ['tetik 301', 'işlem 301', 'aksiyon 301', 'bilader görev 301'],
    'komut_302': ['tetik 302', 'işlem 302', 'aksiyon 302', 'bilader görev 302'],
    'komut_303': ['tetik 303', 'işlem 303', 'aksiyon 303', 'bilader görev 303'],
    'komut_304': ['tetik 304', 'işlem 304', 'aksiyon 304', 'bilader görev 304'],
    'komut_305': ['tetik 305', 'işlem 305', 'aksiyon 305', 'bilader görev 305'],
    'komut_306': ['tetik 306', 'işlem 306', 'aksiyon 306', 'bilader görev 306'],
    'komut_307': ['tetik 307', 'işlem 307', 'aksiyon 307', 'bilader görev 307'],
    'komut_308': ['tetik 308', 'işlem 308', 'aksiyon 308', 'bilader görev 308'],
    'komut_309': ['tetik 309', 'işlem 309', 'aksiyon 309', 'bilader görev 309'],
    'komut_310': ['tetik 310', 'işlem 310', 'aksiyon 310', 'bilader görev 310'],
    'komut_311': ['tetik 311', 'işlem 311', 'aksiyon 311', 'bilader görev 311'],
    'komut_312': ['tetik 312', 'işlem 312', 'aksiyon 312', 'bilader görev 312'],
    'komut_313': ['tetik 313', 'işlem 313', 'aksiyon 313', 'bilader görev 313'],
    'komut_314': ['tetik 314', 'işlem 314', 'aksiyon 314', 'bilader görev 314'],
    'komut_315': ['tetik 315', 'işlem 315', 'aksiyon 315', 'bilader görev 315'],
    'komut_316': ['tetik 316', 'işlem 316', 'aksiyon 316', 'bilader görev 316'],
    'komut_317': ['tetik 317', 'işlem 317', 'aksiyon 317', 'bilader görev 317'],
    'komut_318': ['tetik 318', 'işlem 318', 'aksiyon 318', 'bilader görev 318'],
    'komut_319': ['tetik 319', 'işlem 319', 'aksiyon 319', 'bilader görev 319'],
    'komut_320': ['tetik 320', 'işlem 320', 'aksiyon 320', 'bilader görev 320'],
    'komut_321': ['tetik 321', 'işlem 321', 'aksiyon 321', 'bilader görev 321'],
    'komut_322': ['tetik 322', 'işlem 322', 'aksiyon 322', 'bilader görev 322'],
    'komut_323': ['tetik 323', 'işlem 323', 'aksiyon 323', 'bilader görev 323'],
    'komut_324': ['tetik 324', 'işlem 324', 'aksiyon 324', 'bilader görev 324'],
    'komut_325': ['tetik 325', 'işlem 325', 'aksiyon 325', 'bilader görev 325'],
    'komut_326': ['tetik 326', 'işlem 326', 'aksiyon 326', 'bilader görev 326'],
    'komut_327': ['tetik 327', 'işlem 327', 'aksiyon 327', 'bilader görev 327'],
    'komut_328': ['tetik 328', 'işlem 328', 'aksiyon 328', 'bilader görev 328'],
    'komut_329': ['tetik 329', 'işlem 329', 'aksiyon 329', 'bilader görev 329'],
    'komut_330': ['tetik 330', 'işlem 330', 'aksiyon 330', 'bilader görev 330'],
    'komut_331': ['tetik 331', 'işlem 331', 'aksiyon 331', 'bilader görev 331'],
    'komut_332': ['tetik 332', 'işlem 332', 'aksiyon 332', 'bilader görev 332'],
    'komut_333': ['tetik 333', 'işlem 333', 'aksiyon 333', 'bilader görev 333'],
    'komut_334': ['tetik 334', 'işlem 334', 'aksiyon 334', 'bilader görev 334'],
    'komut_335': ['tetik 335', 'işlem 335', 'aksiyon 335', 'bilader görev 335'],
    'komut_336': ['tetik 336', 'işlem 336', 'aksiyon 336', 'bilader görev 336'],
    'komut_337': ['tetik 337', 'işlem 337', 'aksiyon 337', 'bilader görev 337'],
    'komut_338': ['tetik 338', 'işlem 338', 'aksiyon 338', 'bilader görev 338'],
    'komut_339': ['tetik 339', 'işlem 339', 'aksiyon 339', 'bilader görev 339'],
    'komut_340': ['tetik 340', 'işlem 340', 'aksiyon 340', 'bilader görev 340'],
    'komut_341': ['tetik 341', 'işlem 341', 'aksiyon 341', 'bilader görev 341'],
    'komut_342': ['tetik 342', 'işlem 342', 'aksiyon 342', 'bilader görev 342'],
    'komut_343': ['tetik 343', 'işlem 343', 'aksiyon 343', 'bilader görev 343'],
    'komut_344': ['tetik 344', 'işlem 344', 'aksiyon 344', 'bilader görev 344'],
    'komut_345': ['tetik 345', 'işlem 345', 'aksiyon 345', 'bilader görev 345'],
    'komut_346': ['tetik 346', 'işlem 346', 'aksiyon 346', 'bilader görev 346'],
    'komut_347': ['tetik 347', 'işlem 347', 'aksiyon 347', 'bilader görev 347'],
    'komut_348': ['tetik 348', 'işlem 348', 'aksiyon 348', 'bilader görev 348'],
    'komut_349': ['tetik 349', 'işlem 349', 'aksiyon 349', 'bilader görev 349'],
    'komut_350': ['tetik 350', 'işlem 350', 'aksiyon 350', 'bilader görev 350'],
    'komut_351': ['tetik 351', 'işlem 351', 'aksiyon 351', 'bilader görev 351'],
    'komut_352': ['tetik 352', 'işlem 352', 'aksiyon 352', 'bilader görev 352'],
    'komut_353': ['tetik 353', 'işlem 353', 'aksiyon 353', 'bilader görev 353'],
    'komut_354': ['tetik 354', 'işlem 354', 'aksiyon 354', 'bilader görev 354'],
    'komut_355': ['tetik 355', 'işlem 355', 'aksiyon 355', 'bilader görev 355'],
    'komut_356': ['tetik 356', 'işlem 356', 'aksiyon 356', 'bilader görev 356'],
    'komut_357': ['tetik 357', 'işlem 357', 'aksiyon 357', 'bilader görev 357'],
    'komut_358': ['tetik 358', 'işlem 358', 'aksiyon 358', 'bilader görev 358'],
    'komut_359': ['tetik 359', 'işlem 359', 'aksiyon 359', 'bilader görev 359'],
    'komut_360': ['tetik 360', 'işlem 360', 'aksiyon 360', 'bilader görev 360'],
    'komut_361': ['tetik 361', 'işlem 361', 'aksiyon 361', 'bilader görev 361'],
    'komut_362': ['tetik 362', 'işlem 362', 'aksiyon 362', 'bilader görev 362'],
    'komut_363': ['tetik 363', 'işlem 363', 'aksiyon 363', 'bilader görev 363'],
    'komut_364': ['tetik 364', 'işlem 364', 'aksiyon 364', 'bilader görev 364'],
    'komut_365': ['tetik 365', 'işlem 365', 'aksiyon 365', 'bilader görev 365'],
    'komut_366': ['tetik 366', 'işlem 366', 'aksiyon 366', 'bilader görev 366'],
    'komut_367': ['tetik 367', 'işlem 367', 'aksiyon 367', 'bilader görev 367'],
    'komut_368': ['tetik 368', 'işlem 368', 'aksiyon 368', 'bilader görev 368'],
    'komut_369': ['tetik 369', 'işlem 369', 'aksiyon 369', 'bilader görev 369'],
    'komut_370': ['tetik 370', 'işlem 370', 'aksiyon 370', 'bilader görev 370'],
    'komut_371': ['tetik 371', 'işlem 371', 'aksiyon 371', 'bilader görev 371'],
    'komut_372': ['tetik 372', 'işlem 372', 'aksiyon 372', 'bilader görev 372'],
    'komut_373': ['tetik 373', 'işlem 373', 'aksiyon 373', 'bilader görev 373'],
    'komut_374': ['tetik 374', 'işlem 374', 'aksiyon 374', 'bilader görev 374'],
    'komut_375': ['tetik 375', 'işlem 375', 'aksiyon 375', 'bilader görev 375'],
    'komut_376': ['tetik 376', 'işlem 376', 'aksiyon 376', 'bilader görev 376'],
    'komut_377': ['tetik 377', 'işlem 377', 'aksiyon 377', 'bilader görev 377'],
    'komut_378': ['tetik 378', 'işlem 378', 'aksiyon 378', 'bilader görev 378'],
    'komut_379': ['tetik 379', 'işlem 379', 'aksiyon 379', 'bilader görev 379'],
    'komut_380': ['tetik 380', 'işlem 380', 'aksiyon 380', 'bilader görev 380'],
    'komut_381': ['tetik 381', 'işlem 381', 'aksiyon 381', 'bilader görev 381'],
    'komut_382': ['tetik 382', 'işlem 382', 'aksiyon 382', 'bilader görev 382'],
    'komut_383': ['tetik 383', 'işlem 383', 'aksiyon 383', 'bilader görev 383'],
    'komut_384': ['tetik 384', 'işlem 384', 'aksiyon 384', 'bilader görev 384'],
    'komut_385': ['tetik 385', 'işlem 385', 'aksiyon 385', 'bilader görev 385'],
    'komut_386': ['tetik 386', 'işlem 386', 'aksiyon 386', 'bilader görev 386'],
    'komut_387': ['tetik 387', 'işlem 387', 'aksiyon 387', 'bilader görev 387'],
    'komut_388': ['tetik 388', 'işlem 388', 'aksiyon 388', 'bilader görev 388'],
    'komut_389': ['tetik 389', 'işlem 389', 'aksiyon 389', 'bilader görev 389'],
    'komut_390': ['tetik 390', 'işlem 390', 'aksiyon 390', 'bilader görev 390'],
    'komut_391': ['tetik 391', 'işlem 391', 'aksiyon 391', 'bilader görev 391'],
    'komut_392': ['tetik 392', 'işlem 392', 'aksiyon 392', 'bilader görev 392'],
    'komut_393': ['tetik 393', 'işlem 393', 'aksiyon 393', 'bilader görev 393'],
    'komut_394': ['tetik 394', 'işlem 394', 'aksiyon 394', 'bilader görev 394'],
    'komut_395': ['tetik 395', 'işlem 395', 'aksiyon 395', 'bilader görev 395'],
    'komut_396': ['tetik 396', 'işlem 396', 'aksiyon 396', 'bilader görev 396'],
    'komut_397': ['tetik 397', 'işlem 397', 'aksiyon 397', 'bilader görev 397'],
    'komut_398': ['tetik 398', 'işlem 398', 'aksiyon 398', 'bilader görev 398'],
    'komut_399': ['tetik 399', 'işlem 399', 'aksiyon 399', 'bilader görev 399'],
    'komut_400': ['tetik 400', 'işlem 400', 'aksiyon 400', 'bilader görev 400'],
    'komut_401': ['tetik 401', 'işlem 401', 'aksiyon 401', 'bilader görev 401'],
    'komut_402': ['tetik 402', 'işlem 402', 'aksiyon 402', 'bilader görev 402'],
    'komut_403': ['tetik 403', 'işlem 403', 'aksiyon 403', 'bilader görev 403'],
    'komut_404': ['tetik 404', 'işlem 404', 'aksiyon 404', 'bilader görev 404'],
    'komut_405': ['tetik 405', 'işlem 405', 'aksiyon 405', 'bilader görev 405'],
    'komut_406': ['tetik 406', 'işlem 406', 'aksiyon 406', 'bilader görev 406'],
    'komut_407': ['tetik 407', 'işlem 407', 'aksiyon 407', 'bilader görev 407'],
    'komut_408': ['tetik 408', 'işlem 408', 'aksiyon 408', 'bilader görev 408'],
    'komut_409': ['tetik 409', 'işlem 409', 'aksiyon 409', 'bilader görev 409'],
    'komut_410': ['tetik 410', 'işlem 410', 'aksiyon 410', 'bilader görev 410'],
    'komut_411': ['tetik 411', 'işlem 411', 'aksiyon 411', 'bilader görev 411'],
    'komut_412': ['tetik 412', 'işlem 412', 'aksiyon 412', 'bilader görev 412'],
    'komut_413': ['tetik 413', 'işlem 413', 'aksiyon 413', 'bilader görev 413'],
    'komut_414': ['tetik 414', 'işlem 414', 'aksiyon 414', 'bilader görev 414'],
    'komut_415': ['tetik 415', 'işlem 415', 'aksiyon 415', 'bilader görev 415'],
    'komut_416': ['tetik 416', 'işlem 416', 'aksiyon 416', 'bilader görev 416'],
    'komut_417': ['tetik 417', 'işlem 417', 'aksiyon 417', 'bilader görev 417'],
    'komut_418': ['tetik 418', 'işlem 418', 'aksiyon 418', 'bilader görev 418'],
    'komut_419': ['tetik 419', 'işlem 419', 'aksiyon 419', 'bilader görev 419'],
    'komut_420': ['tetik 420', 'işlem 420', 'aksiyon 420', 'bilader görev 420'],
    'komut_421': ['tetik 421', 'işlem 421', 'aksiyon 421', 'bilader görev 421'],
    'komut_422': ['tetik 422', 'işlem 422', 'aksiyon 422', 'bilader görev 422'],
    'komut_423': ['tetik 423', 'işlem 423', 'aksiyon 423', 'bilader görev 423'],
    'komut_424': ['tetik 424', 'işlem 424', 'aksiyon 424', 'bilader görev 424'],
    'komut_425': ['tetik 425', 'işlem 425', 'aksiyon 425', 'bilader görev 425'],
    'komut_426': ['tetik 426', 'işlem 426', 'aksiyon 426', 'bilader görev 426'],
    'komut_427': ['tetik 427', 'işlem 427', 'aksiyon 427', 'bilader görev 427'],
    'komut_428': ['tetik 428', 'işlem 428', 'aksiyon 428', 'bilader görev 428'],
    'komut_429': ['tetik 429', 'işlem 429', 'aksiyon 429', 'bilader görev 429'],
    'komut_430': ['tetik 430', 'işlem 430', 'aksiyon 430', 'bilader görev 430'],
    'komut_431': ['tetik 431', 'işlem 431', 'aksiyon 431', 'bilader görev 431'],
    'komut_432': ['tetik 432', 'işlem 432', 'aksiyon 432', 'bilader görev 432'],
    'komut_433': ['tetik 433', 'işlem 433', 'aksiyon 433', 'bilader görev 433'],
    'komut_434': ['tetik 434', 'işlem 434', 'aksiyon 434', 'bilader görev 434'],
    'komut_435': ['tetik 435', 'işlem 435', 'aksiyon 435', 'bilader görev 435'],
    'komut_436': ['tetik 436', 'işlem 436', 'aksiyon 436', 'bilader görev 436'],
    'komut_437': ['tetik 437', 'işlem 437', 'aksiyon 437', 'bilader görev 437'],
    'komut_438': ['tetik 438', 'işlem 438', 'aksiyon 438', 'bilader görev 438'],
    'komut_439': ['tetik 439', 'işlem 439', 'aksiyon 439', 'bilader görev 439'],
    'komut_440': ['tetik 440', 'işlem 440', 'aksiyon 440', 'bilader görev 440'],
    'komut_441': ['tetik 441', 'işlem 441', 'aksiyon 441', 'bilader görev 441'],
    'komut_442': ['tetik 442', 'işlem 442', 'aksiyon 442', 'bilader görev 442'],
    'komut_443': ['tetik 443', 'işlem 443', 'aksiyon 443', 'bilader görev 443'],
    'komut_444': ['tetik 444', 'işlem 444', 'aksiyon 444', 'bilader görev 444'],
    'komut_445': ['tetik 445', 'işlem 445', 'aksiyon 445', 'bilader görev 445'],
    'komut_446': ['tetik 446', 'işlem 446', 'aksiyon 446', 'bilader görev 446'],
    'komut_447': ['tetik 447', 'işlem 447', 'aksiyon 447', 'bilader görev 447'],
    'komut_448': ['tetik 448', 'işlem 448', 'aksiyon 448', 'bilader görev 448'],
    'komut_449': ['tetik 449', 'işlem 449', 'aksiyon 449', 'bilader görev 449'],
    'komut_450': ['tetik 450', 'işlem 450', 'aksiyon 450', 'bilader görev 450'],
    'komut_451': ['tetik 451', 'işlem 451', 'aksiyon 451', 'bilader görev 451'],
    'komut_452': ['tetik 452', 'işlem 452', 'aksiyon 452', 'bilader görev 452'],
    'komut_453': ['tetik 453', 'işlem 453', 'aksiyon 453', 'bilader görev 453'],
    'komut_454': ['tetik 454', 'işlem 454', 'aksiyon 454', 'bilader görev 454'],
    'komut_455': ['tetik 455', 'işlem 455', 'aksiyon 455', 'bilader görev 455'],
    'komut_456': ['tetik 456', 'işlem 456', 'aksiyon 456', 'bilader görev 456'],
    'komut_457': ['tetik 457', 'işlem 457', 'aksiyon 457', 'bilader görev 457'],
    'komut_458': ['tetik 458', 'işlem 458', 'aksiyon 458', 'bilader görev 458'],
    'komut_459': ['tetik 459', 'işlem 459', 'aksiyon 459', 'bilader görev 459'],
    'komut_460': ['tetik 460', 'işlem 460', 'aksiyon 460', 'bilader görev 460'],
    'komut_461': ['tetik 461', 'işlem 461', 'aksiyon 461', 'bilader görev 461'],
    'komut_462': ['tetik 462', 'işlem 462', 'aksiyon 462', 'bilader görev 462'],
    'komut_463': ['tetik 463', 'işlem 463', 'aksiyon 463', 'bilader görev 463'],
    'komut_464': ['tetik 464', 'işlem 464', 'aksiyon 464', 'bilader görev 464'],
    'komut_465': ['tetik 465', 'işlem 465', 'aksiyon 465', 'bilader görev 465'],
    'komut_466': ['tetik 466', 'işlem 466', 'aksiyon 466', 'bilader görev 466'],
    'komut_467': ['tetik 467', 'işlem 467', 'aksiyon 467', 'bilader görev 467'],
    'komut_468': ['tetik 468', 'işlem 468', 'aksiyon 468', 'bilader görev 468'],
    'komut_469': ['tetik 469', 'işlem 469', 'aksiyon 469', 'bilader görev 469'],
    'komut_470': ['tetik 470', 'işlem 470', 'aksiyon 470', 'bilader görev 470'],
    'komut_471': ['tetik 471', 'işlem 471', 'aksiyon 471', 'bilader görev 471'],
    'komut_472': ['tetik 472', 'işlem 472', 'aksiyon 472', 'bilader görev 472'],
    'komut_473': ['tetik 473', 'işlem 473', 'aksiyon 473', 'bilader görev 473'],
    'komut_474': ['tetik 474', 'işlem 474', 'aksiyon 474', 'bilader görev 474'],
    'komut_475': ['tetik 475', 'işlem 475', 'aksiyon 475', 'bilader görev 475'],
    'komut_476': ['tetik 476', 'işlem 476', 'aksiyon 476', 'bilader görev 476'],
    'komut_477': ['tetik 477', 'işlem 477', 'aksiyon 477', 'bilader görev 477'],
    'komut_478': ['tetik 478', 'işlem 478', 'aksiyon 478', 'bilader görev 478'],
    'komut_479': ['tetik 479', 'işlem 479', 'aksiyon 479', 'bilader görev 479'],
    'komut_480': ['tetik 480', 'işlem 480', 'aksiyon 480', 'bilader görev 480'],
    'komut_481': ['tetik 481', 'işlem 481', 'aksiyon 481', 'bilader görev 481'],
    'komut_482': ['tetik 482', 'işlem 482', 'aksiyon 482', 'bilader görev 482'],
    'komut_483': ['tetik 483', 'işlem 483', 'aksiyon 483', 'bilader görev 483'],
    'komut_484': ['tetik 484', 'işlem 484', 'aksiyon 484', 'bilader görev 484'],
    'komut_485': ['tetik 485', 'işlem 485', 'aksiyon 485', 'bilader görev 485'],
    'komut_486': ['tetik 486', 'işlem 486', 'aksiyon 486', 'bilader görev 486'],
    'komut_487': ['tetik 487', 'işlem 487', 'aksiyon 487', 'bilader görev 487'],
    'komut_488': ['tetik 488', 'işlem 488', 'aksiyon 488', 'bilader görev 488'],
    'komut_489': ['tetik 489', 'işlem 489', 'aksiyon 489', 'bilader görev 489'],
    'komut_490': ['tetik 490', 'işlem 490', 'aksiyon 490', 'bilader görev 490'],
    'komut_491': ['tetik 491', 'işlem 491', 'aksiyon 491', 'bilader görev 491'],
    'komut_492': ['tetik 492', 'işlem 492', 'aksiyon 492', 'bilader görev 492'],
    'komut_493': ['tetik 493', 'işlem 493', 'aksiyon 493', 'bilader görev 493'],
    'komut_494': ['tetik 494', 'işlem 494', 'aksiyon 494', 'bilader görev 494'],
    'komut_495': ['tetik 495', 'işlem 495', 'aksiyon 495', 'bilader görev 495'],
    'komut_496': ['tetik 496', 'işlem 496', 'aksiyon 496', 'bilader görev 496'],
    'komut_497': ['tetik 497', 'işlem 497', 'aksiyon 497', 'bilader görev 497'],
    'komut_498': ['tetik 498', 'işlem 498', 'aksiyon 498', 'bilader görev 498'],
    'komut_499': ['tetik 499', 'işlem 499', 'aksiyon 499', 'bilader görev 499'],
    'komut_500': ['tetik 500', 'işlem 500', 'aksiyon 500', 'bilader görev 500'],
}

INTENT_RESPONSE_BANK: Dict[str, str] = {
    'yanit_001': 'Hazırım bilader, 1. senaryo için sistem beklemede.',
    'yanit_002': 'Hazırım bilader, 2. senaryo için sistem beklemede.',
    'yanit_003': 'Hazırım bilader, 3. senaryo için sistem beklemede.',
    'yanit_004': 'Hazırım bilader, 4. senaryo için sistem beklemede.',
    'yanit_005': 'Hazırım bilader, 5. senaryo için sistem beklemede.',
    'yanit_006': 'Hazırım bilader, 6. senaryo için sistem beklemede.',
    'yanit_007': 'Hazırım bilader, 7. senaryo için sistem beklemede.',
    'yanit_008': 'Hazırım bilader, 8. senaryo için sistem beklemede.',
    'yanit_009': 'Hazırım bilader, 9. senaryo için sistem beklemede.',
    'yanit_010': 'Hazırım bilader, 10. senaryo için sistem beklemede.',
    'yanit_011': 'Hazırım bilader, 11. senaryo için sistem beklemede.',
    'yanit_012': 'Hazırım bilader, 12. senaryo için sistem beklemede.',
    'yanit_013': 'Hazırım bilader, 13. senaryo için sistem beklemede.',
    'yanit_014': 'Hazırım bilader, 14. senaryo için sistem beklemede.',
    'yanit_015': 'Hazırım bilader, 15. senaryo için sistem beklemede.',
    'yanit_016': 'Hazırım bilader, 16. senaryo için sistem beklemede.',
    'yanit_017': 'Hazırım bilader, 17. senaryo için sistem beklemede.',
    'yanit_018': 'Hazırım bilader, 18. senaryo için sistem beklemede.',
    'yanit_019': 'Hazırım bilader, 19. senaryo için sistem beklemede.',
    'yanit_020': 'Hazırım bilader, 20. senaryo için sistem beklemede.',
    'yanit_021': 'Hazırım bilader, 21. senaryo için sistem beklemede.',
    'yanit_022': 'Hazırım bilader, 22. senaryo için sistem beklemede.',
    'yanit_023': 'Hazırım bilader, 23. senaryo için sistem beklemede.',
    'yanit_024': 'Hazırım bilader, 24. senaryo için sistem beklemede.',
    'yanit_025': 'Hazırım bilader, 25. senaryo için sistem beklemede.',
    'yanit_026': 'Hazırım bilader, 26. senaryo için sistem beklemede.',
    'yanit_027': 'Hazırım bilader, 27. senaryo için sistem beklemede.',
    'yanit_028': 'Hazırım bilader, 28. senaryo için sistem beklemede.',
    'yanit_029': 'Hazırım bilader, 29. senaryo için sistem beklemede.',
    'yanit_030': 'Hazırım bilader, 30. senaryo için sistem beklemede.',
    'yanit_031': 'Hazırım bilader, 31. senaryo için sistem beklemede.',
    'yanit_032': 'Hazırım bilader, 32. senaryo için sistem beklemede.',
    'yanit_033': 'Hazırım bilader, 33. senaryo için sistem beklemede.',
    'yanit_034': 'Hazırım bilader, 34. senaryo için sistem beklemede.',
    'yanit_035': 'Hazırım bilader, 35. senaryo için sistem beklemede.',
    'yanit_036': 'Hazırım bilader, 36. senaryo için sistem beklemede.',
    'yanit_037': 'Hazırım bilader, 37. senaryo için sistem beklemede.',
    'yanit_038': 'Hazırım bilader, 38. senaryo için sistem beklemede.',
    'yanit_039': 'Hazırım bilader, 39. senaryo için sistem beklemede.',
    'yanit_040': 'Hazırım bilader, 40. senaryo için sistem beklemede.',
    'yanit_041': 'Hazırım bilader, 41. senaryo için sistem beklemede.',
    'yanit_042': 'Hazırım bilader, 42. senaryo için sistem beklemede.',
    'yanit_043': 'Hazırım bilader, 43. senaryo için sistem beklemede.',
    'yanit_044': 'Hazırım bilader, 44. senaryo için sistem beklemede.',
    'yanit_045': 'Hazırım bilader, 45. senaryo için sistem beklemede.',
    'yanit_046': 'Hazırım bilader, 46. senaryo için sistem beklemede.',
    'yanit_047': 'Hazırım bilader, 47. senaryo için sistem beklemede.',
    'yanit_048': 'Hazırım bilader, 48. senaryo için sistem beklemede.',
    'yanit_049': 'Hazırım bilader, 49. senaryo için sistem beklemede.',
    'yanit_050': 'Hazırım bilader, 50. senaryo için sistem beklemede.',
    'yanit_051': 'Hazırım bilader, 51. senaryo için sistem beklemede.',
    'yanit_052': 'Hazırım bilader, 52. senaryo için sistem beklemede.',
    'yanit_053': 'Hazırım bilader, 53. senaryo için sistem beklemede.',
    'yanit_054': 'Hazırım bilader, 54. senaryo için sistem beklemede.',
    'yanit_055': 'Hazırım bilader, 55. senaryo için sistem beklemede.',
    'yanit_056': 'Hazırım bilader, 56. senaryo için sistem beklemede.',
    'yanit_057': 'Hazırım bilader, 57. senaryo için sistem beklemede.',
    'yanit_058': 'Hazırım bilader, 58. senaryo için sistem beklemede.',
    'yanit_059': 'Hazırım bilader, 59. senaryo için sistem beklemede.',
    'yanit_060': 'Hazırım bilader, 60. senaryo için sistem beklemede.',
    'yanit_061': 'Hazırım bilader, 61. senaryo için sistem beklemede.',
    'yanit_062': 'Hazırım bilader, 62. senaryo için sistem beklemede.',
    'yanit_063': 'Hazırım bilader, 63. senaryo için sistem beklemede.',
    'yanit_064': 'Hazırım bilader, 64. senaryo için sistem beklemede.',
    'yanit_065': 'Hazırım bilader, 65. senaryo için sistem beklemede.',
    'yanit_066': 'Hazırım bilader, 66. senaryo için sistem beklemede.',
    'yanit_067': 'Hazırım bilader, 67. senaryo için sistem beklemede.',
    'yanit_068': 'Hazırım bilader, 68. senaryo için sistem beklemede.',
    'yanit_069': 'Hazırım bilader, 69. senaryo için sistem beklemede.',
    'yanit_070': 'Hazırım bilader, 70. senaryo için sistem beklemede.',
    'yanit_071': 'Hazırım bilader, 71. senaryo için sistem beklemede.',
    'yanit_072': 'Hazırım bilader, 72. senaryo için sistem beklemede.',
    'yanit_073': 'Hazırım bilader, 73. senaryo için sistem beklemede.',
    'yanit_074': 'Hazırım bilader, 74. senaryo için sistem beklemede.',
    'yanit_075': 'Hazırım bilader, 75. senaryo için sistem beklemede.',
    'yanit_076': 'Hazırım bilader, 76. senaryo için sistem beklemede.',
    'yanit_077': 'Hazırım bilader, 77. senaryo için sistem beklemede.',
    'yanit_078': 'Hazırım bilader, 78. senaryo için sistem beklemede.',
    'yanit_079': 'Hazırım bilader, 79. senaryo için sistem beklemede.',
    'yanit_080': 'Hazırım bilader, 80. senaryo için sistem beklemede.',
    'yanit_081': 'Hazırım bilader, 81. senaryo için sistem beklemede.',
    'yanit_082': 'Hazırım bilader, 82. senaryo için sistem beklemede.',
    'yanit_083': 'Hazırım bilader, 83. senaryo için sistem beklemede.',
    'yanit_084': 'Hazırım bilader, 84. senaryo için sistem beklemede.',
    'yanit_085': 'Hazırım bilader, 85. senaryo için sistem beklemede.',
    'yanit_086': 'Hazırım bilader, 86. senaryo için sistem beklemede.',
    'yanit_087': 'Hazırım bilader, 87. senaryo için sistem beklemede.',
    'yanit_088': 'Hazırım bilader, 88. senaryo için sistem beklemede.',
    'yanit_089': 'Hazırım bilader, 89. senaryo için sistem beklemede.',
    'yanit_090': 'Hazırım bilader, 90. senaryo için sistem beklemede.',
    'yanit_091': 'Hazırım bilader, 91. senaryo için sistem beklemede.',
    'yanit_092': 'Hazırım bilader, 92. senaryo için sistem beklemede.',
    'yanit_093': 'Hazırım bilader, 93. senaryo için sistem beklemede.',
    'yanit_094': 'Hazırım bilader, 94. senaryo için sistem beklemede.',
    'yanit_095': 'Hazırım bilader, 95. senaryo için sistem beklemede.',
    'yanit_096': 'Hazırım bilader, 96. senaryo için sistem beklemede.',
    'yanit_097': 'Hazırım bilader, 97. senaryo için sistem beklemede.',
    'yanit_098': 'Hazırım bilader, 98. senaryo için sistem beklemede.',
    'yanit_099': 'Hazırım bilader, 99. senaryo için sistem beklemede.',
    'yanit_100': 'Hazırım bilader, 100. senaryo için sistem beklemede.',
    'yanit_101': 'Hazırım bilader, 101. senaryo için sistem beklemede.',
    'yanit_102': 'Hazırım bilader, 102. senaryo için sistem beklemede.',
    'yanit_103': 'Hazırım bilader, 103. senaryo için sistem beklemede.',
    'yanit_104': 'Hazırım bilader, 104. senaryo için sistem beklemede.',
    'yanit_105': 'Hazırım bilader, 105. senaryo için sistem beklemede.',
    'yanit_106': 'Hazırım bilader, 106. senaryo için sistem beklemede.',
    'yanit_107': 'Hazırım bilader, 107. senaryo için sistem beklemede.',
    'yanit_108': 'Hazırım bilader, 108. senaryo için sistem beklemede.',
    'yanit_109': 'Hazırım bilader, 109. senaryo için sistem beklemede.',
    'yanit_110': 'Hazırım bilader, 110. senaryo için sistem beklemede.',
    'yanit_111': 'Hazırım bilader, 111. senaryo için sistem beklemede.',
    'yanit_112': 'Hazırım bilader, 112. senaryo için sistem beklemede.',
    'yanit_113': 'Hazırım bilader, 113. senaryo için sistem beklemede.',
    'yanit_114': 'Hazırım bilader, 114. senaryo için sistem beklemede.',
    'yanit_115': 'Hazırım bilader, 115. senaryo için sistem beklemede.',
    'yanit_116': 'Hazırım bilader, 116. senaryo için sistem beklemede.',
    'yanit_117': 'Hazırım bilader, 117. senaryo için sistem beklemede.',
    'yanit_118': 'Hazırım bilader, 118. senaryo için sistem beklemede.',
    'yanit_119': 'Hazırım bilader, 119. senaryo için sistem beklemede.',
    'yanit_120': 'Hazırım bilader, 120. senaryo için sistem beklemede.',
    'yanit_121': 'Hazırım bilader, 121. senaryo için sistem beklemede.',
    'yanit_122': 'Hazırım bilader, 122. senaryo için sistem beklemede.',
    'yanit_123': 'Hazırım bilader, 123. senaryo için sistem beklemede.',
    'yanit_124': 'Hazırım bilader, 124. senaryo için sistem beklemede.',
    'yanit_125': 'Hazırım bilader, 125. senaryo için sistem beklemede.',
    'yanit_126': 'Hazırım bilader, 126. senaryo için sistem beklemede.',
    'yanit_127': 'Hazırım bilader, 127. senaryo için sistem beklemede.',
    'yanit_128': 'Hazırım bilader, 128. senaryo için sistem beklemede.',
    'yanit_129': 'Hazırım bilader, 129. senaryo için sistem beklemede.',
    'yanit_130': 'Hazırım bilader, 130. senaryo için sistem beklemede.',
    'yanit_131': 'Hazırım bilader, 131. senaryo için sistem beklemede.',
    'yanit_132': 'Hazırım bilader, 132. senaryo için sistem beklemede.',
    'yanit_133': 'Hazırım bilader, 133. senaryo için sistem beklemede.',
    'yanit_134': 'Hazırım bilader, 134. senaryo için sistem beklemede.',
    'yanit_135': 'Hazırım bilader, 135. senaryo için sistem beklemede.',
    'yanit_136': 'Hazırım bilader, 136. senaryo için sistem beklemede.',
    'yanit_137': 'Hazırım bilader, 137. senaryo için sistem beklemede.',
    'yanit_138': 'Hazırım bilader, 138. senaryo için sistem beklemede.',
    'yanit_139': 'Hazırım bilader, 139. senaryo için sistem beklemede.',
    'yanit_140': 'Hazırım bilader, 140. senaryo için sistem beklemede.',
    'yanit_141': 'Hazırım bilader, 141. senaryo için sistem beklemede.',
    'yanit_142': 'Hazırım bilader, 142. senaryo için sistem beklemede.',
    'yanit_143': 'Hazırım bilader, 143. senaryo için sistem beklemede.',
    'yanit_144': 'Hazırım bilader, 144. senaryo için sistem beklemede.',
    'yanit_145': 'Hazırım bilader, 145. senaryo için sistem beklemede.',
    'yanit_146': 'Hazırım bilader, 146. senaryo için sistem beklemede.',
    'yanit_147': 'Hazırım bilader, 147. senaryo için sistem beklemede.',
    'yanit_148': 'Hazırım bilader, 148. senaryo için sistem beklemede.',
    'yanit_149': 'Hazırım bilader, 149. senaryo için sistem beklemede.',
    'yanit_150': 'Hazırım bilader, 150. senaryo için sistem beklemede.',
    'yanit_151': 'Hazırım bilader, 151. senaryo için sistem beklemede.',
    'yanit_152': 'Hazırım bilader, 152. senaryo için sistem beklemede.',
    'yanit_153': 'Hazırım bilader, 153. senaryo için sistem beklemede.',
    'yanit_154': 'Hazırım bilader, 154. senaryo için sistem beklemede.',
    'yanit_155': 'Hazırım bilader, 155. senaryo için sistem beklemede.',
    'yanit_156': 'Hazırım bilader, 156. senaryo için sistem beklemede.',
    'yanit_157': 'Hazırım bilader, 157. senaryo için sistem beklemede.',
    'yanit_158': 'Hazırım bilader, 158. senaryo için sistem beklemede.',
    'yanit_159': 'Hazırım bilader, 159. senaryo için sistem beklemede.',
    'yanit_160': 'Hazırım bilader, 160. senaryo için sistem beklemede.',
    'yanit_161': 'Hazırım bilader, 161. senaryo için sistem beklemede.',
    'yanit_162': 'Hazırım bilader, 162. senaryo için sistem beklemede.',
    'yanit_163': 'Hazırım bilader, 163. senaryo için sistem beklemede.',
    'yanit_164': 'Hazırım bilader, 164. senaryo için sistem beklemede.',
    'yanit_165': 'Hazırım bilader, 165. senaryo için sistem beklemede.',
    'yanit_166': 'Hazırım bilader, 166. senaryo için sistem beklemede.',
    'yanit_167': 'Hazırım bilader, 167. senaryo için sistem beklemede.',
    'yanit_168': 'Hazırım bilader, 168. senaryo için sistem beklemede.',
    'yanit_169': 'Hazırım bilader, 169. senaryo için sistem beklemede.',
    'yanit_170': 'Hazırım bilader, 170. senaryo için sistem beklemede.',
    'yanit_171': 'Hazırım bilader, 171. senaryo için sistem beklemede.',
    'yanit_172': 'Hazırım bilader, 172. senaryo için sistem beklemede.',
    'yanit_173': 'Hazırım bilader, 173. senaryo için sistem beklemede.',
    'yanit_174': 'Hazırım bilader, 174. senaryo için sistem beklemede.',
    'yanit_175': 'Hazırım bilader, 175. senaryo için sistem beklemede.',
    'yanit_176': 'Hazırım bilader, 176. senaryo için sistem beklemede.',
    'yanit_177': 'Hazırım bilader, 177. senaryo için sistem beklemede.',
    'yanit_178': 'Hazırım bilader, 178. senaryo için sistem beklemede.',
    'yanit_179': 'Hazırım bilader, 179. senaryo için sistem beklemede.',
    'yanit_180': 'Hazırım bilader, 180. senaryo için sistem beklemede.',
    'yanit_181': 'Hazırım bilader, 181. senaryo için sistem beklemede.',
    'yanit_182': 'Hazırım bilader, 182. senaryo için sistem beklemede.',
    'yanit_183': 'Hazırım bilader, 183. senaryo için sistem beklemede.',
    'yanit_184': 'Hazırım bilader, 184. senaryo için sistem beklemede.',
    'yanit_185': 'Hazırım bilader, 185. senaryo için sistem beklemede.',
    'yanit_186': 'Hazırım bilader, 186. senaryo için sistem beklemede.',
    'yanit_187': 'Hazırım bilader, 187. senaryo için sistem beklemede.',
    'yanit_188': 'Hazırım bilader, 188. senaryo için sistem beklemede.',
    'yanit_189': 'Hazırım bilader, 189. senaryo için sistem beklemede.',
    'yanit_190': 'Hazırım bilader, 190. senaryo için sistem beklemede.',
    'yanit_191': 'Hazırım bilader, 191. senaryo için sistem beklemede.',
    'yanit_192': 'Hazırım bilader, 192. senaryo için sistem beklemede.',
    'yanit_193': 'Hazırım bilader, 193. senaryo için sistem beklemede.',
    'yanit_194': 'Hazırım bilader, 194. senaryo için sistem beklemede.',
    'yanit_195': 'Hazırım bilader, 195. senaryo için sistem beklemede.',
    'yanit_196': 'Hazırım bilader, 196. senaryo için sistem beklemede.',
    'yanit_197': 'Hazırım bilader, 197. senaryo için sistem beklemede.',
    'yanit_198': 'Hazırım bilader, 198. senaryo için sistem beklemede.',
    'yanit_199': 'Hazırım bilader, 199. senaryo için sistem beklemede.',
    'yanit_200': 'Hazırım bilader, 200. senaryo için sistem beklemede.',
    'yanit_201': 'Hazırım bilader, 201. senaryo için sistem beklemede.',
    'yanit_202': 'Hazırım bilader, 202. senaryo için sistem beklemede.',
    'yanit_203': 'Hazırım bilader, 203. senaryo için sistem beklemede.',
    'yanit_204': 'Hazırım bilader, 204. senaryo için sistem beklemede.',
    'yanit_205': 'Hazırım bilader, 205. senaryo için sistem beklemede.',
    'yanit_206': 'Hazırım bilader, 206. senaryo için sistem beklemede.',
    'yanit_207': 'Hazırım bilader, 207. senaryo için sistem beklemede.',
    'yanit_208': 'Hazırım bilader, 208. senaryo için sistem beklemede.',
    'yanit_209': 'Hazırım bilader, 209. senaryo için sistem beklemede.',
    'yanit_210': 'Hazırım bilader, 210. senaryo için sistem beklemede.',
    'yanit_211': 'Hazırım bilader, 211. senaryo için sistem beklemede.',
    'yanit_212': 'Hazırım bilader, 212. senaryo için sistem beklemede.',
    'yanit_213': 'Hazırım bilader, 213. senaryo için sistem beklemede.',
    'yanit_214': 'Hazırım bilader, 214. senaryo için sistem beklemede.',
    'yanit_215': 'Hazırım bilader, 215. senaryo için sistem beklemede.',
    'yanit_216': 'Hazırım bilader, 216. senaryo için sistem beklemede.',
    'yanit_217': 'Hazırım bilader, 217. senaryo için sistem beklemede.',
    'yanit_218': 'Hazırım bilader, 218. senaryo için sistem beklemede.',
    'yanit_219': 'Hazırım bilader, 219. senaryo için sistem beklemede.',
    'yanit_220': 'Hazırım bilader, 220. senaryo için sistem beklemede.',
    'yanit_221': 'Hazırım bilader, 221. senaryo için sistem beklemede.',
    'yanit_222': 'Hazırım bilader, 222. senaryo için sistem beklemede.',
    'yanit_223': 'Hazırım bilader, 223. senaryo için sistem beklemede.',
    'yanit_224': 'Hazırım bilader, 224. senaryo için sistem beklemede.',
    'yanit_225': 'Hazırım bilader, 225. senaryo için sistem beklemede.',
    'yanit_226': 'Hazırım bilader, 226. senaryo için sistem beklemede.',
    'yanit_227': 'Hazırım bilader, 227. senaryo için sistem beklemede.',
    'yanit_228': 'Hazırım bilader, 228. senaryo için sistem beklemede.',
    'yanit_229': 'Hazırım bilader, 229. senaryo için sistem beklemede.',
    'yanit_230': 'Hazırım bilader, 230. senaryo için sistem beklemede.',
    'yanit_231': 'Hazırım bilader, 231. senaryo için sistem beklemede.',
    'yanit_232': 'Hazırım bilader, 232. senaryo için sistem beklemede.',
    'yanit_233': 'Hazırım bilader, 233. senaryo için sistem beklemede.',
    'yanit_234': 'Hazırım bilader, 234. senaryo için sistem beklemede.',
    'yanit_235': 'Hazırım bilader, 235. senaryo için sistem beklemede.',
    'yanit_236': 'Hazırım bilader, 236. senaryo için sistem beklemede.',
    'yanit_237': 'Hazırım bilader, 237. senaryo için sistem beklemede.',
    'yanit_238': 'Hazırım bilader, 238. senaryo için sistem beklemede.',
    'yanit_239': 'Hazırım bilader, 239. senaryo için sistem beklemede.',
    'yanit_240': 'Hazırım bilader, 240. senaryo için sistem beklemede.',
    'yanit_241': 'Hazırım bilader, 241. senaryo için sistem beklemede.',
    'yanit_242': 'Hazırım bilader, 242. senaryo için sistem beklemede.',
    'yanit_243': 'Hazırım bilader, 243. senaryo için sistem beklemede.',
    'yanit_244': 'Hazırım bilader, 244. senaryo için sistem beklemede.',
    'yanit_245': 'Hazırım bilader, 245. senaryo için sistem beklemede.',
    'yanit_246': 'Hazırım bilader, 246. senaryo için sistem beklemede.',
    'yanit_247': 'Hazırım bilader, 247. senaryo için sistem beklemede.',
    'yanit_248': 'Hazırım bilader, 248. senaryo için sistem beklemede.',
    'yanit_249': 'Hazırım bilader, 249. senaryo için sistem beklemede.',
    'yanit_250': 'Hazırım bilader, 250. senaryo için sistem beklemede.',
    'yanit_251': 'Hazırım bilader, 251. senaryo için sistem beklemede.',
    'yanit_252': 'Hazırım bilader, 252. senaryo için sistem beklemede.',
    'yanit_253': 'Hazırım bilader, 253. senaryo için sistem beklemede.',
    'yanit_254': 'Hazırım bilader, 254. senaryo için sistem beklemede.',
    'yanit_255': 'Hazırım bilader, 255. senaryo için sistem beklemede.',
    'yanit_256': 'Hazırım bilader, 256. senaryo için sistem beklemede.',
    'yanit_257': 'Hazırım bilader, 257. senaryo için sistem beklemede.',
    'yanit_258': 'Hazırım bilader, 258. senaryo için sistem beklemede.',
    'yanit_259': 'Hazırım bilader, 259. senaryo için sistem beklemede.',
    'yanit_260': 'Hazırım bilader, 260. senaryo için sistem beklemede.',
    'yanit_261': 'Hazırım bilader, 261. senaryo için sistem beklemede.',
    'yanit_262': 'Hazırım bilader, 262. senaryo için sistem beklemede.',
    'yanit_263': 'Hazırım bilader, 263. senaryo için sistem beklemede.',
    'yanit_264': 'Hazırım bilader, 264. senaryo için sistem beklemede.',
    'yanit_265': 'Hazırım bilader, 265. senaryo için sistem beklemede.',
    'yanit_266': 'Hazırım bilader, 266. senaryo için sistem beklemede.',
    'yanit_267': 'Hazırım bilader, 267. senaryo için sistem beklemede.',
    'yanit_268': 'Hazırım bilader, 268. senaryo için sistem beklemede.',
    'yanit_269': 'Hazırım bilader, 269. senaryo için sistem beklemede.',
    'yanit_270': 'Hazırım bilader, 270. senaryo için sistem beklemede.',
    'yanit_271': 'Hazırım bilader, 271. senaryo için sistem beklemede.',
    'yanit_272': 'Hazırım bilader, 272. senaryo için sistem beklemede.',
    'yanit_273': 'Hazırım bilader, 273. senaryo için sistem beklemede.',
    'yanit_274': 'Hazırım bilader, 274. senaryo için sistem beklemede.',
    'yanit_275': 'Hazırım bilader, 275. senaryo için sistem beklemede.',
    'yanit_276': 'Hazırım bilader, 276. senaryo için sistem beklemede.',
    'yanit_277': 'Hazırım bilader, 277. senaryo için sistem beklemede.',
    'yanit_278': 'Hazırım bilader, 278. senaryo için sistem beklemede.',
    'yanit_279': 'Hazırım bilader, 279. senaryo için sistem beklemede.',
    'yanit_280': 'Hazırım bilader, 280. senaryo için sistem beklemede.',
    'yanit_281': 'Hazırım bilader, 281. senaryo için sistem beklemede.',
    'yanit_282': 'Hazırım bilader, 282. senaryo için sistem beklemede.',
    'yanit_283': 'Hazırım bilader, 283. senaryo için sistem beklemede.',
    'yanit_284': 'Hazırım bilader, 284. senaryo için sistem beklemede.',
    'yanit_285': 'Hazırım bilader, 285. senaryo için sistem beklemede.',
    'yanit_286': 'Hazırım bilader, 286. senaryo için sistem beklemede.',
    'yanit_287': 'Hazırım bilader, 287. senaryo için sistem beklemede.',
    'yanit_288': 'Hazırım bilader, 288. senaryo için sistem beklemede.',
    'yanit_289': 'Hazırım bilader, 289. senaryo için sistem beklemede.',
    'yanit_290': 'Hazırım bilader, 290. senaryo için sistem beklemede.',
    'yanit_291': 'Hazırım bilader, 291. senaryo için sistem beklemede.',
    'yanit_292': 'Hazırım bilader, 292. senaryo için sistem beklemede.',
    'yanit_293': 'Hazırım bilader, 293. senaryo için sistem beklemede.',
    'yanit_294': 'Hazırım bilader, 294. senaryo için sistem beklemede.',
    'yanit_295': 'Hazırım bilader, 295. senaryo için sistem beklemede.',
    'yanit_296': 'Hazırım bilader, 296. senaryo için sistem beklemede.',
    'yanit_297': 'Hazırım bilader, 297. senaryo için sistem beklemede.',
    'yanit_298': 'Hazırım bilader, 298. senaryo için sistem beklemede.',
    'yanit_299': 'Hazırım bilader, 299. senaryo için sistem beklemede.',
    'yanit_300': 'Hazırım bilader, 300. senaryo için sistem beklemede.',
    'yanit_301': 'Hazırım bilader, 301. senaryo için sistem beklemede.',
    'yanit_302': 'Hazırım bilader, 302. senaryo için sistem beklemede.',
    'yanit_303': 'Hazırım bilader, 303. senaryo için sistem beklemede.',
    'yanit_304': 'Hazırım bilader, 304. senaryo için sistem beklemede.',
    'yanit_305': 'Hazırım bilader, 305. senaryo için sistem beklemede.',
    'yanit_306': 'Hazırım bilader, 306. senaryo için sistem beklemede.',
    'yanit_307': 'Hazırım bilader, 307. senaryo için sistem beklemede.',
    'yanit_308': 'Hazırım bilader, 308. senaryo için sistem beklemede.',
    'yanit_309': 'Hazırım bilader, 309. senaryo için sistem beklemede.',
    'yanit_310': 'Hazırım bilader, 310. senaryo için sistem beklemede.',
    'yanit_311': 'Hazırım bilader, 311. senaryo için sistem beklemede.',
    'yanit_312': 'Hazırım bilader, 312. senaryo için sistem beklemede.',
    'yanit_313': 'Hazırım bilader, 313. senaryo için sistem beklemede.',
    'yanit_314': 'Hazırım bilader, 314. senaryo için sistem beklemede.',
    'yanit_315': 'Hazırım bilader, 315. senaryo için sistem beklemede.',
    'yanit_316': 'Hazırım bilader, 316. senaryo için sistem beklemede.',
    'yanit_317': 'Hazırım bilader, 317. senaryo için sistem beklemede.',
    'yanit_318': 'Hazırım bilader, 318. senaryo için sistem beklemede.',
    'yanit_319': 'Hazırım bilader, 319. senaryo için sistem beklemede.',
    'yanit_320': 'Hazırım bilader, 320. senaryo için sistem beklemede.',
    'yanit_321': 'Hazırım bilader, 321. senaryo için sistem beklemede.',
    'yanit_322': 'Hazırım bilader, 322. senaryo için sistem beklemede.',
    'yanit_323': 'Hazırım bilader, 323. senaryo için sistem beklemede.',
    'yanit_324': 'Hazırım bilader, 324. senaryo için sistem beklemede.',
    'yanit_325': 'Hazırım bilader, 325. senaryo için sistem beklemede.',
    'yanit_326': 'Hazırım bilader, 326. senaryo için sistem beklemede.',
    'yanit_327': 'Hazırım bilader, 327. senaryo için sistem beklemede.',
    'yanit_328': 'Hazırım bilader, 328. senaryo için sistem beklemede.',
    'yanit_329': 'Hazırım bilader, 329. senaryo için sistem beklemede.',
    'yanit_330': 'Hazırım bilader, 330. senaryo için sistem beklemede.',
    'yanit_331': 'Hazırım bilader, 331. senaryo için sistem beklemede.',
    'yanit_332': 'Hazırım bilader, 332. senaryo için sistem beklemede.',
    'yanit_333': 'Hazırım bilader, 333. senaryo için sistem beklemede.',
    'yanit_334': 'Hazırım bilader, 334. senaryo için sistem beklemede.',
    'yanit_335': 'Hazırım bilader, 335. senaryo için sistem beklemede.',
    'yanit_336': 'Hazırım bilader, 336. senaryo için sistem beklemede.',
    'yanit_337': 'Hazırım bilader, 337. senaryo için sistem beklemede.',
    'yanit_338': 'Hazırım bilader, 338. senaryo için sistem beklemede.',
    'yanit_339': 'Hazırım bilader, 339. senaryo için sistem beklemede.',
    'yanit_340': 'Hazırım bilader, 340. senaryo için sistem beklemede.',
    'yanit_341': 'Hazırım bilader, 341. senaryo için sistem beklemede.',
    'yanit_342': 'Hazırım bilader, 342. senaryo için sistem beklemede.',
    'yanit_343': 'Hazırım bilader, 343. senaryo için sistem beklemede.',
    'yanit_344': 'Hazırım bilader, 344. senaryo için sistem beklemede.',
    'yanit_345': 'Hazırım bilader, 345. senaryo için sistem beklemede.',
    'yanit_346': 'Hazırım bilader, 346. senaryo için sistem beklemede.',
    'yanit_347': 'Hazırım bilader, 347. senaryo için sistem beklemede.',
    'yanit_348': 'Hazırım bilader, 348. senaryo için sistem beklemede.',
    'yanit_349': 'Hazırım bilader, 349. senaryo için sistem beklemede.',
    'yanit_350': 'Hazırım bilader, 350. senaryo için sistem beklemede.',
    'yanit_351': 'Hazırım bilader, 351. senaryo için sistem beklemede.',
    'yanit_352': 'Hazırım bilader, 352. senaryo için sistem beklemede.',
    'yanit_353': 'Hazırım bilader, 353. senaryo için sistem beklemede.',
    'yanit_354': 'Hazırım bilader, 354. senaryo için sistem beklemede.',
    'yanit_355': 'Hazırım bilader, 355. senaryo için sistem beklemede.',
    'yanit_356': 'Hazırım bilader, 356. senaryo için sistem beklemede.',
    'yanit_357': 'Hazırım bilader, 357. senaryo için sistem beklemede.',
    'yanit_358': 'Hazırım bilader, 358. senaryo için sistem beklemede.',
    'yanit_359': 'Hazırım bilader, 359. senaryo için sistem beklemede.',
    'yanit_360': 'Hazırım bilader, 360. senaryo için sistem beklemede.',
    'yanit_361': 'Hazırım bilader, 361. senaryo için sistem beklemede.',
    'yanit_362': 'Hazırım bilader, 362. senaryo için sistem beklemede.',
    'yanit_363': 'Hazırım bilader, 363. senaryo için sistem beklemede.',
    'yanit_364': 'Hazırım bilader, 364. senaryo için sistem beklemede.',
    'yanit_365': 'Hazırım bilader, 365. senaryo için sistem beklemede.',
    'yanit_366': 'Hazırım bilader, 366. senaryo için sistem beklemede.',
    'yanit_367': 'Hazırım bilader, 367. senaryo için sistem beklemede.',
    'yanit_368': 'Hazırım bilader, 368. senaryo için sistem beklemede.',
    'yanit_369': 'Hazırım bilader, 369. senaryo için sistem beklemede.',
    'yanit_370': 'Hazırım bilader, 370. senaryo için sistem beklemede.',
    'yanit_371': 'Hazırım bilader, 371. senaryo için sistem beklemede.',
    'yanit_372': 'Hazırım bilader, 372. senaryo için sistem beklemede.',
    'yanit_373': 'Hazırım bilader, 373. senaryo için sistem beklemede.',
    'yanit_374': 'Hazırım bilader, 374. senaryo için sistem beklemede.',
    'yanit_375': 'Hazırım bilader, 375. senaryo için sistem beklemede.',
    'yanit_376': 'Hazırım bilader, 376. senaryo için sistem beklemede.',
    'yanit_377': 'Hazırım bilader, 377. senaryo için sistem beklemede.',
    'yanit_378': 'Hazırım bilader, 378. senaryo için sistem beklemede.',
    'yanit_379': 'Hazırım bilader, 379. senaryo için sistem beklemede.',
    'yanit_380': 'Hazırım bilader, 380. senaryo için sistem beklemede.',
    'yanit_381': 'Hazırım bilader, 381. senaryo için sistem beklemede.',
    'yanit_382': 'Hazırım bilader, 382. senaryo için sistem beklemede.',
    'yanit_383': 'Hazırım bilader, 383. senaryo için sistem beklemede.',
    'yanit_384': 'Hazırım bilader, 384. senaryo için sistem beklemede.',
    'yanit_385': 'Hazırım bilader, 385. senaryo için sistem beklemede.',
    'yanit_386': 'Hazırım bilader, 386. senaryo için sistem beklemede.',
    'yanit_387': 'Hazırım bilader, 387. senaryo için sistem beklemede.',
    'yanit_388': 'Hazırım bilader, 388. senaryo için sistem beklemede.',
    'yanit_389': 'Hazırım bilader, 389. senaryo için sistem beklemede.',
    'yanit_390': 'Hazırım bilader, 390. senaryo için sistem beklemede.',
    'yanit_391': 'Hazırım bilader, 391. senaryo için sistem beklemede.',
    'yanit_392': 'Hazırım bilader, 392. senaryo için sistem beklemede.',
    'yanit_393': 'Hazırım bilader, 393. senaryo için sistem beklemede.',
    'yanit_394': 'Hazırım bilader, 394. senaryo için sistem beklemede.',
    'yanit_395': 'Hazırım bilader, 395. senaryo için sistem beklemede.',
    'yanit_396': 'Hazırım bilader, 396. senaryo için sistem beklemede.',
    'yanit_397': 'Hazırım bilader, 397. senaryo için sistem beklemede.',
    'yanit_398': 'Hazırım bilader, 398. senaryo için sistem beklemede.',
    'yanit_399': 'Hazırım bilader, 399. senaryo için sistem beklemede.',
    'yanit_400': 'Hazırım bilader, 400. senaryo için sistem beklemede.',
}

def local_smalltalk(text: str) -> Optional[str]:
    t = text.lower()
    if 'tetik 1' in t: return INTENT_RESPONSE_BANK.get('yanit_002')
    if 'tetik 2' in t: return INTENT_RESPONSE_BANK.get('yanit_003')
    if 'tetik 3' in t: return INTENT_RESPONSE_BANK.get('yanit_004')
    if 'tetik 4' in t: return INTENT_RESPONSE_BANK.get('yanit_005')
    if 'tetik 5' in t: return INTENT_RESPONSE_BANK.get('yanit_006')
    if 'tetik 6' in t: return INTENT_RESPONSE_BANK.get('yanit_007')
    if 'tetik 7' in t: return INTENT_RESPONSE_BANK.get('yanit_008')
    if 'tetik 8' in t: return INTENT_RESPONSE_BANK.get('yanit_009')
    if 'tetik 9' in t: return INTENT_RESPONSE_BANK.get('yanit_010')
    if 'tetik 10' in t: return INTENT_RESPONSE_BANK.get('yanit_011')
    if 'tetik 11' in t: return INTENT_RESPONSE_BANK.get('yanit_012')
    if 'tetik 12' in t: return INTENT_RESPONSE_BANK.get('yanit_013')
    if 'tetik 13' in t: return INTENT_RESPONSE_BANK.get('yanit_014')
    if 'tetik 14' in t: return INTENT_RESPONSE_BANK.get('yanit_015')
    if 'tetik 15' in t: return INTENT_RESPONSE_BANK.get('yanit_016')
    if 'tetik 16' in t: return INTENT_RESPONSE_BANK.get('yanit_017')
    if 'tetik 17' in t: return INTENT_RESPONSE_BANK.get('yanit_018')
    if 'tetik 18' in t: return INTENT_RESPONSE_BANK.get('yanit_019')
    if 'tetik 19' in t: return INTENT_RESPONSE_BANK.get('yanit_020')
    if 'tetik 20' in t: return INTENT_RESPONSE_BANK.get('yanit_021')
    if 'tetik 21' in t: return INTENT_RESPONSE_BANK.get('yanit_022')
    if 'tetik 22' in t: return INTENT_RESPONSE_BANK.get('yanit_023')
    if 'tetik 23' in t: return INTENT_RESPONSE_BANK.get('yanit_024')
    if 'tetik 24' in t: return INTENT_RESPONSE_BANK.get('yanit_025')
    if 'tetik 25' in t: return INTENT_RESPONSE_BANK.get('yanit_026')
    if 'tetik 26' in t: return INTENT_RESPONSE_BANK.get('yanit_027')
    if 'tetik 27' in t: return INTENT_RESPONSE_BANK.get('yanit_028')
    if 'tetik 28' in t: return INTENT_RESPONSE_BANK.get('yanit_029')
    if 'tetik 29' in t: return INTENT_RESPONSE_BANK.get('yanit_030')
    if 'tetik 30' in t: return INTENT_RESPONSE_BANK.get('yanit_031')
    if 'tetik 31' in t: return INTENT_RESPONSE_BANK.get('yanit_032')
    if 'tetik 32' in t: return INTENT_RESPONSE_BANK.get('yanit_033')
    if 'tetik 33' in t: return INTENT_RESPONSE_BANK.get('yanit_034')
    if 'tetik 34' in t: return INTENT_RESPONSE_BANK.get('yanit_035')
    if 'tetik 35' in t: return INTENT_RESPONSE_BANK.get('yanit_036')
    if 'tetik 36' in t: return INTENT_RESPONSE_BANK.get('yanit_037')
    if 'tetik 37' in t: return INTENT_RESPONSE_BANK.get('yanit_038')
    if 'tetik 38' in t: return INTENT_RESPONSE_BANK.get('yanit_039')
    if 'tetik 39' in t: return INTENT_RESPONSE_BANK.get('yanit_040')
    if 'tetik 40' in t: return INTENT_RESPONSE_BANK.get('yanit_041')
    if 'tetik 41' in t: return INTENT_RESPONSE_BANK.get('yanit_042')
    if 'tetik 42' in t: return INTENT_RESPONSE_BANK.get('yanit_043')
    if 'tetik 43' in t: return INTENT_RESPONSE_BANK.get('yanit_044')
    if 'tetik 44' in t: return INTENT_RESPONSE_BANK.get('yanit_045')
    if 'tetik 45' in t: return INTENT_RESPONSE_BANK.get('yanit_046')
    if 'tetik 46' in t: return INTENT_RESPONSE_BANK.get('yanit_047')
    if 'tetik 47' in t: return INTENT_RESPONSE_BANK.get('yanit_048')
    if 'tetik 48' in t: return INTENT_RESPONSE_BANK.get('yanit_049')
    if 'tetik 49' in t: return INTENT_RESPONSE_BANK.get('yanit_050')
    if 'tetik 50' in t: return INTENT_RESPONSE_BANK.get('yanit_051')
    if 'tetik 51' in t: return INTENT_RESPONSE_BANK.get('yanit_052')
    if 'tetik 52' in t: return INTENT_RESPONSE_BANK.get('yanit_053')
    if 'tetik 53' in t: return INTENT_RESPONSE_BANK.get('yanit_054')
    if 'tetik 54' in t: return INTENT_RESPONSE_BANK.get('yanit_055')
    if 'tetik 55' in t: return INTENT_RESPONSE_BANK.get('yanit_056')
    if 'tetik 56' in t: return INTENT_RESPONSE_BANK.get('yanit_057')
    if 'tetik 57' in t: return INTENT_RESPONSE_BANK.get('yanit_058')
    if 'tetik 58' in t: return INTENT_RESPONSE_BANK.get('yanit_059')
    if 'tetik 59' in t: return INTENT_RESPONSE_BANK.get('yanit_060')
    if 'tetik 60' in t: return INTENT_RESPONSE_BANK.get('yanit_061')
    if 'tetik 61' in t: return INTENT_RESPONSE_BANK.get('yanit_062')
    if 'tetik 62' in t: return INTENT_RESPONSE_BANK.get('yanit_063')
    if 'tetik 63' in t: return INTENT_RESPONSE_BANK.get('yanit_064')
    if 'tetik 64' in t: return INTENT_RESPONSE_BANK.get('yanit_065')
    if 'tetik 65' in t: return INTENT_RESPONSE_BANK.get('yanit_066')
    if 'tetik 66' in t: return INTENT_RESPONSE_BANK.get('yanit_067')
    if 'tetik 67' in t: return INTENT_RESPONSE_BANK.get('yanit_068')
    if 'tetik 68' in t: return INTENT_RESPONSE_BANK.get('yanit_069')
    if 'tetik 69' in t: return INTENT_RESPONSE_BANK.get('yanit_070')
    if 'tetik 70' in t: return INTENT_RESPONSE_BANK.get('yanit_071')
    if 'tetik 71' in t: return INTENT_RESPONSE_BANK.get('yanit_072')
    if 'tetik 72' in t: return INTENT_RESPONSE_BANK.get('yanit_073')
    if 'tetik 73' in t: return INTENT_RESPONSE_BANK.get('yanit_074')
    if 'tetik 74' in t: return INTENT_RESPONSE_BANK.get('yanit_075')
    if 'tetik 75' in t: return INTENT_RESPONSE_BANK.get('yanit_076')
    if 'tetik 76' in t: return INTENT_RESPONSE_BANK.get('yanit_077')
    if 'tetik 77' in t: return INTENT_RESPONSE_BANK.get('yanit_078')
    if 'tetik 78' in t: return INTENT_RESPONSE_BANK.get('yanit_079')
    if 'tetik 79' in t: return INTENT_RESPONSE_BANK.get('yanit_080')
    if 'tetik 80' in t: return INTENT_RESPONSE_BANK.get('yanit_081')
    if 'tetik 81' in t: return INTENT_RESPONSE_BANK.get('yanit_082')
    if 'tetik 82' in t: return INTENT_RESPONSE_BANK.get('yanit_083')
    if 'tetik 83' in t: return INTENT_RESPONSE_BANK.get('yanit_084')
    if 'tetik 84' in t: return INTENT_RESPONSE_BANK.get('yanit_085')
    if 'tetik 85' in t: return INTENT_RESPONSE_BANK.get('yanit_086')
    if 'tetik 86' in t: return INTENT_RESPONSE_BANK.get('yanit_087')
    if 'tetik 87' in t: return INTENT_RESPONSE_BANK.get('yanit_088')
    if 'tetik 88' in t: return INTENT_RESPONSE_BANK.get('yanit_089')
    if 'tetik 89' in t: return INTENT_RESPONSE_BANK.get('yanit_090')
    if 'tetik 90' in t: return INTENT_RESPONSE_BANK.get('yanit_091')
    if 'tetik 91' in t: return INTENT_RESPONSE_BANK.get('yanit_092')
    if 'tetik 92' in t: return INTENT_RESPONSE_BANK.get('yanit_093')
    if 'tetik 93' in t: return INTENT_RESPONSE_BANK.get('yanit_094')
    if 'tetik 94' in t: return INTENT_RESPONSE_BANK.get('yanit_095')
    if 'tetik 95' in t: return INTENT_RESPONSE_BANK.get('yanit_096')
    if 'tetik 96' in t: return INTENT_RESPONSE_BANK.get('yanit_097')
    if 'tetik 97' in t: return INTENT_RESPONSE_BANK.get('yanit_098')
    if 'tetik 98' in t: return INTENT_RESPONSE_BANK.get('yanit_099')
    if 'tetik 99' in t: return INTENT_RESPONSE_BANK.get('yanit_100')
    if 'tetik 100' in t: return INTENT_RESPONSE_BANK.get('yanit_101')
    if 'tetik 101' in t: return INTENT_RESPONSE_BANK.get('yanit_102')
    if 'tetik 102' in t: return INTENT_RESPONSE_BANK.get('yanit_103')
    if 'tetik 103' in t: return INTENT_RESPONSE_BANK.get('yanit_104')
    if 'tetik 104' in t: return INTENT_RESPONSE_BANK.get('yanit_105')
    if 'tetik 105' in t: return INTENT_RESPONSE_BANK.get('yanit_106')
    if 'tetik 106' in t: return INTENT_RESPONSE_BANK.get('yanit_107')
    if 'tetik 107' in t: return INTENT_RESPONSE_BANK.get('yanit_108')
    if 'tetik 108' in t: return INTENT_RESPONSE_BANK.get('yanit_109')
    if 'tetik 109' in t: return INTENT_RESPONSE_BANK.get('yanit_110')
    if 'tetik 110' in t: return INTENT_RESPONSE_BANK.get('yanit_111')
    if 'tetik 111' in t: return INTENT_RESPONSE_BANK.get('yanit_112')
    if 'tetik 112' in t: return INTENT_RESPONSE_BANK.get('yanit_113')
    if 'tetik 113' in t: return INTENT_RESPONSE_BANK.get('yanit_114')
    if 'tetik 114' in t: return INTENT_RESPONSE_BANK.get('yanit_115')
    if 'tetik 115' in t: return INTENT_RESPONSE_BANK.get('yanit_116')
    if 'tetik 116' in t: return INTENT_RESPONSE_BANK.get('yanit_117')
    if 'tetik 117' in t: return INTENT_RESPONSE_BANK.get('yanit_118')
    if 'tetik 118' in t: return INTENT_RESPONSE_BANK.get('yanit_119')
    if 'tetik 119' in t: return INTENT_RESPONSE_BANK.get('yanit_120')
    if 'tetik 120' in t: return INTENT_RESPONSE_BANK.get('yanit_121')
    if 'tetik 121' in t: return INTENT_RESPONSE_BANK.get('yanit_122')
    if 'tetik 122' in t: return INTENT_RESPONSE_BANK.get('yanit_123')
    if 'tetik 123' in t: return INTENT_RESPONSE_BANK.get('yanit_124')
    if 'tetik 124' in t: return INTENT_RESPONSE_BANK.get('yanit_125')
    if 'tetik 125' in t: return INTENT_RESPONSE_BANK.get('yanit_126')
    if 'tetik 126' in t: return INTENT_RESPONSE_BANK.get('yanit_127')
    if 'tetik 127' in t: return INTENT_RESPONSE_BANK.get('yanit_128')
    if 'tetik 128' in t: return INTENT_RESPONSE_BANK.get('yanit_129')
    if 'tetik 129' in t: return INTENT_RESPONSE_BANK.get('yanit_130')
    if 'tetik 130' in t: return INTENT_RESPONSE_BANK.get('yanit_131')
    if 'tetik 131' in t: return INTENT_RESPONSE_BANK.get('yanit_132')
    if 'tetik 132' in t: return INTENT_RESPONSE_BANK.get('yanit_133')
    if 'tetik 133' in t: return INTENT_RESPONSE_BANK.get('yanit_134')
    if 'tetik 134' in t: return INTENT_RESPONSE_BANK.get('yanit_135')
    if 'tetik 135' in t: return INTENT_RESPONSE_BANK.get('yanit_136')
    if 'tetik 136' in t: return INTENT_RESPONSE_BANK.get('yanit_137')
    if 'tetik 137' in t: return INTENT_RESPONSE_BANK.get('yanit_138')
    if 'tetik 138' in t: return INTENT_RESPONSE_BANK.get('yanit_139')
    if 'tetik 139' in t: return INTENT_RESPONSE_BANK.get('yanit_140')
    if 'tetik 140' in t: return INTENT_RESPONSE_BANK.get('yanit_141')
    if 'tetik 141' in t: return INTENT_RESPONSE_BANK.get('yanit_142')
    if 'tetik 142' in t: return INTENT_RESPONSE_BANK.get('yanit_143')
    if 'tetik 143' in t: return INTENT_RESPONSE_BANK.get('yanit_144')
    if 'tetik 144' in t: return INTENT_RESPONSE_BANK.get('yanit_145')
    if 'tetik 145' in t: return INTENT_RESPONSE_BANK.get('yanit_146')
    if 'tetik 146' in t: return INTENT_RESPONSE_BANK.get('yanit_147')
    if 'tetik 147' in t: return INTENT_RESPONSE_BANK.get('yanit_148')
    if 'tetik 148' in t: return INTENT_RESPONSE_BANK.get('yanit_149')
    if 'tetik 149' in t: return INTENT_RESPONSE_BANK.get('yanit_150')
    if 'tetik 150' in t: return INTENT_RESPONSE_BANK.get('yanit_151')
    if 'tetik 151' in t: return INTENT_RESPONSE_BANK.get('yanit_152')
    if 'tetik 152' in t: return INTENT_RESPONSE_BANK.get('yanit_153')
    if 'tetik 153' in t: return INTENT_RESPONSE_BANK.get('yanit_154')
    if 'tetik 154' in t: return INTENT_RESPONSE_BANK.get('yanit_155')
    if 'tetik 155' in t: return INTENT_RESPONSE_BANK.get('yanit_156')
    if 'tetik 156' in t: return INTENT_RESPONSE_BANK.get('yanit_157')
    if 'tetik 157' in t: return INTENT_RESPONSE_BANK.get('yanit_158')
    if 'tetik 158' in t: return INTENT_RESPONSE_BANK.get('yanit_159')
    if 'tetik 159' in t: return INTENT_RESPONSE_BANK.get('yanit_160')
    if 'tetik 160' in t: return INTENT_RESPONSE_BANK.get('yanit_161')
    if 'tetik 161' in t: return INTENT_RESPONSE_BANK.get('yanit_162')
    if 'tetik 162' in t: return INTENT_RESPONSE_BANK.get('yanit_163')
    if 'tetik 163' in t: return INTENT_RESPONSE_BANK.get('yanit_164')
    if 'tetik 164' in t: return INTENT_RESPONSE_BANK.get('yanit_165')
    if 'tetik 165' in t: return INTENT_RESPONSE_BANK.get('yanit_166')
    if 'tetik 166' in t: return INTENT_RESPONSE_BANK.get('yanit_167')
    if 'tetik 167' in t: return INTENT_RESPONSE_BANK.get('yanit_168')
    if 'tetik 168' in t: return INTENT_RESPONSE_BANK.get('yanit_169')
    if 'tetik 169' in t: return INTENT_RESPONSE_BANK.get('yanit_170')
    if 'tetik 170' in t: return INTENT_RESPONSE_BANK.get('yanit_171')
    if 'tetik 171' in t: return INTENT_RESPONSE_BANK.get('yanit_172')
    if 'tetik 172' in t: return INTENT_RESPONSE_BANK.get('yanit_173')
    if 'tetik 173' in t: return INTENT_RESPONSE_BANK.get('yanit_174')
    if 'tetik 174' in t: return INTENT_RESPONSE_BANK.get('yanit_175')
    if 'tetik 175' in t: return INTENT_RESPONSE_BANK.get('yanit_176')
    if 'tetik 176' in t: return INTENT_RESPONSE_BANK.get('yanit_177')
    if 'tetik 177' in t: return INTENT_RESPONSE_BANK.get('yanit_178')
    if 'tetik 178' in t: return INTENT_RESPONSE_BANK.get('yanit_179')
    if 'tetik 179' in t: return INTENT_RESPONSE_BANK.get('yanit_180')
    if 'tetik 180' in t: return INTENT_RESPONSE_BANK.get('yanit_181')
    if 'tetik 181' in t: return INTENT_RESPONSE_BANK.get('yanit_182')
    if 'tetik 182' in t: return INTENT_RESPONSE_BANK.get('yanit_183')
    if 'tetik 183' in t: return INTENT_RESPONSE_BANK.get('yanit_184')
    if 'tetik 184' in t: return INTENT_RESPONSE_BANK.get('yanit_185')
    if 'tetik 185' in t: return INTENT_RESPONSE_BANK.get('yanit_186')
    if 'tetik 186' in t: return INTENT_RESPONSE_BANK.get('yanit_187')
    if 'tetik 187' in t: return INTENT_RESPONSE_BANK.get('yanit_188')
    if 'tetik 188' in t: return INTENT_RESPONSE_BANK.get('yanit_189')
    if 'tetik 189' in t: return INTENT_RESPONSE_BANK.get('yanit_190')
    if 'tetik 190' in t: return INTENT_RESPONSE_BANK.get('yanit_191')
    if 'tetik 191' in t: return INTENT_RESPONSE_BANK.get('yanit_192')
    if 'tetik 192' in t: return INTENT_RESPONSE_BANK.get('yanit_193')
    if 'tetik 193' in t: return INTENT_RESPONSE_BANK.get('yanit_194')
    if 'tetik 194' in t: return INTENT_RESPONSE_BANK.get('yanit_195')
    if 'tetik 195' in t: return INTENT_RESPONSE_BANK.get('yanit_196')
    if 'tetik 196' in t: return INTENT_RESPONSE_BANK.get('yanit_197')
    if 'tetik 197' in t: return INTENT_RESPONSE_BANK.get('yanit_198')
    if 'tetik 198' in t: return INTENT_RESPONSE_BANK.get('yanit_199')
    if 'tetik 199' in t: return INTENT_RESPONSE_BANK.get('yanit_200')
    if 'tetik 200' in t: return INTENT_RESPONSE_BANK.get('yanit_201')
    return None

def main() -> None:
    core = BiladerCore()
    # Yerel intent yapısını belleğe al (ileride NLP routing için)
    intents = seed_local_intents()
    core.memory.append_event('intent_seed_loaded', {'intent_count': len(intents), 'alias_count': len(COMMAND_ALIASES)})
    build_window(core)

if __name__ == '__main__':
    main()
