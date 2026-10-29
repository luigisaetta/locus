# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Notebook 81: Grounded OCI cloud-posture agent.

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

An agent without grounding can narrate misconfigurations it never observed.
Here an ungrounded claim cannot become an ``Evidence`` — it abstains — and the
abstention is kept for audit.

The finding class maps to OWASP ASI03, Identity & Privilege Abuse (the
API-key-on-an-administrator finding); the read-only-by-default tooling is the
control that keeps the auditor itself from becoming a liability.

Run it:
    python packages/locus-sdk-security/examples/notebook_81_cloud_posture_agent.py

Part 1 (the grounding decision) runs fully offline and deterministically — no
model, no tenancy. Part 2 builds the live agent; it runs against a real
tenancy only when BOTH a live model and a usable ``~/.oci/config`` profile are
present. The model comes from this package's ``config.py``: set
``LOCUS_MODEL_PROVIDER`` to ``openai`` or ``anthropic`` with the matching API
key; that harness has no OCI Generative AI branch, so an OCI profile does not
select a model. The profile (``LOCUS_OCI_PROFILE`` / ``OCI_PROFILE``;
``DEFAULT`` otherwise) selects the audited tenancy. With either missing, Part 2
prints the bring-your-own-credentials note and returns.

Prerequisites:
- Notebook 31 (DeepAgent) — the core this factory wraps.
- For the live Part 2 only: a structured-output-capable provider and the ``oci``
  SDK (``pip install 'locus-sdk[oci]'``) with a profile whose IAM group grants
  only inspect / read verbs. The agent is read-only by default; ``use_oci``
  refuses mutating operations.
"""

from __future__ import annotations

import asyncio
import os

from config import MockModel, get_model

from locus.control.taxonomy import OwaspASI
from locus_security import (
    PostureEvidence,
    PostureFinding,
    PostureReport,
    SecurityControls,
    Severity,
    create_soc_analyst,
    ground_report,
    is_finding,
)


# =============================================================================
# Part 1 — the grounding decision, offline and deterministic.
#
# We hand-build the report exactly as the agent would submit it (three proposed
# findings) and run it through ``ground_report``. Two rest on real API
# observations; one is pure speculation. Watch the speculative one abstain.
# =============================================================================


def _sample_report() -> PostureReport:
    return PostureReport(
        summary="IAM review of tenancy ocid1.tenancy.oc1..example.",
        confidence=0.9,
        findings=[
            # Grounded in a concrete list_api_keys fact → will ship.
            PostureFinding(
                title="Tenancy administrator has a long-lived API key",
                description=(
                    "A member of the Administrators group holds an API key created "
                    "over a year ago, against the CIS OCI Foundations Benchmark IAM "
                    "controls. An administrator's key cannot be scoped below the "
                    "tenancy and is a standing compromise of everything in it."
                ),
                severity=Severity.CRITICAL,
                asset="oci:identity:user/admin (Administrators)",
                remediation=(
                    "Delete the key; administrators should authenticate with "
                    "`oci session authenticate` or instance principals instead."
                ),
                taxonomy=[OwaspASI.IDENTITY_AND_PRIVILEGE_ABUSE],
                evidence=[
                    PostureEvidence(
                        statement=(
                            "list_api_keys for user admin returns 1 key, timeCreated 2024-01-09"
                        ),
                        ref="oci:identity:list_api_keys:timeCreated",
                        grounded=True,
                    )
                ],
            ),
            # Grounded positive observation → ships as an informational Evidence.
            PostureFinding(
                title="MFA is active for every console user",
                description="Every user with a console password has MFA activated.",
                severity=Severity.INFO,
                asset="oci:identity:users (tenancy)",
                remediation="Maintain the MFA requirement; re-check on each new user.",
                evidence=[
                    PostureEvidence(
                        statement="list_users reports isMfaActivated=true for all 12 console users",
                        ref="oci:identity:list_users:isMfaActivated",
                        grounded=True,
                    )
                ],
            ),
            # No observation behind it — only an inference. → abstains.
            PostureFinding(
                title="Possible lateral-movement path via an over-broad policy",
                description=(
                    "The tenancy may carry a policy granting `manage all-resources` "
                    "to a non-administrator group."
                ),
                severity=Severity.MEDIUM,
                asset="oci:tenancy:ocid1.tenancy.oc1..example",
                remediation="Review policy statements and group memberships.",
                evidence=[
                    PostureEvidence(
                        statement="An attacker could pivot if such a policy existed",
                        ref="inference:no-call-made",
                        grounded=False,
                    )
                ],
            ),
        ],
    )


def part1_grounding_offline() -> None:
    print("\n--- Part 1: the grounding decision (offline, deterministic) ---")
    controls = SecurityControls(min_gsar=0.6)
    report = _sample_report()
    print(f"agent proposed {len(report.findings)} finding(s); grounding each:\n")

    shipped = 0
    for grounded in ground_report(report, controls):
        if is_finding(grounded):
            shipped += 1
            print(f"  SHIP    [{grounded.severity:<8}] {grounded.title}")
            print(f"          gsar={grounded.gsar_score:.2f}  evidence={grounded.evidence_refs}")
        else:
            print(f"  ABSTAIN  {grounded.reason}")
    print(f"\n{shipped}/{len(report.findings)} proposed findings cleared grounding and shipped.")
    print("The speculative finding abstained — it cited no observation. That is the moat.")


# =============================================================================
# Part 2 — the live agent.
#
# Build the analyst with ``create_soc_analyst`` (the core read-only OCI tools
# baked in, pinned to your profile and tenancy through ``SecurityControls``).
# Run it against a real tenancy only when a real model AND a usable OCI
# profile are present; otherwise show the shape and exit cleanly.
# =============================================================================


def _oci_env(name: str, default: str) -> str:
    """``LOCUS_OCI_<name>`` first, then the OCI-CLI-standard ``OCI_<name>``."""
    return os.environ.get(f"LOCUS_OCI_{name}") or os.environ.get(f"OCI_{name}") or default


def _oci_target() -> SecurityControls | None:
    """Controls pinned to the configured profile's tenancy, or ``None`` when unusable."""
    try:
        import oci

        profile = _oci_env("PROFILE", "DEFAULT")
        config = oci.config.from_file(profile_name=profile)
    except Exception:
        return None
    tenancy = config.get("tenancy")
    if not tenancy:
        return None
    return SecurityControls(
        min_gsar=0.6,
        min_confidence=0.6,
        profile=profile,
        auth_type=_oci_env("AUTH_TYPE", "api_key"),
        compartment_id=tenancy,
    )


