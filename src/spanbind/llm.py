from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from spanbind.types import BoundClaim, SourceDoc, SourceSpan, UnboundClaim

ENV_KEY = "SPANBIND_LLM_API_KEY"
ENV_BASE = "SPANBIND_LLM_BASE_URL"
ENV_MODEL = "SPANBIND_LLM_MODEL"
DEFAULT_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


class LlmBinderUnavailable(RuntimeError):
    """LLM binder was requested but is not configured or the call failed."""


def llm_configured() -> bool:
    return bool(os.environ.get(ENV_KEY, "").strip())


def _post_chat(messages: list[dict[str, str]], timeout: float) -> str:
    key = os.environ.get(ENV_KEY, "").strip()
    if not key:
        raise LlmBinderUnavailable(
            f"LLM binder requires {ENV_KEY} in the environment; heuristic bind is the default"
        )
    base = os.environ.get(ENV_BASE, DEFAULT_BASE).rstrip("/")
    model = os.environ.get(ENV_MODEL, DEFAULT_MODEL)
    payload = {
        "model": model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": messages,
    }
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise LlmBinderUnavailable(f"LLM binder request failed: {exc}") from exc
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmBinderUnavailable(f"unexpected LLM response shape: {body!r}") from exc


def bind_llm(
    sentences: list[str],
    docs: list[SourceDoc],
    *,
    min_overlap: float = 0.0,
    timeout: float = 30.0,
) -> list[BoundClaim | UnboundClaim]:
    """Ask a chat API to pick (doc_id, start, end) per sentence.

    Off unless SPANBIND_LLM_API_KEY is set. The model is instructed to copy
    offsets from the provided documents; we still re-check that start/end
    land inside the named document. This is not a published grounding method.
    """
    del min_overlap  # threshold is not used; the model either cites a span or not
    catalog = [
        {
            "id": d.id,
            "sha256": d.sha256,
            "text": d.text,
            "length": len(d.text),
        }
        for d in docs
    ]
    system = (
        "You bind answer sentences to character spans in source documents. "
        "Return JSON object {\"bindings\": [ ... ]} with one object per input "
        "sentence, in order. Each object is either "
        "{\"sentence\": str, \"doc_id\": str, \"start\": int, \"end\": int} "
        "or {\"sentence\": str, \"unbound\": true, \"reason\": str}. "
        "Offsets are 0-based half-open [start, end) into that document's text. "
        "Do not invent offsets that are not a substring of the document."
    )
    user = json.dumps({"sentences": sentences, "sources": catalog})
    raw = _post_chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        timeout=timeout,
    )
    try:
        parsed: Any = json.loads(raw)
        items = parsed["bindings"] if isinstance(parsed, dict) else parsed
        if not isinstance(items, list):
            raise TypeError("bindings is not a list")
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        raise LlmBinderUnavailable(f"LLM binder returned non-JSON bindings: {raw!r}") from exc

    by_id = {d.id: d for d in docs}
    results: list[BoundClaim | UnboundClaim] = []
    for i, sentence in enumerate(sentences):
        item = items[i] if i < len(items) and isinstance(items[i], dict) else {}
        if item.get("unbound") or not item.get("doc_id"):
            results.append(
                UnboundClaim(
                    sentence=sentence,
                    reason=str(item.get("reason") or "llm-unbound"),
                    best_score=0.0,
                    binder="llm",
                )
            )
            continue
        doc = by_id.get(str(item["doc_id"]))
        try:
            start = int(item["start"])
            end = int(item["end"])
        except (KeyError, TypeError, ValueError):
            results.append(
                UnboundClaim(
                    sentence=sentence,
                    reason="llm-invalid-offsets",
                    binder="llm",
                )
            )
            continue
        if doc is None or start < 0 or end > len(doc.text) or start >= end:
            results.append(
                UnboundClaim(
                    sentence=sentence,
                    reason="llm-span-out-of-range",
                    binder="llm",
                )
            )
            continue
        span = SourceSpan(
            doc_id=doc.id,
            start=start,
            end=end,
            sha256=doc.sha256,
            excerpt=doc.text[start:end],
        )
        results.append(BoundClaim(sentence=sentence, span=span, score=1.0, binder="llm"))
    return results
