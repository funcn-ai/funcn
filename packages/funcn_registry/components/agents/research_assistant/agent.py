from __future__ import annotations

from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

# Import Exa search tools
try:
    from exa_search_tools import AnswerArgs, ExaCategory, SearchArgs, exa_answer, exa_search
except ImportError:
    # Fallback imports for when tools aren't available yet
    ExaCategory = None
    SearchArgs = None
    exa_search = None
    exa_answer = None
    AnswerArgs = None


# Response models for structured outputs
class SearchQuery(BaseModel):
    """A single search query for research."""
    query: str = Field(..., description="The search query to execute")
    search_type: str = Field(default="auto", description="Type of search: 'auto', 'keyword', or 'neural'")
    category: ExaCategory | None = Field(default=None, description="Optional category for more targeted results")


class SearchQueriesResponse(BaseModel):
    """Response containing generated search queries."""
    queries: list[SearchQuery] = Field(..., description="List of search queries to execute")


class ResearchSection(BaseModel):
    """A section of the research report."""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    sources_used: list[str] = Field(default_factory=list, description="URLs of sources used in this section")


class ResearchReportResponse(BaseModel):
    """Complete research report response."""
    title: str = Field(..., description="Report title")
    executive_summary: str = Field(..., description="Executive summary of findings")
    sections: list[ResearchSection] = Field(..., description="Report sections")
    all_sources: list[str] = Field(..., description="All unique sources used")
    word_count: int = Field(..., description="Total word count of the report")


# Step 1: Generate search queries
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=SearchQueriesResponse,
)
@prompt_template(
    """
    You are a research expert planning searches for a comprehensive report on a topic.

    Topic: {topic}
    Research depth: {depth}

    Generate diverse search queries that will help create a comprehensive research report.
    Consider different angles and aspects of the topic:
    - Basic definitions and concepts
    - Current state and recent developments
    - Key players and organizations
    - Challenges and opportunities
    - Future trends and predictions
    - Case studies and examples

    For each query, determine:
    1. The search query text
    2. Whether to use 'auto', 'keyword', or 'neural' search
    3. If applicable, a category (company, research_paper, news, etc.)

    Generate {num_queries} diverse queries.
    """
)
async def generate_search_queries(
    topic: str,
    depth: str = "comprehensive",
    num_queries: int = 5
):
    """Generate diverse search queries for research."""
    pass


# Step 2: Search and collect information
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    tools=[exa_search, exa_answer] if exa_search else [],
)
@prompt_template(
    """
    You are a research assistant collecting information on a topic.

    Topic: {topic}
    Search queries to execute: {queries}

    For each query:
    1. Use exa_search with the appropriate parameters
    2. If you need direct answers to specific questions, use exa_answer
    3. Collect comprehensive information from multiple sources

    Focus on:
    - Authoritative and recent sources
    - Diverse perspectives
    - Factual, verifiable information
    - Primary sources when possible

    Execute all searches and collect the results.
    """
)
async def collect_research_data(
    topic: str,
    queries: str
):
    """Collect research data using Exa search."""
    pass


# Step 3: Synthesize research report
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=ResearchReportResponse,
)
@prompt_template(
    """
    You are an expert research writer creating a comprehensive report.

    Topic: {topic}
    Research data collected: {research_data}
    Report style: {style}
    Target audience: {audience}

    Create a well-structured research report with:

    1. **Title**: Clear, descriptive title

    2. **Executive Summary**: 2-3 paragraph overview of key findings

    3. **Sections**: Organize into logical sections such as:
       - Background/Introduction
       - Current State/Overview
       - Key Findings
       - Analysis/Discussion
       - Future Outlook/Trends
       - Conclusions/Recommendations

    4. **Citations**: Include source URLs for all claims and data

    Guidelines:
    - Write in {style} style for {audience} audience
    - Use clear, concise language
    - Support all claims with sources
    - Maintain objectivity and balance
    - Include specific examples and data points
    - Ensure logical flow between sections

    Create a comprehensive report of approximately {target_words} words.
    """
)
async def synthesize_research_report(
    topic: str,
    research_data: str,
    style: str,
    audience: str,
    target_words: int
):
    """Synthesize collected data into a research report."""
    pass


async def research_topic(
    topic: str,
    depth: str = "comprehensive",
    style: str = "professional",
    audience: str = "general business",
    num_queries: int = 5,
    target_words: int = 1000,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini"
) -> ResearchReportResponse:
    """
    Research a topic and generate a comprehensive report.

    This agent performs systematic research by:
    1. Generating diverse search queries
    2. Collecting information using Exa's AI-powered search
    3. Synthesizing findings into a structured report

    Args:
        topic: The topic to research
        depth: Research depth - "quick", "standard", or "comprehensive"
        style: Writing style - "professional", "academic", "casual", or "technical"
        audience: Target audience - "general", "technical", "executive", etc.
        num_queries: Number of search queries to generate
        target_words: Target word count for the report
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        ResearchReportResponse with the complete research report
    """
    # Step 1: Generate search queries
    queries_response = await generate_search_queries(
        topic=topic,
        depth=depth,
        num_queries=num_queries
    )

    # Convert queries to string for the next step
    queries_str = "\n".join([
        f"- {q.query} (type: {q.search_type}, category: {q.category})"
        for q in queries_response.queries
    ])

    # Step 2: Collect research data
    research_data = await collect_research_data(
        topic=topic,
        queries=queries_str
    )

    # Step 3: Synthesize report
    report = await synthesize_research_report(
        topic=topic,
        research_data=str(research_data),
        style=style,
        audience=audience,
        target_words=target_words
    )

    return report


# Convenience functions for common research tasks
async def research_company(company_name: str, **kwargs) -> ResearchReportResponse:
    """
    Research a specific company.

    Optimized for company research with focus on:
    - Business model and products/services
    - Market position and competitors
    - Financial performance
    - Leadership and culture
    - Recent news and developments
    """
    return await research_topic(
        topic=f"{company_name} company analysis",
        depth="comprehensive",
        style="professional",
        audience="business executives",
        **kwargs
    )


async def research_technology(technology: str, **kwargs) -> ResearchReportResponse:
    """
    Research a technology or technical topic.

    Optimized for technology research with focus on:
    - Technical specifications and capabilities
    - Use cases and applications
    - Advantages and limitations
    - Market adoption and trends
    - Future developments
    """
    return await research_topic(
        topic=f"{technology} technology deep dive",
        depth="comprehensive",
        style="technical",
        audience="technical professionals",
        **kwargs
    )


async def research_market(market_or_industry: str, **kwargs) -> ResearchReportResponse:
    """
    Research a market or industry.

    Optimized for market research with focus on:
    - Market size and growth
    - Key players and market share
    - Trends and drivers
    - Challenges and opportunities
    - Future outlook
    """
    return await research_topic(
        topic=f"{market_or_industry} market analysis",
        depth="comprehensive",
        style="professional",
        audience="business strategists",
        **kwargs
    )


async def quick_research_summary(topic: str) -> dict[str, Any]:
    """
    Generate a quick research summary on any topic.

    Returns a simplified dictionary with:
    - summary: Brief overview of the topic
    - key_points: List of main findings
    - sources: List of source URLs
    """
    report = await research_topic(
        topic=topic,
        depth="quick",
        num_queries=3,
        target_words=500
    )

    return {
        "summary": report.executive_summary,
        "key_points": [section.title for section in report.sections],
        "sources": report.all_sources,
        "word_count": report.word_count
    }
