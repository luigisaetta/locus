# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Model providers for Locus.

Native providers (direct API connections):
   - ``OpenAIModel`` — OpenAI (GPT); also fronts OpenAI-compatible gateways via ``base_url``
   - ``AnthropicModel`` — Anthropic (Claude)

Hosted providers (OCI Generative AI):
   - ``OCIChatCompletionsModel`` — OpenAI-compatible ``/openai/v1`` transport
     (OpenAI, Meta, xAI, Mistral, Gemini and non-R Cohere models on OCI).
   - ``OCIModel`` — OCI SDK transport against ``/20231130/actions/v1``
     (Cohere R-series, Dedicated AI Cluster endpoints).
   - ``OCIResponsesModel`` — opt-in server-stateful Responses API transport.

Usage:
    # Direct class
    from locus.models import OpenAIModel
    model = OpenAIModel(model="gpt-4o")

    from locus.models import AnthropicModel
    model = AnthropicModel(model="claude-sonnet-4-6")

    # OCI GenAI — V1 transport
    from locus.models import OCIChatCompletionsModel
    model = OCIChatCompletionsModel(model="openai.gpt-5", profile="DEFAULT")

    # String factory — "provider:model"
    from locus.models import get_model
    model = get_model("anthropic:claude-sonnet-4-6")
    model = get_model("oci:openai.gpt-5", profile="DEFAULT")

Provider failover — ``FallbackChain`` (see :mod:`locus.models.fallback`)::

    from locus.models import FallbackChain

    model = FallbackChain(
        [get_model("anthropic:claude-sonnet-4-6"), get_model("openai:gpt-4o")]
    )
"""

from locus.models.base import (
    ModelConfig,
    ModelProtocol,
    ModelResponse,
    RequestBuilder,
    ResponseParser,
)
from locus.models.registry import get_model, list_providers, register_provider


__all__ = [
    # Protocols
    "ModelProtocol",
    "RequestBuilder",
    "ResponseParser",
    # Base classes
    "ModelConfig",
    "ModelResponse",
    # Registry
    "get_model",
    "list_providers",
    "register_provider",
    # Failover (lazy imports)
    "CircuitBreaker",
    "FallbackChain",
    # Native providers (lazy imports)
    "OpenAIModel",
    "OpenAIConfig",
    "AnthropicModel",
    "AnthropicConfig",
    # OCI GenAI (lazy imports)
    "OCIModel",
    "OCIConfig",
    "OCIAuthType",
    "OCIChatCompletionsModel",
    "OCIChatCompletionsConfig",
    "OCIResponsesModel",
    "OCIResponsesConfig",
]


def __getattr__(name: str) -> object:
    """Lazy import providers to avoid requiring all dependencies."""
    if name in ("FallbackChain", "CircuitBreaker"):
        from locus.models import fallback

        return getattr(fallback, name)

    if name in ("OpenAIModel", "OpenAIConfig"):
        from locus.models.native.openai import OpenAIConfig, OpenAIModel

        return OpenAIModel if name == "OpenAIModel" else OpenAIConfig

    if name in ("AnthropicModel", "AnthropicConfig"):
        from locus.models.native.anthropic import AnthropicConfig, AnthropicModel

        return AnthropicModel if name == "AnthropicModel" else AnthropicConfig

    # OCI GenAI — needs the ``oci`` extra; resolved lazily so importing
    # ``locus.models`` never pulls the OCI SDK in.
    if name in (
        "OCIModel",
        "OCIConfig",
        "OCIAuthType",
        "OCIChatCompletionsModel",
        "OCIChatCompletionsConfig",
        "OCIResponsesModel",
        "OCIResponsesConfig",
    ):
        from locus.models.providers import oci

        return getattr(oci, name)

    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
