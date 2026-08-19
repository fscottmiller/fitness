"""MCP server exposed at /mcp.

FastMCP 2.x — not the FastMCP 1.0 bundled inside the `mcp` SDK. No tools are
registered yet; they arrive with the feature issues. What exists now is the
transport and its authentication, mounted by `app.main`.
"""

from fastmcp import FastMCP
from fastmcp.server.http import StarletteWithLifespan

mcp: FastMCP = FastMCP("PR Engine")


def create_mcp_app() -> StarletteWithLifespan:
    """Build the MCP ASGI app.

    `path="/"` because it is mounted under /mcp — FastMCP's own default would
    make the endpoint /mcp/mcp.
    """
    return mcp.http_app(path="/")
