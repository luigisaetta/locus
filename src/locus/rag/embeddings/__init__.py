"""Embedding providers for RAG.

Available providers:
- OpenAIEmbeddings: OpenAI text-embedding models
- CohereEmbeddings: Cohere's direct embedding API
- OCIEmbeddings: OCI Generative AI embeddings (Cohere embed models on OCI)
- OracleInDBEmbeddings: Oracle 23ai/26ai in-database ONNX embeddings
"""

from typing import Any

from locus.rag.embeddings.base import (
    BaseEmbedding,
    EmbeddingConfig,
    EmbeddingProvider,
    EmbeddingResult,
)


__all__ = [
    # Base
    "BaseEmbedding",
    "EmbeddingConfig",
    "EmbeddingProvider",
    "EmbeddingResult",
    # Providers (lazy imports)
    "OpenAIEmbeddings",
    "CohereEmbeddings",
    "OCIEmbeddings",
    "OracleInDBEmbeddings",
    "OracleSyncInDBEmbeddings",
]


def __getattr__(name: str) -> Any:
    """Lazy import providers to avoid requiring all dependencies."""
    if name == "OpenAIEmbeddings":
        from locus.rag.embeddings.openai import OpenAIEmbeddings

        return OpenAIEmbeddings

    if name == "CohereEmbeddings":
        from locus.rag.embeddings.cohere import CohereEmbeddings

        return CohereEmbeddings

    if name == "OCIEmbeddings":
        from locus.rag.embeddings.oci import OCIEmbeddings

        return OCIEmbeddings
    if name == "OracleInDBEmbeddings":
        from locus.rag.embeddings.oracle_indb import OracleInDBEmbeddings

        return OracleInDBEmbeddings
    if name == "OracleSyncInDBEmbeddings":
        from locus.rag.embeddings.oracle_sync import OracleSyncInDBEmbeddings

        return OracleSyncInDBEmbeddings
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
