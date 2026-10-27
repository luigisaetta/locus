# Agent Server

This notebook deploys an on-call incident triage copilot as an HTTP API.
`AgentServer` wraps any Locus `Agent` in a FastAPI app: synchronous
invoke, streaming SSE, and persisted incident threads. Auth is a single
shared bearer API key (constructor arg or `LOCUS_SERVER_API_KEY`); the
presented key derives the checkpoint namespace: thread ids are stored as
`<principal>:<tid>`, where `<principal>` is the first 12 hex chars of the
SHA-256 of the key (`anon` when no key is configured). That keeps thread
ids from colliding between deployments with different keys that share one
checkpointer; when a key is configured, a caller that does not present it
gets a 401 from the bearer check before the route runs, so no thread is
read. It is **not** per-engineer isolation: the server holds one key, so
everyone who can call it shares one principal and one thread namespace.
For per-tenant isolation, run one keyed `AgentServer` instance per
tenant — see [Agent Server](../concepts/server.md).

Endpoints:

- `POST /invoke` — synchronous invocation.
- `POST /stream` — SSE streaming.
- `GET /threads/{tid}` — load a persisted incident thread.
- `DELETE /threads/{tid}` — drop a persisted incident thread.
- `GET /health` — health check.

When to use `AgentServer` vs `A2AServer`:

- **AgentServer**: first-party HTTP API. Persisted threads,
  single shared-key bearer auth, key-namespaced thread checkpoints. Use
  when Locus is the system of record and clients are yours (a PagerDuty
  webhook or a deploy dashboard).
- **A2AServer**: cross-framework interop with the A2A message spec.
  Use when another A2A-speaking agent runtime needs to call your Locus
  agent.

Run it:

    # Smoke test against a TestClient (no live server, no live model; still needs REDIS_URL):
    LOCUS_MODEL_PROVIDER=mock python examples/notebook_65_agent_server.py

    # Boot a real uvicorn server on http://127.0.0.1:8000:
    LOCUS_NOTEBOOK_BOOT=1 python examples/notebook_65_agent_server.py

Prerequisites:

- `pip install fastapi uvicorn` and the Redis extra
  (`pip install "locus-sdk[redis]"`) — the checkpointer's Redis client
  is imported lazily, so without it the first checkpoint read or write
  raises `ImportError`.
- A Redis instance with `REDIS_URL` set. **Both** run modes require it:
  the notebook checks the variable before it chooses between the
  TestClient smoke test and the live uvicorn boot, prints what's missing,
  and exits. The Redis-backed checkpointer is what makes
  `GET /threads/{tid}` survive a restart.

## Source

The listing starts after the module docstring; the prose above replaces it.
One printed hint near the end of `example_server()` says two engineers with
different bearer tokens see different incidents for the same `thread_id`.
That holds only across two keyed `AgentServer` instances sharing one
checkpointer: a single keyed server rejects any other token with a 401 on
its invoke, stream and thread routes.

````python
--8<-- "examples/notebook_65_agent_server.py:42"
````
