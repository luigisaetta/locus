# RAG Providers

Production RAG is two pluggable pieces, both behind one Locus
interface.

- **Embeddings** — `OpenAIEmbeddings` (`text-embedding-3-small` /
  `-3-large`) or `CohereEmbeddings` (Cohere's direct API).
- **Vector store** — `InMemoryVectorStore` for demos, or a durable
  backend: `PgVectorStore`, `OpenSearchVectorStore`,
  `QdrantVectorStore`, `ChromaVectorStore`. Swapping is one line; the
  retrieve/add API is identical.

The corpus here is a payments-operations runbook — decline codes,
dispute reason codes, refund SLAs, and ACH returns — the same knowledge
a support agent leans on to answer a merchant. Picking the embedding
model and distance metric is an operations decision: it sets retrieval
precision, and weak retrieval routes the agent to the wrong runbook.

What the four parts cover:

- Part 1 — embedding-model selection (small vs large dimensions).
- Part 2 — distance metric choices (`cosine` / `dot` / `euclidean`).
- Part 3 — Qdrant in-memory store as a drop-in for InMemoryVectorStore.
- Part 4 — batch ingest, `count()`, `clear()`.

## Run it

Embeddings need an OpenAI api key:

```bash
export OPENAI_API_KEY=sk-...
python examples/notebook_52_rag_providers.py
```

Offline (skips the live demo cleanly when the key is missing):

```bash
python examples/notebook_52_rag_providers.py
```

## Prerequisites

```bash
export OPENAI_API_KEY=sk-...
```

## Source

````python
--8<-- "examples/notebook_52_rag_providers.py"
````
