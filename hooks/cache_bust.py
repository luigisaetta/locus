# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""mkdocs hook: append a content hash to extra_css / extra_javascript URLs.

GitHub Pages serves CSS/JS at stable filenames with a ~10-minute cache, and
behind Cloudflare that can read as "my change didn't deploy". Appending a
short content hash as a query string (``locus.css?h=ab12cd34``) changes the
URL whenever the file content changes, so browsers fetch the new asset
immediately while unchanged assets stay cached. The query string does not
affect which file GitHub Pages serves.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def _hashed(docs_dir: Path, rel: str) -> str:
    # Leave absolute URLs (https://…) and already-queried entries untouched.
    if "://" in rel or "?" in rel:
        return rel
    f = docs_dir / rel
    if not f.is_file():
        return rel
    digest = hashlib.sha256(f.read_bytes()).hexdigest()[:8]
    return f"{rel}?h={digest}"


def on_config(config: Any) -> Any:
    docs_dir = Path(config["docs_dir"])
    config["extra_css"] = [_hashed(docs_dir, c) for c in config.get("extra_css", [])]
    config["extra_javascript"] = [
        _hashed(docs_dir, j) if isinstance(j, str) else j
        for j in config.get("extra_javascript", [])
    ]
    return config
