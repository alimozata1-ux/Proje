from __future__ import annotations

import argparse
from pathlib import Path

from .interpreter import ProtonInterpreter, ProtonREPL


def main() -> None:
    parser = argparse.ArgumentParser(description="Proton interpreter")
    parser.add_argument("script", nargs="?", help=".pt script path")
    parser.add_argument("--plugin-dir", default="plugins")
    parser.add_argument("--sandbox", action="store_true")
    args = parser.parse_args()

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
