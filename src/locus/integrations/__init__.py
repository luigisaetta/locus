# Copyright (c) 2025, 2026 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v1.0 as shown at
# https://oss.oracle.com/licenses/upl/

"""Integrations with external frameworks."""

from locus.integrations.fastmcp import (
    LocusMCPServer,
    MCPClient,
    MCPConnectionError,
    MCPRequestContext,
    MCPToolNotAllowedError,
    MCPToolResult,
    create_mcp_server,
    mcp_tool_to_locus,
)


__all__ = [
    # Consume MCP servers.
    "MCPClient",
    "MCPConnectionError",
    "MCPRequestContext",
    "MCPToolNotAllowedError",
    "MCPToolResult",
    # Expose Locus's own tools and agent as an MCP server.
    "LocusMCPServer",
    "create_mcp_server",
    "mcp_tool_to_locus",
]
