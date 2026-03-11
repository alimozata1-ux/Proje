"""Pixel tarzı 2D oyunlar için hafif Python motoru."""

from .engine import PixelEngine, Camera
from .map_system import TileMap, MapBounds
from .objects import GameObject
from .components import (
    Component,
    MovementComponent,
    CollisionComponent,
    LifetimeComponent,
    WrapAroundComponent,
    InputDriveComponent,
)
from .prefabs import create_car, create_tree, create_wall, create_enemy_drone
from .builders import create_city_map

__all__ = [
    "PixelEngine",
    "Camera",
    "TileMap",
    "MapBounds",
    "GameObject",
    "Component",
    "MovementComponent",
    "CollisionComponent",
    "LifetimeComponent",
    "WrapAroundComponent",
    "InputDriveComponent",
    "create_car",
    "create_tree",
    "create_wall",
    "create_enemy_drone",
    "create_city_map",
]
