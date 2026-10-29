# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""The router's read-only decision record, its ranking rule, and the risk fallback.

``Router.explain`` / ``CognitiveCompiler.explain`` report the selection the
rule-based ranker makes and why, without running anything. The same tests pin
the two routing rules that changed with them: a canonical protocol wins when
its cost is within one step of the frame's complexity, and a frame whose risk
is above every handler's cap compiles onto ``approval_gated_execution`` and is
held for approval instead of raising.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from locus.agent.result import AgentResult, ExecutionMetrics
from locus.core.state import AgentState
from locus.router import (
    CapabilityIndex,
    CognitiveCompiler,
    Complexity,
    GoalFrame,
    LLMProtocolPicker,
    NoMatchingProtocolError,
    PolicyGate,
    Protocol,
    ProtocolRegistry,
    Risk,
    Router,
    TaskType,
    builtin_protocols,
)
from locus.router.compiler import _ApprovalRunnable
from locus.router.explain import RoutingExplanation, rank_candidates, rejection_for
from locus.router.goal_frame import TASK_TYPE_GUIDE
from locus.router.protocol import A2A_PEER_CAPABILITY, _rank_key
from locus.router.runnable import AgentRunnable
from locus.tools.decorator import tool
from locus.tools.registry import create_registry


@tool
def _echo(text: str) -> str:
    """Echo the input verbatim."""
    return text


def _frame(
    *,
    primary_goal: TaskType = TaskType.ANSWER,
    complexity: Complexity = Complexity.LOW,
    risk: Risk = Risk.LOW,
    approval_required: bool = False,
    required_capabilities: list[str] | None = None,
) -> GoalFrame:
    return GoalFrame(
        primary_goal=primary_goal,
        domain="research",
        complexity=complexity,
        risk=risk,
        approval_required=approval_required,
        required_capabilities=required_capabilities or [],
    )


def _compiler(**overrides: Any) -> CognitiveCompiler:
    idx = CapabilityIndex(create_registry(_echo))
    idx.annotate("c1", tool_name="_echo", description="echo", domain="d")
    reg = ProtocolRegistry()
    reg.register_many(builtin_protocols())
    kwargs: dict[str, Any] = {
        "protocols": reg,
        "capabilities": idx,
        "policy": PolicyGate(),
        "model": "openai:gpt-4o-mini",
    }
    kwargs.update(overrides)
    return CognitiveCompiler(**kwargs)


def _by_id(protocol_id: str) -> Protocol:
    return next(p for p in builtin_protocols() if p.id == protocol_id)


def _agent_result(parsed: GoalFrame | None) -> AgentResult:
    return AgentResult.from_state(
        state=AgentState(),
        stop_reason="complete",
        metrics=ExecutionMetrics(),
        message="",
        parsed=parsed,
    )


# ---------------------------------------------------------------------------
# Rejection reasons and ranking
# ---------------------------------------------------------------------------


class TestRejectionFor:
    def test_goal_gate_is_reported_first(self):
        rejected = rejection_for(_by_id("debate"), _frame(), set())
        assert rejected is not None
        assert rejected.gate == "goal"
        assert "'answer'" in rejected.reason

    def test_risk_gate(self):
        rejected = rejection_for(_by_id("direct_response"), _frame(risk=Risk.MEDIUM), set())
        assert rejected is not None
        assert rejected.gate == "risk"
        assert "'low'" in rejected.reason
        assert "'medium'" in rejected.reason

    def test_capability_gate_names_the_missing_ids(self):
        frame = _frame(primary_goal=TaskType.COORDINATE)
        rejected = rejection_for(_by_id("a2a_delegate"), frame, set())
        assert rejected is not None
        assert rejected.gate == "capabilities"
        assert A2A_PEER_CAPABILITY in rejected.reason

    def test_a_fitting_protocol_is_not_rejected(self):
        assert rejection_for(_by_id("direct_response"), _frame(), set()) is None


class TestRankCandidates:
    def test_orders_like_the_ranker_and_flags_the_selection(self):
        frame = _frame(primary_goal=TaskType.COMPARE)
        candidates = [_by_id("specialist_fanout"), _by_id("debate")]
        ranked = rank_candidates(candidates, frame, selected="debate")
        assert [r.protocol_id for r in ranked] == ["debate", "specialist_fanout"]
        assert ranked[0].selected
        assert not ranked[1].selected
        assert ranked[0].is_canonical
        assert ranked[0].rank == _rank_key(_by_id("debate"), frame)


