"""
PyFileDB Baglanti Uygulamasi - CLI arayuzu.
Dosya ve dis depolama aygitina veritabani baglantisi kurar ve yonetir.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from pyfiledb.connection import ConnectionManager
from pyfiledb.database import Database


class PyFileDBApp:
    """
    PyFileDB komut satiri uygulamasi.
    Veritabanini dosya veya dis depolama aygitina baglar ve interaktif yonetim saglar.
    """

    def __init__(self) -> None:
        self.manager = ConnectionManager()
        self.current_db: Optional[Database] = None
        self.current_name: Optional[str] = None

    def connect_to_file(self, path: str, name: str = "local") -> None:
        """Dosya tabanli veritabanina baglan."""
        try:
            self.current_db = self.manager.connect_file(name, path)
            self.current_name = name
            print(f"[OK] Dosya veritabanina baglandi: {path}")
            print(f"     Baglanti ismi: {name}")
        except Exception as e:
            print(f"[HATA] Baglanti kurulamadi: {e}")

    def connect_to_external(
        self, device_path: str, name: str = "external", db_folder: str = "pyfiledb_data"
    ) -> None:
        """Dis depolama aygitina baglan."""
        try:
            self.current_db = self.manager.connect_external(name, device_path, db_folder)
            self.current_name = name
            print(f"[OK] Dis depolama aygitina baglandi: {device_path}")
            print(f"     Baglanti ismi: {name}")
            print(f"     Veri klasoru: {db_folder}")
        except FileNotFoundError:
            print(f"[HATA] Aygit bulunamadi: {device_path}")
        except PermissionError:
            print(f"[HATA] Aygita yazma izni yok: {device_path}")
        except Exception as e:
            print(f"[HATA] Baglanti kurulamadi: {e}")

    def detect_devices(self) -> None:
        """Sisteme bagli dis depolama aygitlarini tespit et."""
        devices = ConnectionManager.detect_external_devices()
        if not devices:
            print("[BILGI] Dis depolama aygiti bulunamadi.")
            return
        print(f"[BILGI] {len(devices)} dis depolama aygiti tespit edildi:")
        for i, device in enumerate(devices, 1):
            print(f"  {i}. {device['name']} - {device['path']} ({device['type']})")

    def interactive_mode(self) -> None:
        """Interaktif komut satiri modu."""
        print("=" * 60)
        print("  PyFileDB - Veritabani Yonetim Uygulamasi")
        print("  Cikis icin 'cikis' veya 'exit' yazin.")
        print("=" * 60)

        if self.current_db is None:
            print("\n[UYARI] Henuz bir veritabanina baglanilmadi.")
            print("  'baglan dosya <yol>' veya 'baglan aygit <yol>' komutu kullanin.\n")

        while True:
            try:
                prompt = f"pyfiledb"
                if self.current_name:
                    prompt += f"({self.current_name})"
                prompt += "> "
                cmd = input(prompt).strip()

                if not cmd:
                    continue

                if cmd in ("cikis", "exit", "quit", "q"):
                    print("Gule gule!")
                    break

                self._process_command(cmd)

            except KeyboardInterrupt:
                print("\nGule gule!")
                break
            except EOFError:
                break

    def _process_command(self, cmd: str) -> None:
        """Komutu isle."""
        parts = cmd.split(maxsplit=2)
        command = parts[0].lower()

        if command == "yardim" or command == "help":
            self._show_help()

        elif command == "baglan":
            if len(parts) < 3:
                print("Kullanim: baglan dosya <yol> | baglan aygit <yol>")
                return
            sub = parts[1].lower()
            path = parts[2]
            if sub == "dosya":
                self.connect_to_file(path)
            elif sub == "aygit":
                self.connect_to_external(path)
            else:
                print("Kullanim: baglan dosya <yol> | baglan aygit <yol>")

        elif command == "aygitlar":
            self.detect_devices()

        elif command == "bilgi" or command == "info":
            self._show_info()

        elif command == "tablolar":
            self._list_tables()

        elif command == "ekle":
            if len(parts) < 3:
                print("Kullanim: ekle <tablo> <json_veri>")
                return
            self._insert(parts[1], parts[2])

        elif command == "listele":
            if len(parts) < 2:
                print("Kullanim: listele <tablo>")
                return
            self._list_records(parts[1])

        elif command == "bul":
            if len(parts) < 3:
                print("Kullanim: bul <tablo> <json_sorgu>")
                return
            self._find_records(parts[1], parts[2])

        elif command == "guncelle":
            if len(parts) < 3:
                print("Kullanim: guncelle <tablo> <id> <json_veri>")
                return
            sub_parts = parts[2].split(maxsplit=1)
            if len(sub_parts) < 2:
                print("Kullanim: guncelle <tablo> <id> <json_veri>")
                return
            self._update_record(parts[1], sub_parts[0], sub_parts[1])

        elif command == "sil":
            if len(parts) < 3:
                print("Kullanim: sil <tablo> <id>")
                return
            self._delete_record(parts[1], parts[2])

        elif command == "temizle":
            if len(parts) < 2:
                print("Kullanim: temizle <tablo>")
                return
            self._clear_table(parts[1])

        elif command == "tablo_sil":
            if len(parts) < 2:
                print("Kullanim: tablo_sil <tablo>")
                return
            self._drop_table(parts[1])

        elif command == "yedekle":
            if len(parts) < 2:
                print("Kullanim: yedekle <hedef_yol>")
                return
            self._backup(parts[1])

        elif command == "istatistik":
            self._show_stats()

        elif command == "baglantilar":
            self._list_connections()

        else:
            print(f"Bilinmeyen komut: {command}")
            print("Komut listesi icin 'yardim' yazin.")

    def _show_help(self) -> None:
        """Yardim mesajini goster."""
        help_text = """
