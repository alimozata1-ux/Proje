import ctypes
import datetime
import os
import platform
import tkinter.colorchooser as colorchooser
import customtkinter as ctk
import psutil


class SystemWidget(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Sistem Widget")
        self.geometry("390x300+60+60")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.75)

        self.pinned = True
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.bg_color = "#1A2636"
        self.panel_color = "#24364E"

        self._enable_aero_effect()
        self._build_ui()
        self.update_data()

    def _enable_aero_effect(self) -> None:
        """Windows üzerinde DWM blur (AERO benzeri) efekti dener."""
        if platform.system() != "Windows":
            return

        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

            class DWM_BLURBEHIND(ctypes.Structure):
                _fields_ = [
                    ("dwFlags", ctypes.c_uint),
                    ("fEnable", ctypes.c_bool),
                    ("hRgnBlur", ctypes.c_void_p),
                    ("fTransitionOnMaximized", ctypes.c_bool),
                ]

            blur_behind = DWM_BLURBEHIND(1, True, None, False)
            ctypes.windll.dwmapi.DwmEnableBlurBehindWindow(hwnd, ctypes.byref(blur_behind))
        except Exception:
            # İşletim sistemi veya sürüm desteklemiyorsa sessizce geç.
            pass

    def _build_ui(self) -> None:
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=self.bg_color,
            corner_radius=16,
            border_width=1,
            border_color="#7FA5C8",
        )
        self.main_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self.title_bar = ctk.CTkFrame(self.main_frame, fg_color="#6E93BB", corner_radius=10)
        self.title_bar.pack(fill="x", padx=8, pady=(8, 4))

        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text="Sistem Widget",
            text_color="#F2F5FA",
            font=("Segoe UI", 13, "bold"),
        )
        self.title_label.pack(side="left", padx=10, pady=4)

        self.pin_button = self._title_button("📌", self.toggle_pin, "#AFC5DC", "#C2D5E9")
        self.pin_button.pack(side="right", padx=(0, 6), pady=4)

        self.edit_button = self._title_button("✎", self.change_background, "#AFC5DC", "#C2D5E9")
        self.edit_button.pack(side="right", padx=4, pady=4)

        self.close_button = self._title_button("✕", self.destroy, "#D86A6A", "#E58484")
        self.close_button.pack(side="right", padx=4, pady=4)

        for widget in (self.title_bar, self.title_label, self.main_frame):
            self._bind_drag(widget)

        self.content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=self.panel_color,
            corner_radius=12,
        )
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        self.clock_card = self._create_card("TARİH & SAAT")
        self.clock_value = ctk.CTkLabel(
            self.clock_card,
            text="--:--:--",
            font=("Consolas", 24, "bold"),
            text_color="#F4F8FF",
        )
        self.clock_value.pack(anchor="w", padx=10)
        self.date_value = ctk.CTkLabel(
            self.clock_card,
            text="--.--.----",
            font=("Segoe UI", 12),
            text_color="#D4E3F4",
        )
        self.date_value.pack(anchor="w", padx=10, pady=(0, 8))

        self.cpu_card = self._create_card("CPU")
        self.cpu_value = self._card_value(self.cpu_card)

        self.ram_card = self._create_card("RAM")
        self.ram_value = self._card_value(self.ram_card)

        self.gpu_card = self._create_card("GPU")
        self.gpu_value = self._card_value(self.gpu_card)

        self.ssd_card = self._create_card("SSD")
        self.ssd_value = self._card_value(self.ssd_card)

    def _title_button(self, text: str, command, color: str, hover: str) -> ctk.CTkButton:
        return ctk.CTkButton(
            self.title_bar,
            text=text,
            width=28,
            height=22,
            corner_radius=4,
            font=("Segoe UI", 11, "bold"),
            fg_color=color,
            hover_color=hover,
            text_color="#10243A",
            command=command,
        )

    def _create_card(self, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="#2D4360",
            corner_radius=10,
            border_width=1,
            border_color="#8FAECC",
        )
        frame.pack(fill="x", padx=8, pady=4)

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Segoe UI", 11, "bold"),
            text_color="#BFD5EE",
        )
        title_label.pack(anchor="w", padx=10, pady=(6, 0))
        return frame

    def _card_value(self, card: ctk.CTkFrame) -> ctk.CTkLabel:
        label = ctk.CTkLabel(
            card,
            text="--",
            font=("Consolas", 12),
            text_color="#EDF4FF",
        )
        label.pack(anchor="w", padx=10, pady=(0, 6))
        return label

    def _bind_drag(self, widget) -> None:
        widget.bind("<Button-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.on_drag)

    def start_drag(self, event) -> None:
        self.drag_start_x = event.x_root - self.winfo_x()
        self.drag_start_y = event.y_root - self.winfo_y()

    def on_drag(self, event) -> None:
        if not self.pinned:
            x = event.x_root - self.drag_start_x
            y = event.y_root - self.drag_start_y
            self.geometry(f"+{x}+{y}")

    def toggle_pin(self) -> None:
        self.pinned = not self.pinned
        self.pin_button.configure(text="📌" if self.pinned else "📍")

    def change_background(self) -> None:
        color = colorchooser.askcolor(title="Arka Plan Rengini Seç")[1]
        if not color:
            return

        self.bg_color = color
        self.main_frame.configure(fg_color=self.bg_color)

    def _get_gpu_usage(self) -> str:
        """GPU kullanımını mümkün olan yöntemle döndürür."""
        # 1) GPUtil varsa onu kullan
        try:
            import GPUtil  # type: ignore

            gpus = GPUtil.getGPUs()
            if gpus:
                load = gpus[0].load * 100
                temp = gpus[0].temperature
                return f"%{load:5.1f} | {gpus[0].name[:18]} | {temp:.0f}°C"
        except Exception:
            pass

        # 2) Windows + nvidia-smi fallback
        if platform.system() == "Windows":
            cmd = "nvidia-smi --query-gpu=utilization.gpu,name,temperature.gpu --format=csv,noheader,nounits"
            try:
                result = os.popen(cmd).read().strip()
                if result:
                    first = result.splitlines()[0]
                    util, name, temp = [p.strip() for p in first.split(",", 2)]
                    return f"%{float(util):5.1f} | {name[:18]} | {temp}°C"
            except Exception:
                pass

        return "GPU bilgisi alınamadı"

    def update_data(self) -> None:
        now = datetime.datetime.now()
        self.clock_value.configure(text=now.strftime("%H:%M:%S"))
        self.date_value.configure(text=now.strftime("%d.%m.%Y %A"))

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        gpu_text = self._get_gpu_usage()

        self.cpu_value.configure(text=f"%{cpu:5.1f}")
        self.ram_value.configure(
            text=f"%{ram.percent:5.1f} ({ram.used // (1024**3)}GB/{ram.total // (1024**3)}GB)"
        )
        self.gpu_value.configure(text=gpu_text)
        self.ssd_value.configure(
            text=f"%{disk.percent:5.1f} ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)"
        )

        self.after(1000, self.update_data)


def main() -> None:
    app = SystemWidget()
    app.mainloop()


if __name__ == "__main__":
    main()
