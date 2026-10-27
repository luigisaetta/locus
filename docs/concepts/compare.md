---
title: How Locus compares
description: Locus next to LangGraph, LangChain and Strands Agents, feature by feature, as each project documents itself in October 2026.
---

# How Locus compares

Locus is an agent harness: the agent loop, the ways to combine agents, and the
runtime around them. The closest neighbours are LangGraph (with LangChain
underneath) and Strands Agents. This page lists where they meet and where
Locus differs, as each project documents itself in October 2026. Check the
other projects' docs for anything that matters to you; they move fast.

## At a glance

| Capability | Locus | LangGraph / LangChain | Strands Agents |
|---|---|---|---|
| Agent loop with tools | `Agent`, `@tool`, typed argument coercion, idempotent tools | agents and tools via LangChain | `Agent`, `@tool` |
| Graphs | `StateGraph` with reducers, conditional edges, `Send` fan-out, interrupts, checkpointed state; functional API | `StateGraph`, functional API | graph multi-agent tool |
| Composition | `SequentialPipeline`, `ParallelPipeline`, `LoopAgent` | compose from graph nodes | workflow tool |
| Orchestrator, swarm, handoff | built in, typed specialists and handoff context | supervisor and swarm libraries | swarm and graph tools |
| Debate, critic loops | notebooks and protocols | build yourself | build yourself |
| Cognitive router (task to protocol) | `Router.dispatch()`: typed `GoalFrame`, eight protocols, deterministic routing | — | — |
| Cross-process agents | A2A protocol client and server | via integrations | A2A support |
| Admission gate, signed audit trail | `admit()`, `approve()`, `governed_agent()`, hash-chained `AuditTrail` | human-in-the-loop interrupts | — |
| Grounding of claims | GSAR: every claim grounded, contradicted or abstained | — | — |
| Guardrails and steering | input, output and tool-call guardrails, LLM-as-judge steering, trace hygiene | via LangChain | guardrail hooks |
| Checkpointers | 10 backends: Oracle Database 26ai (plus versioned saver), OCI Object Storage, PostgreSQL, MySQL, Redis, OpenSearch, S3-compatible, memory, file, HTTP | PostgreSQL, SQLite, Redis, memory, others via packages | session managers |
| Long-term memory | `OracleStore`, Oracle agent memory, LLM memory manager | store API | via providers |
| RAG | six vector stores, OCI and in-database embeddings, Cohere rerankers, `retriever.as_tool()` | via LangChain | via tools |
| Observability | in-process `EventBus`, `run_context()`, 40+ typed events, SSE | LangSmith | OpenTelemetry |
| Serving | `locus serve` (FastAPI, bearer auth, threads), runner image | LangGraph Platform | AgentCore |
| OCI Generative AI | native: V1, SDK and Responses transports, auto-routing, 36 models verified with tool calls | community packages | — |
| Oracle Database 26ai | native vector store, checkpointer, versioned saver, long-term memory, in-database chunking and embeddings | community packages | — |
| Other providers | OpenAI, Anthropic, 17 OpenAI-compatible routes; 16 frontier models verified through OpenRouter on 27 October 2026 | broad | Bedrock-first, others via providers |

## What this means in practice

- **Coming from LangGraph.** The `StateGraph` surface will feel familiar: nodes,
  edges, reducers, `Send`, interrupts, checkpointers. Locus adds the shapes you
  would otherwise assemble from nodes (orchestrator, swarm, handoff, debate), a
  router that picks the shape from the task, and a control layer that runs
  outside the model. See [StateGraph](multi-agent/graph.md) and
  [Compatibility](../compatibility.md) for the known API differences.
- **Coming from Strands Agents.** The agent loop, `@tool` and the multi-agent
  tools map one to one. Locus is Oracle-first where Strands is AWS-first: OCI
  Generative AI and Oracle Database 26ai are native transports and backends,
  and the admission gate plus GSAR grounding have no counterpart.
- **Coming from plain LangChain.** Locus has no LangChain dependency. Its RAG,
  memory and model layers are its own; the Oracle Database 26ai primitives in
  particular do not go through `langchain-oracle`.

## Where to start

- [Multi-agent shapes](multi-agent.md) for the eight protocols and the router.
- [The Agent](agent.md) and [Tools](tools.md) for the loop.
- [Control-layer architecture](control-layer.md) for the admission gate.
- [OCI Generative AI](providers/oci.md) and [OCI GenAI models](../how-to/oci-models.md) for the verified model matrix.
