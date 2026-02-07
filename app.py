#!/usr/bin/env python3
"""CustomTkinter tabanlı HTML editör + canlı önizleme uygulaması."""

from __future__ import annotations

import argparse
import html
import json
import threading
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import customtkinter as ctk
from tkinter import filedialog, messagebox


APP_TITLE = "HTML Studio - Canlı Önizleme"
DEFAULT_FILE = "target.html"
SETTINGS_FILE = ".html_studio_settings.json"

TEMPLATES = {
    "Boş": "<!doctype html>\n<html lang=\"tr\">\n<head>\n  <meta charset=\"UTF-8\" />\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n  <title>Yeni Sayfa</title>\n</head>\n<body>\n\n</body>\n</html>\n",
    "Kart": "<!doctype html>\n<html lang=\"tr\">\n<head>\n  <meta charset=\"UTF-8\" />\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n  <title>Kart Şablonu</title>\n  <style>\n    body{font-family:Arial,sans-serif;background:#f5f7fb;padding:2rem}\n    .card{max-width:540px;background:white;padding:1.25rem;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.08)}\n  </style>\n</head>\n<body>\n  <div class=\"card\">\n    <h1>Merhaba</h1>\n    <p>Burayı düzenleyin.</p>\n  </div>\n</body>\n</html>\n",
    "Landing": "<!doctype html>\n<html lang=\"tr\">\n<head>\n  <meta charset=\"UTF-8\" />\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n  <title>Landing</title>\n  <style>\n    body{margin:0;font-family:system-ui;background:#0b1020;color:#e6edf3}\n    header{padding:4rem 2rem;text-align:center}\n    button{padding:.7rem 1rem;border:0;border-radius:8px;background:#1f6feb;color:white}\n  </style>\n</head>\n<body>\n  <header>\n    <h1>Hızlı Landing Şablonu</h1>\n    <p>Canlı önizleme ile anında sonuç.</p>\n    <button>Başla</button>\n  </header>\n</body>\n</html>\n",
}


PREVIEW_PAGE = """<!doctype html>
<html lang=\"tr\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Canlı Önizleme</title>
  <style>
    body { margin:0; background:#0d1117; }
    iframe { width:100vw; height:100vh; border:0; }
    .pill {
      position:fixed; left:12px; top:12px; z-index:9;
      font-family:system-ui,sans-serif; font-size:12px; color:#e6edf3;
      background:rgba(0,0,0,.55); padding:6px 10px; border-radius:999px;
    }
  </style>
</head>
<body>
  <div class=\"pill\">Canlı izleme açık</div>
  <iframe id=\"preview\" src=\"/raw?ts=__TS__\"></iframe>
  <script>
    const frame = document.getElementById('preview');
    let lastMtime = 0;
    const stream = new EventSource('/events?last_mtime=0');
    stream.onmessage = (ev) => {
      const m = Number(ev.data || 0);
      if (!Number.isFinite(m)) return;
      if (m > lastMtime) {
        lastMtime = m;
        frame.src = '/raw?ts=' + Date.now();
      }
    };
  </script>
</body>
</html>
"""


@dataclass
class ServerConfig:
    host: str
    port: int
    file_path: Path


class HtmlPreviewHandler(BaseHTTPRequestHandler):
    target_file: Path

    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html("<meta http-equiv='refresh' content='0;url=/preview'>")
            return
        if parsed.path == "/preview":
            page = PREVIEW_PAGE.replace("__TS__", str(int(time.time())))
            self._send_html(page)
            return
        if parsed.path == "/raw":
            self._send_raw()
            return
        if parsed.path == "/events":
            self._stream_events(parse_qs(parsed.query))
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _send_raw(self) -> None:
        if not self.target_file.exists():
            msg = (
                "<!doctype html><meta charset='utf-8'><h2>Dosya bulunamadı</h2>"
                f"<p><code>{html.escape(str(self.target_file))}</code></p>"
            ).encode("utf-8")
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return

        data = self.target_file.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _stream_events(self, query: dict[str, list[str]]) -> None:
        try:
            last_mtime = float(query.get("last_mtime", ["0"])[0])
        except (TypeError, ValueError):
            last_mtime = 0.0

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        while True:
            current = self._file_mtime()
            if current > last_mtime:
                payload = f"data: {current}\n\n".encode("utf-8")
                self.wfile.write(payload)
                self.wfile.flush()
                last_mtime = current
            time.sleep(0.7)

    def _file_mtime(self) -> float:
        try:
            return self.target_file.stat().st_mtime
        except FileNotFoundError:
            return 0.0

    def _send_html(self, content: str) -> None:
        data = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class PreviewServer:
    def __init__(self) -> None:
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.config: ServerConfig | None = None

    @property
    def is_running(self) -> bool:
        return self._server is not None and self._thread is not None and self._thread.is_alive()

    def start(self, config: ServerConfig) -> None:
        if self.is_running:
            self.stop()

        handler = type("ConfiguredHtmlPreviewHandler", (HtmlPreviewHandler,), {})
        handler.target_file = config.file_path.resolve()

        self._server = ThreadingHTTPServer((config.host, config.port), handler)
        self.config = config
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._server:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None


