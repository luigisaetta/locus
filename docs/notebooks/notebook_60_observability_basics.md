# Observability Basics

Locus ships an in-process pub/sub `EventBus` that publishes typed
`StreamEvent`s for every meaningful step of execution: agent thinking,
tool calls, model completions, token usage, multi-agent fan-outs,
checkpoints — all under one canonical `event_type` per component. For a
customer-support bot that is the ticket *timeline*: an ordered,
replayable record of every action the agent took on a case, ready for a
QA review or a customer dispute.

Telemetry is opt-in. Code that never enters a `run_context` pays one
`ContextVar.get()` per emission site — no bus, no events, no
allocations.

Pipeline::

    async with run_context() as rid:  ← activates emission; generates run_id
         │
         │  await agent.arun(…)
         │      │
         │      ├─ agent.think         ← one per ReAct iteration
         │      ├─ agent.tool.started  ┐ span_id ties the pair
         │      ├─ agent.tool.completed┘
         │      ├─ agent.tokens.used   ← per model call (cost meter)
         │      └─ agent.terminate
         │
         └─ bus.subscribe(rid)         ← history replay + live stream

- Run an Agent with no telemetry (the SDK-default path).
- Wrap the same ticket reply in `run_context()` and subscribe to the bus.
- The canonical events: `agent.think`,
  `agent.tool.started/completed`, `agent.tokens.used`,
  `agent.terminate`.
- Read the per-run history buffer after the fact (replay semantics for
  late subscribers — reconstruct the ticket timeline after the run).

Run it (defaults to the bundled mock model; set `LOCUS_MODEL_PROVIDER` to `openai` / `anthropic` for a live model):

    python examples/notebook_60_observability_basics.py

Offline:

    LOCUS_MODEL_PROVIDER=mock python examples/notebook_60_observability_basics.py

## Source

````python
--8<-- "examples/notebook_60_observability_basics.py"
````
