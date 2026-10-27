# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Gemini rides the OpenAI-compatible routing table, because Google publishes and
maintains an OpenAI-shaped endpoint alongside the native API. These tests pin the
registration, the base URL and the key handling of that route.
"""

from __future__ import annotations

import pytest

from locus.models.providers import COMPATIBLE_PROVIDERS
from locus.models.registry import get_model, list_providers


pytest.importorskip("openai", reason="openai extra not installed")


# ------------------------------------------------------------------- gemini


def test_gemini_is_registered() -> None:
    assert "gemini" in list_providers()


def test_gemini_points_at_googles_own_openai_surface() -> None:
    """First-party, not a proxy — the distinction the capability matrix draws."""
    [spec] = [s for s in COMPATIBLE_PROVIDERS if s.prefix == "gemini"]
    assert spec.base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
    assert spec.env_key == "GEMINI_API_KEY"
    assert spec.requires_key is True


def test_gemini_builds_with_an_explicit_key(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    model = get_model("gemini:gemini-2.0-flash", api_key="test-key")
    assert model.config.base_url == "https://generativelanguage.googleapis.com/v1beta/openai/"
    assert model.config.model == "gemini-2.0-flash"


def test_gemini_without_a_key_names_the_variable(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        get_model("gemini:gemini-2.0-flash")


def test_gemini_base_url_is_overridable(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("LOCUS_GEMINI_BASE_URL", "https://proxy.internal/v1")
    assert get_model("gemini:gemini-2.0-flash").config.base_url == "https://proxy.internal/v1"


def test_gemini_is_a_registered_provider() -> None:
    assert "gemini" in set(list_providers())
