"""Aero styled button wrapper."""

from __future__ import annotations

from typing import Callable, Optional

from aerotkinter import AeroButton

from animation import DEFAULT_ENGINE, attach_click_animation, attach_hover_animation
from theme import ThemePalette


class GlassButton(AeroButton):
    """Rounded Aero button with glow and click pulse animation."""

    def __init__(
        self,
        master,
        text: str,
        theme: ThemePalette,
        command: Optional[Callable[[], None]] = None,
        primary: bool = True,
    ) -> None:
        base = theme.accent if primary else theme.secondary
        hover = theme.accent_hover if primary else theme.secondary_hover
        super().__init__(
            master,
            text=text,
            command=command,
            corner_radius=12,
            gradient_overlay=True,
            glow_color=theme.glow,
            background_color=base,
            text_color=theme.text_primary if theme.name == "light" else "#f8fcff",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 10),
        )

        # GUI animasyon motoru ile hover/click efektlerini yönetiyoruz.
        def set_bg(color: str) -> None:
            self.configure(background_color=color)

        attach_hover_animation(DEFAULT_ENGINE, self, base, hover, set_bg, name="button_hover")
        attach_click_animation(DEFAULT_ENGINE, self, theme.glow, base, set_bg, name="button_click")
