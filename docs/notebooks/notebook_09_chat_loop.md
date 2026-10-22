# A Chat Loop

Every other example in this suite is a batch script: it asks one thing,
prints the answer, and exits. That is the right shape for teaching a
primitive and the wrong shape for the first thing most people want to do,
which is have a conversation.

This is the missing REPL. It is deliberately small — a loop, a checkpointer,
and one ``thread_id`` — because the interesting part is not the loop, it is
that continuity comes from the checkpointer rather than from anything you
have to hold in your own code. Every turn is saved; the next turn resumes
from the saved state. Swap ``MemoryCheckpointer`` for Redis or Postgres and
the same conversation survives a restart.

Key ideas:

- A ``thread_id`` names the conversation; the checkpointer stores it.
- The loop keeps no history of its own — the agent's state is the history.
- Tool calls are printed as they happen, so you can see the agent act
  rather than infer it from the answer.
- ``/reset`` starts a fresh thread, which shows the boundary a
  ``thread_id`` draws: same agent, no shared memory.

Run it:

```
.venv/bin/python examples/notebook_09_chat_loop.py
```

Non-interactive (CI, or just to see the shape) — the script detects a
non-tty and replays a scripted conversation instead of prompting:

```
echo "" | .venv/bin/python examples/notebook_09_chat_loop.py
```

Live model:

```
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o .venv/bin/python examples/notebook_09_chat_loop.py
```

Set `OPENAI_API_KEY` first. For Anthropic, set `ANTHROPIC_API_KEY`, use
`LOCUS_MODEL_PROVIDER=anthropic`, and set `LOCUS_MODEL_ID` to a Claude model or
leave it out to use the example's default. For any OpenAI-compatible
endpoint, such as ollama, vllm, groq, together or openrouter, keep
`LOCUS_MODEL_PROVIDER=openai`, set `OPENAI_BASE_URL` to its URL,
`OPENAI_API_KEY` to its key (any non-empty value for a local server that
needs none) and `LOCUS_MODEL_ID` to a model it serves.
Set `LOCUS_MODEL_PROVIDER=mock` for an offline run.

## Source

````python
--8<-- "examples/notebook_09_chat_loop.py"
````
