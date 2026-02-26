"""
PyFileDB - Python Dosya Tabanli Veritabani Kutuphanesi
Siteler icin dosya ve dis depolama aygitina veri yazabilen veritabani kutuphanesi.
"""

from pyfiledb.database import Database
from pyfiledb.table import Table
from pyfiledb.storage import FileStorage, ExternalStorage, StorageBackend
from pyfiledb.connection import ConnectionManager

__version__ = "1.0.0"
__all__ = [
    "Database",
    "Table",
    "FileStorage",
    "ExternalStorage",
    "StorageBackend",
    "ConnectionManager",
]
