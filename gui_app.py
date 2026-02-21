from __future__ import annotations

import json
import shutil
import tkinter as tk
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from uuid import uuid4

BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_FILE = UPLOAD_DIR / "photos.json"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


@dataclass
class Photo:
    id: str
    original_name: str
    saved_name: str
    extension: str
    file_size: int
    uploaded_at: str
    favorite: bool = False


class PhotoStore:
    def __init__(self, upload_dir: Path, db_file: Path) -> None:
        self.upload_dir = upload_dir
        self.db_file = db_file
        self.upload_dir.mkdir(exist_ok=True)
        if not self.db_file.exists():
            self._write([])

    def _read(self) -> list[dict]:
        with self.db_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: list[dict]) -> None:
        with self.db_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def all(self) -> list[Photo]:
        return [Photo(**item) for item in self._read()]

    def add_from_file(self, source_path: Path) -> Photo:
        ext = source_path.suffix.lower().lstrip(".")
        photo_id = uuid4().hex
        saved_name = f"{photo_id}.{ext}"
        dest = self.upload_dir / saved_name
        shutil.copy2(source_path, dest)

        photo = Photo(
            id=photo_id,
            original_name=source_path.name,
            saved_name=saved_name,
            extension=ext,
            file_size=dest.stat().st_size,
            uploaded_at=datetime.utcnow().isoformat(timespec="seconds"),
        )
        data = self._read()
        data.append(asdict(photo))
        self._write(data)
        return photo

    def toggle_favorite(self, photo_id: str) -> Photo | None:
        items = self._read()
        changed = None
        for item in items:
            if item["id"] == photo_id:
                item["favorite"] = not item.get("favorite", False)
                changed = Photo(**item)
                break
        if changed:
            self._write(items)
        return changed

    def delete(self, photo_id: str) -> Photo | None:
        items = self._read()
        target = None
        keep = []
        for item in items:
            if item["id"] == photo_id:
                target = Photo(**item)
            else:
                keep.append(item)
        if target:
            self._write(keep)
            file_path = self.upload_dir / target.saved_name
            if file_path.exists():
                file_path.unlink()
        return target


