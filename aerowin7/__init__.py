"""AeroWin7: Modular Aero-themed GUI toolkit built on top of aerotkinter."""

from .animation import AnimationEngine, DEFAULT_ENGINE, attach_click_animation, attach_hover_animation, fade_in
from .core import AeroAppWindow
from .theme import DARK_THEME, LIGHT_THEME, THEMES, ThemePalette, get_theme

__all__ = [
    "AeroAppWindow",
    "AnimationEngine",
    "DEFAULT_ENGINE",
    "attach_click_animation",
    "attach_hover_animation",
    "fade_in",
    "ThemePalette",
    "LIGHT_THEME",
    "DARK_THEME",
    "THEMES",
    "get_theme",
]
