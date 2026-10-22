# Advanced Graphs

Per-node retry and caching, plus graph diagrams and live streaming.
The scenario is a resilient cloud-provisioning workflow — launch a VM,
attach it, run a health check — where the control plane is flaky by
nature. The executor lets you attach policies to individual nodes, so a
throttled instance-launch call retries with backoff without touching the
rest of the graph, and a repeated machine-image lookup gets cached
without changing how it's called. The visualisation helpers and
streaming hooks give you the operational story to go with it.

What you'll see:

- `RetryPolicy` — exponential backoff with optional jitter, per node.
- `CachePolicy` — TTL-based result caching, per node, keyed on inputs.
- `draw_mermaid` / `draw_ascii` — print the graph as a diagram.
- `graph.stream(...)` + `emit_custom` — push progress events from
  inside a node.

Runs on the same default (mock) as the rest of the notebooks:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_22_graph_advanced.py
# or, the zero-setup default (mock):
LOCUS_MODEL_PROVIDER=mock python examples/notebook_22_graph_advanced.py
```

## Source

````python
--8<-- "examples/notebook_22_graph_advanced.py"
````
