#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from system_monitor import Thresholds, collect_snapshot

WEB_ROOT = Path(__file__).parent / "web"


class Handler(BaseHTTPRequestHandler):
    thresholds = Thresholds()

    def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self._send(b"Not Found", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)
            return
        mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        self._send(file_path.read_bytes(), mime)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path

        if path in ["/", "/index.html"]:
            self._serve_file(WEB_ROOT / "index.html")
            return

        if path == "/api/snapshot":
            data = collect_snapshot(self.thresholds)
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self._send(body, "application/json; charset=utf-8")
            return

        if path.startswith("/static/"):
            target = (WEB_ROOT / "static" / path.removeprefix("/static/")).resolve()
            static_root = (WEB_ROOT / "static").resolve()
            if static_root in target.parents:
                self._serve_file(target)
                return

        self._send(b"Not Found", "text/plain; charset=utf-8", HTTPStatus.NOT_FOUND)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HTML GUI sistem izleyici")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--min-read", type=float, default=5.0)
    p.add_argument("--min-write", type=float, default=5.0)
    p.add_argument("--max-cpu", type=float, default=90.0)
    p.add_argument("--max-ram", type=float, default=90.0)
    p.add_argument("--max-gpu", type=float, default=90.0)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    Handler.thresholds = Thresholds(
        min_disk_read_mb_s=args.min_read,
        min_disk_write_mb_s=args.min_write,
        max_cpu_percent=args.max_cpu,
        max_ram_percent=args.max_ram,
        max_gpu_percent=args.max_gpu,
    )
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"GUI hazır: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
