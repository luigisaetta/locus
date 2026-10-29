# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""``runpod:`` — RunPod serverless and public endpoints behind one prefix.

RunPod's OpenAI-compatible URL embeds the endpoint id
(``https://api.runpod.ai/v2/<endpoint-id>/openai/v1``), so the spec carries a
template filled from ``RUNPOD_ENDPOINT_ID``; the usual explicit / LOCUS_ /
vendor base-URL overrides still win.
"""

from __future__ import annotations

import pytest

from locus.models import get_model
from locus.models.providers import COMPATIBLE_PROVIDERS


SPEC = next(s for s in COMPATIBLE_PROVIDERS if s.prefix == "runpod")


def _clear(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("LOCUS_RUNPOD_BASE_URL", "RUNPOD_BASE_URL", "RUNPOD_ENDPOINT_ID", "RUNPOD_API_KEY"):
        monkeypatch.delenv(var, raising=False)


def test_endpoint_id_builds_the_public_endpoint_url(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear(monkeypatch)
    monkeypatch.setenv("RUNPOD_ENDPOINT_ID", "qwen3-32b-awq")
    model = get_model("runpod:Qwen/Qwen3-32B-AWQ", api_key="k")
    assert model.config.base_url == "https://api.runpod.ai/v2/qwen3-32b-awq/openai/v1"
    assert model.config.model == "Qwen/Qwen3-32B-AWQ"


def test_explicit_and_env_base_urls_beat_the_endpoint_id(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear(monkeypatch)
    monkeypatch.setenv("RUNPOD_ENDPOINT_ID", "qwen3-32b-awq")
    monkeypatch.setenv("RUNPOD_BASE_URL", "https://api.runpod.ai/v2/mine/openai/v1")
    assert SPEC.resolve_base_url() == "https://api.runpod.ai/v2/mine/openai/v1"
    monkeypatch.setenv("LOCUS_RUNPOD_BASE_URL", "https://proxy.internal/v1")
    assert SPEC.resolve_base_url() == "https://proxy.internal/v1"
    assert SPEC.resolve_base_url("https://explicit/v1") == "https://explicit/v1"


def test_without_any_endpoint_the_error_names_the_endpoint_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear(monkeypatch)
    with pytest.raises(ValueError, match="RUNPOD_ENDPOINT_ID"):
        get_model("runpod:Qwen/Qwen3-32B-AWQ", api_key="k")


def test_key_comes_from_runpod_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear(monkeypatch)
    monkeypatch.setenv("RUNPOD_ENDPOINT_ID", "qwen3-32b-awq")
    with pytest.raises(ValueError, match="RUNPOD_API_KEY"):
        get_model("runpod:Qwen/Qwen3-32B-AWQ")
    monkeypatch.setenv("RUNPOD_API_KEY", "rpa_test")
    assert get_model("runpod:Qwen/Qwen3-32B-AWQ").config.base_url.endswith(
        "/qwen3-32b-awq/openai/v1"
    )
