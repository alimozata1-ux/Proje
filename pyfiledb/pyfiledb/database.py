"""
Ana veritabani sinifi - Tablolari ve depolama arka ucunu yonetir.
"""

from typing import Any, Dict, List, Optional

from pyfiledb.storage import ExternalStorage, FileStorage, StorageBackend
from pyfiledb.table import Table


class Database:
    """
    PyFileDB Ana Veritabani Sinifi.

    Kullanim:
        # Dosya tabanli
        db = Database(storage=FileStorage("/path/to/data"))

        # Dis depolama tabanli
        db = Database(storage=ExternalStorage("/mnt/usb"))

        # Tablo islemleri
        users = db.table("users")
        users.insert({"ad": "Ali", "yas": 25})
    """

    def __init__(self, storage: StorageBackend):
        self._storage = storage
        self._tables: Dict[str, Table] = {}

    @classmethod
    def from_file(cls, path: str) -> "Database":
        """Dosya tabanli veritabani olustur."""
        return cls(storage=FileStorage(path))

    @classmethod
    def from_external(
        cls, device_path: str, db_folder: str = "pyfiledb_data"
    ) -> "Database":
        """Dis depolama aygitindan veritabani olustur."""
        return cls(storage=ExternalStorage(device_path, db_folder))

    def table(self, name: str) -> Table:
        """
        Bir tablo (koleksiyon) al veya olustur.
        Ayni isimli tablo zaten varsa mevcut olanı dondurur.
        """
        if name not in self._tables:
            self._tables[name] = Table(name, self._storage)
        return self._tables[name]

    def drop_table(self, name: str) -> bool:
        """Bir tabloyu sil."""
        if name in self._tables:
            self._tables[name].drop()
            del self._tables[name]
            return True
        # Tablo obje olarak yuklenmemis olabilir ama dosyasi var
        if self._storage.exists(name):
            self._storage.delete_collection(name)
            return True
        return False

    def list_tables(self) -> List[str]:
        """Mevcut tum tablolari listele."""
        return self._storage.list_collections()

    def get_storage_info(self) -> Dict[str, Any]:
        """Depolama bilgilerini getir."""
        return self._storage.get_storage_info()

    def get_stats(self) -> Dict[str, Any]:
        """Veritabani istatistiklerini getir."""
        tables = self.list_tables()
        total_records = 0
        table_stats = {}
        for table_name in tables:
            t = self.table(table_name)
            count = t.count()
            total_records += count
            table_stats[table_name] = {"record_count": count}

        storage_info = self.get_storage_info()
        return {
            "table_count": len(tables),
            "total_records": total_records,
            "tables": table_stats,
            "storage": storage_info,
        }

    def backup(self, target_storage: StorageBackend) -> int:
        """
        Veritabanini baska bir depolama arka ucune yedekle.
        Yedeklenen tablo sayisini dondurur.
        """
        tables = self.list_tables()
        for table_name in tables:
            data = self._storage.read(table_name)
            target_storage.write(table_name, data)
        return len(tables)

    def restore(self, source_storage: StorageBackend) -> int:
        """
        Baska bir depolama arka ucunden veritabanini geri yukle.
        Geri yuklenen tablo sayisini dondurur.
        """
        tables = source_storage.list_collections()
        for table_name in tables:
            data = source_storage.read(table_name)
            self._storage.write(table_name, data)
        return len(tables)
