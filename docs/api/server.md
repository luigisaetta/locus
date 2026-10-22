# Agent Server

Drop-in FastAPI wrapper — `POST /invoke`, `POST /stream`,
`GET`/`DELETE /threads/{id}`, `GET /health`.

For the concepts, start with [Agent Server](../concepts/server.md).

::: locus.server.app.AgentServer

## Serving a graph

`GraphRunnable` adapts a compiled `StateGraph` to the runnable interface
`AgentServer` and [`A2AServer`](a2a.md) expect. The value at `output_key` in
the graph's final state becomes the reply; with no `output_key`, the whole
final state is stringified. The server's `thread_id` and `metadata` are
accepted but not yet passed to the graph, and the `GET`/`DELETE /threads/{id}`
routes don't work for a served graph: they read the wrapped agent's
`config.checkpointer`, which `GraphRunnable` doesn't have.

::: locus.server.adapters.GraphRunnable
