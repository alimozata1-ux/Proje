"""Runnable Windows 7 Aero style demo using aerotkinter components."""

from __future__ import annotations

import os
import sys
import tkinter as tk

# `python examples/...` çalıştırmalarında proje kökünü import yoluna ekle.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _can_open_gui() -> bool:
    """Fast GUI availability check for headless environments."""

    try:
        probe = tk.Tk()
        probe.withdraw()
        probe.destroy()
        return True
    except tk.TclError as exc:
        print(f"GUI açılamıyor (headless ortam olabilir): {exc}")
        return False


def build_ui(window) -> None:
    """Create the sample GUI layout and connect simple interactions."""

    from aerotkinter import AeroLabel
    from aerowin7.theme import get_theme
    from aerowin7.widgets import GlassButton, GlassCard, GlassEntry, GlassLabel

    theme = window.theme

    content = GlassCard(window, theme)
    content.pack(fill="both", expand=True, padx=24, pady=24)

    title = GlassLabel(content, "Windows 7 Aero Demo", theme, large=True)
    title.pack(anchor="w", pady=(4, 12))

    subtitle = GlassLabel(content, "Cam efekti, blur, hover glow ve animasyonlar", theme)
    subtitle.pack(anchor="w", pady=(0, 16))

    name_entry = GlassEntry(content, theme, placeholder="Adınızı girin...")
    name_entry.pack(fill="x", pady=(0, 16))

    message = AeroLabel(
        content,
        text="Tema: Light",
        text_color=theme.text_muted,
        background_color="transparent",
        font=("Segoe UI", 10),
    )
    message.pack(anchor="w", pady=(0, 12))

    def switch_theme() -> None:
        new_theme_name = "dark" if window.theme.name == "light" else "light"
        new_theme = get_theme(new_theme_name)
        window.apply_theme(new_theme_name)
        message.configure(text=f"Tema: {new_theme.name.title()}", text_color=new_theme.text_muted)

    def submit_action() -> None:
        entered = name_entry.get().strip() or "Misafir"
        message.configure(text=f"Merhaba, {entered}! Aero GUI hazır.")

    actions = GlassCard(content, theme)
    actions.pack(fill="x", pady=(8, 0))

    primary = GlassButton(actions, "Kaydet", theme, command=submit_action, primary=True)
    primary.pack(side="left", padx=(0, 10), pady=4)

    secondary = GlassButton(actions, "Temayı Değiştir", theme, command=switch_theme, primary=False)
    secondary.pack(side="left", pady=4)


def main() -> None:
    if not _can_open_gui():
        return

    from aerowin7.core import AeroAppWindow

    app = AeroAppWindow(title="AeroTkinter Modular Demo", theme_name="light")
    build_ui(app)
    app.run()


if __name__ == "__main__":
    main()
