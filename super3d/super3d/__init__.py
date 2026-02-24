"""Super3D 3D wireframe çizim kütüphanesi."""

from .kamera import Kamera
from .sahne import Sahne
from .gui2d import Button, Circle2D, GuiManager, InputBox, Line2D, PixelShape, Rect2D, Slider, Toggle
from .sekiller import Capsule, Cone, Cube, Cylinder, Prism, Pyramid, Sekil3D, Sphere, Torus, alpha25, alpha50, alpha75

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
    "alpha25",
    "alpha50",
    "alpha75",
    "Rect2D",
    "Circle2D",
    "Line2D",
    "PixelShape",
    "Button",
    "InputBox",
    "GuiManager",
    "Slider",
    "Toggle",
]


def __getattr__(name: str):
    if name == "Renderer":
        from .cizici import Renderer

        return Renderer
    raise AttributeError(name)
