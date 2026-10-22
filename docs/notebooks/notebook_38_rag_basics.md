# RAG Basics

Retrieval-Augmented Generation grounds an agent's answers in your own
documents. This notebook drives the four-step pipeline over a cloud
Well-Architected best-practice catalogue, using the bundled in-memory
vector store.

- **Embed** — `OpenAIEmbeddings` (`text-embedding-3-small`, 1536 dims).
- **Store** — the pure-Python `InMemoryVectorStore` keeps vectors in
  process with no extra dependencies; swap in `QdrantVectorStore` /
  `PgVectorStore` / `OpenSearchVectorStore` / `ChromaVectorStore` for a
  durable backend.
- **Search** — nearest-neighbour by cosine distance.
- **Retrieve** — `RAGRetriever` wraps embed + chunk + store behind one
  call, tagging each chunk with the pillar/practice metadata the cloud-ops
  agent uses to narrow results.

The corpus is AWS Well-Architected best practices (`REL-xx`, `COST-xx`,
`SEC-xx`, `OPS-xx`) mapped to your runbooks — the Index the cloud-ops
agent (ATLAS, notebook 40) reads from.

## Run it

Embeddings need an OpenAI api key:

```bash
export OPENAI_API_KEY=sk-...
python examples/notebook_38_rag_basics.py
```

Offline (skips the live demo cleanly when the key is missing):

```bash
python examples/notebook_38_rag_basics.py
```

## Prerequisites

```bash
export OPENAI_API_KEY=sk-...
```

## Source

````python
--8<-- "examples/notebook_38_rag_basics.py"
````
