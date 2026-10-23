# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at
# https://oss.oracle.com/licenses/upl/
"""Tool arguments are coerced to the declared parameter types before the call.

Llama on OCI sends ``{"a": "17", "b": "25"}`` for two ``int`` parameters;
without coercion ``add`` returned ``"1725"``.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import BaseModel

from locus.tools import tool
from locus.tools.context import ToolContext


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@tool
def scale(x: float, flag: bool) -> str:
    """Scale."""
    return f"{x * 2}:{flag}"


@tool
def total(values: list[int]) -> int:
    """Sum a list."""
    return sum(values)


@tool
def maybe(n: int | None = None) -> str:
    """Optional."""
    return "none" if n is None else str(n * 2)


class Point(BaseModel):
    x: int
    y: int


@tool
def norm(p: Point) -> int:
    """Model param."""
    return p.x + p.y


@tool
def shout(text: str) -> str:
    """String param."""
    return text.upper()


@tool
def loose(value: Any, untyped=None) -> str:  # noqa: ANN001
    """Untyped params are passed through untouched."""
    return f"{type(value).__name__}:{type(untyped).__name__}"


@tool
def with_ctx(a: int, ctx: ToolContext | None = None) -> str:
    """Context slot is left alone."""
    return f"{a * 2}:{type(ctx).__name__}"


async def test_numeric_strings_become_ints():
    assert await add.execute(a="17", b="25") == "42"


async def test_float_and_bool_strings():
    assert await scale.execute(x="2.5", flag="true") == "5.0:True"


async def test_json_string_becomes_list():
    assert await total.execute(values="[1, 2, 3]") == "6"


async def test_optional_accepts_none_and_strings():
    assert await maybe.execute(n=None) == "none"
    assert await maybe.execute(n="21") == "42"


async def test_dict_becomes_the_declared_model():
    assert await norm.execute(p={"x": "1", "y": 2}) == "3"


async def test_numbers_handed_to_a_str_parameter_are_stringified():
    assert await shout.execute(text=42) == "42"


async def test_unparseable_values_pass_through_unchanged():
    # The tool itself decides what to do with a bad value, as before.
    with pytest.raises(TypeError):
        await add.execute(a="seventeen", b=25)


async def test_untyped_and_any_parameters_are_untouched():
    assert await loose.execute(value="7", untyped="8") == "str:str"


async def test_context_slot_is_untouched():
    assert await with_ctx.execute(a="4") == "8:NoneType"
