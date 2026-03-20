"""GoblinPackege database application built on top of diydb.

Bu uygulama, diydb kütüphanesini gerçek bir "database uygulaması" olarak kullanır.
Opsiyonel olarak dış depolama aygıtı dizini verilebilir; bu durumda:
- `Files/` klasörü otomatik oluşturulur
- metadata `goblin_db.json` içinde tutulur
- eklenen dosyalar `Files/` altına yazılır
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Optional

from diydb import Field, open_db, query


class GoblinDatabaseApp:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.files_dir = self.root_dir / "Files"
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root_dir / "goblin_db.json"
        self.db = open_db(str(self.db_path))
        self._init_schema()

    def _init_schema(self) -> None:
        self.db.create_table(
            "files",
            [
                Field("name", str, required=True),
                Field("stored_path", str, required=True, unique=True),
                Field("size", int, required=True),
                Field("mime", str, required=False, default="application/octet-stream"),
                Field("owner", str, required=False, default="local-user"),
                Field("created_at", str, required=True),
                Field("favorite", bool, required=False, default=False),
            ],
            if_not_exists=True,
        )

    def add_file(self, source: Path, owner: str = "local-user", mime: Optional[str] = None) -> dict:
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"Source not found: {source}")

        destination = self.files_dir / source.name
        counter = 1
        while destination.exists():
            destination = self.files_dir / f"{source.stem} ({counter}){source.suffix}"
            counter += 1

        shutil.copy2(source, destination)

        rec = self.db.insert(
            "files",
            {
                "name": destination.name,
                "stored_path": str(destination.relative_to(self.root_dir)),
                "size": destination.stat().st_size,
                "mime": mime or "application/octet-stream",
                "owner": owner,
                "created_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "favorite": False,
            },
        )
        return rec

    def list_files(self, owner: Optional[str] = None) -> list[dict]:
        if owner:
            return self.db.find("files", query().where_eq("owner", owner).order("created_at", desc=True))
        return self.db.find("files", query().order("created_at", desc=True))

    def delete_file(self, file_id: str) -> bool:
        item = self.db.get("files", file_id)
        if not item:
            return False

        stored = self.root_dir / item["stored_path"]
        if stored.exists():
            stored.unlink()

        self.db.delete("files", file_id)
        return True

    def export_csv(self) -> str:
        return self.db.export_table_csv("files")

    def import_csv(self, csv_text: str) -> dict:
        return self.db.import_table_csv("files", csv_text, merge_by_pk=True, type_cast=True)

    def stats(self) -> dict:
        db_stats = self.db.stats()
        return {
            "table_count": db_stats.table_count,
            "record_count": db_stats.record_count,
            "db_size_bytes": db_stats.file_size_bytes,
            "files_dir": str(self.files_dir),
            "files_on_disk": sum(1 for _ in self.files_dir.glob("**/*") if _.is_file()),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GoblinPackege database app")
    parser.add_argument(
        "--root",
        default="./goblin_storage",
        help="Verilerin yazılacağı kök dizin (harici disk yolu verilebilir)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    add_cmd = sub.add_parser("add", help="Dosya ekle")
    add_cmd.add_argument("source", help="Eklenecek dosya yolu")
    add_cmd.add_argument("--owner", default="local-user")
    add_cmd.add_argument("--mime", default=None)

    list_cmd = sub.add_parser("list", help="Dosyaları listele")
    list_cmd.add_argument("--owner", default=None)

    delete_cmd = sub.add_parser("delete", help="ID ile dosya sil")
    delete_cmd.add_argument("id")

    sub.add_parser("stats", help="İstatistikleri göster")
    sub.add_parser("export-csv", help="CSV yazdır")

    import_cmd = sub.add_parser("import-csv", help="CSV dosyasından içe aktar")
    import_cmd.add_argument("csv_file")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = GoblinDatabaseApp(Path(args.root))

    if args.command == "add":
        rec = app.add_file(Path(args.source), owner=args.owner, mime=args.mime)
        print(json.dumps(rec, indent=2, ensure_ascii=False))
        return

    if args.command == "list":
        rows = app.list_files(owner=args.owner)
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return

    if args.command == "delete":
        ok = app.delete_file(args.id)
        print("deleted" if ok else "not-found")
        return

    if args.command == "stats":
        print(json.dumps(app.stats(), indent=2, ensure_ascii=False))
        return

    if args.command == "export-csv":
        print(app.export_csv())
        return

    if args.command == "import-csv":
        payload = Path(args.csv_file).read_text(encoding="utf-8")
        print(json.dumps(app.import_csv(payload), indent=2, ensure_ascii=False))
        return


if __name__ == "__main__":
    main()
