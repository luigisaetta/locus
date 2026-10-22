# ReAct loop

!!! warning "Deprecated — removed in 3.0.0"

    `locus.loop` is a second ReAct implementation, parallel to the one
    [`Agent`](agent.md) runs, and `Agent` has never used it. Two
    implementations of the same idea drift, and a bug fixed in one stays live
    in the other. Nothing here is a capability `Agent` lacks.

    Everything below still imports and works until 3.0.0, per the
    [deprecation policy](https://github.com/oracle/locus/blob/main/DEPRECATION.md).
    Each access emits `LocusDeprecationWarning`; to find them in your own code:

    ```
    python -W error::DeprecationWarning -m pytest
    ```

    | Instead of | Use |
    |---|---|
    | `ReActLoop`, `create_react_loop` | [`Agent`](agent.md) |
    | `ReActLoopConfig` | [`AgentConfig`](agent.md) |
    | `LoopRunner` | `await agent.arun(prompt)` |
    | `BatchRunner` | [`EvalRunner`](evaluation.md) |
    | `StreamingCollector` | `async for event in agent.run(prompt)` |
    | `ConditionalRouter` | [`StateGraph`](multiagent.md) conditional edges |
    | `ThinkNode` / `ExecuteNode` / `ReflectNode` | internal to `Agent`; hook them with [hooks](hooks.md) |

The low-level ReAct (reason + act) loop primitives, kept here for reference
while the deprecation runs.

## Loop

::: locus.loop.react.ReActLoop
::: locus.loop.react.ReActLoopConfig
::: locus.loop.react.create_react_loop

## Nodes

::: locus.loop.nodes.Node
::: locus.loop.nodes.NodeResult
::: locus.loop.nodes.ThinkNode
::: locus.loop.nodes.ExecuteNode
::: locus.loop.nodes.ReflectNode

## Router

::: locus.loop.router.Router
::: locus.loop.router.ConditionalRouter
::: locus.loop.router.NodeType
::: locus.loop.router.RouteDecision

## Runner

::: locus.loop.runner.LoopRunner
::: locus.loop.runner.BatchRunner
::: locus.loop.runner.StreamingCollector
::: locus.loop.runner.create_runner
