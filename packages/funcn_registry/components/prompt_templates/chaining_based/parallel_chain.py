"""
Parallel chaining examples using Mirascope.

Parallel chains execute multiple prompts simultaneously, enabling efficient
processing of independent tasks and aggregation of diverse perspectives.
"""

import asyncio
import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field
from typing import Any

# Basic parallel execution


class Perspective(BaseModel):
    """Model for different perspectives."""

    viewpoint: str = Field(..., description="The perspective taken")
    analysis: str = Field(..., description="Analysis from this viewpoint")
    key_points: list[str] = Field(..., description="Key points from this perspective")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in analysis")


class AggregatedAnalysis(BaseModel):
    """Model for aggregated analyses."""

    topic: str = Field(..., description="Analysis topic")
    perspectives: dict[str, str] = Field(..., description="Different perspective summaries")
    consensus_points: list[str] = Field(..., description="Points of agreement")
    divergent_points: list[str] = Field(..., description="Points of disagreement")
    synthesis: str = Field(..., description="Synthesized conclusion")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=Perspective)
@prompt_template(
    """
    Analyze this topic from a {viewpoint} perspective:

    Topic: {topic}

    Provide:
    1. Your specific viewpoint
    2. Detailed analysis
    3. Key points (3-5)
    4. Confidence level in your analysis
    """
)
async def analyze_perspective(topic: str, viewpoint: str):
    """Analyze topic from a specific perspective."""
    pass


async def parallel_basic(topic: str) -> list[Perspective]:
    """
    Basic parallel execution of multiple perspectives.

    This demonstrates:
    1. Concurrent execution of multiple prompts
    2. Gathering results from parallel tasks
    3. Independent perspective analysis

    Args:
        topic: Topic to analyze

    Returns:
        List of Perspective analyses
    """
    viewpoints = ["technical", "business", "ethical", "user experience"]

    # Create tasks for parallel execution
    tasks = [analyze_perspective(topic=topic, viewpoint=viewpoint) for viewpoint in viewpoints]

    # Execute all tasks in parallel
    perspectives = await asyncio.gather(*tasks)

    return perspectives


# Parallel aggregation pattern


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=AggregatedAnalysis)
@prompt_template(
    """
    Aggregate these different perspective analyses:

    Topic: {topic}

    {perspectives_text:lists}

    Synthesize by:
    1. Summarizing each perspective
    2. Finding consensus points
    3. Identifying divergent views
    4. Creating a balanced synthesis
    """
)
async def aggregate_perspectives(topic: str, perspectives: list[Perspective]) -> BaseDynamicConfig:
    """Aggregate multiple perspectives into unified analysis."""
    perspectives_text = []
    for p in perspectives:
        perspectives_text.append(
            [
                f"{p.viewpoint} perspective:",
                p.analysis,
                f"Key points: {', '.join(p.key_points)}",
                f"Confidence: {p.confidence}",
                "",
            ]
        )

    return {"computed_fields": {"perspectives_text": perspectives_text}}


async def parallel_aggregation(topic: str) -> AggregatedAnalysis:
    """
    Parallel execution with aggregation.

    Features:
    1. Multiple parallel analyses
    2. Result aggregation
    3. Consensus building

    Args:
        topic: Topic to analyze

    Returns:
        AggregatedAnalysis with synthesized insights
    """
    # Get perspectives in parallel
    perspectives = await parallel_basic(topic)

    # Aggregate the results
    aggregated = await aggregate_perspectives(topic=topic, perspectives=perspectives)

    return aggregated


# Advanced async parallel processing


class ResearchResult(BaseModel):
    """Model for research results."""

    source: str = Field(..., description="Research source")
    findings: list[str] = Field(..., description="Key findings")
    reliability: float = Field(..., ge=0, le=1, description="Source reliability")
    relevance: float = Field(..., ge=0, le=1, description="Relevance to query")


class ValidationResult(BaseModel):
    """Model for validation results."""

    claim: str = Field(..., description="Claim being validated")
    is_valid: bool = Field(..., description="Whether claim is valid")
    evidence: list[str] = Field(..., description="Supporting evidence")
    confidence: float = Field(..., ge=0, le=1, description="Validation confidence")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ResearchResult)
@prompt_template(
    """
    Research this query using {source} as your knowledge source:

    Query: {query}

    Provide findings with reliability and relevance scores.
    """
)
async def research_source(query: str, source: str):
    """Research from a specific source."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ValidationResult)
@prompt_template(
    """
    Validate this claim based on the research findings:

    Claim: {claim}

    Research findings:
    {findings:lists}

    Determine validity with supporting evidence.
    """
)
async def validate_claim(claim: str, research_results: list[ResearchResult]) -> BaseDynamicConfig:
    """Validate a claim against research."""
    findings = []
    for r in research_results:
        findings.append([f"From {r.source} (reliability: {r.reliability}):", *r.findings, ""])

    return {"computed_fields": {"findings": findings}}


async def parallel_async(query: str, claim: str) -> dict[str, Any]:
    """
    Advanced async parallel processing.

    Features:
    1. Multiple async research tasks
    2. Parallel validation
    3. Coordinated results

    Args:
        query: Research query
        claim: Claim to validate

    Returns:
        Dict with research and validation results
    """
    sources = ["academic literature", "industry reports", "expert opinions", "case studies"]

    # Phase 1: Parallel research
    research_tasks = [research_source(query=query, source=source) for source in sources]
    research_results = await asyncio.gather(*research_tasks)

    # Filter high-quality results
    quality_results = [r for r in research_results if r.reliability > 0.7 and r.relevance > 0.6]

    # Phase 2: Validate claim against research
    validation = await validate_claim(claim=claim, research_results=quality_results)

    return {"research": research_results, "quality_research": quality_results, "validation": validation}


# Parallel with dynamic task generation


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Generate {task_type} for: {input_data}

    Requirements: {requirements:list}

    Provide high-quality output following all requirements.
    """
)
async def dynamic_task(input_data: str, task_type: str, requirements: list[str]):
    """Execute a dynamically defined task."""
    pass


async def parallel_dynamic_tasks(input_data: str, task_configs: list[dict[str, Any]]) -> list[Any]:
    """
    Parallel execution with dynamic task generation.

    Features:
    1. Dynamic task creation
    2. Flexible parallel execution
    3. Heterogeneous task handling

    Args:
        input_data: Input for all tasks
        task_configs: List of task configurations

    Returns:
        List of task results
    """
    tasks = []

    for config in task_configs:
        task = dynamic_task(input_data=input_data, task_type=config["type"], requirements=config.get("requirements", []))
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    return results
