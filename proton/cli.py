from __future__ import annotations

import argparse
from pathlib import Path

from .interpreter import ProtonInterpreter, ProtonREPL
from .packager import build_executable, build_runner


def main() -> None:
    parser = argparse.ArgumentParser(description="Proton interpreter")
    parser.add_argument("script", nargs="?", help=".pt script path")
    parser.add_argument("--plugin-dir", default="plugins")
    parser.add_argument("--sandbox", action="store_true")
    parser.add_argument("--to-py", help="pt scriptini self-runner .py dosyasına dönüştür")
    parser.add_argument("--to-exe", help="pt scriptini tek dosya exe'ye dönüştür (PyInstaller gerekli)")
    args = parser.parse_args()

    if args.to_py:
        if not args.script:
            raise SystemExit("--to-py için script path gerekli")
        out = build_runner(args.script, args.to_py, plugin_dir=args.plugin_dir, sandbox=args.sandbox)
        print(f"Runner üretildi: {out}")
        return

    if args.to_exe:
        if not args.script:
            raise SystemExit("--to-exe için script path gerekli")
        out = build_executable(args.script, args.to_exe, plugin_dir=args.plugin_dir, sandbox=args.sandbox)
        print(f"Executable üretildi: {out}")
        return

    interp = ProtonInterpreter(plugin_dir=args.plugin_dir)
    if args.sandbox:
        interp.context.sandbox.enabled = True

    if args.script:
        source = Path(args.script).read_text(encoding="utf-8")
        result = interp.run(source)
        if result is not None:
            print(result)
    else:
        ProtonREPL(interp).loop()


if __name__ == "__main__":
    main()
