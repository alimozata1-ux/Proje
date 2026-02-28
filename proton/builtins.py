from __future__ import annotations

import asyncio
import base64
import csv
import hashlib
import json
import math
import os
import shutil
import signal
import sqlite3
import subprocess
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import request

from .sandbox import parse_sandbox_args


def _split_args(raw: str) -> list[str]:
    return [p for p in raw.split() if p]


def _eval(raw: str, ctx) -> Any:
    return ctx.eval_expr(raw)


def _register_aliases(registry, names, handler):
    for n in names:
        registry.register(n, handler)


def register_builtin_commands(registry) -> None:
    def unsupported(name: str):
        def _handler(args: str, ctx):
            return {"command": name, "args": args, "status": "stub"}
        return _handler

    registry.register("@", lambda a, c: print(_eval(a, c)))
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

    registry.register("mk>", lambda a, c: Path(a.strip().strip('"')).touch())
    registry.register("del>", lambda a, c: Path(a.strip().strip('"')).unlink(missing_ok=True))
    registry.register("dir>", lambda a, c: os.listdir(a.strip().strip('"') or "."))
    registry.register("r<", lambda a, c: Path(a.strip().strip('"')).read_text())
    registry.register("w>", lambda a, c: Path(_split_args(a)[0].strip('"')).write_text(" ".join(_split_args(a)[1:])))
    registry.register("append>", lambda a, c: Path(_split_args(a)[0].strip('"')).open("a").write(" ".join(_split_args(a)[1:])))
    registry.register("copy>", lambda a, c: shutil.copy(_split_args(a)[0].strip('"'), _split_args(a)[1].strip('"')))
    registry.register("move>", lambda a, c: shutil.move(_split_args(a)[0].strip('"'), _split_args(a)[1].strip('"')))
    registry.register("size>", lambda a, c: Path(a.strip().strip('"')).stat().st_size)
    registry.register("perm>", lambda a, c: oct(Path(a.strip().strip('"')).stat().st_mode))

    def shell(args: str, ctx):
        ctx.sandbox.ensure_shell()
        cmd = args.strip().strip('"')
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {"code": res.returncode, "out": res.stdout.strip(), "err": res.stderr.strip()}

    _register_aliases(registry, ["sh:", "sh>", "sh!", "sys:"], shell)
    registry.register("kill>", lambda a, c: os.kill(int(a.strip()), signal.SIGTERM))
    registry.register("proc?>", lambda a, c: subprocess.run("ps -ef", shell=True, capture_output=True, text=True).stdout)
    registry.register("cpu?>", lambda a, c: os.getloadavg())
    registry.register("ram?>", lambda a, c: shutil.disk_usage("/").used)
    registry.register("disk?>", lambda a, c: shutil.disk_usage("/"))
    registry.register("env>", lambda a, c: dict(os.environ))

    def get_url(args: str, ctx):
        ctx.sandbox.ensure_network()
        return request.urlopen(args.strip().strip('"')).read().decode()

    registry.register("ping>", unsupported("ping>"))
    registry.register("get>", get_url)
    registry.register("post>", unsupported("post>"))
    registry.register("port?>", unsupported("port?>"))
    registry.register("ip?>", unsupported("ip?>"))
    registry.register("dns?>", unsupported("dns?>"))

    registry.register("hash>", lambda a, c: hashlib.sha256(a.encode()).hexdigest())
    registry.register("enc>", lambda a, c: base64.b64encode(a.encode()).decode())
    registry.register("dec>", lambda a, c: base64.b64decode(a.encode()).decode())
    registry.register("rand>", lambda a, c: os.urandom(int(a.strip() or "8")).hex())
    registry.register("uuid>", lambda a, c: str(uuid.uuid4()))
    registry.register("sandbox>", lambda a, c: setattr(c, "sandbox", parse_sandbox_args(a)) or c.sandbox.enabled)
    registry.register("scan>", unsupported("scan>"))
    registry.register("firewall>", unsupported("firewall>"))
    registry.register("sign>", unsupported("sign>"))
    registry.register("verify>", unsupported("verify>"))
    registry.register("vault>", unsupported("vault>"))

    registry.register("now>", lambda a, c: datetime.now().isoformat())
    registry.register("wait>", lambda a, c: time.sleep(float(a.strip() or "0")))
    registry.register("t:", lambda a, c: time.time())
    registry.register("timer>", unsupported("timer>"))
    registry.register("date>", lambda a, c: datetime.now().date().isoformat())

    registry.register("py:", lambda a, c: exec(a, c.globals, c.locals))
    registry.register("pip>", lambda a, c: shell(f"python -m pip {a}", c))
    registry.register("venv>", lambda a, c: shell(f"python -m venv {a}", c))

    registry.register("push>", lambda a, c: _eval(_split_args(a)[0], c).append(_eval(_split_args(a)[1], c)))
    registry.register("pop>", lambda a, c: _eval(a, c).pop())
    registry.register("sort>", lambda a, c: sorted(_eval(a, c)))
    registry.register("map>", lambda a, c: list(map(c.eval_expr, _eval(a, c))))
    registry.register("filter>", lambda a, c: list(filter(c.eval_expr, _eval(a, c))))
    registry.register("reduce>", unsupported("reduce>"))
    registry.register("json>", lambda a, c: json.loads(a))
    registry.register("csv>", lambda a, c: list(csv.reader(a.splitlines())))
    registry.register("stream>", unsupported("stream>"))
    registry.register("pipe>", unsupported("pipe>"))
    registry.register("chunk>", unsupported("chunk>"))
    registry.register("compress>", unsupported("compress>"))
    registry.register("decompress>", unsupported("decompress>"))
    registry.register("index>", unsupported("index>"))

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
        "debug>", "trace>", "profile>", "doc>", "test>", "build>",
        "match:", "if:", "elif:", "else:", "for:", "while:", "break>", "cont>",
        "f->", "T->", "bg>", "every>", "async->", "await>",
    ]:
        registry.register(name, unsupported(name))

    def spawn_thread(args: str, ctx):
        fn = ctx.locals.get(args.strip())
        if callable(fn):
            t = threading.Thread(target=fn, daemon=True)
            t.start()
            return t
        raise ValueError(f"Unknown function for thread: {args}")

    registry.register("T->", spawn_thread)
    registry.register("bg>", spawn_thread)

    async def _await_value(value):
        if asyncio.iscoroutine(value):
            return await value
        return value

    registry.register("await>", lambda a, c: asyncio.run(_await_value(_eval(a, c))))
