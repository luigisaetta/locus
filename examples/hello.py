#!/usr/bin/env python3
# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""The smallest thing that is still an agent — a model, a tool, one call.

    export OPENAI_API_KEY=...        # or point LOCUS_MODEL at any provider
    python examples/hello.py

No credentials to hand? Two things run with none at all::

    python -m locus.rogue                       # the 30-second control demo
    python examples/notebook_06_basic_agent.py  # the notebooks use a mock model

The numbered notebooks each teach one idea against a worked scenario, which
makes them longer than the API they demonstrate. This file is the API and
nothing else, so the first code a reader sees is the shape of Locus rather
than the shape of an example.
"""

import os

from locus import Agent, tool


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


agent = Agent(
    model=os.environ.get("LOCUS_MODEL", "openai:gpt-4o-mini"),
    tools=[add],
    system_prompt="Be brief.",
)

print(agent.run_sync("What is 2 plus 2? Use your tool.").message)
