from __future__ import annotations

from spanbind.types import UnboundClaim


class UnboundClaimError(AssertionError):
    """Raised when one or more answer sentences have no bound source span."""

    def __init__(self, unbound: list[UnboundClaim], message: str | None = None) -> None:
        self.unbound = unbound
        if message is None:
            lines = ["answer contains unbound claims:"]
            for item in unbound:
                preview = item.sentence.strip().replace("\n", " ")
                if len(preview) > 120:
                    preview = preview[:117] + "..."
                lines.append(f"  - ({item.best_score:.2f}) {preview} [{item.reason}]")
            message = "\n".join(lines)
        super().__init__(message)
