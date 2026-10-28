# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""Hosted OpenAI-compatible routes, live: one completion and one tool call each.

Each case skips on its own when the provider's key is absent, so a machine
with only one of the keys still exercises that route. The RunPod case uses a
RunPod public endpoint by default (``RUNPOD_ENDPOINT_ID`` overrides it).
"""

from __future__ import annotations

import os

import pytest

from locus.agent import Agent
from locus.tools import tool


CASES = [
    ("openrouter", "openai/gpt-4.1-mini", "OPENROUTER_API_KEY", {}),
    ("together", "openai/gpt-oss-120b", "TOGETHER_API_KEY", {}),
    ("runpod", "Qwen/Qwen3-32B-AWQ", "RUNPOD_API_KEY", {"RUNPOD_ENDPOINT_ID": "qwen3-32b-awq"}),
]


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@pytest.mark.parametrize(("prefix", "model", "key", "defaults"), CASES, ids=[c[0] for c in CASES])
def test_completion_and_tool_call(
    prefix: str, model: str, key: str, defaults: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    if not os.environ.get(key):
        pytest.skip(f"{key} not set")
    for var, value in defaults.items():
        monkeypatch.setenv(var, os.environ.get(var, value))

    text = Agent(model=f"{prefix}:{model}").run_sync("Reply with exactly: pong").text
    assert "pong" in text.lower()

    agent = Agent(
        model=f"{prefix}:{model}",
        tools=[add],
        system_prompt="Use the add tool for arithmetic. Reply with the number only.",
    )
    assert "42" in agent.run_sync("What is 17 + 25?").text
