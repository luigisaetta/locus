# Investigate an incident with SecurityContext

The point of `SecurityContext` is that you reason in *domains*, not vendors.
None of the calls the investigation below makes names a vendor: they name
logs, identity, threat intel, endpoint and actions. Swap a live vendor in by
injecting a provider for one domain (`SecurityContext(logs=MyLogs())`); the
investigation code does not change.

The notebook walks a suspected account compromise through four evidence
domains — search the logs, score the user's risk, enrich an indicator, retrieve
the host timeline — then proposes containment and asks the policy gate for a
decision instead of running it. One investigation, four evidence ports and the
actions gate, and no vendor name in any call it makes.

What this notebook covers:

- How `SecurityContext()` with no arguments gives one handle over the security
  domains, each port filled by a bundled default until a provider is injected
  for that domain.
- Reading four evidence ports in sequence: `logs.search`, `identity.risk`,
  `threat_intel.enrich` and `endpoint.get_host`.
- Proposing a containment `Action` and asking `ctx.actions.request_approval`
  for a `ControlPolicy` decision rather than running the side effect.
- Why the default policy answers `require_human` for an action on a production
  asset even when the verification confidence clears its bar.

The drawing below shows the handle this investigation holds: one
`SecurityContext` with a port per security domain, each filled by the bundled
default until a provider is injected for that domain, and `ctx.actions` as the
admission gate on `ControlPolicy`. The account-compromise walk reads four of
the five domain ports (`ctx.logs`, `ctx.identity`, `ctx.threat_intel`,
`ctx.endpoint`), leaves `ctx.cloud` untouched, and asks `ctx.actions` for a
decision with `request_approval` rather than running a side effect through
`execute`, so the trail ends at the policy's verdict and nothing fires:

{{ locus_diagram security-context }}

## Key lines

The example keeps the whole investigation in `main`: it constructs
`SecurityContext()` with no arguments, reads the four evidence ports in sequence
(`logs.search` over a six-hour window, `identity.risk` for the suspect user,
`threat_intel.enrich` for the observed address and `endpoint.get_host` for the
workstation), then builds a high-confidence `VerificationResult` to stand in for
a verified finding and passes it, with an `Action` named `disable_user` on a
production asset, to `ctx.actions.request_approval`, printing the decision's
outcome and reason. The confidence of 0.93 clears the default policy's
verification bar of 0.8, but the default `ControlPolicy` holds any action
carrying the `production` label for human approval, so the outcome is
`require_human`:

{{ locus_source packages/locus-sdk-security/examples/notebook_89_investigate_with_ctx.py::main }}

## Run it

```bash
python packages/locus-sdk-security/examples/notebook_89_investigate_with_ctx.py
```

The script needs no model and no model provider. `SecurityContext()` with no
arguments fills the logs, identity, threat-intel and endpoint ports with the
bundled reference adapters and gates the action with a default
`ControlPolicy`; the cloud port, which this investigation never reads, defaults
to the bundled read-only Oracle Cloud Infrastructure (OCI) provider. The
reference adapters answer from deterministic offline samples, except that the
logs, threat-intel and endpoint adapters query a live backend when the
environment carries its credentials (`SIEM_URL` with `SIEM_TOKEN`,
`VT_API_KEY`, `EDR_URL` with `EDR_TOKEN`); with none of those set, the run
makes no network call. Inject a provider for one domain, such as
`SecurityContext(logs=...)`, and the same investigation runs against that
service.

## Output

Running it offline — no model and no credentials — prints the five-step investigation trail: each domain port's answer from the reference providers (a high-risk user with impossible travel, a malicious indicator) and the policy verdict on `disable_user` in production, REQUIRE_HUMAN with its reason:

```text
Investigating a suspected account compromise (vendor-agnostic)

1. logs.search -> 0 event(s) from offline-sample
2. identity.risk -> high (impossible_travel=True)
3. threat_intel.enrich -> malicious
4. endpoint.get_host -> timeline from offline-sample
5. actions.request_approval -> REQUIRE_HUMAN: labels ['production'] require human approval

One investigation, five domains, zero vendor names. The same code runs against real Splunk / Okta / CrowdStrike once you inject those providers.
```
<!-- notebook-output:end -->

## See also

- [SecurityContext](../concepts/security-context.md) — the domain ports, and going
  live by injecting a provider
- [Admission control](../concepts/security-context.md#admission-control-the-enforcement-point)
  — `ctx.actions.execute()` and `admit()`, where a decision becomes binding
- [Control API](../api/control.md) — `ControlPolicy` and `Action`
- [How-to: build an integration](../how-to/build-an-integration.md) — writing a
  vendor adapter that keeps an offline path

## Source

??? note "Full source — `packages/locus-sdk-security/examples/notebook_89_investigate_with_ctx.py`"

    ````python
    --8<-- "examples/notebook_89_investigate_with_ctx.py"
    ````
