"""Tiny retrieve-then-generate stand-in: pick source files, stitch an answer, bind it."""

from __future__ import annotations

from pathlib import Path

from spanbind import BoundClaim, UnboundClaim, bind
from spanbind.sentences import split_sentences

ROOT = Path(__file__).resolve().parent


def load_sources() -> list[dict[str, str]]:
    docs = []
    for path in sorted((ROOT / "sources").glob("*.txt")):
        docs.append({"id": path.name, "text": path.read_text(encoding="utf-8")})
    return docs


def fake_generate(question: str, sources: list[dict[str, str]]) -> str:
    """Not an LLM. Copies sentences that share a keyword with the question."""
    q = set(question.lower().split())
    picked: list[str] = []
    for doc in sources:
        for sent in split_sentences(doc["text"]):
            words = set(sent.text.lower().split())
            if q & words:
                picked.append(sent.text)
    return " ".join(picked) if picked else "I do not know."


def main() -> None:
    sources = load_sources()
    question = "When are refunds available and when is the support desk staffed?"
    answer = fake_generate(question, sources)
    print("Q:", question)
    print("A:", answer)
    print()
    for item in bind(answer, sources):
        if isinstance(item, BoundClaim):
            s = item.span
            print(f"BOUND {s.doc_id} [{s.start}:{s.end}] hash={s.sha256[:16]}…")
            print(f"  {item.sentence}")
        else:
            print(f"UNBOUND {item.reason}: {item.sentence}")


if __name__ == "__main__":
    main()
