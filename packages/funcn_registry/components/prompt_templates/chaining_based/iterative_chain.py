"""
Iterative chaining examples using Mirascope.

Iterative chains repeatedly refine outputs through multiple passes, enabling
progressive improvement and convergence toward optimal results.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field

# Basic iterative refinement

class RefinementResult(BaseModel):
    """Model for refinement results."""

    iteration: int = Field(..., description="Iteration number")
    content: str = Field(..., description="Refined content")
    improvements: list[str] = Field(..., description="Improvements made")
    quality_score: float = Field(..., ge=0, le=10, description="Quality score")
    needs_further_refinement: bool = Field(..., description="Whether more refinement is needed")


class QualityAssessment(BaseModel):
    """Model for quality assessment."""

    score: float = Field(..., ge=0, le=10, description="Quality score")
    strengths: list[str] = Field(..., description="Identified strengths")
    weaknesses: list[str] = Field(..., description="Identified weaknesses")
    suggestions: list[str] = Field(..., description="Improvement suggestions")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=QualityAssessment)
@prompt_template(
    """
    Assess the quality of this content:

    {content}

    Criteria:
    - Clarity and coherence
    - Completeness
    - Accuracy
    - Engagement

    Provide score (0-10), strengths, weaknesses, and suggestions.
    """
)
def assess_quality(content: str):
    """Assess content quality."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=RefinementResult)
@prompt_template(
    """
    Refine this content based on feedback:

    Current Content:
    {content}

    Iteration: {iteration}

    Previous Quality Score: {quality_score}
    Weaknesses to address: {weaknesses:list}
    Suggestions to implement: {suggestions:list}

    Improve the content while maintaining its core message.
    """
)
def refine_content(
    content: str,
    iteration: int,
    quality_score: float,
    weaknesses: list[str],
    suggestions: list[str]
):
    """Refine content based on assessment."""
    pass


def iterative_refinement(
    initial_content: str,
    target_score: float = 8.0,
    max_iterations: int = 5
) -> list[RefinementResult]:
    """
    Basic iterative refinement until quality target is met.

    This demonstrates:
    1. Quality assessment
    2. Targeted refinement
    3. Convergence checking

    Args:
        initial_content: Content to refine
        target_score: Target quality score
        max_iterations: Maximum refinement iterations

    Returns:
        List of RefinementResult for each iteration
    """
    results = []
    current_content = initial_content

    for i in range(max_iterations):
        # Assess current quality
        assessment = assess_quality(current_content)

        # Check if target met
        if assessment.score >= target_score:
            results.append(RefinementResult(
                iteration=i + 1,
                content=current_content,
                improvements=["Target quality achieved"],
                quality_score=assessment.score,
                needs_further_refinement=False
            ))
            break

        # Refine based on assessment
        refinement = refine_content(
            content=current_content,
            iteration=i + 1,
            quality_score=assessment.score,
            weaknesses=assessment.weaknesses,
            suggestions=assessment.suggestions
        )

        results.append(refinement)
        current_content = refinement.content

    return results


# Iterative validation and correction

class ValidationResult(BaseModel):
    """Model for validation results."""

    is_valid: bool = Field(..., description="Whether content is valid")
    errors: list[str] = Field(..., description="Identified errors")
    warnings: list[str] = Field(..., description="Identified warnings")
    compliance_score: float = Field(..., ge=0, le=1, description="Compliance score")


class CorrectedContent(BaseModel):
    """Model for corrected content."""

    content: str = Field(..., description="Corrected content")
    corrections_made: list[str] = Field(..., description="List of corrections")
    remaining_issues: list[str] = Field(..., description="Issues that couldn't be fixed")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ValidationResult)
