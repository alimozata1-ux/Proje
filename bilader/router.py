from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RoutedCommand:
    category: str
    intent: str
    payload: str


class CommandRouter:
    """Basit keyword tabanlı niyet yönlendirici.

    Bu modül gelecekte Gemini function calling ile değiştirilebilir.
    """

    APP_MAP = {
        "spotify": "spotify",
        "not defteri": "notepad",
        "hesap makinesi": "calc",
        "tarayıcı": "start https://www.google.com",
    }

    def route(self, utterance: str) -> RoutedCommand:
        text = utterance.lower().strip()

        if any(k in text for k in ["arduino", "bağlan", "seri"]):
            return RoutedCommand(category="arduino", intent="toggle", payload="")

        if any(k in text for k in ["ışığı yak", "lamba aç", "led aç"]):
            return RoutedCommand(category="arduino", intent="light_on", payload="L1")

        if any(k in text for k in ["ışığı kapat", "lamba kapat", "led kapat"]):
            return RoutedCommand(category="arduino", intent="light_off", payload="L0")

        if any(k in text for k in ["sıcaklık", "derece"]):
            return RoutedCommand(category="arduino", intent="temperature", payload="T")

        if any(k in text for k in ["cpu", "ram", "sistem", "kaynak"]):
            return RoutedCommand(category="system", intent="stats", payload="")

        if "aç" in text:
            for key, value in self.APP_MAP.items():
                if key in text:
                    return RoutedCommand(category="system", intent="open_app", payload=value)

        return RoutedCommand(category="ai", intent="chat", payload=utterance)
