"""
Baglanti yoneticisi - Dosya ve dis depolama aygitina baglanti yonetimi.
"""

import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional

from pyfiledb.database import Database
from pyfiledb.storage import ExternalStorage, FileStorage


class ConnectionManager:
    """
    Veritabani baglanti yoneticisi.
    Dosya sistemi ve dis depolama aygitlarina baglanti kurar ve yonetir.
    """

    def __init__(self) -> None:
        self._connections: Dict[str, Database] = {}

    def connect_file(self, name: str, path: str) -> Database:
        """
        Dosya tabanli veritabanina baglan.

        Args:
            name: Baglanti ismi (benzersiz tanimlayici)
            path: Veritabani dosyalarinin saklanacagi dizin yolu

        Returns:
            Database nesnesi
        """
        db = Database.from_file(path)
        self._connections[name] = db
        return db

    def connect_external(
        self, name: str, device_path: str, db_folder: str = "pyfiledb_data"
    ) -> Database:
        """
        Dis depolama aygitina baglan.

        Args:
            name: Baglanti ismi (benzersiz tanimlayici)
            device_path: Dis depolama aygitinin mount noktasi
            db_folder: Veritabani klasor ismi

        Returns:
            Database nesnesi
        """
        db = Database.from_external(device_path, db_folder)
        self._connections[name] = db
        return db

    def disconnect(self, name: str) -> bool:
        """Bir baglantiyi kapat."""
        if name in self._connections:
            del self._connections[name]
            return True
        return False

    def get_connection(self, name: str) -> Optional[Database]:
        """Mevcut bir baglantiyi getir."""
        return self._connections.get(name)

    def list_connections(self) -> Dict[str, Dict[str, Any]]:
        """Tum aktif baglantilari ve bilgilerini listele."""
        result = {}
        for name, db in self._connections.items():
            result[name] = db.get_storage_info()
        return result

    def disconnect_all(self) -> int:
        """Tum baglantilari kapat."""
        count = len(self._connections)
        self._connections.clear()
        return count

    @staticmethod
    def detect_external_devices() -> List[Dict[str, str]]:
        """
        Sisteme bagli dis depolama aygitlarini tespit et.
        Linux ve macOS destekler.
        """
        devices = []
        system = platform.system()

        if system == "Linux":
            # /media ve /mnt altindaki mount noktalarini kontrol et
            for mount_base in ["/media", "/mnt"]:
                mount_path = Path(mount_base)
                if mount_path.exists():
                    for item in mount_path.iterdir():
                        if item.is_dir():
                            # Alt klasorleri de kontrol et (/media/username/device)
                            if item.name != "lost+found":
                                sub_items = list(item.iterdir()) if item.is_dir() else []
                                if sub_items:
                                    for sub in sub_items:
                                        if sub.is_dir() and sub.name != "lost+found":
                                            devices.append(
                                                {
                                                    "path": str(sub),
                                                    "name": sub.name,
                                                    "type": "external",
                                                }
                                            )
                                else:
                                    devices.append(
                                        {
                                            "path": str(item),
                                            "name": item.name,
                                            "type": "external",
                                        }
                                    )

            # /proc/mounts dosyasindan USB aygitlarini kontrol et
            mounts_file = Path("/proc/mounts")
            if mounts_file.exists():
                try:
                    with open(mounts_file, "r") as f:
                        for line in f:
                            parts = line.split()
                            if len(parts) >= 2:
                                device, mount_point = parts[0], parts[1]
                                if "/sd" in device or "/nvme" in device:
                                    if mount_point not in ["/", "/boot", "/home"]:
                                        if not any(
                                            d["path"] == mount_point for d in devices
                                        ):
                                            devices.append(
                                                {
                                                    "path": mount_point,
                                                    "name": Path(mount_point).name,
                                                    "type": "mounted",
                                                }
                                            )
                except IOError:
                    pass

        elif system == "Darwin":  # macOS
            volumes_path = Path("/Volumes")
            if volumes_path.exists():
                for item in volumes_path.iterdir():
                    if item.is_dir() and item.name != "Macintosh HD":
                        devices.append(
                            {
                                "path": str(item),
                                "name": item.name,
                                "type": "external",
                            }
                        )

        return devices

    def auto_connect_external(
        self, db_folder: str = "pyfiledb_data"
    ) -> Dict[str, Database]:
        """
        Tespit edilen tum dis depolama aygitlarina otomatik baglan.
        """
        devices = self.detect_external_devices()
        connected = {}
        for device in devices:
            name = f"ext_{device['name']}"
            try:
                db = self.connect_external(name, device["path"], db_folder)
                connected[name] = db
            except (FileNotFoundError, PermissionError):
                continue
        return connected
