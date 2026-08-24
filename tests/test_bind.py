from __future__ import annotations

import hashlib

import pytest

from spanbind import BoundClaim, UnboundClaim, bind
from spanbind.llm import LlmBinderUnavailable
from spanbind.types import sha256_text


FRANCE = "Paris is the capital of France. Lyon is a large city in France."
POLICY = (
    "Refunds are available within 30 days of purchase if the software has not been activated. "
    "Activated licenses are not refundable."
)


def test_bind_maps_sentence_to_offsets_and_document_hash():
    sources = [{"id": "geo", "text": FRANCE}]
    results = bind("Paris is the capital of France.", sources)
    assert len(results) == 1
    item = results[0]
    assert isinstance(item, BoundClaim)
    assert item.span.doc_id == "geo"
    assert FRANCE[item.span.start : item.span.end]
    assert "Paris" in item.span.excerpt
    assert item.span.sha256 == sha256_text(FRANCE)
    assert item.to_dict()["hash"] == item.span.sha256


def test_plain_string_sources_get_stable_ids():
    results = bind("Paris is the capital of France.", [FRANCE])
    assert isinstance(results[0], BoundClaim)
    assert results[0].span.doc_id == "doc-0"


def test_unbound_when_claim_not_in_sources():
    results = bind("The moon is made of green cheese.", [{"id": "geo", "text": FRANCE}])
    assert len(results) == 1
    assert isinstance(results[0], UnboundClaim)
    assert results[0].reason == "below-overlap-threshold"


def test_mixed_answer_binds_only_supported_sentences():
    answer = (
        "Refunds are available within 30 days of purchase if the software has not been activated. "
        "Every customer receives a lifetime warranty."
    )
    results = bind(answer, [{"id": "policy", "text": POLICY}])
    kinds = [type(r).__name__ for r in results]
    assert kinds == ["BoundClaim", "UnboundClaim"]
    assert "warranty" in results[1].sentence.lower()


def test_empty_answer_returns_empty_list():
    assert bind("   ", [FRANCE]) == []


def test_no_sources_marks_every_sentence_unbound():
    results = bind("Paris is the capital of France.", [])
    assert all(isinstance(r, UnboundClaim) for r in results)
    assert results[0].reason == "no-sources"


def test_too_few_content_tokens():
    results = bind("Yes.", [{"id": "geo", "text": FRANCE}])
    assert isinstance(results[0], UnboundClaim)
    assert results[0].reason == "too-few-content-tokens"


def test_document_hash_changes_when_source_bytes_change():
    a = bind("Paris is the capital of France.", [{"id": "g", "text": FRANCE}])[0]
    b = bind(
        "Paris is the capital of France.",
        [{"id": "g", "text": FRANCE + " Extra."}],
    )[0]
    assert isinstance(a, BoundClaim) and isinstance(b, BoundClaim)
    assert a.span.sha256 != b.span.sha256
    assert a.span.sha256 == hashlib.sha256(FRANCE.encode()).hexdigest()


def test_llm_binder_without_key_raises(monkeypatch):
    monkeypatch.delenv("SPANBIND_LLM_API_KEY", raising=False)
    with pytest.raises(LlmBinderUnavailable):
        bind("Paris is the capital of France.", [FRANCE], binder="llm")


def test_auto_without_key_stays_heuristic(monkeypatch):
    monkeypatch.delenv("SPANBIND_LLM_API_KEY", raising=False)
    results = bind("Paris is the capital of France.", [FRANCE], binder="auto")
    assert isinstance(results[0], BoundClaim)
    assert results[0].binder == "heuristic"


def test_reject_bad_source_type():
    with pytest.raises(TypeError):
        bind("Paris is the capital of France.", [123])  # type: ignore[list-item]


def test_wrong_number_does_not_bind_to_similar_sentence():
    src = [{"id": "sci", "text": "Water boils at 100 degrees Celsius at standard pressure."}]
    results = bind("Water boils at 1000 degrees Celsius on the moon.", src)
    assert isinstance(results[0], UnboundClaim)
