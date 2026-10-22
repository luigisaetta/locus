# Specialist Agents

The orchestrator-pattern notebook introduced the Specialist as the worker an orchestrator
hands tasks to. This notebook dives into the Specialist itself, using RIGHTSIZER — a
cloud cost-and-capacity specialist — as the running case: how to
narrow a model's failure surface with a focused system prompt, a
hand-picked tool set, optional playbooks, and a confidence threshold.

RIGHTSIZER fingerprints a compute workload for rightsizing: it maps observable
utilization telemetry (CPU p50, memory mean, IOPS, network throughput) to a
`(family, size, action)` verdict, then only ships the recommendation once the
evidence clears a grounding threshold — an under-observed instance abstains
rather than guessing.

This notebook covers:

- `Specialist` — a Locus `Agent` with role metadata (`specialist_type`,
  `description`), a tool list, and a `confidence_threshold`.
- `Playbook` + `PlaybookStep` — encode a procedure: preconditions,
  ordered steps with required tools and expected outputs, plus failure
  handling.
- `specialist.select_playbook(task)` — picks one playbook from a pool
  by matching the task description.
- Grounding the verdict with the domain-neutral GSAR core
  (`Claim`, `EvidenceType`, `Partition`, `gsar_score`, `decide`,
  `Decision`) — ship a recommendation only when the evidence partition
  scores above the proceed threshold; abstain otherwise.
- Pre-built helpers (`create_log_analyst`, `create_metrics_analyst`,
  `create_trace_analyst`, `create_code_analyst`) for common
  observability domains.

## Prerequisites

- Agent basics.
- The orchestrator-pattern notebook — Specialists are the workers it routes to.

## Run

```bash
python examples/notebook_27_specialist_agents.py
```

The default provider is the bundled mock model. Set `LOCUS_MODEL_PROVIDER`
(openai / anthropic) and credentials to use a live model. Set
`LOCUS_MODEL_PROVIDER=mock` for offline runs.

## Source

````python
--8<-- "examples/notebook_27_specialist_agents.py"
````
