"""Vector stores for RAG.

Available stores:
- InMemoryVectorStore: In-memory store (testing / small corpora)
- PgVectorStore: PostgreSQL with pgvector extension
- OpenSearchVectorStore: OpenSearch with k-NN plugin
- QdrantVectorStore: Qdrant (local in-memory or server)
- ChromaVectorStore: Chroma (embedded or server)
- OracleVectorStore: Oracle Database 26ai with the native VECTOR type
"""

from typing import Any

from locus.rag.stores.base import (
    BaseVectorStore,
    Document,
    SearchResult,
    VectorStore,
    VectorStoreConfig,
)


__all__ = [
    # Base
    "BaseVectorStore",
    "Document",
    "SearchResult",
    "VectorStore",
    "VectorStoreConfig",
    # Stores (lazy imports)
    "InMemoryVectorStore",
    "PgVectorStore",
    "OpenSearchVectorStore",
    "QdrantVectorStore",
    "ChromaVectorStore",
    "OracleVectorStore",
    "OracleSyncVectorStore",
]


def __getattr__(name: str) -> Any:
    """Lazy import stores to avoid requiring all dependencies."""
    if name == "InMemoryVectorStore":
        from locus.rag.stores.memory import InMemoryVectorStore

        return InMemoryVectorStore

    if name == "PgVectorStore":
        from locus.rag.stores.pgvector import PgVectorStore

        return PgVectorStore

    if name == "OpenSearchVectorStore":
        from locus.rag.stores.opensearch import OpenSearchVectorStore

        return OpenSearchVectorStore

    if name == "QdrantVectorStore":
        from locus.rag.stores.qdrant import QdrantVectorStore

        return QdrantVectorStore

    if name == "ChromaVectorStore":
        from locus.rag.stores.chroma import ChromaVectorStore

        return ChromaVectorStore

    if name == "OracleVectorStore":
        from locus.rag.stores.oracle import OracleVectorStore

        return OracleVectorStore
    if name == "OracleSyncVectorStore":
        from locus.rag.stores.oracle_sync import OracleSyncVectorStore

        return OracleSyncVectorStore
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
