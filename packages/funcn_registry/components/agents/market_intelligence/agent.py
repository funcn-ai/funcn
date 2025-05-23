from __future__ import annotations

from datetime import datetime
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Literal, Optional

# Import Exa websets tools
try:
    from exa_websets_tools import (
        WebsetCriteria,
        WebsetEnrichment,
        WebsetSearchConfig,
        create_webset,
        get_webset_status,
        list_webset_items,
    )
except ImportError:
    # Fallback if tools aren't available yet
    create_webset = None
    get_webset_status = None
    list_webset_items = None
    WebsetSearchConfig = None
    WebsetEnrichment = None
    WebsetCriteria = None


MarketSegment = Literal["fintech", "agrotech", "biotech", "cleantech", "edtech", "healthtech", "proptech", "insurtech", "regtech", "other"]
InvestmentStage = Literal["pre-seed", "seed", "series-a", "series-b", "series-c", "later-stage", "ipo", "acquisition"]


class MarketIntelligenceQuery(BaseModel):
    """Market intelligence search specification."""

    segment: MarketSegment | None = Field(None, description="Market segment to analyze")
    company_type: str | None = Field(None, description="Type of companies to find")
    investment_stage: InvestmentStage | None = Field(None, description="Investment/funding stage")
    time_period: str | None = Field(None, description="Time period for events (e.g., '2024', 'last 6 months')")
    geographic_focus: str | None = Field(None, description="Geographic region of interest")
    investor_criteria: list[str] | None = Field(default_factory=list, description="Specific investor requirements")
    signal_keywords: list[str] | None = Field(default_factory=list, description="Keywords indicating relevant signals")


class MarketIntelligenceResponse(BaseModel):
    """Response from market intelligence search."""

    webset_id: str = Field(..., description="ID of the created webset")
    search_focus: str = Field(..., description="Primary focus of the search")
    search_query: str = Field(..., description="Search query used")
    filters_applied: list[str] = Field(default_factory=list, description="Filters and criteria applied")
    enrichments: list[str] = Field(default_factory=list, description="Data enrichments requested")
    signal_types: list[str] = Field(default_factory=list, description="Types of market signals tracked")
    estimated_results: int | None = Field(None, description="Estimated number of results")
    status: str = Field(..., description="Current status of the search")


@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=MarketIntelligenceResponse,
    tools=[create_webset, get_webset_status, list_webset_items] if create_webset else []
)
@prompt_template(
    """
    SYSTEM:
    You are a market intelligence analyst specializing in investment research using Exa's webset API.
    Current date: {current_date}

    Your capabilities:
    - Track funding rounds and investment activity
    - Monitor company changes (pivots, layoffs, expansions)
    - Identify emerging trends and market signals
    - Find stealth startups and new market entrants
    - Analyze financial reports and company filings
    - Track competitive landscapes

    Search Types & Strategies:

    1. Founder/Leadership Changes:
       - LinkedIn profiles with recent title changes to "Stealth Founder", "Stealth Mode", etc.
       - Track executives leaving major companies
       - Monitor new company registrations

    2. Investment Activity:
       - Companies raising specific rounds (Seed, Series A/B/C)
       - Filter by investor type (major VCs, specific funds)
       - Track investment trends by sector and geography

    3. Company Analysis:
       - Financial reports mentioning key terms (downsizing, expansion, pivot)
       - Technology focus (hardware vs software)
       - Market positioning and competitive advantages

    4. Market Trends:
       - Emerging technologies and solutions
       - Regulatory changes and compliance requirements
       - Industry consolidation and M&A activity

    Enrichment Strategy:
    - Company profiles (size, funding, team)
    - Financial data and reports
    - News coverage and press releases
    - LinkedIn profiles of key personnel
    - Patent filings and technical documentation

    USER REQUEST:
    Market Segment: {segment}
    Company Type: {company_type}
    Investment Stage: {investment_stage}
    Time Period: {time_period}
    Geographic Focus: {geographic_focus}
    Investor Criteria: {investor_criteria}
    Signal Keywords: {signal_keywords}

    Create a webset to track these market intelligence signals.
    """
)
async def market_intelligence_agent(
    segment: MarketSegment | None = None,
    company_type: str | None = None,
    investment_stage: InvestmentStage | None = None,
    time_period: str | None = None,
    geographic_focus: str | None = None,
    investor_criteria: list[str] | None = None,
    signal_keywords: list[str] | None = None,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini"
) -> MarketIntelligenceResponse:
    """
    Track market intelligence and investment opportunities using Exa websets.

    Args:
        segment: Market segment to analyze
        company_type: Type of companies to find
        investment_stage: Investment/funding stage
        time_period: Time period for events
        geographic_focus: Geographic region of interest
        investor_criteria: Specific investor requirements
        signal_keywords: Keywords indicating relevant signals
        llm_provider: LLM provider to use
        model: Model to use

    Returns:
        Market intelligence response with webset details
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    investor_criteria_str = "\n".join(investor_criteria) if investor_criteria else "None specified"
    signal_keywords_str = ", ".join(signal_keywords) if signal_keywords else "None specified"

    return {
        "computed_fields": {
            "current_date": current_date,
            "segment": segment or "All segments",
            "company_type": company_type or "All types",
            "investment_stage": investment_stage or "All stages",
            "time_period": time_period or "All time",
            "geographic_focus": geographic_focus or "Global",
            "investor_criteria": investor_criteria_str,
            "signal_keywords": signal_keywords_str
        }
    }


# Convenience functions for common market intelligence searches
async def track_stealth_founders(
    year: int = 2025,
    **kwargs
) -> MarketIntelligenceResponse:
    """Track LinkedIn profiles that changed to 'Stealth Founder' status."""
    return await market_intelligence_agent(
        signal_keywords=["Stealth Founder", "Stealth Mode", "Building something new"],
        time_period=str(year),
        **kwargs
    )


async def find_funded_startups(
    segment: MarketSegment,
    stage: InvestmentStage,
    year: int = 2024,
    investor_type: str | None = None,
    **kwargs
) -> MarketIntelligenceResponse:
    """Find startups that raised funding in a specific segment."""
    investor_criteria = [f"raised from {investor_type}"] if investor_type else []

    return await market_intelligence_agent(
        segment=segment,
        investment_stage=stage,
        time_period=str(year),
        investor_criteria=investor_criteria,
        **kwargs
    )


async def analyze_company_changes(
    keywords: list[str],
    segment: MarketSegment | None = None,
    **kwargs
) -> MarketIntelligenceResponse:
    """Analyze companies mentioning specific changes in reports."""
    return await market_intelligence_agent(
        segment=segment,
        signal_keywords=keywords,
        company_type="established companies with financial reports",
        **kwargs
    )


async def find_emerging_technologies(
    tech_focus: str,
    hardware_focused: bool = False,
    **kwargs
) -> MarketIntelligenceResponse:
    """Find companies working on emerging technologies."""
    company_type = f"{tech_focus} companies"
    if hardware_focused:
        company_type += " focused on hardware solutions"

    return await market_intelligence_agent(
        company_type=company_type,
        signal_keywords=[tech_focus, "innovation", "breakthrough", "patent"],
        **kwargs
    )
