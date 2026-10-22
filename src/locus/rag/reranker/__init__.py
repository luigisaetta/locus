"""Rerankers — reorder retriever candidates by relevance to a query.

The retrieve-then-rerank pattern materially improves answer grounding in
RAG: pull a wide candidate set (top-K) from the vector store cheaply,
then have a *cross-encoder* reranker score each candidate against the
query before the top-N hits the LLM. The reranker sees both query and
candidate together, so it catches relevance signals an embedding-only
score misses.

This subpackage adds:

  * :class:`Reranker` — abstract base every reranker implements.
  * :class:`CrossEncoderReranker` — local ``sentence-transformers``
    cross-encoder; runs fully offline, no API key.
  * :class:`CohereReranker` — Cohere's hosted rerank API (direct).
  * :class:`OCICohereReranker` — Cohere rerank models served by OCI
    Generative AI (rerank-v3.5, rerank-v4.0).

Wire one into a retriever with ``RAGRetriever(reranker=...)`` to swap the
default semantic-only ordering for a reranked one.
"""

from typing import Any

from locus.rag.reranker.base import Reranker


__all__ = ["CohereReranker", "CrossEncoderReranker", "OCICohereReranker", "Reranker"]


def __getattr__(name: str) -> Any:
    """Lazy import rerankers to avoid requiring optional dependencies."""
    if name == "CrossEncoderReranker":
        from locus.rag.reranker.cross_encoder import CrossEncoderReranker

        return CrossEncoderReranker

    if name == "CohereReranker":
        from locus.rag.reranker.cohere import CohereReranker

        return CohereReranker

    if name == "OCICohereReranker":
        from locus.rag.reranker.cohere_oci import OCICohereReranker

        return OCICohereReranker
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
