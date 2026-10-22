# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Back-compat shim — threat-intel IOC enrichment graduated into the SDK.

This adapter is now first-class in :mod:`locus_security.intel`. Importing
from here still works; prefer::

    from locus_security import (
        enrich_indicator,
        enrich_indicator_tool,
        enrich_to_finding,
    )
"""

from __future__ import annotations

from locus_security.intel import (
    classify_indicator,
    enrich_indicator,
    enrich_indicator_tool,
    enrich_to_finding,
)


__all__ = [
    "classify_indicator",
    "enrich_indicator",
    "enrich_indicator_tool",
    "enrich_to_finding",
]
