# Termination

Composable stop conditions — combine with `|` (OR) and `&` (AND):

```python
from locus.core.termination import MaxIterations, ToolCalled, ConfidenceMet

termination = (
    ToolCalled("submit") & ConfidenceMet(0.9)
) | MaxIterations(15)
```

For the concepts, start with [Termination](../concepts/termination.md).

## Base

::: locus.core.termination.TerminationCondition

## Conditions

::: locus.core.termination.MaxIterations
::: locus.core.termination.TokenLimit
::: locus.core.termination.TextMention
::: locus.core.termination.TimeLimit
::: locus.core.termination.ToolCalled
::: locus.core.termination.ConfidenceMet
::: locus.core.termination.NoToolCalls
::: locus.core.termination.CustomCondition

## Composition operators

::: locus.core.termination.OrCondition
::: locus.core.termination.AndCondition
