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

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv(*_args, **_kwargs):  # type: ignore[no-redef]
        return False

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

    def clear_all(self) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM conversations")
            conn.execute("DELETE FROM events")

    def export_bundle(self, limit: int = 200) -> Dict[str, Any]:
        with self._conn() as conn:
            conv = conn.execute(
                "SELECT role, content, created_at FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            events = conn.execute(
                "SELECT event_type, payload, created_at FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return {
            "conversations": [
                {"role": role, "content": content, "created_at": created_at}
                for role, content, created_at in reversed(conv)
            ],
            "events": [
                {"event_type": et, "payload": payload, "created_at": created_at}
                for et, payload, created_at in reversed(events)
            ],
        }


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




class CommandPlaybook:
    """Yerel komut rehberi ve hızlı eşleştirme envanteri."""

    CORE_GUIDE: Dict[str, Dict[str, Any]] = {
        "arduino_connect": {
            "description": "Arduino seri bağlantısını başlatır.",
            "examples": ["arduinoya bağlan", "arduino bağlantısını aç", "bilader arduinoya bağlan"],
        },
        "arduino_disconnect": {
            "description": "Arduino seri bağlantısını kapatır.",
            "examples": ["arduino bağlantısını kes", "arduinoyu kapat", "bağlantıyı ayır"],
        },
        "light_on": {
            "description": "IoT ışık rölesini açar.",
            "examples": ["ışığı yak", "ışık aç", "oda ışığını aç"],
        },
        "light_off": {
            "description": "IoT ışık rölesini kapatır.",
            "examples": ["ışığı kapat", "ışık söndür", "oda ışığını kapat"],
        },
        "temperature": {
            "description": "Arduino sensöründen sıcaklık alır.",
            "examples": ["sıcaklık kaç", "oda kaç derece", "ısı değeri nedir"],
        },
        "system_status": {
            "description": "CPU, RAM ve disk özetini döndürür.",
            "examples": ["cpu nasıl", "ram durumu", "disk dolu mu"],
        },
        "open_spotify": {
            "description": "Spotify uygulamasını açmayı dener.",
            "examples": ["spotify aç", "müziği spotifydan aç", "spotify başlat"],
        },
        "open_calculator": {
            "description": "Hesap makinesini açar.",
            "examples": ["hesap makinesi aç", "calculator aç", "hesaplayıcı aç"],
        },
        "greeting": {
            "description": "Asistanın hazır yanıt vermesini sağlar.",
            "examples": ["merhaba", "selam bilader", "orada mısın"],
        },
    }

    EXTENDED_GUIDE: Dict[str, Dict[str, Any]] = {
        "scenario_001": {"description": "Özel senaryo 1 için yerel komut şablonu.", "examples": ["bilader senaryo 1", "görev 1 başlat", "otomasyon 1 çalıştır"]},
        "scenario_002": {"description": "Özel senaryo 2 için yerel komut şablonu.", "examples": ["bilader senaryo 2", "görev 2 başlat", "otomasyon 2 çalıştır"]},
        "scenario_003": {"description": "Özel senaryo 3 için yerel komut şablonu.", "examples": ["bilader senaryo 3", "görev 3 başlat", "otomasyon 3 çalıştır"]},
        "scenario_004": {"description": "Özel senaryo 4 için yerel komut şablonu.", "examples": ["bilader senaryo 4", "görev 4 başlat", "otomasyon 4 çalıştır"]},
        "scenario_005": {"description": "Özel senaryo 5 için yerel komut şablonu.", "examples": ["bilader senaryo 5", "görev 5 başlat", "otomasyon 5 çalıştır"]},
        "scenario_006": {"description": "Özel senaryo 6 için yerel komut şablonu.", "examples": ["bilader senaryo 6", "görev 6 başlat", "otomasyon 6 çalıştır"]},
        "scenario_007": {"description": "Özel senaryo 7 için yerel komut şablonu.", "examples": ["bilader senaryo 7", "görev 7 başlat", "otomasyon 7 çalıştır"]},
        "scenario_008": {"description": "Özel senaryo 8 için yerel komut şablonu.", "examples": ["bilader senaryo 8", "görev 8 başlat", "otomasyon 8 çalıştır"]},
        "scenario_009": {"description": "Özel senaryo 9 için yerel komut şablonu.", "examples": ["bilader senaryo 9", "görev 9 başlat", "otomasyon 9 çalıştır"]},
        "scenario_010": {"description": "Özel senaryo 10 için yerel komut şablonu.", "examples": ["bilader senaryo 10", "görev 10 başlat", "otomasyon 10 çalıştır"]},
        "scenario_011": {"description": "Özel senaryo 11 için yerel komut şablonu.", "examples": ["bilader senaryo 11", "görev 11 başlat", "otomasyon 11 çalıştır"]},
        "scenario_012": {"description": "Özel senaryo 12 için yerel komut şablonu.", "examples": ["bilader senaryo 12", "görev 12 başlat", "otomasyon 12 çalıştır"]},
        "scenario_013": {"description": "Özel senaryo 13 için yerel komut şablonu.", "examples": ["bilader senaryo 13", "görev 13 başlat", "otomasyon 13 çalıştır"]},
        "scenario_014": {"description": "Özel senaryo 14 için yerel komut şablonu.", "examples": ["bilader senaryo 14", "görev 14 başlat", "otomasyon 14 çalıştır"]},
        "scenario_015": {"description": "Özel senaryo 15 için yerel komut şablonu.", "examples": ["bilader senaryo 15", "görev 15 başlat", "otomasyon 15 çalıştır"]},
        "scenario_016": {"description": "Özel senaryo 16 için yerel komut şablonu.", "examples": ["bilader senaryo 16", "görev 16 başlat", "otomasyon 16 çalıştır"]},
        "scenario_017": {"description": "Özel senaryo 17 için yerel komut şablonu.", "examples": ["bilader senaryo 17", "görev 17 başlat", "otomasyon 17 çalıştır"]},
        "scenario_018": {"description": "Özel senaryo 18 için yerel komut şablonu.", "examples": ["bilader senaryo 18", "görev 18 başlat", "otomasyon 18 çalıştır"]},
        "scenario_019": {"description": "Özel senaryo 19 için yerel komut şablonu.", "examples": ["bilader senaryo 19", "görev 19 başlat", "otomasyon 19 çalıştır"]},
        "scenario_020": {"description": "Özel senaryo 20 için yerel komut şablonu.", "examples": ["bilader senaryo 20", "görev 20 başlat", "otomasyon 20 çalıştır"]},
        "scenario_021": {"description": "Özel senaryo 21 için yerel komut şablonu.", "examples": ["bilader senaryo 21", "görev 21 başlat", "otomasyon 21 çalıştır"]},
        "scenario_022": {"description": "Özel senaryo 22 için yerel komut şablonu.", "examples": ["bilader senaryo 22", "görev 22 başlat", "otomasyon 22 çalıştır"]},
        "scenario_023": {"description": "Özel senaryo 23 için yerel komut şablonu.", "examples": ["bilader senaryo 23", "görev 23 başlat", "otomasyon 23 çalıştır"]},
        "scenario_024": {"description": "Özel senaryo 24 için yerel komut şablonu.", "examples": ["bilader senaryo 24", "görev 24 başlat", "otomasyon 24 çalıştır"]},
        "scenario_025": {"description": "Özel senaryo 25 için yerel komut şablonu.", "examples": ["bilader senaryo 25", "görev 25 başlat", "otomasyon 25 çalıştır"]},
        "scenario_026": {"description": "Özel senaryo 26 için yerel komut şablonu.", "examples": ["bilader senaryo 26", "görev 26 başlat", "otomasyon 26 çalıştır"]},
        "scenario_027": {"description": "Özel senaryo 27 için yerel komut şablonu.", "examples": ["bilader senaryo 27", "görev 27 başlat", "otomasyon 27 çalıştır"]},
        "scenario_028": {"description": "Özel senaryo 28 için yerel komut şablonu.", "examples": ["bilader senaryo 28", "görev 28 başlat", "otomasyon 28 çalıştır"]},
        "scenario_029": {"description": "Özel senaryo 29 için yerel komut şablonu.", "examples": ["bilader senaryo 29", "görev 29 başlat", "otomasyon 29 çalıştır"]},
        "scenario_030": {"description": "Özel senaryo 30 için yerel komut şablonu.", "examples": ["bilader senaryo 30", "görev 30 başlat", "otomasyon 30 çalıştır"]},
        "scenario_031": {"description": "Özel senaryo 31 için yerel komut şablonu.", "examples": ["bilader senaryo 31", "görev 31 başlat", "otomasyon 31 çalıştır"]},
        "scenario_032": {"description": "Özel senaryo 32 için yerel komut şablonu.", "examples": ["bilader senaryo 32", "görev 32 başlat", "otomasyon 32 çalıştır"]},
        "scenario_033": {"description": "Özel senaryo 33 için yerel komut şablonu.", "examples": ["bilader senaryo 33", "görev 33 başlat", "otomasyon 33 çalıştır"]},
        "scenario_034": {"description": "Özel senaryo 34 için yerel komut şablonu.", "examples": ["bilader senaryo 34", "görev 34 başlat", "otomasyon 34 çalıştır"]},
        "scenario_035": {"description": "Özel senaryo 35 için yerel komut şablonu.", "examples": ["bilader senaryo 35", "görev 35 başlat", "otomasyon 35 çalıştır"]},
        "scenario_036": {"description": "Özel senaryo 36 için yerel komut şablonu.", "examples": ["bilader senaryo 36", "görev 36 başlat", "otomasyon 36 çalıştır"]},
        "scenario_037": {"description": "Özel senaryo 37 için yerel komut şablonu.", "examples": ["bilader senaryo 37", "görev 37 başlat", "otomasyon 37 çalıştır"]},
        "scenario_038": {"description": "Özel senaryo 38 için yerel komut şablonu.", "examples": ["bilader senaryo 38", "görev 38 başlat", "otomasyon 38 çalıştır"]},
        "scenario_039": {"description": "Özel senaryo 39 için yerel komut şablonu.", "examples": ["bilader senaryo 39", "görev 39 başlat", "otomasyon 39 çalıştır"]},
        "scenario_040": {"description": "Özel senaryo 40 için yerel komut şablonu.", "examples": ["bilader senaryo 40", "görev 40 başlat", "otomasyon 40 çalıştır"]},
        "scenario_041": {"description": "Özel senaryo 41 için yerel komut şablonu.", "examples": ["bilader senaryo 41", "görev 41 başlat", "otomasyon 41 çalıştır"]},
        "scenario_042": {"description": "Özel senaryo 42 için yerel komut şablonu.", "examples": ["bilader senaryo 42", "görev 42 başlat", "otomasyon 42 çalıştır"]},
        "scenario_043": {"description": "Özel senaryo 43 için yerel komut şablonu.", "examples": ["bilader senaryo 43", "görev 43 başlat", "otomasyon 43 çalıştır"]},
        "scenario_044": {"description": "Özel senaryo 44 için yerel komut şablonu.", "examples": ["bilader senaryo 44", "görev 44 başlat", "otomasyon 44 çalıştır"]},
        "scenario_045": {"description": "Özel senaryo 45 için yerel komut şablonu.", "examples": ["bilader senaryo 45", "görev 45 başlat", "otomasyon 45 çalıştır"]},
        "scenario_046": {"description": "Özel senaryo 46 için yerel komut şablonu.", "examples": ["bilader senaryo 46", "görev 46 başlat", "otomasyon 46 çalıştır"]},
        "scenario_047": {"description": "Özel senaryo 47 için yerel komut şablonu.", "examples": ["bilader senaryo 47", "görev 47 başlat", "otomasyon 47 çalıştır"]},
        "scenario_048": {"description": "Özel senaryo 48 için yerel komut şablonu.", "examples": ["bilader senaryo 48", "görev 48 başlat", "otomasyon 48 çalıştır"]},
        "scenario_049": {"description": "Özel senaryo 49 için yerel komut şablonu.", "examples": ["bilader senaryo 49", "görev 49 başlat", "otomasyon 49 çalıştır"]},
        "scenario_050": {"description": "Özel senaryo 50 için yerel komut şablonu.", "examples": ["bilader senaryo 50", "görev 50 başlat", "otomasyon 50 çalıştır"]},
        "scenario_051": {"description": "Özel senaryo 51 için yerel komut şablonu.", "examples": ["bilader senaryo 51", "görev 51 başlat", "otomasyon 51 çalıştır"]},
        "scenario_052": {"description": "Özel senaryo 52 için yerel komut şablonu.", "examples": ["bilader senaryo 52", "görev 52 başlat", "otomasyon 52 çalıştır"]},
        "scenario_053": {"description": "Özel senaryo 53 için yerel komut şablonu.", "examples": ["bilader senaryo 53", "görev 53 başlat", "otomasyon 53 çalıştır"]},
        "scenario_054": {"description": "Özel senaryo 54 için yerel komut şablonu.", "examples": ["bilader senaryo 54", "görev 54 başlat", "otomasyon 54 çalıştır"]},
        "scenario_055": {"description": "Özel senaryo 55 için yerel komut şablonu.", "examples": ["bilader senaryo 55", "görev 55 başlat", "otomasyon 55 çalıştır"]},
        "scenario_056": {"description": "Özel senaryo 56 için yerel komut şablonu.", "examples": ["bilader senaryo 56", "görev 56 başlat", "otomasyon 56 çalıştır"]},
        "scenario_057": {"description": "Özel senaryo 57 için yerel komut şablonu.", "examples": ["bilader senaryo 57", "görev 57 başlat", "otomasyon 57 çalıştır"]},
        "scenario_058": {"description": "Özel senaryo 58 için yerel komut şablonu.", "examples": ["bilader senaryo 58", "görev 58 başlat", "otomasyon 58 çalıştır"]},
        "scenario_059": {"description": "Özel senaryo 59 için yerel komut şablonu.", "examples": ["bilader senaryo 59", "görev 59 başlat", "otomasyon 59 çalıştır"]},
        "scenario_060": {"description": "Özel senaryo 60 için yerel komut şablonu.", "examples": ["bilader senaryo 60", "görev 60 başlat", "otomasyon 60 çalıştır"]},
        "scenario_061": {"description": "Özel senaryo 61 için yerel komut şablonu.", "examples": ["bilader senaryo 61", "görev 61 başlat", "otomasyon 61 çalıştır"]},
        "scenario_062": {"description": "Özel senaryo 62 için yerel komut şablonu.", "examples": ["bilader senaryo 62", "görev 62 başlat", "otomasyon 62 çalıştır"]},
        "scenario_063": {"description": "Özel senaryo 63 için yerel komut şablonu.", "examples": ["bilader senaryo 63", "görev 63 başlat", "otomasyon 63 çalıştır"]},
        "scenario_064": {"description": "Özel senaryo 64 için yerel komut şablonu.", "examples": ["bilader senaryo 64", "görev 64 başlat", "otomasyon 64 çalıştır"]},
        "scenario_065": {"description": "Özel senaryo 65 için yerel komut şablonu.", "examples": ["bilader senaryo 65", "görev 65 başlat", "otomasyon 65 çalıştır"]},
        "scenario_066": {"description": "Özel senaryo 66 için yerel komut şablonu.", "examples": ["bilader senaryo 66", "görev 66 başlat", "otomasyon 66 çalıştır"]},
        "scenario_067": {"description": "Özel senaryo 67 için yerel komut şablonu.", "examples": ["bilader senaryo 67", "görev 67 başlat", "otomasyon 67 çalıştır"]},
        "scenario_068": {"description": "Özel senaryo 68 için yerel komut şablonu.", "examples": ["bilader senaryo 68", "görev 68 başlat", "otomasyon 68 çalıştır"]},
        "scenario_069": {"description": "Özel senaryo 69 için yerel komut şablonu.", "examples": ["bilader senaryo 69", "görev 69 başlat", "otomasyon 69 çalıştır"]},
        "scenario_070": {"description": "Özel senaryo 70 için yerel komut şablonu.", "examples": ["bilader senaryo 70", "görev 70 başlat", "otomasyon 70 çalıştır"]},
        "scenario_071": {"description": "Özel senaryo 71 için yerel komut şablonu.", "examples": ["bilader senaryo 71", "görev 71 başlat", "otomasyon 71 çalıştır"]},
        "scenario_072": {"description": "Özel senaryo 72 için yerel komut şablonu.", "examples": ["bilader senaryo 72", "görev 72 başlat", "otomasyon 72 çalıştır"]},
        "scenario_073": {"description": "Özel senaryo 73 için yerel komut şablonu.", "examples": ["bilader senaryo 73", "görev 73 başlat", "otomasyon 73 çalıştır"]},
        "scenario_074": {"description": "Özel senaryo 74 için yerel komut şablonu.", "examples": ["bilader senaryo 74", "görev 74 başlat", "otomasyon 74 çalıştır"]},
        "scenario_075": {"description": "Özel senaryo 75 için yerel komut şablonu.", "examples": ["bilader senaryo 75", "görev 75 başlat", "otomasyon 75 çalıştır"]},
        "scenario_076": {"description": "Özel senaryo 76 için yerel komut şablonu.", "examples": ["bilader senaryo 76", "görev 76 başlat", "otomasyon 76 çalıştır"]},
        "scenario_077": {"description": "Özel senaryo 77 için yerel komut şablonu.", "examples": ["bilader senaryo 77", "görev 77 başlat", "otomasyon 77 çalıştır"]},
        "scenario_078": {"description": "Özel senaryo 78 için yerel komut şablonu.", "examples": ["bilader senaryo 78", "görev 78 başlat", "otomasyon 78 çalıştır"]},
        "scenario_079": {"description": "Özel senaryo 79 için yerel komut şablonu.", "examples": ["bilader senaryo 79", "görev 79 başlat", "otomasyon 79 çalıştır"]},
        "scenario_080": {"description": "Özel senaryo 80 için yerel komut şablonu.", "examples": ["bilader senaryo 80", "görev 80 başlat", "otomasyon 80 çalıştır"]},
        "scenario_081": {"description": "Özel senaryo 81 için yerel komut şablonu.", "examples": ["bilader senaryo 81", "görev 81 başlat", "otomasyon 81 çalıştır"]},
        "scenario_082": {"description": "Özel senaryo 82 için yerel komut şablonu.", "examples": ["bilader senaryo 82", "görev 82 başlat", "otomasyon 82 çalıştır"]},
        "scenario_083": {"description": "Özel senaryo 83 için yerel komut şablonu.", "examples": ["bilader senaryo 83", "görev 83 başlat", "otomasyon 83 çalıştır"]},
        "scenario_084": {"description": "Özel senaryo 84 için yerel komut şablonu.", "examples": ["bilader senaryo 84", "görev 84 başlat", "otomasyon 84 çalıştır"]},
        "scenario_085": {"description": "Özel senaryo 85 için yerel komut şablonu.", "examples": ["bilader senaryo 85", "görev 85 başlat", "otomasyon 85 çalıştır"]},
        "scenario_086": {"description": "Özel senaryo 86 için yerel komut şablonu.", "examples": ["bilader senaryo 86", "görev 86 başlat", "otomasyon 86 çalıştır"]},
        "scenario_087": {"description": "Özel senaryo 87 için yerel komut şablonu.", "examples": ["bilader senaryo 87", "görev 87 başlat", "otomasyon 87 çalıştır"]},
        "scenario_088": {"description": "Özel senaryo 88 için yerel komut şablonu.", "examples": ["bilader senaryo 88", "görev 88 başlat", "otomasyon 88 çalıştır"]},
        "scenario_089": {"description": "Özel senaryo 89 için yerel komut şablonu.", "examples": ["bilader senaryo 89", "görev 89 başlat", "otomasyon 89 çalıştır"]},
        "scenario_090": {"description": "Özel senaryo 90 için yerel komut şablonu.", "examples": ["bilader senaryo 90", "görev 90 başlat", "otomasyon 90 çalıştır"]},
        "scenario_091": {"description": "Özel senaryo 91 için yerel komut şablonu.", "examples": ["bilader senaryo 91", "görev 91 başlat", "otomasyon 91 çalıştır"]},
        "scenario_092": {"description": "Özel senaryo 92 için yerel komut şablonu.", "examples": ["bilader senaryo 92", "görev 92 başlat", "otomasyon 92 çalıştır"]},
        "scenario_093": {"description": "Özel senaryo 93 için yerel komut şablonu.", "examples": ["bilader senaryo 93", "görev 93 başlat", "otomasyon 93 çalıştır"]},
        "scenario_094": {"description": "Özel senaryo 94 için yerel komut şablonu.", "examples": ["bilader senaryo 94", "görev 94 başlat", "otomasyon 94 çalıştır"]},
        "scenario_095": {"description": "Özel senaryo 95 için yerel komut şablonu.", "examples": ["bilader senaryo 95", "görev 95 başlat", "otomasyon 95 çalıştır"]},
        "scenario_096": {"description": "Özel senaryo 96 için yerel komut şablonu.", "examples": ["bilader senaryo 96", "görev 96 başlat", "otomasyon 96 çalıştır"]},
        "scenario_097": {"description": "Özel senaryo 97 için yerel komut şablonu.", "examples": ["bilader senaryo 97", "görev 97 başlat", "otomasyon 97 çalıştır"]},
        "scenario_098": {"description": "Özel senaryo 98 için yerel komut şablonu.", "examples": ["bilader senaryo 98", "görev 98 başlat", "otomasyon 98 çalıştır"]},
        "scenario_099": {"description": "Özel senaryo 99 için yerel komut şablonu.", "examples": ["bilader senaryo 99", "görev 99 başlat", "otomasyon 99 çalıştır"]},
        "scenario_100": {"description": "Özel senaryo 100 için yerel komut şablonu.", "examples": ["bilader senaryo 100", "görev 100 başlat", "otomasyon 100 çalıştır"]},
        "scenario_101": {"description": "Özel senaryo 101 için yerel komut şablonu.", "examples": ["bilader senaryo 101", "görev 101 başlat", "otomasyon 101 çalıştır"]},
        "scenario_102": {"description": "Özel senaryo 102 için yerel komut şablonu.", "examples": ["bilader senaryo 102", "görev 102 başlat", "otomasyon 102 çalıştır"]},
        "scenario_103": {"description": "Özel senaryo 103 için yerel komut şablonu.", "examples": ["bilader senaryo 103", "görev 103 başlat", "otomasyon 103 çalıştır"]},
        "scenario_104": {"description": "Özel senaryo 104 için yerel komut şablonu.", "examples": ["bilader senaryo 104", "görev 104 başlat", "otomasyon 104 çalıştır"]},
        "scenario_105": {"description": "Özel senaryo 105 için yerel komut şablonu.", "examples": ["bilader senaryo 105", "görev 105 başlat", "otomasyon 105 çalıştır"]},
        "scenario_106": {"description": "Özel senaryo 106 için yerel komut şablonu.", "examples": ["bilader senaryo 106", "görev 106 başlat", "otomasyon 106 çalıştır"]},
        "scenario_107": {"description": "Özel senaryo 107 için yerel komut şablonu.", "examples": ["bilader senaryo 107", "görev 107 başlat", "otomasyon 107 çalıştır"]},
        "scenario_108": {"description": "Özel senaryo 108 için yerel komut şablonu.", "examples": ["bilader senaryo 108", "görev 108 başlat", "otomasyon 108 çalıştır"]},
        "scenario_109": {"description": "Özel senaryo 109 için yerel komut şablonu.", "examples": ["bilader senaryo 109", "görev 109 başlat", "otomasyon 109 çalıştır"]},
        "scenario_110": {"description": "Özel senaryo 110 için yerel komut şablonu.", "examples": ["bilader senaryo 110", "görev 110 başlat", "otomasyon 110 çalıştır"]},
        "scenario_111": {"description": "Özel senaryo 111 için yerel komut şablonu.", "examples": ["bilader senaryo 111", "görev 111 başlat", "otomasyon 111 çalıştır"]},
        "scenario_112": {"description": "Özel senaryo 112 için yerel komut şablonu.", "examples": ["bilader senaryo 112", "görev 112 başlat", "otomasyon 112 çalıştır"]},
        "scenario_113": {"description": "Özel senaryo 113 için yerel komut şablonu.", "examples": ["bilader senaryo 113", "görev 113 başlat", "otomasyon 113 çalıştır"]},
        "scenario_114": {"description": "Özel senaryo 114 için yerel komut şablonu.", "examples": ["bilader senaryo 114", "görev 114 başlat", "otomasyon 114 çalıştır"]},
        "scenario_115": {"description": "Özel senaryo 115 için yerel komut şablonu.", "examples": ["bilader senaryo 115", "görev 115 başlat", "otomasyon 115 çalıştır"]},
        "scenario_116": {"description": "Özel senaryo 116 için yerel komut şablonu.", "examples": ["bilader senaryo 116", "görev 116 başlat", "otomasyon 116 çalıştır"]},
        "scenario_117": {"description": "Özel senaryo 117 için yerel komut şablonu.", "examples": ["bilader senaryo 117", "görev 117 başlat", "otomasyon 117 çalıştır"]},
        "scenario_118": {"description": "Özel senaryo 118 için yerel komut şablonu.", "examples": ["bilader senaryo 118", "görev 118 başlat", "otomasyon 118 çalıştır"]},
        "scenario_119": {"description": "Özel senaryo 119 için yerel komut şablonu.", "examples": ["bilader senaryo 119", "görev 119 başlat", "otomasyon 119 çalıştır"]},
        "scenario_120": {"description": "Özel senaryo 120 için yerel komut şablonu.", "examples": ["bilader senaryo 120", "görev 120 başlat", "otomasyon 120 çalıştır"]},
        "scenario_121": {"description": "Özel senaryo 121 için yerel komut şablonu.", "examples": ["bilader senaryo 121", "görev 121 başlat", "otomasyon 121 çalıştır"]},
        "scenario_122": {"description": "Özel senaryo 122 için yerel komut şablonu.", "examples": ["bilader senaryo 122", "görev 122 başlat", "otomasyon 122 çalıştır"]},
        "scenario_123": {"description": "Özel senaryo 123 için yerel komut şablonu.", "examples": ["bilader senaryo 123", "görev 123 başlat", "otomasyon 123 çalıştır"]},
        "scenario_124": {"description": "Özel senaryo 124 için yerel komut şablonu.", "examples": ["bilader senaryo 124", "görev 124 başlat", "otomasyon 124 çalıştır"]},
        "scenario_125": {"description": "Özel senaryo 125 için yerel komut şablonu.", "examples": ["bilader senaryo 125", "görev 125 başlat", "otomasyon 125 çalıştır"]},
        "scenario_126": {"description": "Özel senaryo 126 için yerel komut şablonu.", "examples": ["bilader senaryo 126", "görev 126 başlat", "otomasyon 126 çalıştır"]},
        "scenario_127": {"description": "Özel senaryo 127 için yerel komut şablonu.", "examples": ["bilader senaryo 127", "görev 127 başlat", "otomasyon 127 çalıştır"]},
        "scenario_128": {"description": "Özel senaryo 128 için yerel komut şablonu.", "examples": ["bilader senaryo 128", "görev 128 başlat", "otomasyon 128 çalıştır"]},
        "scenario_129": {"description": "Özel senaryo 129 için yerel komut şablonu.", "examples": ["bilader senaryo 129", "görev 129 başlat", "otomasyon 129 çalıştır"]},
        "scenario_130": {"description": "Özel senaryo 130 için yerel komut şablonu.", "examples": ["bilader senaryo 130", "görev 130 başlat", "otomasyon 130 çalıştır"]},
        "scenario_131": {"description": "Özel senaryo 131 için yerel komut şablonu.", "examples": ["bilader senaryo 131", "görev 131 başlat", "otomasyon 131 çalıştır"]},
        "scenario_132": {"description": "Özel senaryo 132 için yerel komut şablonu.", "examples": ["bilader senaryo 132", "görev 132 başlat", "otomasyon 132 çalıştır"]},
        "scenario_133": {"description": "Özel senaryo 133 için yerel komut şablonu.", "examples": ["bilader senaryo 133", "görev 133 başlat", "otomasyon 133 çalıştır"]},
        "scenario_134": {"description": "Özel senaryo 134 için yerel komut şablonu.", "examples": ["bilader senaryo 134", "görev 134 başlat", "otomasyon 134 çalıştır"]},
        "scenario_135": {"description": "Özel senaryo 135 için yerel komut şablonu.", "examples": ["bilader senaryo 135", "görev 135 başlat", "otomasyon 135 çalıştır"]},
        "scenario_136": {"description": "Özel senaryo 136 için yerel komut şablonu.", "examples": ["bilader senaryo 136", "görev 136 başlat", "otomasyon 136 çalıştır"]},
        "scenario_137": {"description": "Özel senaryo 137 için yerel komut şablonu.", "examples": ["bilader senaryo 137", "görev 137 başlat", "otomasyon 137 çalıştır"]},
        "scenario_138": {"description": "Özel senaryo 138 için yerel komut şablonu.", "examples": ["bilader senaryo 138", "görev 138 başlat", "otomasyon 138 çalıştır"]},
        "scenario_139": {"description": "Özel senaryo 139 için yerel komut şablonu.", "examples": ["bilader senaryo 139", "görev 139 başlat", "otomasyon 139 çalıştır"]},
        "scenario_140": {"description": "Özel senaryo 140 için yerel komut şablonu.", "examples": ["bilader senaryo 140", "görev 140 başlat", "otomasyon 140 çalıştır"]},
        "scenario_141": {"description": "Özel senaryo 141 için yerel komut şablonu.", "examples": ["bilader senaryo 141", "görev 141 başlat", "otomasyon 141 çalıştır"]},
        "scenario_142": {"description": "Özel senaryo 142 için yerel komut şablonu.", "examples": ["bilader senaryo 142", "görev 142 başlat", "otomasyon 142 çalıştır"]},
        "scenario_143": {"description": "Özel senaryo 143 için yerel komut şablonu.", "examples": ["bilader senaryo 143", "görev 143 başlat", "otomasyon 143 çalıştır"]},
        "scenario_144": {"description": "Özel senaryo 144 için yerel komut şablonu.", "examples": ["bilader senaryo 144", "görev 144 başlat", "otomasyon 144 çalıştır"]},
        "scenario_145": {"description": "Özel senaryo 145 için yerel komut şablonu.", "examples": ["bilader senaryo 145", "görev 145 başlat", "otomasyon 145 çalıştır"]},
        "scenario_146": {"description": "Özel senaryo 146 için yerel komut şablonu.", "examples": ["bilader senaryo 146", "görev 146 başlat", "otomasyon 146 çalıştır"]},
        "scenario_147": {"description": "Özel senaryo 147 için yerel komut şablonu.", "examples": ["bilader senaryo 147", "görev 147 başlat", "otomasyon 147 çalıştır"]},
        "scenario_148": {"description": "Özel senaryo 148 için yerel komut şablonu.", "examples": ["bilader senaryo 148", "görev 148 başlat", "otomasyon 148 çalıştır"]},
        "scenario_149": {"description": "Özel senaryo 149 için yerel komut şablonu.", "examples": ["bilader senaryo 149", "görev 149 başlat", "otomasyon 149 çalıştır"]},
        "scenario_150": {"description": "Özel senaryo 150 için yerel komut şablonu.", "examples": ["bilader senaryo 150", "görev 150 başlat", "otomasyon 150 çalıştır"]},
        "scenario_151": {"description": "Özel senaryo 151 için yerel komut şablonu.", "examples": ["bilader senaryo 151", "görev 151 başlat", "otomasyon 151 çalıştır"]},
        "scenario_152": {"description": "Özel senaryo 152 için yerel komut şablonu.", "examples": ["bilader senaryo 152", "görev 152 başlat", "otomasyon 152 çalıştır"]},
        "scenario_153": {"description": "Özel senaryo 153 için yerel komut şablonu.", "examples": ["bilader senaryo 153", "görev 153 başlat", "otomasyon 153 çalıştır"]},
        "scenario_154": {"description": "Özel senaryo 154 için yerel komut şablonu.", "examples": ["bilader senaryo 154", "görev 154 başlat", "otomasyon 154 çalıştır"]},
        "scenario_155": {"description": "Özel senaryo 155 için yerel komut şablonu.", "examples": ["bilader senaryo 155", "görev 155 başlat", "otomasyon 155 çalıştır"]},
        "scenario_156": {"description": "Özel senaryo 156 için yerel komut şablonu.", "examples": ["bilader senaryo 156", "görev 156 başlat", "otomasyon 156 çalıştır"]},
        "scenario_157": {"description": "Özel senaryo 157 için yerel komut şablonu.", "examples": ["bilader senaryo 157", "görev 157 başlat", "otomasyon 157 çalıştır"]},
        "scenario_158": {"description": "Özel senaryo 158 için yerel komut şablonu.", "examples": ["bilader senaryo 158", "görev 158 başlat", "otomasyon 158 çalıştır"]},
        "scenario_159": {"description": "Özel senaryo 159 için yerel komut şablonu.", "examples": ["bilader senaryo 159", "görev 159 başlat", "otomasyon 159 çalıştır"]},
        "scenario_160": {"description": "Özel senaryo 160 için yerel komut şablonu.", "examples": ["bilader senaryo 160", "görev 160 başlat", "otomasyon 160 çalıştır"]},
        "scenario_161": {"description": "Özel senaryo 161 için yerel komut şablonu.", "examples": ["bilader senaryo 161", "görev 161 başlat", "otomasyon 161 çalıştır"]},
        "scenario_162": {"description": "Özel senaryo 162 için yerel komut şablonu.", "examples": ["bilader senaryo 162", "görev 162 başlat", "otomasyon 162 çalıştır"]},
        "scenario_163": {"description": "Özel senaryo 163 için yerel komut şablonu.", "examples": ["bilader senaryo 163", "görev 163 başlat", "otomasyon 163 çalıştır"]},
        "scenario_164": {"description": "Özel senaryo 164 için yerel komut şablonu.", "examples": ["bilader senaryo 164", "görev 164 başlat", "otomasyon 164 çalıştır"]},
        "scenario_165": {"description": "Özel senaryo 165 için yerel komut şablonu.", "examples": ["bilader senaryo 165", "görev 165 başlat", "otomasyon 165 çalıştır"]},
        "scenario_166": {"description": "Özel senaryo 166 için yerel komut şablonu.", "examples": ["bilader senaryo 166", "görev 166 başlat", "otomasyon 166 çalıştır"]},
        "scenario_167": {"description": "Özel senaryo 167 için yerel komut şablonu.", "examples": ["bilader senaryo 167", "görev 167 başlat", "otomasyon 167 çalıştır"]},
        "scenario_168": {"description": "Özel senaryo 168 için yerel komut şablonu.", "examples": ["bilader senaryo 168", "görev 168 başlat", "otomasyon 168 çalıştır"]},
        "scenario_169": {"description": "Özel senaryo 169 için yerel komut şablonu.", "examples": ["bilader senaryo 169", "görev 169 başlat", "otomasyon 169 çalıştır"]},
        "scenario_170": {"description": "Özel senaryo 170 için yerel komut şablonu.", "examples": ["bilader senaryo 170", "görev 170 başlat", "otomasyon 170 çalıştır"]},
        "scenario_171": {"description": "Özel senaryo 171 için yerel komut şablonu.", "examples": ["bilader senaryo 171", "görev 171 başlat", "otomasyon 171 çalıştır"]},
        "scenario_172": {"description": "Özel senaryo 172 için yerel komut şablonu.", "examples": ["bilader senaryo 172", "görev 172 başlat", "otomasyon 172 çalıştır"]},
        "scenario_173": {"description": "Özel senaryo 173 için yerel komut şablonu.", "examples": ["bilader senaryo 173", "görev 173 başlat", "otomasyon 173 çalıştır"]},
        "scenario_174": {"description": "Özel senaryo 174 için yerel komut şablonu.", "examples": ["bilader senaryo 174", "görev 174 başlat", "otomasyon 174 çalıştır"]},
        "scenario_175": {"description": "Özel senaryo 175 için yerel komut şablonu.", "examples": ["bilader senaryo 175", "görev 175 başlat", "otomasyon 175 çalıştır"]},
        "scenario_176": {"description": "Özel senaryo 176 için yerel komut şablonu.", "examples": ["bilader senaryo 176", "görev 176 başlat", "otomasyon 176 çalıştır"]},
        "scenario_177": {"description": "Özel senaryo 177 için yerel komut şablonu.", "examples": ["bilader senaryo 177", "görev 177 başlat", "otomasyon 177 çalıştır"]},
        "scenario_178": {"description": "Özel senaryo 178 için yerel komut şablonu.", "examples": ["bilader senaryo 178", "görev 178 başlat", "otomasyon 178 çalıştır"]},
        "scenario_179": {"description": "Özel senaryo 179 için yerel komut şablonu.", "examples": ["bilader senaryo 179", "görev 179 başlat", "otomasyon 179 çalıştır"]},
        "scenario_180": {"description": "Özel senaryo 180 için yerel komut şablonu.", "examples": ["bilader senaryo 180", "görev 180 başlat", "otomasyon 180 çalıştır"]},
    }

    @classmethod
    def as_text(cls, limit: int = 40) -> str:
        rows: List[str] = []
        for key, val in cls.CORE_GUIDE.items():
            ex = ", ".join(val.get("examples", [])[:2])
            rows.append(f"- {key}: {val.get('description')} | örnek: {ex}")
        ext_items = list(cls.EXTENDED_GUIDE.items())[: max(0, limit - len(rows))]
        for key, val in ext_items:
            ex = ", ".join(val.get("examples", [])[:1])
            rows.append(f"- {key}: {val.get('description')} | örnek: {ex}")
        return "\n".join(rows)

    @classmethod
    def export(cls) -> Dict[str, Any]:
        return {"core": cls.CORE_GUIDE, "extended": cls.EXTENDED_GUIDE}

