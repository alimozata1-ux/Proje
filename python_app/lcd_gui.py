import argparse
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import serial
from serial.tools import list_ports

BAUD_RATE = 9600
TIMEOUT_SECONDS = 1
MAX_LCD_CHAR = 32


def build_permission_help(error_text: str) -> str:
    return (
        f"Port izni yok: {error_text}\n\n"
        "Cozum onerileri:\n"
        "1) Arduino IDE / Serial Monitor'u kapatin.\n"
        "2) Windows'ta uygulamayi yonetici olarak acmayi deneyin.\n"
        "3) Linux icin: sudo usermod -a -G dialout $USER\n"
        "4) Oturumu kapatip acin ve tekrar deneyin."
    )


def send_text_once(port: str, text: str) -> int:
    payload = text.strip()[:MAX_LCD_CHAR]
    if not payload:
        print("Bos mesaj gonderilemez.", file=sys.stderr)
        return 1

    try:
        with serial.Serial(port=port, baudrate=BAUD_RATE, timeout=TIMEOUT_SECONDS) as conn:
            ready = conn.readline().decode(errors="ignore").strip()
            conn.write((payload + "\n").encode("utf-8"))
            response = conn.readline().decode(errors="ignore").strip()
            print(f"Arduino READY: {ready or '-'}")
            print(f"Arduino RESP: {response or '-'}")
            return 0
    except PermissionError as exc:
        print(build_permission_help(str(exc)), file=sys.stderr)
        return 2
    except serial.SerialException as exc:
        error_text = str(exc)
        if "PermissionError" in error_text or "Errno 13" in error_text:
            print(build_permission_help(error_text), file=sys.stderr)
            return 2
        print(f"Baglanti hatasi: {error_text}", file=sys.stderr)
        return 3


class LcdControllerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Arduino LCD Kontrolcusu")
        self.root.geometry("560x330")

        self.serial_conn: serial.Serial | None = None

        self.port_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Durum: Baglanti yok")
        self.vjoy_mode_var = tk.BooleanVar(value=False)

        self._build_ui()
        self.refresh_ports()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        port_row = ttk.Frame(container)
        port_row.pack(fill="x", pady=(0, 12))

        ttk.Label(port_row, text="COM Port:").pack(side="left")
        self.port_combo = ttk.Combobox(port_row, textvariable=self.port_var, state="readonly", width=24)
        self.port_combo.pack(side="left", padx=8)

        ttk.Button(port_row, text="Yenile", command=self.refresh_ports).pack(side="left", padx=4)
        ttk.Button(port_row, text="Baglan", command=self.connect).pack(side="left", padx=4)
        ttk.Button(port_row, text="Baglantiyi Kes", command=self.disconnect).pack(side="left", padx=4)

        mode_row = ttk.Frame(container)
        mode_row.pack(fill="x", pady=(0, 8))
        ttk.Checkbutton(
            mode_row,
            text="vJoy Uyumlu Mod (ASCII + 32 karakter)",
            variable=self.vjoy_mode_var,
        ).pack(anchor="w")

        ttk.Label(container, text="LCD'ye gonderilecek yazi (maks 32 karakter):").pack(anchor="w")

        self.message_entry = ttk.Entry(container, textvariable=self.message_var, width=70)
        self.message_entry.pack(fill="x", pady=(4, 10))

        ttk.Button(container, text="LCD'ye Gonder", command=self.send_text).pack(anchor="e")

        ttk.Label(
            container,
            text="Not: 16x2 LCD oldugu icin metin 2 satira bolunur (16 + 16).",
            foreground="#555",
        ).pack(anchor="w", pady=(10, 2))

        ttk.Label(container, textvariable=self.status_var, foreground="#0a5").pack(anchor="w", pady=(10, 0))

    def refresh_ports(self) -> None:
        ports = [port.device for port in list_ports.comports()]
        self.port_combo["values"] = ports

        if ports and not self.port_var.get():
            self.port_var.set(ports[0])

        self.status_var.set(f"Durum: {len(ports)} port bulundu")

    def connect(self) -> None:
        if self.serial_conn and self.serial_conn.is_open:
            self.status_var.set("Durum: Zaten bagli")
            return

        port = self.port_var.get().strip()
        if not port:
            messagebox.showwarning("Uyari", "Lutfen bir COM port secin.")
            return

        try:
            self.serial_conn = serial.Serial(port=port, baudrate=BAUD_RATE, timeout=TIMEOUT_SECONDS)
            ready = self.serial_conn.readline().decode(errors="ignore").strip()

            if ready:
                self.status_var.set(f"Durum: Baglandi ({port}) | Arduino: {ready}")
            else:
                self.status_var.set(f"Durum: Baglandi ({port})")

        except PermissionError as exc:
            messagebox.showerror("PermissionError [Errno 13]", build_permission_help(str(exc)))
            self.status_var.set("Durum: Port izin hatasi (Errno 13)")
            self.serial_conn = None

        except serial.SerialException as exc:
            error_text = str(exc)
            if "PermissionError" in error_text or "Errno 13" in error_text:
                messagebox.showerror("PermissionError [Errno 13]", build_permission_help(error_text))
                self.status_var.set("Durum: Port izin hatasi (Errno 13)")
            else:
                messagebox.showerror("Baglanti Hatasi", error_text)
                self.status_var.set("Durum: Baglanti hatasi")
            self.serial_conn = None

    def disconnect(self) -> None:
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None

        self.status_var.set("Durum: Baglanti kapatildi")

    def _normalize_text(self, text: str) -> str:
        payload = text[:MAX_LCD_CHAR]
        if self.vjoy_mode_var.get():
            payload = payload.encode("ascii", errors="ignore").decode("ascii")
        return payload

    def send_text(self) -> None:
        if not self.serial_conn or not self.serial_conn.is_open:
            messagebox.showwarning("Uyari", "Once Arduino'ya baglanin.")
            return

        text = self.message_var.get().strip()
        if not text:
            messagebox.showwarning("Uyari", "Bos mesaj gonderemezsiniz.")
            return

        payload = self._normalize_text(text)

        try:
            self.serial_conn.write((payload + "\n").encode("utf-8"))
            response = self.serial_conn.readline().decode(errors="ignore").strip()
            self.status_var.set(f"Durum: Gonderildi | Arduino: {response or 'yanit yok'}")
        except serial.SerialException as exc:
            messagebox.showerror("Gonderim Hatasi", str(exc))
            self.status_var.set("Durum: Gonderim basarisiz")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Arduino LCD Controller")
    parser.add_argument("--vjoy", action="store_true", help="GUI acmadan tek seferlik gonderim yapar")
    parser.add_argument("--port", help="COM port (ornek: COM3 / /dev/ttyUSB0)")
    parser.add_argument("--text", help="LCD'ye gonderilecek metin")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.vjoy:
        if not args.port or not args.text:
            print("--vjoy modunda --port ve --text zorunludur.", file=sys.stderr)
            raise SystemExit(1)
        raise SystemExit(send_text_once(args.port, args.text))

    app_root = tk.Tk()
    LcdControllerApp(app_root)
    app_root.mainloop()
