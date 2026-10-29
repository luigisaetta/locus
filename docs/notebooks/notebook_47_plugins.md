# Plugins

Plugins bundle hooks (and optionally tools) into one reusable object —
the natural way to ship a cloud-ops capability like resource-cost triage
with its audit trail attached, so every right-sizing recommendation is
attributable after the fact. Attach a plugin to an agent and every
relevant hook method runs automatically.

What this notebook covers:

- `Plugin` base class — subclass it, give it a `name`, decorate any
  method with `@hook` and the agent picks it up.
- `@hook` decorator — marks methods like `on_before_model_call` and
  `on_before_tool_call` for auto-discovery.
- `callback_handler` — a plain function that receives every event;
  the lighter-weight alternative when a class is not needed.
- `Agent.cancel()` — stop a running agent from another task or thread;
  the next loop step returns `stop_reason="cancelled"`.

## Prerequisites

- An OCI profile in `~/.oci/config` (picked up automatically), or
  `LOCUS_MODEL_PROVIDER` set to `oci`, `openai` or `anthropic` with the
  matching credentials; `mock` runs offline with none.

## Key lines

A plugin is a `Plugin` subclass with a `name` whose `@hook`-decorated
methods are discovered automatically; `CostAuditPlugin` records every
model and tool call, and a single entry in `plugins=[...]` attaches it to
the agent that triages the cost alert:

{{ locus_source examples/notebook_47_plugins.py::example_plugin }}

When a class is more than the job needs, `callback_handler` takes a plain
callable that receives every event; here it collects the event types
emitted during one run:

{{ locus_source examples/notebook_47_plugins.py::example_callback }}

`Agent.cancel()` signals an in-flight run from another task: the run
starts in the background, is cancelled a moment later, and returns with
`stop_reason="cancelled"` together with the tool calls that completed
before the stop:

{{ locus_source examples/notebook_47_plugins.py::example_cancel }}

## Run it

```bash
python examples/notebook_47_plugins.py
```

Model choice comes from `examples/config.py`: OCI Generative AI when
`~/.oci/config` has a usable profile, otherwise the bundled mock model, so the
example also runs offline with no credentials. Set `LOCUS_MODEL_PROVIDER`
(`oci`, `openai`, `anthropic` or `mock`) to force one.

Offline, with the bundled mock model:

```bash
LOCUS_MODEL_PROVIDER=mock python examples/notebook_47_plugins.py
```

## Output

Running it offline — no credentials, bundled mock model — prints the plugin's audit trail of model and tool hooks in firing order, the event types a callback handler receives, and the `cancelled` stop reason with the count of tool calls that completed before `Agent.cancel()` took effect:

```text
=== Part 1: Plugin System ===

Response: Escalate: the indicators line up with an active phishing campaign....
Audit log: ['model: 2 msgs', 'tool: check_instance_utilization', 'model: 4 msgs']

=== Part 2: Callback Handler ===

Events received: ['think', 'terminate']

=== Part 3: Cancel Signal ===

cancel() signalled 1 in-flight run(s)
Stop reason: cancelled
Tool calls completed before the stop: 1
```
<!-- notebook-output:end -->

## Source

??? note "Full source — `examples/notebook_47_plugins.py`"

    ````python
    --8<-- "examples/notebook_47_plugins.py"
    ````
