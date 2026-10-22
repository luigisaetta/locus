#!/usr/bin/env python
# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""🔓 Can you make the agent go rogue?  (see ``locus.rogue`` for the source)

The challenge now ships inside the package, so it runs from an install with
no clone:

    pip install locus-sdk
    python -m locus.rogue

This file stays as the examples-directory entry point and is equivalent::

    python examples/can_you_make_it_go_rogue.py
"""

import asyncio

from locus.rogue.challenge import main


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
