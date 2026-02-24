"""Super3D kamera ve perspektif projeksiyon."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .yardimci import rotate_x, rotate_y, vec_sub

Vector3 = Tuple[float, float, float]


@dataclass
class Kamera:
    position: Vector3 = (0.0, 0.0, -8.0)
    fov: float = 500.0
    near: float = 0.1
    yaw: float = 0.0
    pitch: float = 0.0

    def move(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        self.position = (
            self.position[0] + dx,
            self.position[1] + dy,
            self.position[2] + dz,
        )

    def rotate(self, dyaw: float = 0.0, dpitch: float = 0.0) -> None:
        self.yaw += dyaw
        self.pitch += dpitch

    def world_to_camera(self, point: Vector3) -> Vector3:
        rel = vec_sub(point, self.position)
        # Kameranın baktığı yöne göre ters dönüş uygula
        rel = rotate_y(rel, -self.yaw)
        rel = rotate_x(rel, -self.pitch)
        return rel

    def project(self, point: Vector3, screen_size: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        width, height = screen_size
        cam_x, cam_y, cam_z = self.world_to_camera(point)

        if cam_z <= self.near:
            return None

        factor = self.fov / cam_z
        sx = int(cam_x * factor + width / 2)
        sy = int(-cam_y * factor + height / 2)
        return (sx, sy)
