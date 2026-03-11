from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class MapBounds:
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


class TileMap:
    """Grid tabanlı map ve sınır sistemi."""

    def __init__(
        self,
        tile_size: int,
        width_tiles: int,
        height_tiles: int,
        default_tile: int = 0,
    ) -> None:
        self.tile_size = tile_size
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles
        self.tiles = [
            [default_tile for _ in range(width_tiles)] for _ in range(height_tiles)
        ]
        self.palette: dict[int, tuple[int, int, int]] = {
            0: (45, 45, 68),
            1: (68, 140, 93),
            2: (120, 120, 120),
            3: (55, 100, 165),
        }
        self.collision_tiles: set[int] = {2}

    @property
    def bounds(self) -> MapBounds:
        return MapBounds(0, 0, self.width_tiles * self.tile_size, self.height_tiles * self.tile_size)

    def resize(self, width_tiles: int, height_tiles: int, fill: int = 0) -> None:
        new_tiles = [[fill for _ in range(width_tiles)] for _ in range(height_tiles)]
        min_h = min(self.height_tiles, height_tiles)
        min_w = min(self.width_tiles, width_tiles)

        for y in range(min_h):
            for x in range(min_w):
                new_tiles[y][x] = self.tiles[y][x]

        self.tiles = new_tiles
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles

    def set_palette(self, tile_id: int, color: tuple[int, int, int]) -> None:
        self.palette[tile_id] = color

    def set_tile(self, tx: int, ty: int, tile_id: int) -> None:
        if 0 <= tx < self.width_tiles and 0 <= ty < self.height_tiles:
            self.tiles[ty][tx] = tile_id

    def fill_rect(self, x: int, y: int, w: int, h: int, tile_id: int) -> None:
        for ty in range(y, y + h):
            for tx in range(x, x + w):
                self.set_tile(tx, ty, tile_id)

    def add_border(self, tile_id: int = 2) -> None:
        for x in range(self.width_tiles):
            self.set_tile(x, 0, tile_id)
            self.set_tile(x, self.height_tiles - 1, tile_id)
        for y in range(self.height_tiles):
            self.set_tile(0, y, tile_id)
            self.set_tile(self.width_tiles - 1, y, tile_id)

    def is_solid_world(self, wx: float, wy: float) -> bool:
        tx = int(wx // self.tile_size)
        ty = int(wy // self.tile_size)
        if tx < 0 or ty < 0 or tx >= self.width_tiles or ty >= self.height_tiles:
            return True
        return self.tiles[ty][tx] in self.collision_tiles

    def draw(self, screen: pygame.Surface, camera) -> None:
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                tile = self.tiles[y][x]
                color = self.palette.get(tile, (255, 0, 255))
                rect = pygame.Rect(
                    x * self.tile_size - camera.x,
                    y * self.tile_size - camera.y,
                    self.tile_size,
                    self.tile_size,
                )
                pygame.draw.rect(screen, color, rect)
