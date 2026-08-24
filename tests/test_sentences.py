from spanbind.sentences import split_sentences


def test_two_sentences_keep_offsets():
    text = "Alpha is first. Beta is second."
    sents = split_sentences(text)
    assert [s.text for s in sents] == ["Alpha is first.", "Beta is second."]
    assert text[sents[0].start : sents[0].end] == "Alpha is first."
    assert text[sents[1].start : sents[1].end] == "Beta is second."


def test_blank_input():
    assert split_sentences("") == []
    assert split_sentences("   \n") == []
