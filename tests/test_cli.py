from pathlib import Path

from spanbind.cli import main

FIX = Path(__file__).resolve().parents[1] / "examples" / "starter"


def test_cli_ok(capsys):
    code = main(
        [
            "check",
            "--answer",
            str(FIX / "answer_ok.txt"),
            "--source",
            str(FIX / "sources"),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "BOUND" in out
    assert "0 unbound" in out


def test_cli_unbound_exits_one(capsys):
    code = main(
        [
            "check",
            "--answer",
            str(FIX / "answer_bad.txt"),
            "--source",
            str(FIX / "sources"),
        ]
    )
    assert code == 1
    out = capsys.readouterr().out
    assert "UNBOUND" in out


def test_cli_json(capsys):
    code = main(
        [
            "check",
            "--answer",
            str(FIX / "answer_ok.txt"),
            "--source",
            str(FIX / "sources"),
            "--json",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert '"bindings"' in out
    assert '"hash"' in out


def test_cli_missing_answer(tmp_path):
    code = main(["check", "--answer", str(tmp_path / "nope.txt"), "--source", str(FIX / "sources")])
    assert code == 2
