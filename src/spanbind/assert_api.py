from __future__ import annotations

from typing import Any

from spanbind.api import bind
from spanbind.exceptions import UnboundClaimError
from spanbind.heuristic import DEFAULT_MIN_OVERLAP
from spanbind.types import UnboundClaim


def assert_bound(
    answer: str,
    sources: list[Any],
    *,
    min_overlap: float = DEFAULT_MIN_OVERLAP,
    binder: str = "heuristic",
) -> None:
    """Fail if any answer sentence is not bound to a source span."""
    results = bind(answer, sources, binder=binder, min_overlap=min_overlap)  # type: ignore[arg-type]
    unbound = [r for r in results if isinstance(r, UnboundClaim)]
    if unbound:
        raise UnboundClaimError(unbound)
