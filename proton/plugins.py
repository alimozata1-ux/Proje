from __future__ import annotations

import importlib.util
from pathlib import Path


def load_plugins(plugin_dir: Path, registry) -> list[str]:
    loaded = []
    if not plugin_dir.exists():
        return loaded
    for path in plugin_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "register"):
                mod.register(registry)
                loaded.append(path.name)
    return loaded
