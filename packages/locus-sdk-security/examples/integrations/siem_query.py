# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Back-compat shim — SIEM search graduated into the SDK.

This adapter is now first-class in :mod:`locus_security.siem`. Importing
from here still works; prefer::

    from locus_security import query_siem, siem_query_tool
"""

from __future__ import annotations

from locus_security.siem import query_siem, siem_query_tool


__all__ = ["query_siem", "siem_query_tool"]