class LocalCommandRouter:
    def __init__(self, arduino: ArduinoHub) -> None:
        self.arduino = arduino

    def route(self, text: str) -> Optional[str]:
        t = text.lower().strip()

        if re.search(r"arduino.*bağ|bağlan.*arduino", t):
            ok, msg = self.arduino.connect()
            return msg
        if re.search(r"arduino.*(kes|kapat|ayır)", t):
            return self.arduino.disconnect()
        if re.search(r"ış(ı|i)ğ(ı|i).*yak", t):
            ok, msg = self.arduino.send("L1")
            return "Işık açma komutu gönderildi." if ok else msg
        if re.search(r"ış(ı|i)ğ(ı|i).*kapat|ış(ı|i)k.*söndür", t):
            ok, msg = self.arduino.send("L0")
            return "Işık kapatma komutu gönderildi." if ok else msg
        if re.search(r"sıcaklık|derece|ısı", t):
            ok, msg = self.arduino.send("T")
            return f"Sıcaklık: {msg}" if ok else msg

        if re.search(r"spotify.*aç|aç.*spotify", t):
            return SystemControl.open_app("spotify")
        if re.search(r"hesap makinesi.*aç|aç.*hesap makinesi", t):
            return SystemControl.open_app("calculator")
        if re.search(r"\bcpu\b|ram|disk|kaynak", t):
            s = SystemControl.snapshot()
            return f"CPU %{s['cpu']:.1f}, RAM %{s['ram_percent']:.1f}, Disk %{s['disk_percent']:.1f}."

        if re.search(r"bilgisayar(ı|i)?.*kapat", t):
            return "Güvenlik nedeniyle kapatma komutu onay olmadan çalıştırılmadı bilader."
        if re.search(r"selam|merhaba|orada mısın|uyan", t):
            return "Buradayım bilader, dinlemedeyim."
        if re.search(r"komut( listesi| rehberi)?|neler yapabiliyorsun", t):
            return "Komut rehberini ekrana bastım bilader.\n" + CommandPlaybook.as_text(25)
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

    def process_input(self, text: str, emit_event: bool = True) -> Dict[str, Any]:
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
        if emit_event:
            self.events.put({"type": "assistant_response", "payload": payload})
        return {"ok": True, **payload}


