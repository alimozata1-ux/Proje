"""Limanı koruma oyunu: 2 namlulu uçaksavar ile gelen uçakları vur.

Kontroller:
- Fare: hedefleme
- Sol tık: ateş
- ESC: çıkış
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from super3d import Kamera, Cone, Cube, Cylinder, Renderer, Sahne, Sphere


@dataclass
class Bullet:
    mesh: Sphere
    vel: tuple[float, float, float]
    life: float = 3.5
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.mesh.translate(dx=self.vel[0] * dt, dy=self.vel[1] * dt, dz=self.vel[2] * dt)


@dataclass
class EnemyPlane:
    body: Cylinder
    wing: Cube
    hp: int
    speed: float
    alive: bool = True

    def parts(self):
        return [self.body, self.wing]


def normalize(v: tuple[float, float, float]) -> tuple[float, float, float]:
    l = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if l == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / l, v[1] / l, v[2] / l)


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)


class AAGun:
    """2 namlulu uçaksavar: gövde 360 döner, namlu pitch yukarı-aşağı döner."""

    def __init__(self) -> None:
        self.base = Cylinder(radius=1.0, height=0.7, segments=16, position=(0, -1.3, 0), color=(80, 85, 90))
        self.base.set_rotation(math.pi / 2, 0, 0)

        self.turret = Cylinder(radius=0.65, height=0.45, segments=14, position=(0, -0.75, 0), color=(110, 120, 120))
        self.turret.set_rotation(math.pi / 2, 0, 0)

        self.barrel_left = Cylinder(radius=0.09, height=1.8, segments=10, color=(155, 165, 170))
        self.barrel_right = Cylinder(radius=0.09, height=1.8, segments=10, color=(155, 165, 170))
        self.muzzle_left = Cone(radius=0.09, height=0.22, segments=8, color=(230, 140, 90))
        self.muzzle_right = Cone(radius=0.09, height=0.22, segments=8, color=(230, 140, 90))

        self.yaw = 0.0
        self.pitch = 0.15
        self.reload = 0.0
        self.fire_side = 1

        self.sync_mesh()

    def meshes(self):
        return [self.base, self.turret, self.barrel_left, self.barrel_right, self.muzzle_left, self.muzzle_right]

    def sync_mesh(self) -> None:
        self.turret.position = (0, -0.75, 0)
        self.turret.set_rotation(math.pi / 2, self.yaw, 0)

        right = (math.cos(self.yaw), 0, -math.sin(self.yaw))
        pitch = max(-0.25, min(1.0, self.pitch))

        left_base = (-right[0] * 0.26, -0.62, right[2] * 0.26)
        right_base = (right[0] * 0.26, -0.62, -right[2] * 0.26)

        self.barrel_left.position = left_base
        self.barrel_right.position = right_base
        self.barrel_left.set_rotation(math.pi / 2 - pitch, self.yaw, 0)
        self.barrel_right.set_rotation(math.pi / 2 - pitch, self.yaw, 0)

        fwd = (math.sin(self.yaw) * math.cos(pitch), math.sin(pitch), math.cos(self.yaw) * math.cos(pitch))
        lm = (left_base[0] + fwd[0] * 0.95, left_base[1] + fwd[1] * 0.95, left_base[2] + fwd[2] * 0.95)
        rm = (right_base[0] + fwd[0] * 0.95, right_base[1] + fwd[1] * 0.95, right_base[2] + fwd[2] * 0.95)
        self.muzzle_left.position = lm
        self.muzzle_right.position = rm
        self.muzzle_left.set_rotation(0, self.yaw, math.pi / 2 - pitch)
        self.muzzle_right.set_rotation(0, self.yaw, math.pi / 2 - pitch)

    def aim_at(self, target: tuple[float, float, float]) -> None:
        dx = target[0]
        dy = target[1] + 0.7
        dz = target[2]
        self.yaw = math.atan2(dx, dz)  # 360 serbest
        flat = math.sqrt(dx * dx + dz * dz)
        self.pitch = math.atan2(dy, flat)
        self.sync_mesh()

    def shoot(self) -> Bullet | None:
        if self.reload > 0:
            return None
        self.reload = 0.08
        self.fire_side *= -1
        muzzle = self.muzzle_left if self.fire_side < 0 else self.muzzle_right
        start = muzzle.position
        fwd = normalize((
            math.sin(self.yaw) * math.cos(self.pitch),
            math.sin(self.pitch),
            math.cos(self.yaw) * math.cos(self.pitch),
        ))
        speed = 35.0
        bullet = Sphere(radius=0.08, stacks=4, slices=6, position=start, color=(255, 220, 110))
        return Bullet(mesh=bullet, vel=(fwd[0] * speed, fwd[1] * speed, fwd[2] * speed))


def spawn_enemy() -> EnemyPlane:
    side = random.choice([-1, 1])
    x = side * random.uniform(35, 55)
    y = random.uniform(8, 18)
    z = random.uniform(30, 125)

    body = Cylinder(radius=0.22, height=2.2, segments=10, position=(x, y, z), color=(180, 165, 135))
    body.set_rotation(math.pi / 2, -math.pi / 2 if side > 0 else math.pi / 2, 0)
    wing = Cube(size=1.1, position=(x, y, z), color=(165, 150, 122))
    wing.scale = (2.4, 0.1, 0.6)
    wing.set_rotation(0, -math.pi / 2 if side > 0 else math.pi / 2, 0)

    return EnemyPlane(body=body, wing=wing, hp=3, speed=random.uniform(5.5, 8.5))


def run_game() -> None:
    renderer = Renderer(size=(1366, 768), caption="Liman Savunma - Cift Namlulu Ucaksavar", draw_grid=False, draw_axes=False)
    cam = Kamera(position=(0, 22, -35), fov=610, pitch=0.38)
    scene = Sahne(kamera=cam)

    sea = Cube(size=280, position=(0, -2.4, 70), color=(36, 76, 122))
    sea.scale = (1.0, 0.01, 1.0)
    sea.set_texture("stripe", 0.06)
    port = Cube(size=60, position=(0, -2.35, 8), color=(86, 82, 74))
    port.scale = (1.0, 0.02, 0.25)

    scene.ekle(sea)
    scene.ekle(port)

    gun = AAGun()
    for m in gun.meshes():
        scene.ekle(m)

    bullets: list[Bullet] = []
    enemies: list[EnemyPlane] = []

    spawn_timer = 0.5
    score = 0
    liman_hp = 100

    while True:
        dt = renderer.clock.tick(renderer.fps) / 1000.0
        gun.reload = max(0.0, gun.reload - dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return

        # mouse hedefleme (ground plane yaklaşık)
        mx, my = pygame.mouse.get_pos()
        nx = (mx - renderer.size[0] / 2) / cam.fov
        ny = -(my - renderer.size[1] / 2) / cam.fov
        target = (nx * 70.0, ny * 35.0 + 10.0, 65.0)
        gun.aim_at(target)

        if pygame.mouse.get_pressed()[0]:
            b = gun.shoot()
            if b:
                bullets.append(b)
                scene.ekle(b.mesh)

        spawn_timer -= dt
        if spawn_timer <= 0:
            spawn_timer = random.uniform(0.55, 1.2)
            e = spawn_enemy()
            enemies.append(e)
            for p in e.parts():
                scene.ekle(p)

        # enemy movement
        for e in enemies:
            if not e.alive:
                continue
            direction = -1 if e.body.position[0] > 0 else 1
            x, y, z = e.body.position
            nxp = x + direction * e.speed * dt
            # limana yaklaşınca hasar
            if abs(nxp) < 6 and z < 18:
                liman_hp = max(0, liman_hp - 8)
                e.alive = False
                continue
            e.body.position = (nxp, y + math.sin(pygame.time.get_ticks() * 0.002 + z) * 0.01, z - e.speed * 0.42 * dt)
            e.wing.position = e.body.position

        # bullets
        for b in bullets:
            if not b.alive:
                continue
            b.update(dt)
            if b.mesh.position[1] < -2 or b.mesh.position[1] > 30 or abs(b.mesh.position[0]) > 70:
                b.alive = False
                continue

            for e in enemies:
                if not e.alive:
                    continue
                if distance(b.mesh.position, e.body.position) < 1.05:
                    e.hp -= 1
                    b.alive = False
                    if e.hp <= 0:
                        e.alive = False
                        score += 25
                    break

        for b in [x for x in bullets if not x.alive]:
            if b.mesh in scene.sekiller:
                scene.sekiller.remove(b.mesh)
        bullets = [x for x in bullets if x.alive]

        for e in [x for x in enemies if not x.alive]:
            for p in e.parts():
                if p in scene.sekiller:
                    scene.sekiller.remove(p)
        enemies = [x for x in enemies if x.alive]

        if liman_hp <= 0:
            break

        renderer.screen.fill((24, 38, 58))
        for shape in renderer._sorted_shapes(scene.sekiller, scene.kamera):
            renderer.draw_shape(shape, scene.kamera)

        font = pygame.font.SysFont("consolas", 24)
        hud = font.render(f"Liman HP: {liman_hp}  Skor: {score}  Dusman Ucak: {len(enemies)}", True, (240, 240, 240))
        renderer.screen.blit(hud, (14, 14))
        pygame.draw.rect(renderer.screen, (55, 55, 55), (14, 44, 240, 12))
        pygame.draw.rect(renderer.screen, (95, 220, 120), (14, 44, int(240 * liman_hp / 100), 12))
        pygame.draw.rect(renderer.screen, (220, 220, 220), (14, 44, 240, 12), 1)

        # crosshair
        pygame.draw.circle(renderer.screen, (255, 120, 120), (mx, my), 8, 1)
        pygame.draw.line(renderer.screen, (255, 120, 120), (mx - 10, my), (mx + 10, my), 1)
        pygame.draw.line(renderer.screen, (255, 120, 120), (mx, my - 10), (mx, my + 10), 1)

        pygame.display.flip()

    renderer.screen.fill((10, 10, 14))
    big = pygame.font.SysFont("consolas", 52)
    txt = "Liman Dustu!" if liman_hp <= 0 else "Zafer!"
    color = (255, 120, 120) if liman_hp <= 0 else (120, 255, 140)
    t = big.render(txt, True, color)
    renderer.screen.blit(t, (renderer.size[0] // 2 - t.get_width() // 2, renderer.size[1] // 2 - 40))
    f2 = pygame.font.SysFont("consolas", 30)
    st = f2.render(f"Skor: {score}", True, (240, 240, 240))
    renderer.screen.blit(st, (renderer.size[0] // 2 - st.get_width() // 2, renderer.size[1] // 2 + 22))
    pygame.display.flip()
    pygame.time.wait(2200)
    pygame.quit()


if __name__ == "__main__":
    run_game()
