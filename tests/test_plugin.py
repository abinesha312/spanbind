import pytest

from spanbind import assert_bound
from spanbind.exceptions import UnboundClaimError

SRC = [{"id": "a", "text": "Water boils at 100 degrees Celsius at standard pressure."}]


def test_assert_bound_passes():
    assert_bound("Water boils at 100 degrees Celsius at standard pressure.", SRC)


def test_assert_bound_fails_on_hallucination():
    with pytest.raises(UnboundClaimError) as excinfo:
        assert_bound("Water boils at 1000 degrees Celsius on the moon.", SRC)
    assert excinfo.value.unbound
