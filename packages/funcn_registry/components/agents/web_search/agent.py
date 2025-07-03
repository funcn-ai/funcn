from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional

# Import all available search tools
try:
    from ...tools.duckduckgo_search.tool import SearchArgs, duckduckgo_search
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    duckduckgo_search = None
    SearchArgs = None
    DUCKDUCKGO_AVAILABLE = False

try:
    from ...tools.exa_search.tool import ExaCategory, exa_answer, exa_find_similar, exa_search
    EXA_AVAILABLE = True
except ImportError:
    ExaCategory = None
    exa_search = None
    exa_answer = None
    exa_find_similar = None
    EXA_AVAILABLE = False

try:
    from ...tools.nimble_search.tool import (
        NimbleMapsSearchArgs,
        NimbleSearchArgs,
        NimbleSERPSearchArgs,
        nimble_maps_search,
        nimble_search,
        nimble_serp_search,
    )
    NIMBLE_AVAILABLE = True
except ImportError:
    nimble_search = None
    nimble_serp_search = None
    nimble_maps_search = None
    NimbleSearchArgs = None
    NimbleSERPSearchArgs = None
    NimbleMapsSearchArgs = None
    NIMBLE_AVAILABLE = False

try:
    from ...tools.qwant_search.tool import qwant_search
    QWANT_AVAILABLE = True
except ImportError:
    qwant_search = None
    QWANT_AVAILABLE = False

try:
    from ...tools.url_content_parser.tool import URLParseArgs, parse_url_content
    URL_PARSER_AVAILABLE = True
except ImportError:
    parse_url_content = None
    URLParseArgs = None
    URL_PARSER_AVAILABLE = False


# Unified response model for all search providers
class WebSearchResponse(BaseModel):
    """Structured response for web search agent."""

    answer: str = Field(..., description="Comprehensive answer based on web search results")
    sources: list[str] = Field(default_factory=list, description="URLs of sources used in the answer")
    search_queries: list[str] = Field(default_factory=list, description="Search queries that were performed")
    search_providers: list[str] = Field(
        default_factory=list, description="Search providers used (e.g., duckduckgo, qwant, exa, nimble)"
    )
    privacy_note: str | None = Field(default=None, description="Privacy information if applicable")


# Type for search provider selection
SearchProvider = Literal["duckduckgo", "qwant", "exa", "nimble", "auto", "all"]


def determine_exa_category(question: str) -> ExaCategory | None:
    """Determine the best Exa category based on the question content."""
    if not ExaCategory:
        return None

    question_lower = question.lower()

    # Company information
    if any(term in question_lower for term in ["company", "business", "corporation", "startup", "enterprise", "organization"]):
        return ExaCategory.COMPANY

    # Research papers and academic content
    if any(
        term in question_lower
        for term in ["research", "paper", "study", "academic", "scientific", "journal", "publication", "thesis", "dissertation"]
    ):
        return ExaCategory.RESEARCH_PAPER

    # News and current events
    if any(
        term in question_lower
        for term in ["news", "breaking", "latest", "current events", "headline", "article", "report", "journalism"]
    ):
        return ExaCategory.NEWS

    # LinkedIn profiles
    if any(
        term in question_lower
        for term in ["linkedin", "professional profile", "career", "resume", "cv", "professional background"]
    ):
        return ExaCategory.LINKEDIN_PROFILE

    # GitHub and code repositories
    if any(
        term in question_lower
        for term in ["github", "repository", "repo", "code", "open source", "programming", "developer", "software project"]
    ):
        return ExaCategory.GITHUB

    # Tweets and Twitter content
    if any(term in question_lower for term in ["tweet", "twitter", "x.com", "social media post", "twitter thread"]):
        return ExaCategory.TWEET

    # Movies and film content
    if any(term in question_lower for term in ["movie", "film", "cinema", "documentary", "tv show", "series", "entertainment"]):
        return ExaCategory.MOVIE

    # Songs and music content
    if any(term in question_lower for term in ["song", "music", "album", "artist", "band", "lyrics", "spotify", "audio"]):
        return ExaCategory.SONG

    # Personal websites and blogs
    if any(term in question_lower for term in ["personal site", "blog", "portfolio", "personal website", "personal page"]):
        return ExaCategory.PERSONAL_SITE

    # PDF documents
    if any(term in question_lower for term in ["pdf", "document", "whitepaper", "manual", "guide", "ebook", "report pdf"]):
        return ExaCategory.PDF

    # Financial reports
    if any(
        term in question_lower
        for term in ["financial report", "quarterly report", "annual report", "earnings", "financial statement", "10-k", "10-q"]
    ):
        return ExaCategory.FINANCIAL_REPORT

    return None