class ApiBridge:
    def __init__(self, core: BiladerCore):
        self.core = core

    def ask(self, text: str) -> Dict[str, Any]:
        # UI doğrudan bu dönüşü işlediği için event kuyruğuna tekrar düşmüyoruz.
        return self.core.process_input(text, emit_event=False)

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

    def clear_memory(self) -> Dict[str, Any]:
        self.core.memory.clear_all()
        return {"ok": True, "message": "Hafıza temizlendi."}

    def export_memory(self, limit: int = 200) -> Dict[str, Any]:
        return self.core.memory.export_bundle(limit=limit)

    def arduino_send(self, cmd: str) -> Dict[str, Any]:
        ok, msg = self.core.arduino.send(cmd.strip())
        return {"ok": ok, "message": msg}

    def get_playbook(self) -> Dict[str, Any]:
        return CommandPlaybook.export()


DIAGNOSTIC_HINTS: List[str] = [
    "İpucu 1: BİLADER senaryo kalibrasyonu adım 1 için hazır.",
    "İpucu 2: BİLADER senaryo kalibrasyonu adım 2 için hazır.",
    "İpucu 3: BİLADER senaryo kalibrasyonu adım 3 için hazır.",
    "İpucu 4: BİLADER senaryo kalibrasyonu adım 4 için hazır.",
    "İpucu 5: BİLADER senaryo kalibrasyonu adım 5 için hazır.",
    "İpucu 6: BİLADER senaryo kalibrasyonu adım 6 için hazır.",
    "İpucu 7: BİLADER senaryo kalibrasyonu adım 7 için hazır.",
    "İpucu 8: BİLADER senaryo kalibrasyonu adım 8 için hazır.",
    "İpucu 9: BİLADER senaryo kalibrasyonu adım 9 için hazır.",
    "İpucu 10: BİLADER senaryo kalibrasyonu adım 10 için hazır.",
    "İpucu 11: BİLADER senaryo kalibrasyonu adım 11 için hazır.",
    "İpucu 12: BİLADER senaryo kalibrasyonu adım 12 için hazır.",
    "İpucu 13: BİLADER senaryo kalibrasyonu adım 13 için hazır.",
    "İpucu 14: BİLADER senaryo kalibrasyonu adım 14 için hazır.",
    "İpucu 15: BİLADER senaryo kalibrasyonu adım 15 için hazır.",
    "İpucu 16: BİLADER senaryo kalibrasyonu adım 16 için hazır.",
    "İpucu 17: BİLADER senaryo kalibrasyonu adım 17 için hazır.",
    "İpucu 18: BİLADER senaryo kalibrasyonu adım 18 için hazır.",
    "İpucu 19: BİLADER senaryo kalibrasyonu adım 19 için hazır.",
    "İpucu 20: BİLADER senaryo kalibrasyonu adım 20 için hazır.",
    "İpucu 21: BİLADER senaryo kalibrasyonu adım 21 için hazır.",
    "İpucu 22: BİLADER senaryo kalibrasyonu adım 22 için hazır.",
    "İpucu 23: BİLADER senaryo kalibrasyonu adım 23 için hazır.",
    "İpucu 24: BİLADER senaryo kalibrasyonu adım 24 için hazır.",
    "İpucu 25: BİLADER senaryo kalibrasyonu adım 25 için hazır.",
    "İpucu 26: BİLADER senaryo kalibrasyonu adım 26 için hazır.",
    "İpucu 27: BİLADER senaryo kalibrasyonu adım 27 için hazır.",
    "İpucu 28: BİLADER senaryo kalibrasyonu adım 28 için hazır.",
    "İpucu 29: BİLADER senaryo kalibrasyonu adım 29 için hazır.",
    "İpucu 30: BİLADER senaryo kalibrasyonu adım 30 için hazır.",
    "İpucu 31: BİLADER senaryo kalibrasyonu adım 31 için hazır.",
    "İpucu 32: BİLADER senaryo kalibrasyonu adım 32 için hazır.",
    "İpucu 33: BİLADER senaryo kalibrasyonu adım 33 için hazır.",
    "İpucu 34: BİLADER senaryo kalibrasyonu adım 34 için hazır.",
    "İpucu 35: BİLADER senaryo kalibrasyonu adım 35 için hazır.",
    "İpucu 36: BİLADER senaryo kalibrasyonu adım 36 için hazır.",
    "İpucu 37: BİLADER senaryo kalibrasyonu adım 37 için hazır.",
    "İpucu 38: BİLADER senaryo kalibrasyonu adım 38 için hazır.",
    "İpucu 39: BİLADER senaryo kalibrasyonu adım 39 için hazır.",
    "İpucu 40: BİLADER senaryo kalibrasyonu adım 40 için hazır.",
    "İpucu 41: BİLADER senaryo kalibrasyonu adım 41 için hazır.",
    "İpucu 42: BİLADER senaryo kalibrasyonu adım 42 için hazır.",
    "İpucu 43: BİLADER senaryo kalibrasyonu adım 43 için hazır.",
    "İpucu 44: BİLADER senaryo kalibrasyonu adım 44 için hazır.",
    "İpucu 45: BİLADER senaryo kalibrasyonu adım 45 için hazır.",
    "İpucu 46: BİLADER senaryo kalibrasyonu adım 46 için hazır.",
    "İpucu 47: BİLADER senaryo kalibrasyonu adım 47 için hazır.",
    "İpucu 48: BİLADER senaryo kalibrasyonu adım 48 için hazır.",
    "İpucu 49: BİLADER senaryo kalibrasyonu adım 49 için hazır.",
    "İpucu 50: BİLADER senaryo kalibrasyonu adım 50 için hazır.",
    "İpucu 51: BİLADER senaryo kalibrasyonu adım 51 için hazır.",
    "İpucu 52: BİLADER senaryo kalibrasyonu adım 52 için hazır.",
    "İpucu 53: BİLADER senaryo kalibrasyonu adım 53 için hazır.",
    "İpucu 54: BİLADER senaryo kalibrasyonu adım 54 için hazır.",
    "İpucu 55: BİLADER senaryo kalibrasyonu adım 55 için hazır.",
    "İpucu 56: BİLADER senaryo kalibrasyonu adım 56 için hazır.",
    "İpucu 57: BİLADER senaryo kalibrasyonu adım 57 için hazır.",
    "İpucu 58: BİLADER senaryo kalibrasyonu adım 58 için hazır.",
    "İpucu 59: BİLADER senaryo kalibrasyonu adım 59 için hazır.",
    "İpucu 60: BİLADER senaryo kalibrasyonu adım 60 için hazır.",
    "İpucu 61: BİLADER senaryo kalibrasyonu adım 61 için hazır.",
    "İpucu 62: BİLADER senaryo kalibrasyonu adım 62 için hazır.",
    "İpucu 63: BİLADER senaryo kalibrasyonu adım 63 için hazır.",
    "İpucu 64: BİLADER senaryo kalibrasyonu adım 64 için hazır.",
    "İpucu 65: BİLADER senaryo kalibrasyonu adım 65 için hazır.",
    "İpucu 66: BİLADER senaryo kalibrasyonu adım 66 için hazır.",
    "İpucu 67: BİLADER senaryo kalibrasyonu adım 67 için hazır.",
    "İpucu 68: BİLADER senaryo kalibrasyonu adım 68 için hazır.",
    "İpucu 69: BİLADER senaryo kalibrasyonu adım 69 için hazır.",
    "İpucu 70: BİLADER senaryo kalibrasyonu adım 70 için hazır.",
    "İpucu 71: BİLADER senaryo kalibrasyonu adım 71 için hazır.",
    "İpucu 72: BİLADER senaryo kalibrasyonu adım 72 için hazır.",
    "İpucu 73: BİLADER senaryo kalibrasyonu adım 73 için hazır.",
    "İpucu 74: BİLADER senaryo kalibrasyonu adım 74 için hazır.",
    "İpucu 75: BİLADER senaryo kalibrasyonu adım 75 için hazır.",
    "İpucu 76: BİLADER senaryo kalibrasyonu adım 76 için hazır.",
    "İpucu 77: BİLADER senaryo kalibrasyonu adım 77 için hazır.",
    "İpucu 78: BİLADER senaryo kalibrasyonu adım 78 için hazır.",
    "İpucu 79: BİLADER senaryo kalibrasyonu adım 79 için hazır.",
    "İpucu 80: BİLADER senaryo kalibrasyonu adım 80 için hazır.",
]

def hint_slice(limit: int = 20) -> List[str]:
    return DIAGNOSTIC_HINTS[: max(1, min(limit, len(DIAGNOSTIC_HINTS)))]


    def get_hints(self, limit: int = 20) -> List[str]:
        return hint_slice(limit)


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
