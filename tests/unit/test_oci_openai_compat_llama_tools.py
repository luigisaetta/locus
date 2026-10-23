# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""OCI V1 transport: Llama + tools needs a user message first.

OCI's ``/openai/v1`` answers ``400 Tool calling for this Llama model
requires the first message to be a user message`` when a system message
leads the conversation. ``fold_leading_system_into_first_user`` merges the
system text into the first user turn; ``_prepare_messages_for_oci`` applies
it only for ``meta.llama*`` with tools.
"""

from __future__ import annotations

from locus.core.messages import Message, Role
from locus.models.providers.oci.openai_compat import (
    OCIChatCompletionsModel,
    fold_leading_system_into_first_user,
)


_TOOLS = [{"type": "function", "function": {"name": "add", "parameters": {"type": "object"}}}]


def _model(name: str) -> OCIChatCompletionsModel:
    return OCIChatCompletionsModel(
        model=name,
        auth_type="instance_principal",
        compartment_id="ocid1.compartment.oc1..test",
    )


class TestFold:
    def test_system_is_prepended_to_first_user(self) -> None:
        msgs = [Message.system("Be terse."), Message.user("Add 1 and 2.")]
        out = fold_leading_system_into_first_user(msgs)
        assert [m.role for m in out] == [Role.USER]
        assert out[0].content == "Be terse.\n\nAdd 1 and 2."
        # input untouched
        assert msgs[0].role == Role.SYSTEM
        assert msgs[1].content == "Add 1 and 2."

    def test_multiple_system_messages_are_merged(self) -> None:
        msgs = [Message.system("A."), Message.system("B."), Message.user("Q")]
        out = fold_leading_system_into_first_user(msgs)
        assert len(out) == 1
        assert out[0].content == "A.\n\nB.\n\nQ"

    def test_history_after_first_user_is_preserved(self) -> None:
        msgs = [
            Message.system("S"),
            Message.user("Q1"),
            Message.assistant("A1"),
            Message.user("Q2"),
        ]
        out = fold_leading_system_into_first_user(msgs)
        assert [m.role for m in out] == [Role.USER, Role.ASSISTANT, Role.USER]
        assert out[0].content == "S\n\nQ1"
        assert out[2].content == "Q2"

    def test_no_leading_system_is_a_no_op(self) -> None:
        msgs = [Message.user("Q"), Message.system("late")]
        assert fold_leading_system_into_first_user(msgs) is msgs

    def test_no_user_message_is_a_no_op(self) -> None:
        msgs = [Message.system("S"), Message.assistant("A")]
        assert fold_leading_system_into_first_user(msgs) is msgs


class TestScope:
    def test_llama_with_tools_folds(self) -> None:
        m = _model("meta.llama-3.3-70b-instruct")
        out = m._prepare_messages_for_oci([Message.system("S"), Message.user("Q")], _TOOLS)
        assert [x.role for x in out] == [Role.USER]

    def test_llama_without_tools_is_untouched(self) -> None:
        m = _model("meta.llama-3.3-70b-instruct")
        msgs = [Message.system("S"), Message.user("Q")]
        assert m._prepare_messages_for_oci(msgs, None) is msgs

    def test_other_vendors_are_untouched(self) -> None:
        m = _model("openai.gpt-oss-120b")
        msgs = [Message.system("S"), Message.user("Q")]
        assert m._prepare_messages_for_oci(msgs, _TOOLS) is msgs
