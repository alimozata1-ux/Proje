"""Super3D GTA tarzı mini açık dünya oyunu.

Özellikler:
- Silahlar: tabanca + rifle, mermi/reload sistemi
- Arabalar: araca binme/inme, sürüş
- Binalar: şehir blokları
- NPC'ler: gezen siviller + saldırgan düşmanlar
- Akıllı telefon: görev/harita/kontaklar paneli

Kontroller:
- W/A/S/D: hareket
- Fare: kamera yaw/pitch
- Sol Tık: ateş
- R: reload
- 1/2: silah değiştir
- E: araca bin / araçtan in
- TAB: telefon aç/kapat
- P: pause
- ESC: çıkış
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from super3d import Kamera, Cube, Cylinder, Renderer, Sahne, Sphere


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    dz = a[2] - b[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def dir_from_yaw(yaw: float) -> tuple[float, float, float]:
    return (math.sin(yaw), 0.0, math.cos(yaw))


@dataclass
class Weapon:
    name: str
    damage: int
    fire_rate: float
    spread: float
    mag_size: int
    ammo: int
    reserve: int
    cooldown: float = 0.0
    reload_time: float = 1.2
    reloading: float = 0.0

    def update(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)
        if self.reloading > 0:
            self.reloading = max(0.0, self.reloading - dt)
            if self.reloading == 0:
                need = self.mag_size - self.ammo
                take = min(need, self.reserve)
                self.reserve -= take
                self.ammo += take

    def can_fire(self) -> bool:
        return self.cooldown <= 0 and self.reloading <= 0 and self.ammo > 0

    def fire(self) -> bool:
        if not self.can_fire():
            return False
        self.ammo -= 1
        self.cooldown = 1.0 / self.fire_rate
        return True

    def start_reload(self) -> None:
        if self.reloading > 0 or self.ammo >= self.mag_size or self.reserve <= 0:
            return
        self.reloading = self.reload_time


@dataclass
class Bullet:
    mesh: Sphere
    vel: tuple[float, float, float]
    life: float = 1.6
    owner: str = "player"
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.mesh.translate(dx=self.vel[0] * dt, dy=self.vel[1] * dt, dz=self.vel[2] * dt)


class Car:
    def __init__(self, pos: tuple[float, float, float], color: tuple[int, int, int]) -> None:
        self.position = [pos[0], pos[1], pos[2]]
        self.yaw = 0.0
        self.speed = 0.0
        self.driver: Player | None = None
        self.health = 180

        self.body = Cube(size=2.0, color=color)
        self.body.scale = (1.4, 0.35, 2.2)
        self.cabin = Cube(size=1.0, color=(120, 160, 210))
        self.cabin.scale = (1.0, 0.35, 1.0)
        self.wheels = [Cylinder(radius=0.22, height=0.24, segments=8, color=(30, 30, 30)) for _ in range(4)]
        self.parts = [self.body, self.cabin, *self.wheels]
        self.sync()

    def sync(self) -> None:
        x, y, z = self.position
        self.body.position = (x, y, z)
        self.body.set_rotation(0, self.yaw, 0)
        self.cabin.position = (x, y + 0.55, z - 0.15)
        self.cabin.set_rotation(0, self.yaw, 0)
        wheel_offsets = [(-1.05, -0.5, -1.2), (1.05, -0.5, -1.2), (-1.05, -0.5, 1.2), (1.05, -0.5, 1.2)]
        sy, cy = math.sin(self.yaw), math.cos(self.yaw)
        for wheel, (ox, oy, oz) in zip(self.wheels, wheel_offsets):
            rx = ox * cy + oz * sy
            rz = -ox * sy + oz * cy
            wheel.position = (x + rx, y + oy, z + rz)
            wheel.set_rotation(math.pi / 2, self.yaw, 0)

    def update(self, dt: float, throttle: float, steering: float) -> None:
        if self.driver is None:
            self.speed *= 0.94
        else:
            self.speed = clamp(self.speed + throttle * 16.0 * dt, -8.0, 22.0)
            self.yaw += steering * dt * (1.0 + abs(self.speed) * 0.05)
        self.position[0] += math.sin(self.yaw) * self.speed * dt
        self.position[2] += math.cos(self.yaw) * self.speed * dt
        self.position[0] = clamp(self.position[0], -95.0, 95.0)
        self.position[2] = clamp(self.position[2], -95.0, 95.0)
        self.sync()


class NPC:
    def __init__(self, pos: tuple[float, float, float], hostile: bool = False) -> None:
        self.position = [pos[0], pos[1], pos[2]]
        self.yaw = random.uniform(-math.pi, math.pi)
        self.hostile = hostile
        self.hp = 70 if hostile else 45
        self.alive = True
        self.move_timer = random.uniform(1.0, 3.0)
        self.attack_timer = random.uniform(0.2, 1.2)

        self.body = Cylinder(radius=0.25, height=1.2, segments=8, color=(180, 70, 70) if hostile else (80, 150, 210))
        self.head = Sphere(radius=0.22, stacks=5, slices=8, color=(230, 205, 170))
        self.parts = [self.body, self.head]
        self.sync()

    def sync(self) -> None:
        x, y, z = self.position
        self.body.position = (x, y, z)
        self.body.set_rotation(math.pi / 2, self.yaw, 0)
        self.head.position = (x, y + 0.9, z)

    def update(self, dt: float, player_pos: tuple[float, float, float]) -> tuple[float, float, float] | None:
        if not self.alive:
            return None
        self.move_timer -= dt

        if self.hostile:
            dx, dz = player_pos[0] - self.position[0], player_pos[2] - self.position[2]
            self.yaw = math.atan2(dx, dz)
            dist = math.sqrt(dx * dx + dz * dz)
            if dist > 7:
                self.position[0] += math.sin(self.yaw) * dt * 4.0
                self.position[2] += math.cos(self.yaw) * dt * 4.0
            self.attack_timer -= dt
            if dist < 36 and self.attack_timer <= 0:
                self.attack_timer = random.uniform(0.5, 1.1)
                return (self.position[0], self.position[1] + 0.7, self.position[2])
        else:
            if self.move_timer <= 0:
                self.move_timer = random.uniform(1.2, 3.4)
                self.yaw += random.uniform(-1.1, 1.1)
            self.position[0] += math.sin(self.yaw) * dt * 1.5
            self.position[2] += math.cos(self.yaw) * dt * 1.5

        self.position[0] = clamp(self.position[0], -96.0, 96.0)
        self.position[2] = clamp(self.position[2], -96.0, 96.0)
        self.sync()
        return None


class Player:
    def __init__(self) -> None:
        self.position = [0.0, -1.1, -2.0]
        self.yaw = 0.0
        self.health = 100
        self.in_car: Car | None = None
        self.money = 0
        self.wanted = 0
        self.weapon_index = 0

        self.weapons = [
            Weapon("Pistol", damage=18, fire_rate=4.0, spread=0.018, mag_size=12, ammo=12, reserve=72, reload_time=1.1),
            Weapon("Rifle", damage=27, fire_rate=9.0, spread=0.010, mag_size=28, ammo=28, reserve=140, reload_time=1.5),
        ]

    @property
    def current_weapon(self) -> Weapon:
        return self.weapons[self.weapon_index]

    def update_weapons(self, dt: float) -> None:
        for w in self.weapons:
            w.update(dt)


class SmartphoneUI:
    def __init__(self) -> None:
        self.open = False
        self.tab = 0
        self.tabs = ["Harita", "Gorev", "Kontak"]

    def handle_key(self, key: int) -> None:
        if key == pygame.K_TAB:
            self.open = not self.open
        if not self.open:
            return
        if key == pygame.K_q:
            self.tab = (self.tab - 1) % len(self.tabs)
        if key == pygame.K_e:
            self.tab = (self.tab + 1) % len(self.tabs)

    def draw(self, screen: pygame.Surface, player: Player, npcs: list[NPC]) -> None:
        if not self.open:
            return
        x, y, w, h = 1020, 70, 320, 620
        pygame.draw.rect(screen, (20, 20, 24), (x, y, w, h), border_radius=18)
        pygame.draw.rect(screen, (95, 95, 110), (x, y, w, h), 2, border_radius=18)

        font = pygame.font.SysFont("consolas", 24)
        title = font.render(f"Telefon - {self.tabs[self.tab]}", True, (235, 235, 235))
        screen.blit(title, (x + 20, y + 20))

        small = pygame.font.SysFont("consolas", 18)
        if self.tab == 0:
            pygame.draw.rect(screen, (32, 42, 52), (x + 18, y + 64, w - 36, h - 96), border_radius=10)
            px = x + 18 + int((player.position[0] + 100) / 200 * (w - 36))
            pz = y + 64 + int((player.position[2] + 100) / 200 * (h - 96))
            pygame.draw.circle(screen, (95, 220, 120), (px, pz), 5)
            for n in npcs[:40]:
                if n.alive and n.hostile:
                    nx = x + 18 + int((n.position[0] + 100) / 200 * (w - 36))
                    nz = y + 64 + int((n.position[2] + 100) / 200 * (h - 96))
                    pygame.draw.circle(screen, (230, 80, 80), (nx, nz), 3)
            hint = small.render("Kirmizi: dusman", True, (220, 220, 220))
            screen.blit(hint, (x + 24, y + h - 40))
        elif self.tab == 1:
            lines = [
                "Gorev: Sehirde hayatta kal",
                "- 10 dusmani etkisiz hale getir",
                "- Araba ile devriye gez",
                "- Paran 1000$ olsun",
                f"Durum: ${player.money} / $1000",
            ]
            for i, line in enumerate(lines):
                screen.blit(small.render(line, True, (230, 230, 230)), (x + 20, y + 76 + i * 30))
        else:
            lines = ["Mekaniker", "Silahci", "Doktor", "Taksi", "Arkadas"]
            for i, c in enumerate(lines):
                screen.blit(small.render(f"- {c}", True, (230, 230, 230)), (x + 22, y + 78 + i * 30))


def create_city(scene: Sahne) -> tuple[list[Cube], list[Car], list[NPC]]:
    buildings: list[Cube] = []
    cars: list[Car] = []
    npcs: list[NPC] = []

    random.seed(41)
    ground = Cube(size=260, position=(0, -2.35, 0), color=(55, 68, 58))
    ground.scale = (1.0, 0.02, 1.0)
    scene.ekle(ground)

    for x in range(-90, 91, 18):
        road = Cube(size=220, position=(x, -2.32, 0), color=(45, 45, 48))
        road.scale = (0.10, 0.005, 1.0)
        road.set_texture("stripe", 0.08)
        scene.ekle(road)

    for z in range(-90, 91, 18):
        road = Cube(size=220, position=(0, -2.32, z), color=(45, 45, 48))
        road.scale = (1.0, 0.005, 0.10)
        road.set_texture("stripe", 0.08)
        scene.ekle(road)

    for z in range(-84, 85, 14):
        for x in range(-84, 85, 14):
            if abs(x) % 18 < 4 or abs(z) % 18 < 4:
                continue
            h = random.uniform(1.5, 4.8)
            b = Cube(size=6.5, position=(x, -1.0, z), color=(80 + random.randint(0, 50), 80 + random.randint(0, 60), 90 + random.randint(0, 70)))
            b.scale = (1.0, h, 1.0)
            b.set_texture("checker", 0.10)
            buildings.append(b)
            scene.ekle(b)

    car_positions = [(-20, -1.1, -6), (18, -1.1, 14), (-42, -1.1, 28), (35, -1.1, -30)]
    for cp in car_positions:
        c = Car(cp, color=random.choice([(210, 80, 70), (70, 120, 220), (230, 210, 90), (95, 205, 120)]))
        cars.append(c)
        for p in c.parts:
            scene.ekle(p)

    for _ in range(24):
        npc = NPC((random.uniform(-80, 80), -1.1, random.uniform(-80, 80)), hostile=False)
        npcs.append(npc)
        for p in npc.parts:
            scene.ekle(p)

    for _ in range(10):
        npc = NPC((random.uniform(-80, 80), -1.1, random.uniform(-80, 80)), hostile=True)
        npcs.append(npc)
        for p in npc.parts:
            scene.ekle(p)

    return buildings, cars, npcs


def run_game() -> None:
    renderer = Renderer(size=(1366, 768), caption="Super3D GTA Tarzi Oyun", draw_grid=False, draw_axes=False, draw_edges=False)
    cam = Kamera(position=(0, 5.2, -12), fov=700, pitch=0.25)
    scene = Sahne(kamera=cam)

    _, cars, npcs = create_city(scene)
    phone = SmartphoneUI()
    player = Player()
    bullets: list[Bullet] = []

    pause = False
    score = 0

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    while True:
        dt = min(0.035, renderer.clock.tick(renderer.fps) / 1000.0)
        player.update_weapons(dt)

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
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_1:
                    player.weapon_index = 0
                if event.key == pygame.K_2:
                    player.weapon_index = 1
                if event.key == pygame.K_r:
                    player.current_weapon.start_reload()
                if event.key == pygame.K_e:
                    if player.in_car is None:
                        for car in cars:
                            if distance(tuple(player.position), tuple(car.position)) < 3.1 and car.driver is None:
                                player.in_car = car
                                car.driver = player
                                break
                    else:
                        player.position[0] = player.in_car.position[0] + 1.8
                        player.position[2] = player.in_car.position[2] + 1.8
                        player.in_car.driver = None
                        player.in_car = None
                phone.handle_key(event.key)

        if pause:
            renderer.screen.fill((10, 12, 16))
            f = pygame.font.SysFont("consolas", 50)
            t = f.render("PAUSED", True, (230, 230, 230))
            renderer.screen.blit(t, (renderer.size[0] // 2 - t.get_width() // 2, renderer.size[1] // 2 - 20))
            pygame.display.flip()
            continue

        if not phone.open:
            mdx, mdy = pygame.mouse.get_rel()
            player.yaw += mdx * 0.0028
            cam.pitch = clamp(cam.pitch - mdy * 0.0020, -0.65, 0.55)

        keys = pygame.key.get_pressed()

        if player.in_car is None:
            fwd = dir_from_yaw(player.yaw)
            right = (math.cos(player.yaw), 0, -math.sin(player.yaw))
            move_x = (fwd[0] * (float(keys[pygame.K_w]) - float(keys[pygame.K_s])) + right[0] * (float(keys[pygame.K_d]) - float(keys[pygame.K_a])))
            move_z = (fwd[2] * (float(keys[pygame.K_w]) - float(keys[pygame.K_s])) + right[2] * (float(keys[pygame.K_d]) - float(keys[pygame.K_a])))
            player.position[0] += move_x * 8.0 * dt
            player.position[2] += move_z * 8.0 * dt
            player.position[0] = clamp(player.position[0], -96.0, 96.0)
            player.position[2] = clamp(player.position[2], -96.0, 96.0)
        else:
            car = player.in_car
            throttle = float(keys[pygame.K_w]) - float(keys[pygame.K_s])
            steering = float(keys[pygame.K_d]) - float(keys[pygame.K_a])
            car.update(dt, throttle, steering)
            player.position[0], player.position[2] = car.position[0], car.position[2]
            player.yaw = car.yaw

        for car in cars:
            if car is not player.in_car:
                car.update(dt, 0.0, 0.0)

        if pygame.mouse.get_pressed()[0] and not phone.open:
            w = player.current_weapon
            if w.fire():
                dir_yaw = player.yaw + random.uniform(-w.spread, w.spread)
                d = dir_from_yaw(dir_yaw)
                b = Sphere(radius=0.07, stacks=4, slices=5, position=(player.position[0], -0.2, player.position[2]), color=(255, 220, 120))
                bullet = Bullet(mesh=b, vel=(d[0] * 62.0, 0.0, d[2] * 62.0), owner="player")
                bullets.append(bullet)
                scene.ekle(b)

        hostile_count = 0
        for npc in npcs:
            shot_origin = npc.update(dt, tuple(player.position))
            if npc.alive and npc.hostile:
                hostile_count += 1
            if shot_origin is not None:
                dx, dz = player.position[0] - shot_origin[0], player.position[2] - shot_origin[2]
                yaw = math.atan2(dx, dz)
                d = dir_from_yaw(yaw)
                b = Sphere(radius=0.06, stacks=4, slices=5, position=(shot_origin[0], shot_origin[1], shot_origin[2]), color=(255, 120, 120))
                bullets.append(Bullet(mesh=b, vel=(d[0] * 45.0, 0.0, d[2] * 45.0), owner="npc"))
                scene.ekle(b)

        for i in range(len(bullets) - 1, -1, -1):
            bullet = bullets[i]
            bullet.update(dt)
            if not bullet.alive:
                if bullet.mesh in scene.sekiller:
                    scene.sekiller.remove(bullet.mesh)
                bullets.pop(i)
                continue

            bp = bullet.mesh.position
            if bullet.owner == "npc" and distance(bp, tuple(player.position)) < 1.2:
                bullet.alive = False
                player.health = max(0, player.health - 8)
                player.wanted = min(5, player.wanted + 1)

            if bullet.owner == "player":
                for npc in npcs:
                    if npc.alive and distance(bp, tuple(npc.position)) < 1.0:
                        npc.hp -= player.current_weapon.damage
                        bullet.alive = False
                        if npc.hp <= 0:
                            npc.alive = False
                            for p in npc.parts:
                                p.color = (40, 40, 40)
                            gain = 120 if npc.hostile else 40
                            score += gain
                            player.money += gain
                        break

            if bullet.alive and (abs(bp[0]) > 110 or abs(bp[2]) > 110):
                bullet.alive = False

            if not bullet.alive:
                if bullet.mesh in scene.sekiller:
                    scene.sekiller.remove(bullet.mesh)
                bullets.pop(i)

        if player.health <= 0:
            break

        if player.in_car is None:
            cam.position = (
                player.position[0] - math.sin(player.yaw) * 7.5,
                4.8,
                player.position[2] - math.cos(player.yaw) * 7.5,
            )
        else:
            cam.position = (
                player.position[0] - math.sin(player.yaw) * 10.5,
                5.8,
                player.position[2] - math.cos(player.yaw) * 10.5,
            )
        cam.yaw = player.yaw

        daytime = (math.sin(pygame.time.get_ticks() * 0.00008) + 1) * 0.5
        renderer.screen.fill((int(20 + 38 * daytime), int(28 + 45 * daytime), int(38 + 70 * daytime)))
        for shape in renderer._sorted_shapes(scene.sekiller, scene.kamera):
            renderer.draw_shape(shape, scene.kamera)

        font = pygame.font.SysFont("consolas", 22)
        hud = font.render(
            f"Can: {player.health}  Silah: {player.current_weapon.name} [{player.current_weapon.ammo}/{player.current_weapon.reserve}]  Para: ${player.money}  Wanted: {'*' * player.wanted}  Dusman: {hostile_count}",
            True,
            (245, 245, 245),
        )
        renderer.screen.blit(hud, (14, 14))
        if player.in_car is not None:
            renderer.screen.blit(font.render("Arac: ICINDE (E ile in)", True, (170, 235, 170)), (14, 42))
        else:
            renderer.screen.blit(font.render("Arac: YAYA (E ile bin)", True, (220, 220, 220)), (14, 42))

        pygame.draw.rect(renderer.screen, (45, 45, 45), (14, 72, 260, 12))
        pygame.draw.rect(renderer.screen, (90, 220, 120), (14, 72, int(260 * player.health / 100), 12))
        pygame.draw.rect(renderer.screen, (220, 220, 220), (14, 72, 260, 12), 1)

        cx, cy = renderer.size[0] // 2, renderer.size[1] // 2
        pygame.draw.circle(renderer.screen, (255, 120, 120), (cx, cy), 7, 1)
        pygame.draw.line(renderer.screen, (255, 120, 120), (cx - 10, cy), (cx + 10, cy), 1)
        pygame.draw.line(renderer.screen, (255, 120, 120), (cx, cy - 10), (cx, cy + 10), 1)

        phone.draw(renderer.screen, player, npcs)
        pygame.display.flip()

    renderer.screen.fill((10, 10, 14))
    big = pygame.font.SysFont("consolas", 52)
    t = big.render("OYUN BITTI", True, (255, 120, 120))
    renderer.screen.blit(t, (renderer.size[0] // 2 - t.get_width() // 2, renderer.size[1] // 2 - 40))
    f2 = pygame.font.SysFont("consolas", 30)
    st = f2.render(f"Skor: {score}   Para: ${player.money}", True, (240, 240, 240))
    renderer.screen.blit(st, (renderer.size[0] // 2 - st.get_width() // 2, renderer.size[1] // 2 + 20))
    pygame.display.flip()
    pygame.time.wait(2600)

    pygame.event.set_grab(False)
    pygame.mouse.set_visible(True)
    pygame.quit()


if __name__ == "__main__":
    run_game()
