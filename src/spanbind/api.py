from __future__ import annotations

from typing import Any, Literal

from spanbind.heuristic import DEFAULT_MIN_OVERLAP, bind_heuristic
from spanbind.llm import LlmBinderUnavailable, bind_llm, llm_configured
from spanbind.sentences import split_sentences
from spanbind.types import BoundClaim, UnboundClaim, normalize_sources

BinderName = Literal["heuristic", "llm", "auto"]


def bind(
    answer: str,
    sources: list[Any],
    *,
    binder: BinderName = "heuristic",
    min_overlap: float = DEFAULT_MIN_OVERLAP,
) -> list[BoundClaim | UnboundClaim]:
    """Map each sentence in *answer* to a source span or an UnboundClaim.

    *sources* may be a list of strings or dicts ``{"id": ..., "text": ...}``.
    The default binder is a token-overlap heuristic. The LLM binder runs only
    when ``binder="llm"`` or ``binder="auto"`` *and* ``SPANBIND_LLM_API_KEY``
    is set; it is never called just because a key exists when binder is
    ``heuristic``.
    """
    docs = normalize_sources(sources)
    sentences = [s.text for s in split_sentences(answer)]
    if not sentences:
        return []
    if not docs:
        return [
            UnboundClaim(sentence=s, reason="no-sources", binder=binder)
            for s in sentences
        ]

    use_llm = binder == "llm" or (binder == "auto" and llm_configured())
    if binder == "llm" and not llm_configured():
        raise LlmBinderUnavailable(
            "binder='llm' requires SPANBIND_LLM_API_KEY; use binder='heuristic' otherwise"
        )
    if use_llm:
        return bind_llm(sentences, docs, min_overlap=min_overlap)
    return bind_heuristic(sentences, docs, min_overlap=min_overlap)
