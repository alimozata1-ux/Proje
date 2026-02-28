from __future__ import annotations

import asyncio
import base64
import csv
import gzip
import hashlib
import hmac
import json
import math
import os
import shutil
import signal
import socket
import sqlite3
import subprocess
import threading
import time
import uuid
from datetime import datetime
from functools import reduce
from pathlib import Path
from typing import Any
from urllib import parse, request

from .sandbox import parse_sandbox_args


def _split_args(raw: str) -> list[str]:
    return [p for p in raw.split() if p]


def _eval(raw: str, ctx) -> Any:
    return ctx.eval_expr(raw)


def _clean_path(raw: str) -> Path:
    return Path(raw.strip().strip('"').strip("'"))


def _ensure_path(raw: str, ctx) -> Path:
    path = _clean_path(raw)
    ctx.sandbox.ensure_path(path)
    return path


def _register_aliases(registry, names, handler):
    for n in names:
        registry.register(n, handler)


def _unsupported(name: str):
    def _handler(args: str, ctx):
        return {"command": name, "args": args, "status": "stub"}

    return _handler


def register_builtin_commands(registry) -> None:
    registry.register("@", lambda a, c: print(_eval(a, c) if a else ""))
    registry.register("!", lambda a, c: input(a.strip().strip('"')))
    registry.register("?", lambda a, c: bool(_eval(a, c)))
    registry.register("type>", lambda a, c: type(_eval(a, c)).__name__)
    registry.register("len>", lambda a, c: len(_eval(a, c)))

    registry.register("+:", lambda a, c: sum(_eval(x, c) for x in _split_args(a)))
    registry.register("-:", lambda a, c: _eval(_split_args(a)[0], c) - _eval(_split_args(a)[1], c))
    registry.register("*:", lambda a, c: math.prod(_eval(x, c) for x in _split_args(a)))
    registry.register("/:", lambda a, c: _eval(_split_args(a)[0], c) / _eval(_split_args(a)[1], c))
    registry.register("^:", lambda a, c: _eval(_split_args(a)[0], c) ** _eval(_split_args(a)[1], c))
    registry.register("%:", lambda a, c: _eval(_split_args(a)[0], c) % _eval(_split_args(a)[1], c))
    registry.register("abs>", lambda a, c: abs(_eval(a, c)))
    registry.register("round>", lambda a, c: round(_eval(a, c)))

    registry.register("mk>", lambda a, c: _ensure_path(a, c).touch())
    registry.register("del>", lambda a, c: _ensure_path(a, c).unlink(missing_ok=True))
    registry.register("dir>", lambda a, c: os.listdir(_ensure_path(a or '.', c)))
    registry.register("r<", lambda a, c: _ensure_path(a, c).read_text())

    def write_file(a: str, c):
        path_expr, data_expr = _eval(a, c)
        path = _ensure_path(repr(path_expr), c)
        path.write_text(str(data_expr))
        return str(path)

    def append_file(a: str, c):
        path_expr, data_expr = _eval(a, c)
        path = _ensure_path(repr(path_expr), c)
        with path.open("a", encoding="utf-8") as f:
            f.write(str(data_expr))
        return str(path)

    registry.register("w>", write_file)
    registry.register("append>", append_file)
    registry.register("copy>", lambda a, c: shutil.copy(*_eval(a, c)))
    registry.register("move>", lambda a, c: shutil.move(*_eval(a, c)))
    registry.register("size>", lambda a, c: _ensure_path(a, c).stat().st_size)
    registry.register("perm>", lambda a, c: oct(_ensure_path(a, c).stat().st_mode))

    def shell(args: str, ctx):
        ctx.sandbox.ensure_shell()
        cmd = args.strip().strip('"')
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {"code": res.returncode, "out": res.stdout.strip(), "err": res.stderr.strip()}

    def shell_print(args: str, ctx):
        payload = shell(args, ctx)
        if payload["out"]:
            print(payload["out"])
        if payload["err"]:
            print(payload["err"])
        return payload["code"]

    _register_aliases(registry, ["sh:", "sh>", "sys:"], shell)
    registry.register("sh!", shell_print)
    registry.register("kill>", lambda a, c: os.kill(int(a.strip()), signal.SIGTERM))
    registry.register("proc?>", lambda a, c: subprocess.run("ps -ef", shell=True, capture_output=True, text=True).stdout)
    registry.register("cpu?>", lambda a, c: os.getloadavg())
    registry.register("ram?>", lambda a, c: shell("free -m", c)["out"])
    registry.register("disk?>", lambda a, c: shutil.disk_usage("/"))
    registry.register("env>", lambda a, c: dict(os.environ))

    def get_url(args: str, ctx):
        ctx.sandbox.ensure_network()
        return request.urlopen(args.strip().strip('"')).read().decode()

    def post_url(args: str, ctx):
        ctx.sandbox.ensure_network()
        url, payload = _eval(args, ctx)
        data = parse.urlencode(payload).encode()
        req = request.Request(url, data=data)
        return request.urlopen(req).read().decode()

    def ping_host(args: str, ctx):
        ctx.sandbox.ensure_network()
        host = args.strip().strip('"')
        try:
            socket.gethostbyname(host)
            return True
        except socket.gaierror:
            return False

    registry.register("ping>", ping_host)
    registry.register("get>", get_url)
    registry.register("post>", post_url)
    def port_open(a: str, c):
        host, port = _eval(a, c)
        c.sandbox.ensure_network()
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            return False

    registry.register("port?>", port_open)
    registry.register("ip?>", lambda a, c: socket.gethostbyname(socket.gethostname()))
    registry.register("dns?>", lambda a, c: socket.gethostbyname_ex(a.strip().strip('"')))

    registry.register("hash>", lambda a, c: hashlib.sha256(str(_eval(a, c)).encode()).hexdigest())
    registry.register("enc>", lambda a, c: base64.b64encode(str(_eval(a, c)).encode()).decode())
    registry.register("dec>", lambda a, c: base64.b64decode(str(_eval(a, c)).encode()).decode())
    registry.register("rand>", lambda a, c: os.urandom(int(a.strip() or "8")).hex())
    registry.register("uuid>", lambda a, c: str(uuid.uuid4()))
    registry.register("sandbox>", lambda a, c: setattr(c, "sandbox", parse_sandbox_args(a)) or c.sandbox.enabled)
    registry.register("scan>", _unsupported("scan>"))
    registry.register("firewall>", _unsupported("firewall>"))

    def sign(args: str, ctx):
        secret, msg = _eval(args, ctx)
        return hmac.new(str(secret).encode(), str(msg).encode(), hashlib.sha256).hexdigest()

    def verify(args: str, ctx):
        secret, msg, signature = _eval(args, ctx)
        expected = hmac.new(str(secret).encode(), str(msg).encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, str(signature))

    def vault(args: str, ctx):
        if not hasattr(ctx, "vault"):
            ctx.vault = {}
        action, key, *rest = _eval(args, ctx)
        if action == "set":
            ctx.vault[key] = rest[0]
            return True
        if action == "get":
            return ctx.vault.get(key)
        if action == "del":
            return ctx.vault.pop(key, None)
        raise ValueError("vault action must be set/get/del")

    registry.register("sign>", sign)
    registry.register("verify>", verify)
    registry.register("vault>", vault)

    registry.register("now>", lambda a, c: datetime.now().isoformat())
    registry.register("wait>", lambda a, c: time.sleep(float(a.strip() or "0")))
    registry.register("t:", lambda a, c: time.time())

    def timer(args: str, ctx):
        start = time.perf_counter()
        value = _eval(args, ctx)
        end = time.perf_counter()
        return {"value": value, "elapsed_ms": round((end - start) * 1000, 3)}

    registry.register("timer>", timer)
    registry.register("date>", lambda a, c: datetime.now().date().isoformat())

    registry.register("py:", lambda a, c: exec(a, c.globals, c.locals))
    registry.register("pip>", lambda a, c: shell(f"python -m pip {a}", c))
    registry.register("venv>", lambda a, c: shell(f"python -m venv {a}", c))

    registry.register("push>", lambda a, c: (_eval(a, c)[0].append(_eval(a, c)[1]), _eval(a, c)[0])[1])
    registry.register("pop>", lambda a, c: _eval(a, c).pop())
    registry.register("sort>", lambda a, c: sorted(_eval(a, c)))
    registry.register("map>", lambda a, c: list(map(*_eval(a, c))))
    registry.register("filter>", lambda a, c: list(filter(*_eval(a, c))))
    registry.register("reduce>", lambda a, c: reduce(*_eval(a, c)))
    registry.register("json>", lambda a, c: json.loads(a) if a.strip().startswith("{") else json.dumps(_eval(a, c), ensure_ascii=False))
    registry.register("csv>", lambda a, c: list(csv.reader(a.splitlines())))
    registry.register("stream>", lambda a, c: iter(_eval(a, c)))
    registry.register("pipe>", lambda a, c: reduce(lambda v, fn: fn(v), _eval(a, c)[1], _eval(a, c)[0]))
    registry.register("chunk>", lambda a, c: [_eval(a, c)[0][i:i + _eval(a, c)[1]] for i in range(0, len(_eval(a, c)[0]), _eval(a, c)[1])])
    registry.register("compress>", lambda a, c: base64.b64encode(gzip.compress(str(_eval(a, c)).encode())).decode())
    registry.register("decompress>", lambda a, c: gzip.decompress(base64.b64decode(str(_eval(a, c)).encode())).decode())
    registry.register("index>", lambda a, c: {v: i for i, v in enumerate(_eval(a, c))})

    registry.register("db.connect>", lambda a, c: setattr(c, "db", sqlite3.connect(a.strip().strip('"'))) or "ok")
    registry.register("db.query>", lambda a, c: c.db.execute(a).fetchall())
    registry.register("db.insert>", lambda a, c: c.db.execute(a) or c.db.commit())
    registry.register("db.update>", lambda a, c: c.db.execute(a) or c.db.commit())
    registry.register("db.delete>", lambda a, c: c.db.execute(a) or c.db.commit())
    registry.register("db.close>", lambda a, c: c.db.close())

    for name in [
        "serve>", "route>", "ws>", "api>", "auth>", "cookie>",
        "ai.load>", "ai.run>", "tensor>", "train>", "predict>", "viz>", "embed>", "vector>", "cluster.ai>", "detect>", "nlp>", "gen>",
        "gpio>", "sensor>", "serial>", "usb>", "bt>", "wifi>",
        "node>", "cluster>", "sync>", "replicate>", "broadcast>", "rpc>",
        "inspect>", "reflect>", "macro>", "inject>", "override>",
        "doc>", "test>", "build>",
        "match:", "if:", "elif:", "else:", "for:", "while:", "break>", "cont>",
        "f->", "async->",
    ]:
        registry.register(name, _unsupported(name))

    def spawn_thread(args: str, ctx):
        fn = ctx.locals.get(args.strip())
        if callable(fn):
            t = threading.Thread(target=fn, daemon=True)
            t.start()
            return t.name
        raise ValueError(f"Unknown function for thread: {args}")

    def every(args: str, ctx):
        sec, fn_name = _eval(args, ctx)
        fn = ctx.locals.get(fn_name) if isinstance(fn_name, str) else fn_name
        if not callable(fn):
            raise ValueError("every> requires callable")

        def runner():
            while True:
                fn()
                time.sleep(float(sec))

        t = threading.Thread(target=runner, daemon=True)
        t.start()
        return t.name

    registry.register("T->", spawn_thread)
    registry.register("bg>", spawn_thread)
    registry.register("every>", every)

    async def _await_value(value):
        if asyncio.iscoroutine(value):
            return await value
        return value

    registry.register("await>", lambda a, c: asyncio.run(_await_value(_eval(a, c))))

    registry.register("debug>", lambda a, c: {"locals": sorted(c.locals.keys()), "globals": sorted(c.globals.keys())})
    registry.register("trace>", lambda a, c: print(f"[trace] {a}"))
    registry.register("profile>", timer)

    # custom additional commands
    registry.register("calc>", lambda a, c: _eval(a, c))
    registry.register("retry>", lambda a, c: _retry(_eval(a, c)))


def _retry(payload):
    fn, tries, delay = payload
    last_err = None
    for _ in range(int(tries)):
        try:
            return fn()
        except Exception as exc:
            last_err = exc
            time.sleep(float(delay))
    raise RuntimeError(f"retry failed: {last_err}")
