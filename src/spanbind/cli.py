from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from spanbind.api import bind
from spanbind.types import BoundClaim, UnboundClaim, sha256_text


def _read_sources(source_dir: Path) -> list[dict[str, str]]:
    if not source_dir.is_dir():
        raise SystemExit(f"source directory not found: {source_dir}")
    docs: list[dict[str, str]] = []
    paths = sorted(
        p
        for p in source_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".txt", ".md", ".json"}
    )
    if not paths:
        raise SystemExit(f"no .txt/.md/.json files in {source_dir}")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            payload = json.loads(text)
            if isinstance(payload, dict) and "text" in payload:
                docs.append(
                    {
                        "id": str(payload.get("id", path.stem)),
                        "text": str(payload["text"]),
                    }
                )
                continue
            if isinstance(payload, list):
                for i, item in enumerate(payload):
                    if isinstance(item, dict) and "text" in item:
                        docs.append(
                            {
                                "id": str(item.get("id", f"{path.stem}-{i}")),
                                "text": str(item["text"]),
                            }
                        )
                continue
        docs.append({"id": path.name, "text": text})
    return docs


def _result_row(item: BoundClaim | UnboundClaim) -> dict[str, Any]:
    if isinstance(item, BoundClaim):
        return {
            "sentence": item.sentence,
            "span": item.span.to_dict(),
            "hash": item.span.sha256,
            "score": item.score,
            "binder": item.binder,
        }
    return item.to_dict()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spanbind",
        description="Bind an answer file to source files and exit non-zero on unbound claims.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("check", help="check --answer FILE --source DIR")
    check.add_argument("--answer", required=True, type=Path, help="path to the answer text")
    check.add_argument(
        "--source",
        required=True,
        type=Path,
        help="directory of source .txt/.md/.json documents",
    )
    check.add_argument(
        "--min-overlap",
        type=float,
        default=None,
        help="heuristic coverage threshold (default: package default)",
    )
    check.add_argument(
        "--binder",
        choices=("heuristic", "llm", "auto"),
        default="heuristic",
        help="heuristic is local; llm requires SPANBIND_LLM_API_KEY",
    )
    check.add_argument("--json", action="store_true", help="print machine-readable bindings")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd != "check":
        return 2
    answer_path: Path = args.answer
    if not answer_path.is_file():
        print(f"answer file not found: {answer_path}", file=sys.stderr)
        return 2
    answer = answer_path.read_text(encoding="utf-8")
    sources = _read_sources(args.source)
    kwargs: dict[str, Any] = {"binder": args.binder}
    if args.min_overlap is not None:
        kwargs["min_overlap"] = args.min_overlap
    results = bind(answer, sources, **kwargs)
    unbound = [r for r in results if isinstance(r, UnboundClaim)]
    if args.json:
        print(
            json.dumps(
                {
                    "answer_sha256": sha256_text(answer),
                    "bindings": [_result_row(r) for r in results],
                    "unbound": len(unbound),
                },
                indent=2,
            )
        )
    else:
        for item in results:
            if isinstance(item, BoundClaim):
                s = item.span
                print(
                    f"BOUND  {s.doc_id}:{s.start}-{s.end}  sha256={s.sha256[:12]}…  {item.sentence}"
                )
            else:
                print(f"UNBOUND ({item.best_score:.2f}) {item.sentence}  [{item.reason}]")
        print(f"{len(results) - len(unbound)} bound, {len(unbound)} unbound")
    return 1 if unbound else 0


if __name__ == "__main__":
    raise SystemExit(main())
