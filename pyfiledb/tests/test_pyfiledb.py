"""PyFileDB testleri."""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from pyfiledb import Database, FileStorage, ExternalStorage, ConnectionManager, Table


class TestFileStorage(unittest.TestCase):
    """FileStorage testleri."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = FileStorage(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_and_read(self):
        data = [{"id": 1, "name": "test"}]
        self.storage.write("col1", data)
        result = self.storage.read("col1")
        self.assertEqual(result, data)

    def test_read_nonexistent(self):
        result = self.storage.read("nonexistent")
        self.assertEqual(result, [])

    def test_exists(self):
        self.assertFalse(self.storage.exists("col1"))
        self.storage.write("col1", [])
        self.assertTrue(self.storage.exists("col1"))

    def test_delete_collection(self):
        self.storage.write("col1", [{"x": 1}])
        self.assertTrue(self.storage.exists("col1"))
        self.storage.delete_collection("col1")
        self.assertFalse(self.storage.exists("col1"))

    def test_list_collections(self):
        self.storage.write("col1", [])
        self.storage.write("col2", [])
        collections = self.storage.list_collections()
        self.assertIn("col1", collections)
        self.assertIn("col2", collections)

    def test_get_storage_info(self):
        info = self.storage.get_storage_info()
        self.assertEqual(info["type"], "file")
        self.assertIn("base_path", info)
        self.assertIn("disk_free", info)


class TestExternalStorage(unittest.TestCase):
    """ExternalStorage testleri (simulasyon)."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = ExternalStorage(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_and_read(self):
        data = [{"id": 1, "name": "external_test"}]
        self.storage.write("ext_col", data)
        result = self.storage.read("ext_col")
        self.assertEqual(result, data)

    def test_meta_file_created(self):
        meta_path = self.storage.base_path / ".pyfiledb_meta.json"
        self.assertTrue(meta_path.exists())
        with open(meta_path, "r") as f:
            meta = json.load(f)
        self.assertIn("created_at", meta)
        self.assertEqual(meta["version"], "1.0.0")

    def test_is_device_connected(self):
        self.assertTrue(self.storage.is_device_connected())

    def test_get_storage_info(self):
        info = self.storage.get_storage_info()
        self.assertEqual(info["type"], "external")


