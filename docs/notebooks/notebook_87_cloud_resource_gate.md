# A cloud-ops agent that can only touch production with a human's say-so

A cloud-ops agent is handy and dangerous in the same breath. It can free up a
forgotten dev box in seconds — and it can just as easily terminate the database
the whole product runs on, or hand an outside principal admin over your account.
The model deciding *what* to do is not the place to enforce *whether* it is
allowed to. That belongs in code that runs before the API call.

This example puts ``admit`` in front of every cloud mutation. The agent proposes
an ``Action``; the gate weighs it against a ``ControlPolicy`` you wrote; the
actual cloud call (here a local stub — no network, no credentials) fires *only*
if the policy admits it. Small, contained changes proceed on their own. Anything
that touches a production resource, or reaches across many resources at once, is
held for a human. Either way the decision lands on a tamper-evident
``AuditTrail``, so there is no un-recorded path to a side effect.

    Agent proposes a cloud action
       │
       ▼
    admit(action, perform, policy, trail)
       │
       ├─ blast radius small AND not production ──> perform() runs (resize dev box)
       │
       └─ production OR wide blast radius ────────> AdmissionError, held for a human
                                                    (terminate prod DB, open IAM)
       │
       ▼
    AuditTrail records every attempt — admitted or not

The policy gates on two attributes of the action. ``max_blast_radius`` caps how
many resources one action may touch and still auto-proceed: resizing a single
dev instance is blast radius 1; deleting an auto-scaling group of 12 nodes is
blast radius 12. ``require_human_for`` lists labels that always need a person —
``production`` and ``iam`` here, but you can add a specific tag, ``billing``, or
anything else. ``require_verification_score`` is set to ``0.0`` because a cloud
mutation is an ops action, not a security finding: there is no verdict to weigh,
so the gate reasons purely over blast radius and the labels on the action.

``admit()`` is the single enforcement point. It asks the policy, records the
decision to the ``AuditTrail`` whether or not it allows, and only then awaits
``perform``. The script runs two attempts through it. The first resizes a
staging CI runner — blast radius 1, not production — so the gate lets it through
and the in-memory inventory shows the new instance size. The second tries to
terminate the production primary database; the ``production`` label trips the
gate, the terminate call never fires, and the row is left exactly as it was. A
model that is jailbroken, prompt-injected, or just wrong still cannot push that
production change past the gate.

Both attempts land on the trail next to each other — the resize that ran and the
terminate that was held — and ``trail.verify()`` confirms the SHA-256 chain is
intact, so the record is tamper-evident. ``perform`` is a local stub: each
side-effect function mutates an in-memory ``INVENTORY`` / ``IAM`` dict instead of
calling boto3, the Azure SDK, or ``gcloud``, so the script runs offline with no
cloud account, no creds, no network. Swap those functions for real API calls and
the gate is unchanged.

Run it (fully offline — no model, no cloud account, no credentials needed):
    python examples/notebook_87_cloud_resource_gate.py

## Output

Running it offline — no model and no credentials — prints a staging resize allowed and a production terminate held:

```text
Notebook 87: gating a cloud-ops agent's actions by blast radius and environment
============================================================

--- agent proposes: resize_instance ---
    asset='i-dev-7a3'  env='staging'  blast_radius=1
  ✅ ADMITTED — the cloud call ran: resized i-dev-7a3 -> t3.medium

--- agent proposes: terminate_instance ---
    asset='i-prod-db1'  env='production'  blast_radius=1
  ⏸  HELD FOR A HUMAN — outcome=require_human
     why: labels ['production'] require human approval
     the cloud call did NOT run; the resource is untouched.

Cloud account after both attempts:
------------------------------------------------------------
  i-dev-7a3     env=staging     state=running     size=t3.medium
  i-prod-db1    env=production  state=running     size=r6i.4xlarge

Audit trail:
------------------------------------------------------------
  #0  resize_instance       -> allow           (i-dev-7a3)
  #1  terminate_instance    -> require_human   (i-prod-db1)
  chain intact (tamper-evident): True

All assertions passed: low-risk action ran, production change held, both audited.
```
<!-- notebook-output:end -->

## Source

````python
--8<-- "examples/notebook_87_cloud_resource_gate.py"
````
