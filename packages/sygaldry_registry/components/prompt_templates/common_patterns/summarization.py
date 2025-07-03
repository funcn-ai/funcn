"""
Summarization patterns using Mirascope.

Common patterns for various summarization tasks including extractive,
abstractive, and structured summarization approaches.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field

# Extractive summarization


class ExtractSummary(BaseModel):
    """Model for extractive summary."""

    key_sentences: list[str] = Field(..., description="Important sentences extracted")
    topics_covered: list[str] = Field(..., description="Main topics identified")
    summary_length: int = Field(..., description="Number of sentences extracted")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ExtractSummary)
@prompt_template(
    """
    Extract the most important sentences from this text:

    {text}

    Requirements:
    - Select {num_sentences} most important sentences
    - Preserve original wording
    - Cover all main topics
    - Maintain logical flow
    """
)
def summarize_extractive(text: str, num_sentences: int = 5):
    """
    Extractive summarization - select key sentences.

    Args:
        text: Text to summarize
        num_sentences: Number of sentences to extract

    Returns:
        ExtractSummary with key sentences
    """
    pass


# Abstractive summarization


class AbstractSummary(BaseModel):
    """Model for abstractive summary."""

    summary: str = Field(..., description="Generated summary")
    main_points: list[str] = Field(..., description="Main points covered")
    tone: str = Field(..., description="Tone of the summary")
    compression_ratio: float = Field(..., description="Text reduction ratio")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=AbstractSummary, call_params={"temperature": 0.3})
@prompt_template(
    """
    Create a {style} summary of this text:

    {text}

    Requirements:
    - Target length: {target_length} words
    - Audience: {audience}
    - Focus on: {focus_areas:list}
    - Maintain {tone} tone

    Generate new text that captures the essence.
    """
)
def summarize_abstractive(
    text: str,
    style: str = "concise",
    target_length: int = 100,
    audience: str = "general",
    focus_areas: list[str] = None,
    tone: str = "neutral",
):
    """
    Abstractive summarization - generate new summary text.

    Args:
        text: Text to summarize
        style: Summary style (concise/detailed/technical)
        target_length: Target word count
        audience: Target audience
        focus_areas: Specific areas to emphasize
        tone: Desired tone

    Returns:
        AbstractSummary with generated text
    """
    if focus_areas is None:
        focus_areas = ["main ideas", "key findings", "conclusions"]
    pass


# Bullet point summarization


class BulletSummary(BaseModel):
    """Model for bullet point summary."""

    title: str = Field(..., description="Summary title")
    bullets: list[str] = Field(..., description="Bullet points")
    categories: dict[str, list[str]] = Field(..., description="Categorized points")
    action_items: list[str] = Field(..., description="Action items identified")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=BulletSummary)
@prompt_template(
    """
    Create a structured bullet-point summary:

    {text}

    Format:
    - Title summarizing the main theme
    - {num_bullets} key bullet points
    - Group related points by category
    - Identify any action items

    Make bullets concise and actionable.
    """
)
def summarize_bullets(text: str, num_bullets: int = 7):
    """
    Bullet point summarization for quick scanning.

    Args:
        text: Text to summarize
        num_bullets: Target number of bullets

    Returns:
        BulletSummary with structured points
    """
    pass


# Advanced hierarchical summarization


class HierarchicalSummary(BaseModel):
    """Model for hierarchical summary."""

    executive_summary: str = Field(..., description="High-level summary")
    section_summaries: dict[str, str] = Field(..., description="Section-wise summaries")
    detail_level: dict[str, list[str]] = Field(..., description="Details by importance")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=HierarchicalSummary)
@prompt_template(
    """
    Create a hierarchical summary with multiple detail levels:

    {text}

    Structure:
    1. Executive summary (2-3 sentences)
    2. Section summaries (paragraph each)
    3. Detailed points organized by importance:
       - Critical: Must-know information
       - Important: Should-know information
       - Supplementary: Nice-to-know details
    """
)
def summarize_hierarchical(text: str):
    """
    Multi-level hierarchical summarization.

    Args:
        text: Text to summarize

    Returns:
        HierarchicalSummary with multiple detail levels
    """
    pass


# Dynamic summarization with context


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", call_params={"temperature": 0.2})
@prompt_template(
    """
    Summarize this text for the specific context:

    Text: {text}

    Context: {context}
    Previous Knowledge: {previous_knowledge:list}

    Summarization goals:
    {goals:lists}

    Adapt the summary to build on previous knowledge
    and serve the specific goals.
    """
)
def summarize_contextual(
    text: str, context: str, previous_knowledge: list[str] = None, goals: list[str] = None
) -> BaseDynamicConfig:
    """
    Context-aware dynamic summarization.

    Args:
        text: Text to summarize
        context: Usage context
        previous_knowledge: What reader already knows
        goals: Specific summarization goals

    Returns:
        Contextually adapted summary
    """
    if previous_knowledge is None:
        previous_knowledge = []

    if goals is None:
        goals = ["inform", "highlight key points"]

    formatted_goals = []
    for goal in goals:
        formatted_goals.append([f"- {goal}"])

    return {"computed_fields": {"goals": formatted_goals}}
