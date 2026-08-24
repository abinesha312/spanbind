# spanbind

**Version 0.1.0 · License MIT**

`spanbind` is a small Python library, pytest plugin, and CLI that **fails a check when an LLM or RAG answer contains sentences that are not bound to a source span**.

A bound sentence maps to:

- `doc_id`
- `start` / `end` character offsets in that document (half-open `[start, end)`)
- `sha256` of the **full source document text** (so a swapped corpus is visible)

Unbound sentences come back as `UnboundClaim` and fail `assert_bound` / `spanbind check`.

This is an original, local tool. The default binder is a **sentence-split + token-overlap heuristic**. It is **not** a published attribution method, not a substitute for human review, and not an evaluation of any model vendor.

## Install

From a clone of this repository:

```bash
python -m pip install -e ".[dev]"
```

That registers:

- the `spanbind` import
- the `spanbind` CLI
- a pytest plugin (`assert_bound` is importable as `from spanbind import assert_bound`)

## Library

```python
from spanbind import bind, BoundClaim, UnboundClaim

answer = "Paris is the capital of France. The moon is made of cheese."
sources = [
    {"id": "facts", "text": "Paris is the capital of France. Lyon is a city in France."},
]
for item in bind(answer, sources):
    if isinstance(item, BoundClaim):
        print(item.sentence, item.span.doc_id, item.span.start, item.span.end, item.span.sha256)
    else:
        print("unbound:", item.sentence, item.reason)
```

`sources` may be `list[str]` or `list[{"id", "text"}]`.

`bind(..., binder="heuristic")` is the default.

`bind(..., binder="llm")` calls a chat Completions API **only** when `SPANBIND_LLM_API_KEY` is set. Optional: `SPANBIND_LLM_BASE_URL`, `SPANBIND_LLM_MODEL`. If you pass `binder="llm"` without the key, it raises. `binder="auto"` uses the LLM path only when the key is present.

No paid API is required for normal use.

## pytest plugin

```python
from spanbind import assert_bound

def test_grounded():
    assert_bound(
        "Paris is the capital of France.",
        [{"id": "wiki", "text": "Paris is the capital of France."}],
    )
```

`assert_bound` raises `UnboundClaimError` (a subclass of `AssertionError`) when any sentence fails to bind.

## CLI

```bash
spanbind check --answer path/to/answer.txt --source path/to/sources_dir
```

`--source` is a directory of `.txt`, `.md`, or `.json` files (`{"id","text"}` or a list of those). Exit code `1` if any sentence is unbound. Add `--json` for machine-readable bindings.

## Example

See `examples/starter/` for a tiny retrieve-then-generate stand-in (no model) and tests that use the plugin.

```bash
python -m pip install -e ".[dev]"
cd examples/starter
python demo.py
pytest
```

From the repo root:

```bash
pytest
spanbind check --answer examples/starter/answer_ok.txt --source examples/starter/sources
```

## How to fork

1. Copy this tree or clone it.
2. Change `name` / version / author in `pyproject.toml` if you publish elsewhere.
3. Keep or replace `LICENSE` (MIT).
4. Tighten `heuristic.py` or add another binder module; keep the `bind` / `assert_bound` / CLI surface if you want drop-in tests.
5. Do not treat the default overlap threshold as a research result. Measure on **your** traces before you enforce it in CI.

## Limitations (read these)

- The heuristic counts **content-token overlap** in a sliding window and refuses a window when the sentence’s digits are missing from it. Paraphrases, numbers written two ways, and “yes/no” answers with almost no content tokens will unbind or can still bind to the wrong window.
- Sentence splitting is punctuation-based. Headings, bullets, and missing periods collapse oddly.
- `sha256` is of the **document**, not of the excerpt alone. Offsets still need the same bytes.
- The optional LLM binder trusts the model for offsets, then only checks they fall inside the named document. That is still not evidence the claim is true.
- There are **no** published accuracy numbers here, **no** named production users, and **no** immigration or “extraordinary ability” claims attached to this repo.

## Related work (not implemented)

Citation checking, NLI-based attribution, and span-grounded QA are active research areas. This package does **not** implement any specific paper, benchmark, or someone else’s unpublished design. If you need those methods, use their code; this is a CI-oriented overlap check.

## License

MIT. See `LICENSE`.
