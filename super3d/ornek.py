"""Super3D örnek kullanım dosyası.

Klavye:
- W/S/A/D: ileri-geri-sol-sağ
- Q/E: yukarı-aşağı
- Ok tuşları: kamerayı döndür
"""

from super3d import Kamera, Cone, Cube, Cylinder, Pyramid, Renderer, Sahne, Sphere, Torus


def main() -> None:
    kamera = Kamera(position=(0, 0, -12), fov=680)
    renderer = Renderer(size=(1280, 720), caption="Super3D - Gelismis Ornek", draw_grid=True)

    cube = Cube(size=2.2, position=(-5, 2.0, 14), color=(255, 120, 120), show_vertices=True)
    pyramid = Pyramid(base=2.4, height=2.8, position=(-2, -2.0, 13), color=(255, 200, 80))
    sphere = Sphere(radius=1.4, stacks=9, slices=14, position=(1.2, 2.0, 14), color=(120, 220, 255))
    cylinder = Cylinder(radius=1.1, height=2.8, segments=18, position=(4.2, -2.0, 14), color=(120, 255, 170))
    cone = Cone(radius=1.2, height=3.0, segments=18, position=(0, -0.2, 17), color=(210, 160, 255))
    torus = Torus(major_radius=1.5, minor_radius=0.45, position=(6.0, 1.5, 16), color=(255, 180, 80))

    cube.angular_velocity = (0.9, 1.1, 0.7)
    pyramid.angular_velocity = (0.7, 0.4, 1.2)
    sphere.angular_velocity = (0.4, 1.3, 0.6)
    cylinder.angular_velocity = (1.0, 0.8, 0.3)
    cone.angular_velocity = (0.6, 1.0, 0.9)
    torus.angular_velocity = (1.2, 0.5, 1.1)

    sahne = Sahne(kamera=kamera, sekiller=[cube, pyramid, sphere, cylinder, cone, torus])

    def on_update(dt: float) -> None:
        sphere.translate(dy=0.5 * dt)
        if sphere.position[1] > 2.8:
            sphere.position = (sphere.position[0], 1.2, sphere.position[2])

    sahne.on_update = on_update
    renderer.run_scene(sahne)


if __name__ == "__main__":
    main()
