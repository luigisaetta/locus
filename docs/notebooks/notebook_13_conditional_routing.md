# Conditional routing

Pick the next node at runtime based on graph state. A conditional edge
is a function attached to a node — it runs after the node returns,
reads the current state, and returns the name of the next node. That is
the whole primitive behind branching workflows, fallback paths, and
routing decided by a large language model (LLM).

The running scenario is cloud incident escalation: low-severity
monitoring alerts auto-resolve, high-severity ones page an on-call site
reliability engineer (SRE), and an LLM sorts raw alerts into families
(compute, storage, network).

What this notebook covers:

- Binary and multi-way branching with `add_conditional_edges`.
- Optional `targets` mapping to translate router output to node ids.
- `default` for handling unexpected router output.
- Two routers in sequence (source → role).
- An LLM acting as the router for one node.

The drawing shows the primitive at work on a different graph: fixed edges
carry state from `plan` through `review`, then a conditional edge reads the
merged state and either loops back to `investigate` or ends the run on a
confidence threshold — the same move that, in this notebook, pages the
on-call SRE or auto-closes a monitoring alert on its anomaly confidence:

{{ locus_diagram graph }}

## Key lines

`add_conditional_edges` takes the source node, a router that receives the
state and returns a name, and an optional `targets` mapping; here the router
picks `escalate` or `auto_close` from the `needs_human` flag the `check` node
wrote, and `graph.execute` runs the graph once per alert:

{{ locus_source examples/notebook_13_conditional_routing.py::example_binary_routing }}

When the router can return a value the `targets` mapping does not list,
`default` names the node that receives it, so an alert family outside
compute, storage and network still lands in the general on-call queue:

{{ locus_source examples/notebook_13_conditional_routing.py::example_default_route }}

The classifier node asks a model for a single-word label and routes on it;
the `Agent` is built once outside the node so every execution shares one
model client, and a reply outside the three known labels is clamped so the
conditional edge always finds a target:

{{ locus_source examples/notebook_13_conditional_routing.py::example_llm_router }}

## Run it

```bash
python examples/notebook_13_conditional_routing.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

Parts 1 to 5 are deterministic and make no model call; only the Part 6
classifier does. To stay offline regardless of the OCI profile on the
machine, force the mock model; it answers in prose rather than with one of
the three labels, so the classifier's fallback sends every alert to the
network team:

```bash
LOCUS_MODEL_PROVIDER=mock python examples/notebook_13_conditional_routing.py
```

## Source

??? note "Full source — `examples/notebook_13_conditional_routing.py`"

    ````python
    --8<-- "examples/notebook_13_conditional_routing.py"
    ````
