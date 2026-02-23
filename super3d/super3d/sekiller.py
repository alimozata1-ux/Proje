"""Super3D 3D şekilleri (wireframe + solid mesh)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

from .yardimci import center_of_points, rotate_xyz, vec_add, vec_scale, vec_sub

Vector3 = Tuple[float, float, float]
Edge = Tuple[int, int]
Face = Tuple[int, ...]


@dataclass
class Sekil3D:
    vertices: List[Vector3]
    edges: List[Edge]
    faces: List[Face] = field(default_factory=list)
    position: Vector3 = (0.0, 0.0, 0.0)
    rotation: Vector3 = (0.0, 0.0, 0.0)
    scale: Vector3 = (1.0, 1.0, 1.0)
    angular_velocity: Vector3 = (0.0, 0.0, 0.0)
    color: Tuple[int, int, int] = (255, 255, 255)
    show_vertices: bool = False
    _local_center: Vector3 = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._local_center = center_of_points(self.vertices)

    @classmethod
    def ozel_sekil(
        cls,
        vertices: Sequence[Vector3],
        faces: Sequence[Face],
        edges: Sequence[Edge] | None = None,
        **kwargs,
    ) -> "Sekil3D":
        """Kullanıcının kendi mesh'ini tasarlayabilmesi için yardımcı kurucu."""
        if edges is None:
            edge_set: set[tuple[int, int]] = set()
            for face in faces:
                for i in range(len(face)):
                    a, b = face[i], face[(i + 1) % len(face)]
                    edge_set.add((min(a, b), max(a, b)))
            edges = sorted(edge_set)
        return cls(vertices=list(vertices), edges=list(edges), faces=list(faces), **kwargs)

    def rotate(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        self.rotation = (
            self.rotation[0] + dx,
            self.rotation[1] + dy,
            self.rotation[2] + dz,
        )

    def set_rotation(self, x: float, y: float, z: float) -> None:
        self.rotation = (x, y, z)

    def translate(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        self.position = (
            self.position[0] + dx,
            self.position[1] + dy,
            self.position[2] + dz,
        )

    def set_scale(self, sx: float, sy: float | None = None, sz: float | None = None) -> None:
        sy = sx if sy is None else sy
        sz = sx if sz is None else sz
        self.scale = (sx, sy, sz)

    def update(self, dt: float) -> None:
        self.rotate(
            self.angular_velocity[0] * dt,
            self.angular_velocity[1] * dt,
            self.angular_velocity[2] * dt,
        )

    def transformed_vertices(self) -> List[Vector3]:
        out: List[Vector3] = []
        for v in self.vertices:
            centered = vec_sub(v, self._local_center)
            scaled = (
                centered[0] * self.scale[0],
                centered[1] * self.scale[1],
                centered[2] * self.scale[2],
            )
            rotated = rotate_xyz(scaled, self.rotation)
            out.append(vec_add(vec_add(rotated, self._local_center), self.position))
        return out

    def center_world(self) -> Vector3:
        return vec_add(vec_scale(self._local_center, 1.0), self.position)


class Cube(Sekil3D):
    def __init__(self, size: float = 2.0, **kwargs) -> None:
        s = size / 2
        vertices = [
            (-s, -s, -s),
            (s, -s, -s),
            (s, s, -s),
            (-s, s, -s),
            (-s, -s, s),
            (s, -s, s),
            (s, s, s),
            (-s, s, s),
        ]
        edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),
        ]
        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        ]
        super().__init__(vertices=vertices, edges=edges, faces=faces, **kwargs)


