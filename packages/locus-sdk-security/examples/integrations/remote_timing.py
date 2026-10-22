# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Back-compat shim — remote-API timing fingerprint graduated into the SDK.

The measurement is now first-class in :mod:`locus_security.fingerprint`.
Importing from here still works; prefer::

    from locus_security import (
        measure_endpoint_timing,
        FEATURE_KEYS,
        default_classifier,
    )
"""

from __future__ import annotations

from locus_security.fingerprint import (
    _SAMPLE_FEATURES,
    FEATURE_KEYS,
    default_classifier,
    measure_endpoint_timing,
)


__all__ = ["FEATURE_KEYS", "_SAMPLE_FEATURES", "default_classifier", "measure_endpoint_timing"]
