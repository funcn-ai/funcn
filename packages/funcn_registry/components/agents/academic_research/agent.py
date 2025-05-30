from __future__ import annotations

from datetime import datetime
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Literal, Optional

# Import Exa websets tools
try:
    from exa_websets import (
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


ResearchField = Literal[
    "computer_science", "physics", "chemistry", "biology", "medicine",
    "engineering", "mathematics", "economics", "psychology", "sociology",
    "environmental_science", "materials_science", "neuroscience", "other"
]

PublicationVenue = Literal["journal", "conference", "arxiv", "preprint", "thesis", "any"]


class ResearchPaperQuery(BaseModel):
    """Research paper search specification."""

    topic: str = Field(..., description="Research topic or keywords")
    field: ResearchField | None = Field(None, description="Academic field")
    author_requirements: list[str] = Field(default_factory=list, description="Author qualifications (e.g., 'PhD', 'from MIT')")
    publication_venue: PublicationVenue | None = Field("any", description="Type of publication venue")
    journal_requirements: list[str] = Field(default_factory=list, description="Journal requirements (e.g., 'major US journal', 'impact factor > 5')")
    time_period: str | None = Field(None, description="Publication time period")
    methodology_focus: str | None = Field(None, description="Specific methodology or approach")
    citation_threshold: int | None = Field(None, description="Minimum citation count")


class AcademicResearchResponse(BaseModel):
    """Response from academic research search."""

    webset_id: str = Field(..., description="ID of the created webset")
    search_query: str = Field(..., description="Search query used")
    research_field: str = Field(..., description="Academic field searched")
    filters: list[str] = Field(default_factory=list, description="Filters applied to the search")
    enrichments: list[str] = Field(default_factory=list, description="Data enrichments requested")
    estimated_papers: int | None = Field(None, description="Estimated number of papers found")
    publication_types: list[str] = Field(default_factory=list, description="Types of publications included")
    status: str = Field(..., description="Current status of the search")


@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=AcademicResearchResponse,
    tools=[create_webset, get_webset_status, list_webset_items] if create_webset else []
)
@prompt_template(
    """
    SYSTEM:
    You are an academic research assistant specializing in finding research papers using Exa's webset API.
    Current date: {current_date}

    Your capabilities:
    - Find research papers across all academic fields
    - Filter by author credentials and affiliations
    - Track publication venues and impact
    - Identify contrarian or novel research
    - Monitor citation patterns and influence
    - Find related work and research trends

    Search Strategies:

    1. Topic-Based Search:
       - Use precise academic terminology
       - Include synonyms and related concepts
       - Consider interdisciplinary connections
       - Track emerging terminology

    2. Author Filtering:
       - PhD requirements and academic credentials
       - Institutional affiliations
       - Research group memberships
       - Publication history and expertise

    3. Venue Selection:
       - Major journals by field
       - Top-tier conferences
       - Preprint servers (arXiv, bioRxiv, etc.)
       - University repositories

    4. Methodology Focus:
       - Specific research methods or approaches
       - Contrarian viewpoints (papers that "disagree with")
       - Novel techniques or frameworks
       - Reproducibility studies

    5. Impact Metrics:
       - Citation counts and patterns
       - Journal impact factors
       - Altmetric scores
       - Cross-disciplinary influence

    Enrichment Priorities:
    - Full paper metadata (title, authors, abstract)
    - Citation information
    - Author affiliations and credentials
    - Related papers and references
    - PDF links and access information
    - Keywords and classifications

    USER REQUEST:
    Topic: {topic}
    Field: {field}
    Author Requirements: {author_requirements}
    Publication Venue: {publication_venue}
    Journal Requirements: {journal_requirements}
    Time Period: {time_period}
    Methodology Focus: {methodology_focus}
    Citation Threshold: {citation_threshold}

    Create a webset to find research papers matching these criteria.
    """
)
async def academic_research_agent(
    topic: str,
    field: ResearchField | None = None,
    author_requirements: list[str] | None = None,
    publication_venue: PublicationVenue | None = "any",
    journal_requirements: list[str] | None = None,
    time_period: str | None = None,
    methodology_focus: str | None = None,
    citation_threshold: int | None = None,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini"
) -> AcademicResearchResponse:
    """
    Find academic research papers using Exa websets.

    Args:
        topic: Research topic or keywords
        field: Academic field
        author_requirements: Author qualifications
        publication_venue: Type of publication venue
        journal_requirements: Journal requirements
        time_period: Publication time period
        methodology_focus: Specific methodology or approach
        citation_threshold: Minimum citation count
        llm_provider: LLM provider to use
        model: Model to use

    Returns:
        Academic research response with webset details
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    author_reqs = "\n".join(author_requirements) if author_requirements else "Any authors"
    journal_reqs = "\n".join(journal_requirements) if journal_requirements else "Any journals"
    citation_req = f"Minimum {citation_threshold} citations" if citation_threshold else "Any citation count"
    ...


# Convenience functions for common research searches
async def find_papers_by_methodology(
    field: ResearchField,
    methodology: str,
    disagree_with: str | None = None,
    **kwargs
) -> AcademicResearchResponse:
    """Find papers focused on specific methodologies or contrarian views."""
    topic = f"{methodology} in {field}"
    if disagree_with:
        topic = f"papers that disagree with {disagree_with} methodology"

    return await academic_research_agent(
        topic=topic,
        field=field,
        methodology_focus=methodology,
        **kwargs
    )


async def find_papers_by_author_credentials(
    topic: str,
    author_degree: str = "PhD",
    institution_type: str | None = None,
    **kwargs
) -> AcademicResearchResponse:
    """Find papers by authors with specific credentials."""
    author_reqs = [f"author with {author_degree}"]
    if institution_type:
        author_reqs.append(f"from {institution_type}")

    return await academic_research_agent(
        topic=topic,
        author_requirements=author_reqs,
        **kwargs
    )


async def find_high_impact_papers(
    topic: str,
    field: ResearchField,
    min_citations: int = 100,
    journal_tier: str = "top tier",
    **kwargs
) -> AcademicResearchResponse:
    """Find highly cited papers in top journals."""
    return await academic_research_agent(
        topic=topic,
        field=field,
        journal_requirements=[f"published in {journal_tier} journal"],
        citation_threshold=min_citations,
        **kwargs
    )


async def find_emerging_research(
    field: ResearchField,
    year: int = 2024,
    venue: PublicationVenue = "arxiv",
    **kwargs
) -> AcademicResearchResponse:
    """Find recent research in emerging areas."""
    return await academic_research_agent(
        topic=f"emerging research in {field}",
        field=field,
        publication_venue=venue,
        time_period=f"published in {year}",
        **kwargs
    )
