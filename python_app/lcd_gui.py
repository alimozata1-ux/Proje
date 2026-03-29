import tkinter as tk
from tkinter import ttk, messagebox
import serial
from serial.tools import list_ports

BAUD_RATE = 9600
TIMEOUT_SECONDS = 1
MAX_LCD_CHAR = 32


class LcdControllerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Arduino LCD Kontrolcusu")
        self.root.geometry("520x300")

        self.serial_conn: serial.Serial | None = None

        self.port_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Durum: Baglanti yok")

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
            detail = (
                f"Port izni yok: {exc}\n\n"
                "Cozum onerileri:\n"
                "1) Arduino IDE / Serial Monitor'u kapatin.\n"
                "2) Linux icin kullanicinizi serial grubuna ekleyin:\n"
                "   sudo usermod -a -G dialout $USER\n"
                "3) Sonra oturumu kapatip acin ve tekrar deneyin."
            )
            messagebox.showerror("PermissionError [Errno 13]", detail)
            self.status_var.set("Durum: Port izin hatasi (Errno 13)")
            self.serial_conn = None

        except serial.SerialException as exc:
            error_text = str(exc)
            if "PermissionError" in error_text or "Errno 13" in error_text:
                detail = (
                    f"Port izni yok: {error_text}\n\n"
                    "Cozum onerileri:\n"
                    "1) Arduino IDE / Serial Monitor'u kapatin.\n"
                    "2) Linux icin: sudo usermod -a -G dialout $USER\n"
                    "3) Tekrar oturum acip uygulamayi yeniden baslatin."
                )
                messagebox.showerror("PermissionError [Errno 13]", detail)
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

    def send_text(self) -> None:
        if not self.serial_conn or not self.serial_conn.is_open:
            messagebox.showwarning("Uyari", "Once Arduino'ya baglanin.")
            return

        text = self.message_var.get().strip()
        if not text:
            messagebox.showwarning("Uyari", "Bos mesaj gonderemezsiniz.")
            return

        payload = text[:MAX_LCD_CHAR]

        try:
            self.serial_conn.write((payload + "\n").encode("utf-8"))
            response = self.serial_conn.readline().decode(errors="ignore").strip()
            self.status_var.set(f"Durum: Gonderildi | Arduino: {response or 'yanit yok'}")
        except serial.SerialException as exc:
            messagebox.showerror("Gonderim Hatasi", str(exc))
            self.status_var.set("Durum: Gonderim basarisiz")


if __name__ == "__main__":
    app_root = tk.Tk()
    LcdControllerApp(app_root)
    app_root.mainloop()
