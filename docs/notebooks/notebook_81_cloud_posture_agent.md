# Grounded OCI cloud-posture agent

A SOC-analyst-shaped agent that audits an OCI tenancy read-only, then
*grounds* every finding it proposes against the API facts it actually
observed. ``create_soc_analyst`` composes the two core spec-driven, read-only
OCI tools — ``describe_oci`` (discover the shape of the OCI control plane from
the installed OCI Python SDK: services, clients, operations, parameters) and
``use_oci`` (run one read-only operation, return the response as evidence) —
behind a ``create_deepagent`` core. The agent proposes findings;
``ground_report`` decides which survive: a proposed finding becomes a typed
``Evidence`` only if its cited evidence clears the GSAR threshold, otherwise it
abstains. The model gathers and proposes; Python decides what ships.

This is the differentiator. A commodity "cloud agent" will confidently narrate
misconfigurations it never actually observed. Here, a finding survives only if
the analyst cited direct API observations for it; inferences alone abstain
(``ground_report``). The control is on the *shape* of the evidence, not its
truth — the agent marks each cited fact as observation or inference (the
``grounded`` flag, which defaults to observation), and the ``ref`` string is
carried for audit, not parsed — so pair this with the raw ``use_oci`` responses
when you need the citation itself checked.

Maps to OWASP ASI: Identity & Privilege Abuse (the API-key-on-an-administrator
class of finding); the read-only-by-default tooling is the control that keeps
the auditor itself from becoming a liability.

Run it:

    python packages/locus-sdk-security/examples/notebook_81_cloud_posture_agent.py

Part 1 (the grounding decision) runs fully offline and deterministically — no
model, no tenancy. Part 2 builds the live agent; it runs against a real
tenancy only when BOTH a real model (OCI Generative AI auto-detected from your
OCI profile, or ``LOCUS_MODEL_PROVIDER=openai`` / ``anthropic``) and a usable
``~/.oci/config`` profile (``LOCUS_OCI_PROFILE`` / ``OCI_PROFILE``; ``DEFAULT``
otherwise) are present. With neither, it prints the bring-your-own-credentials
note and exits cleanly.

Prerequisites:

- The DeepAgent notebook — the core this factory wraps.
- For the live Part 2 only: a structured-output-capable provider + the ``oci``
  SDK (``pip install 'locus-sdk[oci]'``) with a profile whose IAM group grants
  only inspect / read verbs. The agent is read-only by default; ``use_oci``
  refuses mutating operations.

## Source

````python
--8<-- "examples/notebook_81_cloud_posture_agent.py"
````
