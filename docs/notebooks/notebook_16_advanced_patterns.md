# Advanced Patterns

Five primitives that turn a `StateGraph` into a general-purpose
runtime, shown here as a customer-support ticket pipeline. Reach for
these once basic graphs stop being enough: dynamic routing from inside
a node, fan-out to many tickets (or many classifiers), reusable
subgraphs, cross-conversation key/value storage, and combining them
in one workflow.

The pipeline — call it HELPDESK — classifies an incoming ticket and
routes it to the right queue, auto-acknowledges a batch of tickets in
parallel, asks several classifiers about one ticket at once and only
auto-resolves when they agree, validates ticket payloads with a
reusable sub-pipeline, and remembers customers across runs.

What you'll see:

- `Command(update=..., goto=...)` — write state and pick the next node
  in one return value.
- `goto()` and `end()` — short helpers for common `Command` shapes.
- `scatter("worker", items, key=...)` — fan a list of tickets out to
  copies of a worker node.
- `broadcast(nodes, payload)` — fan one ticket out to several different
  classifier nodes, then adjudicate the merged signals.
- Subgraph-as-node — call one `StateGraph` from inside another to
  validate a ticket payload.
- `InMemoryStore` — in-process key/value space shared across runs within
  one process (data is lost when the process exits).

The triage step is confidence-gated: a ticket several independent
classifiers agree on is auto-resolved, while one only a weak heuristic
flagged is escalated to a human agent — so an uncertain automated
decision never ships to the customer on its own.

Runs on the same default (mock) as the rest of the notebooks:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_16_advanced_patterns.py
# or, the zero-setup default (mock):
LOCUS_MODEL_PROVIDER=mock python examples/notebook_16_advanced_patterns.py
```

## Source

````python
--8<-- "examples/notebook_16_advanced_patterns.py"
````
