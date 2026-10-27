# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Integration tests for vector stores: pgvector."""

from __future__ import annotations

import os

import pytest


pytestmark = pytest.mark.integration


def get_embedder():
    """Get embedder based on available credentials.

    OpenAI when ``OPENAI_API_KEY`` is set; otherwise OCI Generative AI when
    ``OCI_PROFILE`` is set (``OCI_EMBED_MODEL``, default ``cohere.embed-v4.0``;
    ``OCI_COMPARTMENT`` / ``OCI_COMPARTMENT_ID`` and ``OCI_ENDPOINT`` honoured),
    mirroring how ``conftest.get_model`` picks the chat model.
    """
    if os.environ.get("OPENAI_API_KEY"):
        from locus.rag.embeddings import OpenAIEmbeddings

        return OpenAIEmbeddings(model="text-embedding-3-small")
    if os.environ.get("OCI_PROFILE"):
        from locus.rag.embeddings.oci import OCIEmbeddings

        return OCIEmbeddings(
            model_id=os.environ.get("OCI_EMBED_MODEL", "cohere.embed-v4.0"),
            profile_name=os.environ["OCI_PROFILE"],
            compartment_id=os.environ.get("OCI_COMPARTMENT")
            or os.environ.get("OCI_COMPARTMENT_ID")
            or "",
            service_endpoint=os.environ.get("OCI_ENDPOINT"),
        )
    return None


# =============================================================================
# pgvector Tests (requires PostgreSQL with pgvector extension)
# =============================================================================


def has_postgres_available() -> bool:
    """Check if PostgreSQL is available."""
    return bool(os.environ.get("POSTGRES_DSN") or os.environ.get("PGVECTOR_DSN"))


@pytest.mark.skipif(not has_postgres_available(), reason="PostgreSQL not configured")
class TestPgVectorStore:
    """Tests for pgvector store."""

    @pytest.mark.asyncio
    async def test_pgvector_basic_operations(self):
        """Test basic operations with pgvector."""
        from locus.rag.stores import PgVectorStore
        from locus.rag.stores.base import Document

        embedder = get_embedder()
        if not embedder:
            pytest.skip("No embedder available")

        dsn = os.environ.get("POSTGRES_DSN") or os.environ.get("PGVECTOR_DSN")

        store = PgVectorStore(
            dsn=dsn,
            table_name="test_pgvector",
            dimension=embedder.config.dimension,
        )

        try:
            result = await embedder.embed("Test document")
            doc = Document(
                id="pg_test_1",
                content="Test document",
                embedding=result.embedding,
            )
            doc_id = await store.add(doc)
            assert doc_id == "pg_test_1"

            retrieved = await store.get("pg_test_1")
            assert retrieved is not None
            assert retrieved.content == "Test document"

        finally:
            await store.clear()
            await store.close()
            await embedder.close()