Komutlar:
  baglan dosya <yol>           Dosya tabanli veritabanina baglan
  baglan aygit <yol>           Dis depolama aygitina baglan
  aygitlar                     Dis depolama aygitlarini tespit et

  tablolar                     Mevcut tablolari listele
  ekle <tablo> <json>          Tabloya yeni kayit ekle
  listele <tablo>              Tablodaki tum kayitlari listele
  bul <tablo> <json_sorgu>     Tabloda arama yap
  guncelle <tablo> <id> <json> Kayit guncelle
  sil <tablo> <id>             Kayit sil
  temizle <tablo>              Tablodaki tum kayitlari sil
  tablo_sil <tablo>            Tabloyu tamamen sil

  bilgi                        Depolama bilgilerini goster
  istatistik                   Veritabani istatistikleri
  baglantilar                  Aktif baglantilari goster
  yedekle <hedef_yol>          Veritabanini yedekle

  yardim                       Bu yardim mesajini goster
  cikis                        Uygulamadan cik
"""
        print(help_text)

    def _ensure_connected(self) -> bool:
        """Veritabanina bagli oldugumuzu kontrol et."""
        if self.current_db is None:
            print("[HATA] Veritabanina baglanilmadi. Once 'baglan' komutunu kullanin.")
            return False
        return True

    def _show_info(self) -> None:
        """Depolama bilgilerini goster."""
        if not self._ensure_connected():
            return
        info = self.current_db.get_storage_info()
        print("\nDepolama Bilgileri:")
        for key, value in info.items():
            if "bytes" in key or "disk_" in key:
                value = self._format_bytes(value)
            print(f"  {key}: {value}")

    def _list_tables(self) -> None:
        """Tablolari listele."""
        if not self._ensure_connected():
            return
        tables = self.current_db.list_tables()
        if not tables:
            print("[BILGI] Henuz tablo yok.")
            return
        print(f"\nMevcut Tablolar ({len(tables)}):")
        for t in tables:
            count = self.current_db.table(t).count()
            print(f"  - {t} ({count} kayit)")

    def _insert(self, table_name: str, json_str: str) -> None:
        """Kayit ekle."""
        if not self._ensure_connected():
            return
        try:
            data = json.loads(json_str)
            table = self.current_db.table(table_name)
            record = table.insert(data)
            print(f"[OK] Kayit eklendi. ID: {record['_id']}")
        except json.JSONDecodeError:
            print("[HATA] Gecersiz JSON formati.")
        except Exception as e:
            print(f"[HATA] Kayit eklenemedi: {e}")

    def _list_records(self, table_name: str) -> None:
        """Tablodaki kayitlari listele."""
        if not self._ensure_connected():
            return
        table = self.current_db.table(table_name)
        records = table.find_all()
        if not records:
            print(f"[BILGI] '{table_name}' tablosunda kayit yok.")
            return
        print(f"\n'{table_name}' tablosu ({len(records)} kayit):")
        for record in records:
            print(f"  {json.dumps(record, ensure_ascii=False)}")

    def _find_records(self, table_name: str, json_str: str) -> None:
        """Kayit ara."""
        if not self._ensure_connected():
            return
        try:
            query = json.loads(json_str)
            table = self.current_db.table(table_name)
            results = table.find(query)
            if not results:
                print("[BILGI] Eslesen kayit bulunamadi.")
                return
            print(f"\nBulunan kayitlar ({len(results)}):")
            for record in results:
                print(f"  {json.dumps(record, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print("[HATA] Gecersiz JSON formati.")

    def _update_record(self, table_name: str, record_id: str, json_str: str) -> None:
        """Kayit guncelle."""
        if not self._ensure_connected():
            return
        try:
            updates = json.loads(json_str)
            table = self.current_db.table(table_name)
            result = table.update_by_id(record_id, updates)
            if result:
                print("[OK] Kayit guncellendi.")
            else:
                print(f"[HATA] ID ile kayit bulunamadi: {record_id}")
        except json.JSONDecodeError:
            print("[HATA] Gecersiz JSON formati.")

    def _delete_record(self, table_name: str, record_id: str) -> None:
        """Kayit sil."""
        if not self._ensure_connected():
            return
        table = self.current_db.table(table_name)
        if table.delete_by_id(record_id):
            print("[OK] Kayit silindi.")
        else:
            print(f"[HATA] ID ile kayit bulunamadi: {record_id}")

    def _clear_table(self, table_name: str) -> None:
        """Tabloyu temizle."""
        if not self._ensure_connected():
            return
        table = self.current_db.table(table_name)
        table.clear()
        print(f"[OK] '{table_name}' tablosu temizlendi.")

    def _drop_table(self, table_name: str) -> None:
        """Tabloyu sil."""
        if not self._ensure_connected():
            return
        if self.current_db.drop_table(table_name):
            print(f"[OK] '{table_name}' tablosu silindi.")
        else:
            print(f"[HATA] Tablo bulunamadi: {table_name}")

    def _backup(self, target_path: str) -> None:
        """Veritabanini yedekle."""
        if not self._ensure_connected():
            return
        try:
            from pyfiledb.storage import FileStorage
            target = FileStorage(target_path)
            count = self.current_db.backup(target)
            print(f"[OK] {count} tablo yedeklendi: {target_path}")
        except Exception as e:
            print(f"[HATA] Yedekleme basarisiz: {e}")

    def _show_stats(self) -> None:
        """Istatistikleri goster."""
        if not self._ensure_connected():
            return
        stats = self.current_db.get_stats()
        print(f"\nVeritabani Istatistikleri:")
        print(f"  Tablo sayisi: {stats['table_count']}")
        print(f"  Toplam kayit: {stats['total_records']}")
        if stats["tables"]:
            print(f"\n  Tablolar:")
            for name, info in stats["tables"].items():
                print(f"    - {name}: {info['record_count']} kayit")

    def _list_connections(self) -> None:
        """Aktif baglantilari listele."""
        connections = self.manager.list_connections()
        if not connections:
            print("[BILGI] Aktif baglanti yok.")
            return
        print(f"\nAktif Baglantilar ({len(connections)}):")
        for name, info in connections.items():
            print(f"  {name}: {info.get('type', '?')} - {info.get('base_path', '?')}")

    @staticmethod
    def _format_bytes(size: int) -> str:
        """Byte degerini okunabilir formata cevir."""
        if not isinstance(size, (int, float)):
            return str(size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"


def main() -> None:
    """Ana giris noktasi."""
    parser = argparse.ArgumentParser(
        description="PyFileDB - Dosya Tabanli Veritabani Yonetim Uygulamasi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  %(prog)s --dosya ./veritabanim
  %(prog)s --aygit /mnt/usb
  %(prog)s --aygit /media/kullanici/usb_disk --klasor benim_verilerim
  %(prog)s --tespit
        """,
    )

    parser.add_argument(
        "--dosya", "-d",
        help="Dosya tabanli veritabani yolu",
        metavar="YOL",
    )
    parser.add_argument(
        "--aygit", "-a",
        help="Dis depolama aygiti yolu (mount noktasi)",
        metavar="YOL",
    )
    parser.add_argument(
        "--klasor", "-k",
        help="Dis depolamadaki veritabani klasor ismi (varsayilan: pyfiledb_data)",
        default="pyfiledb_data",
        metavar="ISIM",
    )
    parser.add_argument(
        "--tespit", "-t",
        action="store_true",
        help="Dis depolama aygitlarini tespit et ve listele",
    )
    parser.add_argument(
        "--isim", "-i",
        help="Baglanti ismi (varsayilan: auto)",
        default=None,
        metavar="ISIM",
    )

    args = parser.parse_args()

    app = PyFileDBApp()

    if args.tespit:
        app.detect_devices()
        return

    if args.dosya:
        name = args.isim or "local"
        app.connect_to_file(args.dosya, name)
    elif args.aygit:
        name = args.isim or "external"
        app.connect_to_external(args.aygit, name, args.klasor)

    app.interactive_mode()


if __name__ == "__main__":
    main()
