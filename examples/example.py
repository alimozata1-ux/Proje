"""Additional runnable example for AeroWin7."""

from __future__ import annotations

import os
import sys
import tkinter as tk

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _can_open_gui() -> bool:
    try:
        probe = tk.Tk()
        probe.withdraw()
        probe.destroy()
        return True
    except tk.TclError as exc:
        print(f"GUI açılamıyor (headless ortam olabilir): {exc}")
        return False


def main() -> None:
    if not _can_open_gui():
        return

    from aerotkinter import AeroLabel
    from aerowin7.core import AeroAppWindow
    from aerowin7.widgets import GlassButton, GlassCard, GlassEntry

    app = AeroAppWindow(title="AeroWin7 Extra Example", theme_name="dark")
    theme = app.theme

    card = GlassCard(app, theme)
    card.pack(fill="both", expand=True, padx=24, pady=24)

    title = AeroLabel(
        card,
        text="Ek Örnek Dosyası",
        text_color=theme.text_primary,
        background_color="transparent",
        font=("Segoe UI", 14, "bold"),
    )
    title.pack(anchor="w", pady=(0, 12))

    entry = GlassEntry(card, theme, placeholder="Mesaj yaz...")
    entry.pack(fill="x", pady=(0, 12))

    info = AeroLabel(
        card,
        text="Butona bas ve metni güncelle.",
        text_color=theme.text_muted,
        background_color="transparent",
        font=("Segoe UI", 10),
    )
    info.pack(anchor="w", pady=(0, 12))

    def update_text() -> None:
        value = entry.get().strip() or "(boş)"
        info.configure(text=f"Yazı: {value}")

    btn = GlassButton(card, "Güncelle", theme, command=update_text, primary=True)
    btn.pack(anchor="w")

    app.run()


if __name__ == "__main__":
    main()
