"""Super3D 3D wireframe çizim kütüphanesi."""

from .kamera import Kamera
from .sahne import Sahne
from .sekiller import Capsule, Cone, Cube, Cylinder, Prism, Pyramid, Sekil3D, Sphere, Torus

__all__ = [
    "Kamera",
    "Renderer",
    "Sahne",
    "Sekil3D",
    "Cube",
    "Pyramid",
    "Sphere",
    "Cylinder",
    "Cone",
    "Torus",
    "Prism",
    "Capsule",
]


def __getattr__(name: str):
    if name == "Renderer":
        from .cizici import Renderer

        return Renderer
    raise AttributeError(name)
