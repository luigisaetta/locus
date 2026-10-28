# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Live integration test: the grounded SOC analyst on a real model + a real tenancy.

Runs :func:`create_soc_analyst` against the OCI tenancy of the ``~/.oci/config``
profile named by ``LOCUS_OCI_PROFILE`` / ``OCI_PROFILE`` (``DEFAULT`` when
neither is set), using a real LLM. Auto-skips unless BOTH a model and a usable
OCI profile are present, so it never runs in a bare CI environment. The model
is OCI Generative AI by default (the same profile, ``LOCUS_OCI_TEST_MODEL``
overrides the model id) or an API-key provider when ``ANTHROPIC_API_KEY`` /
``OPENAI_API_KEY`` is exported.

Any tenancy carries some IAM posture facts (users with or without MFA, API
keys on administrators), so a competent model produces at least one finding;
the load-bearing assertion is the grounding invariant — every *shipped* finding
cleared the GSAR threshold, and the rest abstained.
"""

from __future__ import annotations

import os

import pytest

from locus_security import (
    Abstention,
    Evidence,
    PostureReport,
    SecurityControls,
    create_soc_analyst,
    ground_report,
    is_finding,
)


def _oci_env(name: str, default: str) -> str:
    return os.environ.get(f"LOCUS_OCI_{name}") or os.environ.get(f"OCI_{name}") or default


def _oci_profile() -> tuple[str, str] | None:
    """``(profile, tenancy_ocid)`` when the configured profile resolves, else ``None``."""
    try:
        import oci

        profile = _oci_env("PROFILE", "DEFAULT")
        config = oci.config.from_file(profile_name=profile)
    except Exception:
        return None
    tenancy = config.get("tenancy")
    return (profile, tenancy) if tenancy else None


def _model() -> str | None:
    if os.getenv("ANTHROPIC_API_KEY"):
        return os.getenv("LOCUS_ANTHROPIC_TEST_MODEL", "anthropic:claude-haiku-4-5-20251001")
    if os.getenv("OPENAI_API_KEY"):
        return os.getenv("LOCUS_OPENAI_TEST_MODEL", "openai:gpt-4o-mini")
    if _oci_profile():
        return "oci:" + os.getenv("LOCUS_OCI_TEST_MODEL", "openai.gpt-4o")
    return None


skip_without_stack = pytest.mark.skipif(
    not (_oci_profile() and _model()),
    reason="needs a usable OCI profile (LOCUS_OCI_PROFILE / OCI_PROFILE) and a model",
)


@skip_without_stack
def test_soc_analyst_grounds_tenancy_posture_live() -> None:
    profile, tenancy = _oci_profile()  # type: ignore[misc]
    controls = SecurityControls(
        min_gsar=0.6,
        min_confidence=0.6,
        profile=profile,
        auth_type=_oci_env("AUTH_TYPE", "api_key"),
        compartment_id=tenancy,
    )
    analyst = create_soc_analyst(
        model=_model(),  # type: ignore[arg-type]
        controls=controls,
        max_iterations=14,
    )

    result = analyst.run_sync(
        "Review only the IAM posture of this tenancy: whether console users have "
        "MFA activated and whether members of the Administrators group hold API "
        "keys. Make a few read-only calls (start with identity IdentityClient "
        "list_users on the tenancy compartment), cite the exact API facts as "
        "evidence, then submit your report."
    )

    report = result.parsed
    assert isinstance(report, PostureReport)

    grounded = ground_report(report, controls)
    assert len(grounded) == len(report.findings)

    # The grounding invariant: anything that shipped cleared the threshold;
    # everything else is a typed abstention. This must hold regardless of what
    # the model chose to report.
    for g in grounded:
        if is_finding(g):
            assert isinstance(g, Evidence)
            assert g.gsar_score >= controls.min_gsar
        else:
            assert isinstance(g, Abstention)
            assert g.reason
