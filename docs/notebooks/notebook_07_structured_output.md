# Structured Output

Get a Pydantic object back from a model call instead of a string that
has to be re-parsed — a typed ticket update the rest of the help desk
can route on. Every part below makes a real model call and prints a
`[model call: X.XXs · prompt→completion tokens]` banner.

What this notebook covers:

- `extract_json` / `parse_structured` — pull JSON out of a model reply
  and validate it against a Pydantic schema, the typed contract the
  reply must satisfy.
- `create_schema_prompt` / `create_output_instructions` — emit the
  schema-aware instruction the model needs to comply.
- `Agent(output_schema=YourModel)` — the schema instruction rides the
  system prompt, supporting providers also receive a native
  `response_format`, and the final answer is parsed, repaired on
  failure, and surfaced on `result.parsed`.
- `StructuredOutputError`, raised by `parse_structured(..., strict=True)`
  when a reply fails to parse or validate.

## Prerequisites

- A live, JSON-capable model: OCI Generative AI (the default when
  `~/.oci/config` has a usable profile), or an OpenAI or Anthropic key
  with the matching `LOCUS_MODEL_PROVIDER`.
- For Part 8, a model that returns JSON matching the schema, whether
  through native `response_format` support (OpenAI, and OCI Generative
  AI on the chat-completions transport; see
  [provider compatibility](../concepts/structured-output.md#provider-compatibility))
  or through the prompted instruction and schema repair. Under the mock
  model, the `check_structured_output_capable()` helper exits cleanly
  before the first part runs.

Part 8 hands `IssueList` to `Agent(output_schema=…)`, and the drawing
follows that schema from the constructor argument to `result.parsed` —
the instruction appended to the system prompt, the `response_format` a
call carries when the model supports native structured output and
offers no tools, the agent loop, the parse of the final answer, and the
schema repair that re-prompts with the validation errors when a reply
fails:

{{ locus_diagram structured-output-flow }}

## Key lines

Part 1 pulls JSON out of a reply with `extract_json`; Parts 2 and 3
validate replies against `ContactPoint`, a typed contact reference the
customer relationship management (CRM) system can route on. `Field`
descriptions like these are what Parts 4, 6 and 7 turn into the model's
instruction through `create_schema_prompt` and
`create_output_instructions`:

{{ locus_source examples/notebook_07_structured_output.py::ContactPoint }}

Part 6 parses a chat transcript into `ConversationVerdict`, a
notebook-local schema that bounds `confidence` and `evidence_coverage`
to the 0–1 range. A low coverage value is a typed signal a downstream
step can gate on instead of routing on a guess, the kind of
admit-or-withhold decision [notebook 55](notebook_55_gsar_typed_grounding.md)
builds with GSAR (Grounding-Stratified Adaptive Replanning):

{{ locus_source examples/notebook_07_structured_output.py::ConversationVerdict }}

`IssueList` wraps a list of these; the confidence bounds and the
`Priority` enum are what the parse step validates and what schema repair
re-prompts on when a reply misses them:

{{ locus_source examples/notebook_07_structured_output.py::TicketIssue }}

## Run it

```bash
python examples/notebook_07_structured_output.py
```

Every part needs a live model that can produce JSON. Model choice comes
from `examples/config.py`: OCI Generative AI when `~/.oci/config` has a
usable profile; otherwise set `LOCUS_MODEL_PROVIDER` to `openai` or
`anthropic` with `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in the
environment. There is no offline run: under the bundled mock model,
`check_structured_output_capable()` prints a notice with example
provider settings and exits cleanly (status 0) before Part 1 runs.
Part 8 raises `TypeError`, with a pointer to a stronger model, when the
configured model returns no parsable `IssueList`.

To force a provider and model:

```bash
export LOCUS_MODEL_PROVIDER=openai
export LOCUS_MODEL_ID=gpt-4o
python examples/notebook_07_structured_output.py
```

## See also

- [Structured output](../concepts/structured-output.md) — what lands on
  `AgentResult`, repair on validation failure, and provider
  compatibility.
- [GSAR typed grounding](notebook_55_gsar_typed_grounding.md) — notebook
  55, the admit-or-withhold gate over a typed claim partition; the
  [GSAR concept page](../concepts/gsar.md) defines the grounding score
  and the proceed, regenerate or replan decision.

## Source

??? note "Full source — `examples/notebook_07_structured_output.py`"

    ````python
    --8<-- "examples/notebook_07_structured_output.py"
    ````
