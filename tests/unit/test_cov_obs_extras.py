# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Extra coverage for qdrant.py and rag/__init__.py lazy imports."""

from __future__ import annotations

import pytest


pytest.importorskip("qdrant_client")

from locus.rag.stores.base import Document  # noqa: E402
from locus.rag.stores.qdrant import QdrantVectorStore  # noqa: E402


# ---------------------------------------------------------------------------
# QdrantVectorStore — uncovered branches
# ---------------------------------------------------------------------------


def _store(**kwargs) -> QdrantVectorStore:
    defaults = {"location": ":memory:", "dimension": 3, "collection_name": "cov-test"}
    return QdrantVectorStore(**{**defaults, **kwargs})


def _doc(doc_id: str, vec, **meta) -> Document:
    return Document(id=doc_id, content=f"content-{doc_id}", embedding=list(vec), metadata=meta)


class TestQdrantConfig:
    def test_config_property_returns_vector_store_config(self):
        """config property (line 94) returns the right VectorStoreConfig."""
        from locus.rag.stores.base import VectorStoreConfig  # noqa: PLC0415

        store = _store(dimension=128, distance_metric="cosine")
        cfg = store.config  # line 94
        assert isinstance(cfg, VectorStoreConfig)
        assert cfg.dimension == 128
        assert cfg.distance_metric == "cosine"
        assert cfg.index_type == "hnsw"


class TestQdrantGetClient:
    def test_client_override_returned_directly(self):
        """_get_client returns _client_override without touching imports (line 102)."""
        from unittest import mock  # noqa: PLC0415

        fake_client = mock.MagicMock()
        store = QdrantVectorStore(dimension=3, _client=fake_client)
        assert store._get_client() is fake_client  # line 102

    def test_url_based_client_created(self):
        """Passing url= constructs an AsyncQdrantClient via URL path (line 112).
        AsyncQdrantClient makes a live connection attempt in __init__, so we mock
        the class to avoid network calls."""
        from unittest.mock import MagicMock, patch  # noqa: PLC0415

        fake_client = MagicMock()
        with patch("qdrant_client.AsyncQdrantClient", return_value=fake_client) as mock_cls:
            store = QdrantVectorStore(url="http://localhost:9999", dimension=3, api_key="k")
            client = store._get_client()  # line 112

        assert client is fake_client
        assert store._client is fake_client
        mock_cls.assert_called_once_with(url="http://localhost:9999", api_key="k")
        # Second call returns cached client, not a new one.
        assert store._get_client() is fake_client


class TestQdrantAddBatchEmpty:
    async def test_add_batch_empty_list_returns_empty(self):
        """add_batch([]) returns [] early (line 140)."""
        store = _store()
        result = await store.add_batch([])  # line 140
        assert result == []


class TestQdrantClear:
    async def test_clear_returns_zero_when_no_collection(self):
        """clear() on a fresh store with no collection returns 0 (line 260)."""
        store = _store()
        # _ensured is False; collection doesn't exist yet.
        result = await store.clear()  # line 260
        assert result == 0

    async def test_clear_with_existing_collection(self):
        """clear() on a store with documents returns correct count."""
        store = _store()
        await store.add(_doc("a", [1.0, 0.0, 0.0]))
        await store.add(_doc("b", [0.0, 1.0, 0.0]))
        removed = await store.clear()
        assert removed == 2
        assert await store.count() == 0


class TestQdrantClose:
    async def test_close_clears_client_reference(self):
        """close() sets _client to None (lines 263-265)."""
        store = _store()
        # Initialise client by doing any operation.
        await store.add(_doc("x", [1.0, 0.0, 0.0]))
        assert store._client is not None

        await store.close()  # lines 263-265
        assert store._client is None

    async def test_close_when_client_none_is_noop(self):
        """Calling close() before any use (client is None) must not raise."""
        store = _store()
        await store.close()  # _client is None — noop


# ---------------------------------------------------------------------------
# rag/__init__.py — lazy __getattr__ imports (lines 139, 141, 144, 146,
#                   155, 157, 165, 167, 170, 172, 176, 178, 181, 183)
# and the AttributeError path (line 186)
# ---------------------------------------------------------------------------


