#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import importlib.util
import io
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Dict, Optional

from system_monitor import Thresholds, collect_snapshot

ROOT = Path(__file__).parent
ICON_DIR = ROOT / "web" / "static" / "icons"
REFRESH_MS = 3000


class IconFactory:
    """SVG dosyalarını kullanarak tkinter PhotoImage üretir (opsiyonel bağımlılıklarla)."""

    def __init__(self, size: tuple[int, int] = (160, 100)) -> None:
        self.size = size
        self.cache: Dict[str, tk.PhotoImage] = {}
        self.has_cairosvg = importlib.util.find_spec("cairosvg") is not None
        self.has_pillow = importlib.util.find_spec("PIL") is not None

    def load(self, name: str) -> Optional[tk.PhotoImage]:
        if name in self.cache:
            return self.cache[name]

        svg_path = ICON_DIR / f"{name}.svg"
        if not svg_path.exists():
            return None

        if self.has_cairosvg and self.has_pillow:
            cairosvg = importlib.import_module("cairosvg")
            pil_image = importlib.import_module("PIL.Image")
            pil_imagetk = importlib.import_module("PIL.ImageTk")

            png_bytes = cairosvg.svg2png(url=str(svg_path), output_width=self.size[0], output_height=self.size[1])
            image = pil_image.open(io.BytesIO(png_bytes))
            tk_img = pil_imagetk.PhotoImage(image)
            self.cache[name] = tk_img
            return tk_img

        # Fallback: SVG içindeki metni okuyup tkinter ile basit görsel üret
        svg_text = svg_path.read_text(encoding="utf-8")
        label = "?"
        marker = ">"
        if "</text>" in svg_text and marker in svg_text:
            label = svg_text.split(marker)[-2].split("<")[-1].strip() or name.upper()

        canvas = tk.Canvas(width=self.size[0], height=self.size[1], bg="#1a2430", highlightthickness=0)
        canvas.create_rectangle(4, 4, self.size[0] - 4, self.size[1] - 4, outline="#8aa0b7", width=2, fill="#2a3a4d")
        canvas.create_text(self.size[0] // 2, self.size[1] // 2, text=label, fill="#f2f7ff", font=("Segoe UI", 28, "bold"))
        canvas.update()
        ps = canvas.postscript(colormode="color")
        canvas.destroy()

        # postscript->photoimage dönüşümü: tk kendisi doğrudan desteklemez, bu yüzden boş dön.
        return None


class MonitorGUI(tk.Tk):
    def __init__(self, thresholds: Thresholds) -> None:
        super().__init__()
        self.title("Sistem İzleyici - Tkinter GUI")
        self.geometry("1100x760")
        self.configure(bg="#0f1620")

        self.thresholds = thresholds
        self.icon_factory = IconFactory()
        self.icon_refs: Dict[str, tk.PhotoImage] = {}

        self._build_ui()
        self.after(200, self.refresh_data)

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Card.TFrame", background="#1a2430", borderwidth=1, relief="solid")
        style.configure("Title.TLabel", background="#0f1620", foreground="#e8f1ff", font=("Segoe UI", 18, "bold"))
        style.configure("Key.TLabel", background="#1a2430", foreground="#b9cce2", font=("Segoe UI", 10))
        style.configure("Val.TLabel", background="#1a2430", foreground="#f5f9ff", font=("Segoe UI", 15, "bold"))

        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="Canlı Sistem İzleyici (Tkinter)", style="Title.TLabel").pack(anchor="w", pady=(0, 10))

        self.grid_frame = ttk.Frame(root)
        self.grid_frame.pack(fill="x")

        self.cards: Dict[str, ttk.Label] = {}
        specs = [
            ("cpu", "CPU"), ("gpu", "GPU"), ("ram", "RAM"), ("hdd", "Disk Okuma/Yazma"),
            ("ssd", "SSD Takılı"), ("m2", "M.2/NVMe Takılı"), ("sd", "SD Kart Takılı"), ("usb", "USB Bellek Takılı"),
        ]

        for i, (icon, title) in enumerate(specs):
            card = ttk.Frame(self.grid_frame, style="Card.TFrame", padding=10)
            card.grid(row=i // 4, column=i % 4, sticky="nsew", padx=6, pady=6)
            self.grid_frame.columnconfigure(i % 4, weight=1)

            icon_img = self.icon_factory.load(icon)
            if icon_img:
                self.icon_refs[icon] = icon_img
                ttk.Label(card, image=icon_img, style="Key.TLabel").pack()
            else:
                ttk.Label(card, text=f"[{icon.upper()} SVG]", style="Key.TLabel").pack()

            ttk.Label(card, text=title, style="Key.TLabel").pack(anchor="w", pady=(8, 2))
            val = ttk.Label(card, text="-", style="Val.TLabel")
            val.pack(anchor="w")
            self.cards[icon] = val

        bottom = ttk.Frame(root)
        bottom.pack(fill="both", expand=True, pady=(10, 0))

        alerts_card = ttk.Frame(bottom, style="Card.TFrame", padding=10)
        alerts_card.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ttk.Label(alerts_card, text="Uyarılar", style="Key.TLabel").pack(anchor="w")
        self.alerts = tk.Text(alerts_card, height=10, bg="#1a2430", fg="#ffb0b0", bd=0)
        self.alerts.pack(fill="both", expand=True)

        dev_card = ttk.Frame(bottom, style="Card.TFrame", padding=10)
        dev_card.pack(side="left", fill="both", expand=True, padx=(6, 0))
        ttk.Label(dev_card, text="Algılanan Aygıtlar", style="Key.TLabel").pack(anchor="w")
        self.devices = tk.Text(dev_card, height=10, bg="#1a2430", fg="#d7e9ff", bd=0)
        self.devices.pack(fill="both", expand=True)

        self.status = ttk.Label(root, text="", style="Key.TLabel")
        self.status.pack(anchor="w", pady=(8, 0))

    def refresh_data(self) -> None:
        snap = collect_snapshot(self.thresholds)
        s, st = snap["system"], snap["storage"]

        self.cards["cpu"].configure(text=f"%{s['cpu_percent']:.1f}")
        self.cards["gpu"].configure(text="Tespit yok" if s["gpu_percent"] is None else f"%{s['gpu_percent']:.1f}")
        self.cards["ram"].configure(text=f"%{s['ram_used_percent']:.1f} / {s['ram_total_gb']:.1f} GB")
        self.cards["hdd"].configure(text=f"{st['read_mb_s']:.2f} / {st['write_mb_s']:.2f} MB/s")
        self.cards["ssd"].configure(text="Evet" if st["ssd_takili"] else "Hayır")
        self.cards["m2"].configure(text="Evet" if st["m2_nvme_takili"] else "Hayır")
        self.cards["sd"].configure(text="Evet" if st["sd_kart_takili"] else "Hayır")
        self.cards["usb"].configure(text="Evet" if st["usb_takili"] else "Hayır")

        self.alerts.delete("1.0", "end")
        if snap["alerts"]:
            self.alerts.insert("end", "\n".join(f"• {a}" for a in snap["alerts"]))
        else:
            self.alerts.insert("end", "Uyarı yok")

        self.devices.delete("1.0", "end")
        if st["devices"]:
            self.devices.insert("end", "\n".join(
                f"• {d['name']} | {d['kind']} | {d['interface']} | {d['mountpoint'] or '-'}" for d in st["devices"]
            ))
        else:
            self.devices.insert("end", "Aygıt bulunamadı")

        backend = "psutil" if s.get("psutil_available") else "Linux fallback"
        self.status.configure(text=f"Backend: {backend} | Yenileme: {REFRESH_MS//1000}s")

        self.after(REFRESH_MS, self.refresh_data)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Custom tkinter sistem izleyici GUI")
    p.add_argument("--min-read", type=float, default=5.0)
    p.add_argument("--min-write", type=float, default=5.0)
    p.add_argument("--max-cpu", type=float, default=90.0)
    p.add_argument("--max-ram", type=float, default=90.0)
    p.add_argument("--max-gpu", type=float, default=90.0)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    th = Thresholds(args.min_read, args.min_write, args.max_cpu, args.max_ram, args.max_gpu)
    app = MonitorGUI(th)
    app.mainloop()


if __name__ == "__main__":
    main()
