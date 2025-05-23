"""
Structured output examples using Mirascope.

Structured output prompting ensures the model returns data in a specific,
predictable format using Pydantic models for validation and type safety.
"""

import lilypad
from datetime import datetime
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field, validator
from typing import Any, Optional

# Basic structured extraction

class PersonInfo(BaseModel):
    """Model for person information extraction."""

    name: str = Field(..., description="Full name of the person")
    age: int | None = Field(None, description="Age if mentioned")
    occupation: str | None = Field(None, description="Job or profession")
    location: str | None = Field(None, description="Location or city")
    key_facts: list[str] = Field(default_factory=list, description="Other important facts")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=PersonInfo)
@prompt_template(
    """
    Extract information about the person from this text:

    {text}

    Return structured data including name, age, occupation, location, and any other key facts.
    """
)
def structured_extraction(text: str):
    """
    Basic structured information extraction.

    Demonstrates:
    1. Simple extraction into typed fields
    2. Optional fields handling
    3. List extraction for variable data

    Args:
        text: Text containing person information

    Returns:
        PersonInfo with extracted data
    """
    pass


# Complex nested structures

class Address(BaseModel):
    """Model for address information."""

    street: str | None = Field(None, description="Street address")
    city: str = Field(..., description="City name")
    state: str | None = Field(None, description="State or province")
    country: str = Field(..., description="Country")
    postal_code: str | None = Field(None, description="Postal or ZIP code")


class Company(BaseModel):
    """Model for company information."""

    name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry sector")
    size: str | None = Field(None, description="Company size (small/medium/large)")
    founded: int | None = Field(None, description="Year founded")
    headquarters: Address | None = Field(None, description="Company headquarters")


class JobPosting(BaseModel):
    """Model for job posting information."""

    title: str = Field(..., description="Job title")
    company: Company = Field(..., description="Company information")
    salary_range: dict[str, float] | None = Field(None, description="Salary range with min/max")
    requirements: list[str] = Field(..., description="Job requirements")
    benefits: list[str] = Field(default_factory=list, description="Job benefits")
    remote: bool = Field(..., description="Whether remote work is allowed")
    posted_date: str | None = Field(None, description="When the job was posted")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=JobPosting)
@prompt_template(
    """
    Extract structured job posting information from this text:

    {job_text}

    Include all available details about the position, company, requirements, and benefits.
    """
)
def structured_generation(job_text: str):
    """
    Complex nested structure generation.

    Features:
    1. Nested Pydantic models
    2. Complex data relationships
    3. Mixed required/optional fields

    Args:
        job_text: Job posting text

    Returns:
        JobPosting with complete structured data
    """
    pass


# Validated structured output

class ProductReview(BaseModel):
    """Model for product review with validation."""

    product_name: str = Field(..., description="Name of the product")
    rating: float = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    pros: list[str] = Field(..., min_length=1, description="Positive aspects")
    cons: list[str] = Field(default_factory=list, description="Negative aspects")
    summary: str = Field(..., min_length=10, max_length=200, description="Brief summary")
    recommend: bool = Field(..., description="Whether reviewer recommends the product")

    @validator('rating')
    def validate_rating(cls, v):
        """Ensure rating is in 0.5 increments."""
        if v % 0.5 != 0:
            raise ValueError('Rating must be in 0.5 increments')
        return v

    @validator('summary')
    def validate_summary(cls, v):
        """Ensure summary is properly formatted."""
        if not v[0].isupper():
            v = v[0].upper() + v[1:]
        if not v.endswith('.'):
            v += '.'
        return v


@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=ProductReview,
    call_params={"temperature": 0.3}
)
@prompt_template(
    """
    Analyze this product review and extract structured information:

    {review_text}

    Provide:
    - Product name
    - Rating (1-5 in 0.5 increments)
    - List of pros (at least one)
    - List of cons (if any)
    - Summary (10-200 characters)
    - Recommendation (yes/no)
    """
)
def structured_validation(review_text: str):
    """
    Structured output with validation rules.

    Advanced features:
    1. Field validators
    2. Automatic formatting
    3. Constraint enforcement

    Args:
        review_text: Product review text

    Returns:
        ProductReview with validated data
    """
    pass


# Dynamic structured output

class DataPoint(BaseModel):
    """Generic data point model."""

    label: str = Field(..., description="Data label")
    value: Any = Field(..., description="Data value")
    unit: str | None = Field(None, description="Unit of measurement")
    confidence: float = Field(1.0, ge=0, le=1, description="Confidence score")


class AnalysisResult(BaseModel):
    """Model for analysis results."""

    analysis_type: str = Field(..., description="Type of analysis performed")
    data_points: list[DataPoint] = Field(..., description="Extracted data points")
    insights: list[str] = Field(..., description="Key insights from analysis")
    methodology: str = Field(..., description="Analysis methodology used")
    limitations: list[str] = Field(default_factory=list, description="Analysis limitations")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=AnalysisResult)
@prompt_template(
    """
    Perform {analysis_type} analysis on this data:

    {data}

    Context: {context}

    Extract relevant data points with confidence scores, provide insights,
    explain your methodology, and note any limitations.

    Focus on: {focus_areas:list}
    """
)
def structured_dynamic_analysis(
    data: str,
    analysis_type: str,
    context: str = "General analysis",
    focus_areas: list[str] = None
) -> BaseDynamicConfig:
    """
    Dynamic structured analysis with flexible output.

    Features:
    1. Generic data point extraction
    2. Confidence scoring
    3. Flexible analysis types

    Args:
        data: Data to analyze
        analysis_type: Type of analysis
        context: Analysis context
        focus_areas: Specific areas to focus on

    Returns:
        AnalysisResult with flexible structured data
    """
    if focus_areas is None:
        focus_areas = ["trends", "anomalies", "patterns"]

    return {}


# Structured output with relationships

class Entity(BaseModel):
    """Model for entities in text."""

    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type (person/organization/location)")
    description: str | None = Field(None, description="Brief description")


class Relationship(BaseModel):
    """Model for relationships between entities."""

    source: str = Field(..., description="Source entity name")
    target: str = Field(..., description="Target entity name")
    relationship_type: str = Field(..., description="Type of relationship")
    strength: float = Field(0.5, ge=0, le=1, description="Relationship strength")


class KnowledgeGraph(BaseModel):
    """Model for knowledge graph extraction."""

    entities: list[Entity] = Field(..., description="Entities found in text")
    relationships: list[Relationship] = Field(..., description="Relationships between entities")
    summary: str = Field(..., description="Summary of the knowledge graph")

    @validator('relationships')
    def validate_relationships(cls, v, values):
        """Ensure relationship entities exist."""
        if 'entities' in values:
            entity_names = {e.name for e in values['entities']}
            for rel in v:
                if rel.source not in entity_names or rel.target not in entity_names:
                    raise ValueError("Relationship references unknown entity")
        return v


@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=KnowledgeGraph,
    call_params={"temperature": 0.2}
)
@prompt_template(
    """
    Extract entities and their relationships from this text to build a knowledge graph:

    {text}

    Identify:
    1. All entities (people, organizations, locations)
    2. Relationships between entities
    3. Relationship strength (0-1)

    Provide a summary of the knowledge graph structure.
    """
)
def structured_knowledge_extraction(text: str):
    """
    Knowledge graph extraction with relationships.

    Advanced features:
    1. Entity extraction
    2. Relationship mapping
    3. Cross-validation of relationships

    Args:
        text: Text to analyze

    Returns:
        KnowledgeGraph with entities and relationships
    """
    pass
