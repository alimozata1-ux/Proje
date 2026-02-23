"""Super3D ile basit araba oyunu (sonsuz yol + engellerden kaçınma)."""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from super3d import Kamera, Cone, Cube, Cylinder, Renderer, Sahne


@dataclass
class Obstacle:
    mesh: Cube
    speed: float
    alive: bool = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return
        x, y, z = self.mesh.position
        self.mesh.position = (x, y, z - self.speed * dt)


class Car:
    def __init__(self) -> None:
        self.x = 0.0
        self.z = 0.0
        self.speed = 14.0
        self.health = 100

        self.body = Cube(size=1.8, color=(210, 70, 70))
        self.body.scale = (1.2, 0.35, 2.0)

        self.cabin = Cube(size=1.0, color=(150, 180, 210))
        self.cabin.scale = (0.85, 0.35, 0.9)

        self.wheels = [
            Cylinder(radius=0.25, height=0.26, segments=10, color=(35, 35, 35)),
            Cylinder(radius=0.25, height=0.26, segments=10, color=(35, 35, 35)),
            Cylinder(radius=0.25, height=0.26, segments=10, color=(35, 35, 35)),
            Cylinder(radius=0.25, height=0.26, segments=10, color=(35, 35, 35)),
        ]

        self.nose = Cone(radius=0.2, height=0.45, segments=10, color=(240, 180, 80))
        self.parts = [self.body, self.cabin, *self.wheels, self.nose]
        self.sync()

    def sync(self) -> None:
        self.body.position = (self.x, -1.25, self.z)
        self.cabin.position = (self.x, -0.82, self.z - 0.1)
        wheel_pos = [(-0.85, -1.55, -1.15), (0.85, -1.55, -1.15), (-0.85, -1.55, 1.15), (0.85, -1.55, 1.15)]
        for w, (dx, dy, dz) in zip(self.wheels, wheel_pos):
            w.position = (self.x + dx, dy, self.z + dz)
            w.set_rotation(1.57, 0, 0)
        self.nose.position = (self.x, -1.20, self.z + 1.45)
        self.nose.set_rotation(0, 0, 1.57)


def spawn_obstacle() -> Obstacle:
    lane_x = random.choice([-3.2, -1.1, 1.1, 3.2])
    z = random.uniform(28, 45)
    mesh = Cube(size=random.uniform(1.3, 2.2), position=(lane_x, -1.2, z), color=random.choice([(80, 180, 90), (180, 80, 80), (80, 100, 190)]))
    mesh.scale = (1.0, random.uniform(0.7, 1.3), 1.0)
    mesh.set_texture("checker", 0.12)
    return Obstacle(mesh=mesh, speed=random.uniform(13.0, 17.0))


def run_game() -> None:
    renderer = Renderer(size=(1366, 768), caption="Super3D Araba Oyunu", draw_grid=False, draw_axes=False)
    camera = Kamera(position=(0, 4.2, -10), fov=620, pitch=0.22)
    scene = Sahne(kamera=camera)

    road = Cube(size=140, position=(0, -2.4, 60), color=(45, 45, 50))
    road.scale = (0.12, 0.01, 1.0)
    road.set_texture("stripe", 0.09)
    scene.ekle(road)

    # yol kenar çizgileri
    for x in (-4.6, 4.6):
        edge = Cube(size=140, position=(x, -2.37, 60), color=(230, 230, 120))
        edge.scale = (0.005, 0.01, 1.0)
        scene.ekle(edge)

    car = Car()
    for p in car.parts:
        scene.ekle(p)

    obstacles: list[Obstacle] = []
    spawn_timer = 0.2
    score = 0

    while True:
        dt = renderer.clock.tick(renderer.fps) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        move = 7.0 * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            car.x -= move
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            car.x += move
        car.x = max(-3.8, min(3.8, car.x))
        car.sync()

        # kamera arabanın arkasından sabit offset
        camera.position = (car.x * 0.7, 4.2, -10)

        spawn_timer -= dt
        if spawn_timer <= 0:
            spawn_timer = random.uniform(0.35, 0.8)
            obs = spawn_obstacle()
            obstacles.append(obs)
            scene.ekle(obs.mesh)

        for obs in obstacles:
            if not obs.alive:
                continue
            obs.update(dt)
            if obs.mesh.position[2] < -8:
                obs.alive = False
                score += 5
                continue

            # çarpışma
            dx = abs(obs.mesh.position[0] - car.x)
            dz = abs(obs.mesh.position[2] - car.z)
            if dx < 1.5 and dz < 2.0:
                obs.alive = False
                car.health = max(0, car.health - 20)

        for obs in [o for o in obstacles if not o.alive]:
            if obs.mesh in scene.sekiller:
                scene.sekiller.remove(obs.mesh)
        obstacles = [o for o in obstacles if o.alive]

        if car.health <= 0:
            break

        renderer.screen.fill((18, 26, 38))
        for shape in renderer._sorted_shapes(scene.sekiller, scene.kamera):
            renderer.draw_shape(shape, scene.kamera)

        f = pygame.font.SysFont("consolas", 24)
        txt = f.render(f"Can: {car.health}   Skor: {score}   A/D veya <-/-> ile kac", True, (245, 245, 245))
        renderer.screen.blit(txt, (16, 14))
        pygame.draw.rect(renderer.screen, (45, 45, 45), (16, 44, 240, 12))
        pygame.draw.rect(renderer.screen, (90, 220, 120), (16, 44, int(240 * car.health / 100), 12))
        pygame.draw.rect(renderer.screen, (220, 220, 220), (16, 44, 240, 12), 1)

        pygame.display.flip()

    renderer.screen.fill((10, 10, 14))
    big = pygame.font.SysFont("consolas", 52)
    t = big.render("Araba Pert Oldu!", True, (255, 120, 120))
    renderer.screen.blit(t, (renderer.size[0] // 2 - t.get_width() // 2, renderer.size[1] // 2 - 40))
    f2 = pygame.font.SysFont("consolas", 30)
    st = f2.render(f"Skor: {score}", True, (240, 240, 240))
    renderer.screen.blit(st, (renderer.size[0] // 2 - st.get_width() // 2, renderer.size[1] // 2 + 22))
    pygame.display.flip()
    pygame.time.wait(2200)
    pygame.quit()


if __name__ == "__main__":
    run_game()
