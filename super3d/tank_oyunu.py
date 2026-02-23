"""Super3D ile geliştirilmiş 3D tank oyunu.

Kontroller:
- W/S: ileri/geri
- A/D: gövdeyi döndür
- Fare: nişan al (kule fareyi takip eder)
- SPACE: ateş
- P: duraklat/devam
- ESC: çıkış
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from super3d import Kamera, Cube, Cylinder, Renderer, Sahne, Sphere


@dataclass
class Mermi:
    sekil: Sphere
    velocity: tuple[float, float, float]
    owner: str
    remaining_range: float
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        dx = self.velocity[0] * dt
        dy = self.velocity[1] * dt
        dz = self.velocity[2] * dt
        self.sekil.translate(dx=dx, dy=dy, dz=dz)
        self.remaining_range -= math.sqrt(dx * dx + dy * dy + dz * dz)
        if self.remaining_range <= 0:
            self.alive = False


@dataclass
class CanPoint:
    shape: Cylinder
    amount: int = 40
    cooldown: float = 10.0
    active: bool = True
    timer: float = 0.0

    def update(self, dt: float) -> None:
        if not self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = True

    def consume(self) -> None:
        self.active = False
        self.timer = self.cooldown


@dataclass
class HizBuff:
    shape: Cube
    duration: float = 8.0
    cooldown: float = 16.0
    active: bool = True
    timer: float = 0.0

    def update(self, dt: float) -> None:
        if not self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = True

    def consume(self) -> None:
        self.active = False
        self.timer = self.cooldown


class Tank:
    """M4 Sherman esintili basit tank modeli."""

    def __init__(self, name: str, position: tuple[float, float, float], color: tuple[int, int, int]) -> None:
        self.name = name
        self.position = list(position)
        self.yaw = 0.0
        self.turret_yaw = 0.0
        self.max_health = 180 if name == "player" else 110
        self.health = self.max_health

        self.reload_time = 0.55 if name == "player" else 1.8
        self.reload_timer = 0.0

        self.speed_multiplier = 1.0
        self.speed_buff_timer = 0.0

        self.hull_bottom = Cube(size=2.15, color=color)
        self.hull_top = Cube(size=1.65, color=tuple(min(255, c + 25) for c in color))
        self.track_left = Cube(size=1.0, color=(70, 70, 70))
        self.track_right = Cube(size=1.0, color=(70, 70, 70))

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

        turret_world_yaw = self.yaw + self.turret_yaw
        self.turret.position = (x, y + 1.05, z)
        self.turret.scale = (1.0, 0.7, 1.0)
        self.turret.set_rotation(math.pi / 2, turret_world_yaw, 0.0)

        fwd = (math.sin(turret_world_yaw), 0.0, math.cos(turret_world_yaw))
        self.gun_base.position = (x + fwd[0] * 0.7, y + 1.05, z + fwd[2] * 0.7)
        self.gun_base.scale = (0.6, 0.4, 0.6)
        self.gun_base.set_rotation(0.0, turret_world_yaw, 0.0)

        self.cannon.position = (x + fwd[0] * 1.2, y + 1.05, z + fwd[2] * 1.2)
        self.cannon.set_rotation(math.pi / 2, turret_world_yaw, 0.0)

    def move(self, amount: float, map_limit: tuple[float, float, float, float]) -> None:
        amount *= self.speed_multiplier
        self.position[0] += math.sin(self.yaw) * amount
        self.position[2] += math.cos(self.yaw) * amount
        min_x, max_x, min_z, max_z = map_limit
        self.position[0] = max(min_x, min(max_x, self.position[0]))
        self.position[2] = max(min_z, min(max_z, self.position[2]))
        self.sync_parts()

    def rotate(self, amount: float) -> None:
        self.yaw = clamp_angle(self.yaw + amount)
        self.sync_parts()

    def set_turret_world_yaw(self, world_yaw: float) -> None:
        self.turret_yaw = clamp_angle(world_yaw - self.yaw)
        self.sync_parts()

    def aim_turret_towards(self, world_yaw: float, dt: float, max_speed: float = 4.5) -> None:
        """Turetin bazen sıkışmasını önlemek için kısa açı yolundan yumuşak döndürür."""
        current_world = self.yaw + self.turret_yaw
        diff = clamp_angle(world_yaw - current_world)
        step = max(-max_speed * dt, min(max_speed * dt, diff))
        self.turret_yaw = clamp_angle(self.turret_yaw + step)
        self.sync_parts()

    def activate_speed_buff(self, duration: float) -> None:
        self.speed_multiplier = 1.45
        self.speed_buff_timer = max(self.speed_buff_timer, duration)

    def update(self, dt: float) -> None:
        self.reload_timer = max(0.0, self.reload_timer - dt)
        if self.speed_buff_timer > 0:
            self.speed_buff_timer -= dt
            if self.speed_buff_timer <= 0:
                self.speed_multiplier = 1.0

    def shoot(self) -> Mermi | None:
        if self.reload_timer > 0:
            return None

        world_yaw = self.yaw + self.turret_yaw
        direction = (math.sin(world_yaw), 0.0, math.cos(world_yaw))
        spawn = (
            self.position[0] + direction[0] * 2.25,
            self.position[1] + 1.05,
            self.position[2] + direction[2] * 2.25,
        )
        bullet = Sphere(radius=0.14, stacks=5, slices=8, position=spawn, color=(255, 225, 90))
        if self.name == "player":
            speed, weapon_range = 17.0, 42.0
        else:
            speed, weapon_range = 9.0, 28.0

        self.reload_timer = self.reload_time
        return Mermi(
            sekil=bullet,
            velocity=(direction[0] * speed, 0.0, direction[2] * speed),
            owner=self.name,
            remaining_range=weapon_range,
        )


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
    mx, my = mouse_pos
    w, h = screen_size
    nx = (mx - w / 2) / kamera.fov
    ny = -(my - h / 2) / kamera.fov
    dir_cam = (nx, ny, 1.0)

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


def create_forest_map(sahne: Sahne) -> tuple[list[Cube], list[Cylinder], list[CanPoint], list[HizBuff]]:
    rocks: list[Cube] = []
    trees: list[Cylinder] = []
    heal_points: list[CanPoint] = []
    speed_points: list[HizBuff] = []

    random.seed(22)

    for z in range(10, 110, 5):
        for x in range(-34, 35, 5):
            if random.random() < 0.26:
                b = Cube(size=random.uniform(1.2, 2.4), position=(x, -1.05, z), color=(105, 96, 85))
                b.scale = (1.0, random.uniform(0.45, 1.0), 1.0)
                rocks.append(b)

    for z in range(8, 112, 4):
        for x in range(-36, 37, 4):
            if random.random() < 0.18:
                trunk = Cylinder(radius=0.22, height=random.uniform(1.4, 2.0), segments=10, position=(x, -0.4, z), color=(92, 62, 38))
                trunk.set_rotation(math.pi / 2, 0.0, 0.0)
                trees.append(trunk)

    rocks = [r for r in rocks if distance_xz(r.position, (0.0, -1.2, 8.0)) > 8.0]
    trees = [t for t in trees if distance_xz(t.position, (0.0, -1.2, 8.0)) > 8.0]

    for pos in [(-12.0, -1.1, 28.0), (14.0, -1.1, 52.0), (-6.0, -1.1, 84.0)]:
        p = Cylinder(radius=0.6, height=0.3, segments=16, position=pos, color=(70, 220, 120))
        p.set_rotation(math.pi / 2, 0.0, 0.0)
        heal_points.append(CanPoint(shape=p, amount=45, cooldown=12.0))

    for pos in [(18.0, -1.1, 36.0), (-18.0, -1.1, 68.0)]:
        sp = Cube(size=0.9, position=pos, color=(90, 170, 255))
        sp.scale = (1.0, 0.25, 1.0)
        speed_points.append(HizBuff(shape=sp, duration=8.0, cooldown=18.0))

    for r in rocks:
        sahne.ekle(r)
    for t in trees:
        sahne.ekle(t)
    for h in heal_points:
        sahne.ekle(h.shape)
    for s in speed_points:
        sahne.ekle(s.shape)

    return rocks, trees, heal_points, speed_points


def draw_health_bar(screen, x: int, y: int, w: int, h: int, health: int, max_health: int, color: tuple[int, int, int]) -> None:
    pygame.draw.rect(screen, (45, 45, 45), (x, y, w, h))
    ratio = 0.0 if max_health <= 0 else max(0.0, min(1.0, health / max_health))
    pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
    pygame.draw.rect(screen, (210, 210, 210), (x, y, w, h), 1)


def draw_minimap(screen, map_limit, player_pos, enemy_pos, heal_points, speed_points) -> None:
    x0, y0, w, h = 1080, 20, 260, 160
    pygame.draw.rect(screen, (30, 30, 36), (x0, y0, w, h))
    pygame.draw.rect(screen, (180, 180, 180), (x0, y0, w, h), 1)
    min_x, max_x, min_z, max_z = map_limit

    def to_map(x, z):
        mx = x0 + int((x - min_x) / (max_x - min_x) * w)
        my = y0 + int((z - min_z) / (max_z - min_z) * h)
        return mx, my

    for hp in heal_points:
        if hp.active:
            pygame.draw.circle(screen, (70, 220, 120), to_map(hp.shape.position[0], hp.shape.position[2]), 3)
    for sp in speed_points:
        if sp.active:
            pygame.draw.circle(screen, (90, 170, 255), to_map(sp.shape.position[0], sp.shape.position[2]), 3)

    pygame.draw.circle(screen, (100, 230, 120), to_map(player_pos[0], player_pos[2]), 4)
    pygame.draw.circle(screen, (230, 100, 100), to_map(enemy_pos[0], enemy_pos[2]), 4)


def run_game() -> None:
    renderer = Renderer(
        size=(1366, 768),
        caption="Super3D Tank Oyunu - Orman Map",
        draw_grid=False,
        draw_axes=False,
        draw_edges=False,
    )
    kamera = Kamera(position=(0, 12.5, -10), fov=640, pitch=0.64)
    sahne = Sahne(kamera=kamera)

    map_limit = (-38.0, 38.0, 2.0, 114.0)

    player = Tank("player", position=(0.0, -1.2, 8.0), color=(105, 145, 95))
    enemy = Tank("enemy", position=(0.0, -1.2, 92.0), color=(130, 130, 120))
    enemy.yaw = math.pi
    enemy.sync_parts()

    rocks, trees, heal_points, speed_points = create_forest_map(sahne)
    for p in player.parts + enemy.parts:
        sahne.ekle(p)

    mermiler: list[Mermi] = []
    pause = False
    game_time = 0.0
    score = 0

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
            renderer.screen.fill((12, 18, 14))
            font = pygame.font.SysFont("consolas", 44)
            txt = font.render("PAUSED", True, (220, 220, 220))
            renderer.screen.blit(txt, (renderer.size[0] // 2 - txt.get_width() // 2, renderer.size[1] // 2 - 20))
            pygame.display.flip()
            continue

        if not player.alive or not enemy.alive:
            break

        game_time += dt
        player.update(dt)
        enemy.update(dt)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player.rotate(-1.6 * dt)
        if keys[pygame.K_d]:
            player.rotate(1.6 * dt)
        if keys[pygame.K_w]:
            player.move(7.0 * dt, map_limit)
        if keys[pygame.K_s]:
            player.move(-5.2 * dt, map_limit)

        world_yaw = mouse_to_world_yaw(sahne.kamera, pygame.mouse.get_pos(), renderer.size, player.position[1])
        player.aim_turret_towards(world_yaw, dt, max_speed=7.0)

        if keys[pygame.K_SPACE]:
            bullet = player.shoot()
            if bullet:
                mermiler.append(bullet)
                sahne.ekle(bullet.sekil)

        to_player = distance_xz(tuple(player.position), tuple(enemy.position))
        desired = math.atan2(player.position[0] - enemy.position[0], player.position[2] - enemy.position[2])
        enemy.rotate(clamp_angle(desired - enemy.yaw) * min(1.0, dt * 0.75))
        if to_player > 16:
            enemy.move(2.2 * dt, map_limit)

        enemy.aim_turret_towards(desired + random.uniform(-0.09, 0.09), dt, max_speed=3.0)
        if random.random() > 0.4 and to_player < 55:
            bullet = enemy.shoot()
            if bullet:
                mermiler.append(bullet)
                sahne.ekle(bullet.sekil)

        for hp in heal_points:
            hp.update(dt)
            if hp.active:
                hp.shape.color = (70, 220, 120)
                if distance_xz(tuple(player.position), hp.shape.position) < 1.8:
                    player.health = min(player.max_health, player.health + hp.amount)
                    hp.consume()
                    score += 20
                elif distance_xz(tuple(enemy.position), hp.shape.position) < 1.8:
                    enemy.health = min(enemy.max_health, enemy.health + hp.amount // 2)
                    hp.consume()
            else:
                hp.shape.color = (50, 70, 55)

        for sp in speed_points:
            sp.update(dt)
            if sp.active:
                sp.shape.color = (90, 170, 255)
                if distance_xz(tuple(player.position), sp.shape.position) < 1.8:
                    player.activate_speed_buff(sp.duration)
                    sp.consume()
                    score += 35
                elif distance_xz(tuple(enemy.position), sp.shape.position) < 1.8:
                    enemy.activate_speed_buff(sp.duration * 0.7)
                    sp.consume()
            else:
                sp.shape.color = (40, 70, 90)

        cam_target = (player.position[0], player.position[2] - 7.0)
        kamera.position = (
            kamera.position[0] + (cam_target[0] - kamera.position[0]) * min(1.0, 4.2 * dt),
            kamera.position[1],
            kamera.position[2] + (cam_target[1] - kamera.position[2]) * min(1.0, 4.2 * dt),
        )

        for m in mermiler:
            if not m.alive:
                continue
            m.update(dt)
            x, _, z = m.sekil.position
            if x < map_limit[0] - 4 or x > map_limit[1] + 4 or z < 0 or z > map_limit[3] + 4:
                m.alive = False
                continue

            for obs in rocks:
                if distance_xz(m.sekil.position, obs.position) < 1.15:
                    m.alive = False
                    break
            if not m.alive:
                continue

            for tree in trees:
                if distance_xz(m.sekil.position, tree.position) < 0.7:
                    m.alive = False
                    break
            if not m.alive:
                continue

            if m.owner != "player" and distance_xz(m.sekil.position, tuple(player.position)) < 1.5:
                player.health = max(0, player.health - 11)
                m.alive = False
            if m.owner != "enemy" and distance_xz(m.sekil.position, tuple(enemy.position)) < 1.45:
                enemy.health = max(0, enemy.health - 26)
                m.alive = False
                score += 10

        for m in [x for x in mermiler if not x.alive]:
            if m.sekil in sahne.sekiller:
                sahne.sekiller.remove(m.sekil)
        mermiler = [x for x in mermiler if x.alive]

        day_t = (math.sin(game_time * 0.15) + 1) * 0.5
        bg = (int(20 + 18 * day_t), int(36 + 34 * day_t), int(24 + 20 * day_t))
        renderer.screen.fill(bg)

        for shape in renderer._sorted_shapes(sahne.sekiller, sahne.kamera):
            renderer.draw_shape(shape, sahne.kamera)

        font = pygame.font.SysFont("consolas", 22)
        hud = font.render(
            f"Reload: {player.reload_timer:0.2f}s  Score: {score}  SpeedBuff: {max(0, player.speed_buff_timer):0.1f}s",
            True,
            (240, 240, 240),
        )
        renderer.screen.blit(hud, (14, 14))

        draw_health_bar(renderer.screen, 14, 46, 300, 18, player.health, player.max_health, (78, 220, 98))
        draw_health_bar(renderer.screen, 14, 70, 300, 18, enemy.health, enemy.max_health, (220, 90, 90))
        draw_minimap(renderer.screen, map_limit, tuple(player.position), tuple(enemy.position), heal_points, speed_points)

        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(renderer.screen, (255, 90, 90), (mx, my), 7, 1)
        pygame.draw.line(renderer.screen, (255, 90, 90), (mx - 9, my), (mx + 9, my), 1)
        pygame.draw.line(renderer.screen, (255, 90, 90), (mx, my - 9), (mx, my + 9), 1)
        pygame.display.flip()

    renderer.screen.fill((8, 8, 14))
    font_big = pygame.font.SysFont("consolas", 56)
    if player.health > enemy.health:
        msg, color = "Kazandiniz!", (125, 255, 125)
        score += 150
    elif player.health < enemy.health:
        msg, color = "Kaybettiniz!", (255, 120, 120)
    else:
        msg, color = "Berabere!", (255, 220, 120)

    text = font_big.render(msg, True, color)
    renderer.screen.blit(text, (renderer.size[0] // 2 - text.get_width() // 2, renderer.size[1] // 2 - 35))
    font2 = pygame.font.SysFont("consolas", 30)
    stext = font2.render(f"Skor: {score}", True, (240, 240, 240))
    renderer.screen.blit(stext, (renderer.size[0] // 2 - stext.get_width() // 2, renderer.size[1] // 2 + 35))
    pygame.display.flip()
    pygame.time.wait(2200)
    pygame.quit()


if __name__ == "__main__":
    run_game()
