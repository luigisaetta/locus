# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Back-compat shim — GPU-probe dispatch graduated into the SDK.

The co-located timing-probe lifecycle is now first-class in
:mod:`locus_security.fingerprint`. Core ships the *offline reference*
(``dispatch_timing_probe_reference``); a live probe on a GPU cloud is an
integration you write. This shim re-exports the offline reference under the example's local name::

    from locus_security import dispatch_timing_probe_reference, FEATURE_KEYS
"""

from __future__ import annotations

from locus_security.fingerprint import FEATURE_KEYS
from locus_security.fingerprint import dispatch_timing_probe_reference as dispatch_timing_probe


__all__ = ["FEATURE_KEYS", "dispatch_timing_probe"]
