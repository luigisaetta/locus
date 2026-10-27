# Functional API

Express a payment dispute triage workflow as decorated async functions
instead of a graph. If `StateGraph` feels like overkill for a
straight-line dispute pipeline, the functional API lets you write the
same workflow as ordinary Python: decorate the units of work with
`@task`, decorate the orchestrator with `@entrypoint`, and Locus tracks
timing, retries, and caching behind the scenes. The scenario here is
payments operations: fetch the transaction, look up a risk score, and
assess the dispute.

What you'll see:

- `@task` — a unit of work; can declare `retry_attempts` and `cache`.
- `@entrypoint` — the top-level coroutine; tracks every task it awaits.
- `pipeline.get_result()` returns an `EntrypointResult` with per-task
  metadata.
- Plain `async`/`await` control flow — no graph object, so no state
  reducers, conditional edges, checkpointing or interrupt/resume. Reach
  for `StateGraph` when you need any of those.

The notebook walks through four parts: a two-task fetch-and-assess
pipeline, `@task(retry_attempts=3)` riding out a flaky payment
processor feed, `@task(cache=True)` skipping a repeated risk-score
lookup, and a `@task` wrapping a full Agent call for fraud-risk
assessment.

Runs on the same default (mock) as the rest of the notebooks:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_18_functional_api.py
# or, the zero-setup default (mock):
LOCUS_MODEL_PROVIDER=mock python examples/notebook_18_functional_api.py
```

## Source

````python
--8<-- "examples/notebook_18_functional_api.py"
````
