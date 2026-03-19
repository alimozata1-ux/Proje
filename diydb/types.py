"""Typed helpers for diydb."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple


Validator = Callable[[Any], None]
Transform = Callable[[Any], Any]
Predicate = Callable[[Dict[str, Any]], bool]
Record = Dict[str, Any]


class DiyDbError(Exception):
    """Base error class for diydb."""


class SchemaError(DiyDbError):
    """Raised when schema is invalid or incompatible."""


class ValidationError(DiyDbError):
    """Raised when record validation fails."""


class TransactionError(DiyDbError):
    """Raised on transaction failures."""


class QueryError(DiyDbError):
    """Raised on invalid query construction."""


class StorageError(DiyDbError):
    """Raised on persistence layer failures."""


@dataclass
class Field:
    """
    Field definition for table schemas.

    Attributes:
        name: Field name.
        kind: Python type (or tuple of types).
        required: Whether this field must be present.
        default: Static default or callable default value.
        unique: Uniqueness constraint for table-level checks.
        validator: Additional custom validation function.
        transform: Optional transform applied before validation.
        nullable: Whether None is accepted.
    """

    name: str
    kind: Any = object
    required: bool = False
    default: Any = None
    unique: bool = False
    validator: Optional[Validator] = None
    transform: Optional[Transform] = None
    nullable: bool = False

    def has_default(self) -> bool:
        return self.default is not None

    def get_default(self) -> Any:
        if callable(self.default):
            return self.default()
        return self.default

    def normalize(self, value: Any) -> Any:
        if value is None:
            if self.nullable:
                return None
            if self.required and not self.has_default():
                raise ValidationError(f"Field '{self.name}' cannot be null")

        if self.transform is not None:
            value = self.transform(value)

        if value is None and self.nullable:
            return None

        if self.kind is not object and value is not None and not isinstance(value, self.kind):
            raise ValidationError(
                f"Field '{self.name}' must be {self.kind}, got {type(value)}"
            )

        if self.validator is not None:
            self.validator(value)

        return value


@dataclass
class Index:
    """In-memory index metadata."""

    field_names: Tuple[str, ...]
    unique: bool = False
    mapping: Dict[Tuple[Any, ...], List[int]] = field(default_factory=dict)

    @property
    def key(self) -> str:
        return "|".join(self.field_names)


@dataclass
class Migration:
    """Simple migration unit."""

    version: int
    name: str
    apply: Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class Hook:
    """Hook registry item."""

    event: str
    callback: Callable[..., None]


@dataclass
class QueryPlan:
    """Compiled query plan for diagnostics."""

    filters: List[str] = field(default_factory=list)
    order_by: List[Tuple[str, bool]] = field(default_factory=list)
    limit: Optional[int] = None
    offset: int = 0


@dataclass
class Stats:
    """Database usage stats snapshot."""

    table_count: int
    record_count: int
    file_size_bytes: int
    updated_at: str


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_list(value: Optional[Iterable[Any]]) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return list(value)


def deep_copy_record(record: Record) -> Record:
    result: Record = {}
    for key, value in record.items():
        if isinstance(value, dict):
            result[key] = deep_copy_record(value)
        elif isinstance(value, list):
            copied = []
            for item in value:
                if isinstance(item, dict):
                    copied.append(deep_copy_record(item))
                else:
                    copied.append(item)
            result[key] = copied
        else:
            result[key] = value
    return result
