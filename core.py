"""Core window engine built on top of aerotkinter.AeroWindow."""

from __future__ import annotations

from typing import Callable, Optional

from aerotkinter import AeroLabel, AeroWindow

from animation import DEFAULT_ENGINE
from theme import ThemePalette, get_theme
from utils import blur_radius_for_scale, gradient_stops


class AeroAppWindow(AeroWindow):
    """Main application window with Aero glass setup and title header."""

    def __init__(self, title: str = "AeroTkinter App", theme_name: str = "light") -> None:
        super().__init__()
        self.theme: ThemePalette = get_theme(theme_name)
        self.animation_engine = DEFAULT_ENGINE
        self._header_label: Optional[AeroLabel] = None

        # Core window surface configuration.
        self.title(title)
        self.geometry("980x620")
        self.minsize(880, 560)
        self.attributes("-alpha", 0.0)

        self.configure(
            corner_radius=14,
            blur=blur_radius_for_scale(1.0),
            glass_tint=self.theme.background_start,
            background_gradient=gradient_stops(self.theme.background_start, self.theme.background_end, 16),
        )

        self._create_header(title)
        self.animation_engine.fade_in(self, duration_ms=420, steps=20)

    def _create_header(self, title: str) -> None:
        """Create a gradient title area for a Windows 7-like top bar."""

        self._header_label = AeroLabel(
            self,
            text=title,
            text_color=self.theme.text_primary,
            font=("Segoe UI", 14, "bold"),
            glow_color=self.theme.glow,
            background_gradient=gradient_stops(self.theme.background_start, self.theme.background_end, 18),
            corner_radius=0,
            padding=(22, 14),
            anchor="w",
        )
        self._header_label.pack(fill="x")

    def apply_theme(self, theme_name: str) -> None:
        """Switch all top-level visual colors to a selected theme."""

        self.theme = get_theme(theme_name)
        self.configure(
            glass_tint=self.theme.background_start,
            background_gradient=gradient_stops(self.theme.background_start, self.theme.background_end, 16),
        )
        if self._header_label:
            self._header_label.configure(
                text_color=self.theme.text_primary,
                glow_color=self.theme.glow,
                background_gradient=gradient_stops(self.theme.background_start, self.theme.background_end, 18),
            )

    def run(self, on_ready: Optional[Callable[[], None]] = None) -> None:
        """Start application loop with optional setup callback."""

        if on_ready:
            on_ready()
        self.mainloop()
