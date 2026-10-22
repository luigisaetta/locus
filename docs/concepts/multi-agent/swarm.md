# Swarm

A swarm is a peer-to-peer task pool. Agents pull tasks off a shared
queue, run them, and write what they find to a shared context every
peer reads. **Nobody is in charge.**

{{ locus_diagram swarm }}

## What it is

Three pieces:

- A **`SharedContext`** — a typed blackboard (findings, messages, and
  task results) every agent reads and writes.
- A **task queue** — agents pull from it; `add_task` (and task
  decomposition) push to it.
- N **`SwarmAgent`s** — each with its own `capabilities` tags and
  system prompt.

Each iteration, every agent claims the next task it's qualified for,
runs it, writes its findings to the shared context, and claims again
until nothing it can handle is pending. Agents never add tasks. The
swarm exits when no task is pending or `max_iterations` is hit.

## When to use it

- ✅ **Open-ended research** — the swarm's model can split the brief
  into sub-tasks, and each agent sees what the others have already found.
- ✅ **Heterogeneous specialists** — each agent has its own capability
  tags and system prompt, and any of them can pick up the next task
  they're qualified for.
- ✅ **Long-running batch** — a queue depth + a max-iteration budget
  is the natural shape.
- ✅ **No single coordinator should exist** — peer-to-peer is the
  point.

## When NOT to use it

- ❌ The flow is actually **linear** → use [Composition](composition.md).
- ❌ One agent should **decide** who runs → use [Orchestrator](orchestrator.md).
- ❌ The **conversation transcript** should follow one role to another → use [Handoff](handoff.md).
- ❌ You need **strict execution order** — `priority` orders the queue,
  but each agent works through every task it can handle before the next
  agent starts, so a lower-priority task can run before a higher-priority one.

## Code

```python
import asyncio
from locus.models import get_model
from locus.multiagent import create_swarm, create_swarm_agent


async def main():
    model = get_model("{{ locus_example_model }}")

    scout = create_swarm_agent(
        name="Scout",
        capabilities=["search", "collect", "investigate"],
        system_prompt="You are a research scout. Find sources, pull data, scope leads.",
    )
    analyst = create_swarm_agent(
        name="Analyst",
        capabilities=["analyze", "verify", "compare"],
        system_prompt="You are an analyst. Verify claims, cross-check sources, quantify findings.",
    )
    writer = create_swarm_agent(
        name="Writer",
        capabilities=["write", "summarize", "document"],
        system_prompt="You are a writer. Take confirmed findings, draft the report.",
    )

    swarm = create_swarm(
        name="Research swarm",
        agents=[scout, analyst, writer],
        model=model,
    )
    swarm.max_iterations = 12

    result = await swarm.execute(
        initial_task="Research why checkout conversion dropped last week: collect data, verify causes, draft a report.",
    )
    print(result.summary)
    for task in result.completed_tasks:
        print(task.description, "→", task.status)


asyncio.run(main())
```

A `SwarmAgent` carries free-form `capabilities` tags (not a tool list);
tasks are matched to agents by those tags. A task queued with `add_task`
or `execute` can be claimed by any agent with a tag that appears in the
task's description, or by an agent with no tags at all. `execute()` is
async and returns a `SwarmResult` with `completed_tasks`, `failed_tasks`,
a shared `context`, and a `summary`. The same shape runs an incident-response
(IR) war room — a hunter, a forensics analyst, and a reporter pulling
from one queue.

## How tasks enter the queue

You can seed the queue directly with `add_task(...)` (each agent claims
higher-`priority` tasks first), and `execute(decompose_tasks=True)` will
also ask the swarm's model whether to break the initial task into sub-tasks:

```python
swarm = create_swarm(name="Research swarm", agents=[scout, analyst, writer], model=model)

swarm.add_task("Collect last week's conversion-funnel metrics", priority=10)
swarm.add_task("Write the stakeholder status update", priority=3)

result = await swarm.execute()
```

Each iteration, any qualifying agent claims the next task it's eligible
for and works it, recording findings on the shared `context`.

## Termination

Swarms stop when:

- No task is left pending, OR
- `max_iterations` is hit. A pending task no agent can handle keeps the
  swarm going until then, and ends up in neither `completed_tasks` nor
  `failed_tasks`.

## Notebook

[`notebook_24_swarm_multiagent.py`](https://github.com/oracle/locus/blob/main/examples/notebook_24_swarm_multiagent.py)
— a three-agent outage war room (mitigation, diagnostics, comms) with
shared context.

## Source

[`multiagent/swarm.py`](https://github.com/oracle/locus/blob/main/src/locus/multiagent/swarm.py)
— `Swarm`, `SharedContext`.

## See also

- [Multi-agent overview](../multi-agent.md) — pick a shape.
- [Orchestrator](orchestrator.md) — when you DO want a router.
- [Termination](../termination.md) — composable stop conditions.
