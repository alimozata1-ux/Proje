"""Query builder and predicate helpers for diydb."""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .types import Predicate, QueryError, QueryPlan, Record


@dataclass
class Condition:
    label: str
    predicate: Predicate


@dataclass
class Query:
    """
    Builder-style query object.

    Example:
        q = Query().where_eq("type", "image").order("uploadedAt", desc=True).limit_to(10)
    """

    _conditions: List[Condition] = field(default_factory=list)
    _order_by: List[Tuple[str, bool]] = field(default_factory=list)
    _limit: Optional[int] = None
    _offset: int = 0

    def clone(self) -> "Query":
        q = Query()
        q._conditions = list(self._conditions)
        q._order_by = list(self._order_by)
        q._limit = self._limit
        q._offset = self._offset
        return q

    def where(self, label: str, predicate: Predicate) -> "Query":
        if not label:
            raise QueryError("Condition label cannot be empty")
        self._conditions.append(Condition(label=label, predicate=predicate))
        return self

    def where_eq(self, field: str, value: Any) -> "Query":
        return self.where(f"{field} == {value!r}", lambda rec: rec.get(field) == value)

    def where_ne(self, field: str, value: Any) -> "Query":
        return self.where(f"{field} != {value!r}", lambda rec: rec.get(field) != value)

    def where_in(self, field: str, values: Iterable[Any]) -> "Query":
        value_set = set(values)
        return self.where(f"{field} in {sorted(value_set)!r}", lambda rec: rec.get(field) in value_set)

    def where_not_in(self, field: str, values: Iterable[Any]) -> "Query":
        value_set = set(values)
        return self.where(f"{field} not in {sorted(value_set)!r}", lambda rec: rec.get(field) not in value_set)

    def where_gt(self, field: str, value: Any) -> "Query":
        return self.where(f"{field} > {value!r}", lambda rec: rec.get(field) is not None and rec.get(field) > value)

    def where_gte(self, field: str, value: Any) -> "Query":
        return self.where(f"{field} >= {value!r}", lambda rec: rec.get(field) is not None and rec.get(field) >= value)

    def where_lt(self, field: str, value: Any) -> "Query":
        return self.where(f"{field} < {value!r}", lambda rec: rec.get(field) is not None and rec.get(field) < value)

    def where_lte(self, field: str, value: Any) -> "Query":
        return self.where(f"{field} <= {value!r}", lambda rec: rec.get(field) is not None and rec.get(field) <= value)

    def where_between(self, field: str, low: Any, high: Any, inclusive: bool = True) -> "Query":
        if inclusive:
            return self.where(
                f"{field} between {low!r} and {high!r}",
                lambda rec: rec.get(field) is not None and low <= rec.get(field) <= high,
            )
        return self.where(
            f"{field} between ({low!r}, {high!r})",
            lambda rec: rec.get(field) is not None and low < rec.get(field) < high,
        )

    def where_exists(self, field: str) -> "Query":
        return self.where(f"{field} exists", lambda rec: field in rec)

    def where_missing(self, field: str) -> "Query":
        return self.where(f"{field} missing", lambda rec: field not in rec)

    def where_truthy(self, field: str) -> "Query":
        return self.where(f"truthy({field})", lambda rec: bool(rec.get(field)))

    def where_falsy(self, field: str) -> "Query":
        return self.where(f"falsy({field})", lambda rec: not bool(rec.get(field)))

    def where_startswith(self, field: str, prefix: str) -> "Query":
        return self.where(
            f"{field}.startswith({prefix!r})",
            lambda rec: isinstance(rec.get(field), str) and rec.get(field).startswith(prefix),
        )

    def where_endswith(self, field: str, suffix: str) -> "Query":
        return self.where(
            f"{field}.endswith({suffix!r})",
            lambda rec: isinstance(rec.get(field), str) and rec.get(field).endswith(suffix),
        )

    def where_contains(self, field: str, value: Any) -> "Query":
        def _pred(rec: Record) -> bool:
            current = rec.get(field)
            if isinstance(current, (list, tuple, set, str)):
                return value in current
            return False

        return self.where(f"contains({field}, {value!r})", _pred)

    def where_matches(self, field: str, pattern: str) -> "Query":
        return self.where(
            f"{field} matches {pattern!r}",
            lambda rec: isinstance(rec.get(field), str) and fnmatch(rec.get(field), pattern),
        )

    def where_custom(self, name: str, fn: Predicate) -> "Query":
        return self.where(f"custom:{name}", fn)

    def and_query(self, other: "Query") -> "Query":
        if not isinstance(other, Query):
            raise QueryError("and_query expects Query")
        for cond in other._conditions:
            self._conditions.append(cond)
        return self

    def or_query(self, *queries: "Query") -> "Query":
        for query in queries:
            if not isinstance(query, Query):
                raise QueryError("or_query expects Query instances")

        built = [q.build_predicate() for q in queries]

        def _pred(rec: Record) -> bool:
            for fn in built:
                if fn(rec):
                    return True
            return False

        labels = [" OR ".join([c.label for c in q._conditions]) for q in queries]
        label = "(" + ") OR (".join(labels) + ")"
        self._conditions.append(Condition(label=label, predicate=_pred))
        return self

    def order(self, field: str, desc: bool = False) -> "Query":
        if not field:
            raise QueryError("order field cannot be empty")
        self._order_by.append((field, desc))
        return self

    def limit_to(self, count: Optional[int]) -> "Query":
        if count is None:
            self._limit = None
            return self
        if count < 0:
            raise QueryError("limit cannot be negative")
        self._limit = count
        return self

    def skip(self, count: int) -> "Query":
        if count < 0:
            raise QueryError("offset cannot be negative")
        self._offset = count
        return self

    def build_predicate(self) -> Predicate:
        if not self._conditions:
            return lambda rec: True

        def _pred(rec: Record) -> bool:
            for cond in self._conditions:
                if not cond.predicate(rec):
                    return False
            return True

        return _pred

    def explain(self) -> QueryPlan:
        return QueryPlan(
            filters=[c.label for c in self._conditions],
            order_by=list(self._order_by),
            limit=self._limit,
            offset=self._offset,
        )

    def apply(self, records: Sequence[Record]) -> List[Record]:
        pred = self.build_predicate()
        filtered = [rec for rec in records if pred(rec)]

        for field, desc in reversed(self._order_by):
            filtered.sort(key=lambda rec: rec.get(field), reverse=desc)

        if self._offset:
            filtered = filtered[self._offset :]

        if self._limit is not None:
            filtered = filtered[: self._limit]

        return filtered


def query() -> Query:
    """Convenience constructor."""
    return Query()


def from_filters(filters: Optional[Dict[str, Any]] = None) -> Query:
    """
    Build a query from a simple mapping where values are exact-match filters.
    """
    q = Query()
    if not filters:
        return q
    for key, value in filters.items():
        q.where_eq(key, value)
    return q
