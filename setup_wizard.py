#!/usr/bin/env python3
"""Kurulum sihirbazı: bag_tool için temel ayarlar."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".bag_tool_config.json"


def ask(prompt: str, default: str) -> str:
    raw = input(f"{prompt} [{default}]: ").strip()
    return raw or default


def main() -> int:
    print("=== BAG Kurulum Sihirbazı ===")
    print("Bu sihirbaz varsayılan ayarları kaydeder.\n")

    default_output = ask("Varsayılan çıktı klasörü", str(Path.cwd()))
    auto_extension = ask(".bag uzantısını otomatik ekle? (yes/no)", "yes").lower() in {"yes", "y", "evet", "e"}
    delete_confirm = ask("Silmeden önce ekstra onay iste? (yes/no)", "yes").lower() in {"yes", "y", "evet", "e"}

    config = {
        "default_output": default_output,
        "auto_extension": auto_extension,
        "delete_confirm": delete_confirm,
    }

    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nKurulum tamamlandı. Konfigürasyon dosyası: {CONFIG_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
