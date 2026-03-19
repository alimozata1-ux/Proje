"""diydb: DIY Python database library for local-first apps."""

from .core import (
    DiyDb,
    EVENT_AFTER_COMMIT,
    EVENT_AFTER_DELETE,
    EVENT_AFTER_INSERT,
    EVENT_AFTER_UPDATE,
    EVENT_BEFORE_DELETE,
    EVENT_BEFORE_INSERT,
    EVENT_BEFORE_UPDATE,
    Table,
    Transaction,
    memory_db,
    open_db,
)
from .query import Query, from_filters, query
from .storage import JsonFileStorage, MemoryStorage
from .types import (
    DiyDbError,
    Field,
    Migration,
    QueryError,
    SchemaError,
    Stats,
    StorageError,
    TransactionError,
    ValidationError,
)

__all__ = [
    "DiyDb",
    "Table",
    "Transaction",
    "open_db",
    "memory_db",
    "Query",
    "query",
    "from_filters",
    "Field",
    "Migration",
    "JsonFileStorage",
    "MemoryStorage",
    "DiyDbError",
    "QueryError",
    "SchemaError",
    "Stats",
    "StorageError",
    "TransactionError",
    "ValidationError",
    "EVENT_BEFORE_INSERT",
    "EVENT_AFTER_INSERT",
    "EVENT_BEFORE_UPDATE",
    "EVENT_AFTER_UPDATE",
    "EVENT_BEFORE_DELETE",
    "EVENT_AFTER_DELETE",
    "EVENT_AFTER_COMMIT",
]
