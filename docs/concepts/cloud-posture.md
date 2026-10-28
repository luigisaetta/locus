# Cloud-posture agent — grounded, read-only OCI auditing

`create_soc_analyst()` builds a SOC-analyst-shaped agent that audits an OCI
tenancy **read-only** and grounds every finding it proposes against the API
facts it actually observed. It is the worked, end-to-end application of the
[security layer](security.md): the model gathers evidence and proposes
findings; [GSAR grounding](gsar.md) decides which ones ship.

A commodity "cloud agent" will confidently narrate misconfigurations it never
observed. Here an ungrounded claim *cannot* become a grounded `Evidence` finding — it abstains —
so the report is trustworthy by construction, and the agent is read-only by
default, so the auditor can't become the incident.

{{ locus_diagram cloud-posture }}

## Two spec-driven tools

Instead of one hand-written tool per OCI service, the agent gets the two
generic tools from the core SDK, driven by the **OCI Python SDK** itself —
about 190 service modules, each with its client classes and operations:

- **`describe_oci(service, client, operation)`** — introspect the SDK. No
  arguments lists every service (the *shape* of the control plane); a service
  lists its clients; a service + client lists that client's operations,
  read-only and mutating apart; a service + client + operation lists the
  operation's parameters. This is how the agent discovers what it can call.
- **`use_oci(service, client, operation, parameters)`** — execute one
  read-only operation and return the response, which becomes the **evidence**
  behind a grounded finding.

```python
from locus.tools import describe_oci, use_oci

describe_oci()                                            # every service module
describe_oci("identity")                                  # {"clients": ["IdentityClient"]}
describe_oci("identity", "IdentityClient")                # read-only vs mutating operations
describe_oci("identity", "IdentityClient", "list_users")  # that operation's parameters
use_oci(
    "identity", "IdentityClient", "list_users",
    parameters={"compartment_id": "ocid1.tenancy.oc1..xxx"},
    profile="security-audit",
)                                                         # → {"status": "ok", "data": [...]}
```

### Read-only by default

`use_oci` admits an operation only if its name starts with a read prefix
(`list_`, `get_`, `head_`, `summarize_`, `search_`, `describe_`, …) — and it
checks **before** any call is made. A mutating operation comes back as an
error result, not a call:

```python
use_oci("identity", "IdentityClient", "create_user", parameters={"name": "x"})
# {"status": "error", "error": "Operation 'create_user' looks mutating ... Refusing by default."}
```

The opt-in (`allow_mutations=True` or `LOCUS_USE_OCI_ALLOW_MUTATIONS=1`) exists
for other agents; the SOC analyst never sets it. The tool gate is
defense-in-depth; the **hard backstop is the IAM identity**. Run the agent as
a profile whose group policies grant only `inspect` and `read` verbs, and the
cloud itself refuses a write even if the gate were bypassed. Two independent
controls, neither trusting the model.

## The factory

`create_soc_analyst()` is a thin, security-shaped layer over
[`create_deepagent`](deepagent.md): it bakes in the OCI tools, a SOC-analyst
system prompt, a structured `PostureReport` output schema, and
reflexion + grounding.

```python
from locus_security import create_soc_analyst, SecurityControls

controls = SecurityControls(
    min_gsar=0.6,
    min_confidence=0.6,
    profile="security-audit",                     # ~/.oci/config profile the calls run as
    auth_type="security_token",                   # or api_key (the default)
    compartment_id="ocid1.tenancy.oc1..xxx",      # the tenancy or compartment under review
)
analyst = create_soc_analyst(
    model="{{ locus_example_model }}",
    controls=controls,
    scope="Focus on IAM: MFA for console users and API keys on administrators.",
)

result = analyst.run_sync(
    "Review the IAM posture. Start with identity IdentityClient list_users, "
    "cite the exact API facts as evidence, then submit your report."
)
report = result.parsed            # a PostureReport
```

`SecurityControls` is the one bundle the agent and the grounding step share —
the GSAR threshold a finding's evidence must clear, the submission-confidence
floor, whether the read-only OCI tools are attached, and the OCI identity and
scope they run as. `use_oci` takes `profile`, `auth_type`, `region` and
`compartment_id` as call arguments, so the factory appends the ones you set to
the system prompt for the model to pass on every call. You can add your own
tools (threat-intel, SIEM) alongside the OCI ones via `tools=[...]`.

## The grounding split

The agent submits a `PostureReport` of proposed `PostureFinding`s, each citing
its evidence. `ground_report()` runs each one through GSAR: a finding ships as
a typed `Evidence` only if its cited evidence clears the threshold, otherwise it
abstains.

```python
from locus_security import ground_report, is_finding

for grounded in ground_report(report, controls):
    if is_finding(grounded):
        print("SHIP   ", grounded.severity, grounded.title, grounded.gsar_score)
    else:
        print("ABSTAIN", grounded.reason)
```

Direct API observations become grounded claims; an analyst's *inference*
becomes an ungrounded claim, which cannot on its own admit a finding. So a
finding backed by `list_api_keys` ships, while a "there might be an over-broad
policy" with no call behind it abstains — even though the same model proposed
both.

Run live against a tenancy whose administrator holds an API key, the report
reads:

```text
SHIP    critical  Tenancy administrator has a long-lived API key   gsar=1.00
SHIP    info      MFA is active for every console user             gsar=1.00
ABSTAIN withheld (replan): grounding below the proceed threshold
```

## Credentials

The calls run as a `~/.oci/config` profile. `use_oci` defaults to the
`DEFAULT` profile with API-key auth; set `SecurityControls(profile=...,
auth_type=...)` to pick another — `security_token` for a session from
`oci session authenticate`, `instance_principal` / `resource_principal` when
the agent runs inside OCI. The notebook reads the profile from
`LOCUS_OCI_PROFILE` / `OCI_PROFILE`, the same variables the model harness uses:

```bash
export LOCUS_OCI_PROFILE=<your-profile>       # a group with inspect / read verbs only
export LOCUS_OCI_AUTH_TYPE=security_token     # or api_key
```

The `oci` SDK is an optional dependency of the core package — install the
extra:

```bash
pip install 'locus-sdk[oci]'
```

## Where it shows up

- Notebooks: [grounded cloud-posture agent](../notebooks/notebook_81_cloud_posture_agent.md)
  (Part 1 runs the grounding decision fully offline).
- [OCI tools](../notebooks/notebook_36_oci_tools.md) — `describe_oci` / `use_oci`
  on their own, outside the security package.
- [Security layer](security.md) — the `ground_finding` primitive this builds on.
- [Threat scenarios](threat-scenarios.md) — the catalogue the findings tag into
  (an administrator's API key maps to OWASP ASI03, *Identity & Privilege Abuse*).
- [DeepAgent](deepagent.md) — the agent core the factory wraps.
