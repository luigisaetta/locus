# Conversation memory

Give an agent a checkpointer and every conversation turn is saved under
its `thread_id`. Call the agent again with that `thread_id` — or attach a
new agent to the same store with the same `thread_id` — and the next turn
starts from the saved conversation, with every earlier message in front
of the model. With a durable backend, that holds across a process restart
too.

This notebook uses `MemoryCheckpointer`, an in-memory store, so it runs
with no setup; its state lasts only as long as the process. For a
conversation that survives a restart, swap in a durable checkpointer —
`FileCheckpointer`, or `redis_checkpointer()` /
`postgresql_checkpointer()` — see [Checkpointers](../concepts/checkpointers.md).

What this notebook covers:

- Building a `MemoryCheckpointer` and passing it to the agent.
- Keying conversations with `thread_id` (one per conversation).
- Pinning a checkpoint after every tool-calling iteration with
  `checkpoint_every_n_iterations=1`.
- A second agent attaching to the same store and picking up the same
  `thread_id`.
- Loading the saved `AgentState` and inspecting it field by field.
- Running many independent threads against a single store.

A checkpointer is the second of the four memory layers an agent can carry
— short-term memory, the thread: agent state saved under a `thread_id` and
loaded back on the next call.

{{ locus_diagram memory-layers }}

## Key lines

One checkpointer on the agent and the same `thread_id` on both calls are
enough for the second turn to see the first:

{{ locus_source examples/notebook_05_agent_memory.py::example_conversation_memory }}

`checkpoint_every_n_iterations=1` pins a checkpoint after each
tool-calling iteration — the default for a run with a `thread_id` on a
store that can delete a single checkpoint, such as `MemoryCheckpointer`,
and the setting to add on one that cannot — so a process killed mid-turn
loses at most the iteration in flight and `Agent.continue_turn(thread_id)`
picks the turn up from the last save:

{{ locus_source examples/notebook_05_agent_memory.py::example_checkpointing_with_tools }}

`checkpointer.load(thread_id)` returns the latest saved `AgentState`: the
whole conversation's messages, plus the last turn's iteration count, tool
history and [Reflexion](../concepts/reasoning.md#reflexion) confidence
history — the three that start afresh on each turn — open for inspection:

{{ locus_source examples/notebook_05_agent_memory.py::example_inspect_checkpoint }}

## Run it

```bash
python examples/notebook_05_agent_memory.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

## See also

- [Checkpointers](../concepts/checkpointers.md) — every backend, and how
  to wire the two checkpointer shapes.
- [Memory](../concepts/memory.md) — the four layers in the diagram above.
- [A chat loop](notebook_04_chat_loop.md) — the same checkpointer behind
  an interactive loop (notebook 04).
- [Oracle agent memory](notebook_44_oracle_agent_memory.md) — long-term
  memory backed by Oracle Database 26ai (notebook 44).

## Source

??? note "Full source — `examples/notebook_05_agent_memory.py`"

    ````python
    --8<-- "examples/notebook_05_agent_memory.py"
    ````
