"""Persistence adapters for diydb."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .types import StorageError, now_iso


@dataclass
class StorageAdapter:
    """Base storage adapter interface."""

    def load(self) -> Dict[str, Any]:
        raise NotImplementedError

    def save(self, payload: Dict[str, Any]) -> None:
        raise NotImplementedError

    def size(self) -> int:
        return 0


@dataclass
class JsonFileStorage(StorageAdapter):
    """
    JSON file persistence with atomic writes.

    Payload shape:
    {
      "meta": {...},
      "tables": {...}
    }
    """

    path: str
    indent: int = 2

    def _path(self) -> Path:
        return Path(self.path)

    def _ensure_parent(self) -> None:
        parent = self._path().parent
        parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        p = self._path()
        if not p.exists():
            return {
                "meta": {
                    "version": 1,
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                },
                "tables": {},
            }

        try:
            text = p.read_text(encoding="utf-8")
            data = json.loads(text)
        except Exception as exc:
            raise StorageError(f"Unable to load JSON storage: {exc}") from exc

        if not isinstance(data, dict):
            raise StorageError("Storage payload must be a JSON object")

        data.setdefault("meta", {})
        data.setdefault("tables", {})
        return data

    def save(self, payload: Dict[str, Any]) -> None:
        self._ensure_parent()
        p = self._path()

        payload = dict(payload)
        payload.setdefault("meta", {})
        payload["meta"]["updated_at"] = now_iso()

        fd, tmp = tempfile.mkstemp(prefix=p.name, suffix=".tmp", dir=str(p.parent))
        os.close(fd)
        tmp_path = Path(tmp)

        try:
            tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=self.indent), encoding="utf-8")
            tmp_path.replace(p)
        except Exception as exc:
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            finally:
                raise StorageError(f"Unable to persist JSON storage: {exc}") from exc

    def size(self) -> int:
        p = self._path()
        if not p.exists():
            return 0
        return p.stat().st_size


@dataclass
class MemoryStorage(StorageAdapter):
    """Pure in-memory adapter used for tests or ephemeral usage."""

    payload: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        if self.payload is None:
            self.payload = {
                "meta": {
                    "version": 1,
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                },
                "tables": {},
            }
        return json.loads(json.dumps(self.payload))

    def save(self, payload: Dict[str, Any]) -> None:
        copy_payload = json.loads(json.dumps(payload))
        copy_payload.setdefault("meta", {})
        copy_payload["meta"]["updated_at"] = now_iso()
        self.payload = copy_payload

    def size(self) -> int:
        if self.payload is None:
            return 0
        return len(json.dumps(self.payload).encode("utf-8"))
