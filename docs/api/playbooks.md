# Playbooks

Structured execution plans for agents — declared step sequences with
expected tools, validation criteria, and guidance hints. Attach one
via `AgentConfig.playbook`; enforcement details below.

For the concepts, start with [Playbooks](../concepts/playbooks.md).

## Models

::: locus.playbooks.models.Playbook
::: locus.playbooks.models.PlaybookStep
::: locus.playbooks.models.PlaybookPlan
::: locus.playbooks.models.StepExecution
::: locus.playbooks.models.StepStatus

## Loader

::: locus.playbooks.loader.load_playbook
::: locus.playbooks.loader.PlaybookLoader
::: locus.playbooks.loader.PlaybookLoadError

## Enforcer

`PlaybookEnforcer` is the enforcement engine that holds the model to
the playbook's step sequence. `PlaybookEnforcerHook` is the
`HookProvider` wrapper around it, installed automatically when
`AgentConfig.playbook` is set.

::: locus.playbooks.enforcer.PlaybookEnforcer
::: locus.playbooks.enforcer.EnforcementResult
::: locus.playbooks.enforcer.EnforcementViolation
::: locus.playbooks.hook.PlaybookEnforcerHook
