"""spanbind: bind answer sentences to source character spans, or fail."""

from spanbind.api import bind
from spanbind.exceptions import UnboundClaimError
from spanbind.plugin import assert_bound
from spanbind.types import BoundClaim, SourceDoc, SourceSpan, UnboundClaim

__version__ = "0.1.0"

__all__ = [
    "BoundClaim",
    "SourceDoc",
    "SourceSpan",
    "UnboundClaim",
    "UnboundClaimError",
    "assert_bound",
    "bind",
    "__version__",
]
