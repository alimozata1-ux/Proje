"""GoblinPackege database application built on top of diydb.

Özellikler:
- CLI modunda dosya metadata yönetimi
- GUI (tkinter) modunda temel kullanım ekranı
- Opsiyonel dış depolama kök yolu (`--root`) ve otomatik `Files/` klasörü
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from diydb import Field, open_db, query

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
except Exception:  # noqa: BLE001
    tk = None
    filedialog = None
    messagebox = None
    ttk = None


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
                "created_at": datetime.utcnow().isoformat() + "Z",
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
            "files_on_disk": sum(1 for item in self.files_dir.glob("**/*") if item.is_file()),
        }


class GoblinDatabaseGUI:
    def __init__(self, app: GoblinDatabaseApp):
        if tk is None or ttk is None:
            raise RuntimeError("Tkinter bu ortamda mevcut değil")

        self.app = app
        self.root = tk.Tk()
        self.root.title("Goblin Database GUI")
        self.root.geometry("900x560")

        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=tk.X)

        self.info_label = ttk.Label(top, text=f"Kök: {self.app.root_dir}")
        self.info_label.pack(side=tk.LEFT)

        ttk.Button(top, text="Dosya Ekle", command=self.add_file_dialog).pack(side=tk.RIGHT, padx=4)
        ttk.Button(top, text="CSV İçe Aktar", command=self.import_csv_dialog).pack(side=tk.RIGHT, padx=4)
        ttk.Button(top, text="CSV Dışa Aktar", command=self.export_csv_dialog).pack(side=tk.RIGHT, padx=4)
        ttk.Button(top, text="Yenile", command=self.refresh).pack(side=tk.RIGHT, padx=4)

        self.tree = ttk.Treeview(
            self.root,
            columns=("id", "name", "owner", "size", "created"),
            show="headings",
            height=20,
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Dosya")
        self.tree.heading("owner", text="Owner")
        self.tree.heading("size", text="Boyut")
        self.tree.heading("created", text="Oluşturulma")
        self.tree.column("id", width=180)
        self.tree.column("name", width=240)
        self.tree.column("owner", width=120)
        self.tree.column("size", width=90)
        self.tree.column("created", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill=tk.X)
        ttk.Button(bottom, text="Seçileni Sil", command=self.delete_selected).pack(side=tk.LEFT)
        self.stats_label = ttk.Label(bottom, text="")
        self.stats_label.pack(side=tk.RIGHT)

        self.refresh()

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in self.app.list_files():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row.get("id", ""),
                    row.get("name", ""),
                    row.get("owner", ""),
                    row.get("size", 0),
                    row.get("created_at", ""),
                ),
            )

        stats = self.app.stats()
        self.stats_label.config(text=f"Kayıt: {stats['record_count']} • Disk: {stats['db_size_bytes']} byte")

    def add_file_dialog(self) -> None:
        path = filedialog.askopenfilename(title="Eklenecek dosyayı seç")
        if not path:
            return
        try:
            self.app.add_file(Path(path))
            self.refresh()
            messagebox.showinfo("Başarılı", "Dosya eklendi")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Hata", str(exc))

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        file_id = values[0]
        if not messagebox.askyesno("Onay", "Seçili dosya silinsin mi?"):
            return
        ok = self.app.delete_file(file_id)
        if ok:
            self.refresh()
            messagebox.showinfo("Bilgi", "Dosya silindi")
        else:
            messagebox.showwarning("Bilgi", "Dosya bulunamadı")

    def export_csv_dialog(self) -> None:
        target = filedialog.asksaveasfilename(
            title="CSV kaydet",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("All", "*.*")],
        )
        if not target:
            return
        Path(target).write_text(self.app.export_csv(), encoding="utf-8")
        messagebox.showinfo("Başarılı", "CSV dışa aktarıldı")

    def import_csv_dialog(self) -> None:
        source = filedialog.askopenfilename(title="CSV seç", filetypes=[("CSV", "*.csv"), ("All", "*.*")])
        if not source:
            return
        payload = Path(source).read_text(encoding="utf-8")
        result = self.app.import_csv(payload)
        self.refresh()
        messagebox.showinfo("İçe Aktarım", f"Eklendi: {result['inserted']} • Güncellendi: {result['updated']}")

    def run(self) -> None:
        self.root.mainloop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GoblinPackege database app")
    parser.add_argument(
        "--root",
        default="./goblin_storage",
        help="Verilerin yazılacağı kök dizin (harici disk yolu verilebilir)",
    )
    parser.add_argument("--gui", action="store_true", help="GUI modunda başlat")

    sub = parser.add_subparsers(dest="command", required=False)

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


def run_cli(app: GoblinDatabaseApp, args: argparse.Namespace) -> None:
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

    print("Komut verilmedi.")


def main() -> None:
    args = parse_args()
    app = GoblinDatabaseApp(Path(args.root))

    should_try_gui = args.gui or args.command is None
    if should_try_gui:
        if tk is None:
            print("GUI başlatılamadı: tkinter bu ortamda mevcut değil.")
            if args.command is None:
                print("CLI kullanımı için bir komut verin (örn: stats, list, add).")
                return
        else:
            try:
                GoblinDatabaseGUI(app).run()
                return
            except Exception as exc:  # noqa: BLE001
                print(f"GUI başlatılamadı: {exc}")
                if args.command is None:
                    print("CLI kullanımı için bir komut verin (örn: stats, list, add).")
                    return

    run_cli(app, args)


if __name__ == "__main__":
    main()
