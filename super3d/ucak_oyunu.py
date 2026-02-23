"""Super3D ile basit uçak oyunu: şehri bombala, uçaksavardan kaç.

Kontroller:
- A/D: sağa/sola dön
- W/S: hız artır/azalt
- Q/E: yüksel/alçal
- SPACE: bomba bırak
- ESC: çıkış
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from super3d import Kamera, Cone, Cube, Cylinder, Renderer, Sahne, Sphere


@dataclass
class Bomb:
    body: Sphere
    velocity: list[float]
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.velocity[1] -= 12.0 * dt
        self.body.translate(
            dx=self.velocity[0] * dt,
            dy=self.velocity[1] * dt,
            dz=self.velocity[2] * dt,
        )


@dataclass
class AAProjectile:
    body: Sphere
    velocity: list[float]
    life: float = 4.0
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.body.translate(
            dx=self.velocity[0] * dt,
            dy=self.velocity[1] * dt,
            dz=self.velocity[2] * dt,
        )


class Plane:
    def __init__(self) -> None:
        self.position = [0.0, 9.0, -8.0]
        self.yaw = 0.0
        self.speed = 12.0
        self.health = 100
        self.reload_timer = 0.0

        self.body = Cylinder(radius=0.22, height=2.2, segments=14, color=(175, 185, 205))
        self.body.set_rotation(math.pi / 2, 0, 0)
        self.wing = Cube(size=1.2, color=(145, 155, 180))
        self.tail = Cube(size=0.5, color=(130, 140, 160))
        self.nose = Cone(radius=0.16, height=0.55, segments=10, color=(220, 100, 85))

        self.parts = [self.body, self.wing, self.tail, self.nose]
        self.sync()

    def sync(self) -> None:
        x, y, z = self.position
        fwd = (math.sin(self.yaw), 0.0, math.cos(self.yaw))
        right = (math.cos(self.yaw), 0.0, -math.sin(self.yaw))

        self.body.position = (x, y, z)
        self.body.set_rotation(math.pi / 2, self.yaw, 0)
        self.body.set_texture("stripe", 0.15)

        self.wing.position = (x, y, z)
        self.wing.scale = (2.6, 0.12, 0.7)
        self.wing.set_rotation(0, self.yaw, 0)

        self.tail.position = (x - fwd[0] * 0.95, y + 0.24, z - fwd[2] * 0.95)
        self.tail.scale = (0.3, 0.55, 0.15)
        self.tail.set_rotation(0, self.yaw, 0)

        self.nose.position = (x + fwd[0] * 1.2, y, z + fwd[2] * 1.2)
        self.nose.set_rotation(0, self.yaw, math.pi / 2)

    def update(self, dt: float) -> None:
        self.reload_timer = max(0.0, self.reload_timer - dt)
        self.position[0] += math.sin(self.yaw) * self.speed * dt
        self.position[2] += math.cos(self.yaw) * self.speed * dt
        self.position[0] = max(-55.0, min(55.0, self.position[0]))
        self.position[2] = max(-25.0, min(165.0, self.position[2]))
        self.position[1] = max(4.0, min(20.0, self.position[1]))
        self.sync()

    def drop_bomb(self) -> Bomb | None:
        if self.reload_timer > 0:
            return None
        self.reload_timer = 0.4
        b = Sphere(radius=0.16, stacks=5, slices=7, position=tuple(self.position), color=(45, 45, 45))
        vel = [math.sin(self.yaw) * self.speed, -0.5, math.cos(self.yaw) * self.speed]
        return Bomb(body=b, velocity=vel)


class AAGun:
    def __init__(self, pos: tuple[float, float, float]) -> None:
        self.position = pos
        self.reload = random.uniform(0.8, 1.3)

        self.base = Cylinder(radius=0.45, height=0.4, segments=10, position=pos, color=(85, 95, 90))
        self.base.set_rotation(math.pi / 2, 0, 0)
        self.barrel = Cylinder(radius=0.1, height=0.85, segments=8, position=(pos[0], pos[1] + 0.35, pos[2]), color=(120, 135, 130))
        self.barrel.set_rotation(math.pi / 2, 0, 0)
        self.parts = [self.base, self.barrel]

    def update(self, dt: float, plane_pos: tuple[float, float, float]) -> AAProjectile | None:
        self.reload -= dt
        dx = plane_pos[0] - self.position[0]
        dz = plane_pos[2] - self.position[2]
        dist = math.sqrt(dx * dx + dz * dz)
        yaw = math.atan2(dx, dz)
        self.barrel.set_rotation(math.pi / 2, yaw, 0)
        self.barrel.position = (self.position[0], self.position[1] + 0.35, self.position[2])

        if dist > 34 or self.reload > 0:
            return None

        self.reload = random.uniform(0.9, 1.4)
        speed = 13.0
        # uçaksavar hafif tahminli ateş
        vel = [math.sin(yaw) * speed, 3.8, math.cos(yaw) * speed]
        proj = Sphere(radius=0.12, stacks=4, slices=6, position=(self.position[0], self.position[1] + 0.6, self.position[2]), color=(255, 180, 80))
        return AAProjectile(body=proj, velocity=vel)


class CityBlock:
    def __init__(self, pos: tuple[float, float, float], size: float, height: float) -> None:
        self.hp = int(height * 30)
        self.max_hp = self.hp
        self.destroyed = False
        self.pos = pos

        self.mesh = Cube(size=size, position=pos, color=(90, 100, 115))
        self.mesh.scale = (1.0, height, 1.0)
        self.mesh.set_texture("checker", 0.11)

    def hit(self, damage: int) -> None:
        if self.destroyed:
            return
        self.hp -= damage
        if self.hp <= 0:
            self.destroyed = True
            self.mesh.color = (45, 45, 45)
            self.mesh.set_texture("flat", 0)


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dx, dy, dz = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def run_game() -> None:
    renderer = Renderer(size=(1366, 768), caption="Super3D Ucak Oyunu - Sehri Bombala", draw_grid=False, draw_axes=False)
    scene = Sahne(kamera=Kamera(position=(0, 12, -22), fov=620, pitch=0.44))

    plane = Plane()
    for p in plane.parts:
        scene.ekle(p)

    city: list[CityBlock] = []
    aaguns: list[AAGun] = []

    random.seed(9)
    for z in range(38, 145, 12):
        for x in range(-34, 35, 10):
            h = random.uniform(0.8, 2.2)
            b = CityBlock(pos=(x, -1.1, z), size=3.6, height=h)
            city.append(b)
            scene.ekle(b.mesh)

            if random.random() < 0.32:
                gun = AAGun((x + random.uniform(-2.0, 2.0), -0.9, z + random.uniform(-2.0, 2.0)))
                aaguns.append(gun)
                for part in gun.parts:
                    scene.ekle(part)

    bombs: list[Bomb] = []
    aa_shots: list[AAProjectile] = []
    score = 0
    pause = False

    while True:
        dt = renderer.clock.tick(renderer.fps) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_p:
                    pause = not pause

        if pause:
            renderer.screen.fill((12, 14, 18))
            f = pygame.font.SysFont("consolas", 44)
            t = f.render("PAUSED", True, (220, 220, 220))
            renderer.screen.blit(t, (renderer.size[0] // 2 - t.get_width() // 2, renderer.size[1] // 2 - 20))
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            plane.yaw -= 1.7 * dt
        if keys[pygame.K_d]:
            plane.yaw += 1.7 * dt
        if keys[pygame.K_w]:
            plane.speed = min(22.0, plane.speed + 8.0 * dt)
        if keys[pygame.K_s]:
            plane.speed = max(7.0, plane.speed - 8.0 * dt)
        if keys[pygame.K_q]:
            plane.position[1] += 8.0 * dt
        if keys[pygame.K_e]:
            plane.position[1] -= 8.0 * dt

        if keys[pygame.K_SPACE]:
            b = plane.drop_bomb()
            if b:
                bombs.append(b)
                scene.ekle(b.body)

        plane.update(dt)

        # Kamera uçağı takip etsin
        scene.kamera.position = (
            scene.kamera.position[0] + (plane.position[0] - scene.kamera.position[0]) * min(1.0, 2.3 * dt),
            scene.kamera.position[1] + ((plane.position[1] + 3.0) - scene.kamera.position[1]) * min(1.0, 2.3 * dt),
            scene.kamera.position[2] + ((plane.position[2] - 16.0) - scene.kamera.position[2]) * min(1.0, 2.3 * dt),
        )
        scene.kamera.yaw = plane.yaw * 0.2

        for g in aaguns:
            shot = g.update(dt, tuple(plane.position))
            if shot:
                aa_shots.append(shot)
                scene.ekle(shot.body)

        for bomb in bombs:
            if not bomb.alive:
                continue
            bomb.update(dt)
            if bomb.body.position[1] <= -1.1:
                # binalara hasar
                for block in city:
                    if not block.destroyed and distance(bomb.body.position, block.mesh.position) < 3.2:
                        before = block.destroyed
                        block.hit(85)
                        if (not before) and block.destroyed:
                            score += 100
                bomb.alive = False

        for shot in aa_shots:
            if not shot.alive:
                continue
            shot.update(dt)
            if distance(shot.body.position, tuple(plane.position)) < 1.2:
                plane.health = max(0, plane.health - 12)
                shot.alive = False

        for b in [x for x in bombs if not x.alive]:
            if b.body in scene.sekiller:
                scene.sekiller.remove(b.body)
        bombs = [x for x in bombs if x.alive]

        for s in [x for x in aa_shots if not x.alive]:
            if s.body in scene.sekiller:
                scene.sekiller.remove(s.body)
        aa_shots = [x for x in aa_shots if x.alive]

        alive_city = sum(1 for c in city if not c.destroyed)
        if plane.health <= 0 or alive_city == 0:
            break

        day = (math.sin(pygame.time.get_ticks() * 0.0002) + 1) / 2
        renderer.screen.fill((int(20 + 20 * day), int(30 + 40 * day), int(45 + 60 * day)))
        for shape in renderer._sorted_shapes(scene.sekiller, scene.kamera):
            renderer.draw_shape(shape, scene.kamera)

        f = pygame.font.SysFont("consolas", 22)
        hud = f.render(
            f"Can: {plane.health}  Hiz: {plane.speed:0.1f}  Skor: {score}  Kalan Bina: {alive_city}",
            True,
            (245, 245, 245),
        )
        renderer.screen.blit(hud, (15, 15))
        pygame.draw.rect(renderer.screen, (45, 45, 45), (15, 45, 240, 14))
        pygame.draw.rect(renderer.screen, (90, 220, 120), (15, 45, int(240 * (plane.health / 100)), 14))
        pygame.draw.rect(renderer.screen, (220, 220, 220), (15, 45, 240, 14), 1)

        pygame.display.flip()

    renderer.screen.fill((10, 10, 15))
    big = pygame.font.SysFont("consolas", 52)
    if plane.health <= 0:
        txt, color = "Dusuruldun!", (255, 120, 120)
    else:
        txt, color = "Sehir Yok Edildi!", (120, 255, 140)
    t = big.render(txt, True, color)
    renderer.screen.blit(t, (renderer.size[0] // 2 - t.get_width() // 2, renderer.size[1] // 2 - 40))
    f2 = pygame.font.SysFont("consolas", 30)
    st = f2.render(f"Skor: {score}", True, (240, 240, 240))
    renderer.screen.blit(st, (renderer.size[0] // 2 - st.get_width() // 2, renderer.size[1] // 2 + 26))
    pygame.display.flip()
    pygame.time.wait(2200)
    pygame.quit()


if __name__ == "__main__":
    run_game()
