# Scatter-gather with Send

Three inbound tickets and three triage lenses (sentiment, routing,
resolution) give nine analyst agents running in parallel, then one
synthesizer collapses everything into a single Markdown triage summary.

The pattern is scatter-gather, also called map-reduce: a splitter node
fans the work out as a list of `Send` directives, and a reducer node reads
the results back from the merged graph state.

What this notebook covers:

- `Send(node, payload, metadata)` is a first-class graph primitive: the
  splitter returns a list of Sends and the executor fans them out
  concurrently, without queues or a hand-written `asyncio.gather`.
- Each analyst is a distinct `Agent` with a lens-specific system
  prompt. The graph orchestrates them, not a hand-written loop.
- The synthesizer reads each Send's output back from the merged state and
  renders the final Markdown summary.
- The whole pipeline is one `StateGraph.execute` call. The same graph
  streams through `StateGraph.stream` and checkpoints through `GraphConfig`
  with no change to the nodes, and because each analyst is an ordinary
  `Agent`, agent-level options such as [GSAR](../concepts/gsar.md) typed
  grounding apply to each analyst as to any other agent.

## Prerequisites

- [Basic graph](notebook_12_basic_graph.md).
- [Swarm](notebook_24_swarm_multiagent.md), where agents claim tasks from
  a shared queue instead of each receiving one Send.

Inside the one `StateGraph.execute` call, the splitter returns a `Send`
per ticket and lens. The executor runs the nine analysts concurrently and
merges each successful result into the graph state under its Send's id:

{{ locus_diagram scatter-gather }}

## Key lines

The splitter returns one `Send` per ticket and lens, each naming the
`analyze_one` node and carrying the ticket and role as its payload. Each
analyst receives the graph state with that payload merged on top, so
`analyze_one` reads the ticket and role from its Send and the shared model
from `__model__`:

{{ locus_source examples/notebook_20_map_reduce_support_triage.py::split_tickets }}

The graph declares no edge from `split` to `analyze_one`: each Send carries
its own routing, and the edge from `split` to `synthesize` is where control
goes once every Send has finished:

{{ locus_source examples/notebook_20_map_reduce_support_triage.py::build_triage_graph }}

The synthesizer collects every `analysis` payload from the merged state,
where each Send's result sits under its own id, groups them by ticket and
renders the Markdown summary:

{{ locus_source examples/notebook_20_map_reduce_support_triage.py::synthesize }}

## Run it

```bash
python examples/notebook_20_map_reduce_support_triage.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

## See also

- [Concepts: multi-agent workflow primitives](../concepts/multi-agent.md#send-scatter-map-reduce)
  — `Send` alongside the other workflow primitives.

## Source

??? note "Full source — `examples/notebook_20_map_reduce_support_triage.py`"

    ````python
    --8<-- "examples/notebook_20_map_reduce_support_triage.py"
    ````
