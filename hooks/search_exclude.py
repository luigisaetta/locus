# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""mkdocs hook: keep full source listings out of the search index.

Two kinds of collapsed block carry whole source files: the "Full source"
block at the end of every notebook page and the "Source code in …" block
mkdocstrings adds under each documented object. Indexed, they were four fifths
of a 5 MB search index that every first visit downloads (1 MB compressed on
a phone). Marking them ``data-search-exclude`` tells Material's search plugin
to skip them; the notebook's quoted key lines, the API signatures and the
docstrings stay searchable, so a function name still finds its page.
"""

from __future__ import annotations

import re
from typing import Any


_NOTEBOOK_SOURCE = re.compile(
    r'<details class="note">(?=\s*<summary>Full source\b)',
)
_API_SOURCE = re.compile(r'<details class="mkdocstrings-source">')


def exclude_source_listings(html: str) -> str:
    """Return ``html`` with the full-source details blocks excluded from search."""
    html = _NOTEBOOK_SOURCE.sub('<details class="note" data-search-exclude>', html)
    return _API_SOURCE.sub('<details class="mkdocstrings-source" data-search-exclude>', html)


def on_page_content(html: str, page: Any, config: Any, files: Any) -> str:
    return exclude_source_listings(html)
