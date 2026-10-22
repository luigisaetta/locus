# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""Unit: the notebook-page scaffolder — docstring parsing, SDK resolution, scaffolding."""

from __future__ import annotations

from pathlib import Path

import pytest
from scripts import gen_notebook_pages as gen


def _notebook(path: Path, name: str, docstring: str | None) -> Path:
    body = f'"""{docstring}"""\n' if docstring is not None else "x = 1\n"
    f = path / name
    f.write_text(body, encoding="utf-8")
    return f


# ── _parse ────────────────────────────────────────────────────────────────────
def test_parse_extracts_number_title_body(tmp_path: Path) -> None:
    f = _notebook(
        tmp_path, "notebook_14_basic.py", "Notebook 14: Basic Agent.\n\nLine one.\nLine two."
    )
    assert gen._parse(f) == (14, "Basic Agent", "Line one.\nLine two.")


def test_parse_unnumbered_name_is_zero_but_title_still_read(tmp_path: Path) -> None:
    f = _notebook(tmp_path, "intro.py", "Notebook 3: Intro.")
    num, title, _ = gen._parse(f)
    assert num == 0 and title == "Intro"


def test_parse_falls_back_to_first_line_when_no_prefix(tmp_path: Path) -> None:
    f = _notebook(tmp_path, "notebook_05_x.py", "Just A Heading\n\nbody")
    _, title, body = gen._parse(f)
    assert title == "Just A Heading" and body == "body"


def test_parse_empty_docstring_yields_empty_title(tmp_path: Path) -> None:
    f = _notebook(tmp_path, "notebook_07_e.py", None)  # no docstring
    assert gen._parse(f) == (7, "", "")


# ── _sdk_examples ─────────────────────────────────────────────────────────────
def test_sdk_examples_from_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "examples").mkdir()
    monkeypatch.setenv("LOCUS_SDK_DIR", str(tmp_path))
    assert gen._sdk_examples() == (tmp_path / "examples").resolve()


def test_sdk_examples_exits_when_nothing_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("LOCUS_SDK_DIR", raising=False)
    monkeypatch.setattr(gen, "ROOT", tmp_path / "repo")  # no sibling ../locus-sdk, no .sdk
    with pytest.raises(SystemExit):
        gen._sdk_examples()


# ── main ──────────────────────────────────────────────────────────────────────
def test_main_scaffolds_skips_and_forces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    examples = tmp_path / "examples"
    examples.mkdir()
    out = tmp_path / "out"
    _notebook(examples, "notebook_01_intro.py", "Notebook 1: Intro.\n\nHello world.")
    _notebook(examples, "notebook_99_bad.py", None)  # placeholder, overwritten next
    (examples / "notebook_99_bad.py").write_text("this is !!! not python", encoding="utf-8")
    _notebook(examples, "notebook_98_empty.py", None)  # valid python, no docstring → no title

    monkeypatch.setattr(gen, "_sdk_examples", lambda: examples)
    monkeypatch.setattr(gen, "OUT", out)
    monkeypatch.setattr("sys.argv", ["gen"])

    gen.main()
    page = out / "notebook_01_intro.md"
    assert page.exists()
    text = page.read_text(encoding="utf-8")
    assert text.startswith("# Notebook 01: Intro\n\nHello world.\n\n## Source")
    assert '--8<-- "examples/notebook_01_intro.py"' in text
    assert "scaffolded 1 new pages" in capsys.readouterr().out

    # Re-run: the existing page is left untouched (no --force).
    gen.main()
    assert "0 new pages" in capsys.readouterr().out

    # --force overwrites.
    monkeypatch.setattr("sys.argv", ["gen", "--force"])
    gen.main()
    assert "scaffolded 1 new pages" in capsys.readouterr().out


def test_source_fence_survives_a_fenced_block_inside_the_example(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A ``` block inside an example must not close the page's Source fence.

    notebook_31 shipped a ```text block inside its module docstring. With a
    three-backtick Source fence that inner fence closed the outer one, and the
    remaining ~315 lines rendered as prose — every ``# comment`` became an <h1>.
    The outer fence is four backticks so the inner one cannot terminate it.
    """
    examples = tmp_path / "examples"
    examples.mkdir()
    out = tmp_path / "out"
    (examples / "notebook_31_fenced.py").write_text(
        '"""Notebook 31: Fenced.\n\nShows output:\n\n```text\nrole: MIRROR\n```\n"""\n'
        "# ---------------------------------------------------------------\n"
        "x = 1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(gen, "_sdk_examples", lambda: examples)
    monkeypatch.setattr(gen, "OUT", out)
    monkeypatch.setattr("sys.argv", ["gen"])

    gen.main()
    capsys.readouterr()
    text = (out / "notebook_31_fenced.md").read_text(encoding="utf-8")
    # The docstring body is copied into the page, so its own fence appears
    # first; the Source block is the final pair and must be four backticks.
    fences = [ln for ln in text.splitlines() if ln.startswith("```")]
    assert fences[-2:] == ["````python", "````"], fences
