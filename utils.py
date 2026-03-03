"""Utility helpers used by Aero styled widgets."""

from __future__ import annotations

from typing import Iterable, Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert #RRGGBB to integer RGB tuple."""

    color = hex_color.strip().lstrip("#")
    if len(color) == 8:  # Ignore alpha channel when present.
        color = color[:6]
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Iterable[int]) -> str:
    """Convert an integer RGB tuple to #RRGGBB."""

    return "#" + "".join(f"{max(0, min(255, c)):02x}" for c in rgb)


def blend_colors(color_a: str, color_b: str, ratio: float) -> str:
    """Return a blended color between A and B using ratio 0..1."""

    ratio = max(0.0, min(1.0, ratio))
    rgb_a = hex_to_rgb(color_a)
    rgb_b = hex_to_rgb(color_b)
    mixed = tuple(int(rgb_a[i] + (rgb_b[i] - rgb_a[i]) * ratio) for i in range(3))
    return rgb_to_hex(mixed)


def gradient_stops(start: str, end: str, steps: int = 12) -> Tuple[str, ...]:
    """Generate color stops for gradients used in title and panel areas."""

    if steps < 2:
        return (start, end)
    return tuple(blend_colors(start, end, i / (steps - 1)) for i in range(steps))


def blur_radius_for_scale(scale: float = 1.0) -> int:
    """Helper to derive blur value for glass surfaces."""

    return max(8, int(18 * scale))
