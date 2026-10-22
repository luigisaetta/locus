# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""Unit: the cache-bust mkdocs hook appends a content hash to local asset URLs."""

from __future__ import annotations

import hashlib
from pathlib import Path

from hooks.cache_bust import _hashed, on_config


def test_absolute_urls_pass_through(tmp_path: Path) -> None:
    assert _hashed(tmp_path, "https://cdn.example/x.css") == "https://cdn.example/x.css"


def test_already_queried_passes_through(tmp_path: Path) -> None:
    assert _hashed(tmp_path, "locus.css?v=1") == "locus.css?v=1"


def test_missing_file_passes_through(tmp_path: Path) -> None:
    assert _hashed(tmp_path, "nope.css") == "nope.css"


def test_existing_file_gets_content_hash(tmp_path: Path) -> None:
    (tmp_path / "locus.css").write_bytes(b"body{color:red}")
    expected = hashlib.sha256(b"body{color:red}").hexdigest()[:8]
    assert _hashed(tmp_path, "locus.css") == f"locus.css?h={expected}"


def test_on_config_hashes_css_and_str_js_but_leaves_objects(tmp_path: Path) -> None:
    (tmp_path / "a.css").write_bytes(b"a")
    (tmp_path / "b.js").write_bytes(b"b")
    js_obj = {"path": "c.js", "type": "module"}  # non-str entries pass through untouched
    config = {
        "docs_dir": str(tmp_path),
        "extra_css": ["a.css"],
        "extra_javascript": ["b.js", js_obj],
    }
    out = on_config(config)
    assert out["extra_css"][0].startswith("a.css?h=")
    assert out["extra_javascript"][0].startswith("b.js?h=")
    assert out["extra_javascript"][1] == js_obj


def test_on_config_tolerates_missing_keys(tmp_path: Path) -> None:
    out = on_config({"docs_dir": str(tmp_path)})
    assert out["extra_css"] == []
    assert out["extra_javascript"] == []
