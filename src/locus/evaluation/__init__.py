# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Agent evaluation framework.

Provides systematic testing of agent quality:
- Define test cases with expected behaviors
- Run agents against test suites
- Score results and generate reports
- Grade free-form answers against a rubric with :class:`LLMJudge`
- Run the same suite against a ``StateGraph`` via :func:`as_eval_target`
"""

from locus.evaluation.framework import (
    EvalCase,
    EvalReport,
    EvalResult,
    EvalRunner,
)
from locus.evaluation.graph import GraphEvalTarget, as_eval_target
from locus.evaluation.judge import JudgeUnavailableError, LLMJudge, Verdict, check_trajectory


__all__ = [
    "GraphEvalTarget",
    "JudgeUnavailableError",
    "LLMJudge",
    "Verdict",
    "check_trajectory",
    "EvalCase",
    "EvalReport",
    "EvalResult",
    "EvalRunner",
    "as_eval_target",
]