class TestRankingRule:
    """Canonical fit wins when the protocol's cost is within one step of the complexity."""

    def test_canonical_beats_a_closer_cost_match_when_adjacent(self):
        # MEDIUM research: handoff_chain (medium cost, not canonical) used to win on
        # distance alone; specialist_fanout is canonical and only one step away.
        reg = ProtocolRegistry()
        reg.register_many(builtin_protocols())
        chosen = reg.select(_frame(primary_goal=TaskType.RESEARCH, complexity=Complexity.MEDIUM))
        assert chosen.id == "specialist_fanout"

    def test_canonical_does_not_win_when_two_steps_away(self):
        # LOW-complexity research stays cheap: the canonical fan-out is two steps up.
        reg = ProtocolRegistry()
        reg.register_many(builtin_protocols())
        assert reg.select(_frame(primary_goal=TaskType.RESEARCH)).id == "direct_response"

    def test_sequencing_stays_sequential_at_high_complexity(self):
        reg = ProtocolRegistry()
        reg.register_many(builtin_protocols())
        chosen = reg.select(_frame(primary_goal=TaskType.COORDINATE, complexity=Complexity.HIGH))
        assert chosen.id == "handoff_chain"


# ---------------------------------------------------------------------------
# CognitiveCompiler.explain
# ---------------------------------------------------------------------------


class TestCompilerExplain:
    def test_rule_based_selection_with_rejections_and_verdict(self):
        explanation = _compiler().explain(_frame(), goal="What is RAG?")
        assert explanation.selected_protocol == "direct_response"
        assert explanation.method == "rule_based"
        assert explanation.allowed
        assert not explanation.requires_approval
        assert "c1" in explanation.available_capabilities
        rejected = {r.protocol_id: r.gate for r in explanation.rejected}
        assert rejected["debate"] == "goal"
        assert "direct_response" not in rejected
        assert [c.protocol_id for c in explanation.candidates] == ["direct_response"]

    def test_method_reports_what_a_picker_would_do(self):
        picker = LLMProtocolPicker(model=MagicMock())
        compiler = _compiler(protocol_picker=picker)
        # Two candidates survive for a LOW-risk COMPARE: the picker would be asked.
        assert compiler.explain(_frame(primary_goal=TaskType.COMPARE)).method == "llm_picked"
        # One candidate: the compiler short-circuits without a model call.
        assert compiler.explain(_frame(primary_goal=TaskType.DIAGNOSE)).method == "single_candidate"

    def test_a2a_endpoint_adds_the_peer_capability(self):
        explanation = _compiler(a2a_endpoint="http://peer").explain(
            _frame(primary_goal=TaskType.COORDINATE)
        )
        assert A2A_PEER_CAPABILITY in explanation.available_capabilities
        assert "a2a_delegate" not in {r.protocol_id for r in explanation.rejected}

    def test_approval_shows_in_the_verdict_and_the_rendering(self):
        explanation = _compiler().explain(
            _frame(primary_goal=TaskType.REMEDIATE, risk=Risk.HIGH), goal="restart prod"
        )
        assert explanation.selected_protocol == "approval_gated_execution"
        assert explanation.requires_approval
        text = str(explanation)
        assert "goal: restart prod" in text
        assert "Selected protocol  approval_gated_execution" in text
        assert "human approval required" in text
        assert "Rejected (" in text
        assert "Considered (" in text

    def test_rendering_lists_capabilities_and_rationale(self):
        explanation = RoutingExplanation(
            goal="g",
            goal_frame=_frame(required_capabilities=["c1"]),
            selected_protocol="direct_response",
            method="llm_picked",
            candidates=(),
            rejected=(),
            available_capabilities=("c1",),
            policy=None,
            picker_rationale="cheapest fit",
        )
        text = str(explanation)
        assert "capabilities ['c1']" in text
        assert "chosen by        llm_picked" in text
        assert "rationale        cheapest fit" in text
        assert explanation.allowed  # no verdict means nothing blocked it


# ---------------------------------------------------------------------------
# Risk fallback: too risky for every handler -> approval-gated, held
# ---------------------------------------------------------------------------


