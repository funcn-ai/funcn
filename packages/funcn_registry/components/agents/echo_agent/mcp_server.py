"""MCP server entrypoint for the ``echo_agent``.

This module exists to keep the main ``echo_agent.py`` focused on the agent
implementation itself. It provides a ``run_mcp_server`` helper that can be
used to launch the agent as either a stdio or HTTP/SSE server, following the
Mirascope MCP guidelines.
"""
from __future__ import annotations

from .echo_agent import echo_agent
from mirascope.mcp import start_fastapi_server, start_stdio_server  # type: ignore
from typing import Final

DEFAULT_HOST: Final[str] = "0.0.0.0"
DEFAULT_PORT: Final[int] = 8000


def run_mcp_server(*, mode: str = "stdio", host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:  # noqa: D401
    """Launch the echo_agent as an MCP server.

    Parameters
    ----------
    mode:
        ``"stdio"`` to start a stdio server (default). Use ``"http"`` to start
        an HTTP/SSE server powered by FastAPI.
    host:
        The host interface to bind to when ``mode='http'``. Ignored for stdio.
    port:
        The TCP port to bind to when ``mode='http'``. Ignored for stdio.

    Notes
    -----
    The helper blocks until the server is stopped (i.e., until the stdio
    connection is closed or the HTTP server is shut down).
    """

    try:
        if mode == "stdio":
            # Blocks until the stdio connection is closed.
            start_stdio_server(agent=echo_agent)
        elif mode == "http":
            start_fastapi_server(agent=echo_agent, host=host, port=port)
        else:
            raise ValueError("Unsupported mode for run_mcp_server – use 'stdio' or 'http'.")
    except ModuleNotFoundError as exc:
        # Provide a helpful error message if the MCP extras are missing.
        message = (
            "Mirascope MCP extras are not installed. Install with: "
            "uv pip install \"mirascope[mcp]\""
        )
        raise RuntimeError(message) from exc
