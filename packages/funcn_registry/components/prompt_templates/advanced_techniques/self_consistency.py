"""
Self-consistency technique using Mirascope.

Advanced technique that generates multiple responses and selects the most
consistent answer through voting or aggregation, improving reliability.
"""

import asyncio
import lilypad
from collections import Counter
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field

# Self-consistency checking

class ConsistencyResult(BaseModel):
    """Model for consistency check results."""

    question: str = Field(..., description="Original question")
    responses: list[str] = Field(..., description="All generated responses")
    consistent_answer: str = Field(..., description="Most consistent answer")
    confidence: float = Field(..., ge=0, le=1, description="Consistency confidence")
    agreement_rate: float = Field(..., ge=0, le=1, description="Rate of agreement")
    variations: list[str] = Field(..., description="Different answer variations found")


@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    call_params={"temperature": 0.7}  # Higher temp for diversity
)
@prompt_template(
    """
    Answer this question:

    {question}

    Provide a clear, direct answer.
    """
)
async def generate_response(question: str):
    """Generate a single response to the question."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Analyze these responses for consistency:

    Question: {question}

    Responses:
    {responses:list}

    Determine:
    1. The most consistent/common answer
    2. Level of agreement between responses
    3. Key variations in answers

    Select the best answer based on consistency.
    """
)
async def analyze_consistency(
    question: str,
    responses: list[str]
) -> BaseDynamicConfig:
    """Analyze response consistency."""
    return {}


async def consistency_check(
    question: str,
    num_samples: int = 5,
    temperature_range: tuple[float, float] = (0.5, 0.9)
) -> ConsistencyResult:
    """
    Self-consistency check through multiple sampling.

    This demonstrates:
    1. Multiple response generation
    2. Consistency analysis
    3. Confidence scoring

    Args:
        question: Question to answer
        num_samples: Number of responses to generate
        temperature_range: Range of temperatures to use

    Returns:
        ConsistencyResult with consistent answer
    """
    # Generate multiple responses with varying temperatures
    tasks = []
    for i in range(num_samples):
        # Vary temperature for diversity
        temp = temperature_range[0] + (temperature_range[1] - temperature_range[0]) * (i / max(num_samples - 1, 1))
        # Note: In practice, you'd pass temperature to the call
        tasks.append(generate_response(question))

    responses = await asyncio.gather(*tasks)
    response_texts = [r.content for r in responses]

    # Analyze consistency
    analysis = await analyze_consistency(question, response_texts)

    # Simple consistency scoring (could be more sophisticated)
    response_counter = Counter(response_texts)
    most_common = response_counter.most_common(1)[0]
    agreement_rate = most_common[1] / num_samples

    return ConsistencyResult(
        question=question,
        responses=response_texts,
        consistent_answer=most_common[0],
        confidence=agreement_rate,
        agreement_rate=agreement_rate,
        variations=list(response_counter.keys())
    )


# Ensemble response generation

class EnsembleResponse(BaseModel):
    """Model for ensemble response."""

    question: str = Field(..., description="Original question")
    individual_responses: list[str] = Field(..., description="Individual model responses")
    ensemble_answer: str = Field(..., description="Synthesized ensemble answer")
    confidence_scores: list[float] = Field(..., description="Confidence per response")
    synthesis_method: str = Field(..., description="Method used for synthesis")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=EnsembleResponse)
@prompt_template(
    """
    Synthesize these responses into a single best answer:

    Question: {question}

    Individual responses:
    {responses_with_scores:lists}

    Create an ensemble answer that:
    1. Incorporates the best elements from each
    2. Resolves any contradictions
    3. Provides the most complete answer

    Explain your synthesis approach.
    """
)
async def synthesize_ensemble(
    question: str,
    responses: list[str],
    scores: list[float]
) -> BaseDynamicConfig:
    """Synthesize ensemble response."""
    responses_with_scores = []
    for i, (resp, score) in enumerate(zip(responses, scores, strict=False), 1):
        responses_with_scores.append([
            f"Response {i} (confidence: {score:.2f}):",
            resp,
            ""
        ])

    return {
        "computed_fields": {
            "responses_with_scores": responses_with_scores
        }
    }


