"""Super3D sahne yönetimi."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from .kamera import Kamera
from .sekiller import Sekil3D


@dataclass
class Sahne:
    kamera: Kamera
    sekiller: List[Sekil3D] = field(default_factory=list)
    on_update: Optional[Callable[[float], None]] = None

    def ekle(self, sekil: Sekil3D) -> None:
        self.sekiller.append(sekil)

    def update(self, dt: float) -> None:
        self.kamera.update(dt)
        for sekil in self.sekiller:
            if sekil.visible:
                sekil.update(dt)
        if self.on_update is not None:
            self.on_update(dt)

    def sil(self, sekil: Sekil3D) -> None:
        if sekil in self.sekiller:
            self.sekiller.remove(sekil)

    def etikete_gore(self, tag: str) -> list[Sekil3D]:
        return [s for s in self.sekiller if s.tag == tag]

    def isme_gore(self, name: str) -> list[Sekil3D]:
        return [s for s in self.sekiller if s.name == name]
