# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""The dependency gate for the MCP loopback-server test modules.

Call :func:`require_server_deps` at the top of a module that drives the real
server in ``_mcp_loopback_server.py``. Locally a missing ``mcp``/``uvicorn``
skips the module; with ``LOCUS_REQUIRE_MCP_SERVER_TESTS`` set (CI's full-deps
jobs) it fails collection instead. The gate exists because these modules once
skipped silently on every CI job after the resolver moved to mcp 2.x, which
has no ``mcp.server.fastmcp``.
"""

from __future__ import annotations

import importlib
import os
from types import ModuleType

import pytest


REQUIRE_ENV = "LOCUS_REQUIRE_MCP_SERVER_TESTS"


def require_server_deps() -> ModuleType:
    """Import ``mcp`` and ``uvicorn``; return ``uvicorn``."""
    if os.environ.get(REQUIRE_ENV):
        importlib.import_module("mcp")
        return importlib.import_module("uvicorn")
    pytest.importorskip("mcp")
    return pytest.importorskip("uvicorn")