async def ensemble_response(
    question: str,
    models: list[str] = None,
    synthesis_strategy: str = "weighted"
) -> EnsembleResponse:
    """
    Generate ensemble response from multiple models.

    Features:
    1. Multi-model generation
    2. Confidence weighting
    3. Intelligent synthesis

    Args:
        question: Question to answer
        models: List of models to use
        synthesis_strategy: How to combine responses

    Returns:
        EnsembleResponse with synthesized answer
    """
    if models is None:
        models = ["gpt-4o-mini"] * 3  # Simulate multiple models

    # Generate responses from each model
    responses = []
    scores = []

    for i, model in enumerate(models):
        response = await generate_response(question)
        responses.append(response.content)
        # Simulate confidence scores
        scores.append(0.7 + 0.3 * (i / len(models)))

    # Synthesize ensemble
    ensemble = await synthesize_ensemble(question, responses, scores)

    return ensemble


# Majority voting

class VotingResult(BaseModel):
    """Model for voting results."""

    question: str = Field(..., description="Original question")
    candidates: list[str] = Field(..., description="All candidate answers")
    votes: dict[str, int] = Field(..., description="Vote count per answer")
    winner: str = Field(..., description="Winning answer")
    confidence: float = Field(..., ge=0, le=1, description="Voting confidence")
    consensus_level: str = Field(..., description="Level of consensus")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Answer this {question_type} question:

    {question}

    Approach {approach_number}:
    Think about this from a {perspective} perspective.

    Provide your answer clearly.
    """
)
async def generate_vote(
    question: str,
    question_type: str,
    approach_number: int,
    perspective: str
):
    """Generate a vote with specific perspective."""
    pass


async def majority_voting(
    question: str,
    num_voters: int = 7,
    question_type: str = "general"
) -> VotingResult:
    """
    Majority voting for answer selection.

    Features:
    1. Multiple independent votes
    2. Consensus measurement
    3. Confidence scoring

    Args:
        question: Question to answer
        num_voters: Number of votes to collect
        question_type: Type of question

    Returns:
        VotingResult with winning answer
    """
    perspectives = [
        "analytical", "practical", "theoretical",
        "critical", "creative", "systematic", "intuitive"
    ]

    # Collect votes asynchronously
    tasks = []
    for i in range(num_voters):
        perspective = perspectives[i % len(perspectives)]
        tasks.append(generate_vote(
            question=question,
            question_type=question_type,
            approach_number=i + 1,
            perspective=perspective
        ))

    vote_responses = await asyncio.gather(*tasks)
    votes = [response.content for response in vote_responses]

    # Count votes
    vote_counter = Counter(votes)
    total_votes = sum(vote_counter.values())
    winner, winner_count = vote_counter.most_common(1)[0]

    # Determine consensus level
    winner_percentage = winner_count / total_votes
    if winner_percentage > 0.8:
        consensus_level = "strong"
    elif winner_percentage > 0.6:
        consensus_level = "moderate"
    else:
        consensus_level = "weak"

    return VotingResult(
        question=question,
        candidates=list(vote_counter.keys()),
        votes=dict(vote_counter),
        winner=winner,
        confidence=winner_percentage,
        consensus_level=consensus_level
    )


# Advanced self-consistency with reasoning

class ReasonedConsistency(BaseModel):
    """Model for reasoned consistency check."""

    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Final answer")
    reasoning_paths: list[str] = Field(..., description="Different reasoning paths")
    convergence_points: list[str] = Field(..., description="Where reasoning converged")
    divergence_points: list[str] = Field(..., description="Where reasoning diverged")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ReasonedConsistency)
@prompt_template(
    """
    Analyze reasoning consistency for this question:

    Question: {question}

    Different reasoning approaches:
    {reasoning_approaches:lists}

    Identify:
    1. Common conclusions across approaches
    2. Points where reasoning converges
    3. Points where reasoning diverges
    4. Most reliable answer based on consistency

    Provide confidence in the final answer.
    """
)
def analyze_reasoning_consistency(
    question: str,
    reasoning_approaches: list[dict[str, str]]
) -> BaseDynamicConfig:
    """Analyze consistency across reasoning paths."""
    formatted_approaches = []
    for i, approach in enumerate(reasoning_approaches, 1):
        formatted_approaches.append([
            f"Approach {i}: {approach['method']}",
            f"Reasoning: {approach['reasoning']}",
            f"Answer: {approach['answer']}",
            ""
        ])

    return {
        "computed_fields": {
            "reasoning_approaches": formatted_approaches
        }
    }
