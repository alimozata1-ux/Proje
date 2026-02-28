from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class SandboxPolicy:
    enabled: bool = False
    allowed_roots: list[Path] = field(default_factory=lambda: [Path.cwd()])
    allow_shell: bool = False
    allow_network: bool = False

    def is_path_allowed(self, target: Path) -> bool:
        if not self.enabled:
            return True
        target = target.resolve()
        return any(str(target).startswith(str(root.resolve())) for root in self.allowed_roots)

    def ensure_path(self, target: Path) -> None:
        if not self.is_path_allowed(target):
            raise PermissionError(f"Sandbox blocked path: {target}")

    def ensure_shell(self) -> None:
        if self.enabled and not self.allow_shell:
            raise PermissionError("Sandbox blocked shell command")

    def ensure_network(self) -> None:
        if self.enabled and not self.allow_network:
            raise PermissionError("Sandbox blocked network command")


def parse_sandbox_args(args: str) -> SandboxPolicy:
    mode = args.strip().lower()
    if mode in {"on", "strict"}:
        return SandboxPolicy(enabled=True, allow_shell=False, allow_network=False)
    if mode == "dev":
        return SandboxPolicy(enabled=True, allow_shell=True, allow_network=True)
    return SandboxPolicy(enabled=False, allow_shell=True, allow_network=True)
