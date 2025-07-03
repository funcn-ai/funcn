"""
Research Assistant Agent

An AI-powered research agent that conducts comprehensive research on any topic by:
1. Generating diverse search queries
2. Collecting information using Exa's AI-powered search
3. Synthesizing findings into a structured report

Provides specialized functions for company research, technology analysis,
market research, and quick summaries.
"""

from .agent import (
    ResearchReportResponse,
    ResearchSection,
    SearchQueriesResponse,
    SearchQuery,
    collect_research_data,
    generate_search_queries,
    quick_research_summary,
    research_company,
    research_market,
    research_technology,
    research_topic,
    synthesize_research_report,
)

__all__ = [
    "research_topic",
    "research_company",
    "research_technology",
    "research_market",
    "quick_research_summary",
    "generate_search_queries",
    "collect_research_data",
    "synthesize_research_report",
    "SearchQuery",
    "SearchQueriesResponse",
    "ResearchSection",
    "ResearchReportResponse",
]
