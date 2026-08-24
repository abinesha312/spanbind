from __future__ import annotations

from spanbind.assert_api import assert_bound

__all__ = ["assert_bound"]


def pytest_assertrepr_compare(op: str, left: object, right: object) -> list[str] | None:
    del op, left, right
    return None


def pytest_configure(config):  # type: ignore[no-untyped-def]
    del config


def spanbind_assert():
    return assert_bound


# Fixture registered only when pytest imported this module as a plugin.
try:
    import pytest

    spanbind_assert = pytest.fixture(spanbind_assert)
except ImportError:
    pass