@prompt_template(
    """
    Validate this content against requirements:

    Content: {content}

    Requirements:
    {requirements:list}

    Check for errors, warnings, and overall compliance.
    """
)
def validate_content(content: str, requirements: list[str]):
    """Validate content against requirements."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=CorrectedContent)
@prompt_template(
    """
    Correct these issues in the content:

    Content: {content}

    Errors to fix: {errors:list}
    Warnings to address: {warnings:list}

    Make minimal changes to fix issues while preserving intent.
    """
)
def correct_issues(
    content: str,
    errors: list[str],
    warnings: list[str]
):
    """Correct identified issues."""
    pass


def iterative_validation(
    content: str,
    requirements: list[str],
    max_iterations: int = 3
) -> dict:
    """
    Iterative validation and correction until compliant.

    Features:
    1. Requirements validation
    2. Error correction
    3. Compliance tracking

    Args:
        content: Content to validate
        requirements: List of requirements
        max_iterations: Maximum correction attempts

    Returns:
        Dict with final content and validation history
    """
    validation_history = []
    current_content = content

    for i in range(max_iterations):
        # Validate current content
        validation = validate_content(
            content=current_content,
            requirements=requirements
        )

        validation_history.append({
            "iteration": i + 1,
            "validation": validation,
            "content": current_content
        })

        # Check if valid
        if validation.is_valid and validation.compliance_score >= 0.95:
            break

        # Correct issues
        if validation.errors or validation.warnings:
            correction = correct_issues(
                content=current_content,
                errors=validation.errors,
                warnings=validation.warnings
            )
            current_content = correction.content

    return {
        "final_content": current_content,
        "iterations": len(validation_history),
        "final_validation": validation_history[-1]["validation"],
        "history": validation_history
    }


# Iterative convergence optimization

class OptimizationState(BaseModel):
    """Model for optimization state."""

    iteration: int = Field(..., description="Iteration number")
    value: str = Field(..., description="Current optimized value")
    objective_score: float = Field(..., description="Objective function score")
    gradient: list[str] = Field(..., description="Improvement directions")
    converged: bool = Field(..., description="Whether optimization has converged")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=OptimizationState)
@prompt_template(
    """
    Optimize this solution for the objective:

    Current Solution: {current_solution}
    Objective: {objective}
    Iteration: {iteration}

    Previous Scores: {score_history:list}

    Consider:
    1. Current objective score
    2. Improvement gradient
    3. Convergence criteria

    Provide optimized solution with score and convergence status.
    """
)
def optimize_step(
    current_solution: str,
    objective: str,
    iteration: int,
    score_history: list[float]
) -> BaseDynamicConfig:
    """Single optimization step."""
    return {}


def iterative_convergence(
    initial_solution: str,
    objective: str,
    convergence_threshold: float = 0.01,
    max_iterations: int = 10
) -> list[OptimizationState]:
    """
    Iterative optimization until convergence.

    Features:
    1. Objective-driven optimization
    2. Convergence detection
    3. Score tracking

    Args:
        initial_solution: Starting solution
        objective: Optimization objective
        convergence_threshold: Score change threshold
        max_iterations: Maximum iterations

    Returns:
        List of OptimizationState for each iteration
    """
    states = []
    current_solution = initial_solution
    score_history: list[float] = []

    for i in range(max_iterations):
        # Optimize
        state = optimize_step(
            current_solution=current_solution,
            objective=objective,
            iteration=i + 1,
            score_history=score_history
        )

        states.append(state)
        score_history.append(state.objective_score)

        # Check convergence
        if state.converged:
            break

        if len(score_history) > 1:
            score_change = abs(score_history[-1] - score_history[-2])
            if score_change < convergence_threshold:
                state.converged = True
                break

        current_solution = state.value

    return states


# Advanced iterative with feedback loop

class FeedbackLoop(BaseModel):
    """Model for feedback loop results."""

    iteration: int = Field(..., description="Iteration number")
    input_data: str = Field(..., description="Input for this iteration")
    output: str = Field(..., description="Generated output")
    feedback: str = Field(..., description="Feedback received")
    adaptation: str = Field(..., description="How the system adapted")
    performance_metric: float = Field(..., description="Performance metric")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Process this input with learned adaptations:

    Input: {input_data}

    Previous learnings:
    {learnings:lists}

    Apply learned patterns to improve output.
    """
)
def process_with_learning(
    input_data: str,
    learnings: list[dict]
) -> BaseDynamicConfig:
    """Process input with accumulated learnings."""
    formatted_learnings = []
    for learning in learnings:
        formatted_learnings.append([
            f"Iteration {learning['iteration']}:",
            f"Feedback: {learning['feedback']}",
            f"Adaptation: {learning['adaptation']}",
            ""
        ])

    return {
        "computed_fields": {
            "learnings": formatted_learnings
        }
    }


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=FeedbackLoop)
@prompt_template(
    """
    Generate feedback and adaptation for this iteration:

    Iteration: {iteration}
    Input: {input_data}
    Output: {output}
    Target: {target}

    Analyze performance and suggest adaptation.
    """
)
def generate_feedback(
    iteration: int,
    input_data: str,
    output: str,
    target: str
):
    """Generate feedback and adaptation strategy."""
    pass


def iterative_feedback_loop(
    inputs: list[str],
    target: str,
    initial_learnings: list[dict] = None
) -> list[FeedbackLoop]:
    """
    Iterative processing with feedback and learning.

    Advanced features:
    1. Continuous learning
    2. Adaptive processing
    3. Performance tracking

    Args:
        inputs: List of inputs to process
        target: Target outcome
        initial_learnings: Prior learnings

    Returns:
        List of FeedbackLoop results
    """
    if initial_learnings is None:
        initial_learnings = []

    learnings = initial_learnings.copy()
    results = []

    for i, input_data in enumerate(inputs):
        # Process with current learnings
        output = process_with_learning(
            input_data=input_data,
            learnings=learnings
        )

        # Generate feedback
        feedback_loop = generate_feedback(
            iteration=i + 1,
            input_data=input_data,
            output=output.content,
            target=target
        )

        # Store learning
        learnings.append({
            "iteration": feedback_loop.iteration,
            "feedback": feedback_loop.feedback,
            "adaptation": feedback_loop.adaptation
        })

        results.append(feedback_loop)

    return results