class HtmlStudioApp(ctk.CTk):
    def __init__(self, file_path: Path, host: str, port: int) -> None:
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1200x760")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.file_path = file_path
        self.host_var = ctk.StringVar(value=host)
        self.port_var = ctk.StringVar(value=str(port))
        self.template_var = ctk.StringVar(value="Boş")
        self.autosave_var = ctk.BooleanVar(value=True)
        self.status_var = ctk.StringVar(value="Hazır")
        self.word_count_var = ctk.StringVar(value="Kelime: 0")

        self.server = PreviewServer()
        self._dirty = False
        self._autosave_job: str | None = None

        self._build_ui()
        self._load_file()
        self._load_settings()
        self._update_word_count()
        self._schedule_autosave()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(self)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        toolbar.grid_columnconfigure(14, weight=1)

        ctk.CTkButton(toolbar, text="Dosya Aç", command=self._pick_file, width=90).grid(row=0, column=0, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="Kaydet", command=self._save_file, width=90).grid(row=0, column=1, padx=4, pady=8)
        ctk.CTkButton(toolbar, text="Yedek Al", command=self._backup_file, width=90).grid(row=0, column=2, padx=4, pady=8)

        ctk.CTkLabel(toolbar, text="Şablon:").grid(row=0, column=3, padx=(10, 4))
        ctk.CTkOptionMenu(toolbar, values=list(TEMPLATES), variable=self.template_var, width=140).grid(row=0, column=4, padx=4)
        ctk.CTkButton(toolbar, text="Şablon Uygula", command=self._apply_template, width=110).grid(row=0, column=5, padx=4)

        ctk.CTkLabel(toolbar, text="Host").grid(row=0, column=6, padx=(10, 2))
        ctk.CTkEntry(toolbar, textvariable=self.host_var, width=130).grid(row=0, column=7, padx=2)
        ctk.CTkLabel(toolbar, text="Port").grid(row=0, column=8, padx=(8, 2))
        ctk.CTkEntry(toolbar, textvariable=self.port_var, width=80).grid(row=0, column=9, padx=2)

        ctk.CTkButton(toolbar, text="Önizleme Başlat", command=self._start_preview, width=120).grid(row=0, column=10, padx=4)
        ctk.CTkButton(toolbar, text="Durdur", command=self._stop_preview, width=85).grid(row=0, column=11, padx=4)
        ctk.CTkButton(toolbar, text="Tarayıcıda Aç", command=self._open_preview, width=115).grid(row=0, column=12, padx=4)

        ctk.CTkCheckBox(toolbar, text="Oto Kaydet", variable=self.autosave_var).grid(row=0, column=13, padx=8)

        ctk.CTkButton(toolbar, text="Tema", width=70, command=self._toggle_theme).grid(row=0, column=14, sticky="e", padx=6)

        editor_frame = ctk.CTkFrame(self)
        editor_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)
        editor_frame.grid_rowconfigure(0, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        self.editor = ctk.CTkTextbox(editor_frame, wrap="none", font=("Consolas", 14))
        self.editor.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.editor.bind("<KeyRelease>", self._on_editor_change)

        status = ctk.CTkFrame(self)
        status.grid(row=2, column=0, sticky="ew", padx=10, pady=(2, 10))
        status.grid_columnconfigure(1, weight=1)

        self.file_label = ctk.CTkLabel(status, text=str(self.file_path))
        self.file_label.grid(row=0, column=0, padx=8, pady=6, sticky="w")
        ctk.CTkLabel(status, textvariable=self.word_count_var).grid(row=0, column=1, padx=8, pady=6, sticky="e")
        ctk.CTkLabel(status, textvariable=self.status_var).grid(row=0, column=2, padx=8, pady=6, sticky="e")

    def _load_file(self) -> None:
        if not self.file_path.exists():
            self.file_path.write_text(TEMPLATES["Boş"], encoding="utf-8")
        content = self.file_path.read_text(encoding="utf-8")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", content)
        self.file_label.configure(text=str(self.file_path.resolve()))
        self._dirty = False
        self.status_var.set("Dosya yüklendi")

    def _pick_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="HTML dosyası seç",
            filetypes=[("HTML", "*.html *.htm"), ("Tüm dosyalar", "*.*")],
        )
        if not selected:
            return
        self.file_path = Path(selected)
        self._load_file()
        if self.server.is_running:
            self._start_preview()

    def _save_file(self) -> None:
        self.file_path.write_text(self.editor.get("1.0", "end-1c"), encoding="utf-8")
        self._dirty = False
        self.status_var.set("Kaydedildi")

    def _backup_file(self) -> None:
        backups_dir = self.file_path.parent / "backups"
        backups_dir.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = backups_dir / f"{self.file_path.stem}-{stamp}{self.file_path.suffix}"
        backup.write_text(self.editor.get("1.0", "end-1c"), encoding="utf-8")
        self.status_var.set(f"Yedek alındı: {backup.name}")

    def _apply_template(self) -> None:
        selected = self.template_var.get()
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", TEMPLATES[selected])
        self._dirty = True
        self._update_word_count()
        self.status_var.set(f"Şablon uygulandı: {selected}")

    def _parse_port(self) -> int:
        try:
            port = int(self.port_var.get())
            if not 1 <= port <= 65535:
                raise ValueError
            return port
        except ValueError:
            messagebox.showerror("Hata", "Port 1-65535 aralığında olmalı")
            raise

    def _start_preview(self) -> None:
        if self._dirty:
            self._save_file()
        try:
            port = self._parse_port()
        except ValueError:
            return
        host = self.host_var.get().strip() or "127.0.0.1"
        try:
            self.server.start(ServerConfig(host=host, port=port, file_path=self.file_path))
        except OSError as exc:
            messagebox.showerror("Sunucu Hatası", str(exc))
            return
        self.status_var.set(f"Önizleme aktif: http://{host}:{port}/preview")

    def _stop_preview(self) -> None:
        self.server.stop()
        self.status_var.set("Önizleme durduruldu")

    def _open_preview(self) -> None:
        if not self.server.is_running:
            self._start_preview()
        if not self.server.config:
            return
        webbrowser.open(f"http://{self.server.config.host}:{self.server.config.port}/preview")
        self.status_var.set("Tarayıcıda açıldı")

    def _on_editor_change(self, _event=None) -> None:
        self._dirty = True
        self._update_word_count()
        self.status_var.set("Düzenleniyor...")

    def _update_word_count(self) -> None:
        text = self.editor.get("1.0", "end-1c")
        words = len([w for w in text.split() if w])
        chars = len(text)
        self.word_count_var.set(f"Kelime: {words} | Karakter: {chars}")

    def _schedule_autosave(self) -> None:
        if self._autosave_job:
            self.after_cancel(self._autosave_job)

        def _tick() -> None:
            if self.autosave_var.get() and self._dirty:
                self._save_file()
                if self.server.is_running:
                    self.status_var.set("Oto kaydet + canlı yenileme")
            self._autosave_job = self.after(1200, _tick)

        self._autosave_job = self.after(1200, _tick)

    def _toggle_theme(self) -> None:
        current = ctk.get_appearance_mode().lower()
        ctk.set_appearance_mode("light" if current == "dark" else "dark")

    def _load_settings(self) -> None:
        sfile = Path(SETTINGS_FILE)
        if not sfile.exists():
            return
        try:
            cfg = json.loads(sfile.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        self.host_var.set(str(cfg.get("host", self.host_var.get())))
        self.port_var.set(str(cfg.get("port", self.port_var.get())))
        self.autosave_var.set(bool(cfg.get("autosave", True)))

    def _save_settings(self) -> None:
        cfg = {
            "host": self.host_var.get(),
            "port": self.port_var.get(),
            "autosave": self.autosave_var.get(),
            "last_file": str(self.file_path),
        }
        Path(SETTINGS_FILE).write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    def _on_close(self) -> None:
        if self._dirty and messagebox.askyesno("Çıkış", "Kaydedilmemiş değişiklikler var. Kaydetmek ister misiniz?"):
            self._save_file()
        self._save_settings()
        self.server.stop()
        self.destroy()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CustomTkinter HTML Studio")
    parser.add_argument("file", nargs="?", default=DEFAULT_FILE, help="Açılacak HTML dosyası")
    parser.add_argument("--host", default="127.0.0.1", help="Önizleme host")
    parser.add_argument("--port", type=int, default=8000, help="Önizleme port")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    app = HtmlStudioApp(file_path=Path(args.file), host=args.host, port=args.port)
    app.mainloop()


if __name__ == "__main__":
    main()
