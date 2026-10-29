# Composition Patterns

Chain agents, run them in parallel, or loop one until a stop condition is
met. When privacy work decomposes cleanly into agent-shaped pieces, you do
not need a full `StateGraph`. The three classes here are ready-made
composition primitives: `SequentialPipeline` and `ParallelPipeline` take a
list of `Agent` instances, `LoopAgent` takes one, and each orchestrates the
agents for you. The running scenario is a Data Protection Impact Assessment
(DPIA) over a new customer-analytics dataset.

What this notebook covers:

- `SequentialPipeline` — a personally identifiable information (PII)
  discovery summary feeds a privacy-impact write-up; each agent after the
  first receives the previous agent's output together with the original
  task.
- `ParallelPipeline` — privacy risks and safeguards assessed concurrently
  for the same processing activity, then merged.
- `LoopAgent` — refine a data-subject access request (DSAR) response
  repeatedly until it is APPROVED or `max_loops` is reached.
- One-liner helpers: `sequential()`, `parallel()`, `loop()`.

The diagram draws the three shapes with placeholder agents and three stages
in the sequential and parallel lanes, where this notebook uses two: the PII
analyst and the report writer in sequence, the risk assessor and the
safeguard planner in parallel, and the DSAR response hardener as the one
agent the loop re-runs; every run returns one `PipelineResult`:

{{ locus_diagram composition }}

## Key lines

`SequentialPipeline` takes the two agents in order; the PII analyst's
summary, followed by the original task, becomes the report writer's input
(the default `prompt_template` controls the join), and `result.outputs`
holds one entry per stage:

{{ locus_source examples/notebook_19_composition.py::example_sequential }}

`ParallelPipeline` runs the risk assessor and the safeguard planner on the
same processing activity at once and merges their outputs into
`result.final_output`, by default concatenated with a `---` separator:

{{ locus_source examples/notebook_19_composition.py::example_parallel }}

`LoopAgent` re-runs the response hardener on its own draft through
`loop_prompt` until the `condition` finds APPROVED or `max_loops` is
reached; this `loop_prompt` passes only the previous draft, whereas the
default template also appends the original task:

{{ locus_source examples/notebook_19_composition.py::example_loop }}

## Run it

```bash
python examples/notebook_19_composition.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

To force the mock model and run offline regardless of the local OCI
configuration:

```bash
LOCUS_MODEL_PROVIDER=mock python examples/notebook_19_composition.py
```

Under the mock model every stage returns the same fixed sentence, so the
loop in Part 3 never sees APPROVED and stops when `max_loops` is reached.

## See also

- [Concepts: Composition — pipelines](../concepts/multi-agent/composition.md) — when the pipelines fit and when to reach for `StateGraph`, the orchestrator or a swarm instead.
- [Notebook 20 — Scatter-gather with `Send`](notebook_20_map_reduce_support_triage.md) — the same fan-out shape inside a `StateGraph`, for fan-out that needs shared state.
- [Notebook 63 — Event catalogue](notebook_63_event_catalogue.md) — the `composition.*` events the pipelines publish inside a `run_context`.

## Source

??? note "Full source — `examples/notebook_19_composition.py`"

    ````python
    --8<-- "examples/notebook_19_composition.py"
    ````
