# Hooks

For the concepts, start with [Hooks](../concepts/hooks.md).

## Contract

`HookProvider` is the base class every hook subclasses; `HookRegistry`
collects providers and dispatches events in priority order.
`HookPriority` is a plain class of integer constants that determine
dispatch order (lower = earlier — e.g. a guardrail or policy hook runs before a
logging hook).
`ProtectedEvent` marks events whose payloads can be mutated by hooks
(model calls, tool calls); the invocation and iteration hooks receive
plain arguments instead of an event object.

::: locus.hooks.provider.HookProvider
::: locus.hooks.provider.HookPriority
::: locus.hooks.provider.ProtectedEvent
::: locus.hooks.registry.HookRegistry
::: locus.hooks.registry.create_registry

## Hook events

### Write-protected events

Hooks observing these events can mutate the payload before it reaches
the model / tool / next stage.

::: locus.hooks.provider.BeforeModelCallEvent
::: locus.hooks.provider.AfterModelCallEvent
::: locus.hooks.provider.BeforeToolCallEvent
::: locus.hooks.provider.AfterToolCallEvent

### Lifecycle events

The run and iteration boundaries pass no event object. `Agent.run()`
calls `on_before_invocation(prompt, state)`, which returns the state
(possibly modified), then `on_iteration_start(iteration, state)` and
`on_iteration_end(iteration, state)` around each iteration, and
`on_after_invocation(state, success)` at the end of the run.
`Agent.resume()`, which continues a paused run, fires the iteration,
model-call and tool-call hooks but does not call `on_before_invocation`
or `on_after_invocation`. The
`BeforeInvocationEvent`, `AfterInvocationEvent`, `IterationStartEvent`
and `IterationEndEvent` classes (subclasses of `HookEvent`, below) are
still exported from `locus.hooks`, but the agent loop in
{{ locus_sdk_version }} never emits them.

::: locus.hooks.events.HookEvent
::: locus.hooks.events.HookResult

## Built-in hooks

::: locus.hooks.builtin.logging.LoggingHook
::: locus.hooks.builtin.logging.StructuredLoggingHook
::: locus.hooks.builtin.telemetry.TelemetryHook
::: locus.hooks.builtin.telemetry.NoOpTelemetryHook
::: locus.hooks.builtin.retry.ModelRetryHook
::: locus.hooks.builtin.guardrails.GuardrailsHook
::: locus.hooks.builtin.steering.SteeringHook
