"""FPS Shotgun Hedef Oyunu.

Amaç: Çift namlulu shotgun ile hedef tahtalarını vurup yüksek skor yapmak.

Kontroller:
- W/A/S/D: hareket
- Mouse: nişan
- Sol tık: ateş
- R: doldur (reload)
- ESC: çıkış
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from super3d import Kamera, Cone, Cube, Cylinder, Renderer, Sahne, Sphere


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def normalize(v: tuple[float, float, float]) -> tuple[float, float, float]:
    l = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if l == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / l, v[1] / l, v[2] / l)


@dataclass
class TargetBoard:
    center: tuple[float, float, float]
    radius: float
    score_value: int
    alive: bool = True

    def __post_init__(self) -> None:
        x, y, z = self.center
        self.stand = Cylinder(radius=0.12, height=2.0, segments=10, position=(x, y - 0.9, z), color=(110, 80, 55))
        self.stand.set_rotation(math.pi / 2, 0, 0)

        # Tahta halkaları (gerçeğe benzer hedef tahtası)
        self.outer = Cylinder(radius=self.radius, height=0.12, segments=20, position=self.center, color=(235, 230, 215))
        self.outer.set_rotation(math.pi / 2, 0, 0)
        self.ring1 = Cylinder(radius=self.radius * 0.75, height=0.13, segments=20, position=(x, y + 0.01, z), color=(220, 80, 80))
        self.ring1.set_rotation(math.pi / 2, 0, 0)
        self.ring2 = Cylinder(radius=self.radius * 0.48, height=0.14, segments=20, position=(x, y + 0.02, z), color=(245, 235, 205))
        self.ring2.set_rotation(math.pi / 2, 0, 0)
        self.bullseye = Sphere(radius=self.radius * 0.18, stacks=7, slices=10, position=(x, y + 0.05, z), color=(210, 40, 40))

        self.parts = [self.stand, self.outer, self.ring1, self.ring2, self.bullseye]

    def hide(self) -> None:
        if not self.alive:
            return
        self.alive = False
        for p in self.parts:
            p.color = (45, 45, 45)


@dataclass
class Bullet:
    position: tuple[float, float, float]
    velocity: tuple[float, float, float]
    ttl: float = 2.0
    active: bool = True

    def __post_init__(self) -> None:
        self.mesh = Sphere(radius=0.04, stacks=5, slices=6, position=self.position, color=(250, 205, 120))

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.ttl -= dt
        if self.ttl <= 0:
            self.active = False
            return
        self.position = (
            self.position[0] + self.velocity[0] * dt,
            self.position[1] + self.velocity[1] * dt,
            self.position[2] + self.velocity[2] * dt,
        )
        self.mesh.position = self.position


class Shotgun:
    """Çift namlulu, gerçek görünümlü shotgun modeli."""

    def __init__(self) -> None:
        self.ammo = 2
        self.reserve = 26
        self.reloading = 0.0
        self.cooldown = 0.0

        self.stock = Cube(size=0.8, color=(95, 65, 38))
        self.body = Cube(size=0.9, color=(55, 55, 60))
        self.receiver = Cube(size=0.55, color=(45, 45, 50))
        self.barrel_l = Cylinder(radius=0.05, height=1.55, segments=10, color=(95, 100, 110))
        self.barrel_r = Cylinder(radius=0.05, height=1.55, segments=10, color=(95, 100, 110))
        self.rib = Cube(size=0.25, color=(70, 75, 82))
        self.muzzle_l = Cone(radius=0.05, height=0.12, segments=8, color=(190, 160, 90))
        self.muzzle_r = Cone(radius=0.05, height=0.12, segments=8, color=(190, 160, 90))

        self.parts = [
            self.stock,
            self.body,
            self.receiver,
            self.barrel_l,
            self.barrel_r,
            self.rib,
            self.muzzle_l,
            self.muzzle_r,
        ]

    def update(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)
        if self.reloading > 0:
            self.reloading -= dt
            if self.reloading <= 0 and self.ammo < 2 and self.reserve > 0:
                # break-open shotgun: bir reload çevriminde 2 fişek
                need = min(2 - self.ammo, self.reserve)
                self.ammo += need
                self.reserve -= need

    def start_reload(self) -> None:
        if self.reloading <= 0 and self.ammo < 2 and self.reserve > 0:
            self.reloading = 1.2

    def can_fire(self) -> bool:
        return self.cooldown <= 0 and self.reloading <= 0 and self.ammo > 0

    def fire(self) -> bool:
        if not self.can_fire():
            return False
        self.cooldown = 0.55
        self.ammo -= 1
        return True

    def sync_to_camera(self, cam: Kamera) -> None:
        # Silahı oyuncunun önünde tut
        yaw, pitch = cam.yaw, cam.pitch
        fwd = (math.sin(yaw) * math.cos(pitch), math.sin(pitch), math.cos(yaw) * math.cos(pitch))
        right = (math.cos(yaw), 0.0, -math.sin(yaw))

        base = (
            cam.position[0] + fwd[0] * 0.85 + right[0] * 0.23,
            cam.position[1] - 0.20,
            cam.position[2] + fwd[2] * 0.85 + right[2] * 0.23,
        )

        self.body.position = base
        self.body.scale = (0.50, 0.20, 0.66)
        self.body.set_rotation(0, yaw, 0)

        self.receiver.position = (base[0] + fwd[0] * 0.21, base[1] + 0.015, base[2] + fwd[2] * 0.21)
        self.receiver.scale = (0.30, 0.18, 0.24)
        self.receiver.set_rotation(0, yaw, 0)

        self.stock.position = (base[0] - fwd[0] * 0.35, base[1] - 0.05, base[2] - fwd[2] * 0.35)
        self.stock.scale = (0.42, 0.18, 0.55)
        self.stock.set_rotation(0, yaw, 0)

        left_base = (base[0] - right[0] * 0.04, base[1] + 0.01, base[2] + right[2] * 0.04)
        right_base = (base[0] + right[0] * 0.04, base[1] + 0.01, base[2] - right[2] * 0.04)
        self.barrel_l.position = left_base
        self.barrel_r.position = right_base
        self.barrel_l.set_rotation(math.pi / 2 - pitch * 0.88, yaw, 0)
        self.barrel_r.set_rotation(math.pi / 2 - pitch * 0.88, yaw, 0)

        fshort = (fwd[0] * 0.78, fwd[1] * 0.78, fwd[2] * 0.78)
        self.muzzle_l.position = (left_base[0] + fshort[0], left_base[1] + fshort[1], left_base[2] + fshort[2])
        self.muzzle_r.position = (right_base[0] + fshort[0], right_base[1] + fshort[1], right_base[2] + fshort[2])
        self.muzzle_l.set_rotation(0, yaw, math.pi / 2 - pitch * 0.88)
        self.muzzle_r.set_rotation(0, yaw, math.pi / 2 - pitch * 0.88)

        rib_base = (base[0], base[1] + 0.07, base[2])
        self.rib.position = (rib_base[0] + fwd[0] * 0.42, rib_base[1], rib_base[2] + fwd[2] * 0.42)
        self.rib.scale = (0.06, 0.03, 0.65)
        self.rib.set_rotation(0, yaw, 0)


def fixed_targets() -> list[TargetBoard]:
    """Hedefler aynı hizada, sabit konumda durur."""
    z = 28.0
    y = 2.3
    xs = (-10.0, -6.0, -2.0, 2.0, 6.0, 10.0)
    targets: list[TargetBoard] = []
    for i, x in enumerate(xs):
        radius = 0.95 if i % 2 == 0 else 0.80
        score = 90 if i % 2 == 0 else 120
        targets.append(TargetBoard(center=(x, y, z), radius=radius, score_value=score))
    return targets


def run_game() -> None:
    renderer = Renderer(size=(1366, 768), caption="Shotgun Hedef FPS", draw_grid=False, draw_axes=False)
    cam = Kamera(position=(0.0, 1.6, -2.0), fov=700, pitch=0.0)
    scene = Sahne(kamera=cam)

    ground = Cube(size=160, position=(0, -2.2, 25), color=(70, 95, 70))
    ground.scale = (1.0, 0.01, 1.0)
    ground.set_texture("stripe", 0.05)
    wall = Cube(size=50, position=(0, 2.8, 42), color=(95, 92, 88))
    wall.scale = (1.0, 0.30, 0.03)
    wall.set_texture("checker", 0.08)
    scene.ekle(ground)
    scene.ekle(wall)

    shotgun = Shotgun()
    for p in shotgun.parts:
        scene.ekle(p)

    targets: list[TargetBoard] = fixed_targets()
    for t in targets:
        for p in t.parts:
            scene.ekle(p)

    bullets: list[Bullet] = []

    score = 0
    sensitivity = 0.0028
    move_speed = 6.5

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    while True:
        dt = renderer.clock.tick(renderer.fps) / 1000.0
        shotgun.update(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.event.set_grab(False)
                pygame.mouse.set_visible(True)
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.set_grab(False)
                    pygame.mouse.set_visible(True)
                    pygame.quit()
                    return
                if event.key == pygame.K_r:
                    shotgun.start_reload()

        # Mouse look
        mdx, mdy = pygame.mouse.get_rel()
        cam.yaw += mdx * sensitivity
        cam.pitch = clamp(cam.pitch - mdy * sensitivity, -0.7, 0.7)

        # WASD hareket
        keys = pygame.key.get_pressed()
        forward = (math.sin(cam.yaw), 0.0, math.cos(cam.yaw))
        right = (math.cos(cam.yaw), 0.0, -math.sin(cam.yaw))

        if keys[pygame.K_w]:
            cam.move(dx=forward[0] * move_speed * dt, dz=forward[2] * move_speed * dt)
        if keys[pygame.K_s]:
            cam.move(dx=-forward[0] * move_speed * dt, dz=-forward[2] * move_speed * dt)
        if keys[pygame.K_a]:
            cam.move(dx=-right[0] * move_speed * dt, dz=-right[2] * move_speed * dt)
        if keys[pygame.K_d]:
            cam.move(dx=right[0] * move_speed * dt, dz=right[2] * move_speed * dt)

        cam.position = (clamp(cam.position[0], -14.0, 14.0), 1.6, clamp(cam.position[2], -8.0, 10.0))

        shotgun.sync_to_camera(cam)

        if pygame.mouse.get_pressed()[0] and shotgun.fire():
            # Tek kurşun, gerçek uçuş hissi
            shoot_dir = normalize((
                math.sin(cam.yaw) * math.cos(cam.pitch),
                math.sin(cam.pitch),
                math.cos(cam.yaw) * math.cos(cam.pitch),
            ))
            muzzle_pos = (
                cam.position[0] + shoot_dir[0] * 1.0,
                cam.position[1] - 0.03 + shoot_dir[1] * 1.0,
                cam.position[2] + shoot_dir[2] * 1.0,
            )
            bullet_speed = 115.0
            bullet = Bullet(
                position=muzzle_pos,
                velocity=(shoot_dir[0] * bullet_speed, shoot_dir[1] * bullet_speed, shoot_dir[2] * bullet_speed),
            )
            bullets.append(bullet)
            scene.ekle(bullet.mesh)

        for bullet in bullets:
            if not bullet.active:
                continue
            bullet.update(dt)
            for tgt in targets:
                if not tgt.alive:
                    continue
                # Hedef tahtası z düzlemine göre gerçek çarpışma kontrolü
                dz = bullet.position[2] - tgt.center[2]
                if abs(dz) > 0.22:
                    continue
                dx = bullet.position[0] - tgt.center[0]
                dy = bullet.position[1] - tgt.center[1]
                if dx * dx + dy * dy <= tgt.radius * tgt.radius:
                    tgt.hide()
                    score += tgt.score_value
                    bullet.active = False
                    break

        for bullet in [b for b in bullets if not b.active]:
            if bullet.mesh in scene.sekiller:
                scene.sekiller.remove(bullet.mesh)
            bullets.remove(bullet)

        renderer.screen.fill((24, 30, 35))
        for shape in renderer._sorted_shapes(scene.sekiller, scene.kamera):
            renderer.draw_shape(shape, scene.kamera)

        # HUD
        font = pygame.font.SysFont("consolas", 24)
        hud = font.render(
            f"Skor: {score}   Mermi: {shotgun.ammo}/2   Yedek: {shotgun.reserve}   Reload: {'Evet' if shotgun.reloading>0 else 'Hayir'}",
            True,
            (240, 240, 240),
        )
        renderer.screen.blit(hud, (14, 14))

        # crosshair
        cx, cy = renderer.size[0] // 2, renderer.size[1] // 2
        pygame.draw.circle(renderer.screen, (255, 120, 120), (cx, cy), 10, 1)
        pygame.draw.line(renderer.screen, (255, 120, 120), (cx - 12, cy), (cx + 12, cy), 1)
        pygame.draw.line(renderer.screen, (255, 120, 120), (cx, cy - 12), (cx, cy + 12), 1)

        pygame.display.flip()


if __name__ == "__main__":
    run_game()
