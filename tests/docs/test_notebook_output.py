# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""The captured-output tool, tested without running the SDK.

`scripts/notebook_output.py` puts real terminal output on the notebook pages
and re-checks it in CI. The re-check is the part that matters: output on a page
rots the moment the example changes, and rotted output is worse than none —
a reader who runs it and gets something else has no way to tell which of the
two is wrong.

These cover the page surgery, which is where a mistake would be silent: a
section appended twice on every update, or a stale block left in place beside a
fresh one. Running the notebooks themselves is the build job's business; here
the output is supplied directly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import notebook_output  # noqa: E402
from notebook_output import (  # noqa: E402
    PAGES,
    apply,
    main,
    render,
    run_notebook,
    sdk_dir,
    uses_model,
)


PAGE = """\
# Something

Prose about it.

## Source

```python
--8<-- "examples/notebook_74_data_deletion_gate.py"
```
"""


@pytest.fixture
def page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    import notebook_output

    docs = tmp_path / "notebooks"
    docs.mkdir()
    path = docs / "notebook_74_data_deletion_gate.md"
    path.write_text(PAGE)
    monkeypatch.setattr(notebook_output, "DOCS", docs)
    return path


def _apply(text: str, *, write: bool = True) -> bool:
    return apply("notebook_74_data_deletion_gate", "the chain", text, write=write)


def test_output_lands_before_the_source(page: Path) -> None:
    """Read what it does, then read it — not the other way round."""
    _apply("chain intact: True")
    body = page.read_text()

    assert body.index("## Output") < body.index("## Source")
    assert "chain intact: True" in body


def test_updating_replaces_rather_than_appends(page: Path) -> None:
    """The failure this guards is quiet: a page growing a section per run."""
    _apply("first run")
    _apply("second run")
    body = page.read_text()

    assert body.count("## Output") == 1
    assert "second run" in body
    assert "first run" not in body


def test_an_unchanged_page_reports_as_current(page: Path) -> None:
    _apply("stable output")

    assert _apply("stable output") is True


def test_a_changed_notebook_reports_as_stale(page: Path) -> None:
    """This is the check that keeps the pages honest."""
    _apply("old output")

    assert _apply("new output") is False


def test_check_mode_does_not_touch_the_page(page: Path) -> None:
    """``--check`` runs in CI; it must report, not repair."""
    _apply("captured")
    before = page.read_text()

    assert _apply("something else", write=False) is False
    assert page.read_text() == before


def test_a_page_without_a_source_section_is_refused(tmp_path: Path, monkeypatch) -> None:
    """Silently appending to the end would put output nowhere useful."""
    import notebook_output

    docs = tmp_path / "notebooks"
    docs.mkdir()
    (docs / "notebook_74_data_deletion_gate.md").write_text("# Bare\n\nNo source here.\n")
    monkeypatch.setattr(notebook_output, "DOCS", docs)

    with pytest.raises(SystemExit, match="no '## Source' section"):
        _apply("output")


def test_a_missing_page_is_refused(tmp_path: Path, monkeypatch) -> None:
    import notebook_output

    docs = tmp_path / "notebooks"
    docs.mkdir()
    monkeypatch.setattr(notebook_output, "DOCS", docs)

    with pytest.raises(SystemExit, match="no page for"):
        _apply("output")


def test_the_rendered_block_is_fenced_as_text() -> None:
    """Not ```python — this is a transcript, and highlighting it as source
    makes a reader look for code that is not there."""
    block = render("notebook_74_data_deletion_gate", "the chain", "line one\nline two")

    assert "```text\n" in block
    assert "```python" not in block


def test_every_listed_page_exists() -> None:
    """A typo in PAGES would otherwise fail only in CI, against the real SDK."""
    docs = Path(__file__).resolve().parents[2] / "docs" / "notebooks"
    missing = [stem for stem in PAGES if not (docs / f"{stem}.md").is_file()]

    assert not missing, f"PAGES names pages that do not exist: {missing}"


def test_every_listed_page_carries_a_reason() -> None:
    """The reason is printed on the page, so an empty one ships an empty
    sentence to a reader."""
    assert all(reason.strip() for reason in PAGES.values())


# --------------------------------------------------------------------------
# Finding the SDK, and running against it
# --------------------------------------------------------------------------


