# Advanced Graphs

Per-node retry and caching, plus graph diagrams and live streaming. The
scenario is a cloud-provisioning workflow for a small web tier — a
`launch` step, an `attach` step and a `healthcheck` step — in which a
control-plane call is sometimes throttled. `StateGraph.add_node` accepts
a policy for one node at a time, so the throttled instance-launch call
retries with backoff while the rest of the graph is unchanged, and a
repeated machine-image lookup is served from a cache without changing
how the node is called. The diagram helpers render the graph as text,
the streaming hooks report a node's progress while it runs, and the last
part puts a `RetryPolicy` on a node that calls a model, because the
policy applies to any node regardless of what it does.

What this notebook covers:

- `RetryPolicy` — exponential backoff with optional jitter, per node.
- `CachePolicy` — result caching with a time-to-live (TTL), per node,
  keyed on the node's inputs.
- `draw_mermaid` / `draw_ascii` — render the graph as a Mermaid or an
  ASCII diagram.
- `graph.stream(...)` + `emit_custom` — push progress events from inside
  a node.

The Part 3 provisioning graph is built from two kinds of edge: `add_edge`
fixes the path from START to `launch`, from `launch` to `attach` and from
`healthcheck` to END, and `add_conditional_edges` after `attach` lets a
router send the run to `healthcheck` or directly to END. The two policies
leave those edges unchanged: in Parts 1 and 2 each is passed to
`add_node` on a one-node graph of its own. The drawing shows the same two
edge kinds on a `StateGraph` with a review loop — the solid edges are
fixed with `add_edge`, and the dashed edges after `review` are chosen by
a router through `add_conditional_edges` that loops back to
`investigate` while the confidence written by `review` is below 0.85 and
reaches END once it is 0.85 or higher:

{{ locus_diagram graph }}

## Key lines

A `RetryPolicy` on the `launch` node alone absorbs the throttled control
plane — the launch call raises on its first two attempts, returns the
running instance on the third, and `graph.execute` reports success:

{{ locus_source examples/notebook_17_graph_advanced.py::example_retry }}

A `CachePolicy` with a 60-second TTL on the `lookup` node serves the
second `execute` with the same image name from the cache, so the lookup
function runs once and both results carry the same `image_ocid`:

{{ locus_source examples/notebook_17_graph_advanced.py::example_cache }}

Inside the `provision` node, `emit_custom` pushes stage events while the
run is streamed with `graph.stream(..., mode=StreamMode.UPDATES)`, which
delivers them tagged `StreamMode.CUSTOM` alongside the node's own state
update:

{{ locus_source examples/notebook_17_graph_advanced.py::example_realtime_streaming }}

## Run it

```bash
python examples/notebook_17_graph_advanced.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

Parts 1 to 4 are deterministic and make no model call; only the Part 5
summarizer does. To stay offline regardless of the OCI profile on the
machine, force the mock model:

```bash
LOCUS_MODEL_PROVIDER=mock python examples/notebook_17_graph_advanced.py
```

## Source

??? note "Full source — `examples/notebook_17_graph_advanced.py`"

    ````python
    --8<-- "examples/notebook_17_graph_advanced.py"
    ````
