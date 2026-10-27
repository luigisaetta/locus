# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""``OracleAgentMemoryManager`` derives litellm's OCI auth from the OCI profile.

litellm's ``oci/`` driver ignores ``~/.oci/config``; without these kwargs an
``oci/...`` embedder or LLM fails with "Missing credentials" on any machine
that authenticates through a profile or a session token.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from locus.memory.managers.oracle_agent_memory import _litellm_kwargs_for, oci_litellm_auth


def test_non_oci_specs_are_left_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OCI_PROFILE", "DEFAULT")
    assert oci_litellm_auth("openai/text-embedding-3-small") == {}


def test_litellm_env_configuration_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    """When the caller configured litellm's own OCI variables, do not interfere."""
    monkeypatch.setenv("OCI_USER", "ocid1.user.oc1..example")
    assert oci_litellm_auth("oci/cohere.embed-v4.0") == {}


def test_missing_profile_means_no_kwargs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pytest.importorskip("oci")
    for k in ("OCI_USER", "OCI_KEY_FILE", "OCI_KEY_CONTENT", "OCI_FINGERPRINT", "OCI_AUTH_TYPE"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("OCI_PROFILE", "no-such-profile-for-this-test")
    monkeypatch.setenv("OCI_CLI_CONFIG_FILE", str(tmp_path / "missing-config"))
    assert oci_litellm_auth("oci/openai.gpt-4.1") == {}


def test_session_token_profile_yields_signer_region_and_compartment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    oci = pytest.importorskip("oci")
    rsa = pytest.importorskip("cryptography.hazmat.primitives.asymmetric.rsa")
    from cryptography.hazmat.primitives import serialization  # noqa: PLC0415

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    key_file = tmp_path / "key.pem"
    key_file.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )
    token_file = tmp_path / "token"
    token_file.write_text("session-token-for-test")
    for k in ("OCI_USER", "OCI_KEY_FILE", "OCI_KEY_CONTENT", "OCI_FINGERPRINT", "OCI_AUTH_TYPE"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("OCI_SESSION_PROFILE", "SESSION")
    monkeypatch.setenv("OCI_REGION", "eu-frankfurt-1")
    monkeypatch.setenv("OCI_COMPARTMENT_ID", "ocid1.compartment.oc1..example")
    monkeypatch.setattr(
        oci.config,
        "from_file",
        lambda profile_name: {
            "region": "us-chicago-1",
            "key_file": str(key_file),
            "security_token_file": str(token_file),
            "tenancy": "ocid1.tenancy.oc1..example",
        },
    )

    kwargs = oci_litellm_auth("oci/cohere.embed-v4.0")

    assert isinstance(kwargs["oci_signer"], oci.auth.signers.SecurityTokenSigner)
    assert kwargs["oci_region"] == "eu-frankfurt-1"  # env beats the profile region
    assert kwargs["oci_compartment_id"] == "ocid1.compartment.oc1..example"

    layered = _litellm_kwargs_for("oci/cohere.embed-v4.0", {"oci_region": "us-ashburn-1"})
    assert layered["oci_region"] == "us-ashburn-1"
    assert "oci_signer" in layered
