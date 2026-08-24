from __future__ import annotations

import re
from dataclasses import dataclass

# Split after sentence-ending punctuation when the next token looks like a new sentence.
_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")
_WS = re.compile(r"\s+")


@dataclass(frozen=True)
class Sentence:
    text: str
    start: int
    end: int


def split_sentences(answer: str) -> list[Sentence]:
    """Split *answer* into sentences with original character offsets.

    This is a punctuation heuristic, not a linguistic parser. Lists, headings,
    and answers without terminal punctuation become a single sentence each
    (or one whole-answer sentence).
    """
    if not answer or not answer.strip():
        return []

    pieces: list[str] = []
    last = 0
    for match in _SPLIT.finditer(answer):
        pieces.append(answer[last : match.start()])
        last = match.end()
    pieces.append(answer[last:])

    sentences: list[Sentence] = []
    cursor = 0
    for piece in pieces:
        # Preserve offsets against the original string.
        idx = answer.find(piece, cursor)
        if idx < 0:
            idx = cursor
        text = piece.strip()
        if text:
            # Map stripped text back to the piece so start/end stay in *answer*.
            lead = len(piece) - len(piece.lstrip())
            sentences.append(
                Sentence(text=text, start=idx + lead, end=idx + lead + len(text))
            )
        cursor = idx + len(piece)
    return sentences
