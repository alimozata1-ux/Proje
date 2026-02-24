"""BF 109 Orman Saldırısı.

Amaç:
- Oyuncu BF 109 savaş uçağını kullanır.
- Ormanın içindeki düşman üssünü yok etmeye çalışır.
- Uçakta 2 makineli tüfek ve bomba bulunur.
- Düşman üssünde 4 adet AA gun vardır.

Kontroller:
- A/D: yaw (sağa/sola dön)
- W/S: hız artır/azalt
- Q/E: yüksel/alçal
- Sol Tık: çift makineli tüfek ateşi
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


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def normalize(v: tuple[float, float, float]) -> tuple[float, float, float]:
    l = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if l <= 1e-8:
        return (0.0, 0.0, 0.0)
    return (v[0] / l, v[1] / l, v[2] / l)


@dataclass
class Bullet:
    body: Sphere
    velocity: tuple[float, float, float]
    owner: str
    life: float = 2.0
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.body.translate(dx=self.velocity[0] * dt, dy=self.velocity[1] * dt, dz=self.velocity[2] * dt)


@dataclass
class Bomb:
    body: Sphere
    velocity: list[float]
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.velocity[1] -= 11.5 * dt
        self.body.translate(dx=self.velocity[0] * dt, dy=self.velocity[1] * dt, dz=self.velocity[2] * dt)


class BF109:
    def __init__(self) -> None:
        self.position = [0.0, 10.5, -70.0]
        self.yaw = 0.0
        self.speed = 13.0
        self.hp = 120
        self.gun_cooldown = 0.0
        self.bomb_cooldown = 0.0
        self.ammo = 700
        self.bombs = 10

        self.fuselage = Cylinder(radius=0.28, height=3.2, segments=18, color=(170, 180, 172))
        self.wing = Cube(size=1.2, color=(145, 160, 148))
        self.tail_wing = Cube(size=0.72, color=(140, 155, 142))
        self.tail_fin = Cube(size=0.42, color=(130, 142, 132))
        self.nose = Cone(radius=0.18, height=0.55, segments=12, color=(220, 140, 90))
        self.prop = Cylinder(radius=0.05, height=0.9, segments=8, color=(42, 42, 42))

        self.parts = [self.fuselage, self.wing, self.tail_wing, self.tail_fin, self.nose, self.prop]
        self.sync()

    def sync(self) -> None:
        x, y, z = self.position
        fwd = (math.sin(self.yaw), 0.0, math.cos(self.yaw))

        self.fuselage.position = (x, y, z)
        self.fuselage.set_rotation(math.pi / 2, self.yaw, 0.0)

        self.wing.position = (x, y - 0.04, z)
        self.wing.scale = (4.0, 0.12, 0.72)
        self.wing.set_rotation(0.0, self.yaw, 0.0)

        self.tail_wing.position = (x - fwd[0] * 1.55, y + 0.05, z - fwd[2] * 1.55)
        self.tail_wing.scale = (1.25, 0.10, 0.38)
        self.tail_wing.set_rotation(0.0, self.yaw, 0.0)

        self.tail_fin.position = (x - fwd[0] * 1.55, y + 0.50, z - fwd[2] * 1.55)
        self.tail_fin.scale = (0.18, 0.72, 0.2)
        self.tail_fin.set_rotation(0.0, self.yaw, 0.0)

        self.nose.position = (x + fwd[0] * 1.75, y, z + fwd[2] * 1.75)
        self.nose.set_rotation(0.0, self.yaw, math.pi / 2)

        self.prop.position = (x + fwd[0] * 2.0, y, z + fwd[2] * 2.0)
        self.prop.set_rotation(0.0, self.yaw, math.pi / 2)

    def update(self, dt: float) -> None:
        self.gun_cooldown = max(0.0, self.gun_cooldown - dt)
        self.bomb_cooldown = max(0.0, self.bomb_cooldown - dt)
        self.position[0] += math.sin(self.yaw) * self.speed * dt
        self.position[2] += math.cos(self.yaw) * self.speed * dt
        self.position[0] = clamp(self.position[0], -120.0, 120.0)
        self.position[2] = clamp(self.position[2], -120.0, 220.0)
        self.position[1] = clamp(self.position[1], 5.0, 28.0)
        self.sync()

    def shoot_machineguns(self) -> list[Bullet]:
        if self.gun_cooldown > 0 or self.ammo <= 0:
            return []
        self.gun_cooldown = 0.08

        self.ammo = max(0, self.ammo - 2)
        fwd = normalize((math.sin(self.yaw), -0.01, math.cos(self.yaw)))
        right = (math.cos(self.yaw), 0.0, -math.sin(self.yaw))

        left_pos = (
            self.position[0] - right[0] * 0.38 + fwd[0] * 2.05,
            self.position[1] - 0.08,
            self.position[2] + right[2] * 0.38 + fwd[2] * 2.05,
        )
        right_pos = (
            self.position[0] + right[0] * 0.38 + fwd[0] * 2.05,
            self.position[1] - 0.08,
            self.position[2] - right[2] * 0.38 + fwd[2] * 2.05,
        )

        speed = 78.0
        b1 = Bullet(body=Sphere(radius=0.06, stacks=4, slices=5, position=left_pos, color=(255, 230, 120)), velocity=(fwd[0] * speed, fwd[1] * speed, fwd[2] * speed), owner="player")
        b2 = Bullet(body=Sphere(radius=0.06, stacks=4, slices=5, position=right_pos, color=(255, 230, 120)), velocity=(fwd[0] * speed, fwd[1] * speed, fwd[2] * speed), owner="player")
        return [b1, b2]

    def drop_bomb(self) -> Bomb | None:
        if self.bomb_cooldown > 0 or self.bombs <= 0:
            return None
        self.bomb_cooldown = 0.65
        self.bombs -= 1
        pos = (self.position[0], self.position[1] - 0.25, self.position[2])
        vel = [math.sin(self.yaw) * self.speed, -0.8, math.cos(self.yaw) * self.speed]
        return Bomb(body=Sphere(radius=0.18, stacks=5, slices=7, position=pos, color=(38, 38, 42)), velocity=vel)


class AAGun:
    def __init__(self, pos: tuple[float, float, float]) -> None:
        self.position = pos
        self.hp = 120
        self.alive = True
        self.reload = random.uniform(0.7, 1.2)

        self.base = Cylinder(radius=0.52, height=0.38, segments=12, position=pos, color=(88, 92, 86))
        self.base.set_rotation(math.pi / 2, 0, 0)
        self.turret = Cylinder(radius=0.34, height=0.25, segments=10, position=(pos[0], pos[1] + 0.24, pos[2]), color=(105, 115, 102))
        self.turret.set_rotation(math.pi / 2, 0, 0)
        self.barrel = Cylinder(radius=0.08, height=1.1, segments=8, position=(pos[0], pos[1] + 0.36, pos[2]), color=(145, 145, 138))
        self.barrel.set_rotation(math.pi / 2, 0, 0)
        self.parts = [self.base, self.turret, self.barrel]

    def update(self, dt: float, plane_pos: tuple[float, float, float]) -> Bullet | None:
        if not self.alive:
            return None
        self.reload -= dt
        dx = plane_pos[0] - self.position[0]
        dz = plane_pos[2] - self.position[2]
        yaw = math.atan2(dx, dz)
        dist = math.sqrt(dx * dx + dz * dz)

        self.turret.set_rotation(math.pi / 2, yaw, 0)
        self.turret.position = (self.position[0], self.position[1] + 0.24, self.position[2])
        self.barrel.set_rotation(math.pi / 2, yaw, 0)
        self.barrel.position = (self.position[0], self.position[1] + 0.36, self.position[2])

        if self.reload > 0 or dist > 62:
            return None

        self.reload = random.uniform(0.45, 0.95)
        direction = normalize((dx, (plane_pos[1] - (self.position[1] + 0.5)) * 0.28, dz))
        speed = 33.0
        shot = Bullet(
            body=Sphere(radius=0.08, stacks=4, slices=6, position=(self.position[0], self.position[1] + 0.6, self.position[2]), color=(255, 120, 90)),
            velocity=(direction[0] * speed, direction[1] * speed, direction[2] * speed),
            owner="aa",
            life=3.8,
        )
        return shot

    def hit(self, damage: int) -> bool:
        if not self.alive:
            return False
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
            for p in self.parts:
                p.color = (46, 46, 46)
            return True
        return False


class BasePart:
    def __init__(self, shape: Cube, hp: int, score_value: int) -> None:
        self.shape = shape
        self.hp = hp
        self.max_hp = hp
        self.score_value = score_value
        self.destroyed = False

    def hit(self, damage: int) -> bool:
        if self.destroyed:
            return False
        self.hp -= damage
        if self.hp <= 0:
            self.destroyed = True
            self.shape.color = (40, 40, 40)
            self.shape.set_texture("flat", 0)
            return True
        return False


def create_forest_and_base(scene: Sahne) -> tuple[list[Cube], list[BasePart], list[AAGun]]:
    trees: list[Cube] = []
    base_parts: list[BasePart] = []

    ground = Cube(size=320, position=(0, -2.4, 40), color=(38, 86, 44))
    ground.scale = (1.0, 0.02, 1.0)
    ground.set_texture("noise", 0.12)
    scene.ekle(ground)

    random.seed(133)
    for _ in range(480):
        x = random.uniform(-145, 145)
        z = random.uniform(-115, 205)
        # üs çevresi, başlangıç hattı ve kamera koridorunu temiz bırak
        if 62 < z < 132 and -35 < x < 35:
            continue
        if -95 < z < -45 and -28 < x < 28:
            continue
        if -88 < z < -20 and -42 < x < 42:
            continue

        h = random.uniform(1.2, 2.5)
        trunk = Cube(size=random.uniform(0.55, 0.85), position=(x, -1.3, z), color=(92, 70, 45))
        trunk.scale = (0.40, h, 0.40)
        crown = Cube(size=random.uniform(1.5, 2.4), position=(x, -1.3 + 0.95 + h * 0.55, z), color=(48, random.randint(88, 130), 52))
        crown.scale = (1.0, random.uniform(0.82, 1.2), 1.0)
        trees.extend([trunk, crown])
        scene.ekle(trunk)
        scene.ekle(crown)

    # düşman üs yapıları
    bunker = Cube(size=13, position=(0, -1.1, 96), color=(100, 100, 95))
    bunker.scale = (1.5, 0.55, 1.0)
    bunker.set_texture("checker", 0.08)
    radar = Cube(size=6.5, position=(-16, -0.2, 110), color=(110, 115, 108))
    radar.scale = (1.0, 1.2, 1.0)
    radar.set_texture("stripe", 0.10)
    fuel = Cube(size=7.5, position=(17, -0.7, 104), color=(122, 108, 80))
    fuel.scale = (1.0, 0.65, 1.0)
    fuel.set_texture("checker", 0.12)

    for shape, hp, score_val in [(bunker, 300, 350), (radar, 220, 280), (fuel, 260, 320)]:
        scene.ekle(shape)
        base_parts.append(BasePart(shape, hp=hp, score_value=score_val))

    aa_positions = [(-24, -1.0, 82), (24, -1.0, 82), (-24, -1.0, 124), (24, -1.0, 124)]
    aa_guns: list[AAGun] = []
    for pos in aa_positions:
        aa = AAGun(pos)
        aa_guns.append(aa)
        for p in aa.parts:
            scene.ekle(p)

    return trees, base_parts, aa_guns


def run_game() -> None:
    renderer = Renderer(size=(1366, 768), caption="BF 109 - Orman Ussu Saldirisi", draw_grid=False, draw_axes=False, draw_edges=False)
    camera = Kamera(position=(0, 14, -90), fov=620, pitch=0.32)
    scene = Sahne(kamera=camera)

    _, base_parts, aa_guns = create_forest_and_base(scene)

    plane = BF109()
    for p in plane.parts:
        scene.ekle(p)

    bullets: list[Bullet] = []
    bombs: list[Bomb] = []

    pause = False
    score = 0
    mission_time = 0.0

    while True:
        dt = min(0.035, renderer.clock.tick(renderer.fps) / 1000.0)

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
            renderer.screen.fill((12, 14, 16))
            f = pygame.font.SysFont("consolas", 44)
            t = f.render("PAUSED", True, (220, 220, 220))
            renderer.screen.blit(t, (renderer.size[0] // 2 - t.get_width() // 2, renderer.size[1] // 2 - 20))
            pygame.display.flip()
            continue

        mission_time += dt
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            plane.yaw -= 1.65 * dt
        if keys[pygame.K_d]:
            plane.yaw += 1.65 * dt
        if keys[pygame.K_w]:
            plane.speed = min(26.0, plane.speed + 8.0 * dt)
        if keys[pygame.K_s]:
            plane.speed = max(8.5, plane.speed - 8.0 * dt)
        if keys[pygame.K_q]:
            plane.position[1] += 8.0 * dt
        if keys[pygame.K_e]:
            plane.position[1] -= 8.0 * dt

        if pygame.mouse.get_pressed()[0]:
            for b in plane.shoot_machineguns():
                bullets.append(b)
                scene.ekle(b.body)

        if keys[pygame.K_SPACE]:
            bomb = plane.drop_bomb()
            if bomb:
                bombs.append(bomb)
                scene.ekle(bomb.body)

        plane.update(dt)

        # Kamera uçağı sabit offsetten takip eder
        cam_back = 18.0
        cam_up = 6.2
        camera.position = (
            plane.position[0] - math.sin(plane.yaw) * cam_back,
            plane.position[1] + cam_up,
            plane.position[2] - math.cos(plane.yaw) * cam_back,
        )
        camera.yaw = plane.yaw
        camera.pitch = 0.30

        # AA ateşleri
        for aa in aa_guns:
            shot = aa.update(dt, tuple(plane.position))
            if shot:
                bullets.append(shot)
                scene.ekle(shot.body)

        # mermiler
        for i in range(len(bullets) - 1, -1, -1):
            b = bullets[i]
            b.update(dt)
            if not b.alive:
                if b.body in scene.sekiller:
                    scene.sekiller.remove(b.body)
                bullets.pop(i)
                continue

            pos = b.body.position
            if b.owner == "aa" and distance(pos, tuple(plane.position)) < 1.2:
                b.alive = False
                plane.hp = max(0, plane.hp - 8)

            if b.owner == "player":
                for aa in aa_guns:
                    if aa.alive and distance(pos, aa.position) < 1.2:
                        b.alive = False
                        if aa.hit(34):
                            score += 240
                        break
                if b.alive:
                    for part in base_parts:
                        if not part.destroyed and distance(pos, part.shape.position) < 4.8:
                            b.alive = False
                            if part.hit(20):
                                score += part.score_value
                            break

            if b.alive and (abs(pos[0]) > 180 or pos[1] < -3 or pos[1] > 60 or pos[2] < -140 or pos[2] > 250):
                b.alive = False

            if not b.alive:
                if b.body in scene.sekiller:
                    scene.sekiller.remove(b.body)
                bullets.pop(i)

        # bombalar
        for i in range(len(bombs) - 1, -1, -1):
            bomb = bombs[i]
            bomb.update(dt)
            if not bomb.alive:
                continue
            if bomb.body.position[1] <= -1.0:
                impact = bomb.body.position

                for aa in aa_guns:
                    if aa.alive:
                        d = distance(impact, aa.position)
                        if d <= 8.5 and aa.hit(int(170 * (1.0 - d / 8.5))):
                            score += 270

                for part in base_parts:
                    if not part.destroyed:
                        d = distance(impact, part.shape.position)
                        if d <= 12.0 and part.hit(int(240 * (1.0 - d / 12.0))):
                            score += part.score_value

                bomb.alive = False

            if not bomb.alive:
                if bomb.body in scene.sekiller:
                    scene.sekiller.remove(bomb.body)
                bombs.pop(i)

        alive_aa = sum(1 for a in aa_guns if a.alive)
        alive_base = sum(1 for p in base_parts if not p.destroyed)

        if plane.hp <= 0:
            break
        if alive_aa == 0 and alive_base == 0:
            score += max(0, 600 - int(mission_time * 8))
            break

        day = (math.sin(pygame.time.get_ticks() * 0.0001) + 1) * 0.5
        renderer.screen.fill((int(22 + 12 * day), int(36 + 20 * day), int(52 + 30 * day)))
        for shape in renderer._sorted_shapes(scene.sekiller, scene.kamera):
            renderer.draw_shape(shape, scene.kamera)

        f = pygame.font.SysFont("consolas", 22)
        hud = f.render(
            f"Can: {plane.hp}  Hiz: {plane.speed:0.1f}  Mermi: {plane.ammo}  Bomba: {plane.bombs}  AA: {alive_aa}/4  Uss: {alive_base}/3  Skor: {score}",
            True,
            (245, 245, 245),
        )
        renderer.screen.blit(hud, (14, 14))

        pygame.draw.rect(renderer.screen, (45, 45, 45), (14, 44, 250, 13))
        pygame.draw.rect(renderer.screen, (90, 220, 120), (14, 44, int(250 * plane.hp / 120), 13))
        pygame.draw.rect(renderer.screen, (220, 220, 220), (14, 44, 250, 13), 1)

        cx, cy = renderer.size[0] // 2, renderer.size[1] // 2
        pygame.draw.circle(renderer.screen, (255, 130, 110), (cx, cy), 9, 1)
        pygame.draw.line(renderer.screen, (255, 130, 110), (cx - 12, cy), (cx + 12, cy), 1)
        pygame.draw.line(renderer.screen, (255, 130, 110), (cx, cy - 12), (cx, cy + 12), 1)

        pygame.display.flip()

    renderer.screen.fill((10, 10, 15))
    big = pygame.font.SysFont("consolas", 50)
    if plane.hp <= 0:
        msg, color = "Gorev Basarisiz!", (255, 120, 120)
    else:
        msg, color = "Uss Yok Edildi!", (130, 255, 140)
    t = big.render(msg, True, color)
    renderer.screen.blit(t, (renderer.size[0] // 2 - t.get_width() // 2, renderer.size[1] // 2 - 40))

    f2 = pygame.font.SysFont("consolas", 30)
    st = f2.render(f"Skor: {score}", True, (240, 240, 240))
    renderer.screen.blit(st, (renderer.size[0] // 2 - st.get_width() // 2, renderer.size[1] // 2 + 22))
    pygame.display.flip()
    pygame.time.wait(2600)
    pygame.quit()


if __name__ == "__main__":
    run_game()
