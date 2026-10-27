"""OCI V1 transport: Gemini needs JSON-object tool results.

OCI maps a ``tool`` message onto Gemini's ``function_response.response``, a
protobuf ``Struct``; a bare string or number is rejected with ``400 Invalid
value at 'contents[n].parts[0].function_response.response'``.
``wrap_tool_results_as_objects`` wraps such results as ``{"result": …}`` and
``_prepare_messages_for_oci`` applies it for ``google.*`` models only.
"""

from __future__ import annotations

import json

import pytest


pytest.importorskip("oci")

from locus.core.messages import Message, Role  # noqa: E402
from locus.models.providers.oci.openai_compat import (  # noqa: E402
    OCIChatCompletionsModel,
    wrap_tool_results_as_objects,
)


_TOOLS = [{"type": "function", "function": {"name": "add", "parameters": {"type": "object"}}}]


def _model(name: str) -> OCIChatCompletionsModel:
    return OCIChatCompletionsModel(
        model=name,
        auth_type="instance_principal",
        compartment_id="ocid1.compartment.oc1..test",
    )


def _tool(content: str | None) -> Message:
    return Message(role=Role.TOOL, content=content, tool_call_id="call_1")


class TestWrapToolResults:
    def test_number_is_wrapped_as_parsed_json(self) -> None:
        (out,) = wrap_tool_results_as_objects([_tool("42")])
        assert json.loads(out.content or "") == {"result": 42}

    def test_plain_text_is_wrapped_as_string(self) -> None:
        (out,) = wrap_tool_results_as_objects([_tool("sunny, 21C")])
        assert json.loads(out.content or "") == {"result": "sunny, 21C"}

    def test_json_array_is_wrapped(self) -> None:
        (out,) = wrap_tool_results_as_objects([_tool("[1, 2]")])
        assert json.loads(out.content or "") == {"result": [1, 2]}

    def test_json_object_passes_through_unchanged(self) -> None:
        msg = _tool('{"sum": 42}')
        (out,) = wrap_tool_results_as_objects([msg])
        assert out is msg

    def test_empty_content_is_left_alone(self) -> None:
        msg = _tool(None)
        (out,) = wrap_tool_results_as_objects([msg])
        assert out is msg

    def test_other_roles_are_untouched_and_order_is_kept(self) -> None:
        user = Message.user("17 + 25?")
        assistant = Message(role=Role.ASSISTANT, content="calling add")
        out = wrap_tool_results_as_objects([user, assistant, _tool("42")])
        assert out[0] is user
        assert out[1] is assistant
        assert json.loads(out[2].content or "") == {"result": 42}

    def test_wrapped_message_keeps_tool_call_id(self) -> None:
        (out,) = wrap_tool_results_as_objects([_tool("42")])
        assert out.tool_call_id == "call_1"
        assert out.role is Role.TOOL


class TestPrepareMessagesForGemini:
    def test_gemini_tool_results_are_wrapped(self) -> None:
        m = _model("google.gemini-2.5-flash")
        out = m._prepare_messages_for_oci([Message.user("Q"), _tool("42")], _TOOLS)
        assert json.loads(out[1].content or "") == {"result": 42}

    def test_gemini_wraps_even_without_tools_argument(self) -> None:
        # A history replayed without the tool list still carries tool turns.
        m = _model("google.gemini-2.5-pro")
        out = m._prepare_messages_for_oci([Message.user("Q"), _tool("ok")], None)
        assert json.loads(out[1].content or "") == {"result": "ok"}

    def test_openai_models_are_untouched(self) -> None:
        m = _model("openai.gpt-4.1")
        msgs = [Message.user("Q"), _tool("42")]
        assert m._prepare_messages_for_oci(msgs, _TOOLS) is msgs

    def test_llama_fold_still_applies_without_wrapping(self) -> None:
        m = _model("meta.llama-3.3-70b-instruct")
        out = m._prepare_messages_for_oci(
            [Message.system("S"), Message.user("Q"), _tool("42")], _TOOLS
        )
        assert out[0].role is Role.USER
        assert out[-1].content == "42"
