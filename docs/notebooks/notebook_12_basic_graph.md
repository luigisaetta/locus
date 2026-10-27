# Basic Graph

Build a data-subject-request triage workflow as a graph of nodes that
pass state to each other. A `StateGraph` is a directed graph where each
node is an async function that takes the current state in and returns
updates to merge back. Use it when one Agent isn't enough — multi-step
privacy pipelines (parse → enrich → verdict), branching logic, fan-out /
fan-in across enrichment lookups, human approval gates before a DSAR
response goes out.

What you'll see:

- Nodes and edges; `START` and `END` sentinels.
- Sequential, parallel, and conditional flow on the same primitives.
- `GraphResult` — final state plus per-node status, timing, and order.
- Streaming node updates and pushing custom progress events from inside a node.
- An Agent embedded inside a graph node.

Runs on the same default (mock) as the rest of the notebooks:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_12_basic_graph.py
# or, the zero-setup default (mock):
LOCUS_MODEL_PROVIDER=mock python examples/notebook_12_basic_graph.py
```

## Source

````python
--8<-- "examples/notebook_12_basic_graph.py"
````
