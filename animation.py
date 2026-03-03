"""Reusable animation helpers (hover/click/fade) for Aero widgets."""

from __future__ import annotations

from typing import Callable, Optional


def _safe_after(widget, delay_ms: int, callback: Callable[[], None]) -> None:
    """Tk-like safe after wrapper used by all animations."""

    try:
        widget.after(delay_ms, callback)
    except Exception:
        # Keeps demos robust if a widget has been destroyed mid-animation.
        pass


def fade_in(widget, duration_ms: int = 300, steps: int = 12) -> None:
    """Fade a window/widget in by adjusting alpha smoothly."""

    steps = max(2, steps)
    interval = max(10, duration_ms // steps)

    def step(index: int = 0) -> None:
        alpha = index / (steps - 1)
        if hasattr(widget, "attributes"):
            try:
                widget.attributes("-alpha", alpha)
            except Exception:
                return
        if index + 1 < steps:
            _safe_after(widget, interval, lambda: step(index + 1))

    step(0)


def animate_color(widget, start: str, end: str, setter: Callable[[str], None], duration_ms: int = 160, steps: int = 8) -> None:
    """Transition between two colors over time."""

    from utils import blend_colors

    steps = max(2, steps)
    interval = max(10, duration_ms // steps)

    def step(index: int = 0) -> None:
        color = blend_colors(start, end, index / (steps - 1))
        setter(color)
        if index + 1 < steps:
            _safe_after(widget, interval, lambda: step(index + 1))

    step(0)


def attach_hover_animation(widget, normal_color: str, hover_color: str, setter: Callable[[str], None]) -> None:
    """Bind enter/leave events to color glow transitions."""

    widget.bind("<Enter>", lambda _e: animate_color(widget, normal_color, hover_color, setter))
    widget.bind("<Leave>", lambda _e: animate_color(widget, hover_color, normal_color, setter))


def attach_click_animation(widget, pulse_color: str, base_color: str, setter: Callable[[str], None]) -> None:
    """Create a short click pulse for button-like widgets."""

    def on_press(_event: Optional[object] = None) -> None:
        animate_color(widget, base_color, pulse_color, setter, duration_ms=90, steps=5)

    def on_release(_event: Optional[object] = None) -> None:
        animate_color(widget, pulse_color, base_color, setter, duration_ms=120, steps=6)

    widget.bind("<ButtonPress-1>", on_press)
    widget.bind("<ButtonRelease-1>", on_release)
