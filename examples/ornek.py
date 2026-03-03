"""ASCII alias for `örnek.py` to avoid filename issues on some systems."""

from __future__ import annotations

import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "örnek.py")

if __name__ == "__main__":
    runpy.run_path(TARGET, run_name="__main__")
