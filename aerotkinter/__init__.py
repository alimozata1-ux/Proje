"""Local lightweight fallback implementation of `aerotkinter`.

This compatibility layer mirrors the subset of API used by the project so
examples run even when the external dependency is unavailable.
"""

from __future__ import annotations

import tkinter as tk
from typing import Any


class _AeroBase:
    """Mixin to translate Aero-style kwargs into Tk-compatible options."""

    _bg: str | None = None
    _fg: str | None = None

    def _translate(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        k = dict(kwargs)
        bg = k.pop("background_color", None)
        fg = k.pop("text_color", None)
        font = k.pop("font", None)

        # Accepted custom options (ignored visually in fallback, but not errors).
        for opt in (
            "corner_radius",
            "blur",
            "glass_tint",
            "background_gradient",
            "gradient_overlay",
            "glow_color",
            "shadow_color",
            "border_color",
            "placeholder_color",
            "padding",
        ):
            k.pop(opt, None)

        if bg not in (None, "transparent"):
            k["bg"] = bg
            self._bg = bg
        if fg is not None:
            k["fg"] = fg
            self._fg = fg
        if font is not None:
            k["font"] = font
        return k

    def configure(self, cnf=None, **kw):  # type: ignore[override]
        options = {}
        if cnf:
            options.update(cnf)
        options.update(kw)
        translated = self._translate(options)
        return super().configure(translated)

    config = configure


class AeroWindow(tk.Tk, _AeroBase):
    def __init__(self, **kwargs):
        super().__init__()
        if kwargs:
            self.configure(**kwargs)


class AeroCard(tk.Frame, _AeroBase):
    def __init__(self, master=None, **kwargs):
        translated = self._translate(kwargs)
        super().__init__(master, **translated)


class AeroLabel(tk.Label, _AeroBase):
    def __init__(self, master=None, **kwargs):
        translated = self._translate(kwargs)
        super().__init__(master, **translated)


class AeroButton(tk.Button, _AeroBase):
    def __init__(self, master=None, **kwargs):
        translated = self._translate(kwargs)
        super().__init__(master, **translated)


class AeroEntry(tk.Entry, _AeroBase):
    def __init__(self, master=None, **kwargs):
        self._placeholder = kwargs.pop("placeholder", "")
        self._placeholder_color = kwargs.get("placeholder_color", "#808080")
        translated = self._translate(kwargs)
        super().__init__(master, **translated)

        self._normal_fg = translated.get("fg", "#000000")
        self._showing_placeholder = False
        self._apply_placeholder()
        self.bind("<FocusIn>", self._on_focus_in, add="+")
        self.bind("<FocusOut>", self._on_focus_out, add="+")

    def _apply_placeholder(self) -> None:
        if not self.get() and self._placeholder:
            self._showing_placeholder = True
            self.insert(0, self._placeholder)
            super().configure(fg=self._placeholder_color)

    def _on_focus_in(self, _event=None) -> None:
        if self._showing_placeholder:
            self.delete(0, tk.END)
            self._showing_placeholder = False
            super().configure(fg=self._normal_fg)

    def _on_focus_out(self, _event=None) -> None:
        if not self.get():
            self._apply_placeholder()

    def get(self) -> str:  # type: ignore[override]
        value = super().get()
        if self._showing_placeholder:
            return ""
        return value
