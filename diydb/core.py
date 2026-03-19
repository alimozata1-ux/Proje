"""Core DIY database implementation for GoblinPackege and similar projects."""

from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple
from uuid import uuid4

from .query import Query, from_filters, query
from .storage import JsonFileStorage, MemoryStorage, StorageAdapter
from .types import (
    DiyDbError,
    Field,
    Hook,
    Index,
    Migration,
    QueryError,
    Record,
    SchemaError,
    Stats,
    TransactionError,
    ValidationError,
    deep_copy_record,
    now_iso,
)


EVENT_BEFORE_INSERT = "before_insert"
EVENT_AFTER_INSERT = "after_insert"
EVENT_BEFORE_UPDATE = "before_update"
EVENT_AFTER_UPDATE = "after_update"
EVENT_BEFORE_DELETE = "before_delete"
EVENT_AFTER_DELETE = "after_delete"
EVENT_AFTER_COMMIT = "after_commit"


@dataclass
class Table:
    """Represents a table in the DIY database."""

    name: str
    fields: Dict[str, Field]
    records: List[Record] = field(default_factory=list)
    primary_key: str = "id"
    indexes: Dict[str, Index] = field(default_factory=dict)
    _hooks: List[Hook] = field(default_factory=list)

    def _build_index_key(self, record: Record, index: Index) -> Tuple[Any, ...]:
        return tuple(record.get(field) for field in index.field_names)

    def _rebuild_indexes(self) -> None:
        for index in self.indexes.values():
            index.mapping.clear()

        for pos, rec in enumerate(self.records):
            for index in self.indexes.values():
                key = self._build_index_key(rec, index)
                if index.unique and key in index.mapping:
                    raise ValidationError(
                        f"Unique index '{index.key}' violation in table '{self.name}'"
                    )
                index.mapping.setdefault(key, []).append(pos)

    def create_index(self, *field_names: str, unique: bool = False) -> None:
        if not field_names:
            raise SchemaError("create_index requires at least one field")
        for field_name in field_names:
            if field_name not in self.fields and field_name != self.primary_key:
                raise SchemaError(f"Unknown field for index: {field_name}")

        idx = Index(field_names=tuple(field_names), unique=unique)
        self.indexes[idx.key] = idx
        self._rebuild_indexes()

    def drop_index(self, *field_names: str) -> None:
        key = "|".join(field_names)
        if key in self.indexes:
            del self.indexes[key]

    def on(self, event: str, callback: Callable[..., None]) -> None:
        self._hooks.append(Hook(event=event, callback=callback))

    def _emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        for hook in self._hooks:
            if hook.event == event:
                hook.callback(*args, **kwargs)

    def _validate_required_fields(self, record: Record, partial: bool) -> None:
        for field_name, field in self.fields.items():
            if partial and field_name not in record:
                continue
            if field.required and field_name not in record and not field.has_default():
                raise ValidationError(f"Missing required field: {field_name}")

    def _apply_defaults(self, record: Record, partial: bool) -> Record:
        output = dict(record)
        for field_name, field in self.fields.items():
            if field_name not in output and field.has_default() and not partial:
                output[field_name] = field.get_default()
        return output

    def _normalize_record(self, record: Record, partial: bool = False) -> Record:
        if not isinstance(record, dict):
            raise ValidationError("Record must be a dict")

        self._validate_required_fields(record, partial=partial)
        data = self._apply_defaults(record, partial=partial)

        normalized: Record = {}
        for key, value in data.items():
            if key == self.primary_key:
                normalized[key] = value
                continue

            field = self.fields.get(key)
            if field is None:
                normalized[key] = value
                continue

            normalized[key] = field.normalize(value)

        if self.primary_key not in normalized and not partial:
            normalized[self.primary_key] = str(uuid4())

        return normalized

    def _check_unique_constraints(self, record: Record, existing_id: Optional[str] = None) -> None:
        for field_name, field in self.fields.items():
            if not field.unique:
                continue
            value = record.get(field_name)
            for item in self.records:
                if existing_id is not None and item.get(self.primary_key) == existing_id:
                    continue
                if item.get(field_name) == value:
                    raise ValidationError(
                        f"Unique field violation '{field_name}={value}' in table '{self.name}'"
                    )

        for idx in self.indexes.values():
            if not idx.unique:
                continue
            key = self._build_index_key(record, idx)
            for position in idx.mapping.get(key, []):
                existing = self.records[position]
                if existing_id is not None and existing.get(self.primary_key) == existing_id:
                    continue
                raise ValidationError(
                    f"Unique index violation on '{idx.key}' with key {key!r}"
                )

    def _find_index_by_pk(self, value: Any) -> int:
        for i, rec in enumerate(self.records):
            if rec.get(self.primary_key) == value:
                return i
        return -1

    def insert(self, record: Record) -> Record:
        normalized = self._normalize_record(record, partial=False)
        self._check_unique_constraints(normalized)

        self._emit(EVENT_BEFORE_INSERT, table=self.name, record=deep_copy_record(normalized))
        self.records.append(normalized)
        self._rebuild_indexes()
        inserted = deep_copy_record(normalized)
        self._emit(EVENT_AFTER_INSERT, table=self.name, record=deep_copy_record(inserted))
        return inserted

    def insert_many(self, records: Iterable[Record]) -> List[Record]:
        inserted: List[Record] = []
        for rec in records:
            inserted.append(self.insert(rec))
        return inserted

    def all(self) -> List[Record]:
        return [deep_copy_record(r) for r in self.records]

    def count(self, q: Optional[Query] = None) -> int:
        if q is None:
            return len(self.records)
        return len(q.apply(self.records))

    def exists(self, q: Optional[Query] = None) -> bool:
        if q is None:
            return bool(self.records)
        for rec in self.records:
            if q.build_predicate()(rec):
                return True
        return False

    def first(self, q: Optional[Query] = None) -> Optional[Record]:
        if q is None:
            return deep_copy_record(self.records[0]) if self.records else None
        matched = q.limit_to(1).apply(self.records)
        if not matched:
            return None
        return deep_copy_record(matched[0])

    def get(self, pk: Any) -> Optional[Record]:
        idx = self._find_index_by_pk(pk)
        if idx == -1:
            return None
        return deep_copy_record(self.records[idx])

    def find(self, q: Optional[Query] = None, **filters: Any) -> List[Record]:
        if q is None:
            q = from_filters(filters)
        elif filters:
            q = q.clone().and_query(from_filters(filters))
        return [deep_copy_record(rec) for rec in q.apply(self.records)]

    def update(self, pk: Any, updates: Record, upsert: bool = False) -> Optional[Record]:
        idx = self._find_index_by_pk(pk)

        if idx == -1:
            if not upsert:
                return None
            data = dict(updates)
            data[self.primary_key] = pk
            return self.insert(data)

        current = self.records[idx]
        merged = dict(current)
        merged.update(updates)

        normalized = self._normalize_record(merged, partial=False)
        self._check_unique_constraints(normalized, existing_id=current.get(self.primary_key))

        before = deep_copy_record(current)
        after = deep_copy_record(normalized)

        self._emit(EVENT_BEFORE_UPDATE, table=self.name, before=before, after=after)
        self.records[idx] = normalized
        self._rebuild_indexes()
        self._emit(EVENT_AFTER_UPDATE, table=self.name, before=before, after=after)
        return deep_copy_record(normalized)

    def update_where(self, q: Query, updates: Record) -> int:
        matched = q.apply(self.records)
        target_ids = [rec.get(self.primary_key) for rec in matched]
        count = 0
        for pk in target_ids:
            result = self.update(pk, updates, upsert=False)
            if result is not None:
                count += 1
        return count

    def upsert(self, record: Record) -> Record:
        if self.primary_key in record:
            updated = self.update(record[self.primary_key], record, upsert=True)
            assert updated is not None
            return updated
        return self.insert(record)

    def delete(self, pk: Any) -> bool:
        idx = self._find_index_by_pk(pk)
        if idx == -1:
            return False

        record = deep_copy_record(self.records[idx])
        self._emit(EVENT_BEFORE_DELETE, table=self.name, record=deep_copy_record(record))
        del self.records[idx]
        self._rebuild_indexes()
        self._emit(EVENT_AFTER_DELETE, table=self.name, record=deep_copy_record(record))
        return True

    def delete_where(self, q: Query) -> int:
        matched = q.apply(self.records)
        target_ids = [rec.get(self.primary_key) for rec in matched]
        removed = 0
        for pk in target_ids:
            if self.delete(pk):
                removed += 1
        return removed

    def purge(self) -> int:
        removed = len(self.records)
        if not removed:
            return 0
        for rec in list(self.records):
            self._emit(EVENT_BEFORE_DELETE, table=self.name, record=deep_copy_record(rec))
        self.records.clear()
        self._rebuild_indexes()
        return removed

    def aggregate_sum(self, field: str, q: Optional[Query] = None) -> float:
        rows = self.records if q is None else q.apply(self.records)
        total = 0.0
        for row in rows:
            value = row.get(field)
            if isinstance(value, (int, float)):
                total += value
        return total

    def aggregate_avg(self, field: str, q: Optional[Query] = None) -> float:
        rows = self.records if q is None else q.apply(self.records)
        values: List[float] = []
        for row in rows:
            value = row.get(field)
            if isinstance(value, (int, float)):
                values.append(float(value))
        if not values:
            return 0.0
        return sum(values) / len(values)

    def aggregate_min(self, field: str, q: Optional[Query] = None) -> Any:
        rows = self.records if q is None else q.apply(self.records)
        values = [row.get(field) for row in rows if row.get(field) is not None]
        if not values:
            return None
        return min(values)

    def aggregate_max(self, field: str, q: Optional[Query] = None) -> Any:
        rows = self.records if q is None else q.apply(self.records)
        values = [row.get(field) for row in rows if row.get(field) is not None]
        if not values:
            return None
        return max(values)

    def group_count(self, field: str, q: Optional[Query] = None) -> Dict[Any, int]:
        rows = self.records if q is None else q.apply(self.records)
        out: Dict[Any, int] = {}
        for row in rows:
            key = row.get(field)
            out[key] = out.get(key, 0) + 1
        return out

    def to_payload(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "primary_key": self.primary_key,
            "fields": {
                name: {
                    "kind": getattr(field.kind, "__name__", "object"),
                    "required": field.required,
                    "default": field.get_default() if field.has_default() and not callable(field.default) else None,
                    "unique": field.unique,
                    "nullable": field.nullable,
                }
                for name, field in self.fields.items()
            },
            "records": [deep_copy_record(r) for r in self.records],
            "indexes": [
                {
                    "field_names": list(idx.field_names),
                    "unique": idx.unique,
                }
                for idx in self.indexes.values()
            ],
        }

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "Table":
        name = payload["name"]
        primary_key = payload.get("primary_key", "id")

        type_map = {
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "dict": dict,
            "list": list,
            "object": object,
        }

        fields: Dict[str, Field] = {}
        for field_name, meta in payload.get("fields", {}).items():
            kind_name = meta.get("kind", "object")
            kind = type_map.get(kind_name, object)
            fields[field_name] = Field(
                name=field_name,
                kind=kind,
                required=meta.get("required", False),
                default=meta.get("default"),
                unique=meta.get("unique", False),
                nullable=meta.get("nullable", False),
            )

        table = cls(name=name, fields=fields, primary_key=primary_key)
        table.records = [dict(row) for row in payload.get("records", [])]

        for idx_meta in payload.get("indexes", []):
            table.create_index(*idx_meta.get("field_names", []), unique=idx_meta.get("unique", False))

        table._rebuild_indexes()
        return table


