"""Super3D yardımcı matematik fonksiyonları."""

from __future__ import annotations

import math
from typing import Iterable, Tuple

Vector3 = Tuple[float, float, float]


def vec_add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec_sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_scale(v: Vector3, s: float) -> Vector3:
    return (v[0] * s, v[1] * s, v[2] * s)


def dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def length(v: Vector3) -> float:
    return math.sqrt(dot(v, v))


def normalize(v: Vector3) -> Vector3:
    l = length(v)
    if l == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / l, v[1] / l, v[2] / l)


def rotate_x(v: Vector3, angle: float) -> Vector3:
    c, s = math.cos(angle), math.sin(angle)
    return (v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c)


def rotate_y(v: Vector3, angle: float) -> Vector3:
    c, s = math.cos(angle), math.sin(angle)
    return (v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c)


def rotate_z(v: Vector3, angle: float) -> Vector3:
    c, s = math.cos(angle), math.sin(angle)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c, v[2])


def rotate_xyz(v: Vector3, angles: Vector3) -> Vector3:
    x, y, z = angles
    return rotate_z(rotate_y(rotate_x(v, x), y), z)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def center_of_points(points: Iterable[Vector3]) -> Vector3:
    pts = list(points)
    if not pts:
        return (0.0, 0.0, 0.0)
    sx = sum(p[0] for p in pts)
    sy = sum(p[1] for p in pts)
    sz = sum(p[2] for p in pts)
    n = float(len(pts))
    return (sx / n, sy / n, sz / n)
