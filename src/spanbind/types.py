from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Union


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SourceDoc:
    """A retrieval document the answer is allowed to cite."""

    id: str
    text: str

    @property
    def sha256(self) -> str:
        return sha256_text(self.text)


@dataclass(frozen=True)
class SourceSpan:
    """Character span inside one source document, plus a hash of that source."""

    doc_id: str
    start: int
    end: int
    sha256: str
    excerpt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BoundClaim:
    sentence: str
    span: SourceSpan
    score: float = 0.0
    binder: str = "heuristic"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["hash"] = self.span.sha256
        return data


@dataclass(frozen=True)
class UnboundClaim:
    """A sentence that could not be mapped to any source span."""

    sentence: str
    reason: str
    best_score: float = 0.0
    binder: str = "heuristic"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


Binding = Union[BoundClaim, UnboundClaim]


def normalize_sources(sources: list[Any]) -> list[SourceDoc]:
    docs: list[SourceDoc] = []
    for i, item in enumerate(sources):
        if isinstance(item, SourceDoc):
            docs.append(item)
            continue
        if isinstance(item, str):
            docs.append(SourceDoc(id=f"doc-{i}", text=item))
            continue
        if isinstance(item, dict):
            text = item.get("text")
            if text is None:
                raise TypeError("source dict must include a 'text' field")
            doc_id = str(item.get("id", item.get("doc_id", f"doc-{i}")))
            docs.append(SourceDoc(id=doc_id, text=str(text)))
            continue
        raise TypeError(
            f"source must be str, SourceDoc, or dict with text; got {type(item)!r}"
        )
    return docs
