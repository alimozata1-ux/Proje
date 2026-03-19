#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from system_monitor import Thresholds, collect_snapshot

WEB_ROOT = Path(__file__).parent / "web"


class Handler(BaseHTTPRequestHandler):
    thresholds = Thresholds()

    def _send(self, body: bytes, content_type: str = "text/html; charset=utf-8", status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ["/", "/index.html"]:
            body = (WEB_ROOT / "index.html").read_bytes()
            self._send(body)
            return

        if self.path == "/api/snapshot":
            data = collect_snapshot(self.thresholds)
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self._send(body, content_type="application/json; charset=utf-8")
            return

        if self.path.startswith("/static/"):
            rel = self.path[len("/") :]
            target = Path(rel)
            full = Path(__file__).parent / target
            if full.exists() and full.is_file():
                ext = full.suffix.lower()
                mime = "image/svg+xml" if ext == ".svg" else "text/plain; charset=utf-8"
                self._send(full.read_bytes(), content_type=mime)
                return

        self._send(b"Not Found", content_type="text/plain; charset=utf-8", status=HTTPStatus.NOT_FOUND)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HTML GUI sistem izleyici")
    p.add_argument("--host", default="0.0.0.0")
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
