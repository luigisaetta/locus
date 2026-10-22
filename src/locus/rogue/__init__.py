# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""The rogue-agent challenge — try to make a governed agent fire a real action.

Ships inside the package so it runs straight from an install, with no clone
and no API key::

    pip install locus-sdk
    python -m locus.rogue

The agent holds live-looking production tools and the offline model arrives
already compromised. What holds is :func:`locus.control.admit`, not the
model's judgement.
"""

from locus.rogue.challenge import build_agent, main, pick_mode


__all__ = ["build_agent", "main", "pick_mode"]
