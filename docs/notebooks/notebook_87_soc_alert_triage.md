# SOC alert triage with SIEM-grounded verdicts

A security operations centre (SOC) analyst agent files a verdict on every
alert its security information and event management (SIEM) platform raises.
In this notebook every verdict proposed for an alert goes through
`ground_report`: a proposed finding is filed as an `Evidence` only if the
evidence cited for it clears the [GSAR](../concepts/gsar.md) proceed
threshold of the shared `SecurityControls` (`min_gsar`, 0.6 by default). A
proposed finding whose evidence falls short comes back as an `Abstention`:
nothing is filed, and the abstention is kept with its reason so an analyst
can review the alert.

The benign case shows the point of the split. When the agent sees noise and
correctly finds no corroborating evidence, an `Abstention` is the right
output, because a finding without evidence is not filed. The example triages
four SIEM alerts — a phishing click, PsExec lateral movement, a beacon to a
known command-and-control (C2) address, and benign process noise — and
prints three grounded `Evidence` results and one `Abstention`.

The example runs fully offline: a mock builder stands in for the SOC analyst
agent and derives each proposed finding from corroboration flags on the
alert. Swap it for `security_toolset(siem=True, edr=True, threat_intel=True)`,
`create_soc_analyst` and a real model to run against a live environment.

What this notebook covers:

- a `PostureEvidence` marked `grounded=True` for every SIEM, endpoint
  detection and response (EDR) or threat-intelligence corroboration, and a
  single ungrounded statement when nothing corroborates the alert
- `ground_report` over a `PostureReport` of proposed findings, with the
  proceed threshold taken from one shared `SecurityControls`
- `is_finding` splitting the `Evidence` results, which carry a GSAR score and
  evidence references, from the `Abstention` that records why a verdict was
  withheld

`ground_report` runs each proposed finding through `ground_finding`, the
decision below. Only the claims are scored: every corroboration the agent
cited counts for the finding and a statement it could not ground counts
against it, while the title, severity and asset are carried but never scored.
The three corroborated alerts clear the proceed threshold and ship as
`Evidence` with a score and evidence references; the benign-noise alert falls
below it and comes back as an `Abstention` that records why:

{{ locus_diagram grounded-findings }}

## Key lines

Each proposed finding is built from the alert's corroboration flags. Every
SIEM, EDR or threat-intelligence corroboration becomes a `PostureEvidence`
marked `grounded=True`; an alert with none gets a single statement the agent
cannot mark grounded, which is the row that should abstain. The docstring
names the SOC analyst agent call that takes this builder's place in
production:

{{ locus_source packages/locus-sdk-security/examples/notebook_87_soc_alert_triage.py::_build_mock_evidence }}

The triage loop wraps each alert's proposed findings in a `PostureReport` and
hands it to `ground_report` with the shared `SecurityControls`; `is_finding`
then separates the `Evidence` results, which carry a GSAR score and evidence
references, from the `Abstention`, which keeps the candidate title, the reason
it was withheld and the score that fell short:

{{ locus_source packages/locus-sdk-security/examples/notebook_87_soc_alert_triage.py::triage_alerts }}

## Run it

```bash
python packages/locus-sdk-security/examples/notebook_87_soc_alert_triage.py
```

The script is fully offline: no model, no provider, no network. It reads no
environment variable either, so `LOCUS_MODEL_PROVIDER` has no effect; the
proposed findings come from `_build_mock_evidence`.

## Output

Running it offline — no model and no credentials — prints one verdict per alert: the three corroborated alerts filed as findings with their severity, GSAR score and evidence references, the benign-noise alert withheld as an abstention with the reason and the score that fell short, then the count of findings filed and abstentions:

```text

────────────────────────────────────────────────────────────
Alert ALT-001: Phishing link clicked by user jsmith
  [FINDING ] HIGH     Phishing link clicked by user jsmith
             grounded @ 1.00
             evidence : ['siem:ALT-001:related_events']
             taxonomy : —

────────────────────────────────────────────────────────────
Alert ALT-002: PsExec lateral movement from WKSTN-04 to SRV-FINANCE
  [FINDING ] CRITICAL PsExec lateral movement from WKSTN-04 to SRV-FINANCE
             grounded @ 1.00
             evidence : ['siem:ALT-002:related_events', 'edr:WKSTN-04:process_tree']
             taxonomy : —

────────────────────────────────────────────────────────────
Alert ALT-003: Outbound connection to known C2 IP 203.0.113.99
  [FINDING ] HIGH     Outbound connection to known C2 IP 203.0.113.99
             grounded @ 1.00
             evidence : ['siem:ALT-003:related_events', 'intel:203.0.113.99:malicious']
             taxonomy : —

────────────────────────────────────────────────────────────
Alert ALT-004: Unusual process: msiexec.exe spawned by Teams.exe
  [ABSTAIN ] Unusual process: msiexec.exe spawned by Teams.exe
             reason   : withheld (replan): grounding below the proceed threshold (1 ungrounded of 1 claims)
             gsar     : 0.00 (below threshold)

════════════════════════════════════════════════════════════
Triage complete: 3 findings filed, 1 abstentions.
The abstention(s) above are alerts a commodity AI SOC would have filed as findings.
Here they were withheld because no corroborating evidence was cited — reducing
analyst noise and false-positive rate.
```
<!-- notebook-output:end -->

## See also

- [GSAR — typed grounding](../concepts/gsar.md)
- [`ground_report`](../concepts/cloud-posture.md#the-grounding-split)
- [Agentic AI-security](../concepts/agentic-ai-security.md)

## Source

??? note "Full source — `packages/locus-sdk-security/examples/notebook_87_soc_alert_triage.py`"

    ````python
    --8<-- "examples/notebook_87_soc_alert_triage.py"
    ````