class TestRiskFallback:
    def test_high_risk_plan_is_held_instead_of_raising(self):
        compiler = _compiler()
        frame = _frame(primary_goal=TaskType.PLAN, risk=Risk.HIGH)
        explanation = compiler.explain(frame)
        assert explanation.selected_protocol == "approval_gated_execution"
        assert explanation.method == "risk_fallback"
        assert explanation.requires_approval  # the gate itself requires it at HIGH
        runnable = asyncio.run(compiler.compile(frame))
        assert isinstance(runnable, _ApprovalRunnable)

    def test_medium_risk_answer_is_held_too(self):
        # direct_response caps at LOW; the gate alone would let MEDIUM through
        # unheld, but the fallback path always holds.
        explanation = _compiler().explain(_frame(risk=Risk.MEDIUM))
        assert explanation.selected_protocol == "approval_gated_execution"
        assert explanation.requires_approval
        assert explanation.policy is not None
        assert "held for approval" in explanation.policy.reason

    def test_fallback_is_not_used_when_a_handler_fits(self):
        explanation = _compiler().explain(_frame(primary_goal=TaskType.PLAN, risk=Risk.MEDIUM))
        assert explanation.selected_protocol == "plan_execute_validate"
        assert explanation.method == "rule_based"

    def test_unhandled_goal_still_raises(self):
        reg = ProtocolRegistry()
        reg.register_many([_by_id("direct_response"), _by_id("approval_gated_execution")])
        compiler = _compiler(protocols=reg)
        frame = _frame(primary_goal=TaskType.GENERATE_CODE, risk=Risk.HIGH)
        assert compiler.explain(frame).selected_protocol is None
        with pytest.raises(NoMatchingProtocolError):
            asyncio.run(compiler.compile(frame))

    def test_fallback_can_be_disabled(self):
        compiler = _compiler(risk_fallback=None)
        frame = _frame(primary_goal=TaskType.PLAN, risk=Risk.HIGH)
        assert compiler.explain(frame).selected_protocol is None
        with pytest.raises(NoMatchingProtocolError):
            asyncio.run(compiler.compile(frame))

    def test_fallback_needs_a_registered_protocol_that_takes_the_risk(self):
        reg = ProtocolRegistry()
        reg.register_many([_by_id("direct_response"), _by_id("plan_execute_validate")])
        compiler = _compiler(protocols=reg)  # default fallback id is not registered
        with pytest.raises(NoMatchingProtocolError):
            asyncio.run(compiler.compile(_frame(primary_goal=TaskType.PLAN, risk=Risk.HIGH)))

    def test_gate_ceiling_still_denies_above_max_risk(self):
        from locus.router import PolicyDeniedError

        compiler = _compiler(policy=PolicyGate(max_risk=Risk.MEDIUM))
        with pytest.raises(PolicyDeniedError):
            asyncio.run(compiler.compile(_frame(primary_goal=TaskType.PLAN, risk=Risk.HIGH)))


# ---------------------------------------------------------------------------
# Intent guide reaches the schema the extractor fills
# ---------------------------------------------------------------------------


class TestIntentGuide:
    def test_every_task_type_has_a_line(self):
        assert set(TASK_TYPE_GUIDE) == set(TaskType)

    def test_guide_is_in_the_primary_goal_description(self):
        description = GoalFrame.model_json_schema()["properties"]["primary_goal"]["description"]
        for task_type, text in TASK_TYPE_GUIDE.items():
            assert f"{task_type.value}: {text}" in description


# ---------------------------------------------------------------------------
# Router.explain / Router.compile / failure event
# ---------------------------------------------------------------------------


class TestRouterReadOnly:
    def _router(self, frame: GoalFrame) -> Router:
        extractor = MagicMock()
        extractor.invoke = MagicMock(return_value=_agent_result(frame))
        return Router(extractor=extractor, compiler=_compiler())

    def test_explain_extracts_once_and_executes_nothing(self):
        router = self._router(_frame())
        explanation = asyncio.run(router.explain("What is RAG?"))
        assert explanation.goal == "What is RAG?"
        assert explanation.selected_protocol == "direct_response"
        router.extractor.invoke.assert_called_once_with("What is RAG?")

    def test_explain_with_a_pinned_frame_skips_the_extractor(self):
        router = self._router(_frame())
        explanation = asyncio.run(
            router.explain("ignored", frame=_frame(primary_goal=TaskType.COMPARE))
        )
        assert explanation.selected_protocol == "debate"
        router.extractor.invoke.assert_not_called()

    def test_compile_builds_without_running(self):
        router = self._router(_frame())
        runnable = asyncio.run(router.compile("What is RAG?"))
        assert isinstance(runnable, AgentRunnable)
        runnable_pinned = asyncio.run(router.compile("x", frame=_frame(primary_goal=TaskType.PLAN)))
        assert runnable_pinned.protocol_id == "plan_execute_validate"

    def test_dispatch_reports_a_runnable_failure_on_the_bus(self, monkeypatch):
        failed = AsyncMock()
        monkeypatch.setattr("locus.router.runtime.emit_runnable_failed", failed)
        router = self._router(_frame())
        boom = MagicMock()
        boom.protocol_id = "direct_response"
        boom.execute = AsyncMock(side_effect=RuntimeError("boom"))
        router.compiler.compile = AsyncMock(return_value=boom)  # type: ignore[method-assign]
        with pytest.raises(RuntimeError, match="boom"):
            asyncio.run(router.dispatch("What is RAG?", run_id="r1"))
        failed.assert_awaited_once_with("r1", "direct_response", "RuntimeError: boom")
