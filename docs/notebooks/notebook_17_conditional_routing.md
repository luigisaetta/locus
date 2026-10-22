# Conditional Routing

Pick the next node at runtime based on graph state. A conditional edge
is a function attached to a node — it runs after the node returns,
reads the current state, and returns the name of the next node. That's
the whole primitive behind branching workflows, fallback paths, and
LLM-decided routing.

What you'll see:

- Binary and multi-way branching with `add_conditional_edges`.
- Optional `targets` mapping to translate router output to node ids.
- `default` for handling unexpected router output.
- Two routers in sequence (source → role).
- An LLM acting as the router for one node.

The running scenario is cloud incident escalation: low-severity
monitoring alerts auto-resolve, high-severity ones page an on-call SRE,
and an LLM sorts raw alerts into families (compute, storage, network).

Runs on the same default (mock) as the rest of the notebooks:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_17_conditional_routing.py
# or, the zero-setup default (mock):
LOCUS_MODEL_PROVIDER=mock python examples/notebook_17_conditional_routing.py
```

## Source

````python
--8<-- "examples/notebook_17_conditional_routing.py"
````