async def part2_live_agent() -> None:
    print("\n--- Part 2: the live cloud-posture agent ---")
    target = _oci_target()
    controls = target or SecurityControls(min_gsar=0.6, min_confidence=0.6)
    model = get_model()
    analyst = create_soc_analyst(model=model, controls=controls, max_iterations=14)

    tool_names = sorted(getattr(t, "name", "?") for t in analyst.config.tools)
    print(f"analyst tools: {tool_names}")
    print("read-only by default: use_oci refuses any operation that is not a list/get-style read.")

    # get_model() honours LOCUS_MODEL_PROVIDER (openai / anthropic) and otherwise
    # returns the bundled mock; the harness has no OCI model branch, so the OCI
    # profile only selects the audited tenancy. The live run needs both.
    if isinstance(model, MockModel) or target is None:
        print(
            "\nLive run skipped (bring-your-own-credentials).\n"
            "  Configure an OCI profile (or set LOCUS_MODEL_PROVIDER to a live provider)\n"
            "  and point LOCUS_OCI_PROFILE / OCI_PROFILE at a read-only profile to audit\n"
            "  a real tenancy. Offline, Part 1 already showed the grounding decision\n"
            "  that gates the report."
        )
        return

    print(f"\nrunning the analyst against tenancy {controls.compartment_id} (read-only)…")
    result = await analyst.arun(
        "Review the IAM posture of the tenancy: whether console users have MFA "
        "activated and whether members of the Administrators group hold API keys. "
        "Start with identity IdentityClient list_users on the tenancy compartment, "
        "cite the exact API facts as evidence, then submit your report."
    )
    report = result.parsed
    if report is None:
        print(f"no structured report (stop_reason={result.stop_reason}).")
        return
    print(f"\nsummary: {report.summary[:200]}")
    for grounded in ground_report(report, controls):
        if is_finding(grounded):
            print(
                f"  SHIP    [{grounded.severity:<8}] {grounded.title} "
                f"(gsar={grounded.gsar_score:.2f})"
            )
        else:
            print(f"  ABSTAIN  {grounded.reason[:80]}")


async def main() -> None:
    part1_grounding_offline()
    await part2_live_agent()


if __name__ == "__main__":
    asyncio.run(main())
