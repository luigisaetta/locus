# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Back-compat re-export — the adapter toolkit now lives in :mod:`locus_security.adapter`.

The shared helper conventions were promoted to the public contract module
``locus_security.adapter`` (the langchain-core-style boundary). This module
re-exports them so the bundled adapters' ``from locus_security._adapters import …``
imports keep working; new code should import from ``locus_security`` or
``locus_security.adapter``.
"""

from __future__ import annotations

from locus_security.adapter import (
    as_json,
    env,
    indicator_type,
    inference_claim,
    tool_match,
)


__all__ = [
    "as_json",
    "env",
    "indicator_type",
    "inference_claim",
    "tool_match",
]
