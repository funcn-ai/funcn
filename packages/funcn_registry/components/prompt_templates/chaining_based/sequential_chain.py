"""
Sequential chaining examples using Mirascope.

Sequential chains process information through multiple steps where each step's
output becomes the input for the next step, creating a pipeline of transformations.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field

# Basic sequential chain

class TopicSummary(BaseModel):
    """Model for topic summaries."""

    topic: str = Field(..., description="The main topic")
    key_points: list[str] = Field(..., description="Key points about the topic")
    summary: str = Field(..., description="Brief summary")


class ExpandedContent(BaseModel):
    """Model for expanded content."""

    introduction: str = Field(..., description="Introduction paragraph")
    main_sections: list[str] = Field(..., description="Main content sections")
    conclusion: str = Field(..., description="Conclusion paragraph")
    word_count: int = Field(..., description="Total word count")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=TopicSummary)
@prompt_template(
    """
    Research and summarize the topic: {topic}

    Provide:
    1. The main topic clearly stated
    2. 3-5 key points
    3. A brief summary (2-3 sentences)
    """
)
def research_topic(topic: str):
    """First step: Research and summarize a topic."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ExpandedContent)
@prompt_template(
    """
    Based on this topic summary, create expanded content:

    Topic: {topic}
    Key Points: {key_points:list}
    Summary: {summary}

    Create:
    1. An engaging introduction
    2. Detailed sections for each key point
    3. A compelling conclusion
    """
)
def expand_content(topic: str, key_points: list[str], summary: str):
    """Second step: Expand the summary into full content."""
    pass


def sequential_basic(topic: str) -> ExpandedContent:
    """
    Basic sequential chain example.

    This demonstrates:
    1. Simple two-step chain
    2. Data passing between steps
    3. Progressive content development

    Args:
        topic: Topic to research and expand

    Returns:
        ExpandedContent with full article
    """
    # Step 1: Research the topic
    research = research_topic(topic)

    # Step 2: Expand into full content
    content = expand_content(
        topic=research.topic,
        key_points=research.key_points,
        summary=research.summary
    )

    return content


# Sequential chain with context preservation

class ContextualAnalysis(BaseModel):
    """Model for contextual analysis."""

    context: str = Field(..., description="Analysis context")
    findings: list[str] = Field(..., description="Key findings")
    implications: list[str] = Field(..., description="Implications of findings")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Analyze this data in the given context:

    Data: {data}
    Context: {context}
    Previous Analysis: {previous_analysis}

    Build upon the previous analysis to provide deeper insights.
    """
)
def analyze_with_context(
    data: str,
    context: str,
    previous_analysis: str = "No previous analysis"
) -> BaseDynamicConfig:
    """Contextual analysis that builds on previous results."""
    return {}


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ContextualAnalysis)
@prompt_template(
    """
    Synthesize these analyses into final insights:

    {analyses:lists}

    Original Context: {original_context}

    Provide:
    1. Unified context understanding
    2. Combined findings
    3. Overall implications
    4. Confidence in conclusions
    """
)
def synthesize_analyses(
    analyses: list[str],
    original_context: str
) -> BaseDynamicConfig:
    """Synthesize multiple analyses into final insights."""
    formatted_analyses = []
    for i, analysis in enumerate(analyses, 1):
        formatted_analyses.append([
            f"Analysis {i}:",
            analysis,
            ""
        ])

    return {
        "computed_fields": {
            "analyses": formatted_analyses
        }
    }


def sequential_with_context(
    data_points: list[str],
    context: str
) -> ContextualAnalysis:
    """
    Sequential chain with context preservation.

    Features:
    1. Context threading through steps
    2. Building on previous analyses
    3. Synthesis of multiple results

    Args:
        data_points: List of data to analyze
        context: Analysis context

    Returns:
        ContextualAnalysis with synthesized insights
    """
    analyses = []
    previous = "No previous analysis"

    # Analyze each data point with context
    for data in data_points:
        analysis = analyze_with_context(
            data=data,
            context=context,
            previous_analysis=previous
        )
        analyses.append(analysis.content)
        previous = analysis.content

    # Synthesize all analyses
    final_analysis = synthesize_analyses(
        analyses=analyses,
        original_context=context
    )

    return final_analysis


# Multi-step sequential processing

class ProcessedData(BaseModel):
    """Model for processed data."""

    stage: str = Field(..., description="Processing stage")
    data: str = Field(..., description="Processed data")
    transformations: list[str] = Field(..., description="Applied transformations")
    quality_score: float = Field(..., ge=0, le=1, description="Data quality score")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ProcessedData)
@prompt_template(
    """
    Stage: Data Cleaning

    Clean and prepare this data:
    {raw_data}

    Apply:
    1. Remove inconsistencies
    2. Standardize format
    3. Handle missing values
    4. Validate data quality
    """
)
def clean_data(raw_data: str):
    """Step 1: Clean raw data."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ProcessedData)
@prompt_template(
    """
    Stage: Data Transformation

    Transform this cleaned data:
    {cleaned_data}

    Previous transformations: {transformations:list}

    Apply:
    1. Normalize values
    2. Extract features
    3. Aggregate where appropriate
    4. Enhance with derived metrics
    """
)
def transform_data(cleaned_data: str, transformations: list[str]):
    """Step 2: Transform cleaned data."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ProcessedData)
@prompt_template(
    """
    Stage: Data Enrichment

    Enrich this transformed data:
    {transformed_data}

    Previous transformations: {transformations:list}

    Add:
    1. Contextual information
    2. Related metrics
    3. Predictive indicators
    4. Quality assessment
    """
)
def enrich_data(transformed_data: str, transformations: list[str]):
    """Step 3: Enrich transformed data."""
    pass


def sequential_multi_step(raw_data: str) -> list[ProcessedData]:
    """
    Multi-step sequential data processing.

    Advanced features:
    1. Multiple processing stages
    2. Transformation tracking
    3. Quality scoring at each step

    Args:
        raw_data: Raw data to process

    Returns:
        List of ProcessedData for each stage
    """
    results = []

    # Step 1: Clean
    cleaned = clean_data(raw_data)
    results.append(cleaned)

    # Step 2: Transform
    transformed = transform_data(
        cleaned_data=cleaned.data,
        transformations=cleaned.transformations
    )
    results.append(transformed)

    # Step 3: Enrich
    enriched = enrich_data(
        transformed_data=transformed.data,
        transformations=cleaned.transformations + transformed.transformations
    )
    results.append(enriched)

    return results
