"""Animation engine and reusable helpers for Aero widgets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

from .utils import blend_colors


def ease_out_cubic(t: float) -> float:
    """Smooth ending easing used for hover/click transitions."""

    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


@dataclass
class AnimationHandle:
    """Stores after callback id for cancellation/replacement."""

    after_id: Optional[str] = None


class AnimationEngine:
    """Small Tk-compatible animation motor for widget/window transitions."""

    def __init__(self) -> None:
        self._handles: Dict[str, AnimationHandle] = {}

    def _key(self, widget, name: str) -> str:
        return f"{id(widget)}::{name}"

    def cancel(self, widget, name: str) -> None:
        """Cancel an existing animation by logical name."""

        key = self._key(widget, name)
        handle = self._handles.get(key)
        if not handle or not handle.after_id:
            return
        try:
            widget.after_cancel(handle.after_id)
        except Exception:
            pass
        self._handles.pop(key, None)

    def animate(
        self,
        widget,
        name: str,
        duration_ms: int,
        steps: int,
        on_step: Callable[[float], None],
        easing: Callable[[float], float] = ease_out_cubic,
    ) -> None:
        """Core timeline runner (0..1 progress) with easing and replacement."""

        self.cancel(widget, name)
        key = self._key(widget, name)
        handle = AnimationHandle()
        self._handles[key] = handle
        steps = max(2, steps)
        interval = max(10, duration_ms // steps)

        def frame(index: int = 0) -> None:
            progress = index / (steps - 1)
            on_step(easing(progress))
            if index + 1 >= steps:
                self._handles.pop(key, None)
                return
            try:
                handle.after_id = widget.after(interval, lambda: frame(index + 1))
            except Exception:
                self._handles.pop(key, None)

        frame(0)

    def color_transition(
        self,
        widget,
        name: str,
        start: str,
        end: str,
        setter: Callable[[str], None],
        duration_ms: int = 160,
        steps: int = 10,
    ) -> None:
        """Animate a color from start to end with easing."""

        def on_step(progress: float) -> None:
            setter(blend_colors(start, end, progress))

        self.animate(widget, name, duration_ms, steps, on_step)

    def fade_in(self, widget, duration_ms: int = 350, steps: int = 18) -> None:
        """Fade a toplevel window in using alpha channel."""

        def on_step(progress: float) -> None:
            if hasattr(widget, "attributes"):
                try:
                    widget.attributes("-alpha", progress)
                except Exception:
                    pass

        self.animate(widget, "window_fade_in", duration_ms, steps, on_step)


def attach_hover_animation(
    engine: AnimationEngine,
    widget,
    normal_color: str,
    hover_color: str,
    setter: Callable[[str], None],
    name: str = "hover",
) -> None:
    """Bind enter/leave events to smooth hover transitions."""

    widget.bind(
        "<Enter>",
        lambda _e: engine.color_transition(widget, f"{name}_in", normal_color, hover_color, setter, 150, 10),
    )
    widget.bind(
        "<Leave>",
        lambda _e: engine.color_transition(widget, f"{name}_out", hover_color, normal_color, setter, 180, 12),
    )


def attach_click_animation(
    engine: AnimationEngine,
    widget,
    pulse_color: str,
    base_color: str,
    setter: Callable[[str], None],
    name: str = "click",
) -> None:
    """Bind press/release pulse animations for button-like widgets."""

    widget.bind(
        "<ButtonPress-1>",
        lambda _e: engine.color_transition(widget, f"{name}_press", base_color, pulse_color, setter, 90, 7),
    )
    widget.bind(
        "<ButtonRelease-1>",
        lambda _e: engine.color_transition(widget, f"{name}_release", pulse_color, base_color, setter, 120, 8),
    )


DEFAULT_ENGINE = AnimationEngine()


def fade_in(widget, duration_ms: int = 350, steps: int = 18) -> None:
    """Backward-compatible facade for fade animation."""

    DEFAULT_ENGINE.fade_in(widget, duration_ms=duration_ms, steps=steps)
