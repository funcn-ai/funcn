from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

# SYGALDRY_LILYPAD_IMPORT_PLACEHOLDER
# SYGALDRY_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field


class URLParseArgs(BaseModel):
    """Arguments for URL content parsing."""

    url: str = Field(..., description="URL of the webpage to extract content from")
    max_chars: int = Field(default=8000, description="Maximum number of characters to extract from the page")


# SYGALDRY_LILYPAD_DECORATOR_PLACEHOLDER
async def parse_url_content(args: URLParseArgs) -> str:
    """Extract and return the main textual content from a webpage.

    This function provides a clean interface to URL content parsing,
    extracting the main text content while removing scripts, styles, and other noise.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(args.url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Truncate if needed
            if len(text) > args.max_chars:
                text = text[: args.max_chars] + "..."

            return text

    except Exception as e:
        return f"Error parsing URL {args.url}: {str(e)}"
