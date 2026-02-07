import datetime
import tkinter as tk
from tkinter import colorchooser

import psutil


class SystemWidget:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sistem Widget")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.75)

        self.bg_color = "#1f1f1f"
        self.fg_color = "#f2f2f2"

        self.pinned = True
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.container = tk.Frame(root, bg=self.bg_color, bd=2, relief="flat")
        self.container.pack(fill="both", expand=True)

        self._build_titlebar()
        self._build_content()

        self._bind_drag(self.titlebar)
        self._bind_drag(self.container)

        self.update_data()

    def _build_titlebar(self) -> None:
        self.titlebar = tk.Frame(self.container, bg=self.bg_color)
        self.titlebar.pack(fill="x", padx=6, pady=(6, 2))

        self.title_label = tk.Label(
            self.titlebar,
            text="Widget",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 10, "bold"),
        )
        self.title_label.pack(side="left")

        self.pin_button = tk.Button(
            self.titlebar,
            text="📌",
            command=self.toggle_pin,
            bg=self.bg_color,
            fg="#ffd166",
            activebackground=self.bg_color,
            activeforeground="#ffe08a",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.pin_button.pack(side="right", padx=(2, 4))

        self.color_button = tk.Button(
            self.titlebar,
            text="🎨",
            command=self.choose_color,
            bg=self.bg_color,
            fg="#8ecae6",
            activebackground=self.bg_color,
            activeforeground="#bde0fe",
            bd=0,
            font=("Segoe UI", 10),
            cursor="hand2",
        )
        self.color_button.pack(side="right", padx=2)

        self.close_button = tk.Button(
            self.titlebar,
            text="X",
            command=self.root.destroy,
            bg=self.bg_color,
            fg="#ff4d4d",
            activebackground=self.bg_color,
            activeforeground="#ff8080",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.close_button.pack(side="right", padx=2)

        self._bind_drag(self.title_label)

    def _build_content(self) -> None:
        self.content = tk.Frame(self.container, bg=self.bg_color)
        self.content.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        self.clock_label = tk.Label(
            self.content,
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        )
        self.clock_label.pack(fill="x", pady=(0, 4))

        self.date_label = tk.Label(
            self.content,
            bg=self.bg_color,
            fg="#c7c7c7",
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.date_label.pack(fill="x", pady=(0, 8))

        self.cpu_label = self._metric_label("CPU: --")
        self.ram_label = self._metric_label("RAM: --")
        self.ssd_label = self._metric_label("SSD: --")

    def _metric_label(self, text: str) -> tk.Label:
        label = tk.Label(
            self.content,
            text=text,
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Consolas", 10),
            anchor="w",
        )
        label.pack(fill="x", pady=1)
        return label

    def _bind_drag(self, widget: tk.Widget) -> None:
        widget.bind("<Button-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.on_drag)

    def start_drag(self, event: tk.Event) -> None:
        self.drag_start_x = event.x_root - self.root.winfo_x()
        self.drag_start_y = event.y_root - self.root.winfo_y()

    def on_drag(self, event: tk.Event) -> None:
        if not self.pinned:
            x = event.x_root - self.drag_start_x
            y = event.y_root - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")

    def toggle_pin(self) -> None:
        self.pinned = not self.pinned
        self.pin_button.config(text="📌" if self.pinned else "📍")

    def choose_color(self) -> None:
        color = colorchooser.askcolor(title="Arkaplan Rengi Seç")[1]
        if color:
            self.bg_color = color
            self.apply_theme()

    def apply_theme(self) -> None:
        widgets = [
            self.container,
            self.titlebar,
            self.title_label,
            self.content,
            self.clock_label,
            self.date_label,
            self.cpu_label,
            self.ram_label,
            self.ssd_label,
            self.pin_button,
            self.color_button,
            self.close_button,
        ]

        for widget in widgets:
            widget.configure(bg=self.bg_color)

        self.title_label.configure(fg=self.fg_color)
        self.clock_label.configure(fg=self.fg_color)
        self.cpu_label.configure(fg=self.fg_color)
        self.ram_label.configure(fg=self.fg_color)
        self.ssd_label.configure(fg=self.fg_color)

        self.date_label.configure(fg="#d8d8d8")
        self.pin_button.configure(
            fg="#ffd166", activebackground=self.bg_color, activeforeground="#ffe08a"
        )
        self.color_button.configure(
            fg="#8ecae6", activebackground=self.bg_color, activeforeground="#bde0fe"
        )
        self.close_button.configure(
            fg="#ff4d4d", activebackground=self.bg_color, activeforeground="#ff8080"
        )

    def update_data(self) -> None:
        now = datetime.datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))
        self.date_label.config(text=now.strftime("%d.%m.%Y - %A"))

        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        self.cpu_label.config(text=f"CPU : %{cpu:5.1f}")
        self.ram_label.config(text=f"RAM : %{ram.percent:5.1f} ({ram.used // (1024**3)}GB/{ram.total // (1024**3)}GB)")
        self.ssd_label.config(text=f"SSD : %{disk.percent:5.1f} ({disk.used // (1024**3)}GB/{disk.total // (1024**3)}GB)")

        self.root.after(1000, self.update_data)


def main() -> None:
    root = tk.Tk()
    root.geometry("280x170+50+50")
    SystemWidget(root)
    root.mainloop()


if __name__ == "__main__":
    main()
