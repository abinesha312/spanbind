from __future__ import annotations

from typing import Any

import pytest

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
    """Fail the current test if any answer sentence is not bound to a source span."""
    results = bind(answer, sources, binder=binder, min_overlap=min_overlap)  # type: ignore[arg-type]
    unbound = [r for r in results if isinstance(r, UnboundClaim)]
    if unbound:
        raise UnboundClaimError(unbound)


def pytest_assertrepr_compare(op: str, left: object, right: object) -> list[str] | None:
    # Hook reserved so the plugin is a real pytest plugin even if unused.
    del op, left, right
    return None


@pytest.fixture
def spanbind_assert():
    """Expose assert_bound as a fixture for tests that prefer injection."""
    return assert_bound
