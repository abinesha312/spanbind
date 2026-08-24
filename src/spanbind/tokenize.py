from __future__ import annotations

import re
from dataclasses import dataclass

# Small closed-class list so short function words do not inflate overlap.
_STOP = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "if",
        "then",
        "than",
        "that",
        "this",
        "these",
        "those",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "as",
        "by",
        "at",
        "from",
        "it",
        "its",
        "into",
        "about",
        "over",
        "after",
        "before",
        "not",
        "no",
        "nor",
        "so",
        "such",
        "can",
        "may",
        "do",
        "does",
        "did",
        "has",
        "have",
        "had",
        "will",
        "would",
        "should",
        "could",
        "their",
        "there",
        "here",
        "we",
        "you",
        "they",
        "he",
        "she",
        "i",
    }
)

_TOKEN = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int

    @property
    def norm(self) -> str:
        return self.text.lower()


def tokenize(text: str, *, drop_stop: bool = False) -> list[Token]:
    tokens = [Token(m.group(0), m.start(), m.end()) for m in _TOKEN.finditer(text)]
    if drop_stop:
        tokens = [t for t in tokens if t.norm not in _STOP]
    return tokens


def content_norms(text: str) -> list[str]:
    return [t.norm for t in tokenize(text, drop_stop=True)]
