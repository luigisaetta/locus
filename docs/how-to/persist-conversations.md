---
title: Persist conversations
---

# Persist conversations across restarts

The agent keeps conversation state in `AgentState`. Pass a
`BaseCheckpointer` and the same `thread_id` across invocations to
resume a conversation — even across process restarts. This is what
keeps a multi-day case durable: a teammate picks up the same customer
thread tomorrow, on a different worker, with full history intact.

## 1. Pick a backend

Checkpointers come in two shapes. Knowing which shape you're holding
matters: you pass the **native** ones straight to `Agent`, and you
**wrap** the storage-backed ones through a factory.

**Native checkpointers** (subclasses of `BaseCheckpointer` — pass to
`Agent` directly):

- `MemoryCheckpointer` — in-process dict; tests / REPL
- `FileCheckpointer` — JSON files on disk; single-machine dev
- `HTTPCheckpointer` — talks to a remote checkpoint service you run
- `S3Backend` — S3-compatible object storage; lifecycle policies, region replication
  (`s3_checkpointer(...)` is a convenience alias that returns an `S3Backend`)

**Storage-backed checkpointers** (wrap a dict-shaped storage with a
factory):

- `redis_checkpointer(...)` — Redis (self-hosted or managed)
- `postgresql_checkpointer(...)` — Postgres (self-hosted or managed)
- `mysql_checkpointer(...)` — MySQL (via the official Connector/Python async driver)
- `opensearch_checkpointer(...)` — OpenSearch (self-hosted or managed)

The native ones are normal classes — instantiate one, e.g. `S3Backend(...)`, and
hand it to `Agent`. The storage-backed ones are the underlying
`RedisBackend` / `PostgreSQLBackend` / `MySQLBackend` / etc. wrapped by an adapter; if
you instantiate the backend class directly and pass it to `Agent`,
save/load will fail at runtime (the agent calls
`checkpointer.save(state, thread_id)` but backends expose
`save(thread_id, dict)`). Use the matching `*_checkpointer()` factory.

## 2. Instantiate and pass to the Agent

Native checkpointer (no wrapping):

```python
from locus.agent import Agent
from locus.memory.backends import S3Backend

checkpointer = S3Backend(
    bucket="my-app-checkpoints",
    prefix="my-namespace/",
)

agent = Agent(
    model="{{ locus_example_model }}",   # any model — see concepts/models.md
    tools=[...],
    checkpointer=checkpointer,
)
```

Storage-backend with the factory:

```python
from locus.memory.backends import postgresql_checkpointer

checkpointer = postgresql_checkpointer(
    dsn="postgresql://locus:locus@db.example.com:5432/locus",
)
agent = Agent(model="{{ locus_example_model }}", tools=[...], checkpointer=checkpointer)
```

MySQL with the official async driver:

```python
from locus.memory.backends import mysql_checkpointer

checkpointer = mysql_checkpointer(
    dsn="mysql://locus:locus@db.example.com:3306/locus",
)
agent = Agent(model="{{ locus_example_model }}", tools=[...], checkpointer=checkpointer)
```

## 3. Use a stable thread_id

```python
# First turn — new case thread
await agent.run("Open case C-4821 for the billing dispute.", thread_id="case-4821").__anext__()

# Second turn, possibly a different process instance (a teammate tomorrow)
await agent.run("What did we establish so far?", thread_id="case-4821").__anext__()
```

The agent calls `checkpointer.load(thread_id)` at the start of every
run. If state exists, the new user turn is appended and the run
continues. If not, a fresh state is created.

## 4. Tune the checkpoint cadence

By default the agent writes a checkpoint at the end of every run. For
long runs with expensive tools, also write every N iterations:

```python
agent = Agent(
    ...,
    checkpointer=checkpointer,
    checkpoint_every_n_iterations=5,
)
```

## Testing it works

A brand-new `Agent` instance on the same `thread_id` should see the
prior conversation:

```python
agent1 = Agent(..., checkpointer=checkpointer)
await agent1.run("This is case C-4821.", thread_id="t1").__anext__()
del agent1

# Simulates a process restart / different worker (e.g. a teammate tomorrow).
agent2 = Agent(..., checkpointer=checkpointer)
await agent2.run("Which case are we on?", thread_id="t1").__anext__()
# The model sees the earlier user turn.
```

Locus's suite covers pieces of this shape, not the whole of it:
`tests/integration/test_checkpointer_adapters.py::TestAgentWithCheckpointer::test_agent_resumes_from_checkpoint`
checks that a run saves the thread's checkpoint and that it loads back
with at least two messages (it does not check their content), against
`MemoryCheckpointer` with a single `Agent`, and `tests/unit/test_memory_backends_s3.py` exercises
`S3Backend` save/load against an in-process `moto` mock. Neither starts
a second `Agent` on the same thread, and there is no live-bucket test
in the SDK repo — run the snippet above against your own backend.
