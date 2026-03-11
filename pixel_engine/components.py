from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from .engine import PixelEngine
    from .objects import GameObject


@dataclass
class Component:
    owner: "GameObject" | None = None

    def update(self, dt: float, engine: "PixelEngine") -> None:
        pass

    def on_event(self, event: pygame.event.Event) -> None:
        pass


class MovementComponent(Component):
    def update(self, dt: float, engine: "PixelEngine") -> None:
        if not self.owner:
            return
        next_x = self.owner.x + self.owner.velocity_x * dt
        next_y = self.owner.y + self.owner.velocity_y * dt

        blocked_x = engine.map and (
            engine.map.is_solid_world(next_x, self.owner.y)
            or engine.map.is_solid_world(next_x + self.owner.width - 1, self.owner.y)
            or engine.map.is_solid_world(next_x, self.owner.y + self.owner.height - 1)
            or engine.map.is_solid_world(
                next_x + self.owner.width - 1, self.owner.y + self.owner.height - 1
            )
        )
        blocked_y = engine.map and (
            engine.map.is_solid_world(self.owner.x, next_y)
            or engine.map.is_solid_world(self.owner.x + self.owner.width - 1, next_y)
            or engine.map.is_solid_world(self.owner.x, next_y + self.owner.height - 1)
            or engine.map.is_solid_world(
                self.owner.x + self.owner.width - 1, next_y + self.owner.height - 1
            )
        )

        if not blocked_x:
            self.owner.x = next_x
        else:
            self.owner.velocity_x = 0

        if not blocked_y:
            self.owner.y = next_y
        else:
            self.owner.velocity_y = 0


class CollisionComponent(Component):
    def __init__(self, block_tag: str = "solid") -> None:
        super().__init__()
        self.block_tag = block_tag

    def update(self, dt: float, engine: "PixelEngine") -> None:
        if not self.owner:
            return
        for obj in engine.objects:
            if obj is self.owner or self.block_tag not in obj.tags:
                continue
            if self.owner.collides_with(obj):
                self.owner.x -= self.owner.velocity_x * dt
                self.owner.y -= self.owner.velocity_y * dt
                self.owner.velocity_x = 0
                self.owner.velocity_y = 0
                break


class LifetimeComponent(Component):
    def __init__(self, seconds: float) -> None:
        super().__init__()
        self.remaining = seconds

    def update(self, dt: float, engine: "PixelEngine") -> None:
        if not self.owner:
            return
        self.remaining -= dt
        if self.remaining <= 0:
            self.owner.destroy()


class WrapAroundComponent(Component):
    """Map sınırından çıkan nesneyi karşı taraftan getirir."""

    def update(self, dt: float, engine: "PixelEngine") -> None:
        if not self.owner:
            return
        bounds = engine.map_bounds

        if self.owner.x > bounds.right:
            self.owner.x = bounds.x - self.owner.width
        elif self.owner.x + self.owner.width < bounds.x:
            self.owner.x = bounds.right

        if self.owner.y > bounds.bottom:
            self.owner.y = bounds.y - self.owner.height
        elif self.owner.y + self.owner.height < bounds.y:
            self.owner.y = bounds.bottom


class InputDriveComponent(Component):
    def __init__(self, speed: float = 180) -> None:
        super().__init__()
        self.speed = speed

    def update(self, dt: float, engine: "PixelEngine") -> None:
        if not self.owner:
            return
        keys = pygame.key.get_pressed()
        self.owner.velocity_x = 0
        self.owner.velocity_y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.owner.velocity_x = -self.speed
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.owner.velocity_x = self.speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.owner.velocity_y = -self.speed
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.owner.velocity_y = self.speed
