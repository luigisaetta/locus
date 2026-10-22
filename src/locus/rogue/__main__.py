# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""``python -m locus.rogue`` — run the rogue-agent challenge."""

import asyncio

from locus.rogue.challenge import main


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
