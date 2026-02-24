from __future__ import annotations

import html
import os
import secrets
import shutil
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import cgi

from projectdb import ProjectDatabase

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
STATIC_DIR = BASE_DIR / "static"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "İazemy68")
SESSIONS: set[str] = set()

UPLOAD_DIR.mkdir(exist_ok=True)
db = ProjectDatabase(BASE_DIR / "data.db")


def page_layout(title: str, body: str, admin_link: str = '<a class="admin-link" href="/admin">Admin</a>') -> str:
    return f"""<!doctype html>
<html lang=\"tr\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{html.escape(title)}</title>
  <link rel=\"stylesheet\" href=\"/static/style.css\">
</head>
<body>
  <div class=\"window\">
    <header class=\"window-header\">
      <div class=\"logo\">◎</div>
      <h1>{html.escape(title)}</h1>
      {admin_link}
    </header>
    {body}
  </div>
</body>
</html>"""


def index_html() -> str:
    cards = []
    for p in db.list_projects():
        cards.append(
            f"""
            <article class=\"card\">
              <h2>{html.escape(p['title'])}</h2>
              <p>{html.escape(p['description'])}</p>
              <small>{html.escape(p['size_mb'])} MB • {p['download_count']} indirme</small>
              <a class=\"download-btn\" href=\"/download?id={p['id']}\">⬇ İndir</a>
            </article>
            """
        )
    if not cards:
        cards.append('<article class="card full"><h2>Henüz proje yok</h2><p>Admin panelinden ilk projeyi yükleyebilirsin.</p></article>')

    return page_layout("Rocketcc Package", f"<main class=\"grid\">{''.join(cards)}</main>")


def login_html(message: str = "") -> str:
    alerts = f"<ul class='alerts'><li class='error'>{html.escape(message)}</li></ul>" if message else ""
    body = f"""
    <main class=\"panel\">
      {alerts}
      <form method=\"post\" class=\"form\" action=\"/admin\">
        <label>Şifre</label>
        <input type=\"password\" name=\"password\" required>
        <button type=\"submit\">Giriş Yap</button>
      </form>
      <a class=\"download-btn\" href=\"/\">Ana sayfaya dön</a>
    </main>
    """
    return page_layout("Admin Giriş", body)


def admin_panel_html(message: str = "") -> str:
    alerts = f"<ul class='alerts'><li class='success'>{html.escape(message)}</li></ul>" if message else ""
    projects = "".join(
        f"<li>{html.escape(p['title'])} ({html.escape(p['size_mb'])} MB) - {p['download_count']} indirme</li>"
        for p in db.list_projects()
    ) or "<li>Kayıt yok.</li>"

    body = f"""
    <main class=\"panel\">
      {alerts}
      <form method=\"post\" enctype=\"multipart/form-data\" class=\"form\" action=\"/admin/panel\">
        <label>Proje Adı</label><input name=\"title\" required>
        <label>Açıklama</label><input name=\"description\" required>
        <label>Boyut (MB)</label><input name=\"size_mb\" required>
        <label>Dosya</label><input type=\"file\" name=\"file\" required>
        <button type=\"submit\">Yükle</button>
      </form>
      <h2>Yüklü Projeler</h2>
      <ul class=\"project-list\">{projects}</ul>
    </main>
    """
    return page_layout("Admin Paneli", body, '<a class="admin-link" href="/admin/logout">Çıkış</a>')


class Handler(BaseHTTPRequestHandler):
    def _session_token(self) -> str | None:
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None
        c = cookies.SimpleCookie()
        c.load(cookie_header)
        m = c.get("session_token")
        return m.value if m else None

    def _is_admin(self) -> bool:
        token = self._session_token()
        return bool(token and token in SESSIONS)

    def _send_html(self, text: str, status: int = 200, extra_headers: dict[str, str] | None = None) -> None:
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, location: str, extra_headers: dict[str, str] | None = None) -> None:
        self.send_response(302)
        self.send_header("Location", location)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/":
            return self._send_html(index_html())

        if parsed.path == "/admin":
            return self._send_html(login_html())

        if parsed.path == "/admin/panel":
            if not self._is_admin():
                return self._redirect("/admin")
            return self._send_html(admin_panel_html())

        if parsed.path == "/admin/logout":
            token = self._session_token()
            if token:
                SESSIONS.discard(token)
            return self._redirect("/", {"Set-Cookie": "session_token=; Path=/; Max-Age=0"})

        if parsed.path == "/download":
            query = parse_qs(parsed.query)
            try:
                project_id = int(query.get("id", [""])[0])
            except ValueError:
                return self._redirect("/")
            project = db.get_project(project_id)
            if not project:
                return self._redirect("/")

            file_path = UPLOAD_DIR / project["filename"]
            if not file_path.exists():
                return self._redirect("/")

            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f"attachment; filename={project['filename']}")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        if parsed.path.startswith("/static/"):
            rel = parsed.path.replace("/static/", "", 1)
            file_path = STATIC_DIR / rel
            if file_path.exists() and file_path.is_file():
                ctype = "text/css" if file_path.suffix == ".css" else "application/octet-stream"
                data = file_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", f"{ctype}; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        self._send_html("<h1>404</h1>", status=404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/admin":
            length = int(self.headers.get("Content-Length", "0"))
            payload = self.rfile.read(length).decode("utf-8", errors="ignore")
            params = parse_qs(payload)
            password = params.get("password", [""])[0]
            if password == ADMIN_PASSWORD:
                token = secrets.token_hex(16)
                SESSIONS.add(token)
                return self._redirect("/admin/panel", {"Set-Cookie": f"session_token={token}; Path=/; HttpOnly"})
            return self._send_html(login_html("Şifre hatalı."))

        if parsed.path == "/admin/panel":
            if not self._is_admin():
                return self._redirect("/admin")

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            title = form.getfirst("title", "").strip()
            description = form.getfirst("description", "").strip()
            size_mb = form.getfirst("size_mb", "").strip()
            file_item = form["file"] if "file" in form else None

            if not title or not description or not size_mb or not file_item or not getattr(file_item, "filename", ""):
                return self._send_html(admin_panel_html("Tüm alanlar zorunludur."))

            filename = os.path.basename(file_item.filename)
            save_path = UPLOAD_DIR / filename
            counter = 1
            while save_path.exists():
                stem, suffix = os.path.splitext(filename)
                filename = f"{stem}_{counter}{suffix}"
                save_path = UPLOAD_DIR / filename
                counter += 1

            with open(save_path, "wb") as f:
                shutil.copyfileobj(file_item.file, f)

            db.add_project(title, description, size_mb, filename)
            return self._send_html(admin_panel_html("Proje başarıyla yüklendi."))

        self._send_html("<h1>404</h1>", status=404)


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Sunucu çalışıyor: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