def human_size(size: int) -> str:
    unit_list = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in unit_list:
        if value < 1024 or unit == unit_list[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


class PhotoManagerGUI:
    def __init__(self, root: tk.Tk, store: PhotoStore) -> None:
        self.root = root
        self.store = store
        self.root.title("Fotoğraflar GUI")
        self.root.geometry("980x620")

        self.search_var = tk.StringVar(value="")
        self.ext_var = tk.StringVar(value="all")
        self.sort_var = tk.StringVar(value="latest")
        self.selected_photo_id: str | None = None

        self.preview_label: tk.Label | None = None
        self.tk_image = None

        self._build_layout()
        self.refresh_table()

    def _build_layout(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Button(top, text="Fotoğraf Ekle", command=self.upload_file).pack(side="left")
        ttk.Button(top, text="Favori Değiştir", command=self.toggle_selected_favorite).pack(side="left", padx=6)
        ttk.Button(top, text="Seçileni Sil", command=self.delete_selected).pack(side="left")

        ttk.Label(top, text="Ara:").pack(side="left", padx=(20, 4))
        search = ttk.Entry(top, textvariable=self.search_var, width=24)
        search.pack(side="left")
        search.bind("<KeyRelease>", lambda _: self.refresh_table())

        ttk.Label(top, text="Uzantı:").pack(side="left", padx=(10, 4))
        ext_menu = ttk.Combobox(top, textvariable=self.ext_var, values=["all", "png", "jpg", "jpeg", "gif", "webp"], width=8, state="readonly")
        ext_menu.pack(side="left")
        ext_menu.bind("<<ComboboxSelected>>", lambda _: self.refresh_table())

        ttk.Label(top, text="Sırala:").pack(side="left", padx=(10, 4))
        sort_menu = ttk.Combobox(top, textvariable=self.sort_var, values=["latest", "name", "size", "favorite"], width=10, state="readonly")
        sort_menu.pack(side="left")
        sort_menu.bind("<<ComboboxSelected>>", lambda _: self.refresh_table())

        middle = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        middle.pack(fill="both", expand=True)

        columns = ("id", "name", "ext", "size", "date", "fav")
        self.table = ttk.Treeview(middle, columns=columns, show="headings", height=18)
        for col, width in [("id", 210), ("name", 240), ("ext", 70), ("size", 90), ("date", 170), ("fav", 60)]:
            self.table.heading(col, text=col.upper())
            self.table.column(col, width=width, anchor="center")
        self.table.bind("<<TreeviewSelect>>", self.on_select)

        scrollbar = ttk.Scrollbar(middle, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

        right = ttk.Frame(middle, padding=(10, 0, 0, 0))
        right.pack(side="left", fill="both")

        self.info_var = tk.StringVar(value="Fotoğraf seçildiğinde detaylar burada görünür.")
        ttk.Label(right, text="Detaylar", font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(right, textvariable=self.info_var, wraplength=260, justify="left").pack(anchor="w", pady=(4, 10))

        self.preview_label = ttk.Label(right, text="Önizleme yok")
        self.preview_label.pack(anchor="w")

        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")
        self.stats_var = tk.StringVar(value="Toplam: 0 | Favori: 0 | Boyut: 0 B")
        ttk.Label(bottom, textvariable=self.stats_var).pack(side="left")

    def _filtered_sorted(self, photos: list[Photo]) -> list[Photo]:
        q = self.search_var.get().strip().lower()
        ext = self.ext_var.get()
        sort = self.sort_var.get()

        result = photos
        if q:
            result = [p for p in result if q in p.original_name.lower()]
        if ext != "all":
            result = [p for p in result if p.extension == ext]

        if sort == "name":
            result.sort(key=lambda p: p.original_name.lower())
        elif sort == "size":
            result.sort(key=lambda p: p.file_size, reverse=True)
        elif sort == "favorite":
            result.sort(key=lambda p: (not p.favorite, p.uploaded_at))
        else:
            result.sort(key=lambda p: p.uploaded_at, reverse=True)
        return result

    def refresh_table(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        photos = self._filtered_sorted(self.store.all())
        for photo in photos:
            self.table.insert(
                "",
                "end",
                iid=photo.id,
                values=(photo.id, photo.original_name, photo.extension.upper(), human_size(photo.file_size), photo.uploaded_at, "⭐" if photo.favorite else "-"),
            )

        favorite_count = sum(1 for p in photos if p.favorite)
        total_size = sum(p.file_size for p in photos)
        self.stats_var.set(f"Toplam: {len(photos)} | Favori: {favorite_count} | Boyut: {human_size(total_size)}")

    def upload_file(self) -> None:
        filetypes = [("Image Files", "*.png *.jpg *.jpeg *.gif *.webp")]
        selected = filedialog.askopenfilename(title="Fotoğraf seç", filetypes=filetypes)
        if not selected:
            return

        src = Path(selected)
        ext = src.suffix.lower().lstrip(".")
        if ext not in ALLOWED_EXTENSIONS:
            messagebox.showwarning("Hata", "Desteklenmeyen dosya uzantısı")
            return

        try:
            self.store.add_from_file(src)
            self.refresh_table()
            messagebox.showinfo("Başarılı", "Fotoğraf eklendi")
        except Exception as exc:
            messagebox.showerror("Hata", f"Yükleme başarısız: {exc}")

    def on_select(self, _event=None) -> None:
        selection = self.table.selection()
        if not selection:
            return
        self.selected_photo_id = selection[0]

        photo = next((p for p in self.store.all() if p.id == self.selected_photo_id), None)
        if not photo:
            return

        self.info_var.set(
            f"Ad: {photo.original_name}\n"
            f"Uzantı: {photo.extension.upper()}\n"
            f"Boyut: {human_size(photo.file_size)}\n"
            f"Yüklenme: {photo.uploaded_at}\n"
            f"Favori: {'Evet' if photo.favorite else 'Hayır'}"
        )

        self.show_preview(UPLOAD_DIR / photo.saved_name)

    def show_preview(self, image_path: Path) -> None:
        if not self.preview_label:
            return

        try:
            from PIL import Image, ImageTk  # type: ignore

            image = Image.open(image_path)
            image.thumbnail((260, 260))
            self.tk_image = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self.tk_image, text="")
        except Exception:
            self.preview_label.configure(text=f"Önizleme açılamadı:\n{image_path.name}", image="")

    def toggle_selected_favorite(self) -> None:
        if not self.selected_photo_id:
            messagebox.showwarning("Uyarı", "Önce bir fotoğraf seç")
            return
        updated = self.store.toggle_favorite(self.selected_photo_id)
        if not updated:
            messagebox.showwarning("Uyarı", "Fotoğraf bulunamadı")
            return
        self.refresh_table()

    def delete_selected(self) -> None:
        if not self.selected_photo_id:
            messagebox.showwarning("Uyarı", "Önce bir fotoğraf seç")
            return
        answer = messagebox.askyesno("Onay", "Seçili fotoğraf silinsin mi?")
        if not answer:
            return
        removed = self.store.delete(self.selected_photo_id)
        if not removed:
            messagebox.showwarning("Uyarı", "Fotoğraf bulunamadı")
            return
        self.selected_photo_id = None
        self.info_var.set("Fotoğraf seçildiğinde detaylar burada görünür.")
        if self.preview_label:
            self.preview_label.configure(image="", text="Önizleme yok")
        self.refresh_table()


def main() -> None:
    root = tk.Tk()
    store = PhotoStore(UPLOAD_DIR, DB_FILE)
    app = PhotoManagerGUI(root, store)
    root.mainloop()


if __name__ == "__main__":
    main()
