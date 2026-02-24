"""Super3D GPU / performans test uygulaması.

Kontroller:
- '+': yeni şekil dalgası ekle
- '-': şekil azalt
- R: sıfırla
- ESC: çıkış
"""

from __future__ import annotations

import random

import pygame

from super3d import Kamera, Cone, Cube, Cylinder, Renderer, Sahne, Sphere, Torus


def random_shape() -> object:
    color = (random.randint(70, 255), random.randint(70, 255), random.randint(70, 255))
    px = random.uniform(-24, 24)
    py = random.uniform(-3, 7)
    pz = random.uniform(8, 70)
    choice = random.choice(["cube", "sphere", "cylinder", "cone", "torus"])

    if choice == "cube":
        s = Cube(size=random.uniform(0.8, 2.0), position=(px, py, pz), color=color)
    elif choice == "sphere":
        s = Sphere(radius=random.uniform(0.5, 1.2), stacks=7, slices=10, position=(px, py, pz), color=color)
    elif choice == "cylinder":
        s = Cylinder(radius=random.uniform(0.5, 1.0), height=random.uniform(1.0, 2.4), segments=12, position=(px, py, pz), color=color)
    elif choice == "cone":
        s = Cone(radius=random.uniform(0.5, 1.0), height=random.uniform(1.0, 2.4), segments=12, position=(px, py, pz), color=color)
    else:
        s = Torus(
            major_radius=random.uniform(0.9, 1.6),
            minor_radius=random.uniform(0.25, 0.55),
            major_segments=12,
            minor_segments=9,
            position=(px, py, pz),
            color=color,
        )

    s.angular_velocity = (
        random.uniform(-0.9, 0.9),
        random.uniform(-1.2, 1.2),
        random.uniform(-0.9, 0.9),
    )
    return s


def add_wave(scene: Sahne, count: int) -> None:
    for _ in range(count):
        scene.ekle(random_shape())


def run_gpu_test() -> None:
    renderer = Renderer(size=(1366, 768), caption="Super3D GPU Test (+ ile şekil ekle)", draw_grid=True, draw_axes=False)
    kamera = Kamera(position=(0, 3, -10), fov=620)
    scene = Sahne(kamera=kamera)

    add_wave(scene, 120)

    running = True
    while running:
        dt = renderer.clock.tick(renderer.fps) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    add_wave(scene, 50)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    del_count = min(40, len(scene.sekiller))
                    if del_count > 0:
                        scene.sekiller = scene.sekiller[:-del_count]
                elif event.key == pygame.K_r:
                    scene.sekiller.clear()
                    add_wave(scene, 120)

        keys = pygame.key.get_pressed()
        move = 10.0 * dt
        rot = 1.4 * dt
        if keys[pygame.K_w]:
            kamera.move(dz=move)
        if keys[pygame.K_s]:
            kamera.move(dz=-move)
        if keys[pygame.K_a]:
            kamera.move(dx=-move)
        if keys[pygame.K_d]:
            kamera.move(dx=move)
        if keys[pygame.K_q]:
            kamera.move(dy=move)
        if keys[pygame.K_e]:
            kamera.move(dy=-move)
        if keys[pygame.K_LEFT]:
            kamera.rotate(dyaw=-rot)
        if keys[pygame.K_RIGHT]:
            kamera.rotate(dyaw=rot)

        scene.update(dt)

        renderer.screen.fill(renderer.bg_color)
        renderer.draw_reference(scene.kamera)
        for shape in renderer._sorted_shapes(scene.sekiller, scene.kamera):
            renderer.draw_shape(shape, scene.kamera)

        fps = renderer.clock.get_fps()
        font = pygame.font.SysFont("consolas", 22)
        hud = font.render(
            f"Sekil: {len(scene.sekiller)} | FPS: {fps:5.1f} | '+' ekle, '-' azalt, R reset",
            True,
            (245, 245, 245),
        )
        renderer.screen.blit(hud, (15, 15))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_gpu_test()
