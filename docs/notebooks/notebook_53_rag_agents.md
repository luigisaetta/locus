# RAG Agents

Once you have runbooks in a vector store (the RAG basics and RAG providers notebooks), the next
step is to let an agent reach into it — so an incident answer cites your
runbooks instead of model memory. `RAGRetriever.as_tool()` turns the
retriever into an ordinary Locus tool that the agent picks up alongside
any other `@tool` you define. ATLAS is the platform team's on-call SRE
copilot; it reads the Index — the internal runbook knowledge base.

- `retriever.as_tool(name, description)` — convert a retriever into a
  callable tool for the agent.
- Single-tool Q&A copilot against an internal runbook KB.
- Mixed tool set — runbook search alongside a calculator and a date tool
  for rollout math.
- Streaming events from the agent while it searches and answers.
- An **answer-grounding gate**: before ATLAS ships remediation advice,
  the GSAR scorer (`locus.reasoning.gsar`) partitions the answer's claims
  into grounded vs. ungrounded, and `decide()` returns proceed /
  regenerate / replan. A fix anchored in a retrieved runbook chunk
  proceeds; a hunch with no retrieved text replans rather than guess.
- Best-practice notes on chunk size, prompt design, and metadata
  filters for ops corpora.

Backend: the pure-Python `InMemoryVectorStore` keeps the demo dependency-free
and runnable anywhere. Swap `_make_store` for any other Locus vector store
(`PgVectorStore`, `OpenSearchVectorStore`, `QdrantVectorStore`,
`ChromaVectorStore`) for a durable backend.

## Run it

Embeddings need an OpenAI api key:

```bash
export OPENAI_API_KEY=sk-...
python examples/notebook_53_rag_agents.py
```

Offline (skips the retrieval sections cleanly when the key is missing;
the answer-grounding gate is pure-Python and always runs):

```bash
python examples/notebook_53_rag_agents.py
```

## Prerequisites

```bash
export OPENAI_API_KEY=sk-...
```

## Source

````python
--8<-- "examples/notebook_53_rag_agents.py"
````
