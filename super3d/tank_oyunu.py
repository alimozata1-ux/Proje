"""Super3D ile basit 3D tank oyunu.

Kontroller:
- Sol/Sağ: tank gövdesini döndür
- Yukarı/Aşağı: ileri/geri hareket
- A/D: kuleyi döndür
- Space: ateş
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
        if not self.alive:
            return
        self.sekil.translate(
            dx=self.velocity[0] * dt,
            dy=self.velocity[1] * dt,
            dz=self.velocity[2] * dt,
        )


class Tank:
    def __init__(self, name: str, position: tuple[float, float, float], color: tuple[int, int, int]) -> None:
        self.name = name
        self.position = list(position)
        self.yaw = 0.0
        self.turret_yaw = 0.0
        self.speed = 0.0
        self.health = 100

        self.body = Cube(size=1.8, color=color)
        self.turret = Cylinder(radius=0.45, height=0.35, segments=14, color=(220, 220, 220))
        self.cannon = Cone(radius=0.12, height=1.2, segments=10, color=(255, 180, 100))

        self.parts = [self.body, self.turret, self.cannon]
        self.sync_parts()

    @property
    def alive(self) -> bool:
        return self.health > 0

    def sync_parts(self) -> None:
        x, y, z = self.position
        self.body.position = (x, y, z)
        self.body.set_rotation(0.0, self.yaw, 0.0)

        self.turret.position = (x, y + 0.95, z)
        self.turret.set_rotation(math.pi / 2, self.yaw + self.turret_yaw, 0.0)

        # Namlu konumu (kule önüne)
        forward = (
            math.sin(self.yaw + self.turret_yaw),
            0.0,
            math.cos(self.yaw + self.turret_yaw),
        )
        self.cannon.position = (x + forward[0] * 0.85, y + 1.0, z + forward[2] * 0.85)
        self.cannon.set_rotation(0.0, self.yaw + self.turret_yaw, math.pi / 2)

    def move(self, amount: float) -> None:
        self.position[0] += math.sin(self.yaw) * amount
        self.position[2] += math.cos(self.yaw) * amount
        self.position[0] = max(-12.0, min(12.0, self.position[0]))
        self.position[2] = max(4.0, min(32.0, self.position[2]))
        self.sync_parts()

    def rotate(self, amount: float) -> None:
        self.yaw += amount
        self.sync_parts()

    def rotate_turret(self, amount: float) -> None:
        self.turret_yaw += amount
        self.sync_parts()

    def shoot(self) -> Mermi:
        direction = (
            math.sin(self.yaw + self.turret_yaw),
            0.0,
            math.cos(self.yaw + self.turret_yaw),
        )
        spawn = (
            self.position[0] + direction[0] * 1.35,
            self.position[1] + 1.0,
            self.position[2] + direction[2] * 1.35,
        )
        bullet = Sphere(radius=0.15, stacks=5, slices=8, position=spawn, color=(255, 240, 90))
        speed = 12.0
        vel = (direction[0] * speed, 0.0, direction[2] * speed)
        return Mermi(sekil=bullet, velocity=vel, owner=self.name)


def distance_xz(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dx = a[0] - b[0]
    dz = a[2] - b[2]
    return math.sqrt(dx * dx + dz * dz)


def run_game() -> None:
    renderer = Renderer(size=(1280, 720), caption="Super3D Tank Oyunu", draw_grid=True, draw_axes=True)
    sahne = Sahne(kamera=Kamera(position=(0, 7, -8), fov=560, pitch=0.35))

    player = Tank("player", position=(0.0, -1.2, 9.0), color=(80, 200, 120))
    enemy = Tank("enemy", position=(0.0, -1.2, 24.0), color=(220, 90, 90))
    enemy.yaw = math.pi
    enemy.sync_parts()

    for part in player.parts + enemy.parts:
        sahne.ekle(part)

    mermiler: list[Mermi] = []
    fire_cooldown = 0.0
    enemy_fire_cooldown = 0.0
    enemy_turn_timer = 0.0
    enemy_turn_dir = 1.0

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
        if keys[pygame.K_LEFT]:
            player.rotate(-1.8 * dt)
        if keys[pygame.K_RIGHT]:
            player.rotate(1.8 * dt)
        if keys[pygame.K_UP]:
            player.move(6.0 * dt)
        if keys[pygame.K_DOWN]:
            player.move(-6.0 * dt)
        if keys[pygame.K_a]:
            player.rotate_turret(-2.0 * dt)
        if keys[pygame.K_d]:
            player.rotate_turret(2.0 * dt)

        fire_cooldown -= dt
        if keys[pygame.K_SPACE] and fire_cooldown <= 0:
            bullet = player.shoot()
            mermiler.append(bullet)
            sahne.ekle(bullet.sekil)
            fire_cooldown = 0.35

        # Basit düşman yapay zekası
        enemy_turn_timer -= dt
        enemy_fire_cooldown -= dt
        if enemy_turn_timer <= 0:
            enemy_turn_timer = random.uniform(0.8, 2.0)
            enemy_turn_dir = random.choice([-1.0, 1.0])

        enemy.rotate(enemy_turn_dir * 0.9 * dt)
        enemy.move(3.5 * dt)

        desired_yaw = math.atan2(player.position[0] - enemy.position[0], player.position[2] - enemy.position[2])
        diff = desired_yaw - (enemy.yaw + enemy.turret_yaw)
        diff = (diff + math.pi) % (2 * math.pi) - math.pi
        enemy.rotate_turret(max(-1.2 * dt, min(1.2 * dt, diff)))

        if enemy_fire_cooldown <= 0 and abs(diff) < 0.22:
            bullet = enemy.shoot()
            mermiler.append(bullet)
            sahne.ekle(bullet.sekil)
            enemy_fire_cooldown = random.uniform(0.7, 1.4)

        # Mermi güncelleme / çarpışma
        for mermi in mermiler:
            if not mermi.alive:
                continue
            mermi.update(dt)
            x, y, z = mermi.sekil.position
            if x < -15 or x > 15 or z < 0 or z > 36:
                mermi.alive = False
                continue

            if mermi.owner != "player" and distance_xz(mermi.sekil.position, tuple(player.position)) < 1.2:
                player.health = max(0, player.health - 20)
                mermi.alive = False
            if mermi.owner != "enemy" and distance_xz(mermi.sekil.position, tuple(enemy.position)) < 1.2:
                enemy.health = max(0, enemy.health - 20)
                mermi.alive = False

        # Ölü mermileri sahneden kaldır
        for m in [m for m in mermiler if not m.alive]:
            if m.sekil in sahne.sekiller:
                sahne.sekiller.remove(m.sekil)
        mermiler = [m for m in mermiler if m.alive]

        renderer.screen.fill(renderer.bg_color)
        renderer.draw_reference(sahne.kamera)
        for shape in renderer._sorted_shapes(sahne.sekiller, sahne.kamera):
            renderer.draw_shape(shape, sahne.kamera)

        font = pygame.font.SysFont("consolas", 24)
        hud = font.render(
            f"Player HP: {player.health}    Enemy HP: {enemy.health}    SPACE: Ates",
            True,
            (240, 240, 240),
        )
        renderer.screen.blit(hud, (20, 20))

        pygame.display.flip()

    # Oyun sonu ekranı
    renderer.screen.fill((10, 10, 15))
    font_big = pygame.font.SysFont("consolas", 56)
    if player.health > enemy.health:
        msg = "Kazandiniz!"
        color = (120, 255, 120)
    elif player.health < enemy.health:
        msg = "Kaybettiniz!"
        color = (255, 120, 120)
    else:
        msg = "Berabere!"
        color = (255, 220, 120)

    text = font_big.render(msg, True, color)
    renderer.screen.blit(text, (renderer.size[0] // 2 - text.get_width() // 2, renderer.size[1] // 2 - 40))
    pygame.display.flip()
    pygame.time.wait(1800)
    pygame.quit()


if __name__ == "__main__":
    run_game()
