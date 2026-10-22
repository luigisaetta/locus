# Agent Yield Bridge

Every event an agent yields is republished on the bus automatically as
an `agent.*` event whenever a `run_context` is open — no hook
registration, no config flag. Under the hood, `Agent.run` is decorated
with `@_bus_bridge`; the bridge is always there and only fires when
telemetry is active. The scenario is a data-privacy review agent, whose
tool calls are the part DPOs and auditors care about most: every
dataset the reviewer inspects shows up in the run stream.

Event mapping::

    LocusEvent (inner stream)       →  bus event_type
    ─────────────────────────────────────────────────
    ThinkEvent                      →  agent.think
    ToolStartEvent                  →  agent.tool.started   ┐ share span_id
    ToolCompleteEvent               →  agent.tool.completed ┘
    ReflectEvent                    →  agent.reflect
    GroundingEvent                  →  agent.grounding
    ModelChunkEvent                 →  agent.model.chunk      (streaming)
    ModelCompleteEvent              →  agent.model.completed
                                    +  agent.tokens.used      (extra event)
    InterruptEvent                  →  agent.interrupt
    TerminateEvent                  →  agent.terminate

- How nine yielded `LocusEvent` types map to `agent.*` bus events.
- Tool-call telemetry with `span_id` pairing —
  `agent.tool.started` and `agent.tool.completed` share an id so
  consumers can compute durations without subtracting timestamps. Each
  tool span is one auditable review step (classify a field's
  sensitivity, count PII records in a dataset).
- Token usage from `result.metrics` — the canonical source for cost
  meters and budget enforcers on always-on privacy-review automation.

Run it (defaults to the bundled mock model; set `LOCUS_MODEL_PROVIDER` to `openai` / `anthropic` for a live model):

    python examples/notebook_60_agent_yield_bridge.py

Offline:

    LOCUS_MODEL_PROVIDER=mock python examples/notebook_60_agent_yield_bridge.py

## Source

````python
--8<-- "examples/notebook_60_agent_yield_bridge.py"
````
