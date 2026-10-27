---
hide:
  - navigation
  - toc
description: "Oracle Generative AI Agentic Harness. Locus is a Python agent harness with eight multi-agent shapes, native OCI Generative AI (including Dedicated AI Clusters) and Oracle Database 26ai, and the runtime around the model: tools, memory, RAG, observability, guardrails, admission gate."
---

<div class="locus-hero" markdown>
<div class="locus-hero__copy" markdown>

<p class="locus-product-name"><span class="locus-product-name__brand">Oracle Generative AI</span><span class="locus-product-name__name">Agentic Harness</span></p>

# Multi-agent workflows built for <span class="accent">production.</span>

One `Agent` class, eight ways to combine agents, Oracle Cloud underneath, and the runtime around the model: tools, memory, RAG, observability, guardrails, an admission gate.

- **Eight multi-agent shapes.** Pipelines, fan-out, orchestrator, swarm, handoff, graphs, debate, A2A. A cognitive router picks one from the task.
- **Oracle Cloud, native.** OCI Generative AI on day 0, 36 models verified with tool calls, Dedicated AI Clusters, and Oracle Database 26ai for vectors, threads and memory.
- **Production from the first line.** Durable threads, typed events, grounded answers, and `admit()` in front of every consequential action.

[Quickstart](how-to/quickstart.md){ .md-button .md-button--primary }
[Multi-agent shapes](concepts/multi-agent.md){ .md-button }
[GitHub](https://github.com/oracle/locus){ .md-button }

```bash
pip install "locus-sdk[oci,oracledb]"
```

Built inside Oracle · Used in production · Open source (UPL-1.0)

</div>

<div class="locus-hero__code" markdown>

```python
from locus.agent import Agent
from locus.agent.composition import (
    SequentialPipeline,
)

model = "oci:openai.gpt-5.5"  # OCI, day 0

diagnose = Agent(
    model=model,
    tools=[query_metrics, search_logs],
    system_prompt="Find what changed.",
)
mitigate = Agent(
    model=model,
    tools=[scale_up, rollback],  # admit()
    system_prompt="Fix it, smallest step.",
)
brief = Agent(
    model=model,
    system_prompt="Write the update.",
)

war_room = SequentialPipeline(
    agents=[diagnose, mitigate, brief],
)
result = await war_room.run(
    "checkout p99 hit 4.2s: fix and brief"
)
print(result.final_output)
```

</div>
</div>

## Your first agent

```python
from locus.agent import Agent

agent = Agent(model="oci:openai.gpt-5.5")
print(agent.run_sync("What is the capital of France?").text)
# → Paris
```

Swap `oci:openai.gpt-5.5` for `openai:gpt-4o` or `anthropic:claude-sonnet-4-6`;
the call stays the same. With an OCI profile in `~/.oci/config`, every notebook
runs against OCI Generative AI with no further setup.

[The Agent →](concepts/agent.md) ·
[Notebook 06 — Basic agent →](notebooks/notebook_06_basic_agent.md) ·
[Notebook 07 — Agent with tools →](notebooks/notebook_07_agent_with_tools.md)

## Eight shapes, one `Agent`

Every shape runs the same `Agent`, emits the same events, and checkpoints to
the same backends. Pick the shape; the agents don't change.

<div class="grid cards locus-feature-cards" markdown>

- :material-arrow-right-bold-box:{ .lg .middle } **[Pipelines](concepts/multi-agent/composition.md)**

    ---
    `SequentialPipeline`, `ParallelPipeline`, `LoopAgent`: chain, fan out,
    or revise until a reviewer clears. Three lines each.

- :material-sitemap:{ .lg .middle } **[Orchestrator and specialists](concepts/multi-agent/orchestrator.md)**

    ---
    One coordinator delegates to typed specialists with their own tools,
    and merges what comes back.

- :material-account-group:{ .lg .middle } **[Swarm](concepts/multi-agent/swarm.md)**

    ---
    Peers that hand work to each other on their own judgement, with a
    shared scratchpad and a hard stop.

- :material-swap-horizontal:{ .lg .middle } **[Handoff](concepts/multi-agent/handoff.md)**

    ---
    Tiered escalation with typed context: L1 to L2 to L3, nothing lost
    in between.

- :material-graph:{ .lg .middle } **[StateGraph and functional API](concepts/multi-agent/graph.md)**

    ---
    Nodes, edges, reducers, `Send` fan-out, interrupts for a human, and
    checkpointed state, LangGraph-style.

- :material-forum:{ .lg .middle } **[Debate and critic loops](notebooks/notebook_32_debate_with_judge.md)**

    ---
    Two debaters and a judge, or a skeptical reviewer that kills unproven
    claims before they ship.

- :material-routes:{ .lg .middle } **[Cognitive router](concepts/multi-agent.md#the-eight-shapes)**

    ---
    Describe the task; the router extracts a typed `GoalFrame`, picks one
    of eight protocols and compiles it onto real agents.

- :material-lan-connect:{ .lg .middle } **[A2A protocol](concepts/multi-agent/a2a.md)**

    ---
    Cross-process agents as spec-compliant peers: expose yours, call
    theirs, same tool contract.

- :material-telescope:{ .lg .middle } **[DeepAgent and research workflows](concepts/deepagent.md)**

    ---
    Plan, explore, validate, report, with per-turn grounding and a
    post-hoc grounding evaluation.

</div>

```python
result = await router.dispatch("Diagnose the checkout API slowdown.")
print(result.protocol_id)   # "specialist_fanout"
print(result.text)          # findings from 3 parallel probes
```

[Multi-agent overview →](concepts/multi-agent.md) ·
[Notebook 21 — Composition →](notebooks/notebook_21_composition.md) ·
[Notebook 26 — Orchestrator →](notebooks/notebook_26_orchestrator_pattern.md) ·
[Notebook 58 — Cognitive router →](notebooks/notebook_58_cognitive_router.md)

## Oracle Cloud, native

The OCI and Oracle Database primitives are first-class classes, not adapters:
same `Agent`, same events, same admission gate.

<div class="grid cards locus-feature-cards" markdown>

- :material-cloud-check:{ .lg .middle } **[OCI Generative AI](concepts/providers/oci.md)**

    ---
    `model="oci:…"` picks the transport from the model id: V1 for OpenAI,
    Meta, xAI, Gemini; SDK for Cohere; Responses where the region serves it.

- :material-server-network:{ .lg .middle } **[Dedicated AI Clusters](how-to/oci-dac.md)**

    ---
    `model="oci:ocid1.generativeaiendpoint…"` targets your own DAC
    endpoint, with the compartment and auth resolved from your profile.

- :material-console:{ .lg .middle } **[OCI tools](notebooks/notebook_89_oci_tools.md)**

    ---
    `use_oci()` and `describe_oci()` put the OCI control plane behind
    tools, so an agent can list, inspect and act on your tenancy.

- :material-database-search:{ .lg .middle } **[Oracle Database 26ai RAG](notebooks/notebook_41_oracle_26ai_rag.md)**

    ---
    `OracleVectorStore` on native `VECTOR` columns, hybrid search, plus
    in-database chunking and embeddings so text never leaves the database.

- :material-content-save:{ .lg .middle } **[26ai checkpoints and history](notebooks/notebook_53_oracle_26ai_checkpointer.md)**

    ---
    `oracle_checkpointer` for durable threads, `OracleCheckpointSaver` for
    versioned history and time travel, OCI Object Storage as the alternative.

- :material-brain:{ .lg .middle } **[26ai long-term memory](notebooks/notebook_88_oracle_agent_memory.md)**

    ---
    `OracleStore` for cross-thread memory and `OracleAgentMemoryManager`
    over Oracle's official agent-memory client.

</div>

<div class="locus-stats" markdown>
<div class="locus-stat" markdown><span class="locus-stat__n">36</span><span class="locus-stat__l">OCI models</span><span class="locus-stat__s">completion + tool call</span></div>
<div class="locus-stat" markdown><span class="locus-stat__n">9,579</span><span class="locus-stat__l">unit tests</span><span class="locus-stat__s">0 failed</span></div>
<div class="locus-stat" markdown><span class="locus-stat__n">278</span><span class="locus-stat__l">integration tests</span><span class="locus-stat__s">0 failed, live on OCI</span></div>
<div class="locus-stat" markdown><span class="locus-stat__n">20</span><span class="locus-stat__l">provider prefixes</span><span class="locus-stat__s">one model string</span></div>
</div>

<p class="locus-chips__vendor">Verified with tool calls on 27 October 2026, eu-frankfurt-1</p>
<div class="locus-chips"><span>gpt-5.5</span><span>gpt-5.4</span><span>gpt-5.2</span><span>gpt-5.1</span><span>gpt-5</span><span>gpt-4.1</span><span>gpt-4o</span><span>gpt-oss-120b</span><span>o3</span><span>gemini-2.5-pro</span><span>gemini-2.5-flash</span><span>llama-3.3-70b</span><span>command-a-03-2025</span><span>embed-v4.0</span><span>rerank-v4.0-fast</span><span>text-embedding-3-large</span></div>

```python
from locus.agent import Agent
from locus.rag import OCIEmbeddings, OracleVectorStore, RAGRetriever

Agent(model="oci:openai.gpt-5.5")                    # V1 transport
Agent(model="oci:cohere.command-a-03-2025")          # SDK transport, auto-routed
Agent(model="oci:ocid1.generativeaiendpoint.oc1...") # your Dedicated AI Cluster

retriever = RAGRetriever(                            # Oracle Database 26ai
    embedder=OCIEmbeddings(model_id="cohere.embed-v4.0"),
    store=OracleVectorStore(dsn="mydb_low", user="locus_app", password="…",
                            wallet_location="~/.oci/wallets/mydb", dimension=1536),
)
agent = Agent(model="oci:openai.gpt-5.5", tools=[retriever.as_tool()])
```

[The full model matrix, including what's retired →](how-to/oci-models.md#verified-on-oci-eu-frankfurt-1-27-october-2026) ·
[Dedicated AI Clusters →](how-to/oci-dac.md) ·
[Oracle Database 26ai notebooks →](notebooks/index.md#oracle-cloud-database-26ai)

## The harness

<div class="grid cards locus-feature-cards" markdown>

- :material-tools:{ .lg .middle } **[Tools and MCP](concepts/tools.md)**

    ---
    `@tool` on any function, typed arguments coerced from whatever the
    model sends, idempotent execution, MCP servers in or out.

- :material-database:{ .lg .middle } **[Memory and RAG](concepts/checkpointers.md)**

    ---
    Durable threads on 10 backends, long-term memory, six vector stores,
    rerankers, and `retriever.as_tool()`.

- :material-shield-lock:{ .lg .middle } **[Grounding, guardrails, admission gate](concepts/control-layer.md)**

    ---
    GSAR checks every claim against evidence; guardrails and steering
    catch the rest; `admit()` holds or denies consequential actions.

- :material-eye:{ .lg .middle } **[Observability and streaming](concepts/observability.md)**

    ---
    One `run_context()` streams typed events from every layer; SSE and
    token streaming for the UI.

- :material-server:{ .lg .middle } **[Server and deploy](concepts/server.md)**

    ---
    `locus serve` puts an agent behind FastAPI with bearer auth and thread
    persistence; a runner image ships for OKE.

- :material-school:{ .lg .middle } **[Skills, playbooks, evaluation](concepts/skills.md)**

    ---
    Progressive-disclosure skills, enforced playbooks, and regression
    suites with `EvalRunner` so behaviour stays put.

</div>

## Control, when you need it

The admission gate is one call around the agent you already have, or built in:

```python
from locus.control import governed_agent

agent = governed_agent(model="oci:openai.gpt-5.5", tools=[...])
print(agent.run_sync("Refund order 8812 if the return was received.").text)
assert agent.audit_trail.verify()   # the chain is intact
```

```bash
pip install locus-sdk && python -m locus.rogue
# 🛡️  wipe_database → deny: labels ['irreversible'] are denied by policy
# FINAL SCORE · dangerous attempts: 1 · BREACHES: 0 · audit chain intact: ✓
```

[How the admission gate works →](concepts/control-layer.md) ·
[First controlled action →](how-to/first-controlled-action.md) ·
[Notebook 83 — Payment refund gate →](notebooks/notebook_83_payment_refund_gate.md)

## How Locus compares

| | Locus | LangGraph | Strands Agents |
|---|---|---|---|
| Agent loop with tools | `Agent` + `@tool` | via LangChain | `Agent` + `@tool` |
| Graphs with state, reducers, interrupts | `StateGraph`, functional API | `StateGraph` | graph tool |
| Pipelines, orchestrator, swarm, handoff, debate | built in | compose yourself | graph, swarm, workflow |
| Cognitive router: task to protocol | built in | — | — |
| Admission gate and signed audit trail | `admit()`, `governed_agent()` | — | — |
| Grounding of every claim | GSAR | — | — |
| OCI Generative AI, DAC, Oracle Database 26ai | native | community packages | — |

As documented by each project in October 2026. [Full comparison →](concepts/compare.md)

## Where next

[All notebooks →](notebooks/index.md) ·
[Capabilities →](capabilities.md) ·
[API reference →](api/index.md) ·
[Deploy →](how-to/deploy.md)

---

**Built inside Oracle. Used in production. Open to everyone.**
