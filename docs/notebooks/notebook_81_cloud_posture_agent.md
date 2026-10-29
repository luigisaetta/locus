# Grounded OCI cloud-posture agent

A security operations centre (SOC) analyst-shaped agent that audits an OCI
tenancy read-only, then *grounds* every finding it proposes against the API
facts it actually observed. `create_soc_analyst` composes the two core
spec-driven, read-only OCI tools — `describe_oci` (discover the shape of the
OCI control plane from the installed OCI Python SDK: services, clients,
operations, parameters) and `use_oci` (run one read-only operation, return the
response as evidence) — behind a `create_deepagent` core. The agent proposes
findings; `ground_report` decides which survive: a proposed finding becomes a
typed `Evidence` only if its cited evidence clears the
[GSAR (typed grounding)](../concepts/gsar.md) threshold, otherwise it
abstains. The model gathers and proposes; Python decides what ships.

An agent without grounding can narrate misconfigurations it never observed.
Here, a finding survives only if the analyst cited direct API observations for
it; inferences alone abstain (`ground_report`). The control is on the *shape*
of the evidence, not its truth — the agent marks each cited fact as
observation or inference (the `grounded` flag, which defaults to observation),
and the `ref` string is carried for audit, not parsed — so pair this with the
raw `use_oci` responses when you need the citation itself checked.

