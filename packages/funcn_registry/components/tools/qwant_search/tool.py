from __future__ import annotations

import httpx

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field


class SearchArgs(BaseModel):
    """Arguments for web search."""

    query: str = Field(..., description="Search query to find relevant web pages")
    max_results: int = Field(default=5, description="Maximum number of search results to return")
    locale: str = Field(default="en_US", description="Locale for search results (e.g., en_US, fr_FR)")


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
async def qwant_search(args: SearchArgs) -> SearchResponse:
    """Search the web using Qwant and return structured results.

    Qwant is a privacy-focused search engine that doesn't track users.
    This provides an alternative to DuckDuckGo for web searches.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Qwant API endpoint for web search
            url = "https://api.qwant.com/v3/search/web"
            params: dict[str, str | int] = {
                "q": args.query,
                "count": min(args.max_results, 10),  # Qwant limits to 10 results per request
                "locale": args.locale,
                "safesearch": 1,  # Enable safe search
                "freshness": "all"
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            results = []

            if "data" in data and "result" in data["data"] and "items" in data["data"]["result"]:
                items = data["data"]["result"]["items"]

                for item in items[:args.max_results]:
                    if item.get("type") == "web":  # Only include web results
                        results.append(SearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=item.get("desc", "")
                        ))

            return SearchResponse(
                results=results,
                query=args.query,
                provider="qwant"
            )

    except Exception as e:
        # Fallback to a single error result
        return SearchResponse(
            results=[SearchResult(
                title=f"Search Error for: {args.query}",
                url="",
                snippet=f"Error performing Qwant search: {str(e)}"
            )],
            query=args.query,
            provider="qwant"
        )
