# SOC playbooks over the security toolset

`locus_security` (the separate `locus-sdk-security` package, installed from
the repository) ships four curated incident-response (IR) and security
operations centre (SOC) playbooks — `phishing_triage`, `nist_800_61_ir`,
`ransomware_containment` and `cloud_posture_audit` — together with
`security_toolset()`, which assembles the agent-ready security adapters:
indicator-of-compromise (IOC) enrichment, security information and event
management (SIEM) search, endpoint detection and response (EDR) forensics,
vulnerability and posture scanning, and inference fingerprinting. Every tool
the phishing-triage steps name in `expected_tools` comes from it
(`isolate_host` only with `allow_containment=True`). The enforcement itself is
core SDK: `PlaybookEnforcer` is imported from `locus.playbooks`,
`PlaybookEnforcerHook` from `locus.playbooks.hook`, and `Agent(playbook=...)`
installs the hook.

A playbook takes an investigation through its steps in order. The bundled
security playbooks are lenient — each sets `allow_extra_tools=True` — so the
enforcer records which step every tool call belonged to and advances a step
once all of its expected tools have been called, but it does not cancel a tool
the current step did not list (the one block that remains is a step's
`max_tool_calls` ceiling, which none of the bundled steps set). The strict
mode that does cancel is the default for playbooks you write yourself and is
described on
[the playbooks concept page](../concepts/playbooks.md#strict-vs-lenient-enforcement).
What this notebook prints is the gate itself, driven by hand: each expected
tool validated and recorded in turn, then the progress and the violations read
back from the enforcer.

What this notebook covers:

- the four bundled playbooks from `all_playbooks()`, printed with their steps
  in order
- an `Agent` built with `security_toolset(allow_containment=True)` and
  `playbook=phishing_triage()`, which installs the `PlaybookEnforcerHook` and
  runs a triage request through it
- the same `PlaybookEnforcer` walked by hand with no model in the loop:
  `validate_tool_call`, `record_tool_call` and `complete_current_step` for
  each step, then `progress` and `violations` read back

## Prerequisites

- The `locus-sdk-security` package. It is not part of `locus-sdk` and is not
  on PyPI; the [Security API page](../api/security.md) has the `pip install`
  command that installs it from the repository. `Agent`, `PlaybookEnforcer`
  and `PlaybookEnforcerHook` come from the core package.
- [Notebook 49 — Playbooks](notebook_49_playbooks.md), which introduces
  `Playbook`, `PlaybookStep` and the enforcer on a core example.

The drawing below is the hook point the agent run relies on. The
`PlaybookEnforcerHook` that `Agent(playbook=...)` installs sits on
`on_before_tool_call`, where it asks the enforcer to validate each tool the
model proposes against the playbook's current step, and on
`on_after_tool_call`, where it records the call that ran in that step's
`StepExecution` and completes the step once every tool in its `expected_tools`
has been seen, so a model that follows the steps moves through `gather`,
`enrich`, `scope` and `contain` in order. The drawing labels the steps with
the refund playbook from the concept page and shows both verdicts. Its denied
branch — the call cancelled before its body runs, the model reading the
`PlaybookEnforcer blocked:` message with the step's hints as the tool's
result — is the strict mode; the lenient bundled playbooks on this page, which
set no `max_tool_calls`, never reach it, and an out-of-step call takes the
allowed branch and is recorded against the current step:

{{ locus_diagram playbook-enforcement }}

## Key lines

`main` is the whole example, and two places carry the point. The `Agent` call
wires `tools=security_toolset(allow_containment=True)` — the eight adapter
tools, the read-only triage set plus the opt-in `isolate_host` containment
write — and `playbook=playbook`, which installs the enforcer hook for the
`arun` that follows. On the bundled mock model that run makes a single tool
call, and it is not `gather`'s `query_siem`, so the playbook stays on its first
step; the final loop therefore drives a fresh
`PlaybookEnforcer.from_playbook(playbook, block_violations=True)` by hand:
`validate_tool_call` for each tool a step expects, `record_tool_call` when the
verdict allows it, `complete_current_step` to advance, then `progress` and
`violations` read back. `contain` is declared `required=False`, a flag the hook
never acts on (only `skip_current_step` and
`PlaybookPlan.unresolved_required_steps` read it), so the walk completes it
like the others:

{{ locus_source packages/locus-sdk-security/examples/notebook_82_security_playbooks.py::main }}

## Run it

```bash
python packages/locus-sdk-security/examples/notebook_82_security_playbooks.py
```

Model choice comes from `packages/locus-sdk-security/examples/config.py`, the
security package's own notebook helper: with `LOCUS_MODEL_PROVIDER` unset it
returns the bundled mock model, so the script runs offline with no credentials
and no network. Set `LOCUS_MODEL_PROVIDER` to `openai` or `anthropic`, with the
matching `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, to run the agent step on a
live model; this helper offers `mock`, `openai` and `anthropic` only and does
not pick up an OCI profile from `~/.oci/config`.

## Output

Running it offline — no credentials, bundled mock model — prints the four bundled playbooks with their step order, the mock model's one-line triage verdict from the enforced agent run, then the `PlaybookEnforcer` step gate for phishing triage: each expected tool allowed in turn, progress 100% and no violations:

```text
== Bundled security playbooks ==
  phishing_triage          gather -> enrich -> scope -> contain
  nist_800_61_ir           detect -> analyze -> contain -> recover -> report
  ransomware_containment   confirm -> contain -> assess_scope -> preserve
  cloud_posture_audit      discover -> gather -> report

== Running 'Phishing triage' with 8 security tools (mock model) ==
  agent result (truncated): Escalate: the indicators line up with an active phishing campaign.

== PlaybookEnforcer step gate ==
  [gather] query_siem           -> ok
  [enrich] enrich_indicator     -> ok
  [scope] fetch_host_timeline  -> ok
  [scope] list_detections      -> ok
  [contain] isolate_host         -> ok
  progress: 100%  violations: 0
```
<!-- notebook-output:end -->

## See also

- [Concepts: Playbooks](../concepts/playbooks.md) — strict versus lenient
  enforcement, evidence probes and inspecting execution
- [Notebook 49 — Playbooks](notebook_49_playbooks.md) — the enforcer on a core
  example, with execution tracking
- [Notebook 87 — SOC alert triage](notebook_87_soc_alert_triage.md) —
  `ground_report`, which grounds the verdicts a SOC analyst agent files on
  SIEM alerts

## Source

??? note "Full source — `packages/locus-sdk-security/examples/notebook_82_security_playbooks.py`"

    ````python
    --8<-- "examples/notebook_82_security_playbooks.py"
    ````
