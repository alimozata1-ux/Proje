from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .config import DEFAULT_PROMPT
from .memory import ChatMessage

try:
    from google import genai
except Exception:
    genai = None


@dataclass(slots=True)
class GeminiResult:
    text: str
    model: str
    ok: bool
    error: str = ""


class GeminiService:
    def __init__(self, api_key: str, model: str, temperature: float = 0.6) -> None:
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = None
        self._setup()

    def _setup(self) -> None:
        if not self.api_key or genai is None:
            self.client = None
            return
        self.client = genai.Client(api_key=self.api_key)

    @property
    def available(self) -> bool:
        return self.client is not None

    def _build_context(self, history: Iterable[ChatMessage]) -> list[dict]:
        contents: list[dict] = [{"role": "user", "parts": [{"text": DEFAULT_PROMPT}]}]
        for item in history:
            role = "model" if item.role == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": item.content}]})
        return contents

    def ask(self, prompt: str, history: Iterable[ChatMessage]) -> GeminiResult:
        if self.client is None:
            return GeminiResult(
                text=(
                    "Gemini bağlantısı kapalı bilader. "
                    "GEMINI_API_KEY değişkenini ayarlayıp tekrar dene."
                ),
                model=self.model,
                ok=False,
                error="missing_api_key_or_dependency",
            )

        try:
            contents = self._build_context(history)
            contents.append({"role": "user", "parts": [{"text": prompt}]})
            result = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config={"temperature": self.temperature},
            )
            return GeminiResult(
                text=result.text or "Şu an cevap üretemedim bilader.",
                model=self.model,
                ok=True,
            )
        except Exception as exc:
            return GeminiResult(
                text=f"Gemini çağrısında hata var bilader: {exc}",
                model=self.model,
                ok=False,
                error=str(exc),
            )
