#!/usr/bin/env python3
"""BAG archive utility.

A .bag file is a ZIP archive with an internal metadata file that can store
an optional password hash.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import secrets
import shutil
import sys
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

BAG_META_PATH = ".bag/metadata.json"
CONFIG_FILE = Path.home() / ".bag_tool_config.json"


def _load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def _build_meta(password: str | None) -> dict:
    if not password:
        return {"password_enabled": False}

    salt = secrets.token_hex(16)
    return {
        "password_enabled": True,
        "password": {
            "salt": salt,
            "hash": _hash_password(password, salt),
            "algorithm": "sha256",
        },
    }


def _read_meta(bag_file: Path) -> dict:
    with ZipFile(bag_file, "r") as zf:
        try:
            raw = zf.read(BAG_META_PATH).decode("utf-8")
        except KeyError:
            return {"password_enabled": False}
        return json.loads(raw)


def _verify_password(meta: dict, password: str) -> bool:
    if not meta.get("password_enabled"):
        return True

    pw = meta.get("password", {})
    salt = pw.get("salt", "")
    expected = pw.get("hash", "")
    return _hash_password(password, salt) == expected


def _replace_meta(bag_file: Path, new_meta: dict) -> None:
    with tempfile.TemporaryDirectory(prefix="bag-edit-") as td:
        td_path = Path(td)
        with ZipFile(bag_file, "r") as src:
            src.extractall(td_path)

        meta_path = td_path / BAG_META_PATH
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(new_meta, ensure_ascii=False, indent=2), encoding="utf-8")

        tmp_bag = bag_file.with_suffix(bag_file.suffix + ".tmp")
        with ZipFile(tmp_bag, "w", compression=ZIP_DEFLATED) as dst:
            for item in td_path.rglob("*"):
                if item.is_file():
                    arcname = item.relative_to(td_path)
                    dst.write(item, arcname.as_posix())
        tmp_bag.replace(bag_file)


def cmd_create(args: argparse.Namespace) -> int:
    config = _load_config()
    out = Path(args.output)
    auto_extension = config.get("auto_extension", True)
    if auto_extension and out.suffix != ".bag":
        out = out.with_suffix(".bag")

    paths = [Path(p) for p in args.inputs]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print(f"Hata: Dosyalar bulunamadı: {', '.join(missing)}", file=sys.stderr)
        return 1

    password = args.password
    if args.ask_password:
        p1 = getpass.getpass("Arşiv şifresi (boş bırakılabilir): ")
        p2 = getpass.getpass("Şifre tekrar: ")
        if p1 != p2:
            print("Hata: Şifreler eşleşmiyor.", file=sys.stderr)
            return 1
        password = p1

    with ZipFile(out, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr(BAG_META_PATH, json.dumps(_build_meta(password), ensure_ascii=False, indent=2))
        for source in paths:
            if source.is_file():
                zf.write(source, source.name)
            else:
                for child in source.rglob("*"):
                    if child.is_file():
                        zf.write(child, child.relative_to(source.parent))

    print(f"BAG oluşturuldu: {out}")
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    bag = Path(args.bag_file)
    target = Path(args.target)
    if not bag.exists():
        print(f"Hata: {bag} bulunamadı.", file=sys.stderr)
        return 1

    with ZipFile(bag, "r") as zf:
        zf.extractall(target)

    meta_file = target / BAG_META_PATH
    if meta_file.exists():
        meta_file.unlink()
        try:
            shutil.rmtree(meta_file.parent)
        except OSError:
            pass

    print(f"Arşiv çıkarıldı: {target}")
    return 0


def cmd_set_password(args: argparse.Namespace) -> int:
    bag = Path(args.bag_file)
    if not bag.exists():
        print(f"Hata: {bag} bulunamadı.", file=sys.stderr)
        return 1

    meta = _read_meta(bag)
    if meta.get("password_enabled"):
        old_pw = getpass.getpass("Mevcut şifre: ")
        if not _verify_password(meta, old_pw):
            print("Hata: Mevcut şifre yanlış.", file=sys.stderr)
            return 1

    new_pw = args.password
    if args.ask_password:
        p1 = getpass.getpass("Yeni şifre (boş = kaldır): ")
        p2 = getpass.getpass("Yeni şifre tekrar: ")
        if p1 != p2:
            print("Hata: Şifreler eşleşmiyor.", file=sys.stderr)
            return 1
        new_pw = p1

    _replace_meta(bag, _build_meta(new_pw))
    if new_pw:
        print("Şifre ayarlandı.")
    else:
        print("Şifre kaldırıldı.")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    config = _load_config()
    bag = Path(args.bag_file)
    if not bag.exists():
        print(f"Hata: {bag} bulunamadı.", file=sys.stderr)
        return 1

    meta = _read_meta(bag)
    if meta.get("password_enabled"):
        password = args.password or getpass.getpass("Silmek için şifre: ")
        if not _verify_password(meta, password):
            print("Hata: Şifre yanlış, dosya silinmedi.", file=sys.stderr)
            return 1

    if config.get("delete_confirm", True):
        answer = input(f"{bag} silinsin mi? (yes/no): ").strip().lower()
        if answer not in {"yes", "y", "evet", "e"}:
            print("Silme iptal edildi.")
            return 0

    bag.unlink()
    print(f"Silindi: {bag}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=".bag arşiv aracı")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Yeni .bag arşivi oluştur")
    p_create.add_argument("output", help="Çıktı .bag dosyası")
    p_create.add_argument("inputs", nargs="+", help="Arşive eklenecek dosya/klasörler")
    p_create.add_argument("--password", default=None, help="Arşiv parolası")
    p_create.add_argument("--ask-password", action="store_true", help="Şifreyi etkileşimli sor")
    p_create.set_defaults(func=cmd_create)

    p_extract = sub.add_parser("extract", help=".bag arşivi aç")
    p_extract.add_argument("bag_file")
    p_extract.add_argument("target", nargs="?", default=".", help="Hedef klasör")
    p_extract.set_defaults(func=cmd_extract)

    p_pw = sub.add_parser("set-password", help="Arşiv şifresi ekle/değiştir/kaldır")
    p_pw.add_argument("bag_file")
    p_pw.add_argument("--password", default=None, help="Yeni şifre (boşsa kaldırılır)")
    p_pw.add_argument("--ask-password", action="store_true", help="Yeni şifreyi etkileşimli sor")
    p_pw.set_defaults(func=cmd_set_password)

    p_del = sub.add_parser("delete", help="Arşivi sil")
    p_del.add_argument("bag_file")
    p_del.add_argument("--password", default=None, help="Şifreli arşiv için parola")
    p_del.set_defaults(func=cmd_delete)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