The finding class maps to
[OWASP ASI03, Identity & Privilege Abuse](../concepts/threat-scenarios.md#owasp-asi-top-10-agentic-2026)
(the API-key-on-an-administrator finding); the read-only-by-default tooling
is the control that keeps the auditor itself from becoming a liability.

What this notebook covers:

- Building the `PostureReport` the analyst submits: `PostureFinding` entries
  whose `PostureEvidence` marks each cited fact as a direct API observation
  or an inference.
- The grounding decision offline: `SecurityControls(min_gsar=0.6)`,
  `ground_report` and `is_finding`, with a typed `Evidence` for each finding
  that ships and an `Abstention` for each that does not.
- The live analyst: `create_soc_analyst` over `describe_oci`, `use_oci` and
  `submit_posture`, pinned to one profile and tenancy, and the same
  `ground_report` pass over the report in `result.parsed`.

## Prerequisites

- The [DeepAgent](notebook_31_deepagent.md) notebook — the core this factory
  wraps.
- For the live Part 2 only: a structured-output-capable provider and the
  `oci` SDK (`pip install 'locus-sdk[oci]'`) with a profile whose Identity and
  Access Management (IAM) group grants only inspect / read verbs. The agent is
  read-only by default: before any call is made, `use_oci` refuses an
  operation whose name does not start with a read-only prefix (`list_`,
  `get_`, `head_`, `summarize_`, …) unless its `allow_mutations` opt-in or
  `LOCUS_USE_OCI_ALLOW_MUTATIONS=1` is set. The factory sets neither, but
  `allow_mutations` remains a parameter of the tool the model is offered, so
  the read-only IAM group is the hard backstop.

The drawing follows one IAM review through both halves of the notebook:
during the run the analyst reaches the OCI APIs only through `use_oci`, which
sends a read such as `list_users` or `list_api_keys` under the audit profile
(pointed at a read-only IAM group as the hard backstop) and returns the
response as evidence, while a write is refused before any call is made and
the refusal goes back to the analyst as an error; the run ends with a
submitted `PostureReport`, and after it `ground_report` scores each proposed
finding with GSAR, so a finding whose score reaches `min_gsar` ships as a
typed `Evidence` and one below it abstains and is kept for audit — direct API
observations count as grounded evidence, and an inference alone cannot ship a
finding.

{{ locus_diagram cloud-posture }}

## Key lines

`_sample_report` builds the `PostureReport` exactly as the agent would submit
it: three `PostureFinding` entries with their `PostureEvidence`, the first two
citing facts read from `list_api_keys` and `list_users` (`grounded=True`, the
`ref` kept for audit) and the third resting on an inference with no call
behind it (`grounded=False`):

{{ locus_source packages/locus-sdk-security/examples/notebook_81_cloud_posture_agent.py::_sample_report }}

`part1_grounding_offline` is the grounding decision with no model involved:
`SecurityControls(min_gsar=0.6)` sets the threshold, `ground_report` scores
each proposed finding, and `is_finding` separates the typed findings, which
carry `gsar_score` and `evidence_refs`, from the abstentions, which carry the
reason:

{{ locus_source packages/locus-sdk-security/examples/notebook_81_cloud_posture_agent.py::part1_grounding_offline }}

`part2_live_agent` builds the analyst with `create_soc_analyst` from the
model, the `SecurityControls` that `_oci_target` pins to the configured
profile and its tenancy, and an iteration cap, lists its tools
(`describe_oci`, `use_oci` and `submit_posture`), returns with the
bring-your-own-credentials notice when the model is the bundled mock or no
profile is usable, and otherwise runs the IAM review with `arun`, reads the
submitted `PostureReport` from `result.parsed` and passes it through the same
`ground_report` decision:

{{ locus_source packages/locus-sdk-security/examples/notebook_81_cloud_posture_agent.py::part2_live_agent }}

## Run it

```bash
python packages/locus-sdk-security/examples/notebook_81_cloud_posture_agent.py
```

Part 1 needs nothing beyond the package: it hand-builds the report and runs
`ground_report` without a model or a tenancy, so it is deterministic offline.
Part 2 takes its model from the security package's own harness,
`packages/locus-sdk-security/examples/config.py`, which reads
`LOCUS_MODEL_PROVIDER` (`openai` or `anthropic`, with the matching API key)
and otherwise returns the bundled mock model; this harness has no OCI
Generative AI branch, so an OCI profile alone does not select a live model.
The live audit also needs the `oci` SDK and a usable `~/.oci/config` profile,
named by `LOCUS_OCI_PROFILE` or `OCI_PROFILE` (`DEFAULT` otherwise) with
`LOCUS_OCI_AUTH_TYPE` or `OCI_AUTH_TYPE` selecting the auth type (`api_key`
otherwise); the profile selects the tenancy the `SecurityControls` are pinned
to, not the model. Both are required: without a live provider or without a
usable profile, Part 2 still builds the analyst and lists its tools, then
prints the bring-your-own-credentials notice and returns.

## Output

Running it offline — no credentials, bundled mock model — prints the grounding decision trail: two findings shipped with their GSAR score and evidence refs, the speculative one abstaining with its reason, then the analyst's read-only tool list before the bring-your-own-credentials skip notice:

```text

--- Part 1: the grounding decision (offline, deterministic) ---
agent proposed 3 finding(s); grounding each:

  SHIP    [critical] Tenancy administrator has a long-lived API key
          gsar=1.00  evidence=['oci:identity:list_api_keys:timeCreated']
  SHIP    [info    ] MFA is active for every console user
          gsar=1.00  evidence=['oci:identity:list_users:isMfaActivated']
  ABSTAIN  withheld (replan): grounding below the proceed threshold (1 ungrounded of 1 claims)

2/3 proposed findings cleared grounding and shipped.
The speculative finding abstained — it cited no observation. That is the moat.

--- Part 2: the live cloud-posture agent ---
analyst tools: ['describe_oci', 'submit_posture', 'use_oci']
read-only by default: use_oci refuses any operation that is not a list/get-style read.

Live run skipped (bring-your-own-credentials).
  Configure an OCI profile (or set LOCUS_MODEL_PROVIDER to a live provider)
  and point LOCUS_OCI_PROFILE / OCI_PROFILE at a read-only profile to audit
  a real tenancy. Offline, Part 1 already showed the grounding decision
  that gates the report.
```
<!-- notebook-output:end -->

## See also

- [Cloud-posture agent](../concepts/cloud-posture.md) — the two spec-driven
  tools, the factory,
  [the grounding split](../concepts/cloud-posture.md#the-grounding-split) and
  the [credentials](../concepts/cloud-posture.md#credentials) the calls run as.
- [GSAR (typed grounding)](../concepts/gsar.md) — the score and the decision
  behind `ground_report`.
- [OCI tools](notebook_36_oci_tools.md) — `describe_oci` and `use_oci` on
  their own, outside the security package.

## Source

??? note "Full source — `packages/locus-sdk-security/examples/notebook_81_cloud_posture_agent.py`"

    ````python
    --8<-- "examples/notebook_81_cloud_posture_agent.py"
    ````
