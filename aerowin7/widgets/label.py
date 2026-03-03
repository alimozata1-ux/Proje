"""Aero styled label wrapper."""

from __future__ import annotations

from aerotkinter import AeroLabel

from ..animation import DEFAULT_ENGINE, attach_hover_animation
from ..theme import ThemePalette


class GlassLabel(AeroLabel):
    """Text label using theme colors and soft hover glow."""

    def __init__(self, master, text: str, theme: ThemePalette, large: bool = False) -> None:
        super().__init__(
            master,
            text=text,
            text_color=theme.text_primary,
            glow_color=theme.glow,
            font=("Segoe UI", 14 if large else 10, "bold" if large else "normal"),
            background_color="transparent",
        )

        def set_glow(color: str) -> None:
            self.configure(glow_color=color)

        attach_hover_animation(DEFAULT_ENGINE, self, theme.card_border[:7], theme.glow, set_glow, name="label_hover")
