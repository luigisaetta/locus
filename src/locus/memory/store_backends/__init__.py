"""Store backends for Locus long-term memory.

A :class:`~locus.memory.store.BaseStore` is the cross-thread persistent
key/value store used for long-term memory (see ``store.py``). Where the
``backends/`` package holds **checkpointer** drivers (per-thread agent
state), this package holds **store** drivers — namespace-keyed value
storage that survives across threads, optionally with vector search.

Two long-term memory stores ship here: :class:`HolographicStore` (zero-infra
SQLite + FTS5 + HRR — the free/personal default) and :class:`PgMemory`
(Postgres + pgvector with per-tenant Row-Level Security — the enterprise
backend). Both implement ``BaseStore``; implement a custom store by subclassing
it. The built-in :class:`~locus.memory.store.InMemoryStore` covers small tests.
"""

from typing import Any


__all__: list[str] = []

from locus.memory.store_backends.holographic import HolographicStore  # noqa: E402
from locus.memory.store_backends.postgresql import PgMemory  # noqa: E402


__all__ = ["HolographicStore", "OracleStore", "OracleStoreConfig", "OracleSyncStore", "PgMemory"]


def __getattr__(name: str) -> Any:
    """Lazy import the Oracle Database 26ai stores (optional ``oracledb`` dependency).

    :class:`OracleStore` is the ``BaseStore`` over Oracle's native VECTOR +
    JSON columns — cross-thread long-term memory with semantic search, no
    langchain/langgraph imports.
    """
    if name in {"OracleStore", "OracleStoreConfig"}:
        from locus.memory.store_backends import oracle

        return getattr(oracle, name)
    if name == "OracleSyncStore":
        from locus.memory.store_backends.oracle_sync import OracleSyncStore

        return OracleSyncStore
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
