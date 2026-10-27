---
title: Oracle Database 26ai
description: "Every Oracle Database 26ai primitive in Locus — vector search, in-database chunking and embeddings, table ingestion, durable and versioned threads, long-term memory and Oracle agent memory — with the notebook that runs each one."
---

# Oracle Database 26ai

Locus treats Oracle Database 26ai as the place where an agent's state lives:
vectors for retrieval, threads for continuity, memories for what it has
learned, in the same database as the data it acts on. Each primitive is a
first-class Locus class on the `oracledb` driver, with no adapter layer in
between, and it works with the same `Agent` as everything else.

```bash
pip install "locus-sdk[oci,oracledb]"
```

## What ships

| Need | Class | Notebook |
|---|---|---|
| Vector search for RAG on native `VECTOR` columns | `OracleVectorStore` | [38 — Oracle 26ai RAG](../notebooks/notebook_38_oracle_26ai_rag.md) |
| Ingest rows from your own tables as documents | `OracleADBLoader` | [39 — ADB loader](../notebooks/notebook_39_oracle_adb_loader.md) |
| Chunk text inside the database | `OracleInDBChunker` | [40 — In-database chunker](../notebooks/notebook_40_oracle_indb_chunker.md) |
| Embed inside the database with an ONNX model | `OracleInDBEmbeddings` | [41 — In-database embeddings](../notebooks/notebook_41_oracle_indb_embeddings.md) |
| Durable conversation threads | `oracle_checkpointer()` | [42 — Oracle 26ai checkpointer](../notebooks/notebook_42_oracle_26ai_checkpointer.md) |
| Every version of a thread, resume from any point | `OracleCheckpointSaver` | [43 — Versioned saver](../notebooks/notebook_43_oracle_versioned_saver.md) |
| Long-term memory store (`BaseStore`) | `OracleStore` | [37 — Oracle store](../notebooks/notebook_37_oracle_store.md) |
| Oracle's agent-memory service, in-database extraction and recall | `OracleAgentMemoryManager` | [44 — Oracle agent memory](../notebooks/notebook_44_oracle_agent_memory.md) |

Every class has a synchronous twin (`OracleSyncVectorStore`,
`OracleSyncInDBEmbeddings`, `OracleSyncInDBChunker`, `OracleSyncADBLoader`,
`OracleSyncStore`, `OracleSyncCheckpointSaver`) for code that is not async.

## Connecting

All of them take the same connection arguments: `dsn`, `user`, `password`,
and for Autonomous Database `wallet_location` and `wallet_password`; or
`host`, `port` and `service_name` for a plain listener. The notebooks and the
integration tests read them from `ORACLE_DSN`, `ORACLE_USER`,
`ORACLE_PASSWORD`, `ORACLE_WALLET` and `ORACLE_WALLET_PASSWORD`.

## Retrieval

The agent's own documents on a `VECTOR` column, searched with
`VECTOR_DISTANCE`, exposed to the model as a tool.

```python
import os

from locus.agent import Agent
from locus.rag import OCIEmbeddings, OracleVectorStore, RAGRetriever

db = dict(
    dsn=os.environ["ORACLE_DSN"],
    user=os.environ["ORACLE_USER"],
    password=os.environ["ORACLE_PASSWORD"],
    wallet_location=os.environ["ORACLE_WALLET"],
    wallet_password=os.environ.get("ORACLE_WALLET_PASSWORD", ""),
)
retriever = RAGRetriever(
    embedder=OCIEmbeddings(model_id="cohere.embed-v4.0"),
    store=OracleVectorStore(table_name="runbooks", dimension=1536, **db),
)
agent = Agent(model="oci:openai.gpt-5.5", tools=[retriever.as_tool()])
```

When the text must not leave the database, chunk and embed inside it:
`OracleInDBChunker` splits with `DBMS_VECTOR_CHAIN`, `OracleInDBEmbeddings`
runs an ONNX model loaded into the database, and `OracleVectorStore` keeps
the result, so no document content goes to a hosted embedding API. The
model is a one-time load. On Autonomous Database, Oracle's prebuilt
all-MiniLM-L12-v2 (384 dimensions) loads straight from Object Storage:

```sql
BEGIN
  DBMS_VECTOR.LOAD_ONNX_MODEL_CLOUD(
    model_name => 'ALL_MINILM_L12_V2',
    credential => NULL,   -- pre-authenticated URL
    uri        => '<URL of all_MiniLM_L12_v2.onnx from the Oracle Machine Learning blog>');
END;
/
SELECT vector_dimension_count(vector_embedding(ALL_MINILM_L12_V2 USING 'hello' AS data)) FROM dual;  -- 384
```

Then `OracleInDBEmbeddings(model_name="ALL_MINILM_L12_V2", dimension=384)`
and `OracleVectorStore(dimension=384)`; notebook 41 runs the whole path.

## Threads and memory

`oracle_checkpointer()` gives every thread a durable home;
`OracleCheckpointSaver` keeps the full history of each thread; `OracleStore`
and `OracleAgentMemoryManager` hold what the agent learns across threads.
[Memory: short-term and long-term](memory.md) explains the three layers
and shows each one on Oracle Database 26ai.

## Where to go next

- [OCI Generative AI](providers/oci.md) for the model side of the same stack.
- [Dedicated AI Clusters](../how-to/oci-dac.md) for your own model endpoints.
- [RAG](rag.md), [Checkpointers](checkpointers.md) and [Long-term memory manager](memory-manager.md) for the general surfaces these classes plug into.
