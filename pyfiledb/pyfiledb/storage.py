"""
Depolama arka uclari - Dosya sistemi ve dis depolama aygiti destegi.
"""

import json
import os
import shutil
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class StorageBackend(ABC):
    """Tum depolama arka uclari icin soyut temel sinif."""

    @abstractmethod
    def read(self, collection: str) -> List[Dict[str, Any]]:
        """Bir koleksiyondaki tum kayitlari oku."""
        ...

    @abstractmethod
    def write(self, collection: str, data: List[Dict[str, Any]]) -> None:
        """Bir koleksiyona veri yaz."""
        ...

    @abstractmethod
    def exists(self, collection: str) -> bool:
        """Koleksiyonun var olup olmadigini kontrol et."""
        ...

    @abstractmethod
    def delete_collection(self, collection: str) -> None:
        """Bir koleksiyonu sil."""
        ...

    @abstractmethod
    def list_collections(self) -> List[str]:
        """Mevcut tum koleksiyonlari listele."""
        ...

    @abstractmethod
    def get_storage_info(self) -> Dict[str, Any]:
        """Depolama bilgilerini dondur."""
        ...


class FileStorage(StorageBackend):
    """
    Yerel dosya sistemi tabanli depolama.
    Verileri JSON dosyalari olarak belirtilen dizine yazar.
    """

    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self._lock = threading.Lock()
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Temel dizinin var oldugundan emin ol."""
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _collection_path(self, collection: str) -> Path:
        """Koleksiyon dosyasinin yolunu dondur."""
        safe_name = collection.replace("/", "_").replace("\\", "_")
        return self.base_path / f"{safe_name}.json"

    def read(self, collection: str) -> List[Dict[str, Any]]:
        """JSON dosyasindan kayitlari oku."""
        with self._lock:
            file_path = self._collection_path(collection)
            if not file_path.exists():
                return []
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError):
                return []

    def write(self, collection: str, data: List[Dict[str, Any]]) -> None:
        """Kayitlari JSON dosyasina yaz."""
        with self._lock:
            file_path = self._collection_path(collection)
            self._ensure_directory()
            temp_path = file_path.with_suffix(".tmp")
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                temp_path.replace(file_path)
            except IOError:
                if temp_path.exists():
                    temp_path.unlink()
                raise

    def exists(self, collection: str) -> bool:
        """Koleksiyon dosyasinin var olup olmadigini kontrol et."""
        return self._collection_path(collection).exists()

    def delete_collection(self, collection: str) -> None:
        """Koleksiyon dosyasini sil."""
        with self._lock:
            file_path = self._collection_path(collection)
            if file_path.exists():
                file_path.unlink()

    def list_collections(self) -> List[str]:
        """Mevcut koleksiyonlari listele."""
        if not self.base_path.exists():
            return []
        return [f.stem for f in self.base_path.glob("*.json")]

    def get_storage_info(self) -> Dict[str, Any]:
        """Dosya depolama bilgilerini dondur."""
        total_size = 0
        file_count = 0
        if self.base_path.exists():
            for f in self.base_path.glob("*.json"):
                total_size += f.stat().st_size
                file_count += 1

        disk_usage = shutil.disk_usage(self.base_path)
        return {
            "type": "file",
            "base_path": str(self.base_path),
            "total_size_bytes": total_size,
            "file_count": file_count,
            "disk_total": disk_usage.total,
            "disk_used": disk_usage.used,
            "disk_free": disk_usage.free,
        }


class ExternalStorage(StorageBackend):
    """
    Dis depolama aygiti tabanli depolama (USB, SD kart, harici disk vb.)
    Belirtilen mount noktasina veya aygit yoluna veri yazar.
    """

    def __init__(self, device_path: str, db_folder: str = "pyfiledb_data"):
        self.device_path = Path(device_path).resolve()
        self.db_folder = db_folder
        self.base_path = self.device_path / db_folder
        self._lock = threading.Lock()
        self._validate_device()
        self._ensure_directory()

    def _validate_device(self) -> None:
        """Dis depolama aygitinin erisilebilir oldugundan emin ol."""
        if not self.device_path.exists():
            raise FileNotFoundError(
                f"Dis depolama aygiti bulunamadi: {self.device_path}"
            )
        if not os.access(self.device_path, os.W_OK):
            raise PermissionError(
                f"Dis depolama aygitina yazma izni yok: {self.device_path}"
            )

    def _ensure_directory(self) -> None:
        """Veritabani klasorunun var oldugundan emin ol."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        # Meta dosyasi olustur
        meta_file = self.base_path / ".pyfiledb_meta.json"
        if not meta_file.exists():
            meta = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "device_path": str(self.device_path),
            }
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

    def _collection_path(self, collection: str) -> Path:
        """Koleksiyon dosyasinin yolunu dondur."""
        safe_name = collection.replace("/", "_").replace("\\", "_")
        return self.base_path / f"{safe_name}.json"

    def read(self, collection: str) -> List[Dict[str, Any]]:
        """Dis depolamadan kayitlari oku."""
        with self._lock:
            file_path = self._collection_path(collection)
            if not file_path.exists():
                return []
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, IOError):
                return []

    def write(self, collection: str, data: List[Dict[str, Any]]) -> None:
        """Dis depolamaya kayitlari yaz."""
        with self._lock:
            self._validate_device()
            file_path = self._collection_path(collection)
            self._ensure_directory()
            temp_path = file_path.with_suffix(".tmp")
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
                temp_path.replace(file_path)
            except IOError:
                if temp_path.exists():
                    temp_path.unlink()
                raise

    def exists(self, collection: str) -> bool:
        """Koleksiyon dosyasinin var olup olmadigini kontrol et."""
        return self._collection_path(collection).exists()

    def delete_collection(self, collection: str) -> None:
        """Koleksiyon dosyasini sil."""
        with self._lock:
            file_path = self._collection_path(collection)
            if file_path.exists():
                file_path.unlink()

    def list_collections(self) -> List[str]:
        """Mevcut koleksiyonlari listele."""
        if not self.base_path.exists():
            return []
        return [
            f.stem
            for f in self.base_path.glob("*.json")
            if not f.name.startswith(".")
        ]

    def get_storage_info(self) -> Dict[str, Any]:
        """Dis depolama bilgilerini dondur."""
        total_size = 0
        file_count = 0
        if self.base_path.exists():
            for f in self.base_path.glob("*.json"):
                if not f.name.startswith("."):
                    total_size += f.stat().st_size
                    file_count += 1

        try:
            disk_usage = shutil.disk_usage(self.device_path)
            disk_info = {
                "disk_total": disk_usage.total,
                "disk_used": disk_usage.used,
                "disk_free": disk_usage.free,
            }
        except OSError:
            disk_info = {"disk_total": 0, "disk_used": 0, "disk_free": 0}

        return {
            "type": "external",
            "device_path": str(self.device_path),
            "base_path": str(self.base_path),
            "total_size_bytes": total_size,
            "file_count": file_count,
            **disk_info,
        }

    def is_device_connected(self) -> bool:
        """Dis depolama aygitinin hala bagli olup olmadigini kontrol et."""
        return self.device_path.exists() and os.access(self.device_path, os.R_OK)

    def sync(self) -> None:
        """Diskteki degisiklikleri senkronize et (flush)."""
        os.sync()
