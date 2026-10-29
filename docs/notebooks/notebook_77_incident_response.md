# Incident response runbook

This notebook models the loop an on-call site reliability engineer (SRE)
runs when a production page fires, built as a `StateGraph`: the triage,
investigator, synthesizer, mitigator and postmortem nodes each run an
`Agent`, and the routing between them is ordinary graph edges.

A faulty `v4.12.0` deployment triggers the page: the triage agent
classifies severity, then the workflow scatters to three parallel
investigator agents — a log analyst, a metric analyst and a trace
analyst — each inspecting its own signal (pod logs, latency and
saturation metrics, downstream service traces). A synthesizer agent
fuses their reports into a single root-cause hypothesis, a severity gate
decides whether to mitigate automatically or page a human, and the run
ends with a structured postmortem.

What this notebook covers:

- `Send`: fan out to three investigator agents in parallel (logs,
  metrics, traces).
- `add_conditional_edges`: severity-based routing decides between
  automatic mitigation (rollback, scale-up, feature-flag toggle) and
  escalation to a human.
- `interrupt()`: critical severity pauses for explicit human approval
  before any remediation runs.
- `output_schema=Postmortem`: the final report is a typed Pydantic
  instance rather than free text.

The graph below is the one `build_runbook` assembles: a fixed path from
triage through the fan-out to the synthesizer, one conditional edge at
the severity gate, and a fixed path from the mitigator to the
postmortem:

{{ locus_diagram incident-response }}

## Key lines

`build_runbook` wires the shape the diagram draws. `scatter` is a node
whose return value is a list of `Send`s, one per signal; the executor
runs the three investigators, merges their results into state and only
then follows the fixed edge from `scatter` to `synthesize`.
`add_conditional_edges` hands the routing decision to `severity_gate`,
which reads the severity `triage` wrote and returns `page_human` only for
a critical incident. The edge from `page_human` to `auto_mitigate` is
unconditional, so both answers continue to the mitigator:

{{ locus_source examples/notebook_77_incident_response.py::build_runbook }}

On the critical path, `page_human` calls `interrupt()` with the
hypothesis and a yes/no choice, which pauses the run and hands the
payload back to the caller on `result.interrupt`. `main()` resumes with
`Command(resume="yes", update=...)`; because the graph has no
checkpointer, the paused state travels back inside that `Command` with
the model re-injected. The node then runs again from the top, this time
`interrupt()` returns the answer, and `mitigate` reads `human_approved`,
running no agent and recording the mitigation as skipped when the human
declined:

{{ locus_source examples/notebook_77_incident_response.py::page_human }}

`write_postmortem` runs one more `Agent` with `output_schema=Postmortem`
and reads the typed report from `AgentResult.parsed`. That field is `None`
only after the runtime's own schema-repair re-prompts
(`output_schema_retries`, two by default) have failed, and the node then
raises rather than fabricating a record. `StateGraph` does not propagate
that exception: it records the node as failed in `GraphResult.node_results`
and returns `success=False`, so the caller decides what a missing
postmortem means:

{{ locus_source examples/notebook_77_incident_response.py::write_postmortem }}

## Run it

```bash
python examples/notebook_77_incident_response.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

Under the mock model the agents answer with fixed sample text: triage
falls back to `warn`, so no human is paged, and the postmortem writer
cannot produce a `Postmortem`. The graph records the failed node rather
than propagating the error, and `main()` never checks `result.success`,
so the script still exits cleanly (status 0) and reports the postmortem
as missing. To pin a model that supports structured output for the
postmortem schema, use an OCI profile:

```bash
export LOCUS_MODEL_PROVIDER=oci
export LOCUS_MODEL_ID=openai.gpt-4o
python examples/notebook_77_incident_response.py
```

The direct form, `LOCUS_MODEL_PROVIDER=openai` with
`LOCUS_MODEL_ID=gpt-4o`, needs `OPENAI_API_KEY` in the environment.

## See also

- [Multi-agent workflow primitives](../concepts/multi-agent.md#workflow-primitives)
  — `Send`, `interrupt()` and `Agent(output_schema=...)` alongside the
  other workflow primitives.
- [Interrupts and human-in-the-loop](../concepts/interrupts.md) — the
  pause-and-resume contract behind `page_human`.
- [Structured output](../concepts/structured-output.md) — what
  `output_schema` sends to each provider and the repair loop behind
  `result.parsed`.
- [Scatter-gather with Send](notebook_20_map_reduce_support_triage.md) —
  the `Send` fan-out and gather step on its own.
- [Incident response with an audit chain](notebook_76_ir_audit_trail.md)
  — an SRE runbook in which every tool call is recorded on a
  tamper-evident `AuditTrail`.

## Source

??? note "Full source — `examples/notebook_77_incident_response.py`"

    ````python
    --8<-- "examples/notebook_77_incident_response.py"
    ````
