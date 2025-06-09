"""
Content generation patterns using Mirascope.

Common patterns for generating various types of content including creative writing,
technical documentation, and structured content.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field
from typing import Any, Optional

# Creative content generation


class CreativeContent(BaseModel):
    """Model for creative content."""

    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Generated content")
    genre: str = Field(..., description="Content genre/style")
    tone: str = Field(..., description="Tone of the content")
    word_count: int = Field(..., description="Approximate word count")
    key_themes: list[str] = Field(..., description="Key themes explored")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=CreativeContent, call_params={"temperature": 0.8})
@prompt_template(
    """
    Generate creative content with these parameters:

    Type: {content_type}
    Theme: {theme}
    Style: {style}
    Tone: {tone}
    Length: {target_length} words

    Additional requirements:
    {requirements:list}

    Create engaging, original content that captures the essence of the theme.
    """
)
def generate_creative(
    content_type: str,
    theme: str,
    style: str = "contemporary",
    tone: str = "engaging",
    target_length: int = 500,
    requirements: list[str] = None,
):
    """
    Generate creative content (stories, poems, etc.).

    Args:
        content_type: Type of content (story/poem/essay)
        theme: Central theme
        style: Writing style
        tone: Desired tone
        target_length: Target word count
        requirements: Additional requirements

    Returns:
        CreativeContent with generated text
    """
    if requirements is None:
        requirements = []
    pass


# Technical content generation


class TechnicalContent(BaseModel):
    """Model for technical content."""

    title: str = Field(..., description="Document title")
    sections: dict[str, str] = Field(..., description="Document sections")
    code_examples: list[str] = Field(..., description="Code examples included")
    technical_level: str = Field(..., description="Technical complexity level")
    prerequisites: list[str] = Field(..., description="Prerequisites listed")
    references: list[str] = Field(..., description="References and resources")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=TechnicalContent, call_params={"temperature": 0.3})
@prompt_template(
    """
    Generate technical documentation:

    Topic: {topic}
    Document Type: {doc_type}
    Audience: {audience}
    Technical Level: {tech_level}

    Include:
    - Clear structure with sections
    - Code examples where relevant
    - Prerequisites
    - Best practices
    - References

    Focus areas: {focus_areas:list}
    """
)
def generate_technical(
    topic: str, doc_type: str, audience: str = "developers", tech_level: str = "intermediate", focus_areas: list[str] = None
):
    """
    Generate technical documentation.

    Args:
        topic: Technical topic
        doc_type: Type of documentation
        audience: Target audience
        tech_level: Technical level
        focus_areas: Specific areas to focus on

    Returns:
        TechnicalContent with structured documentation
    """
    if focus_areas is None:
        focus_areas = ["implementation", "best practices", "troubleshooting"]
    pass


# Structured content generation


class StructuredContent(BaseModel):
    """Model for structured content."""

    format: str = Field(..., description="Content format")
    metadata: dict[str, Any] = Field(..., description="Content metadata")
    main_content: dict[str, str] = Field(..., description="Main content sections")
    supplementary: dict[str, list[str]] = Field(..., description="Supplementary elements")
    seo_elements: dict[str, str] = Field(..., description="SEO-related elements")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=StructuredContent)
@prompt_template(
    """
    Generate structured content following this template:

    Format: {format}
    Topic: {topic}

    Template Structure:
    {template:lists}

    Requirements:
    - Follow the exact structure
    - Include all required sections
    - Optimize for {optimization_goal}
    - Maintain consistency throughout

    Target length per section: {section_length} words
    """
)
def generate_structured(
    format: str, topic: str, template: dict[str, list[str]], optimization_goal: str = "readability", section_length: int = 200
) -> BaseDynamicConfig:
    """
    Generate content following a specific structure.

    Args:
        format: Content format (blog/article/report)
        topic: Content topic
        template: Structure template
        optimization_goal: What to optimize for
        section_length: Target length per section

    Returns:
        StructuredContent following template
    """
    formatted_template = []
    for section, elements in template.items():
        formatted_template.append([f"{section}:"])
        for element in elements:
            formatted_template.append([f"  - {element}"])

    return {"computed_fields": {"template": formatted_template}}


# Marketing content generation


class MarketingContent(BaseModel):
    """Model for marketing content."""

    headline: str = Field(..., description="Attention-grabbing headline")
    subheadline: str = Field(..., description="Supporting subheadline")
    body_copy: str = Field(..., description="Main marketing copy")
    call_to_action: str = Field(..., description="Call to action")
    value_propositions: list[str] = Field(..., description="Key value props")
    emotional_hooks: list[str] = Field(..., description="Emotional appeals used")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=MarketingContent, call_params={"temperature": 0.7})
@prompt_template(
    """
    Generate marketing content for:

    Product/Service: {product}
    Target Audience: {audience}
    Goal: {marketing_goal}
    Tone: {tone}

    Key Features: {features:list}
    Unique Selling Points: {usps:list}

    Create compelling copy that:
    - Grabs attention
    - Communicates value
    - Drives action
    - Resonates emotionally
    """
)
def generate_marketing(
    product: str,
    audience: str,
    marketing_goal: str,
    tone: str = "professional",
    features: list[str] = None,
    usps: list[str] = None,
):
    """
    Generate marketing copy.

    Args:
        product: Product/service name
        audience: Target audience
        marketing_goal: Marketing objective
        tone: Copy tone
        features: Key features
        usps: Unique selling points

    Returns:
        MarketingContent with compelling copy
    """
    if features is None:
        features = []
    if usps is None:
        usps = []
    pass


# Dynamic content variation


class ContentVariation(BaseModel):
    """Model for content variations."""

    original: str = Field(..., description="Original content")
    variations: list[str] = Field(..., description="Content variations")
    variation_types: list[str] = Field(..., description="Types of variations")
    best_for: dict[str, str] = Field(..., description="Best variation for each use case")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ContentVariation)
@prompt_template(
    """
    Create variations of this content:

    Original: {original_content}

    Generate {num_variations} variations for:
    - Different tones: {tones:list}
    - Different lengths: {lengths:list}
    - Different audiences: {audiences:list}

    Maintain core message while adapting style and presentation.
    """
)
def generate_variations(
    original_content: str,
    num_variations: int = 3,
    tones: list[str] = None,
    lengths: list[str] = None,
    audiences: list[str] = None,
):
    """
    Generate content variations.

    Args:
        original_content: Base content
        num_variations: Number of variations
        tones: Tone variations
        lengths: Length variations
        audiences: Audience variations

    Returns:
        ContentVariation with multiple versions
    """
    if tones is None:
        tones = ["formal", "casual", "enthusiastic"]
    if lengths is None:
        lengths = ["brief", "standard", "detailed"]
    if audiences is None:
        audiences = ["general", "technical", "executive"]
    pass


# Template-based generation


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Fill in this content template:

    Template:
    {template}

    Variables to fill:
    {variables:lists}

    Context: {context}

    Instructions:
    - Replace all placeholders
    - Maintain template structure
    - Ensure coherent flow
    - Adapt tone to context
    """
)
def generate_from_template(template: str, variables: dict[str, str], context: str) -> BaseDynamicConfig:
    """
    Generate content from template.

    Args:
        template: Content template with placeholders
        variables: Variables to fill in
        context: Generation context

    Returns:
        Filled template content
    """
    formatted_variables = []
    for key, value in variables.items():
        formatted_variables.append([f"{{{key}}}: {value}"])

    return {"computed_fields": {"variables": formatted_variables}}
