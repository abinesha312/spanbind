# Measured numbers (do not invent more)

Source: clean venv, `pip install "git+https://github.com/abinesha312/spanbind.git"`, then `spanbind demo`.

Box: Linux, Python 3.13. Date: 2026-08-24 America/Chicago.

This is **not** a published benchmark and not a user study.

## `spanbind demo`

Bound example (packaged `answer_bound.txt` + `data/sources/`):

- 2 sentences bound, 0 unbound
- Refunds sentence → `policy.txt:0-87` sha256 prefix `a760f22d2b2c`
- Support-desk sentence → `hours.txt:4-81` sha256 prefix `1f168d512099`

Unbound example (packaged `answer_unbound.txt`):

- 1 bound, 1 unbound
- Unbound sentence: “Customers receive a lifetime warranty on every license.” reason `below-overlap-threshold` (overlap 0.00)
- Process exit 0 (`demo ok`)

## What this does not show

No precision/recall on a public corpus. No third-party installs. No PyPI downloads. Heuristic binder only (no LLM key).
