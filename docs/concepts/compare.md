---
title: Coming from LangGraph or Strands
description: "How Locus maps onto what you already know from LangGraph, LangChain and Strands Agents, and where it adds something."
---

# Coming from LangGraph or Strands

Locus is an agent harness: the agent loop, the ways to combine agents, and the
runtime around them. If you have built with LangGraph, LangChain or Strands
Agents, most of it will feel familiar. This page is the orientation.

## Coming from LangGraph

The `StateGraph` surface maps closely: nodes, edges, reducers, `Send`
fan-out, interrupts, checkpointers, and a functional API. Locus adds the
shapes you would otherwise assemble from nodes (orchestrator, swarm, handoff,
debate), a router that picks the shape from the task, and a control layer
that runs outside the model. See [StateGraph](multi-agent/graph.md) and
[Compatibility](../compatibility.md) for the known API differences.

## Coming from Strands Agents

The agent loop, `@tool` and the multi-agent tools map one to one. Locus is
Oracle-first: OCI Generative AI and Oracle Database 26ai are native
transports and backends, and the admission gate and GSAR grounding are part
of the runtime rather than add-ons.

## Coming from plain LangChain

Locus has no LangChain dependency. Its RAG, memory and model layers are its
own; the Oracle Database 26ai primitives in particular do not go through
`langchain-oracle`.

## Where to start

- [Multi-agent shapes](multi-agent.md) for the eight protocols and the router.
- [The Agent](agent.md) and [Tools](tools.md) for the loop.
- [Control-layer architecture](control-layer.md) for the admission gate.
- [OCI Generative AI](providers/oci.md) and [OCI GenAI models](../how-to/oci-models.md) for transports and model support.
