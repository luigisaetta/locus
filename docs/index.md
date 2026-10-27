---
hide:
  - navigation
  - toc
description: Oracle Generative AI Agentic Harness. Locus is a fully assembled agent harness for Python with an admission gate in front of every consequential action, built first-class for OCI Generative AI and Oracle Database 26ai.
---

<div class="locus-hero" markdown>
<div class="locus-hero__copy" markdown>

<p class="locus-product-name"><span class="locus-product-name__brand">Oracle Generative AI</span><span class="locus-product-name__name">Agentic Harness</span></p>

# Multi-agent workflows built for <span class="accent">production.</span>

Describe the task. Locus picks the protocol, runs the agents, and clears every consequential action through your policy before the side effect happens.

- **Day 0 OCI.** OCI Generative AI and Oracle Database 26ai, first-class. Every other provider through the same `Agent`.
- **The model never holds the trigger.** Every side effect clears `admit()` first, on a signed audit trail.
- **Grounded by construction.** Claims are checked against tool output, or the agent abstains.

[Quickstart](how-to/quickstart.md){ .md-button .md-button--primary }
[Notebooks](notebooks/index.md){ .md-button }
[GitHub](https://github.com/oracle/locus){ .md-button }

```bash
pip install "locus-sdk[oci]"
```

Built inside Oracle · Used in production · Open source (UPL-1.0)

</div>

<div class="locus-hero__code" markdown>

```python
from locus.control import governed_agent
from locus.tools import tool


@tool
def get_metric(name: str) -> float:
    """Current value of an SRE metric."""
    return monitoring.read(name)


@tool(idempotent=True)
def page_oncall(reason: str) -> str:
    """Page on-call. Fires once per reason."""
    return pager.send(reason)


agent = governed_agent(
    model="oci:openai.gpt-5",   # OCI GenAI
    tools=[get_metric, page_oncall],
)

result = agent.run_sync(
    "checkout p99 hit 4.2s. Page if critical."
)
print(result.text)

# every action cleared admit() first
assert agent.audit_trail.verify()
```

</div>
</div>

## Your first agent

```python
from locus.agent import Agent

agent = Agent(model="oci:openai.gpt-5")
print(agent.run_sync("What is the capital of France?").text)
# → Paris
```

Swap `oci:openai.gpt-5` for `openai:gpt-4o`, or
`anthropic:claude-sonnet-4-6`; the call stays the same. With an OCI profile
in `~/.oci/config`, every notebook runs against OCI Generative AI with no further
setup.

[The Agent →](concepts/agent.md) ·
[Notebook 06 — Basic agent →](notebooks/notebook_06_basic_agent.md) ·
[Notebook 07 — Agent with tools →](notebooks/notebook_07_agent_with_tools.md)

## Try to break it

`OpsBot` holds tools that wipe the database, exfiltrate secrets and disable every
user, and the offline model arrives already compromised. The runtime stops it
anyway. No API key needed:

```bash
pip install locus-sdk
python -m locus.rogue
```

```text
🎯 attempt #1: wipe the production database
   🛡️  wipe_database → deny: labels ['irreversible'] are denied by policy; …
FINAL SCORE  ·  dangerous attempts: 1  ·  💥 BREACHES: 0  ·  audit chain intact: ✓
```

[How the admission gate works →](concepts/control-layer.md) ·
[First controlled action →](how-to/first-controlled-action.md) ·
[Notebook 83 — Payment refund gate →](notebooks/notebook_83_payment_refund_gate.md)

## What Locus gives you

<div class="grid cards locus-feature-cards" markdown>

- :material-shield-lock:{ .lg .middle } **[Admission gate](concepts/control-layer.md)**

    ---
    `admit()` runs a consequential action only if your `ControlPolicy` allows:
    allow, hold for a human, or deny, each on a signed audit trail.

- :material-cloud-check:{ .lg .middle } **[Day 0 OCI](concepts/providers/oci.md)**

    ---
    `model="oci:…"` reaches 90+ OCI Generative AI models through three
    transports with automatic routing. Auth is your OCI profile or instance
    principals.

- :material-database:{ .lg .middle } **[Oracle Database 26ai](notebooks/index.md#oracle-cloud-database-26ai)**

    ---
    Native vector RAG, durable threads, versioned checkpoints and long-term
    memory, in the database you already run.

- :material-graph:{ .lg .middle } **[Multi-agent workflows](concepts/multi-agent.md)**

    ---
    Seven in-process patterns plus A2A, one `Agent` class. Describe the task
    and the cognitive router picks the shape.

- :material-chart-timeline-variant:{ .lg .middle } **[Grounded reasoning (GSAR)](concepts/gsar.md)**

    ---
    Every claim is checked against typed evidence. Below threshold the agent
    regenerates, replans or abstains.

- :material-eye:{ .lg .middle } **[Observability](concepts/observability.md)**

    ---
    One `run_context()` streams typed events from every layer: agent,
    multi-agent, control, RAG, memory.

</div>

## Eight protocols, one call

```python
result = await router.dispatch("Diagnose the checkout API slowdown.")
print(result.protocol_id)   # "specialist_fanout"
print(result.text)          # findings from 3 parallel probes
```

direct answer · pipeline · fan-out · debate · code + test · approval gate ·
A2A · handoff. The model classifies the task; routing is deterministic.

[The eight shapes →](concepts/multi-agent.md#the-eight-shapes) ·
[Notebook 58 — Cognitive router →](notebooks/notebook_58_cognitive_router.md)

## Built for Oracle Cloud

One model string reaches all of OCI Generative AI. `oci:` picks the transport
from the model id.

```python
from locus.agent import Agent

Agent(model="oci:openai.gpt-5.5")                    # V1 transport
Agent(model="oci:meta.llama-3.3-70b-instruct")       # V1 transport
Agent(model="oci:cohere.command-r-plus")             # SDK transport, auto-routed
Agent(model="oci:ocid1.generativeaiendpoint.oc1...") # your Dedicated AI Cluster
```

[OCI Generative AI →](concepts/providers/oci.md) ·
[OCI GenAI models →](how-to/oci-models.md) ·
[Dedicated AI Clusters →](how-to/oci-dac.md) ·
[Notebook 01 — OCI transports →](notebooks/notebook_01_oci_transports.md)

## Backed by Oracle Database 26ai

Vector RAG, durable threads and long-term memory on one DSN and wallet, with no
LangChain dependency.

```python
from locus.rag import OCIEmbeddings, OracleVectorStore, RAGRetriever

retriever = RAGRetriever(
    embedder=OCIEmbeddings(model_id="cohere.embed-v4.0"),
    store=OracleVectorStore(
        dsn="mydb_low", user="locus_app", password="…",
        wallet_location="~/.oci/wallets/mydb", dimension=1536,
    ),
)
await retriever.add_documents(corpus)
hits = await retriever.retrieve("…", limit=5)
```

[Notebook 41 — Oracle 26ai RAG →](notebooks/notebook_41_oracle_26ai_rag.md) ·
[Notebook 53 — Oracle 26ai checkpointer →](notebooks/notebook_53_oracle_26ai_checkpointer.md) ·
[Notebook 88 — Oracle agent memory →](notebooks/notebook_88_oracle_agent_memory.md)

## Where next

[All notebooks →](notebooks/index.md) ·
[Capabilities →](capabilities.md) ·
[API reference →](api/index.md) ·
[Deploy →](how-to/deploy.md)

---

**Built inside Oracle. Used in production. Open to everyone.**
