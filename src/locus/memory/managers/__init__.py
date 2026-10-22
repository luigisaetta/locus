"""Specialised memory managers.

Where :mod:`locus.memory.manager` ships the framework-level memory
contracts (:class:`BaseMemoryManager`, :class:`LLMMemoryManager`) that
work against any :class:`~locus.memory.store.BaseStore`, this
subpackage holds higher-fidelity memory managers built on top of
purpose-built external libraries.

:class:`Mem0MemoryManager` delegates to the open-source
`mem0 <https://pypi.org/project/mem0ai/>`_ memory layer, bringing in
fact extraction, scoped retrieval by user/agent/thread, and a
self-hostable vector store. The portable ``LLMMemoryManager`` stays
first-class for plain backends (InMemory / Redis / Postgres /
OpenSearch) and for test environments where pulling in ``mem0ai`` would
be overkill.

For Oracle Database 26ai deployments, :class:`OracleAgentMemoryManager`
delegates to Oracle's official ``oracleagentmemory`` client
(https://pypi.org/project/oracleagentmemory/): context-card summaries,
scoped retrieval by user/agent/thread, and LongMemEval-benchmarked
extraction quality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from locus.memory.managers.mem0 import Mem0MemoryManager
    from locus.memory.managers.oracle_agent_memory import OracleAgentMemoryManager

__all__ = ["Mem0MemoryManager", "OracleAgentMemoryManager"]


def __getattr__(name: str) -> Any:  # pragma: no cover - lazy export wiring
    # Lazy-load the Mem0-backed manager so importing
    # ``locus.memory.managers`` (or even ``locus.memory``) does not
    # require the optional ``mem0ai`` dependency to be installed. Only
    # consumers that actually construct the class pay the import cost.
    if name == "Mem0MemoryManager":
        from locus.memory.managers.mem0 import Mem0MemoryManager  # noqa: PLC0415

        return Mem0MemoryManager
    if name == "OracleAgentMemoryManager":
        from locus.memory.managers.oracle_agent_memory import (  # noqa: PLC0415
            OracleAgentMemoryManager,
        )

        return OracleAgentMemoryManager
    raise AttributeError(f"module 'locus.memory.managers' has no attribute {name!r}")