class Pyramid(Sekil3D):
    def __init__(self, base: float = 2.0, height: float = 2.5, **kwargs) -> None:
        b = base / 2
        vertices = [(-b, 0, -b), (b, 0, -b), (b, 0, b), (-b, 0, b), (0, height, 0)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4), (2, 4), (3, 4)]
        faces = [(0, 1, 2, 3), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        super().__init__(vertices=vertices, edges=edges, faces=faces, **kwargs)


class Sphere(Sekil3D):
    def __init__(self, radius: float = 1.2, stacks: int = 8, slices: int = 12, **kwargs) -> None:
        vertices: List[Vector3] = []
        edges: List[Edge] = []
        faces: List[Face] = []

        for i in range(stacks + 1):
            phi = math.pi * i / stacks
            for j in range(slices):
                theta = 2 * math.pi * j / slices
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.cos(phi)
                z = radius * math.sin(phi) * math.sin(theta)
                vertices.append((x, y, z))

        for i in range(stacks + 1):
            for j in range(slices):
                idx = i * slices + j
                edges.append((idx, i * slices + (j + 1) % slices))
                if i < stacks:
                    edges.append((idx, (i + 1) * slices + j))

        for i in range(stacks):
            for j in range(slices):
                a = i * slices + j
                b = i * slices + (j + 1) % slices
                c = (i + 1) * slices + (j + 1) % slices
                d = (i + 1) * slices + j
                faces.append((a, b, c, d))

        super().__init__(vertices=vertices, edges=edges, faces=faces, **kwargs)


class Cylinder(Sekil3D):
    def __init__(self, radius: float = 1.0, height: float = 2.5, segments: int = 16, **kwargs) -> None:
        h = height / 2
        vertices = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            x = radius * math.cos(a)
            z = radius * math.sin(a)
            vertices.append((x, -h, z))
            vertices.append((x, h, z))

        edges: List[Edge] = []
        faces: List[Face] = []
        alt = list(range(0, segments * 2, 2))
        ust = list(range(1, segments * 2, 2))
        faces.append(tuple(alt))
        faces.append(tuple(reversed(ust)))

        for i in range(segments):
            ni = (i + 1) % segments
            edges.extend([(2 * i, 2 * ni), (2 * i + 1, 2 * ni + 1), (2 * i, 2 * i + 1)])
            faces.append((2 * i, 2 * ni, 2 * ni + 1, 2 * i + 1))
        super().__init__(vertices=vertices, edges=edges, faces=faces, **kwargs)


class Cone(Sekil3D):
    def __init__(self, radius: float = 1.0, height: float = 2.5, segments: int = 16, **kwargs) -> None:
        h = height / 2
        vertices = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            vertices.append((radius * math.cos(a), -h, radius * math.sin(a)))
        vertices.append((0.0, h, 0.0))
        apex = len(vertices) - 1

        edges: List[Edge] = []
        faces: List[Face] = [tuple(range(segments))]
        for i in range(segments):
            ni = (i + 1) % segments
            edges.append((i, ni))
            edges.append((i, apex))
            faces.append((i, ni, apex))

        super().__init__(vertices=vertices, edges=edges, faces=faces, **kwargs)


class Torus(Sekil3D):
    def __init__(
        self,
        major_radius: float = 1.8,
        minor_radius: float = 0.6,
        major_segments: int = 16,
        minor_segments: int = 12,
        **kwargs,
    ) -> None:
        vertices: List[Vector3] = []
        edges: List[Edge] = []
        faces: List[Face] = []

        for i in range(major_segments):
            u = 2 * math.pi * i / major_segments
            cu, su = math.cos(u), math.sin(u)
            for j in range(minor_segments):
                v = 2 * math.pi * j / minor_segments
                cv, sv = math.cos(v), math.sin(v)
                x = (major_radius + minor_radius * cv) * cu
                y = minor_radius * sv
                z = (major_radius + minor_radius * cv) * su
                vertices.append((x, y, z))

        for i in range(major_segments):
            for j in range(minor_segments):
                idx = i * minor_segments + j
                right = i * minor_segments + (j + 1) % minor_segments
                down = ((i + 1) % major_segments) * minor_segments + j
                diag = ((i + 1) % major_segments) * minor_segments + (j + 1) % minor_segments
                edges.append((idx, right))
                edges.append((idx, down))
                faces.append((idx, right, diag, down))

        super().__init__(vertices=vertices, edges=edges, faces=faces, **kwargs)


ShapeType = Sequence[Sekil3D]
