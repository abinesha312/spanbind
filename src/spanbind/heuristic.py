from __future__ import annotations

from spanbind.tokenize import Token, content_norms, tokenize
from spanbind.types import BoundClaim, SourceDoc, SourceSpan, UnboundClaim

# Coverage = |sentence content tokens present in the window| / |sentence content tokens|
DEFAULT_MIN_OVERLAP = 0.55
_MIN_CONTENT_TOKENS = 2


def _is_numeric(tok: str) -> bool:
    return tok.isdigit() or tok.replace(".", "", 1).isdigit()


def _window_coverage(sent: list[str], window: list[Token]) -> float:
    if not sent:
        return 0.0
    present = {t.norm for t in window}
    hits = sum(1 for tok in sent if tok in present)
    score = hits / len(sent)
    # Wrong quantities are a common RAG failure; do not treat them as overlap.
    sent_nums = [tok for tok in sent if _is_numeric(tok)]
    if sent_nums and any(n not in present for n in sent_nums):
        return 0.0
    return score


def best_span(
    sentence: str, doc: SourceDoc, *, max_window_mult: float = 3.0
) -> tuple[SourceSpan | None, float]:
    sent_norms = content_norms(sentence)
    if len(sent_norms) < _MIN_CONTENT_TOKENS:
        return None, 0.0

    tokens = tokenize(doc.text, drop_stop=True)
    if not tokens:
        return None, 0.0

    width = max(len(sent_norms), _MIN_CONTENT_TOKENS)
    max_width = min(len(tokens), max(width, int(width * max_window_mult)))

    best_score = 0.0
    best_i = 0
    best_j = min(width, len(tokens))

    for w in range(width, max_width + 1):
        if w > len(tokens):
            break
        for i in range(0, len(tokens) - w + 1):
            window = tokens[i : i + w]
            score = _window_coverage(sent_norms, window)
            if score > best_score:
                best_score = score
                best_i = i
                best_j = i + w
            if best_score >= 1.0:
                break
        if best_score >= 1.0:
            break

    start = tokens[best_i].start
    end = tokens[best_j - 1].end
    span = SourceSpan(
        doc_id=doc.id,
        start=start,
        end=end,
        sha256=doc.sha256,
        excerpt=doc.text[start:end],
    )
    return span, best_score


def bind_heuristic(
    sentences: list[str],
    docs: list[SourceDoc],
    *,
    min_overlap: float = DEFAULT_MIN_OVERLAP,
) -> list[BoundClaim | UnboundClaim]:
    results: list[BoundClaim | UnboundClaim] = []
    for sentence in sentences:
        sent_norms = content_norms(sentence)
        if len(sent_norms) < _MIN_CONTENT_TOKENS:
            results.append(
                UnboundClaim(
                    sentence=sentence,
                    reason="too-few-content-tokens",
                    best_score=0.0,
                    binder="heuristic",
                )
            )
            continue

        winner: tuple[SourceSpan, float] | None = None
        for doc in docs:
            span, score = best_span(sentence, doc)
            if span is None:
                continue
            if winner is None or score > winner[1]:
                winner = (span, score)

        if winner is None or winner[1] < min_overlap:
            score = 0.0 if winner is None else winner[1]
            results.append(
                UnboundClaim(
                    sentence=sentence,
                    reason="below-overlap-threshold",
                    best_score=score,
                    binder="heuristic",
                )
            )
        else:
            span, score = winner
            results.append(
                BoundClaim(
                    sentence=sentence,
                    span=span,
                    score=score,
                    binder="heuristic",
                )
            )
    return results