def determine_search_strategy(question: str, search_provider: SearchProvider) -> str:
    """Determine the optimal search strategy based on question content and provider preference."""
    if search_provider != "auto":
        return search_provider

    question_lower = question.lower()

    # Location-based queries -> Nimble
    if any(
        term in question_lower
        for term in ["restaurant", "store", "near me", "location", "address", "place", "map", "directions", "local", "nearby"]
    ):
        return "nimble"

    # Exa categories -> Exa
    exa_category = determine_exa_category(question)
    if exa_category:
        return "exa"

    # General semantic/AI queries -> Exa
    if any(
        term in question_lower for term in ["similar to", "like", "semantic", "meaning", "context", "understanding", "analysis"]
    ):
        return "exa"

    # Privacy-sensitive queries could default to Qwant, but for now default to DuckDuckGo
    # Default to DuckDuckGo for general queries
    return "duckduckgo"


# Single unified web search agent using dynamic configuration
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=WebSearchResponse,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert web search agent with access to multiple search providers.
    Current date: {current_date}
    Search history: {search_history}

    Available search tools:
    - `duckduckgo_search`: DuckDuckGo search (general purpose, wide coverage)
    - `qwant_search`: Qwant search (privacy-focused, no user tracking)
    - `exa_search`: Exa AI-powered search (neural/semantic, advanced filtering, relevance scoring)
    - `exa_answer`: Get direct answers with citations (combines search + LLM)
    - `exa_find_similar`: Find pages similar to a given URL
    - `nimble_search`: Nimble Web API for comprehensive web data extraction
    - `nimble_serp_search`: Nimble SERP API for structured search engine results
    - `nimble_maps_search`: Nimble Maps API for location-based searches
    - `parse_url_content`: Extract content from specific URLs

    Search strategy: {search_strategy}
    Locale: {locale}
    Privacy mode: {privacy_mode}

    Instructions:
    1. Based on the search strategy, select appropriate search tools
    2. Generate diverse search queries to explore different aspects of the question
    3. Use the selected search tools to find relevant information
    4. Extract content from the most promising URLs
    5. Synthesize a comprehensive answer with proper source attribution
    6. Include information about which providers were used
    7. If using privacy-focused search, mention the privacy benefits

    Search Strategy Guidelines:
    - "duckduckgo": Use only DuckDuckGo for broad, comprehensive coverage
    - "qwant": Use only Qwant for privacy-focused searching
    - "exa": Use Exa for AI-powered search with neural understanding and direct answers
    - "nimble": Use Nimble APIs for structured data extraction and specialized searches
    - "auto": Automatically select the best provider based on query type
    - "all": Use multiple providers for maximum coverage and validation

    Exa-specific capabilities and categories:
    - Best for: company info, research papers, news, LinkedIn profiles, GitHub repos, tweets, movies, songs, personal sites, PDFs, financial reports
    - Use `exa_answer` for direct Q&A with citations
    - Use `exa_search` with appropriate category for targeted results
    - Use `exa_find_similar` to find related content based on URLs

    Nimble-specific capabilities:
    - Use `nimble_serp_search` for structured search results with titles, snippets, and URLs
    - Use `nimble_maps_search` for location-based queries (restaurants, businesses, places)
    - Use `nimble_search` for general web data extraction with parsing

    Return a structured response with:
    - Complete answer addressing all aspects of the question
    - List of source URLs referenced
    - Search queries performed for transparency
    - Search providers used
    - Privacy note if privacy-focused search was used

    USER: {question}
    ASSISTANT:
    """
)
async def web_search_agent(
    question: str,
    search_provider: SearchProvider = "auto",
    search_history: list[str] | None = None,
    locale: str = "en_US",
    privacy_mode: bool = False,
    max_results_per_search: int = 5,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
    stream: bool = False,
) -> BaseDynamicConfig:
    """
    Unified web search agent using dynamic configuration.

    This agent provides a single interface for web searching while allowing
    users to choose their preferred search strategy, providers, and runtime configuration.

    Args:
        question: The user's question to answer
        search_provider: Which search provider(s) to use
        search_history: Previous searches for context
        locale: Search locale for international results
        privacy_mode: Whether to prioritize privacy-focused search
        max_results_per_search: Maximum results per search query
        llm_provider: LLM provider to use
        model: Specific model to use
        stream: Whether to stream the response

    Returns:
        Dynamic configuration for the web search agent
    """
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    search_history_str = "\n".join(search_history) if search_history else "No previous searches"

    # Determine search strategy based on privacy mode and provider
    if privacy_mode and search_provider == "auto":
        search_strategy = "qwant"
    else:
        search_strategy = determine_search_strategy(question, search_provider)

    # Build the list of available tools
    available_tools = []
    if DUCKDUCKGO_AVAILABLE:
        available_tools.append(duckduckgo_search)
    if QWANT_AVAILABLE:
        available_tools.append(qwant_search)
    if EXA_AVAILABLE:
        available_tools.extend([exa_search, exa_answer, exa_find_similar])
    if NIMBLE_AVAILABLE:
        available_tools.extend([nimble_search, nimble_serp_search, nimble_maps_search])
    if URL_PARSER_AVAILABLE:
        available_tools.append(parse_url_content)

    # Return dynamic configuration
    return {
        "tools": available_tools,
        "call_params": {
            "stream": stream,
        },
        "computed_fields": {
            "current_date": current_date,
            "search_history": search_history_str,
            "search_strategy": search_strategy,
            "locale": locale,
            "privacy_mode": privacy_mode,
            "question": question,
        },
        "metadata": {
            "search_provider": search_provider,
            "max_results": max_results_per_search,
            "llm_provider": llm_provider,
            "model": model,
        },
    }


# Convenience functions remain the same but now use the unified agent
async def web_search_private(question: str, **kwargs) -> WebSearchResponse:
    """Convenience function for privacy-focused search using Qwant."""
    return await web_search_agent(question=question, search_provider="qwant", privacy_mode=True, **kwargs)


async def web_search_comprehensive(question: str, **kwargs) -> WebSearchResponse:
    """Convenience function for comprehensive search using all available providers."""
    return await web_search_agent(question=question, search_provider="all", **kwargs)


async def web_search_fast(question: str, **kwargs) -> WebSearchResponse:
    """Convenience function for fast search using DuckDuckGo."""
    return await web_search_agent(question=question, search_provider="duckduckgo", **kwargs)


async def web_search_ai(question: str, **kwargs) -> WebSearchResponse:
    """Convenience function for AI-powered semantic search using Exa."""
    return await web_search_agent(question=question, search_provider="exa", **kwargs)


async def web_search_structured(question: str, **kwargs) -> WebSearchResponse:
    """Convenience function for structured search using Nimble."""
    return await web_search_agent(question=question, search_provider="nimble", **kwargs)


# Streaming version using the same unified agent with stream=True
async def web_search_agent_stream(question: str, search_provider: SearchProvider = "auto", **kwargs) -> AsyncGenerator[str, None]:
    """
    Streaming version of the unified web search agent.

    Simply calls the main agent with stream=True in the dynamic config.
    """
    async for chunk in await web_search_agent(question=question, search_provider=search_provider, stream=True, **kwargs):
        yield chunk
