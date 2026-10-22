# MCP Integration

MCP (Model Context Protocol) is the open standard that lets AI
assistants call tools running in a different process — exactly how a
support desk wires its order system, help center, and billing services
into an agent without bundling them. Locus speaks both sides of it.

- Publish a Locus support agent as an MCP server — tools and the agent's
  own `run_agent` become MCP methods.
- Connect a Locus agent to an external MCP server (an order system, a
  knowledge base) and use its tools as ordinary `@tool`-decorated
  callables.
- Convert tool schemas in both directions
  (`locus_tool_to_mcp` / `mcp_tool_to_locus`).
- Handle `tools/list` and `tools/call` requests programmatically.
- Expose a **refund-eligibility probe** as an MCP tool: a deterministic
  classifier returns an `EligibilityVerdict`, and a GSAR grounding step
  (`gsar_score` / `decide`) either ships the refund decision or abstains
  when signal coverage is too low.

The configured provider drives the agent. The MCP layer is transport-only
— the same agent works against any provider. All tool outputs are mock
data (invented order ids, fixed signals) — no live order system.

## Run it

The bundled mock model is the default; set `LOCUS_MODEL_PROVIDER` for a live provider:

```bash
LOCUS_MODEL_PROVIDER=openai LOCUS_MODEL_ID=gpt-4o python examples/notebook_45_mcp_integration.py
```

Offline:

```bash
LOCUS_MODEL_PROVIDER=mock python examples/notebook_45_mcp_integration.py
```

## Prerequisites

- An OpenAI or Anthropic API key, or `LOCUS_MODEL_PROVIDER` set to
  `openai` / `anthropic` / `mock`.
- Optional: `pip install fastmcp` to exercise live request handling.

See <https://modelcontextprotocol.io> for the MCP specification.

## Source

````python
--8<-- "examples/notebook_45_mcp_integration.py"
````
