<p align="center">
  <img src="docs/img/og-card.png" alt="Oracle Generative AI Agentic Harness · Locus SDK · pip install locus-sdk · Built by Oracle · github.com/oracle/locus" width="720">
</p>

<p align="center">
  <strong>Oracle Generative AI Agentic Harness</strong><br>
  <em>Multi-agent reasoning orchestrator SDK · Built inside Oracle. Used in production. Open to everyone.</em>
</p>

<p align="center">
  <strong>The agent framework where the model never holds the trigger.</strong><br>
  <em>Your agent is about to issue a refund, ship a deploy, or delete a customer record. Every
  consequential action clears a policy check first — real code, outside the model, before the
  side effect, on a record you can verify. Build on it, or put it around the agent you already
  have.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/locus-sdk/"><img src="https://img.shields.io/pypi/v/locus-sdk.svg?label=PyPI&color=blue" alt="PyPI version"></a>
  <img src="https://img.shields.io/badge/Python-3.11%E2%80%933.14-blue.svg" alt="Python 3.11–3.14">
  <img src="https://img.shields.io/badge/License-UPL--1.0-green.svg" alt="License: UPL-1.0">
  <img src="https://img.shields.io/badge/mypy-strict-brightgreen.svg" alt="mypy strict">
  <img src="https://img.shields.io/badge/ruff-clean-brightgreen.svg" alt="ruff clean">
  <img src="https://img.shields.io/badge/OCI%20GenAI-day%200-orange.svg" alt="OCI GenAI day-0">
</p>

<p align="center">
  <strong>OCI Generative AI · Oracle Database 26ai · OpenAI · Anthropic · 16 OpenAI-compatible endpoints</strong><br>
  <em>Same <code>Agent</code>, same loop, same event stream — only the model id changes.</em>
</p>

<p align="center">
  <a href="https://locusagents.ai/">Documentation</a> ·
  <a href="https://locusagents.ai/concepts/control-layer/">The admission gate</a> ·
  <a href="https://locusagents.ai/how-to/quickstart/">Quickstart</a> ·
  <a href="https://locusagents.ai/how-to/oci-models/">OCI GenAI models</a> ·
  <a href="https://locusagents.ai/concepts/multi-agent/">Multi-agent</a> ·
  <a href="https://locusagents.ai/notebooks/">Notebooks</a>
</p>

<p align="center">
  <em>Oracle Database 26ai is wired in as a first-class backend — native <code>VECTOR(N, FLOAT32)</code> RAG, durable agent threads, in-DB chunking and embeddings, long-term agent memory.</em>
</p>

---

## The Oracle Generative AI Agentic Harness

Locus is the **Oracle Generative AI Agentic Harness**: a fully assembled agent harness you build on, or
wrap around the agent you already have, and control end-to-end. The harness is the layer *around*
the model — the parts a model cannot be trusted to supply for itself:

- **Admission gate.** Every consequential action clears `admit()` first: real code, outside the
  model, before the side effect, held for a human when the policy says so, recorded on a signed
  audit trail.
- **Grounding and guardrails.** Every claim is checked against the tool result that produced it or
  the agent abstains (GSAR); input, output and tool-call guardrails catch the rest.
- **Cognitive routing and multi-agent shapes.** Describe the task; the router picks one of eight
  production-tested protocols — direct answer, pipeline, fan-out, debate, code + test, approval
  gate, A2A, handoff — and coordinates the agents.
- **Oracle Cloud, first-class.** Day-0 on OCI Generative AI (90+ models, three transports,
  automatic routing) and Oracle Database 26ai for RAG, durable threads and long-term memory. Every
  other provider through the same `Agent`.

One call assembles the whole harness:

```python
from locus.control import governed_agent

agent = governed_agent(model="oci:openai.gpt-5", tools=[...])
print(agent.run_sync("Refund order 8812 if the return was received.").text)
assert agent.audit_trail.verify()   # the chain is intact — no record was altered
```

