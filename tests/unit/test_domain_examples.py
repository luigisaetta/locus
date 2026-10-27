# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""The non-security domain examples run end-to-end.

The control runtime is domain-neutral: ``notebook_83``..``87`` show ``admit()``
gating payments, infrastructure, customer-support, data-privacy, and cloud
actions. They run offline (no network or credentials) and must exit 0 and hold
the risky action for a human, so a future change that breaks one fails CI
instead of silently shipping.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


_REPO = Path(__file__).resolve().parents[2]


def _run(notebook: str) -> subprocess.CompletedProcess[str]:
    # Pin the bundled mock model: ``examples/config.py`` auto-detects OCI when a
    # usable ``~/.oci/config`` profile exists, and these are offline tests.
    env = {**os.environ, "LOCUS_MODEL_PROVIDER": "mock"}
    return subprocess.run(
        [sys.executable, f"examples/{notebook}"],
        cwd=_REPO,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=env,
    )


@pytest.mark.parametrize(
    ("notebook", "domain"),
    [
        ("notebook_71_payment_refund_gate.py", "payments"),
        ("notebook_72_infra_deploy_gate.py", "infra/devops"),
        ("notebook_73_support_account_gate.py", "customer support"),
        ("notebook_74_data_deletion_gate.py", "data/privacy"),
        ("notebook_75_cloud_resource_gate.py", "cloud"),
    ],
)
def test_domain_example_runs(notebook: str, domain: str) -> None:
    """Each domain example runs offline and holds the risky action for a human."""
    proc = _run(notebook)
    assert proc.returncode == 0, f"{notebook} ({domain}) exited {proc.returncode}:\n{proc.stderr}"
    # The whole point of the gate: the high-risk action is held, not auto-run.
    assert "require_human" in proc.stdout, (
        f"{notebook} ({domain}) never held an action for a human:\n{proc.stdout[-500:]}"
    )


def test_ir_audit_trail_example_runs() -> None:
    """The incident-response audit-trail example runs offline on the control core."""
    proc = _run("notebook_76_ir_audit_trail.py")
    assert proc.returncode == 0, f"notebook_81 exited {proc.returncode}:\n{proc.stderr}"
    assert "Incident Response" in proc.stdout
