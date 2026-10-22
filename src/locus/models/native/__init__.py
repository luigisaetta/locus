# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Native model providers for Locus.

Native providers connect directly to model vendor APIs:
- OpenAI → GPT models (and OpenAI-compatible gateways via ``base_url``)
- Anthropic → Claude models
"""

from locus.models.native.openai import OpenAIConfig, OpenAIModel


__all__ = [
    "OpenAIModel",
    "OpenAIConfig",
    # Anthropic is a lazy import to avoid a hard dependency:
    #   from locus.models.native.anthropic import AnthropicModel
]