class TestRagLazyImports:
    def test_in_memory_vector_store_lazy(self):
        """Accessing locus.rag.InMemoryVectorStore triggers the lazy import
        (lines 149-152)."""
        from locus import rag  # noqa: PLC0415

        cls = rag.InMemoryVectorStore  # lines 149-152
        from locus.rag.stores.memory import InMemoryVectorStore  # noqa: PLC0415

        assert cls is InMemoryVectorStore

    def test_opensearch_vector_store_lazy(self):
        """Accessing locus.rag.OpenSearchVectorStore triggers the lazy import
        (lines 159-162). The opensearch module is omitted from coverage, but the
        __getattr__ branch itself (lines 159-162 in __init__.py) IS measured."""
        from locus import rag  # noqa: PLC0415

        cls = rag.OpenSearchVectorStore  # lines 159-162
        from locus.rag.stores.opensearch import OpenSearchVectorStore  # noqa: PLC0415

        assert cls is OpenSearchVectorStore

    def test_openai_embeddings_lazy(self):
        """Accessing locus.rag.OpenAIEmbeddings triggers the lazy import
        (lines 139, 141)."""
        from locus import rag  # noqa: PLC0415

        cls = rag.OpenAIEmbeddings  # lines 139, 141
        from locus.rag.embeddings.openai import OpenAIEmbeddings  # noqa: PLC0415

        assert cls is OpenAIEmbeddings

    def test_cohere_embeddings_lazy(self):
        """Accessing locus.rag.CohereEmbeddings triggers the lazy import
        (lines 144, 146)."""
        from locus import rag  # noqa: PLC0415

        cls = rag.CohereEmbeddings  # lines 144, 146
        from locus.rag.embeddings.cohere import CohereEmbeddings  # noqa: PLC0415

        assert cls is CohereEmbeddings

    def test_pgvector_store_lazy(self):
        """Accessing locus.rag.PgVectorStore triggers the lazy import
        (lines 155, 157)."""
        from locus import rag  # noqa: PLC0415

        cls = rag.PgVectorStore  # lines 155, 157
        from locus.rag.stores.pgvector import PgVectorStore  # noqa: PLC0415

        assert cls is PgVectorStore

    def test_qdrant_store_lazy(self):
        """Accessing locus.rag.QdrantVectorStore triggers the lazy import
        (lines 165, 167)."""
        from locus import rag  # noqa: PLC0415

        cls = rag.QdrantVectorStore  # lines 165, 167
        from locus.rag.stores.qdrant import QdrantVectorStore as QdrantStore  # noqa: PLC0415

        assert cls is QdrantStore

    def test_chroma_store_lazy(self):
        """Accessing locus.rag.ChromaVectorStore triggers the lazy import
        (lines 170, 172).  chromadb installs fine; only direct 'import chromadb'
        fails in this env due to a protobuf conflict — the locus module wraps it."""
        from locus import rag  # noqa: PLC0415

        try:
            cls = rag.ChromaVectorStore  # lines 170, 172
        except (ImportError, TypeError):
            pytest.skip("ChromaVectorStore not importable in this environment")

        from locus.rag.stores.chroma import ChromaVectorStore  # noqa: PLC0415

        assert cls is ChromaVectorStore

    def test_cross_encoder_reranker_lazy(self):
        """Accessing locus.rag.CrossEncoderReranker triggers the lazy import
        (lines 176, 178)."""
        from locus import rag  # noqa: PLC0415

        cls = rag.CrossEncoderReranker  # lines 176, 178
        from locus.rag.reranker.cross_encoder import CrossEncoderReranker  # noqa: PLC0415

        assert cls is CrossEncoderReranker

    def test_cohere_reranker_lazy(self):
        """Accessing locus.rag.CohereReranker triggers the lazy import
        (lines 181, 183)."""
        from locus import rag  # noqa: PLC0415

        cls = rag.CohereReranker  # lines 181, 183
        from locus.rag.reranker.cohere import CohereReranker  # noqa: PLC0415

        assert cls is CohereReranker

    def test_unknown_attribute_raises(self):
        """Accessing an unknown attribute raises AttributeError (line 186)."""
        from locus import rag  # noqa: PLC0415

        with pytest.raises(AttributeError, match="has no attribute"):
            _ = rag.NonExistentAttribute  # line 186