def test_the_env_var_wins_when_finding_the_sdk(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("LOCUS_SDK_DIR", str(tmp_path))

    assert sdk_dir() == tmp_path


def test_a_relative_sdk_path_is_resolved(tmp_path: Path, monkeypatch) -> None:
    """The subprocess runs with ``cwd`` set to this directory, so a relative
    path would be read relative to itself.

    CI passes ``LOCUS_SDK_DIR=./.sdk``; unresolved, that became
    ``.sdk/.sdk/examples/...``. It passed locally, where the variable happened
    to be absolute, and failed only on the runner.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".sdk").mkdir()
    monkeypatch.setenv("LOCUS_SDK_DIR", "./.sdk")

    resolved = sdk_dir()

    assert resolved.is_absolute()
    assert resolved == (tmp_path / ".sdk").resolve()


def test_no_sdk_anywhere_is_refused(tmp_path: Path, monkeypatch) -> None:
    """Better than running against whatever happens to be importable."""
    monkeypatch.delenv("LOCUS_SDK_DIR", raising=False)
    monkeypatch.setattr(notebook_output, "ROOT", tmp_path)

    with pytest.raises(SystemExit, match="SDK checkout not found"):
        sdk_dir()


def test_a_missing_notebook_names_the_path(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="is the SDK checkout current"):
        run_notebook("notebook_99_nonexistent", tmp_path)


def _fake_sdk(tmp_path: Path, stem: str) -> Path:
    (tmp_path / "examples").mkdir(parents=True)
    (tmp_path / "examples" / f"{stem}.py").write_text("print('hi')\n")
    return tmp_path


def test_a_notebook_that_fails_is_not_captured(tmp_path: Path, monkeypatch) -> None:
    """Capturing a traceback onto the page would publish the breakage as if
    it were the example."""
    import subprocess

    sdk = _fake_sdk(tmp_path, "notebook_74_data_deletion_gate")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 1, "", "Traceback: boom"),
    )

    with pytest.raises(SystemExit, match="exited 1"):
        run_notebook("notebook_74_data_deletion_gate", sdk)


def test_trailing_blank_lines_are_trimmed(tmp_path: Path, monkeypatch) -> None:
    """Otherwise every capture churns the diff by a newline."""
    import subprocess

    sdk = _fake_sdk(tmp_path, "notebook_74_data_deletion_gate")
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a[0], 0, "out\n\n\n", "")
    )

    assert run_notebook("notebook_74_data_deletion_gate", sdk) == "out"


# --------------------------------------------------------------------------
# The two modes end to end
# --------------------------------------------------------------------------


@pytest.fixture
def one_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    docs = tmp_path / "notebooks"
    docs.mkdir()
    path = docs / "notebook_74_data_deletion_gate.md"
    path.write_text(PAGE)
    monkeypatch.setattr(notebook_output, "DOCS", docs)
    monkeypatch.setattr(notebook_output, "PAGES", {"notebook_74_data_deletion_gate": "the chain"})
    monkeypatch.setattr(notebook_output, "sdk_dir", lambda: tmp_path)
    return path


def test_update_writes_and_then_check_passes(one_page: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(notebook_output, "run_notebook", lambda *a: "captured output")

    assert main(["x", "--update"]) == 0
    assert "captured output" in one_page.read_text()
    assert main(["x", "--check"]) == 0
    assert "matches a real run" in capsys.readouterr().out


def test_check_fails_and_names_the_stale_page(one_page: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(notebook_output, "run_notebook", lambda *a: "old")
    main(["x", "--update"])
    monkeypatch.setattr(notebook_output, "run_notebook", lambda *a: "new")

    assert main(["x", "--check"]) == 1
    out = capsys.readouterr().out
    assert "notebook_74_data_deletion_gate.md" in out
    assert "--update" in out, "a failure has to say how to fix it"


def test_a_mode_is_required(one_page: Path) -> None:
    with pytest.raises(SystemExit):
        main(["x"])


# --------------------------------------------------------------------------
# The lead-in describes what the notebook actually runs
# --------------------------------------------------------------------------


def test_a_notebook_without_a_model_is_not_described_as_using_one() -> None:
    """Six of the seven gate notebooks call admit() directly and never build a
    model; the lead-in used to promise a "bundled mock model" on every page."""
    block = render("notebook_72_infra_deploy_gate", "a deploy", "out", with_model=False)

    assert "no model and no credentials" in block
    assert "mock model" not in block


def test_a_notebook_with_a_model_keeps_the_mock_lead_in() -> None:
    block = render("notebook_87_soc_alert_triage", "the triage", "out", with_model=True)

    assert "bundled mock model" in block


def test_model_use_is_read_from_the_notebook_source(tmp_path: Path) -> None:
    examples = tmp_path / "examples"
    examples.mkdir()
    (examples / "uses.py").write_text("from config import get_model\nmodel = get_model()\n")
    (examples / "direct.py").write_text("from locus.control import admit\n")

    assert uses_model("uses", tmp_path) is True
    assert uses_model("direct", tmp_path) is False
    assert uses_model("absent", tmp_path) is False