class Transaction:
    """Context manager handling rollback for database mutations."""

    def __init__(self, db: "DiyDb"):
        self.db = db
        self._snapshot: Optional[str] = None
        self._active = False

    def __enter__(self) -> "DiyDb":
        if self.db._in_transaction:
            raise TransactionError("Nested transactions are not supported")
        self._snapshot = self.db._serialize_state()
        self._active = True
        self.db._in_transaction = True
        return self.db

    def __exit__(self, exc_type, exc, tb) -> bool:
        if not self._active:
            return False

        try:
            if exc is None:
                self.db.commit()
            else:
                assert self._snapshot is not None
                self.db._deserialize_state(self._snapshot)
        finally:
            self.db._in_transaction = False
            self._active = False

        return False


class DiyDb:
    """
    A small DIY Python database library backed by JSON storage.

    Highlights:
      - Table schemas with typed fields and constraints
      - Query builder with filtering, ordering, pagination
      - Transaction support with rollback
      - Hooks for table lifecycle events
      - Backup/restore + migrations
      - In-memory indexing
    """

    def __init__(
        self,
        path: Optional[str] = None,
        storage: Optional[StorageAdapter] = None,
        autosave: bool = True,
    ) -> None:
        if storage is not None and path is not None:
            raise ValueError("Pass either 'path' or 'storage', not both")

        self.storage = storage or (JsonFileStorage(path) if path else MemoryStorage())
        self.autosave = autosave

        self._lock = threading.RLock()
        self._in_transaction = False
        self._migrations: Dict[int, Migration] = {}

        self.meta: Dict[str, Any] = {
            "version": 1,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "name": "diydb",
        }
        self.tables: Dict[str, Table] = {}

        self.load()

    def _serialize_state(self) -> str:
        payload = self.to_payload()
        return json.dumps(payload, ensure_ascii=False)

    def _deserialize_state(self, state: str) -> None:
        payload = json.loads(state)
        self.from_payload(payload)

    def _auto_commit(self) -> None:
        if self.autosave and not self._in_transaction:
            self.commit()

    def register_migration(self, migration: Migration) -> None:
        if migration.version in self._migrations:
            raise SchemaError(f"Migration version '{migration.version}' already registered")
        self._migrations[migration.version] = migration

    def run_migrations(self, target_version: Optional[int] = None) -> None:
        with self._lock:
            current = int(self.meta.get("version", 1))
            versions = sorted(self._migrations)
            for version in versions:
                if version <= current:
                    continue
                if target_version is not None and version > target_version:
                    break
                migration = self._migrations[version]
                for table_name, table in list(self.tables.items()):
                    migrated = [migration.apply(rec) for rec in table.records]
                    table.records = migrated
                    table._rebuild_indexes()
                current = version
            self.meta["version"] = current
            self._auto_commit()

    def create_table(
        self,
        name: str,
        fields: Sequence[Field],
        primary_key: str = "id",
        if_not_exists: bool = False,
    ) -> Table:
        with self._lock:
            if name in self.tables:
                if if_not_exists:
                    return self.tables[name]
                raise SchemaError(f"Table '{name}' already exists")

            field_map: Dict[str, Field] = {}
            for fld in fields:
                if fld.name in field_map:
                    raise SchemaError(f"Duplicate field name: {fld.name}")
                field_map[fld.name] = fld

            table = Table(name=name, fields=field_map, primary_key=primary_key)
            self.tables[name] = table
            self._auto_commit()
            return table

    def drop_table(self, name: str, if_exists: bool = False) -> bool:
        with self._lock:
            if name not in self.tables:
                if if_exists:
                    return False
                raise SchemaError(f"Unknown table: {name}")
            del self.tables[name]
            self._auto_commit()
            return True

    def table(self, name: str) -> Table:
        tbl = self.tables.get(name)
        if tbl is None:
            raise SchemaError(f"Unknown table: {name}")
        return tbl

    def list_tables(self) -> List[str]:
        return sorted(self.tables.keys())

    def transaction(self) -> Transaction:
        return Transaction(self)

    @contextmanager
    def locked(self) -> Iterator[None]:
        self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()

    def insert(self, table_name: str, record: Record) -> Record:
        with self._lock:
            item = self.table(table_name).insert(record)
            self._auto_commit()
            return item

    def insert_many(self, table_name: str, records: Iterable[Record]) -> List[Record]:
        with self._lock:
            out = self.table(table_name).insert_many(records)
            self._auto_commit()
            return out

    def find(self, table_name: str, q: Optional[Query] = None, **filters: Any) -> List[Record]:
        with self._lock:
            return self.table(table_name).find(q=q, **filters)

    def first(self, table_name: str, q: Optional[Query] = None, **filters: Any) -> Optional[Record]:
        with self._lock:
            if q is None:
                q = from_filters(filters)
            elif filters:
                q = q.clone().and_query(from_filters(filters))
            return self.table(table_name).first(q)

    def get(self, table_name: str, pk: Any) -> Optional[Record]:
        with self._lock:
            return self.table(table_name).get(pk)

    def update(self, table_name: str, pk: Any, updates: Record, upsert: bool = False) -> Optional[Record]:
        with self._lock:
            out = self.table(table_name).update(pk, updates, upsert=upsert)
            self._auto_commit()
            return out

    def update_where(self, table_name: str, q: Query, updates: Record) -> int:
        with self._lock:
            count = self.table(table_name).update_where(q, updates)
            self._auto_commit()
            return count

    def upsert(self, table_name: str, record: Record) -> Record:
        with self._lock:
            out = self.table(table_name).upsert(record)
            self._auto_commit()
            return out

    def delete(self, table_name: str, pk: Any) -> bool:
        with self._lock:
            removed = self.table(table_name).delete(pk)
            self._auto_commit()
            return removed

    def delete_where(self, table_name: str, q: Query) -> int:
        with self._lock:
            removed = self.table(table_name).delete_where(q)
            self._auto_commit()
            return removed

    def purge(self, table_name: str) -> int:
        with self._lock:
            removed = self.table(table_name).purge()
            self._auto_commit()
            return removed

    def count(self, table_name: str, q: Optional[Query] = None) -> int:
        with self._lock:
            return self.table(table_name).count(q)

    def exists(self, table_name: str, q: Optional[Query] = None) -> bool:
        with self._lock:
            return self.table(table_name).exists(q)

    def sum(self, table_name: str, field: str, q: Optional[Query] = None) -> float:
        with self._lock:
            return self.table(table_name).aggregate_sum(field, q)

    def avg(self, table_name: str, field: str, q: Optional[Query] = None) -> float:
        with self._lock:
            return self.table(table_name).aggregate_avg(field, q)

    def min(self, table_name: str, field: str, q: Optional[Query] = None) -> Any:
        with self._lock:
            return self.table(table_name).aggregate_min(field, q)

    def max(self, table_name: str, field: str, q: Optional[Query] = None) -> Any:
        with self._lock:
            return self.table(table_name).aggregate_max(field, q)

    def group_count(self, table_name: str, field: str, q: Optional[Query] = None) -> Dict[Any, int]:
        with self._lock:
            return self.table(table_name).group_count(field, q)

    def create_index(self, table_name: str, *field_names: str, unique: bool = False) -> None:
        with self._lock:
            self.table(table_name).create_index(*field_names, unique=unique)
            self._auto_commit()

    def drop_index(self, table_name: str, *field_names: str) -> None:
        with self._lock:
            self.table(table_name).drop_index(*field_names)
            self._auto_commit()

    def on(self, table_name: str, event: str, callback: Callable[..., None]) -> None:
        with self._lock:
            self.table(table_name).on(event, callback)

    def backup(self) -> Dict[str, Any]:
        with self._lock:
            return self.to_payload()

    def restore(self, payload: Dict[str, Any], merge: bool = False) -> None:
        with self._lock:
            if merge:
                incoming = DiyDb(storage=MemoryStorage(), autosave=False)
                incoming.from_payload(payload)
                for table_name in incoming.list_tables():
                    if table_name not in self.tables:
                        self.tables[table_name] = incoming.table(table_name)
                        continue
                    table = self.tables[table_name]
                    for rec in incoming.table(table_name).all():
                        table.upsert(rec)
            else:
                self.from_payload(payload)
            self._auto_commit()

    def stats(self) -> Stats:
        with self._lock:
            record_count = 0
            for t in self.tables.values():
                record_count += len(t.records)
            return Stats(
                table_count=len(self.tables),
                record_count=record_count,
                file_size_bytes=self.storage.size(),
                updated_at=self.meta.get("updated_at", now_iso()),
            )

    def to_payload(self) -> Dict[str, Any]:
        return {
            "meta": dict(self.meta),
            "tables": {name: table.to_payload() for name, table in self.tables.items()},
        }

    def from_payload(self, payload: Dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise SchemaError("Payload must be object")

        meta = payload.get("meta", {})
        tables_payload = payload.get("tables", {})

        if not isinstance(tables_payload, dict):
            raise SchemaError("'tables' must be object")

        tables: Dict[str, Table] = {}
        for name, table_payload in tables_payload.items():
            table = Table.from_payload(table_payload)
            tables[name] = table

        self.meta = {
            "version": int(meta.get("version", 1)),
            "created_at": meta.get("created_at", now_iso()),
            "updated_at": meta.get("updated_at", now_iso()),
            "name": meta.get("name", "diydb"),
        }
        self.tables = tables

    def load(self) -> None:
        with self._lock:
            payload = self.storage.load()
            self.from_payload(payload)

    def commit(self) -> None:
        with self._lock:
            self.meta["updated_at"] = now_iso()
            payload = self.to_payload()
            self.storage.save(payload)
            for table in self.tables.values():
                table._emit(EVENT_AFTER_COMMIT, table=table.name)

    def vacuum(self) -> None:
        """Rebuild all indexes and compact persisted data through re-save."""
        with self._lock:
            for table in self.tables.values():
                table._rebuild_indexes()
            self.commit()

    def clone(self) -> "DiyDb":
        with self._lock:
            copied = DiyDb(storage=MemoryStorage(), autosave=self.autosave)
            copied.from_payload(self.to_payload())
            return copied

    def close(self) -> None:
        with self._lock:
            self.commit()


def open_db(path: str, autosave: bool = True) -> DiyDb:
    """Create a file-backed DIY database."""
    return DiyDb(path=path, autosave=autosave)


def memory_db(autosave: bool = False) -> DiyDb:
    """Create an in-memory DIY database."""
    return DiyDb(storage=MemoryStorage(), autosave=autosave)


__all__ = [
    "DiyDb",
    "Table",
    "Transaction",
    "open_db",
    "memory_db",
    "query",
    "from_filters",
    "EVENT_BEFORE_INSERT",
    "EVENT_AFTER_INSERT",
    "EVENT_BEFORE_UPDATE",
    "EVENT_AFTER_UPDATE",
    "EVENT_BEFORE_DELETE",
    "EVENT_AFTER_DELETE",
    "EVENT_AFTER_COMMIT",
]
