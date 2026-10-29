# Infra deploy gate

An operations agent watches continuous integration (CI). When a build goes
green it proposes the next move: roll the new image onto staging, promote it to
production, or roll production back. Left to act on its own, the agent can take
the checkout API down overnight with nobody watching; requiring a human for
every change stops releases altogether. The middle path is a gate: cheap,
reversible staging changes go through automatically, and any change to the
production environment stops and waits for a human.

The decision of *whether the rollout runs* does not live in the agent's prompt.
It lives in `admit()`, a gate that runs before `kubectl` (the Kubernetes
command-line tool) touches the cluster, and the rule it enforces is written
once, in a `ControlPolicy`: any action carrying the `production` label waits
for a person, however small its blast radius; staging clears on blast radius
alone; and the verification bar is switched off, because a deploy is an
operations action with no security verdict to weigh. The agent can be confused,
manipulated by a prompt injection, or wrong about the blast radius it declares;
a production change still waits for a human, and nothing runs that `admit()`
has not cleared.

`admit()` is the single enforcement point. It asks the policy through
`approve()`, records the decision on the `AuditTrail` whether or not it allows
the action, and only then awaits `perform`; a hold surfaces as an
`AdmissionError` that carries the decision, and a later `admit()` call with
`approved_by=` runs the held action and records the approver on the trail. The
rollout itself is a local stub that appends to an in-memory list instead of
calling `kubectl`, so the script runs offline with no cluster, no credentials
and no network; swap that one function for a real `kubectl rollout` call and
the gate is unchanged.

What this notebook covers:

- Describing each proposal as an `Action` with an `environment`, a `kind`, tags
  and a declared `blast_radius`.
- Writing the deploy rule once, in a `ControlPolicy` with `max_blast_radius=4`,
  `require_human_for={"production"}` and `require_verification_score=0.0`.
- Passing the side effect to `admit()` as a zero-argument async callable that
  runs only on an allow.
- Handling a hold as an `AdmissionError` whose `decision` carries the outcome
  and the reason.
- Reading both decisions back from the hash-chained `AuditTrail` and checking
  that the chain is internally consistent with `trail.verify()`.

The drawing below follows both proposals through the gate: `admit()` hands each
`Action` to `approve()` with the policy, the staging deploy clears on blast
radius alone and `perform()` runs the rollout, the production rollback is held
under `require_human_for` even though its blast radius is smaller, and both
decisions are recorded on the hash-chained `AuditTrail` before anything runs.

{{ locus_diagram gate-infra-deploy }}

## Key lines

The side effect is built as a zero-argument async callable that `admit()` runs
only on an allow; here it appends to an in-memory list where the real version
would call `kubectl`:

{{ locus_source examples/notebook_72_infra_deploy_gate.py::make_rollout }}

Each proposed action goes through `admit()` with the module-level `POLICY` and
the trail: an allowed action returns what `perform` produced, a held one raises
`AdmissionError` carrying the decision and its reason, and nothing is applied:

{{ locus_source examples/notebook_72_infra_deploy_gate.py::propose }}

## Run it

```bash
python examples/notebook_72_infra_deploy_gate.py
```

No model is involved: the agent's two proposals are `Action` values built in
`main()` and the rollout is an in-memory stub, so the example runs offline with
no provider configuration and no credentials. `examples/config.py` and
`LOCUS_MODEL_PROVIDER` play no part in this notebook.

## Output

Running it offline — no model and no credentials — prints a staging deploy allowed and a production rollback held:

```text
Notebook 72: An ops agent that ships to staging on its own and waits for a human in production
============================================================

--- deploy checkout-api in staging (blast radius 3) ---
  ALLOWED — the agent acted on its own authority.
  Applied: deploy checkout-api -> checkout-api:1.8.2 (staging)

--- rollback checkout-api in production (blast radius 2) ---
  HELD (require_human) — nothing was applied.
  Reason: labels ['production'] require human approval
  Next: route to the on-call human for sign-off.

Audit trail
------------------------------------------------------------
  action-admission: deploy checkout-api -> allow
  action-admission: rollback checkout-api -> require_human
  chain intact: True

Side effects applied: ['deploy checkout-api -> checkout-api:1.8.2 (staging)']

OK — staging shipped, production held, both on the trail.
```
<!-- notebook-output:end -->

## See also

- [Control-layer architecture](../concepts/control-layer.md) — where `admit()`
  sits among the agent loop, approvals, persistence and audit.
- [Admitting an action](../api/control.md#admitting-an-action) — the `admit()`
  and `AdmissionError` reference, including `approved_by`.
- [What `verify()` catches](../api/control.md#what-verify-catches-and-the-one-thing-it-cannot)
  — a bare `trail.verify()` catches edits, reorders and deletions from the
  middle of the chain, not a truncation.

## Source

??? note "Full source — `examples/notebook_72_infra_deploy_gate.py`"

    ````python
    --8<-- "examples/notebook_72_infra_deploy_gate.py"
    ````