Or put the same `admit()` / `approve()` gate around a LangChain chain, a plain OpenAI loop or a
CrewAI crew — see [The admission gate](#the-admission-gate).

---

## Try to break it — 30 seconds, no API key

`OpsBot` holds live-looking production tools: wipe the database, exfiltrate secrets, isolate
the cluster, disable every user. Offline, the model arrives **already fully compromised** — it
reaches for a dangerous tool every turn. Nothing left to jailbreak. Watch what stops it anyway.

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

Point `LOCUS_MODEL_URL` at your own vLLM / Ollama / LM Studio server to run it against a real
model, or set `ANTHROPIC_API_KEY` for the hard version against a frontier one. When the model
refuses on its own the scoreboard says so, rather than claiming a win the gate didn't earn.

---

## The admission gate

The moment an agent stops advising and starts **acting**, a wrong step becomes a real
consequence. A prompt rule is advisory — a misleading input or an injected document can talk the
model past it. Locus makes the rule **structural**: the side-effecting call runs only after it
clears `admit()`, which the model has no way to reach around.

```python
from locus.control import Action, AuditTrail, ControlPolicy, admit, AdmissionError

policy = ControlPolicy(require_human_for={"production"})
trail = AuditTrail()

async def safe_refund(order_id: str, usd: float):
    try:
        return await admit(
            Action(name="refund", asset=order_id, kind="payment", environment="production"),
            lambda: payments.refund(order_id, usd),     # your code — any agent loop
            policy=policy, trail=trail,
        )
    except AdmissionError as e:
        notify_oncall(e.decision)                       # the gate held it; the trail has it
```

On a tool your own agent calls, `gate_tool` does the same thing in one line —
the returned tool keeps the original's name, description and schema, so the
model cannot tell the difference and nothing else in the agent changes:

```python
from locus.control import ControlPolicy, gate_tool

agent = Agent(model=model, tools=[
    lookup_order,                                     # read-only, ungated
    gate_tool(issue_refund, policy=ControlPolicy()),  # gated
])
```

Refused calls come back to the model as a readable refusal naming the outcome
and the reason, so the agent explains the hold instead of the run ending in a
traceback.

`action → policy → approval → admission → audit`

- **Policy + approval** — `approve()` weighs your `ControlPolicy` (blast radius,
  `require_human_for`, verification score) and returns allow, hold, or deny.
- **Admission** — `admit()` runs the action **only if** approval allows, recording the decision
  to the `AuditTrail`; otherwise it raises `AdmissionError`.
- **Audit** — every entry is linked to the one before it, so editing any record breaks
  `verify()`. (A keyless SHA-256 chain: tamper-evident, not notarized — add signing before
  treating it as legally authoritative.)

Human approvals can survive a restart: with `gate_tool(..., on_refusal="interrupt",
approval=FileApprovals(path))` a hold pauses the run, a checkpointer keeps the conversation,
and once a named person decides, `agent.resume(..., perform_dangling=True)` runs the approved
call exactly once, with the arguments that were approved.

**Measured, not asserted.** Running the integration suite against a weaker judge
model (Qwen3.6-35B) produced the contrast by accident: `SteeringHook` — the SDK's
own LLM-as-judge guardrail — failed open and the agent reported a table deleted,
while in the same session, under the same model, a tool body behind `admit()`
held: the model *did* call the destructive tool, admission refused it, the side
effect never ran, and the refusal landed on a chain that still verifies. Nobody
designed the experiment — a weaker judge is simply the condition under which an
advisory control degrades, and degradation under a weaker model is precisely the
risk a structural control exists to remove. (Recorded in
[#145](https://github.com/oracle/locus/issues/145).)

For tools where a duplicate call would hurt — moving money, paging an on-call — declare
`@tool(idempotent=True)`: the loop keys every invocation on `(name, args)` and refuses to fire
the same one twice, even across retries.

→ [The admission gate](https://locusagents.ai/concepts/control-layer/) ·
[Idempotency](https://locusagents.ai/concepts/idempotency/)

---

## And underneath it, a full SDK

If you're starting fresh rather than wrapping something, the gate sits on a complete agent
framework. A model is a string, a tool is a function, and `run_sync` runs the loop.

```python
from locus import Agent, tool

@tool
def search_flights(origin: str, destination: str, date: str) -> list[dict]:
    """Find available flights between two cities on a given date."""
    return flights.search(origin, destination, date)

agent = Agent(
    model="oci:openai.gpt-5",                     # OCI GenAI; swap providers with one string
    tools=[search_flights],
    system_prompt="You are a travel assistant. Be concise and cite prices.",
)

print(agent.run_sync("Cheapest flight from Lisbon to Berlin next Friday?").text)
```

```bash
pip install "locus-sdk[oci]"           # OCI Generative AI (90+ models, day-0)
pip install "locus-sdk[anthropic]"     # or [openai], or [sdk] for everything
```

And `governed_agent()` gives any Locus agent the whole harness — grounded, guarded, risk-gated,
audited — in one call:

```python
from locus.control import governed_agent

secured = governed_agent(model="oci:openai.gpt-5", tools=[...])
assert secured.audit_trail.verify()   # the chain is intact — no record was altered
```

A bundled `MockModel` means every notebook runs offline with no credentials; with an OCI
profile in `~/.oci/config` the notebooks pick OCI Generative AI automatically.

---

## What you get

**Control** — the runtime that clears actions:

| | |
|---|---|
| **[⚖️ Admission gate](https://locusagents.ai/concepts/control-layer/)** | `admit()` / `approve()` run a consequential action only if your `ControlPolicy` allows — else hold for a human or deny, recorded either way. |
| **[🧠 GSAR grounding](https://locusagents.ai/concepts/gsar/)** | Claims partitioned grounded / ungrounded / contradicted / complementary; below threshold the agent regenerates, replans, or abstains. `arXiv:2604.23366`. |
| **[🎯 Decisions](docs/decision.md)** | `locus.decision` — `Choice` / `YesNo` / `Score` answered with a probability per answer from one forward pass, on any OpenAI-compatible server. An admit head plugs into `approve(advisor=)`; safety heads feed verification. Escalate-only. |
| **[🔁 Idempotent tools](https://locusagents.ai/concepts/idempotency/)** | `@tool(idempotent=True)` — dedupes on `(name, args)`. The model can't double-charge, double-book, or double-page. |
| **[🪝 Hooks](https://locusagents.ai/concepts/hooks/)** | Logging · OpenTelemetry · ModelRetry · Guardrails · Steering (LLM-as-judge). |

**Build** — the agent framework surface:

| | |
|---|---|
| **[🧭 Cognitive router](https://locusagents.ai/concepts/multi-agent/#the-eight-shapes)** | Describe a task → eight named protocols → the right primitive compiled automatically. The LLM fills a typed schema; routing is deterministic. |
| **[🤝 Multi-agent](https://locusagents.ai/concepts/multi-agent/)** | Seven native patterns + cross-process A2A. One `Agent` class. One event stream. |
| **[🔬 DeepAgent](https://locusagents.ai/concepts/deepagent/)** | `create_deepagent` (per-turn grounding) and `create_research_workflow` (StateGraph with post-hoc grounding eval). |
| **[🪙 MCP](https://locusagents.ai/concepts/mcp/)** | `MCPClient` consumes MCP servers. `LocusMCPServer` exposes the SDK's tools as MCP. |
| **[🌐 Multi-modal](https://locusagents.ai/concepts/multi-modal-providers/)** | `Agent(web_search=…, web_fetch=…, image_generator=…, speech_provider=…)` auto-registers tools. |

**Run** — operate it in production:

| | |
|---|---|
| **[📡 Observability](https://locusagents.ai/concepts/observability/)** | Opt-in `EventBus` — one `run_context()` streams 40+ canonical events from every layer, no external broker. |
| **[💾 Durable memory](https://locusagents.ai/concepts/checkpointers/)** | 10 checkpoint backends — Oracle Database 26ai (plus a versioned saver) · OCI Object Storage · PostgreSQL · MySQL · Redis · OpenSearch · S3 / MinIO / R2 · in-memory · file · HTTP. |
| **[🧠 Long-term memory](https://locusagents.ai/concepts/memory-manager/)** | `OracleStore` on 26ai, `OracleAgentMemoryManager` over Oracle's official `oracleagentmemory` client, plus the portable `LLMMemoryManager`, holographic and Postgres stores. |
| **[🔎 RAG](https://locusagents.ai/concepts/rag/)** | 6 vector stores — Oracle 26ai · pgvector · Qdrant · Chroma · OpenSearch · in-memory. OCI, in-database, OpenAI and Cohere embeddings; OCI Cohere, local and Cohere rerankers. |
| **[📡 Streaming + Server](https://locusagents.ai/concepts/server/)** | Typed events · SSE · `AgentServer` (FastAPI, bearer auth, thread persistence). |
| **[📊 Evaluation](https://locusagents.ai/concepts/evaluation/)** | `EvalCase` / `EvalRunner` / `EvalReport` regression suites. |

Every backend is an optional extra — install only what you use
(`pip install "locus-sdk[oci,oracledb]"` for the Oracle stack, `[qdrant,s3,rerank-local]` for others).

---

## Grounded by construction (GSAR)

An agent that *acts* must not assert what it can't back up. Locus's grounding layer implements
GSAR, the method described in [Kamelhar, 2026](https://arxiv.org/abs/2604.23366), and partitions
every claim — **grounded / ungrounded /
contradicted / complementary** — against typed evidence, where tool output outranks inference and
inference outranks domain priors. Below threshold the run **regenerates, replans, or abstains**.
There is no public constructor that emits a grounded result without a score, so an ungrounded
claim is unshippable *by construction* — not filtered after the fact.

```python
from locus.control import ground_finding, Severity, is_finding

result = ground_finding(..., partition=partition)
# A grounded partition → a typed result. An ungrounded one → an auditable
# Abstention with the reason it was withheld. There is no third path.
print(result.title if is_finding(result) else f"withheld: {result.reason}")
```

→ [GSAR grounding](https://locusagents.ai/concepts/gsar/)

---

## The cognitive router and multi-agent shapes

Describe a task in plain language; the **[cognitive router](https://locusagents.ai/concepts/multi-agent/#the-eight-shapes)**
(PRISM) runs an LLM classifier that fills a typed `GoalFrame`, matches it to one of eight
coordination protocols, and compiles the matching runtime primitive. **The model classifies;
routing is deterministic — it never authors the topology.**

| Protocol | Compiled shape | Best for |
|---|---|---|
| `direct_response` | Single `Agent` | `ANSWER`, `EXPLAIN` |
| `plan_execute_validate` | `SequentialPipeline` (planner → executor → validator) | `PLAN`, `BUILD`, `MODIFY` |
| `specialist_fanout` | `ParallelPipeline` of N tool-bound Agents | `DIAGNOSE`, `MONITOR` |
| `debate` | Two debaters + judge `Agent` | `COMPARE` |
| `codegen_test_validate` | `LoopAgent` (stops on `PASS`) | `GENERATE_CODE` |
| `approval_gated_execution` | `Agent` wrapped in approval interrupt | `ESCALATE`, `REMEDIATE` |
| `handoff_chain` | `SequentialPipeline` of one-tool Agents | `COORDINATE` |
| `a2a_delegate` | Cross-process agent-to-agent call (opt-in) | distributed meshes |

Each shape is also a first-class primitive you can use directly — `SequentialPipeline`,
`ParallelPipeline`, `LoopAgent`, `Orchestrator`, `Swarm`, `Handoff`, `StateGraph`, `A2A`.

```python
import asyncio

from locus.agent import Agent, SequentialPipeline


async def main():
    result = await SequentialPipeline(agents=[draft, check, finalize]).run(
        "Summarize the trade-offs of moving the checkout service to a queue."
    )
    print(result.final_output)


asyncio.run(main())
```

→ [Cognitive router](https://locusagents.ai/concepts/multi-agent/#the-eight-shapes) ·
[All patterns](https://locusagents.ai/concepts/multi-agent/)

---

## Providers

A model is a string. The prefix picks the provider; the rest is the model id it expects.

**20 prefixes ship built in.** `oci:`, `openai:` and `anthropic:` are native;
the rest are OpenAI-compatible endpoints with their base URL and key convention already
filled in — `gemini:` · `ollama:` · `vllm:` · `lmstudio:` · `llamacpp:` · `litellm:` ·
`groq:` · `together:` · `openrouter:` · `deepseek:` · `mistral:` · `xai:` · `fireworks:` ·
`cerebras:` · `perplexity:` · `nvidia:`, plus `openai-compatible:` for anything else.

```python
Agent(model="oci:openai.gpt-5.5")                   # OCI GenAI → V1 transport, OCI_PROFILE from the environment
Agent(model="oci:cohere.command-r-plus")            # OCI GenAI → SDK transport, auto-routed
Agent(model="ollama:llama3.2")                      # localhost:11434, no key needed
Agent(model="groq:llama-3.3-70b-versatile")         # GROQ_API_KEY from the environment
Agent(model="anthropic:claude-sonnet-5")
Agent(model="gemini:gemini-2.0-flash")              # GEMINI_API_KEY
```

`oci:` picks the transport from the model id. OpenAI, Meta Llama, xAI Grok, Mistral and
Google Gemini go through **V1** (`OCIChatCompletionsModel`, the OpenAI-compatible
`/openai/v1` endpoint — SSE streaming, day-0 model support); Cohere (Command R and
Command A) and Dedicated AI Cluster endpoint OCIDs go through the **SDK** transport
(`OCIModel`); the server-stateful **Responses** API is opt-in (`OCIResponsesModel`). Auth is
the OCI config profile, a session token, or instance / resource principals on OKE and
Compute. Install with `pip install "locus-sdk[oci]"`.

| Provider | Transport | Models |
|---|---|---|
| **OCI Generative AI** | **V1** (`OCIChatCompletionsModel`) — default | OpenAI commercial · Meta Llama · xAI Grok · Mistral · Google Gemini · Cohere on-demand |
| **OCI Generative AI** | **SDK** (`OCIModel`) — auto for `cohere.*` and DAC OCIDs | Cohere native chat API (Command R and Command A) · Dedicated AI Clusters |
| **OCI Generative AI** | **Responses** (`OCIResponsesModel`) — opt-in | Server-stateful endpoint for OpenAI / xAI / Gemini Responses-only models |

`gemini:` uses Google's own OpenAI-compatible endpoint, so it needs no additional client.

Configuration that is not in the environment travels in `model_kwargs` — a per-agent key, or
a host that is not the default:

```python
Agent(
    model="openai-compatible:qwen3.6-35b",
    model_kwargs={"base_url": "http://gpu-1:8000/v1", "api_key": "unused"},
)
```

Anything else implements `ModelProtocol` — `complete` · `stream`, ~50 lines — and registers
with `register_provider("myco", MyModel)`.

→ [Model providers](https://locusagents.ai/concepts/models/) ·
[OCI GenAI models](https://locusagents.ai/how-to/oci-models/) ·
[OCI Dedicated AI Cluster](https://locusagents.ai/how-to/oci-dac/) ·
[OpenAI-compatible endpoints](https://locusagents.ai/concepts/providers/openai-compatible/)

---

## Backed by Oracle Database 26ai

The SDK ships native primitives for **Oracle Database 26ai** — vector
search, durable agent threads, in-database chunking and embeddings, and
a long-term key/value store. The contract is owned end-to-end inside
`locus.rag.stores` and `locus.memory.backends`, and the same connection
envelope (DSN + wallet) powers every primitive.

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

The eight primitives:

| Primitive | What it does |
|---|---|
| **`OracleVectorStore`** | Native `VECTOR(N, FLOAT32)` column · `VECTOR_DISTANCE` SQL · HNSW / IVF / flat indexes · hybrid lexical + vector search · Mongo-style metadata filters · MMR re-rank. |
| **`oracle_checkpointer`** | Single-row-per-thread durable agent state in Autonomous Database. Resume conversations across restarts, replicas, operator handoffs. |
| **`OracleCheckpointSaver`** | LangGraph-shape versioned checkpoint history — every step preserved, with pending writes for intra-step durability. |
| **`OracleStore`** | Cross-thread long-term memory: namespaced key/value with optional vector search inside a namespace (`aput` / `aget` / `asearch` aliases for langgraph-oracledb parity). |
| **`OracleADBLoader`** | Stream rows out of any SELECT as `Document` objects (lazy or eager). Feed straight into a chunker, embedder, or retriever. |
| **`OracleInDBChunker`** | Server-side text chunking via `DBMS_VECTOR_CHAIN.UTL_TO_CHUNKS`. Text never leaves the database. |
| **`OracleInDBEmbeddings`** | In-database ONNX embeddings via `DBMS_VECTOR_CHAIN.UTL_TO_EMBEDDING`. Zero round-trips when the embedding model is loaded in the DB. |
| **`OracleAgentMemoryManager`** | Long-term agent memory over Oracle's official `oracleagentmemory` client — context-card summaries, scoped retrieval by user / agent / thread. |

The contracts live in the SDK, the SQL is generated locally, and the
only runtime requirement is `python-oracledb` thin mode.

→ [Notebook 38 — Oracle 26ai RAG](https://locusagents.ai/notebooks/notebook_38_oracle_26ai_rag/) · [Notebook 42 — Oracle 26ai checkpointer](https://locusagents.ai/notebooks/notebook_42_oracle_26ai_checkpointer/) · [Notebooks 39-41, 54, 10, 88 — loader, chunker, embeddings, versioned saver, store, agent memory](https://locusagents.ai/notebooks/#oracle-cloud-database-26ai)

---

## Notebooks and deploy

[`examples/`](examples/) has progressive notebooks, numbered in suggested reading order. Each
defaults to the bundled mock model when no API key is present.

```bash
git clone https://github.com/oracle/locus.git
cd locus-sdk && pip install -e .

python examples/notebook_01_oci_transports.py        # the three OCI GenAI transports
python examples/notebook_02_basic_agent.py           # your first agent
python examples/notebook_38_oracle_26ai_rag.py       # RAG on Oracle Database 26ai
python examples/notebook_29_cognitive_router.py      # the cognitive router
python examples/notebook_32_research_workflow.py     # full research pipeline
```

For production, `AgentServer` is a drop-in FastAPI app (`POST /invoke`, `POST /stream`, `GET/DELETE /threads/{id}`, `GET /health`)
and the repo ships a multi-stage `Dockerfile`.

```python
from locus.server import AgentServer

AgentServer(agent=my_agent, api_key=os.environ["API_KEY"]).run(host="0.0.0.0", port=8080)
```

→ [Notebooks](https://locusagents.ai/notebooks/) ·
[Deploy](https://locusagents.ai/how-to/deploy/)

---

## Any domain, one contract

The same contracts run wherever an agent acts. Security-domain tooling built on them — AI
red-teaming, SOC triage, and threat-intel / SIEM / EDR adapters — ships separately as the opt-in
[`locus-sdk-security`](https://github.com/oracle/locus/tree/main/packages/locus-sdk-security) package,
installed from this repository (it is not published to PyPI); the core runtime does not include it.

---

## Repo layout

```text
src/locus/
├── control/        Admission gate, policy, audit trail, grounded findings, verification
├── decision/       Typed decisions (choice, yes/no, score) with probabilities; per-tenant heads
├── rogue/          The rogue-agent challenge (`python -m locus.rogue`)
├── agent/          Agent runtime, config, Sequential / Parallel / Loop pipelines
├── core/           AgentState, Message, events, termination algebra, Send
├── loop/           ReAct nodes (Think, Execute, Reflect)
├── router/         Cognitive router — GoalFrame, ProtocolRegistry, PolicyGate, Compiler
├── reasoning/      Reflexion, Grounding, Causal, GSAR
├── multiagent/     Orchestrator, Swarm, Handoff, StateGraph, Functional
├── a2a/            Cross-process Agent-to-Agent protocol
├── deepagent/      create_deepagent + create_research_workflow + 6 node primitives
├── memory/         BaseCheckpointer + 10 backends (Oracle 26ai, OCI Object Storage, …), stores, memory managers
├── rag/            Embeddings + 6 vector stores (Oracle 26ai, …) + rerankers + loaders + chunkers
├── models/         Provider registry + OCI GenAI (V1 / SDK / Responses), OpenAI, Anthropic
├── tools/          @tool decorator, registry, builtins, executors
├── hooks/          Logging, telemetry, retry, guardrails, steering
├── observability/  EventBus, run_context, agent yield bridge, EV_* constants
├── skills/         AgentSkills.io filesystem-first capability disclosure
├── playbooks/      Declarative step plans + PlaybookEnforcer
├── providers/      Multi-modal: web search, web fetch, image, speech
├── server/         FastAPI AgentServer with thread persistence
├── evaluation/     EvalCase + EvalRunner + EvalReport
└── integrations/   MCP (client + server)
```

The docs site lives in [`docs/`](docs/) (`mkdocs.yml`, theme in `overrides/`, build hooks in
`hooks/`) and publishes to [locusagents.ai](https://locusagents.ai/).

---

## Contributing

```bash
git clone https://github.com/oracle/locus.git
cd locus-sdk && pip install -e ".[dev,sdk]"
hatch run check        # ruff + mypy
hatch run test         # unit tests across Python 3.11–3.14
pre-commit install
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions need the
[Oracle Contributor Agreement](https://oca.opensource.oracle.com); every PR runs format,
lint, mypy, unit tests and the OCA check.
Please consult the [security guide](./SECURITY.md) for vulnerability disclosure.

---

## GSAR reference

Locus's GSAR layer is based on the method described in F. A. Kamelhar,
[GSAR: Typed Grounding for Hallucination Detection and Recovery in Multi-Agent LLMs](https://arxiv.org/abs/2604.23366)
([PDF](https://arxiv.org/pdf/2604.23366)), arXiv:2604.23366, 2026. The paper is separate from this
project; if you use the method, cite it directly:

```bibtex
@article{kamelhar2026gsar,
  author  = {Kamelhar, Federico A.},
  title   = {GSAR: Typed Grounding for Hallucination Detection and Recovery in Multi-Agent LLMs},
  journal = {arXiv preprint arXiv:2604.23366},
  year    = {2026},
  url     = {https://arxiv.org/abs/2604.23366},
}
```

---

## License

Copyright (c) 2025, 2026 Oracle and/or its affiliates.

Released under the **Universal Permissive License v1.0** — see [LICENSE](LICENSE) and
[THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt). Releases `1.0.0` – `2.28.0` were
published as `tulip-agents` under the Apache License 2.0 while the project was developed
outside Oracle; they remain available under that licence from their tags. See
[PROVENANCE.md](PROVENANCE.md).
