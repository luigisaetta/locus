# Playbooks

A playbook is a typed, ordered sequence of steps with declared
`expected_tools`. Wire it into an agent and the agent is constrained
to walk the steps in order, calling only the tools each step allows.
Useful for GDPR data-subject requests, right-to-erasure workflows, and
any privacy procedure where you want auditability over agent freedom.

- `PlaybookStep` — id, description, expected tools, hints, validation
  rules.
- `Playbook` — a collection of steps with ordering, max-iteration, and
  tagging.
- `PlaybookPlan` and `StepExecution` — runtime tracking, progress, and
  status (`PENDING` / `IN_PROGRESS` / `COMPLETED` / `FAILED` /
  `SKIPPED`).
- `Agent(playbook=...)` — bind a playbook to an agent and watch it
  execute against real tools.

Each part fires a real model call so you can see live behaviour next
to the structured execution mechanics — every section prints
`[model call: X.XXs · prompt→completion tokens]`.

## Run it

The bundled mock model is the default; set `LOCUS_MODEL_PROVIDER` for a live provider:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_49_playbooks.py
```

Offline:

```bash
LOCUS_MODEL_PROVIDER=mock python examples/notebook_49_playbooks.py
```

## Prerequisites

- An OpenAI or Anthropic API key, or `LOCUS_MODEL_PROVIDER` set to
  `openai` / `anthropic` / `mock`.

## Source

````python
--8<-- "examples/notebook_49_playbooks.py"
````
