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
        self.geometry("360x245+60+60")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.75)

        self.pinned = True
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.desktop_only_hidden = False

        self.bg_color = "#4A79A6"
        self.panel_color = "#2F4F73"

        self._build_ui()
        self.after(100, self._enable_aero_effect)
        self._desktop_only_tick()
        self.update_data()

    def _enable_aero_effect(self) -> None:
        """Windows'ta AERO'ya yakın blur + acrylic benzeri arka plan uygular."""
        if platform.system() != "Windows":
            return

        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

            class ACCENT_POLICY(ctypes.Structure):
                _fields_ = [
                    ("AccentState", ctypes.c_int),
                    ("AccentFlags", ctypes.c_int),
                    ("GradientColor", ctypes.c_uint),
                    ("AnimationId", ctypes.c_int),
                ]

            class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
                _fields_ = [
                    ("Attribute", ctypes.c_int),
                    ("Data", ctypes.c_void_p),
                    ("SizeOfData", ctypes.c_size_t),
                ]

            accent = ACCENT_POLICY()
            accent.AccentState = 3  # ACCENT_ENABLE_BLURBEHIND
            accent.AccentFlags = 2
            accent.GradientColor = 0x55D6B588  # yarı saydam mavi-gri

            data = WINDOWCOMPOSITIONATTRIBDATA(
                19, ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p), ctypes.sizeof(accent)
            )

            ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
        except Exception:
            pass

    def _desktop_only_tick(self) -> None:
        """Pencereyi sadece masaüstü aktifken görünür yapar (Windows)."""
        if platform.system() != "Windows":
            self.after(800, self._desktop_only_tick)
            return

        try:
            fg = ctypes.windll.user32.GetForegroundWindow()
            class_name = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(fg, class_name, 255)
            is_desktop = class_name.value in {"Progman", "WorkerW"}

            if is_desktop and self.desktop_only_hidden:
                self.deiconify()
                self.desktop_only_hidden = False
            elif not is_desktop and not self.desktop_only_hidden:
                self.withdraw()
                self.desktop_only_hidden = True
        except Exception:
            pass

        self.after(800, self._desktop_only_tick)

    def _build_ui(self) -> None:
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=self.bg_color,
            corner_radius=14,
            border_width=1,
            border_color="#CFE6FF",
        )
        self.main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.title_bar = ctk.CTkFrame(self.main_frame, fg_color="#8EB3D9", corner_radius=8)
        self.title_bar.pack(fill="x", padx=6, pady=(6, 4))

        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text="Sistem Widget",
            text_color="#FFFFFF",
            font=("Segoe UI", 13, "bold"),
        )
        self.title_label.pack(side="left", padx=8, pady=2)

        self.pin_button = self._title_button("📌", self.toggle_pin, "#C2D9EE", "#D6E6F3")
        self.pin_button.pack(side="right", padx=(0, 4), pady=3)

        self.edit_button = self._title_button("✎", self.change_background, "#C2D9EE", "#D6E6F3")
        self.edit_button.pack(side="right", padx=2, pady=3)

        self.close_button = self._title_button("✕", self.destroy, "#D84F4F", "#E46C6C")
        self.close_button.pack(side="right", padx=2, pady=3)

        for widget in (self.title_bar, self.title_label, self.main_frame):
            self._bind_drag(widget)

        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=self.panel_color, corner_radius=10)
        self.content_frame.pack(fill="both", expand=True, padx=8, pady=(2, 8))

        self.clock_card = self._create_card("TARİH & SAAT")
        self.clock_value = ctk.CTkLabel(
            self.clock_card,
            text="--:--:--",
            font=("Consolas", 20, "bold"),
            text_color="#FFFFFF",
        )
        self.clock_value.pack(anchor="w", padx=8)

        self.date_value = ctk.CTkLabel(
            self.clock_card,
            text="--.--.----",
            font=("Segoe UI", 11, "bold"),
            text_color="#F1F7FF",
        )
        self.date_value.pack(anchor="w", padx=8, pady=(0, 4))

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
            width=26,
            height=20,
            corner_radius=3,
            font=("Segoe UI", 11, "bold"),
            fg_color=color,
            hover_color=hover,
            text_color="#0D233B",
            command=command,
        )

    def _create_card(self, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="#35597F",
            corner_radius=8,
            border_width=1,
            border_color="#A9CCE9",
            height=33,
        )
        frame.pack(fill="x", padx=6, pady=2)
        frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Segoe UI", 10, "bold"),
            text_color="#EAF5FF",
        )
        title_label.pack(anchor="w", padx=8, pady=(3, 0))

        return frame

    def _card_value(self, card: ctk.CTkFrame) -> ctk.CTkLabel:
        label = ctk.CTkLabel(
            card,
            text="--",
            font=("Consolas", 11, "bold"),
            text_color="#FFFFFF",
        )
        label.pack(anchor="w", padx=8, pady=(0, 2))
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
        try:
            import GPUtil  # type: ignore

            gpus = GPUtil.getGPUs()
            if gpus:
                load = gpus[0].load * 100
                return f"%{load:4.1f} {gpus[0].name[:14]}"
        except Exception:
            pass

        if platform.system() == "Windows":
            cmd = "nvidia-smi --query-gpu=utilization.gpu,name --format=csv,noheader,nounits"
            try:
                result = os.popen(cmd).read().strip()
                if result:
                    util, name = [p.strip() for p in result.splitlines()[0].split(",", 1)]
                    return f"%{float(util):4.1f} {name[:14]}"
            except Exception:
                pass

        return "GPU bilgisi yok"

    def update_data(self) -> None:
        now = datetime.datetime.now()
        self.clock_value.configure(text=now.strftime("%H:%M:%S"))
        self.date_value.configure(text=now.strftime("%d.%m.%Y %A"))

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        gpu_text = self._get_gpu_usage()

        self.cpu_value.configure(text=f"%{cpu:4.1f}")
        self.ram_value.configure(text=f"%{ram.percent:4.1f} ({ram.used // (1024**3)}G/{ram.total // (1024**3)}G)")
        self.gpu_value.configure(text=gpu_text)
        self.ssd_value.configure(text=f"%{disk.percent:4.1f} ({disk.used // (1024**3)}G/{disk.total // (1024**3)}G)")

        self.after(1000, self.update_data)


def main() -> None:
    app = SystemWidget()
    app.mainloop()


if __name__ == "__main__":
    main()
