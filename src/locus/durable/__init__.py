# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Durable execution for agent runs.

:mod:`locus.durable.temporal` runs an agent on Temporal: a run is a workflow
that survives worker restarts, and a held approval is a wait of any length for
a signal. Needs ``pip install "locus-sdk[temporal]"``.

:mod:`locus.durable.dbos` does the same on DBOS, in your own process with the
state in Postgres (or SQLite), for agents and for
:class:`~locus.multiagent.graph.StateGraph` runs, whose interrupts become waits
of any length. Needs ``pip install "locus-sdk[dbos]"``.

Both run the agent in segments (:mod:`locus.durable.segments`), each at most
once. Nothing is imported here, so this package costs nothing unless you use it.
"""