class TestTable(unittest.TestCase):
    """Table CRUD testleri."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = FileStorage(self.test_dir)
        self.table = Table("test_table", self.storage)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_insert(self):
        record = self.table.insert({"ad": "Ali", "yas": 25})
        self.assertIn("_id", record)
        self.assertIn("_created_at", record)
        self.assertEqual(record["ad"], "Ali")

    def test_insert_many(self):
        records = self.table.insert_many([
            {"ad": "Ali", "yas": 25},
            {"ad": "Ayse", "yas": 30},
        ])
        self.assertEqual(len(records), 2)
        self.assertEqual(self.table.count(), 2)

    def test_find_all(self):
        self.table.insert({"ad": "Ali"})
        self.table.insert({"ad": "Ayse"})
        all_records = self.table.find_all()
        self.assertEqual(len(all_records), 2)

    def test_find_by_id(self):
        record = self.table.insert({"ad": "Ali"})
        found = self.table.find_by_id(record["_id"])
        self.assertIsNotNone(found)
        self.assertEqual(found["ad"], "Ali")

    def test_find_by_id_not_found(self):
        result = self.table.find_by_id("nonexistent")
        self.assertIsNone(result)

    def test_find_with_query(self):
        self.table.insert({"ad": "Ali", "sehir": "Istanbul"})
        self.table.insert({"ad": "Ayse", "sehir": "Ankara"})
        results = self.table.find({"sehir": "Istanbul"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["ad"], "Ali")

    def test_find_one(self):
        self.table.insert({"ad": "Ali"})
        self.table.insert({"ad": "Ayse"})
        result = self.table.find_one({"ad": "Ayse"})
        self.assertIsNotNone(result)
        self.assertEqual(result["ad"], "Ayse")

    def test_find_where(self):
        self.table.insert({"ad": "Ali", "yas": 25})
        self.table.insert({"ad": "Ayse", "yas": 30})
        self.table.insert({"ad": "Mehmet", "yas": 17})
        results = self.table.find_where(lambda r: r.get("yas", 0) >= 25)
        self.assertEqual(len(results), 2)

    def test_update_by_id(self):
        record = self.table.insert({"ad": "Ali", "yas": 25})
        updated = self.table.update_by_id(record["_id"], {"yas": 26})
        self.assertIsNotNone(updated)
        self.assertEqual(updated["yas"], 26)

    def test_update_by_query(self):
        self.table.insert({"ad": "Ali", "sehir": "Istanbul"})
        self.table.insert({"ad": "Ayse", "sehir": "Istanbul"})
        updated = self.table.update({"sehir": "Istanbul"}, {"sehir": "Ankara"})
        self.assertEqual(len(updated), 2)

    def test_delete_by_id(self):
        record = self.table.insert({"ad": "Ali"})
        self.assertTrue(self.table.delete_by_id(record["_id"]))
        self.assertEqual(self.table.count(), 0)

    def test_delete_by_id_not_found(self):
        self.assertFalse(self.table.delete_by_id("nonexistent"))

    def test_delete_by_query(self):
        self.table.insert({"ad": "Ali", "sehir": "Istanbul"})
        self.table.insert({"ad": "Ayse", "sehir": "Ankara"})
        deleted = self.table.delete({"sehir": "Istanbul"})
        self.assertEqual(deleted, 1)
        self.assertEqual(self.table.count(), 1)

    def test_count(self):
        self.assertEqual(self.table.count(), 0)
        self.table.insert({"ad": "Ali"})
        self.assertEqual(self.table.count(), 1)

    def test_count_with_query(self):
        self.table.insert({"ad": "Ali", "aktif": True})
        self.table.insert({"ad": "Ayse", "aktif": False})
        self.assertEqual(self.table.count({"aktif": True}), 1)

    def test_clear(self):
        self.table.insert({"ad": "Ali"})
        self.table.insert({"ad": "Ayse"})
        self.table.clear()
        self.assertEqual(self.table.count(), 0)

    def test_drop(self):
        self.table.insert({"ad": "Ali"})
        self.table.drop()
        self.assertFalse(self.storage.exists("test_table"))


class TestDatabase(unittest.TestCase):
    """Database testleri."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = Database.from_file(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_from_file(self):
        self.assertIsInstance(self.db, Database)

    def test_from_external(self):
        db = Database.from_external(self.test_dir)
        self.assertIsInstance(db, Database)

    def test_table(self):
        table = self.db.table("users")
        self.assertIsInstance(table, Table)

    def test_table_reuse(self):
        t1 = self.db.table("users")
        t2 = self.db.table("users")
        self.assertIs(t1, t2)

    def test_list_tables(self):
        self.db.table("users").insert({"ad": "Ali"})
        self.db.table("products").insert({"isim": "Laptop"})
        tables = self.db.list_tables()
        self.assertIn("users", tables)
        self.assertIn("products", tables)

    def test_drop_table(self):
        self.db.table("users").insert({"ad": "Ali"})
        self.assertTrue(self.db.drop_table("users"))
        self.assertNotIn("users", self.db.list_tables())

    def test_get_stats(self):
        self.db.table("users").insert({"ad": "Ali"})
        stats = self.db.get_stats()
        self.assertEqual(stats["table_count"], 1)
        self.assertEqual(stats["total_records"], 1)

    def test_backup_and_restore(self):
        self.db.table("users").insert({"ad": "Ali"})
        self.db.table("products").insert({"isim": "Laptop"})

        backup_dir = tempfile.mkdtemp()
        try:
            backup_storage = FileStorage(backup_dir)
            count = self.db.backup(backup_storage)
            self.assertEqual(count, 2)

            new_dir = tempfile.mkdtemp()
            try:
                new_db = Database.from_file(new_dir)
                restored = new_db.restore(backup_storage)
                self.assertEqual(restored, 2)
                self.assertEqual(new_db.table("users").count(), 1)
            finally:
                shutil.rmtree(new_dir, ignore_errors=True)
        finally:
            shutil.rmtree(backup_dir, ignore_errors=True)


class TestConnectionManager(unittest.TestCase):
    """ConnectionManager testleri."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manager = ConnectionManager()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_connect_file(self):
        db = self.manager.connect_file("local", self.test_dir)
        self.assertIsInstance(db, Database)

    def test_connect_external(self):
        db = self.manager.connect_external("ext", self.test_dir)
        self.assertIsInstance(db, Database)

    def test_get_connection(self):
        self.manager.connect_file("local", self.test_dir)
        db = self.manager.get_connection("local")
        self.assertIsNotNone(db)

    def test_get_connection_not_found(self):
        db = self.manager.get_connection("nonexistent")
        self.assertIsNone(db)

    def test_disconnect(self):
        self.manager.connect_file("local", self.test_dir)
        self.assertTrue(self.manager.disconnect("local"))
        self.assertIsNone(self.manager.get_connection("local"))

    def test_list_connections(self):
        self.manager.connect_file("local", self.test_dir)
        connections = self.manager.list_connections()
        self.assertIn("local", connections)

    def test_disconnect_all(self):
        self.manager.connect_file("db1", self.test_dir)
        dir2 = tempfile.mkdtemp()
        try:
            self.manager.connect_file("db2", dir2)
            count = self.manager.disconnect_all()
            self.assertEqual(count, 2)
        finally:
            shutil.rmtree(dir2, ignore_errors=True)

    def test_detect_external_devices(self):
        # Sadece calistigini kontrol et (aygit bulamayabilir)
        devices = ConnectionManager.detect_external_devices()
        self.assertIsInstance(devices, list)


if __name__ == "__main__":
    unittest.main()
