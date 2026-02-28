from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


CommandHandler = Callable[[str, "RuntimeContext"], Any]


@dataclass
class CommandRegistry:
    handlers: dict[str, CommandHandler] = field(default_factory=dict)

    def register(self, name: str, handler: CommandHandler) -> None:
        self.handlers[name] = handler

    def execute(self, name: str, args: str, ctx: "RuntimeContext") -> Any:
        if name not in self.handlers:
            raise KeyError(f"Unknown command: {name}")
        return self.handlers[name](args, ctx)


class RuntimeContext:  # lightweight protocol carrier
    pass
