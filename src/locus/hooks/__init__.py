# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Lifecycle hooks for Locus.

This module provides a hook system for observing and modifying
agent behavior at key lifecycle points.

Example:
    from locus.hooks import HookRegistry, HookProvider, HookPriority
    from locus.hooks.builtin import LoggingHook, GuardrailsHook

    # Create registry with hooks
    registry = HookRegistry()
    registry.add_provider(GuardrailsHook())  # Priority 50 (security)
    registry.add_provider(LoggingHook())     # Priority 150 (observability)

    # Use in agent
    agent = Agent(
        model="openai:gpt-4o",
        hooks=registry,
    )
"""

from locus.hooks.events import (
    AfterInvocationEvent,
    BeforeInvocationEvent,
    HookEvent,
    HookResult,
    IterationEndEvent,
    IterationStartEvent,
)
from locus.hooks.external import (
    ExternalHooks,
    HookBlockedError,
    HookCommand,
    HookConfig,
    HookOutcome,
    HookRun,
    ToolCallVerdict,
)
from locus.hooks.provider import (
    AfterModelCallEvent,
    AfterToolCallEvent,
    BeforeCompactionEvent,
    BeforeModelCallEvent,
    BeforeToolCallEvent,
    HookPriority,
    HookProvider,
    ProtectedEvent,
)
from locus.hooks.registry import HookRegistry, create_registry


__all__ = [
    # Core classes
    "HookProvider",
    "HookPriority",
    "HookRegistry",
    "ProtectedEvent",
    "create_registry",
    # Command and HTTP hooks an operator configures in a settings file
    "ExternalHooks",
    "HookBlockedError",
    "HookCommand",
    "HookConfig",
    "HookOutcome",
    "HookRun",
    "ToolCallVerdict",
    # Events - write-protected (from provider)
    "AfterModelCallEvent",
    "AfterToolCallEvent",
    "BeforeCompactionEvent",
    "BeforeModelCallEvent",
    "BeforeToolCallEvent",
    # Events - info (from events)
    "AfterInvocationEvent",
    "BeforeInvocationEvent",
    "HookEvent",
    "HookResult",
    "IterationEndEvent",
    "IterationStartEvent",
]
