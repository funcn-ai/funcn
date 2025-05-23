"""
Academic Research Agent

A specialized agent for finding research papers using Exa websets.
Perfect for academics, researchers, and anyone needing to discover scholarly publications.
"""

from .agent import (
    AcademicResearchResponse,
    PublicationVenue,
    ResearchField,
    ResearchPaperQuery,
    academic_research_agent,
    find_emerging_research,
    find_high_impact_papers,
    find_papers_by_author_credentials,
    find_papers_by_methodology,
)

__all__ = [
    "academic_research_agent",
    "find_papers_by_methodology",
    "find_papers_by_author_credentials",
    "find_high_impact_papers",
    "find_emerging_research",
    "ResearchPaperQuery",
    "AcademicResearchResponse",
    "ResearchField",
    "PublicationVenue"
]
