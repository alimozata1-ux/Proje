"""Test amaçlı AeroWin7 örneği.

Bu dosya, kütüphaneyi hızlıca doğrulamak için ayrı bir çalıştırılabilir örnek sunar.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys

# `python examples/...` çalıştırmalarında proje kökünü import yoluna ekle.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def _check_runtime_dependencies() -> bool:
    """Gerekirse aerotkinter kurulumu deneyip bağımlılıkları doğrula."""

    if importlib.util.find_spec("aerotkinter") is not None:
        return True

    print("Bilgi: 'aerotkinter' bulunamadı, otomatik kurulum deneniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aerotkinter"])
    except Exception as exc:
        print(f"Hata: otomatik kurulum başarısız oldu: {exc}")
        print("Lütfen elle kurun: pip install aerotkinter")
        return False

    if importlib.util.find_spec("aerotkinter") is None:
        print("Hata: kurulum denendi ancak 'aerotkinter' yine bulunamadı.")
        return False
    return True


def main() -> None:
    """Minimal fakat görsel olarak tam bir AeroWin7 test penceresi aç."""

    if not _check_runtime_dependencies():
        return

    from aerowin7.core import AeroAppWindow
    from aerowin7.widgets import GlassButton, GlassCard, GlassEntry, GlassLabel

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
