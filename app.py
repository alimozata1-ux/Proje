from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
DB_FILE = UPLOAD_FOLDER / "photos.json"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_UPLOAD_BYTES = 8 * 1024 * 1024


@dataclass
class Photo:
    id: str
    original_name: str
    saved_name: str
    extension: str
    file_size: int
    uploaded_at: str
    favorite: bool = False


class PhotoRepository:
    def __init__(self, db_file: Path) -> None:
        self.db_file = db_file
        self.db_file.parent.mkdir(exist_ok=True)
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

    def get(self, photo_id: str) -> Photo | None:
        for item in self._read():
            if item["id"] == photo_id:
                return Photo(**item)
        return None

    def add(self, photo: Photo) -> None:
        data = self._read()
        data.append(asdict(photo))
        self._write(data)

    def update(self, updated: Photo) -> None:
        data = self._read()
        new_data = [asdict(updated) if item["id"] == updated.id else item for item in data]
        self._write(new_data)

    def remove(self, photo_id: str) -> Photo | None:
        data = self._read()
        target = None
        kept = []
        for item in data:
            if item["id"] == photo_id:
                target = Photo(**item)
            else:
                kept.append(item)
        if target:
            self._write(kept)
        return target


app = Flask(__name__)
app.secret_key = "gelistirme-icin-degistir"
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
UPLOAD_FOLDER.mkdir(exist_ok=True)

repo = PhotoRepository(DB_FILE)


def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def query_photos(photos: list[Photo], q: str, ext: str, sort: str) -> list[Photo]:
    result = photos
    if q:
        q_lower = q.lower()
        result = [p for p in result if q_lower in p.original_name.lower()]
    if ext:
        result = [p for p in result if p.extension == ext.lower()]

    if sort == "name":
        result.sort(key=lambda p: p.original_name.lower())
    elif sort == "size":
        result.sort(key=lambda p: p.file_size, reverse=True)
    elif sort == "favorite":
        result.sort(key=lambda p: (not p.favorite, p.uploaded_at), reverse=False)
    else:
        result.sort(key=lambda p: p.uploaded_at, reverse=True)

    return result


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    ext = request.args.get("ext", "").strip().lower()
    sort = request.args.get("sort", "latest").strip().lower()

    photos = query_photos(repo.all(), q=q, ext=ext, sort=sort)
    stats = {
        "count": len(photos),
        "favorites": sum(1 for p in photos if p.favorite),
        "total_size": format_bytes(sum(p.file_size for p in photos)),
    }
    return render_template("index.html", photos=photos, stats=stats, q=q, ext=ext, sort=sort)


@app.route("/upload", methods=["POST"])
def upload_photo():
    if "photo" not in request.files:
        flash("Dosya alanı bulunamadı.")
        return redirect(url_for("index"))

    photo_file = request.files["photo"]
    if photo_file.filename == "":
        flash("Lütfen bir fotoğraf seç.")
        return redirect(url_for("index"))

    if not is_allowed_file(photo_file.filename):
        flash("Sadece png, jpg, jpeg, gif veya webp yükleyebilirsin.")
        return redirect(url_for("index"))

    original_name = secure_filename(photo_file.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    photo_id = uuid4().hex
    saved_name = f"{photo_id}.{ext}"

    path = UPLOAD_FOLDER / saved_name
    photo_file.save(path)

    record = Photo(
        id=photo_id,
        original_name=original_name,
        saved_name=saved_name,
        extension=ext,
        file_size=path.stat().st_size,
        uploaded_at=datetime.utcnow().isoformat(timespec="seconds"),
    )
    repo.add(record)

    flash("Fotoğraf başarıyla yüklendi.")
    return redirect(url_for("index"))


@app.route("/photo/<photo_id>")
def photo_detail(photo_id: str):
    photo = repo.get(photo_id)
    if not photo:
        flash("Fotoğraf bulunamadı.")
        return redirect(url_for("index"))
    return render_template("photo_detail.html", photo=photo, readable_size=format_bytes(photo.file_size))


@app.route("/photo/<photo_id>/favorite", methods=["POST"])
def toggle_favorite(photo_id: str):
    photo = repo.get(photo_id)
    if not photo:
        flash("Fotoğraf bulunamadı.")
        return redirect(url_for("index"))

    photo.favorite = not photo.favorite
    repo.update(photo)
    flash("Favori durumu güncellendi.")
    return redirect(url_for("index"))


@app.route("/photo/<photo_id>/delete", methods=["POST"])
def delete_photo(photo_id: str):
    photo = repo.remove(photo_id)
    if not photo:
        flash("Silinecek fotoğraf bulunamadı.")
        return redirect(url_for("index"))

    image_path = UPLOAD_FOLDER / photo.saved_name
    if image_path.exists():
        image_path.unlink()
    flash("Fotoğraf silindi.")
    return redirect(url_for("index"))


@app.route("/uploads/<path:filename>")
def uploaded_file(filename: str):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/api/photos")
def list_photos_api():
    photos = [asdict(photo) for photo in repo.all()]
    return jsonify({"count": len(photos), "photos": photos})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
