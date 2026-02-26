"""
Tablo (koleksiyon) sinifi - CRUD islemleri.
"""

import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from pyfiledb.storage import StorageBackend


class Table:
    """
    Veritabani tablosu / koleksiyonu.
    Insert, select, update, delete islemlerini destekler.
    """

    def __init__(self, name: str, storage: StorageBackend):
        self.name = name
        self._storage = storage

    def _load(self) -> List[Dict[str, Any]]:
        """Tum kayitlari yukle."""
        return self._storage.read(self.name)

    def _save(self, data: List[Dict[str, Any]]) -> None:
        """Tum kayitlari kaydet."""
        self._storage.write(self.name, data)

    def insert(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Yeni bir kayit ekle.
        Otomatik olarak _id, _created_at ve _updated_at alanlari eklenir.
        """
        data = self._load()
        new_record = {
            "_id": str(uuid.uuid4()),
            "_created_at": datetime.now().isoformat(),
            "_updated_at": datetime.now().isoformat(),
            **record,
        }
        data.append(new_record)
        self._save(data)
        return new_record

    def insert_many(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Birden fazla kayit ekle."""
        data = self._load()
        new_records = []
        now = datetime.now().isoformat()
        for record in records:
            new_record = {
                "_id": str(uuid.uuid4()),
                "_created_at": now,
                "_updated_at": now,
                **record,
            }
            new_records.append(new_record)
            data.append(new_record)
        self._save(data)
        return new_records

    def find_all(self) -> List[Dict[str, Any]]:
        """Tum kayitlari getir."""
        return self._load()

    def find_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """ID ile kayit bul."""
        data = self._load()
        for record in data:
            if record.get("_id") == record_id:
                return record
        return None

    def find(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Sorgu ile eslesen kayitlari getir.
        query: {"alan": "deger"} seklinde filtre.
        """
        data = self._load()
        if query is None:
            return data
        results = []
        for record in data:
            match = True
            for key, value in query.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                results.append(record)
        return results

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sorgu ile eslesen ilk kayiti getir."""
        results = self.find(query)
        return results[0] if results else None

    def find_where(
        self, condition: Callable[[Dict[str, Any]], bool]
    ) -> List[Dict[str, Any]]:
        """
        Ozel kosul fonksiyonu ile kayit bul.
        Ornek: table.find_where(lambda r: r.get("yas", 0) > 18)
        """
        data = self._load()
        return [record for record in data if condition(record)]

    def update_by_id(
        self, record_id: str, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """ID ile kayit guncelle."""
        data = self._load()
        for i, record in enumerate(data):
            if record.get("_id") == record_id:
                record.update(updates)
                record["_updated_at"] = datetime.now().isoformat()
                data[i] = record
                self._save(data)
                return record
        return None

    def update(
        self, query: Dict[str, Any], updates: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Sorgu ile eslesen tum kayitlari guncelle."""
        data = self._load()
        updated = []
        for i, record in enumerate(data):
            match = True
            for key, value in query.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                record.update(updates)
                record["_updated_at"] = datetime.now().isoformat()
                data[i] = record
                updated.append(record)
        if updated:
            self._save(data)
        return updated

    def delete_by_id(self, record_id: str) -> bool:
        """ID ile kayit sil."""
        data = self._load()
        original_len = len(data)
        data = [r for r in data if r.get("_id") != record_id]
        if len(data) < original_len:
            self._save(data)
            return True
        return False

    def delete(self, query: Dict[str, Any]) -> int:
        """Sorgu ile eslesen tum kayitlari sil. Silinen kayit sayisini dondurur."""
        data = self._load()
        original_len = len(data)
        remaining = []
        for record in data:
            match = True
            for key, value in query.items():
                if record.get(key) != value:
                    match = False
                    break
            if not match:
                remaining.append(record)
        deleted_count = original_len - len(remaining)
        if deleted_count > 0:
            self._save(remaining)
        return deleted_count

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """Kayit sayisini dondur."""
        if query is None:
            return len(self._load())
        return len(self.find(query))

    def drop(self) -> None:
        """Tabloyu tamamen sil."""
        self._storage.delete_collection(self.name)

    def clear(self) -> None:
        """Tablodaki tum kayitlari sil ama tabloyu koru."""
        self._save([])
