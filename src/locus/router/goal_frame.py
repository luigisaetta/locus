# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Typed contract the LLM authors at the front of the router.

One rule: the model never invents orchestration topology. It fills
:class:`GoalFrame` — a typed Pydantic schema — and downstream selection
and compilation are deterministic.

This module defines the schema and the three enums it depends on.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class TaskType(StrEnum):
    """The kind of cognitive work the user is asking for.

    Every protocol declares which ``TaskType`` values it can handle, so
    the registry can filter candidates by ``frame.primary_goal`` alone.
    """

    ANSWER = "answer"
    EXPLAIN = "explain"
    PLAN = "plan"
    BUILD = "build"
    MODIFY = "modify"
    DIAGNOSE = "diagnose"
    REMEDIATE = "remediate"
    GENERATE_CODE = "generate_code"
    RESEARCH = "research"
    COMPARE = "compare"
    MONITOR = "monitor"
    COORDINATE = "coordinate"
    ESCALATE = "escalate"


class _OrderedStrEnum(StrEnum):
    """StrEnum with ordering by declaration index.

    ``Risk.LOW < Risk.MEDIUM < Risk.HIGH`` is essential to the policy
    gate (``protocol.risk_max >= frame.risk``) and to the protocol
    registry's complexity-match ranking.

    All four comparison operators are defined explicitly because
    :class:`StrEnum` inherits string comparison from :class:`str` —
    ``functools.total_ordering`` only fills in *missing* methods, so it
    leaves ``str.__gt__`` in place and yields the wrong answer
    (``"low" > "high"`` is True alphabetically).
    """

    def _index(self) -> int:
        return list(type(self)).index(self)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index() < other._index()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index() <= other._index()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index() > other._index()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._index() >= other._index()


class Risk(_OrderedStrEnum):
    """How costly it would be to get this goal wrong."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Complexity(_OrderedStrEnum):
    """How much work the goal needs — the budget half of the routing call."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


#: One line per intent, shown to the extractor through the ``primary_goal``
#: field description so a model sees what separates neighbouring intents
#: instead of thirteen bare enum names.
TASK_TYPE_GUIDE: dict[TaskType, str] = {
    TaskType.ANSWER: "a factual question answered in one reply",
    TaskType.EXPLAIN: "a concept, mechanism or trade-off explained; no artefact produced",
    TaskType.PLAN: "a sequence of steps written down, not executed",
    TaskType.BUILD: "a new artefact produced (schema, config, CLI, document) other than program code",
    TaskType.MODIFY: "an existing artefact, setting or policy changed",
    TaskType.DIAGNOSE: "the cause of a symptom found from alerts, metrics or logs",
    TaskType.REMEDIATE: "a live system acted on to fix it (restart, roll back, drain, recreate)",
    TaskType.GENERATE_CODE: "program code written, usually with tests",
    TaskType.RESEARCH: "information looked up or gathered from sources",
    TaskType.COMPARE: "two or more options weighed against each other, a recommendation made",
    TaskType.MONITOR: "current values and alerts observed and reported, possibly repeatedly",
    TaskType.COORDINATE: "several agents or steps sequenced, each handing off to the next",
    TaskType.ESCALATE: "a person or team notified, a runbook triggered",
}


def _intent_guide() -> str:
    return "; ".join(f"{t.value}: {text}" for t, text in TASK_TYPE_GUIDE.items())


class GoalFrame(BaseModel):
    """The single typed object the LLM produces.

    Everything downstream of ``GoalFrame`` — protocol selection,
    capability binding, policy verdict, builder dispatch — is
    deterministic. The LLM never authors graph topology, only this
    schema.
    """

    primary_goal: TaskType = Field(
        ...,
        description=(
            "The dominant intent; the protocol registry filters by this. "
            "Pick by what the request wants done, not by its subject. "
            f"Meanings: {_intent_guide()}."
        ),
    )
    secondary_goals: list[TaskType] = Field(
        default_factory=list,
        description="Other intents the request also implies. Used as a tiebreaker.",
    )
    domain: str = Field(
        ...,
        description=(
            "Free-form domain tag (e.g. 'observability', 'codegen', 'minecraft'). "
            "Used by CapabilityIndex.for_domain to scope the capability pool."
        ),
    )
    complexity: Complexity = Field(
        ...,
        description="Estimated cognitive complexity. Drives builder fan-out / loop limits.",
    )
    risk: Risk = Field(
        ...,
        description=(
            "Risk of the requested action. The policy gate compares this "
            "against each protocol's ``risk_max`` and against the gate's "
            "``require_approval_above`` threshold."
        ),
    )

    requires_tools: bool = False
    requires_memory: bool = False
    requires_code_generation: bool = False
    requires_multi_agent: bool = False
    approval_required: bool = False

    success_criteria: list[str] = Field(
        default_factory=list,
        description="Plain-text criteria the validator agent (if any) checks against.",
    )
    required_capabilities: list[str] = Field(
        default_factory=list,
        description="Capability ids that must be available; the registry binds these.",
    )

    model_config = {"frozen": True}
