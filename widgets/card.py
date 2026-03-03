"""Aero styled card/panel wrapper."""

from __future__ import annotations

from aerotkinter import AeroCard

from animation import attach_hover_animation
from theme import ThemePalette


class GlassCard(AeroCard):
    """Semi-transparent card with subtle shadow and glow transition."""

    def __init__(self, master, theme: ThemePalette) -> None:
        super().__init__(
            master,
            corner_radius=14,
            background_color=theme.card_color,
            border_color=theme.card_border,
            shadow_color=theme.shadow,
            glow_color=theme.glow,
            padding=16,
        )

        def set_border(color: str) -> None:
            self.configure(border_color=color)

        attach_hover_animation(self, theme.card_border[:7], theme.glow, set_border)
