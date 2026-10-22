# Handoff

Handoff is what an escalation desk does. One agent owns the case
until your code decides it needs a different tier; the manager then
hands a **structured summary** — findings and key context — to the
next agent, who picks up where it left off.

{{ locus_diagram handoff }}

## What it is

A handoff flow has:

- A pool of **`HandoffAgent`s** — each a named agent that can receive a
  handoff, with optional `can_escalate_to` / `can_delegate_to` paths
  (lists of agent ids; `execute_handoff` does not check them).
- A **`Handoff` manager** (build it with `create_handoff_manager`) — it
  registers the agents, caps how many handoffs it runs (`max_chain`,
  counted across every handoff in its `history`, not per chain), and
  records the chain of custody.

When the manager runs `execute_handoff(...)`, it packages the case into
a typed **`HandoffContext`** — original task, findings, and
instructions, plus a conversation summary and the source's confidence
when you pass the source's `state` — and hands it to the target agent.
The target reads that context as its opening prompt on the same case.

## When to use it

- ✅ **Support-desk escalation (L1 support → L2 billing)** where the
  case is the unit of work.
- ✅ **SOC tier escalation (L1 → L2 → L3)** — the same shape for a
  security operations center.
- ✅ **"Pass to a human"** — the on-call human is the next tier
  (the HITL notebook below pauses for them with a graph `interrupt()`).
- ✅ **Escalation** when the case turns out to be above the first
  agent's tier (after a few turns of triage, not on first read).
- ✅ The case should **carry its findings forward** so the next
  tier doesn't re-triage from scratch when control transfers.

## When NOT to use it

- ❌ The coordinator delegates a **sub-task** and waits for the
  answer (the conversation belongs to the coordinator) — use
  [Orchestrator](orchestrator.md) instead.
- ❌ Multiple agents should **process the conversation in parallel**
  — use [Composition](composition.md) or [Swarm](swarm.md).
- ❌ The flow is **fully scripted** — handoff is for cases where
  the routing emerges from the conversation.

## Difference vs Orchestrator

| | Handoff | Orchestrator |
|---|---|---|
| Case owner | **moves** between agents | stays with the coordinator |
| Routing decision | your code — it names the target in `execute_handoff` | always the coordinator |
| Receiving agent's view of history | the handoff context (task + findings, plus a conversation summary when you pass `state`) | just the sub-task they were dispatched for |
| Drives the live case? | usually yes | usually no |

## Code

```python
from locus.models import get_model
from locus.multiagent import (
    HandoffReason,
    create_handoff_agent,
    create_handoff_manager,
)

# HandoffAgent calls model.complete() directly, so pass a model client,
# not a "provider:model" string.
model = get_model("{{ locus_example_model }}")

triage = create_handoff_agent(
    name="L1 Support",
    system_prompt=(
        "You are L1 support triage on incoming tickets. "
        "Decide whether this is a billing, shipping, or account case, "
        "then escalate to the right specialist."
    ),
    tools=[lookup_order, lookup_customer],
    model=model,
)
billing = create_handoff_agent(
    name="L2 Billing",
    system_prompt="You are an L2 billing specialist handling escalations.",
    tools=[lookup_order, issue_refund],
    model=model,
)
accounts = create_handoff_agent(
    name="L3 Accounts",
    system_prompt="You are an L3 account specialist handling account takeovers.",
    tools=[lock_account],
    model=model,
)

# Declare the escalation paths (by agent id).
triage.can_escalate_to = [billing.id, accounts.id]

manager = create_handoff_manager(agents=[triage, billing, accounts])

# Hand the case from L1 support up to the L2 billing specialist.
result = await manager.execute_handoff(
    source_agent=triage,
    target_agent_id=billing.id,
    task="Customer 4821 reports a duplicate charge on order ord-4821.",
    reason=HandoffReason.ESCALATION,
    findings={"ticket_id": "t-8804", "order": "ord-4821"},
)
```

`execute_handoff` is async — `await` it. It returns a `HandoffResult`
from the target agent. If the target id isn't registered, or the manager
has already run `max_chain` handoffs, it returns a `HandoffResult` with
`success=False` and an `error` instead, and the target never runs.
`HandoffReason` enumerates why the handoff happened (`SPECIALIZATION`,
`ESCALATION`, `DELEGATION`, ...).

## What transfers across the handoff

The `HandoffContext` the target agent receives carries:

- `original_task` — the `task` you passed to `execute_handoff`.
- `findings` — what the source agent learned, rendered into the
  target's opening prompt.
- `conversation_summary` — only when you pass `state`: each of its
  messages that has text, clipped to 200 characters.
- `confidence` — the `state.confidence` you pass (`0.0` without
  `state`).
- `instructions` — any specific guidance for the next tier.
- `handoff_chain` — the chain of custody (who handed to whom).

By default the raw message transcript is **not** forwarded —
`preserve_full_history` is `False`, so the next tier reads the rendered
context, not the messages themselves. Set
`manager.preserve_full_history = True` to also attach key messages (the
first system message plus the last five messages), which the target's
model receives right after the handoff prompt. Like the conversation
summary, they come from `state`, so nothing is attached unless you pass
it.

## Notebooks

- [`notebook_25_agent_handoff.py`](https://github.com/oracle/locus/blob/main/examples/notebook_25_agent_handoff.py)
  — support-tier escalation (L1 → L2 → L3) on a duplicate-charge
  ticket, with `execute_handoff` and `chain_handoff`.
- [`notebook_33_multiagent_human_in_loop.py`](https://github.com/oracle/locus/blob/main/examples/notebook_33_multiagent_human_in_loop.py)
  — escalating to a human with a graph `interrupt()` (one of three
  human-in-the-loop (HITL) patterns in the same file; it does not use
  the handoff manager).

## Source

[`multiagent/handoff.py`](https://github.com/oracle/locus/blob/main/src/locus/multiagent/handoff.py).

## See also

- [Conversation Management](../conversation-management.md) — how an
  agent's thread is checkpointed. The handoff manager checkpoints
  nothing; its `history` lives in memory on the manager.
- [Multi-agent overview](../multi-agent.md) — pick a shape.
