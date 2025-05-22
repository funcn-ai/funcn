from __future__ import annotations

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
import random
from pydantic import BaseModel, Field

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my computer I needed a break, and it said 'No problem — I'll go to sleep.'",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
]


class JokeArgs(BaseModel):
    """Arguments for :pyfunc:`tell_joke`. Kept for future extensibility."""

    topic: str | None = Field(
        default=None,
        description="Optional topic to bias the joke selection. Currently unused but reserved for future use.",
    )


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
def tell_joke(args: JokeArgs | None = None) -> str:  # noqa: D401
    """Return a random dad-level programming joke.

    If *args* is provided, we may use additional filters in the future.
    """
    # Currently we disregard the *topic* attribute, but keep the signature future-proof.
    _ = args  # noqa: F841 – accessed for future logic
    return random.choice(JOKES)
