from __future__ import annotations

import os
from enum import Enum
from exa_py import Exa

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field
from typing import Any, Optional


class ExaCategory(str, Enum):
    """Valid Exa search categories."""
    COMPANY = "company"
    RESEARCH_PAPER = "research paper"
    NEWS = "news"
    LINKEDIN_PROFILE = "linkedin profile"
    GITHUB = "github"
    TWEET = "tweet"
    MOVIE = "movie"
    SONG = "song"
    PERSONAL_SITE = "personal site"
    PDF = "pdf"
    FINANCIAL_REPORT = "financial report"


# Unified search models (compatible with other search providers)
class SearchArgs(BaseModel):
    """Arguments for web search."""

    query: str = Field(..., description="Search query to find relevant web pages")
    max_results: int = Field(default=5, description="Maximum number of search results to return", alias="num_results")
    # Exa-specific optional parameters
    search_type: str = Field(default="auto", description="Type of search: 'auto', 'keyword', or 'neural'")
    category: ExaCategory | None = Field(default=None, description="Focus category for more targeted results")
    start_published_date: str | None = Field(default=None, description="Results published after this date (YYYY-MM-DD)")
    end_published_date: str | None = Field(default=None, description="Results published before this date (YYYY-MM-DD)")
    include_domains: list[str] | None = Field(default=None, description="Domains to include in search")
    exclude_domains: list[str] | None = Field(default=None, description="Domains to exclude from search")

    class Config:
        populate_by_name = True


class SearchResult(BaseModel):
    """A single search result."""

    title: str
    url: str
    snippet: str = Field(default="", description="Text snippet from the result")
    published_date: str | None = Field(default=None)
    author: str | None = Field(default=None)
    score: float | None = Field(default=None, description="Relevance score")


class SearchResponse(BaseModel):
    """Response from web search containing multiple results."""

    results: list[SearchResult]
    query: str
    provider: str
    autoprompt_string: str | None = Field(default=None, description="Exa's suggested query refinement")


# Exa-specific models for advanced features
class FindSimilarArgs(BaseModel):
    """Arguments for finding similar pages."""

    url: str = Field(..., description="URL to find similar pages for")
    max_results: int = Field(default=5, description="Maximum number of similar results", alias="num_results")
    include_domains: list[str] | None = Field(default=None)
    exclude_domains: list[str] | None = Field(default=None)
    category: ExaCategory | None = Field(default=None, description="Focus category for similar page results")
    exclude_source_domain: bool = Field(default=False, description="Exclude results from the same domain as input URL")

    class Config:
        populate_by_name = True


class AnswerArgs(BaseModel):
    """Arguments for Exa's answer API."""

    query: str = Field(..., description="Question to answer")
    include_citations: bool = Field(default=True, description="Include source citations with the answer", alias="text")

    class Config:
        populate_by_name = True


class AnswerCitation(BaseModel):
    """Citation information for an answer."""

    url: str
    title: str | None = None
    published_date: str | None = None
    author: str | None = None
    text: str | None = None


class AnswerResponse(BaseModel):
    """Response from Exa's answer API."""

    answer: str
    citations: list[AnswerCitation] = Field(default_factory=list)
    query: str
    provider: str = "exa"


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def exa_search(args: SearchArgs) -> SearchResponse:
    """Search the web using Exa's AI-powered search.

    Exa provides both neural (semantic) and keyword search capabilities,
    with advanced filtering options and relevance scoring.
    """
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return SearchResponse(
            results=[SearchResult(
                title="API Key Missing",
                url="",
                snippet="EXA_API_KEY environment variable is required. Get your API key from https://exa.ai"
            )],
            query=args.query,
            provider="exa"
        )

    try:
        exa = Exa(api_key)

        # Run synchronous Exa SDK in thread pool
        import asyncio
        def _search():
            return exa.search(
                query=args.query,
                num_results=args.max_results,
                type=args.search_type if args.search_type != "auto" else None,
                category=args.category.value if args.category else None,
                start_published_date=args.start_published_date,
                end_published_date=args.end_published_date,
                include_domains=args.include_domains,
                exclude_domains=args.exclude_domains,
            )

        result = await asyncio.to_thread(_search)

        # Convert to unified format
        results = []
        for item in result.results:
            results.append(SearchResult(
                title=item.title or "",
                url=item.url,
                snippet=getattr(item, 'text', '') or "",  # Exa might include text in basic search
                published_date=item.published_date,
                author=item.author,
                score=item.score
            ))

        return SearchResponse(
            results=results,
            query=args.query,
            provider="exa",
            autoprompt_string=result.autoprompt_string
        )

    except Exception as e:
        return SearchResponse(
            results=[SearchResult(
                title=f"Search Error for: {args.query}",
                url="",
                snippet=f"Error performing Exa search: {str(e)}"
            )],
            query=args.query,
            provider="exa"
        )


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def exa_find_similar(args: FindSimilarArgs) -> SearchResponse:
    """Find pages similar to a given URL using Exa's similarity search.

    This uses Exa's embeddings to find semantically similar content.
    """
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return SearchResponse(
            results=[SearchResult(
                title="API Key Missing",
                url="",
                snippet="EXA_API_KEY environment variable is required"
            )],
            query=f"Similar to: {args.url}",
            provider="exa"
        )

    try:
        exa = Exa(api_key)

        import asyncio
        def _find_similar():
            return exa.find_similar(
                url=args.url,
                num_results=args.max_results,
                include_domains=args.include_domains,
                exclude_domains=args.exclude_domains,
                category=args.category.value if args.category else None,
                exclude_source_domain=args.exclude_source_domain,
            )

        result = await asyncio.to_thread(_find_similar)

        # Convert to unified format
        results = []
        for item in result.results:
            results.append(SearchResult(
                title=item.title or "",
                url=item.url,
                snippet="",  # Basic find_similar doesn't include text
                published_date=item.published_date,
                author=item.author,
                score=item.score
            ))

        return SearchResponse(
            results=results,
            query=f"Similar to: {args.url}",
            provider="exa",
            autoprompt_string=result.autoprompt_string
        )

    except Exception as e:
        return SearchResponse(
            results=[SearchResult(
                title="Error finding similar pages",
                url="",
                snippet=f"Error: {str(e)}"
            )],
            query=f"Similar to: {args.url}",
            provider="exa"
        )


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def exa_answer(args: AnswerArgs) -> AnswerResponse:
    """Get a direct answer to a question using Exa's answer API.

    This combines Exa's search with LLM capabilities to provide
    accurate, sourced answers to questions.
    """
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return AnswerResponse(
            answer="EXA_API_KEY environment variable is required. Get your API key from https://exa.ai",
            citations=[],
            query=args.query
        )

    try:
        exa = Exa(api_key)

        import asyncio
        def _answer():
            return exa.answer(
                query=args.query,
                text=args.include_citations
            )

        result = await asyncio.to_thread(_answer)

        # Convert citations to our format
        citations = []
        if hasattr(result, 'citations'):
            for citation in result.citations:
                citations.append(AnswerCitation(
                    url=citation.url,
                    title=citation.title,
                    published_date=citation.published_date,
                    author=citation.author,
                    text=getattr(citation, 'text', None)
                ))

        return AnswerResponse(
            answer=result.answer,
            citations=citations,
            query=args.query
        )

    except Exception as e:
        return AnswerResponse(
            answer=f"Error getting answer: {str(e)}",
            citations=[],
            query=args.query
        )
