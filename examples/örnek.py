"""Test amaçlı AeroWin7 örneği.

Bu dosya, kütüphaneyi hızlıca doğrulamak için ayrı bir çalıştırılabilir örnek sunar.
"""

from __future__ import annotations

from aerowin7.core import AeroAppWindow
from aerowin7.widgets import GlassButton, GlassCard, GlassEntry, GlassLabel


def main() -> None:
    """Minimal fakat görsel olarak tam bir AeroWin7 test penceresi aç."""

    app = AeroAppWindow(title="AeroWin7 Test Örneği", theme_name="light")
    theme = app.theme

    card = GlassCard(app, theme)
    card.pack(fill="both", expand=True, padx=24, pady=24)

    title = GlassLabel(card, "Örnek Test Ekranı", theme, large=True)
    title.pack(anchor="w", pady=(0, 12))

    entry = GlassEntry(card, theme, placeholder="Bir şey yazın...")
    entry.pack(fill="x", pady=(0, 12))

    status = GlassLabel(card, "Durum: Bekleniyor", theme)
    status.pack(anchor="w", pady=(0, 12))

    def on_click() -> None:
        value = entry.get().strip() or "(boş)"
        status.configure(text=f"Durum: {value}")

    btn = GlassButton(card, "Test Et", theme, command=on_click, primary=True)
    btn.pack(anchor="w")

    app.run()


if __name__ == "__main__":
    main()
