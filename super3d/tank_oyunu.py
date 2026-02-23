"""Super3D ile geliştirilmiş 3D tank oyunu.

Kontroller:
- W/S: ileri/geri
- A/D: gövdeyi döndür
- Fare: nişan al (kule fareyi takip eder)
- SPACE: ateş
- ESC: çıkış
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from super3d import Kamera, Cone, Cube, Cylinder, Renderer, Sahne, Sphere


@dataclass
class Mermi:
    sekil: Sphere
    velocity: tuple[float, float, float]
    owner: str
    alive: bool = True

    def update(self, dt: float) -> None:
        if self.alive:
            self.sekil.translate(
                dx=self.velocity[0] * dt,
                dy=self.velocity[1] * dt,
                dz=self.velocity[2] * dt,
            )


class Tank:
    """M4 Sherman esintili basit tank modeli."""

    def __init__(self, name: str, position: tuple[float, float, float], color: tuple[int, int, int]) -> None:
        self.name = name
        self.position = list(position)
        self.yaw = 0.0
        self.turret_yaw = 0.0
        self.health = 140 if name == "player" else 80

        # Gövde (Sherman benzeri: geniş alt gövde + üst gövde + palet blokları)
        self.hull_bottom = Cube(size=2.15, color=color)
        self.hull_top = Cube(size=1.65, color=tuple(min(255, c + 25) for c in color))
        self.track_left = Cube(size=1.0, color=(70, 70, 70))
        self.track_right = Cube(size=1.0, color=(70, 70, 70))

        # Taret + namlu
        self.turret = Cylinder(radius=0.62, height=0.48, segments=16, color=(150, 160, 150))
        self.gun_base = Cube(size=0.32, color=(155, 155, 155))
        self.cannon = Cylinder(radius=0.12, height=1.9, segments=12, color=(190, 190, 190))

        self.parts = [
            self.hull_bottom,
            self.hull_top,
            self.track_left,
            self.track_right,
            self.turret,
            self.gun_base,
            self.cannon,
        ]
        self.sync_parts()

    @property
    def alive(self) -> bool:
        return self.health > 0

    def sync_parts(self) -> None:
        x, y, z = self.position

        # Gövde
        self.hull_bottom.position = (x, y, z)
        self.hull_bottom.scale = (1.55, 0.55, 2.05)
        self.hull_bottom.set_rotation(0.0, self.yaw, 0.0)

        self.hull_top.position = (x, y + 0.55, z - 0.05)
        self.hull_top.scale = (1.15, 0.45, 1.15)
        self.hull_top.set_rotation(0.0, self.yaw, 0.0)

        self.track_left.position = (x - math.cos(self.yaw) * 1.02, y - 0.05, z + math.sin(self.yaw) * 1.02)
        self.track_left.scale = (0.42, 0.45, 2.15)
        self.track_left.set_rotation(0.0, self.yaw, 0.0)

        self.track_right.position = (x + math.cos(self.yaw) * 1.02, y - 0.05, z - math.sin(self.yaw) * 1.02)
        self.track_right.scale = (0.42, 0.45, 2.15)
        self.track_right.set_rotation(0.0, self.yaw, 0.0)

        # Taret
        turret_world_yaw = self.yaw + self.turret_yaw
        self.turret.position = (x, y + 1.05, z)
        self.turret.scale = (1.0, 0.7, 1.0)
        self.turret.set_rotation(math.pi / 2, turret_world_yaw, 0.0)

        fwd = (math.sin(turret_world_yaw), 0.0, math.cos(turret_world_yaw))
        self.gun_base.position = (x + fwd[0] * 0.7, y + 1.05, z + fwd[2] * 0.7)
        self.gun_base.scale = (0.6, 0.4, 0.6)
        self.gun_base.set_rotation(0.0, turret_world_yaw, 0.0)

        self.cannon.position = (x + fwd[0] * 1.2, y + 1.05, z + fwd[2] * 1.2)
        self.cannon.scale = (1.0, 1.0, 1.0)
        self.cannon.set_rotation(math.pi / 2, turret_world_yaw, 0.0)

    def move(self, amount: float) -> None:
        self.position[0] += math.sin(self.yaw) * amount
        self.position[2] += math.cos(self.yaw) * amount
        self.position[0] = max(-18.0, min(18.0, self.position[0]))
        self.position[2] = max(2.0, min(48.0, self.position[2]))
        self.sync_parts()

    def rotate(self, amount: float) -> None:
        self.yaw += amount
        self.sync_parts()

    def set_turret_world_yaw(self, world_yaw: float) -> None:
        self.turret_yaw = world_yaw - self.yaw
        self.sync_parts()

    def shoot(self) -> Mermi:
        world_yaw = self.yaw + self.turret_yaw
        direction = (math.sin(world_yaw), 0.0, math.cos(world_yaw))
        spawn = (
            self.position[0] + direction[0] * 2.25,
            self.position[1] + 1.05,
            self.position[2] + direction[2] * 2.25,
        )
        bullet = Sphere(radius=0.14, stacks=5, slices=8, position=spawn, color=(255, 225, 90))
        speed = 15.0 if self.name == "player" else 8.0
        return Mermi(sekil=bullet, velocity=(direction[0] * speed, 0.0, direction[2] * speed), owner=self.name)


def clamp_angle(a: float) -> float:
    return (a + math.pi) % (2 * math.pi) - math.pi


def distance_xz(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dx = a[0] - b[0]
    dz = a[2] - b[2]
    return math.sqrt(dx * dx + dz * dz)


def rotate_x(v: tuple[float, float, float], angle: float) -> tuple[float, float, float]:
    c, s = math.cos(angle), math.sin(angle)
    return (v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c)


def rotate_y(v: tuple[float, float, float], angle: float) -> tuple[float, float, float]:
    c, s = math.cos(angle), math.sin(angle)
    return (v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c)


def mouse_to_world_yaw(kamera: Kamera, mouse_pos: tuple[int, int], screen_size: tuple[int, int], tank_y: float) -> float:
    """Fareyi yer düzlemine ışınlayarak tank kulesi için dünya yaw açısı döndürür."""
    mx, my = mouse_pos
    w, h = screen_size

    nx = (mx - w / 2) / kamera.fov
    ny = -(my - h / 2) / kamera.fov
    dir_cam = (nx, ny, 1.0)

    # camera -> world dönüşümü (world_to_camera'nin tersi)
    dir_world = rotate_x(dir_cam, kamera.pitch)
    dir_world = rotate_y(dir_world, kamera.yaw)

    plane_y = tank_y + 1.05
    if abs(dir_world[1]) < 1e-4:
        return kamera.yaw

    t = (plane_y - kamera.position[1]) / dir_world[1]
    if t < 0:
        return kamera.yaw

    hit_x = kamera.position[0] + dir_world[0] * t
    hit_z = kamera.position[2] + dir_world[2] * t
    return math.atan2(hit_x, hit_z)


def create_map(sahne: Sahne) -> list[Cube]:
    """Kolay harita: birkaç alçak engel ve siper."""
    engeller: list[Cube] = []
    random.seed(7)
    for z in [14, 20, 28, 34, 40]:
        for x in [-10, -4, 4, 10]:
            if random.random() < 0.55:
                b = Cube(size=1.6, position=(x, -1.1, z), color=(115, 95, 70))
                b.scale = (1.0, 0.7, 1.0)
                engeller.append(b)
    # Oyuncuya kolaylık: ortada güvenli koridor
    engeller = [e for e in engeller if abs(e.position[0]) > 2.8 or e.position[2] > 22]

    for e in engeller:
        sahne.ekle(e)
    return engeller


def run_game() -> None:
    renderer = Renderer(
        size=(1280, 720),
        caption="Super3D Tank Oyunu - Gelismis",
        draw_grid=True,
        draw_axes=False,
        draw_edges=False,
    )
    kamera = Kamera(position=(0, 10.5, -10), fov=620, pitch=0.62)
    sahne = Sahne(kamera=kamera)

    player = Tank("player", position=(0.0, -1.2, 7.0), color=(105, 145, 95))
    enemy = Tank("enemy", position=(0.0, -1.2, 39.0), color=(130, 130, 120))
    enemy.yaw = math.pi
    enemy.sync_parts()

    obstacles = create_map(sahne)
    for p in player.parts + enemy.parts:
        sahne.ekle(p)

    mermiler: list[Mermi] = []
    fire_cooldown = 0.0
    enemy_fire_cooldown = 1.5

    pygame.mouse.set_visible(True)

    running = True
    while running:
        dt = renderer.clock.tick(renderer.fps) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if not player.alive or not enemy.alive:
            running = False

        keys = pygame.key.get_pressed()

        # Kolay kontrol (W/S + A/D)
        if keys[pygame.K_a]:
            player.rotate(-1.65 * dt)
        if keys[pygame.K_d]:
            player.rotate(1.65 * dt)
        if keys[pygame.K_w]:
            player.move(7.2 * dt)
        if keys[pygame.K_s]:
            player.move(-5.5 * dt)

        # Kule baktığın yere dönsün (fare raycast)
        world_yaw = mouse_to_world_yaw(sahne.kamera, pygame.mouse.get_pos(), renderer.size, player.position[1])
        player.set_turret_world_yaw(world_yaw)

        fire_cooldown -= dt
        if keys[pygame.K_SPACE] and fire_cooldown <= 0:
            bullet = player.shoot()
            mermiler.append(bullet)
            sahne.ekle(bullet.sekil)
            fire_cooldown = 0.22  # oyunu kolaylaştırmak için hızlı ateş

        # Düşman AI (kolay): yavaş hareket, düşük isabet
        vec_x = player.position[0] - enemy.position[0]
        vec_z = player.position[2] - enemy.position[2]
        desired = math.atan2(vec_x, vec_z)
        enemy.rotate(clamp_angle(desired - enemy.yaw) * min(1.0, dt * 0.85))
        if distance_xz(tuple(player.position), tuple(enemy.position)) > 13:
            enemy.move(2.0 * dt)

        turret_desired = math.atan2(player.position[0] - enemy.position[0], player.position[2] - enemy.position[2])
        enemy.set_turret_world_yaw(turret_desired + random.uniform(-0.07, 0.07))

        enemy_fire_cooldown -= dt
        if enemy_fire_cooldown <= 0 and random.random() > 0.35:
            bullet = enemy.shoot()
            mermiler.append(bullet)
            sahne.ekle(bullet.sekil)
            enemy_fire_cooldown = random.uniform(1.3, 2.2)

        # Kamera oyuncuyu takip etsin
        cam_target = (player.position[0], player.position[2] - 5.8)
        kamera.position = (
            kamera.position[0] + (cam_target[0] - kamera.position[0]) * min(1.0, 4.5 * dt),
            kamera.position[1],
            kamera.position[2] + (cam_target[1] - kamera.position[2]) * min(1.0, 4.5 * dt),
        )

        # Mermiler ve çarpışma
        for m in mermiler:
            if not m.alive:
                continue
            m.update(dt)
            x, _, z = m.sekil.position
            if x < -21 or x > 21 or z < 0 or z > 52:
                m.alive = False
                continue

            # Engel çarpışması
            for obs in obstacles:
                if distance_xz(m.sekil.position, obs.position) < 1.05:
                    m.alive = False
                    break
            if not m.alive:
                continue

            if m.owner != "player" and distance_xz(m.sekil.position, tuple(player.position)) < 1.5:
                player.health = max(0, player.health - 12)
                m.alive = False
            if m.owner != "enemy" and distance_xz(m.sekil.position, tuple(enemy.position)) < 1.45:
                enemy.health = max(0, enemy.health - 28)
                m.alive = False

        for m in [x for x in mermiler if not x.alive]:
            if m.sekil in sahne.sekiller:
                sahne.sekiller.remove(m.sekil)
        mermiler = [x for x in mermiler if x.alive]

        renderer.screen.fill(renderer.bg_color)
        renderer.draw_reference(sahne.kamera)
        for shape in renderer._sorted_shapes(sahne.sekiller, sahne.kamera):
            renderer.draw_shape(shape, sahne.kamera)

        font = pygame.font.SysFont("consolas", 24)
        hud = font.render(
            f"HP: {player.health}   DUSMAN: {enemy.health}   SPACE: ATES   Fare ile NisAN",
            True,
            (240, 240, 240),
        )
        renderer.screen.blit(hud, (18, 16))

        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(renderer.screen, (255, 90, 90), (mx, my), 7, 1)
        pygame.draw.line(renderer.screen, (255, 90, 90), (mx - 10, my), (mx + 10, my), 1)
        pygame.draw.line(renderer.screen, (255, 90, 90), (mx, my - 10), (mx, my + 10), 1)

        pygame.display.flip()

    renderer.screen.fill((8, 8, 14))
    font_big = pygame.font.SysFont("consolas", 58)
    if player.health > enemy.health:
        msg, color = "Kazandiniz!", (125, 255, 125)
    elif player.health < enemy.health:
        msg, color = "Kaybettiniz!", (255, 120, 120)
    else:
        msg, color = "Berabere!", (255, 220, 120)

    text = font_big.render(msg, True, color)
    renderer.screen.blit(text, (renderer.size[0] // 2 - text.get_width() // 2, renderer.size[1] // 2 - 35))
    pygame.display.flip()
    pygame.time.wait(1800)
    pygame.quit()


if __name__ == "__main__":
    run_game()
