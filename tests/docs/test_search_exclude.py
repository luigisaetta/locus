# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""Unit: the search-exclude hook marks full source listings, and nothing else."""

from __future__ import annotations

from hooks.search_exclude import exclude_source_listings, on_page_content


NOTEBOOK = (
    '<h2 id="source">Source</h2>\n'
    '<details class="note">\n<summary>Full source — <code>examples/notebook_77.py</code></summary>\n'
    "<pre><code>print('hi')</code></pre>\n</details>"
)
API = (
    '<div class="doc doc-contents">'
    '<details class="mkdocstrings-source"><summary>Source code in <code>src/locus/hooks/base.py</code></summary>'
    '<table class="highlighttable"></table></details></div>'
)


def test_notebook_full_source_block_is_excluded() -> None:
    out = exclude_source_listings(NOTEBOOK)
    assert '<details class="note" data-search-exclude>' in out
    assert out.count("data-search-exclude") == 1


def test_mkdocstrings_source_block_is_excluded() -> None:
    out = exclude_source_listings(API)
    assert '<details class="mkdocstrings-source" data-search-exclude>' in out


def test_other_details_blocks_are_untouched() -> None:
    html = (
        '<details class="note"><summary>Why this matters</summary><p>text</p></details>'
        '<details class="example" open><summary>Usage</summary></details>'
    )
    assert exclude_source_listings(html) == html


def test_hook_entry_point_returns_rewritten_html() -> None:
    assert on_page_content(NOTEBOOK, page=None, config=None, files=None) != NOTEBOOK
