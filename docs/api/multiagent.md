# Multi-agent

Ways to combine agents into one system — pipelines, an orchestrator
with specialists, swarms, handoffs, and the `StateGraph` workflow
primitive.

For the concepts, start with [Multi-agent workflows](../concepts/multi-agent.md).

## Composition

The agent-level pipelines. Each exposes an async `run(task)` that
returns a `PipelineResult` (`success`, `outputs`, `final_output`,
`duration_ms`, `error`) — `await pipeline.run(task)`.

::: locus.agent.composition.SequentialPipeline
::: locus.agent.composition.ParallelPipeline
::: locus.agent.composition.LoopAgent

## Orchestrator + Specialists

A central `Orchestrator` routes each turn to one of N domain-focused
`Specialist`s. `RoutingDecision` is the typed decision record; the
built-in specialists below are factory-built for common roles.

::: locus.multiagent.orchestrator.Orchestrator
::: locus.multiagent.orchestrator.OrchestratorResult
::: locus.multiagent.orchestrator.RoutingDecision
::: locus.multiagent.orchestrator.create_orchestrator
::: locus.multiagent.specialist.Specialist
::: locus.multiagent.specialist.SpecialistResult
::: locus.multiagent.specialist.Playbook
::: locus.multiagent.specialist.PlaybookStep

### Built-in specialists

::: locus.multiagent.specialist.create_code_analyst
::: locus.multiagent.specialist.create_log_analyst
::: locus.multiagent.specialist.create_metrics_analyst
::: locus.multiagent.specialist.create_trace_analyst

## Swarm

Self-organizing agents that pick up tasks from a shared queue and
share progress via `SharedContext`.

::: locus.multiagent.swarm.Swarm
::: locus.multiagent.swarm.SharedContext
::: locus.multiagent.swarm.SwarmAgent
::: locus.multiagent.swarm.SwarmTask
::: locus.multiagent.swarm.SwarmResult
::: locus.multiagent.swarm.TaskStatus
::: locus.multiagent.swarm.create_swarm
::: locus.multiagent.swarm.create_swarm_agent

## Handoff

Agent-to-agent context transfer. `HandoffReason` is the typed reason
the source agent emitted; `HandoffContext` is the carried state.

::: locus.multiagent.handoff.Handoff
::: locus.multiagent.handoff.HandoffAgent
::: locus.multiagent.handoff.HandoffContext
::: locus.multiagent.handoff.HandoffReason
::: locus.multiagent.handoff.HandoffEvent
::: locus.multiagent.handoff.HandoffResult
::: locus.multiagent.handoff.create_handoff_agent
::: locus.multiagent.handoff.create_handoff_manager

## StateGraph

DAG-based workflow with explicit nodes, edges, reducers, and a typed
state. The most expressive composition primitive — used by
`create_research_workflow` (see [DeepAgent](deepagent.md)) and the
router's compiled `Runnable`s.

To publish a compiled graph over HTTP or A2A, wrap it in `GraphRunnable` —
see [Serving a graph](server.md#serving-a-graph).

::: locus.multiagent.graph.StateGraph
::: locus.multiagent.graph.GraphConfig
::: locus.multiagent.graph.Graph
::: locus.multiagent.graph.GraphResult
::: locus.multiagent.graph.Node
::: locus.multiagent.graph.NodeResult
::: locus.multiagent.graph.NodeStatus
::: locus.multiagent.graph.Edge
::: locus.multiagent.graph.ConditionalEdge
::: locus.multiagent.graph.CachePolicy
::: locus.multiagent.graph.RetryPolicy
::: locus.multiagent.graph.StreamMode
::: locus.multiagent.graph.StreamEvent

### Special nodes

::: locus.multiagent.graph.START
::: locus.multiagent.graph.END

### Convenience builders

::: locus.multiagent.graph.create_graph
::: locus.multiagent.graph.node
::: locus.multiagent.graph.emit_custom

## Functional API

::: locus.multiagent.functional.task
::: locus.multiagent.functional.entrypoint

## A2A protocol

::: locus.a2a.protocol.A2AServer
::: locus.a2a.protocol.A2AClient
