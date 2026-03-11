from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .engine import PixelEngine
    from .components import Component


@dataclass
class GameObject:
    name: str
    x: float
    y: float
    width: int
    height: int
    color: tuple[int, int, int] = (220, 220, 220)
    z_index: int = 0
    velocity_x: float = 0
    velocity_y: float = 0
    tags: set[str] = field(default_factory=set)
    components: list["Component"] = field(default_factory=list)
    destroyed: bool = False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def add_component(self, component: "Component") -> "GameObject":
        component.owner = self
        self.components.append(component)
        return self

    def update(self, dt: float, engine: "PixelEngine") -> None:
        for component in self.components:
            component.update(dt, engine)

    def on_event(self, event: pygame.event.Event) -> None:
        for component in self.components:
            component.on_event(event)

    def draw(self, screen: pygame.Surface, camera) -> None:
        rect = pygame.Rect(int(self.x - camera.x), int(self.y - camera.y), self.width, self.height)
        pygame.draw.rect(screen, self.color, rect)

    def collides_with(self, other: "GameObject") -> bool:
        return self.rect().colliderect(other.rect())

    def destroy(self) -> None:
        self.destroyed = True
