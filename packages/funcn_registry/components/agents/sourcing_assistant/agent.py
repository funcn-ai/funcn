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


SourcingCategory = Literal["manufacturer", "supplier", "software", "service", "tool", "platform", "solution"]
Industry = Literal["chemical", "textile", "electronics", "automotive", "pharmaceutical", "food", "technology", "logistics", "other"]


class SourcingRequirements(BaseModel):
    """Sourcing requirements specification."""

    product_type: str = Field(..., description="Type of product or service needed")
    category: SourcingCategory = Field(..., description="Category of sourcing")
    specifications: list[str] = Field(default_factory=list, description="Technical specifications")
    location_preference: str | None = Field(None, description="Preferred geographic location")
    sustainability_required: bool = Field(False, description="Whether sustainability is required")
    minimum_order_quantity: str | None = Field(None, description="MOQ requirements")
    certifications: list[str] = Field(default_factory=list, description="Required certifications")
    budget_range: str | None = Field(None, description="Budget range or pricing expectations")


class SourcingSearchResponse(BaseModel):
    """Response from sourcing search."""

    webset_id: str = Field(..., description="ID of the created webset")
    search_query: str = Field(..., description="Search query used")
    sourcing_type: str = Field(..., description="Type of sourcing search performed")
    criteria: list[str] = Field(default_factory=list, description="Qualification criteria applied")
    enrichments: list[str] = Field(default_factory=list, description="Data enrichments requested")
    geographic_scope: str = Field(..., description="Geographic scope of search")
    estimated_suppliers: int | None = Field(None, description="Estimated number of suppliers found")
    status: str = Field(..., description="Current status of the search")


@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=SourcingSearchResponse,
    tools=[create_webset, get_webset_status, list_webset_items] if create_webset else []
)
@prompt_template(
    """
    SYSTEM:
    You are a sourcing assistant specializing in finding suppliers, manufacturers, and solutions using Exa's webset API.
    Current date: {current_date}

    Your capabilities:
    - Find manufacturers and suppliers globally
    - Identify software solutions and platforms
    - Locate service providers and consultants
    - Track sustainability and certification compliance
    - Analyze pricing and MOQ information
    - Evaluate supplier capabilities and reputation

    Sourcing Strategies by Type:

    1. Manufacturers:
       - Search for factory websites and B2B platforms
       - Look for production capabilities and certifications
       - Check MOQ, lead times, and geographic coverage
       - Verify sustainability practices if required

    2. Chemical/Material Suppliers:
       - Focus on safety certifications and compliance
       - Check for sustainability angles and green chemistry
       - Verify supply chain transparency
       - Look for technical specifications match

    3. Software/Technology Solutions:
       - Search for specific features and integrations
       - Check customer reviews and case studies
       - Verify scalability and support options
       - Look for industry-specific solutions

    4. Service Providers:
       - Focus on expertise and track record
       - Check client testimonials and portfolios
       - Verify geographic coverage and availability
       - Look for relevant certifications

    Enrichment Priorities:
    - Company profiles and capabilities
    - Product catalogs and specifications
    - Certifications and compliance documents
    - Customer reviews and testimonials
    - Pricing and MOQ information
    - Contact information and RFQ processes

    USER REQUEST:
    Product Type: {product_type}
    Category: {category}
    Specifications: {specifications}
    Location Preference: {location_preference}
    Sustainability Required: {sustainability_required}
    MOQ Requirements: {moq_requirements}
    Certifications: {certifications}
    Budget Range: {budget_range}

    Create a webset to find suppliers matching these requirements.
    """
)
async def sourcing_assistant_agent(
    product_type: str,
    category: SourcingCategory = "supplier",
    specifications: list[str] | None = None,
    location_preference: str | None = None,
    sustainability_required: bool = False,
    moq_requirements: str | None = None,
    certifications: list[str] | None = None,
    budget_range: str | None = None,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini"
) -> SourcingSearchResponse:
    """
    Find suppliers and solutions using Exa websets.

    Args:
        product_type: Type of product or service needed
        category: Category of sourcing
        specifications: Technical specifications
        location_preference: Preferred geographic location
        sustainability_required: Whether sustainability is required
        moq_requirements: Minimum order quantity requirements
        certifications: Required certifications
        budget_range: Budget range or pricing expectations
        llm_provider: LLM provider to use
        model: Model to use

    Returns:
        Sourcing search response with webset details
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    specs_str = "\n".join(specifications) if specifications else "None specified"
    certs_str = ", ".join(certifications) if certifications else "None required"

    # This function should be decorated with @llm.call but mypy needs the return type
    # The actual implementation would use the LLM to create websets and return proper response
    return SourcingSearchResponse(
        webset_id="placeholder",
        search_query=f"Find {product_type} suppliers",
        sourcing_type=category,
        criteria=[specs_str] if specs_str != "None specified" else [],
        enrichments=["company_profiles", "contact_info"],
        geographic_scope=location_preference or "Global",
        estimated_suppliers=None,
        status="pending"
    )


# Convenience functions for common sourcing searches
async def find_sustainable_manufacturers(
    product_type: str,
    location: str,
    certifications: list[str] | None = None,
    **kwargs
) -> SourcingSearchResponse:
    """Find manufacturers with sustainability focus."""
    certs = certifications or []
    certs.extend(["ISO 14001", "B Corp", "Cradle to Cradle"])

    return await sourcing_assistant_agent(
        product_type=product_type,
        category="manufacturer",
        location_preference=location,
        sustainability_required=True,
        certifications=certs,
        **kwargs
    )


async def find_low_moq_suppliers(
    product_type: str,
    max_moq: str,
    regions: list[str],
    **kwargs
) -> SourcingSearchResponse:
    """Find suppliers with low minimum order quantities."""
    location = " or ".join(regions)

    return await sourcing_assistant_agent(
        product_type=product_type,
        category="supplier",
        location_preference=location,
        moq_requirements=f"Maximum MOQ: {max_moq}",
        specifications=["Low minimum order quantity", "Flexible ordering"],
        **kwargs
    )


async def find_software_solutions(
    solution_type: str,
    features: list[str],
    industry: str | None = None,
    **kwargs
) -> SourcingSearchResponse:
    """Find software solutions with specific features."""
    specs = features.copy()
    if industry:
        specs.append(f"Industry focus: {industry}")

    return await sourcing_assistant_agent(
        product_type=f"{solution_type} software",
        category="software",
        specifications=specs,
        **kwargs
    )


async def find_ai_productivity_tools(
    use_case: str,
    **kwargs
) -> SourcingSearchResponse:
    """Find AI tools for productivity enhancement."""
    return await sourcing_assistant_agent(
        product_type="AI productivity tools",
        category="tool",
        specifications=[
            f"Use case: {use_case}",
            "Agentic AI capabilities",
            "Automation features",
            "Integration capabilities"
        ],
        **kwargs
    )
