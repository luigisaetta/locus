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
    fold_schema_enums,
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


class TestFoldSchemaEnums:
    def test_enum_moves_into_description_and_type_stays(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": ["ANSWER", "PLAN"],
                    "description": "What to do",
                },
            },
        }
        out = fold_schema_enums(schema)
        prop = out["properties"]["intent"]
        assert "enum" not in prop
        assert prop["type"] == "string"
        assert prop["description"] == 'What to do Allowed values: "ANSWER", "PLAN".'
        # The input is not mutated.
        assert "enum" in schema["properties"]["intent"]

    def test_const_is_folded_and_type_defaults_to_string(self) -> None:
        out = fold_schema_enums({"const": "fixed"})
        assert out == {"description": 'Allowed values: "fixed".', "type": "string"}

    def test_nested_arrays_and_anyof_are_walked(self) -> None:
        schema = {
            "anyOf": [
                {"type": "array", "items": {"type": "integer", "enum": [1, 2]}},
                {"type": "null"},
            ]
        }
        out = fold_schema_enums(schema)
        items = out["anyOf"][0]["items"]
        assert "enum" not in items and items["description"] == "Allowed values: 1, 2."
        assert out["anyOf"][1] == {"type": "null"}

    def test_non_dict_passthrough(self) -> None:
        assert fold_schema_enums("x") == "x"
        assert fold_schema_enums(None) is None

    def test_unsupported_validation_keywords_are_dropped(self) -> None:
        schema = {
            "type": "object",
            "title": "Goal",
            "additionalProperties": False,
            "properties": {
                "n": {"type": "integer", "minimum": 0, "maximum": 9, "default": 1},
                "s": {"type": "string", "pattern": "^a", "format": "uuid", "maxLength": 8},
                "title": {"type": "string"},
            },
            "required": ["n"],
        }
        out = fold_schema_enums(schema)
        assert out == {
            "type": "object",
            "properties": {
                "n": {"type": "integer"},
                "s": {"type": "string"},
                "title": {"type": "string"},
            },
            "required": ["n"],
        }


class TestGeminiResponseFormatAndTools:
    _RF = {
        "type": "json_schema",
        "json_schema": {
            "name": "Goal",
            "schema": {
                "type": "object",
                "properties": {"k": {"type": "string", "enum": ["a", "b"]}},
            },
        },
    }

    def test_gemini_response_format_loses_enum(self) -> None:
        m = _model("google.gemini-2.5-flash")
        out = m._munge_response_format_for_gemini({"response_format": self._RF})
        prop = out["response_format"]["json_schema"]["schema"]["properties"]["k"]
        assert "enum" not in prop and "Allowed values" in prop["description"]

    def test_openai_response_format_is_untouched(self) -> None:
        m = _model("openai.gpt-4.1")
        kwargs = {"response_format": self._RF}
        assert m._munge_response_format_for_gemini(kwargs) is kwargs

    def test_gemini_tool_parameters_lose_enum_but_openai_keep_it(self) -> None:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "set_mode",
                    "parameters": {
                        "type": "object",
                        "properties": {"mode": {"type": "string", "enum": ["fast", "slow"]}},
                    },
                },
            }
        ]
        gem = _model("google.gemini-2.5-flash")._sanitize_tools_for_oci(tools)
        assert "enum" not in gem[0]["function"]["parameters"]["properties"]["mode"]
        oai = _model("openai.gpt-4.1")._sanitize_tools_for_oci(tools)
        assert oai[0]["function"]["parameters"]["properties"]["mode"]["enum"] == ["fast", "slow"]
