from __future__ import annotations

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field


class EchoAgentResponse(BaseModel):
    """Structured response for ``echo_agent``."""

    echoed_text: str = Field(..., description="The input text echoed back to the user, including any prefix.")


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=EchoAgentResponse,
)
@prompt_template(
    """
    SYSTEM: You are an echo assistant. When given user input, you MUST reply with the same text, verbatim, prefixed by the provided ``prefix`` string.

    The reply should include no additional text, explanations, or formatting beyond the prefix and the echoed user input.

    PREFIX: {prefix}
    USER: {user_input}
    ASSISTANT:
    """
)
async def echo_agent(prefix: str, user_input: str) -> None:
    """Echo the ``user_input`` back to the caller."""
    pass


# ---------------------------------------------------------------------------
# MCP server entrypoint
# ---------------------------------------------------------------------------
# MCP server entrypoint has been moved to `mcp_server.py` to keep this
# module focused on the agent implementation.
