from __future__ import annotations

from .map_system import TileMap


def create_city_map(width_tiles: int = 64, height_tiles: int = 36, tile_size: int = 16) -> TileMap:
    tile_map = TileMap(tile_size=tile_size, width_tiles=width_tiles, height_tiles=height_tiles, default_tile=1)
    tile_map.add_border(tile_id=2)

    # Yollar
    tile_map.fill_rect(4, 6, width_tiles - 8, 4, 0)
    tile_map.fill_rect(4, 16, width_tiles - 8, 4, 0)
    tile_map.fill_rect(10, 2, 5, height_tiles - 4, 0)
    tile_map.fill_rect(width_tiles - 15, 2, 5, height_tiles - 4, 0)

    # Su alanı
    tile_map.fill_rect(width_tiles // 2 - 6, height_tiles // 2 + 2, 12, 6, 3)
    return tile_map
