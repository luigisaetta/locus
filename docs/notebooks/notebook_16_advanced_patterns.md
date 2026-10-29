# Advanced graph patterns

The graph primitives that turn a `StateGraph` into a general-purpose
runtime, shown here as a customer-support ticket pipeline. They apply
once a fixed topology is no longer enough: routing decided inside a
node, fan-out to many tickets (or many classifiers), reusable
subgraphs, and a key/value store that persists across graph runs in
the same process.

The pipeline — call it HELPDESK — classifies an incoming ticket and
routes it to the right queue, auto-acknowledges a batch of tickets in
parallel, asks three classifiers about one ticket at once, validates
ticket payloads with a reusable sub-pipeline, remembers customers
across runs and, in its last part, lets a model choose the `Command`
target for a ticket update.

The triage step is confidence-gated: a ticket matched by both strong
classifiers is auto-resolved, one matched by a single strong classifier
gets a drafted reply for an agent to review, and one flagged only by the
length heuristic is escalated to a human agent — so an uncertain
automated decision never reaches the customer on its own.

What this notebook covers:

- `Command(update=..., goto=...)` — write state and pick the next node
  in one return value.
- `goto()` and `end()` — short helpers for common `Command` shapes.
- `scatter("worker", items, key=...)` — fan a list of tickets out so the
  worker node runs once per ticket, in parallel.
- `broadcast(nodes, payload)` — send one ticket to several different
  classifier nodes, then adjudicate the merged signals.
- Subgraph-as-node — call one `StateGraph` from inside another to
  validate a ticket payload.
- `InMemoryStore` — key/value space that outlives a single graph run and
  is shared across runs in one process (data is lost when the process
  exits).

The drawing shows the shared `StateGraph` shape — fixed edges carry the
merged state from node to node and a conditional edge after `review`
picks the next hop; in this notebook that decision moves inside the
node, which returns either a `Command` naming its own successor or a
list of `Send` objects from `scatter` or `broadcast`, whose targets run
at once on the current state plus each payload before a fixed edge
carries the merged results to the fan-in node:

{{ locus_diagram graph }}

## Key lines

The `classify` node has no outgoing edges; the `Command` that
`classify_ticket` returns writes the queue into state and names the
branch that runs next, replacing a conditional edge and a separate state
writer:

{{ locus_source examples/notebook_16_advanced_patterns.py::example_command_routing }}

`broadcast` sends one ticket to the intent, knowledge-base and heuristic
classifiers at once; the fan-in node merges their `send_*` results and
auto-resolves only when both strong signals agree, drafts a suggestion
on one, and escalates when nothing stronger than the length heuristic
fired:

{{ locus_source examples/notebook_16_advanced_patterns.py::example_broadcast }}

The combined pipeline reads VIP status from an `InMemoryStore` to choose
between priority and standard handling, fans the priority actions out
with `scatter`, and records every ticket in the store under the
customer's namespace:

{{ locus_source examples/notebook_16_advanced_patterns.py::example_combined }}

## Run it

```bash
python examples/notebook_16_advanced_patterns.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

Parts 1 to 5 are deterministic and make no model call; only the Part 6
`triage` node sends a ticket update to a model. To stay offline
regardless of the OCI profile on the machine, force the mock model; it
answers in prose rather than with one of the three labels, so the clamp
in `triage` escalates every sample:

```bash
LOCUS_MODEL_PROVIDER=mock python examples/notebook_16_advanced_patterns.py
```

## See also

- [StateGraph](../concepts/multi-agent/graph.md) — the primitive in full:
  per-node policies, `Send` fan-out and Mermaid output.
- [The built-in store](../concepts/checkpointers.md#the-built-in-store-inmemorystore)
  — `InMemoryStore` and the `BaseStore` backends that persist beyond one
  process.
- [Conditional routing](notebook_13_conditional_routing.md) — the
  `add_conditional_edges` router the diagram shows (notebook 13).
- [Scatter-gather with Send](notebook_20_map_reduce_support_triage.md) —
  `Send` fan-out to analyst agents and a reducer that reads their results
  back from state (notebook 20).

## Source

??? note "Full source — `examples/notebook_16_advanced_patterns.py`"

    ````python
    --8<-- "examples/notebook_16_advanced_patterns.py"
    ````
