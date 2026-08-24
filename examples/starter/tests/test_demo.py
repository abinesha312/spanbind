from pathlib import Path

from spanbind import assert_bound, bind
from spanbind.exceptions import UnboundClaimError

from demo import fake_generate, load_sources

ROOT = Path(__file__).resolve().parents[1]


def test_plugin_accepts_grounded_answer():
    sources = load_sources()
    answer = (ROOT / "answer_ok.txt").read_text(encoding="utf-8")
    assert_bound(answer, sources)


def test_plugin_rejects_warranty_hallucination():
    sources = load_sources()
    answer = (ROOT / "answer_bad.txt").read_text(encoding="utf-8")
    try:
        assert_bound(answer, sources)
    except UnboundClaimError as exc:
        assert any("warranty" in u.sentence.lower() for u in exc.unbound)
    else:
        raise AssertionError("expected UnboundClaimError")


def test_fake_generate_is_bindable():
    sources = load_sources()
    answer = fake_generate("refunds support desk", sources)
    results = bind(answer, sources)
    assert results
    assert all(item.__class__.__name__ == "BoundClaim" for item in results)
