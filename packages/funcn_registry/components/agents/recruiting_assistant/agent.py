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


class CandidateProfile(BaseModel):
    """Candidate profile specification."""

    role: str = Field(..., description="Target role (e.g., 'Engineer', 'SDR', 'ML Engineer')")
    skills: list[str] = Field(default_factory=list, description="Required skills")
    experience: list[str] = Field(default_factory=list, description="Experience requirements")
    education: str | None = Field(None, description="Education requirements")
    location: str | None = Field(None, description="Geographic location preference")
    industry_experience: str | None = Field(None, description="Specific industry experience")
    additional_qualifications: list[str] = Field(default_factory=list, description="Additional qualifications")


class RecruitingSearchResponse(BaseModel):
    """Response from recruiting search."""

    webset_id: str = Field(..., description="ID of the created webset")
    search_query: str = Field(..., description="Search query used")
    candidate_criteria: list[str] = Field(default_factory=list, description="Candidate qualification criteria")
    enrichments: list[str] = Field(default_factory=list, description="Profile enrichments requested")
    estimated_candidates: int | None = Field(None, description="Estimated number of candidates")
    status: str = Field(..., description="Current status of the search")
    search_type: str = Field(..., description="Type of candidate search performed")


@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=RecruitingSearchResponse,
    tools=[create_webset, get_webset_status, list_webset_items] if create_webset else []
)
@prompt_template(
    """
    SYSTEM:
    You are a recruiting assistant specializing in finding qualified candidates using Exa's webset API.
    Current date: {current_date}

    Your capabilities:
    - Create websets to find candidates with specific skills and experience
    - Define precise qualification criteria
    - Request enrichments for professional profiles and portfolios
    - Track open source contributions and professional achievements

    Search Strategy:
    1. Analyze the candidate requirements
    2. Build a comprehensive search query incorporating skills, experience, and qualifications
    3. Define verification criteria to filter qualified candidates
    4. Add enrichments for LinkedIn profiles, GitHub, portfolios, etc.
    5. Create and monitor the webset

    Candidate Types & Strategies:
    - Technical roles: Focus on GitHub profiles, open source contributions, technical blogs
    - Sales roles: Look for LinkedIn profiles with relevant industry experience
    - Academic candidates: Search for research papers, university affiliations, publications
    - Executive roles: Focus on leadership experience, company achievements, board positions

    Enrichment Priorities:
    - LinkedIn profiles (professional history)
    - GitHub profiles (technical contributions)
    - Personal websites/portfolios
    - Publications and research papers
    - Professional certifications

    USER REQUEST:
    Role: {role}
    Required Skills: {skills}
    Experience Requirements: {experience}
    Education: {education}
    Location: {location}
    Industry Experience: {industry_experience}
    Additional Qualifications: {additional_qualifications}

    Create a webset to find candidates matching these requirements.
    """
)
async def recruiting_assistant_agent(
    role: str,
    skills: list[str] | None = None,
    experience: list[str] | None = None,
    education: str | None = None,
    location: str | None = None,
    industry_experience: str | None = None,
    additional_qualifications: list[str] | None = None,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini"
) -> RecruitingSearchResponse:
    """
    Find qualified candidates using Exa websets.

    Args:
        role: Target role or position
        skills: Required technical or soft skills
        experience: Specific experience requirements
        education: Educational background requirements
        location: Geographic location preference
        industry_experience: Specific industry experience needed
        additional_qualifications: Other qualifications or nice-to-haves
        llm_provider: LLM provider to use
        model: Model to use

    Returns:
        Recruiting search response with webset details
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    skills_str = ", ".join(skills) if skills else "Not specified"
    experience_str = "\n".join(experience) if experience else "Not specified"
    additional_str = "\n".join(additional_qualifications) if additional_qualifications else "None"

    # This function should be decorated with @llm.call but mypy needs the return type
    # The actual implementation would use the LLM to create websets and return proper response
    return RecruitingSearchResponse(
        webset_id="placeholder",
        search_query=f"Find {role} candidates",
        candidate_criteria=[
            f"Skills: {skills_str}" if skills_str != "Not specified" else "",
            f"Experience: {experience_str}" if experience_str != "Not specified" else "",
            f"Education: {education}" if education else "",
            f"Location: {location}" if location else "",
            f"Industry: {industry_experience}" if industry_experience else ""
        ],
        enrichments=["linkedin_profiles", "github_profiles", "portfolios"],
        estimated_candidates=None,
        status="pending",
        search_type="candidate_search"
    )


# Convenience functions for common recruiting searches
async def find_engineers_with_opensource(
    skills: list[str],
    startup_experience: bool = True,
    **kwargs
) -> RecruitingSearchResponse:
    """Find engineers with open source contributions."""
    experience = ["startup experience"] if startup_experience else []
    experience.append("contributed to open source projects")

    return await recruiting_assistant_agent(
        role="Engineer",
        skills=skills,
        experience=experience,
        **kwargs
    )


async def find_sales_professionals(
    industry: str,
    location: str,
    role: str = "SDR",
    **kwargs
) -> RecruitingSearchResponse:
    """Find sales professionals with specific industry experience."""
    return await recruiting_assistant_agent(
        role=role,
        industry_experience=f"selling {industry} products",
        location=location,
        experience=[f"experience in {industry} sales"],
        **kwargs
    )


async def find_ml_engineers(
    education_level: str = "PhD",
    university_ranking: str = "top 20 US university",
    **kwargs
) -> RecruitingSearchResponse:
    """Find ML engineers or researchers with strong academic backgrounds."""
    return await recruiting_assistant_agent(
        role="ML Software Engineer or Computer Science PhD student",
        education=f"{education_level} from {university_ranking}",
        skills=["machine learning", "deep learning", "neural networks"],
        **kwargs
    )


async def find_consultants_bankers(
    min_years: int = 2,
    education: str = "Ivy League",
    **kwargs
) -> RecruitingSearchResponse:
    """Find investment bankers or consultants with elite education."""
    return await recruiting_assistant_agent(
        role="Investment Banker or Consultant",
        education=f"attended {education}",
        experience=[f"at their role for over {min_years} years"],
        skills=["financial modeling", "strategic analysis", "client management"],
        **kwargs
    )
