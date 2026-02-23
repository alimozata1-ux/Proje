"""Super3D ile geliştirilmiş uçak oyunu: şehri bombala, uçaksavardan kaç.

Kontroller:
- A/D: sağa/sola dön
- W/S: hız artır/azalt
- Q/E: yüksel/alçal
- SPACE: bomba bırak
- P: duraklat
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
        self.body.translate(dx=self.velocity[0] * dt, dy=self.velocity[1] * dt, dz=self.velocity[2] * dt)


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
        self.body.translate(dx=self.velocity[0] * dt, dy=self.velocity[1] * dt, dz=self.velocity[2] * dt)


class Plane:
    """Daha detaylı, parçalı uçak modeli."""

    def __init__(self) -> None:
        self.position = [0.0, 9.5, -5.0]
        self.yaw = 0.0
        self.speed = 12.0
        self.health = 100
        self.reload_timer = 0.0

        self.body = Cylinder(radius=0.25, height=2.5, segments=16, color=(182, 192, 214))
        self.wing_main = Cube(size=1.2, color=(150, 162, 188))
        self.wing_tail = Cube(size=0.7, color=(145, 154, 175))
        self.vertical_tail = Cube(size=0.45, color=(135, 145, 165))
        self.nose = Cone(radius=0.17, height=0.65, segments=12, color=(220, 100, 85))
        self.engine_left = Cylinder(radius=0.08, height=0.42, segments=8, color=(95, 100, 110))
        self.engine_right = Cylinder(radius=0.08, height=0.42, segments=8, color=(95, 100, 110))

        self.parts = [
            self.body,
            self.wing_main,
            self.wing_tail,
            self.vertical_tail,
            self.nose,
            self.engine_left,
            self.engine_right,
        ]
        self.sync()

    def sync(self) -> None:
        x, y, z = self.position
        fwd = (math.sin(self.yaw), 0.0, math.cos(self.yaw))
        right = (math.cos(self.yaw), 0.0, -math.sin(self.yaw))

        self.body.position = (x, y, z)
        self.body.set_rotation(math.pi / 2, self.yaw, 0)
        self.body.set_texture("stripe", 0.13)

        self.wing_main.position = (x, y - 0.03, z)
        self.wing_main.scale = (3.6, 0.11, 0.75)
        self.wing_main.set_rotation(0, self.yaw, 0)
        self.wing_main.set_texture("checker", 0.08)

        self.wing_tail.position = (x - fwd[0] * 1.45, y + 0.04, z - fwd[2] * 1.45)
        self.wing_tail.scale = (1.3, 0.1, 0.42)
        self.wing_tail.set_rotation(0, self.yaw, 0)

        self.vertical_tail.position = (x - fwd[0] * 1.45, y + 0.48, z - fwd[2] * 1.45)
        self.vertical_tail.scale = (0.2, 0.65, 0.2)
        self.vertical_tail.set_rotation(0, self.yaw, 0)

        self.nose.position = (x + fwd[0] * 1.42, y, z + fwd[2] * 1.42)
        self.nose.set_rotation(0, self.yaw, math.pi / 2)

        el = (x - right[0] * 0.85, y - 0.04, z + right[2] * 0.85)
        er = (x + right[0] * 0.85, y - 0.04, z - right[2] * 0.85)
        self.engine_left.position = el
        self.engine_left.set_rotation(math.pi / 2, self.yaw, 0)
        self.engine_right.position = er
        self.engine_right.set_rotation(math.pi / 2, self.yaw, 0)

    def update(self, dt: float) -> None:
        self.reload_timer = max(0.0, self.reload_timer - dt)
        self.position[0] += math.sin(self.yaw) * self.speed * dt
        self.position[2] += math.cos(self.yaw) * self.speed * dt
        self.position[0] = max(-58.0, min(58.0, self.position[0]))
        self.position[2] = max(-25.0, min(185.0, self.position[2]))
        self.position[1] = max(4.0, min(20.0, self.position[1]))
        self.sync()

    def drop_bomb(self) -> Bomb | None:
        if self.reload_timer > 0:
            return None
        self.reload_timer = 0.38
        b = Sphere(radius=0.16, stacks=5, slices=7, position=tuple(self.position), color=(40, 40, 45))
        vel = [math.sin(self.yaw) * self.speed, -0.7, math.cos(self.yaw) * self.speed]
        return Bomb(body=b, velocity=vel)


class AAGun:
    def __init__(self, pos: tuple[float, float, float]) -> None:
        self.position = pos
        self.reload = random.uniform(0.8, 1.3)

        self.base = Cylinder(radius=0.52, height=0.36, segments=12, position=pos, color=(78, 88, 84))
        self.base.set_rotation(math.pi / 2, 0, 0)
        self.barrel = Cylinder(radius=0.1, height=0.95, segments=9, position=(pos[0], pos[1] + 0.35, pos[2]), color=(120, 135, 130))
        self.barrel.set_rotation(math.pi / 2, 0, 0)
        self.radar = Sphere(radius=0.16, stacks=5, slices=8, position=(pos[0], pos[1] + 0.58, pos[2]), color=(80, 130, 90))
        self.parts = [self.base, self.barrel, self.radar]

    def update(self, dt: float, plane_pos: tuple[float, float, float]) -> AAProjectile | None:
        self.reload -= dt
        dx = plane_pos[0] - self.position[0]
        dz = plane_pos[2] - self.position[2]
        dist = math.sqrt(dx * dx + dz * dz)
        yaw = math.atan2(dx, dz)

        self.barrel.set_rotation(math.pi / 2, yaw, 0)
        self.barrel.position = (self.position[0], self.position[1] + 0.35, self.position[2])
        self.radar.position = (self.position[0], self.position[1] + 0.58, self.position[2])

        if dist > 38 or self.reload > 0:
            return None

        self.reload = random.uniform(0.95, 1.45)
        speed = 13.2
        vel = [math.sin(yaw) * speed, 3.7, math.cos(yaw) * speed]
        proj = Sphere(radius=0.12, stacks=4, slices=6, position=(self.position[0], self.position[1] + 0.6, self.position[2]), color=(255, 180, 80))
        return AAProjectile(body=proj, velocity=vel)


class CityBlock:
    """Daha detaylı bina modeli: taban + gövde + çatı."""

    def __init__(self, pos: tuple[float, float, float], size: float, height: float, color_seed: float) -> None:
        self.hp = int(height * 34)
        self.max_hp = self.hp
        self.destroyed = False

        base_color = (
            int(80 + 35 * color_seed),
            int(90 + 30 * color_seed),
            int(102 + 28 * color_seed),
        )

        self.base = Cube(size=size, position=(pos[0], pos[1], pos[2]), color=base_color)
        self.base.scale = (1.0, 0.25, 1.0)
        self.base.set_texture("flat")

        self.tower = Cube(size=size * 0.86, position=(pos[0], pos[1] + 0.7, pos[2]), color=base_color)
        self.tower.scale = (1.0, height, 1.0)
        self.tower.set_texture("checker", 0.11)

        self.roof = Cube(size=size * 0.92, position=(pos[0], pos[1] + 1.25 + height * 0.45, pos[2]), color=(70, 70, 78))
        self.roof.scale = (1.0, 0.12, 1.0)

        self.parts = [self.base, self.tower, self.roof]

    @property
    def center(self) -> tuple[float, float, float]:
        return self.tower.position

    def hit(self, damage: int) -> bool:
        if self.destroyed:
            return False
        self.hp -= damage
        if self.hp <= 0:
            self.destroyed = True
            for p in self.parts:
                p.color = (38, 38, 38)
                p.set_texture("flat", 0)
            return True
        return False


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dx, dy, dz = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def run_game() -> None:
    renderer = Renderer(size=(1366, 768), caption="Super3D Ucak Oyunu - Sehri Bombala", draw_grid=False, draw_axes=False)
    # Kullanıcı isteğine göre kamera uçakta ama sabit offsetli
    camera = Kamera(position=(0, 13.0, -18.0), fov=560, pitch=0.35)
    scene = Sahne(kamera=camera)

    # sabit zemin
    ground = Cube(size=260, position=(0, -2.3, 80), color=(35, 75, 35))
    ground.scale = (1.0, 0.02, 1.0)
    ground.set_texture("stripe", 0.06)
    scene.ekle(ground)

    plane = Plane()
    for p in plane.parts:
        scene.ekle(p)

    city: list[CityBlock] = []
    aaguns: list[AAGun] = []

    random.seed(9)
    for z in range(36, 170, 11):
        for x in range(-36, 37, 9):
            h = random.uniform(0.9, 2.7)
            cseed = random.random()
            block = CityBlock(pos=(x, -1.4, z), size=3.8, height=h, color_seed=cseed)
            city.append(block)
            for part in block.parts:
                scene.ekle(part)

            if random.random() < 0.30:
                gun = AAGun((x + random.uniform(-2.0, 2.0), -1.0, z + random.uniform(-2.0, 2.0)))
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
            plane.speed = min(23.0, plane.speed + 8.0 * dt)
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

        # Kamera uçağa bağlı ama sabit bir ofsetten izler
        cam_back = 15.5
        cam_up = 5.8
        camera.position = (
            plane.position[0] - math.sin(plane.yaw) * cam_back,
            plane.position[1] + cam_up,
            plane.position[2] - math.cos(plane.yaw) * cam_back,
        )
        camera.yaw = plane.yaw
        camera.pitch = 0.33

        for g in aaguns:
            shot = g.update(dt, tuple(plane.position))
            if shot:
                aa_shots.append(shot)
                scene.ekle(shot.body)

        for bomb in bombs:
            if not bomb.alive:
                continue
            bomb.update(dt)
            if bomb.body.position[1] <= -1.3:
                for block in city:
                    if (not block.destroyed) and distance(bomb.body.position, block.center) < 3.5:
                        destroyed = block.hit(95)
                        if destroyed:
                            score += 110
                bomb.alive = False

        for shot in aa_shots:
            if not shot.alive:
                continue
            shot.update(dt)
            if distance(shot.body.position, tuple(plane.position)) < 1.25:
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
        renderer.screen.fill((int(22 + 18 * day), int(32 + 38 * day), int(48 + 58 * day)))
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
