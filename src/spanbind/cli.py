from __future__ import annotations

import argparse
import json
import sys
from importlib.resources import files
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


def _print_results(
    results: list[BoundClaim | UnboundClaim],
    *,
    as_json: bool,
    answer: str,
    label: str | None = None,
) -> list[UnboundClaim]:
    unbound = [r for r in results if isinstance(r, UnboundClaim)]
    if as_json:
        payload: dict[str, Any] = {
            "answer_sha256": sha256_text(answer),
            "bindings": [_result_row(r) for r in results],
            "unbound": len(unbound),
        }
        if label is not None:
            payload["example"] = label
        print(json.dumps(payload, indent=2))
        return unbound
    if label:
        print(f"=== {label} ===")
    for item in results:
        if isinstance(item, BoundClaim):
            s = item.span
            print(
                f"BOUND  {s.doc_id}:{s.start}-{s.end}  sha256={s.sha256[:12]}…  {item.sentence}"
            )
        else:
            print(f"UNBOUND ({item.best_score:.2f}) {item.sentence}  [{item.reason}]")
    print(f"{len(results) - len(unbound)} bound, {len(unbound)} unbound")
    return unbound


def _demo_corpus() -> tuple[str, str, list[dict[str, str]]]:
    root = files("spanbind").joinpath("data")
    bound = root.joinpath("answer_bound.txt").read_text(encoding="utf-8")
    unbound = root.joinpath("answer_unbound.txt").read_text(encoding="utf-8")
    sources: list[dict[str, str]] = []
    src_dir = root.joinpath("sources")
    for name in ("hours.txt", "policy.txt"):
        path = src_dir.joinpath(name)
        sources.append({"id": name, "text": path.read_text(encoding="utf-8")})
    return bound, unbound, sources


def _run_demo(*, as_json: bool) -> int:
    bound_answer, unbound_answer, sources = _demo_corpus()
    bound_results = bind(bound_answer, sources)
    unbound_results = bind(unbound_answer, sources)
    bound_unbound = _print_results(
        bound_results, as_json=as_json, answer=bound_answer, label="bound"
    )
    unbound_unbound = _print_results(
        unbound_results, as_json=as_json, answer=unbound_answer, label="unbound"
    )
    ok = (not bound_unbound) and bool(unbound_unbound)
    if not as_json:
        if ok:
            print(
                "demo ok: bound example fully bound; unbound example has unbound claims"
            )
        else:
            print(
                "demo failed: expected the bound example to bind and the unbound example to unbind",
                file=sys.stderr,
            )
    return 0 if ok else 1


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
    demo = sub.add_parser(
        "demo",
        help="run built-in bound and unbound examples (package data); exit 0 if both behave",
    )
    demo.add_argument("--json", action="store_true", help="print machine-readable bindings")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "demo":
        return _run_demo(as_json=args.json)
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
    unbound = _print_results(results, as_json=args.json, answer=answer)
    return 1 if unbound else 0


if __name__ == "__main__":
    raise SystemExit(main())
