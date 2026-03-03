"""Aero styled entry wrapper."""

from __future__ import annotations

from aerotkinter import AeroEntry

from ..animation import DEFAULT_ENGINE, attach_hover_animation
from ..theme import ThemePalette


class GlassEntry(AeroEntry):
    """Glass input with placeholder text and hover glow."""

    def __init__(self, master, theme: ThemePalette, placeholder: str = "Type here...") -> None:
        super().__init__(
            master,
            placeholder=placeholder,
            corner_radius=10,
            blur=12,
            background_color=theme.entry_background,
            text_color=theme.entry_text,
            placeholder_color=theme.text_muted,
            border_color=theme.card_border,
            glow_color=theme.glow,
            font=("Segoe UI", 10),
            padding=(10, 8),
        )

        def set_border(color: str) -> None:
            self.configure(border_color=color)

        attach_hover_animation(DEFAULT_ENGINE, self, theme.card_border[:7], theme.glow, set_border, name="entry_hover")
