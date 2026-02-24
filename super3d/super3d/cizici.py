"""Super3D pygame çizici modülü."""

from __future__ import annotations

from typing import Callable, Iterable, Optional, Tuple

import pygame

from .kamera import Kamera
from .sahne import Sahne
from .sekiller import Face, Sekil3D


class Renderer:
    def __init__(
        self,
        size: Tuple[int, int] = (1200, 720),
        bg_color: Tuple[int, int, int] = (18, 18, 24),
        fps: int = 60,
        caption: str = "Super3D",
        draw_grid: bool = True,
        draw_axes: bool = True,
        draw_edges: bool = False,
    ) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.size = size
        self.bg_color = bg_color
        self.fps = fps
        self.draw_grid = draw_grid
        self.draw_axes = draw_axes
        self.draw_edges = draw_edges

    def _draw_line_3d(self, kamera: Kamera, p1, p2, color, width=1) -> None:
        s1 = kamera.project(p1, self.size)
        s2 = kamera.project(p2, self.size)
        if s1 is not None and s2 is not None:
            pygame.draw.line(self.screen, color, s1, s2, width)

    def draw_reference(self, kamera: Kamera) -> None:
        if self.draw_grid:
            grid_color = (45, 45, 58)
            for i in range(-10, 11):
                self._draw_line_3d(kamera, (i, -2, 0), (i, -2, 20), grid_color)
                self._draw_line_3d(kamera, (-10, -2, i + 10), (10, -2, i + 10), grid_color)

        if self.draw_axes:
            self._draw_line_3d(kamera, (0, 0, 0), (3, 0, 0), (255, 80, 80), 2)
            self._draw_line_3d(kamera, (0, 0, 0), (0, 3, 0), (80, 255, 80), 2)
            self._draw_line_3d(kamera, (0, 0, 0), (0, 0, 3), (80, 120, 255), 2)

    def _face_depth(self, face: Face, verts: list[tuple[float, float, float]], kamera: Kamera) -> float:
        zs = [kamera.world_to_camera(verts[i])[2] for i in face]
        return sum(zs) / len(zs)


    def _poly_reasonable(self, poly: list[tuple[int, int]]) -> bool:
        """Near-plane taşmalarında oluşan dev/bozuk polygonları elemek için koruma."""
        if not poly:
            return False
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Tamamen ekran dışında çok uzaksa çizme
        margin = 2500
        if max_x < -margin or min_x > self.size[0] + margin or max_y < -margin or min_y > self.size[1] + margin:
            return False

        # Aşırı büyük span'ler yatay/dikey artefakta neden olabiliyor
        if (max_x - min_x) > self.size[0] * 8 or (max_y - min_y) > self.size[1] * 8:
            return False

        # Alanı çok küçük/bozuk polygonları da ele
        area2 = 0
        for i in range(len(poly)):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % len(poly)]
            area2 += x1 * y2 - x2 * y1
        if abs(area2) < 2:
            return False
        return True

    def _draw_polygon_alpha(self, color: tuple[int, int, int], points: list[tuple[int, int]], alpha: int) -> None:
        if alpha >= 255:
            pygame.draw.polygon(self.screen, color, points)
            return
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        w = max(1, max_x - min_x + 1)
        h = max(1, max_y - min_y + 1)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        shifted = [(p[0] - min_x, p[1] - min_y) for p in points]
        pygame.draw.polygon(surf, (color[0], color[1], color[2], alpha), shifted)
        self.screen.blit(surf, (min_x, min_y))

    def draw_shape(self, shape: Sekil3D, kamera: Kamera) -> None:
        if not getattr(shape, "visible", True):
            return

        points_3d = shape.transformed_vertices()
        points_2d = [kamera.project(p, self.size) for p in points_3d]

        if shape.faces:
            indexed_faces = list(enumerate(shape.faces))
            faces_sorted = sorted(indexed_faces, key=lambda item: self._face_depth(item[1], points_3d, kamera), reverse=True)
            for face_index, face in faces_sorted:
                poly = [points_2d[idx] for idx in face]
                if any(p is None for p in poly):
                    continue
                if not self._poly_reasonable(poly):
                    continue
                self._draw_polygon_alpha(shape.face_color(face_index), poly, shape.alpha)
                if self.draw_edges:
                    pygame.draw.polygon(self.screen, (25, 25, 25), poly, max(1, shape.line_thickness))
        elif self.draw_edges:
            for i1, i2 in shape.edges:
                p1 = points_2d[i1]
                p2 = points_2d[i2]
                if p1 is not None and p2 is not None:
                    pygame.draw.line(self.screen, shape.color, p1, p2, max(1, shape.line_thickness))

        if shape.show_vertices:
            for p in points_2d:
                if p is not None:
                    pygame.draw.circle(self.screen, (255, 255, 255), p, 2)


    def draw_hud_text(
        self,
        text: str,
        pos: tuple[int, int] = (12, 12),
        color: tuple[int, int, int] = (240, 240, 240),
        size: int = 22,
        font_name: str = "consolas",
    ) -> None:
        font = pygame.font.SysFont(font_name, size)
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)


    def draw_progress_bar(
        self,
        value: float,
        pos: tuple[int, int],
        size: tuple[int, int],
        color: tuple[int, int, int] = (90, 200, 255),
        bg: tuple[int, int, int] = (28, 30, 38),
    ) -> None:
        x, y = pos
        w, h = size
        value = max(0.0, min(1.0, value))
        pygame.draw.rect(self.screen, bg, (x, y, w, h), border_radius=5)
        pygame.draw.rect(self.screen, color, (x + 2, y + 2, int((w - 4) * value), h - 4), border_radius=4)
        pygame.draw.rect(self.screen, (220, 220, 220), (x, y, w, h), 1, border_radius=5)

    def draw_crosshair(
        self,
        center: tuple[int, int] | None = None,
        color: tuple[int, int, int] = (255, 120, 120),
        radius: int = 10,
    ) -> None:
        cx, cy = center if center is not None else (self.size[0] // 2, self.size[1] // 2)
        pygame.draw.circle(self.screen, color, (cx, cy), radius, 1)
        pygame.draw.line(self.screen, color, (cx - radius - 2, cy), (cx + radius + 2, cy), 1)
        pygame.draw.line(self.screen, color, (cx, cy - radius - 2), (cx, cy + radius + 2), 1)

    def _sorted_shapes(self, shapes: Iterable[Sekil3D], kamera: Kamera) -> list[Sekil3D]:
        return sorted(
            list(shapes),
            key=lambda s: kamera.world_to_camera(s.center_world())[2],
            reverse=True,
        )

    def run(self, shapes: Iterable[Sekil3D], kamera: Kamera, update_fn=None) -> None:
        scene = Sahne(kamera=kamera, sekiller=list(shapes))
        self.run_scene(scene, update_fn)

    def run_scene(self, scene: Sahne, update_fn: Optional[Callable[[], None]] = None) -> None:
        running = True
        while running:
            dt = self.clock.tick(self.fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            move_speed = 6.0 * dt
            rot_speed = 1.4 * dt

            if keys[pygame.K_w]:
                scene.kamera.move(dz=move_speed)
            if keys[pygame.K_s]:
                scene.kamera.move(dz=-move_speed)
            if keys[pygame.K_a]:
                scene.kamera.move(dx=-move_speed)
            if keys[pygame.K_d]:
                scene.kamera.move(dx=move_speed)
            if keys[pygame.K_q]:
                scene.kamera.move(dy=move_speed)
            if keys[pygame.K_e]:
                scene.kamera.move(dy=-move_speed)
            if keys[pygame.K_LEFT]:
                scene.kamera.rotate(dyaw=-rot_speed)
            if keys[pygame.K_RIGHT]:
                scene.kamera.rotate(dyaw=rot_speed)
            if keys[pygame.K_UP]:
                scene.kamera.rotate(dpitch=rot_speed)
            if keys[pygame.K_DOWN]:
                scene.kamera.rotate(dpitch=-rot_speed)

            scene.update(dt)
            if update_fn:
                update_fn()

            self.screen.fill(self.bg_color)
            self.draw_reference(scene.kamera)
            for shape in self._sorted_shapes(scene.sekiller, scene.kamera):
                self.draw_shape(shape, scene.kamera)

            pygame.display.flip()

        pygame.quit()
