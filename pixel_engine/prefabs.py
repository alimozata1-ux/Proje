from __future__ import annotations

from .components import CollisionComponent, InputDriveComponent, MovementComponent, WrapAroundComponent
from .objects import GameObject


def create_car(x: float, y: float, color: tuple[int, int, int] = (200, 30, 40)) -> GameObject:
    """Hazır araba nesnesi: sürüş, hareket, çarpışma içerir."""
    car = GameObject(name="car", x=x, y=y, width=24, height=14, color=color, z_index=3)
    car.tags.add("player")
    car.add_component(InputDriveComponent(speed=220))
    car.add_component(MovementComponent())
    car.add_component(CollisionComponent(block_tag="solid"))
    return car


def create_wall(x: float, y: float, width: int, height: int) -> GameObject:
    wall = GameObject(name="wall", x=x, y=y, width=width, height=height, color=(85, 85, 90), z_index=2)
    wall.tags.add("solid")
    return wall


def create_tree(x: float, y: float) -> GameObject:
    tree = GameObject(name="tree", x=x, y=y, width=18, height=18, color=(20, 140, 50), z_index=1)
    tree.tags.add("solid")
    return tree


def create_enemy_drone(x: float, y: float, speed: float = 90) -> GameObject:
    drone = GameObject(name="drone", x=x, y=y, width=12, height=12, color=(240, 190, 40), z_index=2)
    drone.velocity_x = speed
    drone.velocity_y = speed * 0.4
    drone.add_component(MovementComponent())
    drone.add_component(WrapAroundComponent())
    return drone
