from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)


@dataclass(slots=True)
class AppConfig:
    app_name: str = os.getenv("BILADER_APP_NAME", "BİLADER")
    app_width: int = int(os.getenv("BILADER_APP_WIDTH", "1500"))
    app_height: int = int(os.getenv("BILADER_APP_HEIGHT", "900"))
    web_dir: Path = ROOT_DIR / "web"

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.6"))

    arduino_port: str = os.getenv("ARDUINO_PORT", "COM3")
    arduino_baud: int = int(os.getenv("ARDUINO_BAUD", "9600"))
    arduino_timeout: float = float(os.getenv("ARDUINO_TIMEOUT", "1"))

    wake_words: tuple[str, ...] = tuple(
        os.getenv("WAKE_WORDS", "hey bilader,bilader").split(",")
    )

    tts_rate: int = int(os.getenv("TTS_RATE", "190"))
    tts_volume: float = float(os.getenv("TTS_VOLUME", "0.95"))

    memory_db: Path = ROOT_DIR / "memory.db"
    telemetry_interval: float = float(os.getenv("TELEMETRY_INTERVAL", "1.0"))

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.app_width < 960:
            issues.append("Uygulama genişliği en az 960 olmalı.")
        if self.app_height < 640:
            issues.append("Uygulama yüksekliği en az 640 olmalı.")
        if self.arduino_baud <= 0:
            issues.append("Arduino baud pozitif olmalı.")
        if not self.web_dir.exists():
            issues.append(f"web klasörü bulunamadı: {self.web_dir}")
        return issues


DEFAULT_PROMPT = """
Sen BİLADER isimli bir asistansın.
Ton: samimi, hızlı, teknik, kısa cümleler.
Hitap: 'bilader'.
Kural: Kod bloğunu ayrı üret; açıklama ve kodu karıştırma.
""".strip()


def load_config() -> AppConfig:
    return AppConfig()
