# Basic Agent

The smallest end-to-end Locus example. Build LEDGER, a tier-1
transaction-triage agent for a payments team, send it a prompt two ways
(blocking and streaming), and look at what comes back.

What you'll learn:

- How an `Agent` pairs a model with a system prompt.
- The difference between `agent.run_sync(...)` (one result) and
  `agent.run(...)` (an async stream of events).
- The fields on `AgentResult`: `message`, `success`, `stop_reason`,
  `metrics`.
- Reusing the same agent to triage many transactions in a row.

The sample transactions map to common payments patterns: card testing
(many small declines then a charge), an authorized recurring
subscription, and a friendly-fraud chargeback.

Run it:

```
.venv/bin/python examples/notebook_06_basic_agent.py
```

The default provider is the bundled deterministic mock model. Set
`LOCUS_MODEL_PROVIDER=openai` (or anthropic ) and the matching
credentials to send prompts to a live model.

## Source

````python
--8<-- "examples/notebook_06_basic_agent.py"
````
