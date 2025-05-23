"""
Sales Intelligence Agent

A specialized agent for finding targeted business contacts and companies using Exa websets.
Perfect for sales prospecting, lead generation, and market intelligence.
"""

from .agent import (
    SalesIntelligenceResponse,
    SalesTarget,
    find_marketing_agencies,
    find_sales_leaders,
    find_startup_executives,
    sales_intelligence_agent,
)

__all__ = [
    "sales_intelligence_agent",
    "find_sales_leaders",
    "find_marketing_agencies",
    "find_startup_executives",
    "SalesTarget",
    "SalesIntelligenceResponse"
]
