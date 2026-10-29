# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""The Codex specification quotes two guide pages; the quotes must not drift.

``codex/SPEC.md`` has the agent write the Quickstart's ``first_agent.py`` and
the first controlled action's ``controlled_refund.py`` verbatim. The pages are
the source of truth (the specification says so), so every Python block in the
specification has to be one of theirs, character for character.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _blocks(path: Path) -> list[str]:
    return [block.strip() for block in BLOCK.findall(path.read_text(encoding="utf-8"))]


def test_spec_quotes_the_guide_pages_verbatim() -> None:
    spec = _blocks(ROOT / "codex" / "SPEC.md")
    pages = _blocks(ROOT / "docs" / "how-to" / "quickstart.md") + _blocks(
        ROOT / "docs" / "how-to" / "first-controlled-action.md"
    )
    assert len(spec) == 2, "the specification quotes exactly the two files"
    for block in spec:
        assert block in pages, f"not on a guide page: {block.splitlines()[0]!r}"


def test_spec_names_the_outputs_the_pages_promise() -> None:
    spec = (ROOT / "codex" / "SPEC.md").read_text(encoding="utf-8")
    controlled = (ROOT / "docs" / "how-to" / "first-controlled-action.md").read_text(
        encoding="utf-8"
    )
    expected = re.search(r"Expected output:\n\n```text\n(.*?)```", controlled, re.DOTALL)
    assert expected is not None
    assert expected.group(1) in spec, "the six expected lines must match the page"
    assert "ORD-7842" in spec and "delivered" in spec
