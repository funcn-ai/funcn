from __future__ import annotations

import asyncio
from duckduckgo_search import DDGS

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field


class SearchArgs(BaseModel):
    """Arguments for web search."""

    query: str = Field(..., description="Search query to find relevant web pages")
    max_results: int = Field(default=5, description="Maximum number of search results to return")


class SearchResult(BaseModel):
    """A single search result."""

    title: str
    url: str
    snippet: str


class SearchResponse(BaseModel):
    """Response from web search containing multiple results."""

    results: list[SearchResult]
    query: str
    provider: str


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def duckduckgo_search(args: SearchArgs) -> SearchResponse:
    """Search the web using DuckDuckGo and return structured results.

    This function provides a clean interface to DuckDuckGo search functionality.
    """
    try:
        results = []

        # Run DuckDuckGo search in a thread to avoid blocking
        def _search():
            with DDGS() as ddgs:
                search_results = ddgs.text(args.query, max_results=args.max_results)
                return list(search_results)

        raw_results = await asyncio.to_thread(_search)

        for result in raw_results:
            results.append(SearchResult(
                title=result.get("title", ""),
                url=result.get("href", ""),
                snippet=result.get("body", "")
            ))

        return SearchResponse(
            results=results,
            query=args.query,
            provider="duckduckgo"
        )

    except ImportError:
        # Fallback if duckduckgo_search is not available
        return SearchResponse(
            results=[SearchResult(
                title=f"Search for: {args.query}",
                url="",
                snippet="DuckDuckGo search library not available. Please install 'duckduckgo-search' package."
            )],
            query=args.query,
            provider="duckduckgo"
        )
    except Exception as e:
        return SearchResponse(
            results=[SearchResult(
                title=f"Search Error for: {args.query}",
                url="",
                snippet=f"Error performing search: {str(e)}"
            )],
            query=args.query,
            provider="duckduckgo"
        )
