from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import pygame

from .map_system import TileMap, MapBounds
from .objects import GameObject


@dataclass
class Camera:
    x: float = 0
    y: float = 0


class PixelEngine:
    def __init__(
        self,
        width: int = 960,
        height: int = 540,
        title: str = "Pixel Engine",
        background_color: tuple[int, int, int] = (30, 30, 45),
        fps: int = 60,
        pixel_scale: int = 1,
    ) -> None:
        pygame.init()
        self.width = width
        self.height = height
        self.title = title
        self.background_color = background_color
        self.fps = fps
        self.pixel_scale = max(pixel_scale, 1)
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

        self.camera = Camera()
        self.objects: list[GameObject] = []
        self.map: TileMap | None = None
        self.map_bounds = MapBounds(0, 0, width, height)
        self.running = False

    def set_map(self, tile_map: TileMap) -> None:
        self.map = tile_map
        self.map_bounds = tile_map.bounds

    def add_object(self, obj: GameObject) -> GameObject:
        self.objects.append(obj)
        return obj

    def add_objects(self, objects: Iterable[GameObject]) -> None:
        self.objects.extend(objects)

    def remove_destroyed(self) -> None:
        self.objects = [obj for obj in self.objects if not obj.destroyed]

    def process_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            for obj in self.objects:
                obj.on_event(event)
        return True

    def update(self, dt: float) -> None:
        for obj in self.objects:
            obj.update(dt, self)
        self.remove_destroyed()

    def draw(self) -> None:
        self.screen.fill(self.background_color)
        if self.map:
            self.map.draw(self.screen, self.camera)
        for obj in sorted(self.objects, key=lambda x: x.z_index):
            obj.draw(self.screen, self.camera)
        pygame.display.flip()

    def run(self, on_start: Callable[["PixelEngine"], None] | None = None) -> None:
        if on_start:
            on_start(self)

        self.running = True
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.running = self.process_events()
            self.update(dt)
            self.draw()

        pygame.quit()
