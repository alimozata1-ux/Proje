from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True)
class FilteredResponse:
    spoken: str
    code: str
    has_code: bool


class CodeFilter:
    CODE_FENCE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)

    INLINE_PATTERNS = [
        r"<\?php[\s\S]*?\?>",
        r"<script[\s\S]*?<\/script>",
        r"\bfor\s+i\s+in\s+range\s*\(",
        r"\bwhile\s+\w+\s*:",
        r"\bdef\s+\w+\s*\(",
        r"\bclass\s+\w+\s*:",
        r"\bSELECT\s+.+?\s+FROM\b",
        r"\bINSERT\s+INTO\b",
        r"\bUPDATE\s+\w+\s+SET\b",
        r"\bDELETE\s+FROM\b",
        r"\bfunction\s+\w+\s*\(",
        r"\bconst\s+\w+\s*=",
        r"\blet\s+\w+\s*=",
        r"\bvar\s+\w+\s*=",
        r"\bif\s*\(.+\)\s*\{",
        r"\breturn\s+.+;",
    ]

    def split(self, text: str) -> FilteredResponse:
        code_blocks = self.CODE_FENCE_RE.findall(text)
        cleaned = self.CODE_FENCE_RE.sub("", text)

        for pattern in self.INLINE_PATTERNS:
            found = re.findall(pattern, cleaned, flags=re.IGNORECASE)
            if not found:
                continue
            code_blocks.extend(found)
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        spoken = self._normalize_text(cleaned)
        code = "\n\n".join([c.strip() for c in code_blocks if c.strip()])
        return FilteredResponse(spoken=spoken, code=code, has_code=bool(code))

    def _normalize_text(self, text: str) -> str:
        text = text.replace("\r", "\n")
        lines = [ln.strip() for ln in text.split("\n")]
        collapsed = [ln for ln in lines if ln]
        return "\n".join(collapsed).strip()

    def is_likely_code(self, text: str) -> bool:
        if self.CODE_FENCE_RE.search(text):
            return True
        for pattern in self.INLINE_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return True
        return False
