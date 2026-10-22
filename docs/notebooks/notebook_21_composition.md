# Composition Patterns

Chain agents, run them in parallel, or loop one until it's satisfied.
When privacy work decomposes cleanly into agent-shaped pieces, you don't
need a full `StateGraph`. The three pipeline classes here are
batteries-included composition primitives that take a list of `Agent`
instances and orchestrate them for you. The running scenario is a Data
Protection Impact Assessment (DPIA) over a new customer-analytics dataset.

What you'll see:

- `SequentialPipeline` — a PII-discovery summary feeds a privacy-impact
  write-up; each agent's output becomes the next agent's input.
- `ParallelPipeline` — privacy risks and safeguards assessed concurrently
  for the same processing activity, then merged.
- `LoopAgent` — refine a data-subject access request (DSAR) response
  repeatedly until it's APPROVED or `max_loops` fires.
- One-liner helpers: `sequential()`, `parallel()`, `loop()`.

Runs on the same default (mock) as the rest of the notebooks:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_21_composition.py
# or, the zero-setup default (mock):
LOCUS_MODEL_PROVIDER=mock python examples/notebook_21_composition.py
```

## Source

````python
--8<-- "examples/notebook_21_composition.py"
````
