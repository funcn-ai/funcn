"""
Market Intelligence Agent

A specialized agent for tracking investment opportunities and market trends using Exa websets.
Perfect for VCs, analysts, and business development professionals.
"""

from .agent import (
    InvestmentStage,
    MarketIntelligenceQuery,
    MarketIntelligenceResponse,
    MarketSegment,
    analyze_company_changes,
    find_emerging_technologies,
    find_funded_startups,
    market_intelligence_agent,
    track_stealth_founders,
)

__all__ = [
    "market_intelligence_agent",
    "track_stealth_founders",
    "find_funded_startups",
    "analyze_company_changes",
    "find_emerging_technologies",
    "MarketIntelligenceQuery",
    "MarketIntelligenceResponse",
    "MarketSegment",
    "InvestmentStage",
]
