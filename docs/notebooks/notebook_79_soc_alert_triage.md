# SOC alert triage with SIEM-grounded verdicts

A commodity AI SOC agent emits a verdict for every alert it sees, whether or not
it can back that verdict with evidence. Here, the SOC analyst grounds every
verdict through ``ground_report``: a proposed ``Evidence`` ships only if the
evidence the agent actually cited clears the GSAR threshold. When the agent
opines without evidence, the result is an ``Abstention`` — nothing is filed, and
the analyst knows to review it manually.

The false-positive case matters most. When the agent sees benign noise and
correctly finds no corroborating evidence, an ``Abstention`` is the right output:
don't file a finding you can't prove. Four SIEM alerts arrive in a one-hour
window — a phishing click, lateral movement, a C2 beacon, and benign process
noise — yielding three grounded ``Evidence`` results and one ``Abstention``.

Runs fully offline on mock SIEM / EDR / intel adapters. Swap them for
``security_toolset(siem=True, edr=True, threat_intel=True)`` and a real model to
run against a live environment.

Run it:
    python examples/notebook_79_soc_alert_triage.py

## Output

Running it offline — no credentials, bundled mock model — prints the triage an analyst would otherwise do:

```text

────────────────────────────────────────────────────────────
Alert ALT-001: Phishing link clicked by user jsmith
  [FINDING ] HIGH     User clicked confirmed phishing URL
             grounded @ 1.00
             evidence : ['siem:ALT-001:dns_lookups=3', 'siem:ALT-001:url_not_in_allowlist']
             taxonomy : LLM01

────────────────────────────────────────────────────────────
Alert ALT-002: PsExec lateral movement from WKSTN-04 to SRV-FINANCE
  [FINDING ] CRITICAL PsExec lateral movement: WKSTN-04 → SRV-FINANCE
             grounded @ 1.00
             evidence : ['edr:WKSTN-04:process_tree:psexec', 'siem:ALT-002:smb_admin_share_access']
             taxonomy : —

────────────────────────────────────────────────────────────
Alert ALT-003: Outbound connection to known C2 IP 203.0.113.99
  [FINDING ] HIGH     Outbound C2 beacon to 203.0.113.99 (threat-intel confirmed malicious)
             grounded @ 1.00
             evidence : ['intel:203.0.113.99:emerging_threats', 'intel:203.0.113.99:vt_score=47/72', 'siem:ALT-003:beacon_pattern_60s']
             taxonomy : —

────────────────────────────────────────────────────────────
Alert ALT-004: Unusual process: msiexec.exe spawned by Teams.exe
  [ABSTAIN ] msiexec.exe spawned by Teams.exe — possible software update
             reason   : withheld (replan): grounding below the proceed threshold (1 ungrounded of 1 claims)
             gsar     : 0.00 (below threshold)

════════════════════════════════════════════════════════════
Triage complete: 3 findings filed, 1 abstentions.
The abstention(s) above are alerts a commodity AI SOC would have filed as findings.
Here they were withheld because no corroborating evidence was cited — reducing
analyst noise and false-positive rate.
```
<!-- notebook-output:end -->

## Source

````python
--8<-- "examples/notebook_79_soc_alert_triage.py"
````
