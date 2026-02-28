from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class TokenLine:
    line_no: int
    indent: int
    content: str


class ProtonLexer:
    """Line-based lexer for Proton."""

    def tokenize(self, source: str) -> List[TokenLine]:
        tokens: List[TokenLine] = []
        for idx, raw in enumerate(source.splitlines(), start=1):
            if not raw.strip() or raw.strip().startswith("//"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            tokens.append(TokenLine(line_no=idx, indent=indent, content=raw.strip()))
        return tokens
