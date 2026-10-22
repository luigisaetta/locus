# Agent Memory

Give an agent a checkpointer and every conversation turn is saved under
its `thread_id`. Call the agent again with that `thread_id` — or attach a
new agent to the same store with the same `thread_id` — and the
conversation resumes: messages,
tool history, confidence score and all. With a durable backend, that
holds across a process restart too.

What you'll learn:

- Building a `MemoryCheckpointer` and passing it to the agent.
- Keying conversations with `thread_id` (one per conversation).
- Writing a checkpoint after every iteration
  (`checkpoint_every_n_iterations=1`), not only when a run finishes.
- A second agent attaching to the same store and picking up the same
  `thread_id`.
- Loading the saved `AgentState` and inspecting it field by field.
- Running many independent threads against a single store.

This notebook uses `MemoryCheckpointer`, an in-memory store, so it runs
with no setup; its state lasts only as long as the process. For a
conversation that survives a restart, swap in a durable checkpointer —
`FileCheckpointer`, or `redis_checkpointer()` /
`postgresql_checkpointer()` — see [Checkpointers](../concepts/checkpointers.md).

Run it:

```
python examples/notebook_08_agent_memory.py
```

With `LOCUS_MODEL_PROVIDER` unset it uses the bundled mock model, so it
needs no credentials. The agent's model goes through whichever
provider you configure via `LOCUS_MODEL_PROVIDER` (`openai` / `anthropic`) for a live model; set `LOCUS_MODEL_PROVIDER=mock` for offline runs.

## Source

````python
--8<-- "examples/notebook_08_agent_memory.py"
````
