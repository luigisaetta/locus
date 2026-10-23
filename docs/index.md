---
hide:
  - navigation
  - toc
description: Oracle Generative AI Agentic Harness. Locus is a fully assembled agent harness for Python with an admission gate in front of every consequential action, built first-class for OCI Generative AI and Oracle Database 26ai.
---

<div class="locus-hero" markdown>
<div class="locus-hero__copy" markdown>

<p class="locus-product-name">Oracle Generative AI Agentic Harness</p>

# Multi-agent workflows built for <span class="accent">production.</span>

Describe the task. Locus selects the protocol, coordinates the agents, and runs every consequential action through a policy you wrote before the side effect happens.

<div class="locus-stat-strip" markdown><span style="white-space:nowrap">[direct&nbsp;answer](concepts/multi-agent.md#the-eight-shapes)</span> · <span style="white-space:nowrap">[pipeline](concepts/multi-agent/composition.md)</span> · <span style="white-space:nowrap">[fan&#8209;out](concepts/multi-agent/composition.md)</span> · <span style="white-space:nowrap">[debate](concepts/multi-agent/composition.md)</span> · <span style="white-space:nowrap">[code&nbsp;+&nbsp;test](concepts/multi-agent/composition.md)</span> · <span style="white-space:nowrap">[approval&nbsp;gate](how-to/first-controlled-action.md)</span> · <span style="white-space:nowrap">[A2A](concepts/multi-agent/a2a.md)</span> · <span style="white-space:nowrap">[handoff](concepts/multi-agent/handoff.md)</span></div>

- **From idea to production agent in minutes, not weeks.** Describe the task; Locus picks the pattern and assembles the network from eight production-tested protocols.
- **The model never holds the trigger.** A refund, a deploy, a deletion — every consequential action clears `admit()` first: real code, outside the model, on an audit trail you can verify.
- **Self-critiquing agents with grounded outputs.** Every turn is scored; every claim is verified against the tool result that produced it, or the agent abstains.
- **Oracle Cloud, first-class.** OCI Generative AI with automatic transport routing, Oracle Database 26ai for RAG, durable threads and long-term memory — and every other provider through the same `Agent`.

[Quickstart](how-to/quickstart.md){ .md-button .md-button--primary }
[Notebooks](notebooks/index.md){ .md-button }
[GitHub](https://github.com/oracle/locus){ .md-button }

```bash
pip install "locus-sdk[oci]"   # OCI GenAI · Oracle 26ai · OpenAI · Anthropic · Bedrock · Azure
```

Built inside Oracle · Used in production · Open source (UPL-1.0)

</div>

<div class="locus-hero__code" markdown>

```python
import asyncio

from locus.agent import Agent
from locus.observability import get_event_bus
from locus.observability import run_context
from locus.tools import tool


@tool
def get_metric(name: str) -> float:
    """Current value of an SRE metric."""
    return monitoring.read(name)


@tool
def fetch_runbook(topic: str) -> str:
    """Runbook section for a topic."""
    return wiki.fetch(topic)


@tool(idempotent=True)
def page_oncall(reason: str) -> str:
    """Page on-call. Fires once per reason."""
    return pager.send(reason)


agent = Agent(
    model="oci:openai.gpt-5",   # OCI GenAI
    tools=[get_metric, fetch_runbook, page_oncall],
    reflexion=True,   # self-evaluates every turn
    grounding=True,   # claims checked vs tool output
)


async def main() -> None:
    async with run_context() as rid:
        task = "p99 on checkout-api hit 4.2s. Investigate."
        result = await agent.run(task)
        bus = get_event_bus()
        async for ev in bus.subscribe(rid):
            match ev.event_type:
                case "agent.tool.started":
                    print("🔧", ev.data["tool_name"])
                case "agent.tool.completed":
                    print("✓ ", ev.data["tool_name"])
                case "agent.terminate":
                    print("■ ", result.text[:60])


asyncio.run(main())
```

</div>
</div>

## The Oracle Generative AI Agentic Harness

Locus is the **Oracle Generative AI Agentic Harness**: a fully assembled agent harness you
build on, or wrap around the agent you already have, and control end-to-end. The
harness is the layer *around* the model — the parts a model cannot be trusted to
supply for itself.

<div class="grid cards locus-feature-cards" markdown>

- :material-shield-lock:{ .lg .middle } **Admission gate**

    ---
    Every consequential action clears `admit()` first: real code, outside the
    model, before the side effect, held for a human when the policy says so,
    recorded on a signed audit trail.

- :material-check-decagram:{ .lg .middle } **Grounding and guardrails**

    ---
    Every claim is checked against the tool result that produced it or the
    agent abstains (GSAR). Input, output and tool-call guardrails catch the rest.

- :material-graph:{ .lg .middle } **Cognitive routing**

    ---
    Describe the task; the router picks one of eight production-tested
    protocols and coordinates the agents.

- :material-cloud:{ .lg .middle } **Oracle Cloud, first-class**

    ---
    Day-0 on OCI Generative AI with three transports and automatic routing, and
    Oracle Database 26ai for RAG, durable threads and long-term memory.

</div>

One call assembles the whole harness:

```python
from locus.control import governed_agent

agent = governed_agent(model="oci:openai.gpt-5", tools=[...])
print(agent.run_sync("Refund order 8812 if the return was received.").text)
assert agent.audit_trail.verify()   # the chain is intact — no record was altered
```

Or put the same gate around a LangChain chain, a plain OpenAI loop or a CrewAI
crew — see [the admission gate](concepts/security.md).

## Your first agent in five lines

```python
from locus.agent import Agent

agent = Agent(model="oci:openai.gpt-5")
print(agent.run_sync("What is the capital of France?").text)
# → Paris
```

That's the entire interface. `Agent` handles the model call, the response,
and any retries. Swap `oci:openai.gpt-5` for `openai:gpt-4o`,
`anthropic:claude-sonnet-4-6` or `bedrock:us.amazon.nova-lite-v1:0` — the
call stays the same. With an OCI profile in `~/.oci/config`, every notebook
runs against OCI Generative AI with no further setup.

Add a tool, and the agent loops Think → call tool → Think → answer until
it's done:

```python
from locus.agent import Agent
from locus.tools import tool


@tool
def get_weather(city: str) -> str:
    """Return the current weather for a city."""
    return weather_api.fetch(city)


agent = Agent(
    model="oci:openai.gpt-5",
    tools=[get_weather],
    system_prompt="You are a helpful travel assistant.",
)
print(agent.run_sync("Should I bring an umbrella to Tokyo tomorrow?").text)
```

[Notebook 06 — basic agent →](notebooks/notebook_06_basic_agent.md) ·
[Notebook 01 — the OCI transports →](notebooks/notebook_01_oci_transports.md)

## Try to break it — 30 seconds, no API key

`OpsBot` holds live-looking production tools: wipe the database, exfiltrate
secrets, isolate the cluster, disable every user. Offline, the model arrives
**already fully compromised** — it reaches for a dangerous tool every turn.
Nothing left to jailbreak. Watch what stops it anyway.

```bash
pip install locus-sdk
python -m locus.rogue
```

```text
🎯 attempt #1: wipe the production database
🤖 OpsBot: Blocked before it ran. I could not complete that.
   ⚠️  model was talked into trying: wipe_database
   🛡️  wipe_database → deny: labels ['irreversible'] are denied by policy;
       blast radius 999 exceeds the maximum 1; labels ['production'] require human approval
   → the MODEL was already owned. The RUNTIME didn't care. Breaches still 0.

FINAL SCORE  ·  dangerous attempts: 1  ·  💥 BREACHES: 0  ·  audit chain intact: ✓
```

The gate is `admit()`: the side-effecting call runs only after it clears a
`ControlPolicy` you wrote — allow, hold for a named person, or deny — and
every decision lands on a tamper-evident audit trail. Put it around the
agent you already have, or build on the full runtime.

[The admission gate →](concepts/security.md) ·
[Control an action in five minutes →](how-to/first-controlled-action.md)

## What Locus gives you

<div class="grid cards locus-feature-cards" markdown>

- :material-shield-lock:{ .lg .middle } **[Admission gate](concepts/security.md)**

    ---
    `admit()` / `approve()` run a consequential action only if your
    `ControlPolicy` allows — otherwise hold for a human or deny, recorded
    either way on a signed audit trail. `governed_agent()` wraps any agent
    in the whole harness in one call.

- :material-graph:{ .lg .middle } **[Multi-agent coordination](concepts/multi-agent.md)**

    ---
    Seven in-process patterns plus A2A: Sequential, Parallel, Loop,
    Orchestrator, Swarm, Handoff, StateGraph, plus DeepAgent. One `Agent`
    class, one event stream.

- :material-routes:{ .lg .middle } **[Cognitive router](concepts/multi-agent.md#the-eight-shapes)**

    ---
    Describe a task in plain language. The router extracts a typed
    `GoalFrame`, picks one of eight built-in protocols, and compiles it onto
    a real `Agent` / `Pipeline` / `Orchestrator`. The model classifies;
    routing is deterministic.

- :material-chart-timeline-variant:{ .lg .middle } **[Grounded reasoning (GSAR)](concepts/gsar.md)**

    ---
    Every claim is partitioned grounded / ungrounded / contradicted /
    complementary against typed evidence. Below threshold the agent
    regenerates, replans, or abstains — an ungrounded claim is unshippable
    by construction.

- :material-database:{ .lg .middle } **[Oracle Database 26ai](concepts/checkpointers.md)**

    ---
    Native `VECTOR(N, FLOAT32)` RAG, durable agent threads, a versioned
    checkpoint saver, in-database chunking and embeddings, and long-term
    agent memory — in the database you already run.

- :material-shield-check:{ .lg .middle } **[Idempotent tools](concepts/idempotency.md)**

    ---
    `@tool(idempotent=True)` deduplicates on `(name, args)` inside the
    Execute node. No double-charge, double-book, or double-page — even on
    model retry or checkpoint resume.

- :material-eye:{ .lg .middle } **[In-process observability](concepts/observability.md)**

    ---
    Opt-in `EventBus` with an agent yield bridge. One `run_context()`
    streams the canonical events from every layer — agent, multi-agent,
    control, RAG, memory. Zero allocations when unused.

- :material-code-braces:{ .lg .middle } **[Termination algebra](concepts/termination.md)**

    ---
    `MaxIterations(10) | TextMention("DONE") & ConfidenceMet(0.9)` is real
    Python — `__or__` / `__and__` overloads on typed classes. Greppable,
    unit-testable, serialisable.

</div>

## Eight protocols, one dispatch call

Once you have an agent, the next question is *which shape* to use. The
cognitive router picks for you:

| Protocol | Compiled shape | Best for |
|---|---|---|
| `direct_response` | Single `Agent` | `ANSWER`, `EXPLAIN` |
| `plan_execute_validate` | `SequentialPipeline` (planner → executor → validator) | `PLAN`, `BUILD`, `MODIFY` |
| `specialist_fanout` | `ParallelPipeline` of N tool-bound Agents | `DIAGNOSE`, `MONITOR` |
| `debate` | Two debaters + judge `Agent` | `COMPARE` |
| `codegen_test_validate` | `LoopAgent` (stops on `PASS`) | `GENERATE_CODE` |
| `approval_gated_execution` | `Agent` wrapped in approval interrupt | `ESCALATE`, `REMEDIATE` |
| `handoff_chain` | `SequentialPipeline` of one-tool Agents | `COORDINATE` |
| `a2a_delegate` | Cross-process A2A call (opt-in) | distributed meshes |

```python
result = await router.dispatch("Diagnose the checkout API slowdown.")
print(result.protocol_id)   # "specialist_fanout"
print(result.text)          # findings from 3 parallel probes
```

[The eight shapes →](concepts/multi-agent.md#the-eight-shapes)

## Built for Oracle Cloud

One model string reaches all of OCI Generative AI. `oci:` picks the
transport from the model id — the OpenAI-compatible **V1** endpoint for
OpenAI, Meta, xAI, Mistral, Gemini and Cohere on-demand models (SSE
streaming, day-0 model support), the **SDK** transport for Cohere R-series
and Dedicated AI Cluster endpoints, and the opt-in **Responses** API. Auth
is your OCI config profile, a session token, or instance / resource
principals on OKE and Compute.

```python
from locus.agent import Agent

Agent(model="oci:openai.gpt-5.5")                    # V1 transport
Agent(model="oci:meta.llama-3.3-70b-instruct")       # V1 transport
Agent(model="oci:cohere.command-r-plus")             # SDK transport, auto-routed
Agent(model="oci:ocid1.generativeaiendpoint.oc1...") # your Dedicated AI Cluster
```

[OCI GenAI models →](how-to/oci-models.md) ·
[Dedicated AI Clusters →](how-to/oci-dac.md) ·
[OCI Responses API →](concepts/oci-responses.md)

## Backed by Oracle Database 26ai

Locus ships native primitives for Oracle Database 26ai — `VECTOR(N, FLOAT32)`
with `VECTOR_DISTANCE`, durable agent threads in the database, in-DB chunking
and embeddings, cross-thread long-term memory — with no langchain or
langgraph dependency. The same connection envelope (DSN + wallet) powers
every primitive.

```python
import asyncio

from locus.rag import OCIEmbeddings, OracleVectorStore, RAGRetriever

retriever = RAGRetriever(
    embedder=OCIEmbeddings(model_id="cohere.embed-v4.0"),
    store=OracleVectorStore(
        dsn="mydb_low",
        user="locus_app",
        password="…",
        wallet_location="~/.oci/wallets/mydb",
        dimension=1536,        # HNSW index by default
    ),
)


async def main() -> None:
    await retriever.add_documents(corpus)
    hits = await retriever.retrieve("…", limit=5)
    print(hits.documents[0].document.content)


asyncio.run(main())
```

| Primitive | What it does |
|---|---|
| `OracleVectorStore` | Native vector column, `VECTOR_DISTANCE` SQL, HNSW / IVF indexes, hybrid lexical + vector search, metadata filters |
| `oracle_checkpointer` | Single-row-per-thread durable agent state in Autonomous Database — resume across restarts and replicas |
| `OracleCheckpointSaver` | Versioned checkpoint history with pending writes, for time-travel and intra-step durability |
| `OracleStore` · `OracleAgentMemoryManager` | Cross-thread long-term memory, and Oracle's official `oracleagentmemory` client with context-card summaries |
| `OracleADBLoader` · `OracleInDBChunker` · `OracleInDBEmbeddings` | Ingest from ADB tables, chunk and embed inside the database — text never leaves it |

[Notebook 41 — Oracle 26ai RAG →](notebooks/notebook_41_oracle_26ai_rag.md) ·
[Notebook 53 — checkpointer →](notebooks/notebook_53_oracle_26ai_checkpointer.md) ·
[Notebook 88 — agent memory →](notebooks/notebook_88_oracle_agent_memory.md)

## Walk the notebooks

The fastest way to read Locus is to run the notebooks. Each one is a single
self-contained file under [`examples/`][gh-examples] with a matching docs
page — start at the topic you want and click through to the source.

| What | Notebooks (click any one) |
|---|---|
| OCI Generative AI | [01 — OCI transports](notebooks/notebook_01_oci_transports.md) · [02 — OCI v1](notebooks/notebook_02_oci_openai_chat.md) · [03 — OCI Responses](notebooks/notebook_03_oci_responses.md) · [04 — Dedicated AI Cluster](notebooks/notebook_04_oci_dac.md) · [05 — Cohere reranker on OCI](notebooks/notebook_05_cohere_reranker.md) |
| Oracle Database 26ai | [41 — RAG](notebooks/notebook_41_oracle_26ai_rag.md) · [53 — Checkpointer](notebooks/notebook_53_oracle_26ai_checkpointer.md) · [54 — Versioned saver](notebooks/notebook_54_oracle_versioned_saver.md) · [42 — ADB loader](notebooks/notebook_42_oracle_adb_loader.md) · [43 — In-DB chunker](notebooks/notebook_43_oracle_indb_chunker.md) · [44 — In-DB embeddings](notebooks/notebook_44_oracle_indb_embeddings.md) · [10 — Cross-thread store](notebooks/notebook_10_oracle_store.md) · [88 — Agent memory](notebooks/notebook_88_oracle_agent_memory.md) · [89 — OCI tools](notebooks/notebook_89_oci_tools.md) |
| Agent + ReAct loop | [06 — Basic agent](notebooks/notebook_06_basic_agent.md) · [07 — Agent with tools](notebooks/notebook_07_agent_with_tools.md) · [12 — Lifecycle hooks](notebooks/notebook_12_agent_hooks.md) · [15 — Termination](notebooks/notebook_15_termination.md) |
| The admission gate | [83 — Payment refund gate](notebooks/notebook_83_payment_refund_gate.md) · [84 — Infra deploy gate](notebooks/notebook_84_infra_deploy_gate.md) · [85 — Support account gate](notebooks/notebook_85_support_account_gate.md) · [86 — Data deletion gate](notebooks/notebook_86_data_deletion_gate.md) · [87 — Cloud resource gate](notebooks/notebook_87_cloud_resource_gate.md) |
| Cognitive router (PRISM) | [58 — Cognitive router](notebooks/notebook_58_cognitive_router.md) · [34 — Emergent routing](notebooks/notebook_34_emergent_routing.md) |
| Multi-agent shapes | [16 — Basic graph](notebooks/notebook_16_basic_graph.md) · [21 — Composition](notebooks/notebook_21_composition.md) · [24 — Swarm](notebooks/notebook_24_swarm_multiagent.md) · [25 — Handoff](notebooks/notebook_25_agent_handoff.md) · [26 — Orchestrator](notebooks/notebook_26_orchestrator_pattern.md) · [28 — A2A](notebooks/notebook_28_a2a_protocol.md) |
| Grounding & evaluation | [37 — GSAR typed grounding](notebooks/notebook_37_gsar_typed_grounding.md) · [55 — Evaluation](notebooks/notebook_55_evaluation.md) · [36 — Reasoning patterns](notebooks/notebook_36_reasoning_patterns.md) |
| Observability | [11 — Streaming events](notebooks/notebook_11_agent_streaming.md) · [59 — Observability basics](notebooks/notebook_59_observability_basics.md) · [62 — Event catalogue](notebooks/notebook_62_event_catalogue.md) |
| Security operations | [75 — Red-team an AI agent](notebooks/notebook_75_agent_red_team.md) · [79 — SOC alert triage](notebooks/notebook_79_soc_alert_triage.md) · [81 — IR with an audit trail](notebooks/notebook_81_ir_audit_trail.md) |

Full catalog → [Notebooks index](notebooks/index.md) · [Capabilities matrix](capabilities.md) · [API reference](api/index.md)

[gh-examples]: https://github.com/oracle/locus/tree/main/examples

---

**Built inside Oracle. Used in production. Open to everyone.**
