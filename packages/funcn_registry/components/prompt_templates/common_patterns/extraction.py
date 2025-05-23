"""
Extraction patterns using Mirascope.

Common patterns for extracting structured information from unstructured text,
including entities, relationships, and key information.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field
from typing import Any, Optional

# Entity extraction

class Entity(BaseModel):
    """Model for an extracted entity."""

    text: str = Field(..., description="Entity text as found")
    type: str = Field(..., description="Entity type")
    normalized: str = Field(..., description="Normalized form")
    context: str = Field(..., description="Surrounding context")
    confidence: float = Field(..., ge=0, le=1, description="Extraction confidence")


class EntitiesExtracted(BaseModel):
    """Model for entity extraction results."""

    entities: list[Entity] = Field(..., description="All extracted entities")
    entity_types_found: list[str] = Field(..., description="Types of entities found")
    total_count: int = Field(..., description="Total entities extracted")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=EntitiesExtracted)
@prompt_template(
    """
    Extract all entities from this text:

    {text}

    Entity types to extract: {entity_types:list}

    For each entity provide:
    - Exact text as it appears
    - Entity type
    - Normalized form (e.g., "NYC" -> "New York City")
    - Surrounding context
    - Confidence score

    Include all instances, even repeated entities.
    """
)
def extract_entities(
    text: str,
    entity_types: list[str] = None
):
    """
    Extract named entities from text.

    Args:
        text: Text to extract from
        entity_types: Types of entities to extract

    Returns:
        EntitiesExtracted with all entities
    """
    if entity_types is None:
        entity_types = ["person", "organization", "location", "date", "amount", "product"]
    pass


# Relationship extraction

class Relationship(BaseModel):
    """Model for an extracted relationship."""

    subject: str = Field(..., description="Subject entity")
    subject_type: str = Field(..., description="Subject entity type")
    predicate: str = Field(..., description="Relationship type")
    object: str = Field(..., description="Object entity")
    object_type: str = Field(..., description="Object entity type")
    confidence: float = Field(..., ge=0, le=1, description="Relationship confidence")
    evidence: str = Field(..., description="Supporting text")


class RelationshipsExtracted(BaseModel):
    """Model for relationship extraction results."""

    relationships: list[Relationship] = Field(..., description="Extracted relationships")
    entities_involved: list[str] = Field(..., description="All entities in relationships")
    relationship_types: list[str] = Field(..., description="Types of relationships found")


@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=RelationshipsExtracted,
    call_params={"temperature": 0.2}
)
@prompt_template(
    """
    Extract relationships between entities in this text:

    {text}

    Focus on relationship types: {relationship_types:list}

    For each relationship identify:
    - Subject (who/what)
    - Predicate (relationship type)
    - Object (to whom/what)
    - Entity types
    - Supporting evidence from text

    Only extract clear, stated relationships.
    """
)
def extract_relationships(
    text: str,
    relationship_types: list[str] = None
):
    """
    Extract entity relationships from text.

    Args:
        text: Text to analyze
        relationship_types: Types of relationships to find

    Returns:
        RelationshipsExtracted with entity relationships
    """
    if relationship_types is None:
        relationship_types = ["works_for", "located_in", "owns", "created", "partners_with"]
    pass


# Key points extraction

class KeyPoint(BaseModel):
    """Model for a key point."""

    point: str = Field(..., description="The key point")
    category: str = Field(..., description="Category of the point")
    importance: float = Field(..., ge=0, le=1, description="Importance score")
    supporting_text: str = Field(..., description="Supporting text from source")
    implications: list[str] = Field(..., description="Implications of this point")


class KeyPointsExtracted(BaseModel):
    """Model for key points extraction."""

    key_points: list[KeyPoint] = Field(..., description="Extracted key points")
    main_theme: str = Field(..., description="Overall main theme")
    point_categories: dict[str, int] = Field(..., description="Count by category")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=KeyPointsExtracted)
@prompt_template(
    """
    Extract key points from this text:

    {text}

    Extraction criteria:
    - Focus: {focus_area}
    - Max points: {max_points}

    For each key point provide:
    1. Clear statement of the point
    2. Category (finding/conclusion/recommendation/fact/opinion)
    3. Importance score (0-1)
    4. Supporting text quote
    5. Implications or significance

    Prioritize most important and actionable points.
    """
)
def extract_key_points(
    text: str,
    focus_area: str = "main ideas",
    max_points: int = 10
):
    """
    Extract key points from text.

    Args:
        text: Text to analyze
        focus_area: Area to focus extraction on
        max_points: Maximum points to extract

    Returns:
        KeyPointsExtracted with prioritized points
    """
    pass


# Structured data extraction

class StructuredData(BaseModel):
    """Model for structured data extraction."""

    data_points: dict[str, Any] = Field(..., description="Extracted data points")
    data_types: dict[str, str] = Field(..., description="Type of each data point")
    confidence_scores: dict[str, float] = Field(..., description="Confidence per field")
    missing_fields: list[str] = Field(..., description="Expected fields not found")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=StructuredData)
@prompt_template(
    """
    Extract structured data from this text:

    {text}

    Schema to extract:
    {schema:lists}

    Instructions:
    - Extract values for each field if present
    - Indicate data type for each value
    - Provide confidence score
    - Note any missing expected fields

    Be precise and extract only explicitly stated information.
    """
)
def extract_structured(
    text: str,
    schema: dict[str, str]
) -> BaseDynamicConfig:
    """
    Extract data according to schema.

    Args:
        text: Text to extract from
        schema: Schema defining fields to extract

    Returns:
        StructuredData with extracted values
    """
    formatted_schema = []
    for field, description in schema.items():
        formatted_schema.append([f"- {field}: {description}"])

    return {
        "computed_fields": {
            "schema": formatted_schema
        }
    }


# Contact information extraction

class ContactInfo(BaseModel):
    """Model for contact information."""

    name: str | None = Field(None, description="Person/organization name")
    email: str | None = Field(None, description="Email address")
    phone: str | None = Field(None, description="Phone number")
    address: str | None = Field(None, description="Physical address")
    website: str | None = Field(None, description="Website URL")
    social_media: dict[str, str] = Field(default_factory=dict, description="Social media handles")
    job_title: str | None = Field(None, description="Job title if mentioned")
    company: str | None = Field(None, description="Company affiliation")


@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=ContactInfo,
    call_params={"temperature": 0.1}
)
@prompt_template(
    """
    Extract contact information from this text:

    {text}

    Look for:
    - Names (person or organization)
    - Email addresses
    - Phone numbers (any format)
    - Physical addresses
    - Websites
    - Social media profiles
    - Job titles
    - Company affiliations

    Only extract clearly stated contact details.
    """
)
def extract_contact_info(text: str):
    """
    Extract contact information from text.

    Args:
        text: Text containing contact details

    Returns:
        ContactInfo with all found contact details
    """
    pass
