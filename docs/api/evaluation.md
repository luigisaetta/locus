# Evaluation

Test harness for agents — define `EvalCase`s, run them with `EvalRunner`, and
collect results into an `EvalReport`.

For the concepts, start with [Evaluation](../concepts/evaluation.md) and
[Testing agents](../concepts/testing.md).

::: locus.evaluation.framework.EvalCase
::: locus.evaluation.framework.EvalResult
::: locus.evaluation.framework.EvalReport
::: locus.evaluation.framework.EvalRunner

## Grading an answer that has no single right string

Structural checks verify shape, not quality. `expected_output_contains`
in particular fails in both directions: it passes on an answer that happens to
contain the word, and fails on a correct answer phrased differently. Where the
right answer is not one exact string, something has to read it.

`LLMJudge` grades against a written rubric and returns a typed `Verdict`. Two
things it deliberately does not do:

- **It does not retry until it passes.** A judge you re-roll is not a judge.
- **It does not score zero when it cannot be reached.** An unusable judge
  raises, because a "failing" eval that actually means *the judge was down* is
  worse than no eval.

Use a different model from the one under test where you can — a model grading
its own output is measuring self-consistency, not correctness.

::: locus.evaluation.judge.LLMJudge
::: locus.evaluation.judge.Verdict

## Asserting the order, not just the membership

`expected_tools` asks whether a tool appeared *somewhere* in the run. It cannot
tell "looked the order up, then refunded it" from "refunded it, then looked it
up" — and for an agent that acts, that ordering is most of what correctness
means.

::: locus.evaluation.judge.check_trajectory

## Running a suite against a graph

`EvalRunner` expects an agent: it calls `run_sync(prompt)` and reads `.message`,
`.iterations` and `.tool_executions`. A `StateGraph` takes a dict and returns a
`GraphResult` with none of those. `as_eval_target` adapts one to the other.

It has to make two translations a graph cannot make for itself:

- **A prompt is not a state.** `input_key` says which field of the graph's
  initial state the case prompt becomes. There is no universally right default,
  so `"prompt"` is a starting guess to correct.
- **Nodes are the graph's tools.** `expected_tools` and
  `expected_tool_sequence` match on **node ids**, which makes "a change sent
  this down the wrong branch" — the regression a graph suite exists to catch —
  an ordinary assertion.

Addressing the answer takes two arguments rather than one, because
`final_outputs` is keyed by node id while a graph's result accumulates in
`final_state`: `output_key` reads the state, `output_node` reads one node's own
output, and passing both raises rather than silently preferring one.

::: locus.evaluation.graph.as_eval_target
::: locus.evaluation.graph.GraphEvalTarget
