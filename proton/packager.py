from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _runner_template(source: str, plugin_dir: str | None, sandbox: bool) -> str:
    return f'''#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())
sys.path.insert(0, str(Path(__file__).resolve().parent))

from proton.interpreter import ProtonInterpreter

SOURCE = {source!r}

def main() -> None:
    interp = ProtonInterpreter(plugin_dir={plugin_dir!r})
    if {sandbox!r}:
        interp.context.sandbox.enabled = True
    result = interp.run(SOURCE)
    if result is not None:
        print(result)

if __name__ == "__main__":
    main()
'''


def build_runner(pt_path: str, output_py: str, plugin_dir: str | None = "plugins", sandbox: bool = False) -> Path:
    src = Path(pt_path).read_text(encoding="utf-8")
    out = Path(output_py)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_runner_template(src, plugin_dir=plugin_dir, sandbox=sandbox), encoding="utf-8")
    out.chmod(0o755)
    return out


def build_executable(pt_path: str, output_name: str, plugin_dir: str | None = "plugins", sandbox: bool = False) -> Path:
    py_path = Path(f"{output_name}.py")
    build_runner(pt_path=pt_path, output_py=str(py_path), plugin_dir=plugin_dir, sandbox=sandbox)
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        output_name,
        str(py_path),
    ]
    subprocess.run(cmd, check=True)
    return Path("dist") / output_name
