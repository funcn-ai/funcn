"""
Chain-of-thought (CoT) prompting examples using Mirascope.

Chain-of-thought prompting encourages the model to break down complex problems
into step-by-step reasoning, leading to more accurate and explainable results.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field


class ReasoningResult(BaseModel):
    """Model for reasoning outputs."""

    steps: list[str] = Field(..., description="Step-by-step reasoning")
    final_answer: str = Field(..., description="Final answer")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the answer")
    assumptions: list[str] = Field(..., description="Assumptions made")


class MathSolution(BaseModel):
    """Model for mathematical solutions."""

    problem_understanding: str = Field(..., description="Understanding of the problem")
    approach: str = Field(..., description="Solution approach")
    calculations: list[str] = Field(..., description="Step-by-step calculations")
    answer: str = Field(..., description="Final answer with units")
    verification: str = Field(..., description="Answer verification")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ReasoningResult)
@prompt_template(
    """
    Let's solve this step-by-step.

    Question: {question}

    Think through this carefully:
    1. First, identify what we're being asked to find
    2. List any relevant information or constraints
    3. Work through the logic step by step
    4. Arrive at the final answer
    5. Check if the answer makes sense

    Show all your reasoning.
    """
)
def chain_of_thought_basic(question: str):
    """
    Basic chain-of-thought prompting.

    This demonstrates:
    1. Explicit step-by-step instructions
    2. Structured reasoning process
    3. Self-verification step

    Args:
        question: Question to answer

    Returns:
        ReasoningResult with step-by-step solution
    """
    pass


@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=MathSolution,
    call_params={"temperature": 0.1}  # Low temperature for mathematical accuracy
)
@prompt_template(
    """
    Solve this math problem step by step.

    Problem: {problem}

    Follow these steps:
    1. Understanding: What are we asked to find?
    2. Given Information: What do we know?
    3. Approach: What method will we use?
    4. Calculations: Show each step clearly
    5. Answer: State the final answer with appropriate units
    6. Verification: Check the answer makes sense

    Important: Show all work and explain each step.
    """
)
def chain_of_thought_math(problem: str):
    """
    Mathematical chain-of-thought with structured steps.

    Features:
    1. Structured mathematical reasoning
    2. Clear calculation steps
    3. Answer verification
    4. Low temperature for accuracy

    Args:
        problem: Math problem to solve

    Returns:
        MathSolution with detailed solution
    """
    pass


# Advanced CoT with dynamic reasoning paths

class ComplexReasoning(BaseModel):
    """Model for complex reasoning tasks."""

    problem_decomposition: list[str] = Field(..., description="Problem broken into sub-problems")
    reasoning_paths: dict[str, list[str]] = Field(..., description="Different reasoning paths explored")
    selected_path: str = Field(..., description="The chosen reasoning path")
    detailed_steps: list[str] = Field(..., description="Detailed steps of selected path")
    conclusion: str = Field(..., description="Final conclusion")
    alternative_approaches: list[str] = Field(..., description="Other possible approaches")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ComplexReasoning)
@prompt_template(
    """
    Let's approach this complex problem systematically.

    Problem: {problem}

    Context: {context}

    Step 1: Break down the problem
    - What are the key components?
    - What are we trying to achieve?

    Step 2: Consider multiple approaches
    - Path A: {approach_a}
    - Path B: {approach_b}
    - Path C: {approach_c}

    Step 3: Evaluate each approach
    - Which is most suitable and why?

    Step 4: Execute the chosen approach
    - Work through it step by step

    Step 5: Conclude and reflect
    - What's the answer?
    - What other approaches might work?

    Think deeply and show all reasoning.
    """
)
def chain_of_thought_reasoning(
    problem: str,
    context: str = "",
    approach_a: str = "Direct analytical approach",
    approach_b: str = "Comparative analysis",
    approach_c: str = "First principles thinking"
):
    """
    Complex reasoning with multiple paths.

    Advanced features:
    1. Problem decomposition
    2. Multiple reasoning paths
    3. Path evaluation and selection
    4. Alternative approaches

    Args:
        problem: Complex problem to solve
        context: Additional context
        approach_a-c: Different approaches to consider

    Returns:
        ComplexReasoning with detailed analysis
    """
    pass


# CoT with self-correction

class SelfCorrectingReasoning(BaseModel):
    """Model for self-correcting reasoning."""

    initial_reasoning: list[str] = Field(..., description="Initial reasoning steps")
    potential_errors: list[str] = Field(..., description="Identified potential errors")
    corrections: list[str] = Field(..., description="Corrections made")
    revised_answer: str = Field(..., description="Revised final answer")
    confidence_before: float = Field(..., ge=0, le=1, description="Initial confidence")
    confidence_after: float = Field(..., ge=0, le=1, description="Confidence after correction")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=SelfCorrectingReasoning)
@prompt_template(
    """
    Solve this problem with self-correction.

    Problem: {problem}

    Phase 1: Initial Solution
    - Work through the problem step by step
    - Arrive at an initial answer

    Phase 2: Error Check
    - Review each step critically
    - Identify any potential mistakes or oversights
    - Consider edge cases

    Phase 3: Correction
    - Fix any identified issues
    - Revise the solution if needed

    Phase 4: Final Answer
    - State the corrected answer
    - Compare confidence before and after correction

    Be thorough in checking your work.
    """
)
def chain_of_thought_self_correcting(problem: str):
    """
    Self-correcting chain-of-thought reasoning.

    Features:
    1. Initial solution attempt
    2. Critical self-review
    3. Error identification and correction
    4. Confidence comparison

    Args:
        problem: Problem to solve with self-correction

    Returns:
        SelfCorrectingReasoning with corrections
    """
    pass


# CoT with examples

@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    call_params={"temperature": 0.2}
)
@prompt_template(
    """
    Let me show you how to think through problems step by step.

    Example:
    Question: "If a train travels 120 miles in 2 hours, how far will it travel in 5 hours at the same speed?"

    Step-by-step thinking:
    1. Find the speed: 120 miles ÷ 2 hours = 60 miles per hour
    2. Calculate distance for 5 hours: 60 miles/hour × 5 hours = 300 miles
    3. Answer: The train will travel 300 miles

    Now solve this problem the same way:
    Question: {question}

    Remember to:
    - Break it down into clear steps
    - Show all calculations
    - State the final answer clearly
    """
)
def chain_of_thought_with_example(question: str):
    """
    Chain-of-thought with example demonstration.

    Features:
    1. Example-based learning
    2. Clear step format
    3. Consistent structure

    Args:
        question: Question to solve

    Returns:
        Step-by-step solution following example
    """
    pass


# Dynamic CoT with computed steps

@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Solve this problem using the following reasoning framework:

    Problem: {problem}

    {reasoning_steps:lists}

    Additional considerations:
    {considerations:list}

    Work through each step methodically and show your thinking.
    """
)
def chain_of_thought_dynamic(
    problem: str,
    problem_type: str,
    considerations: list[str] = None
) -> BaseDynamicConfig:
    """
    Dynamic chain-of-thought with computed reasoning steps.

    Features:
    1. Problem-type specific steps
    2. Dynamic step generation
    3. Additional considerations

    Args:
        problem: Problem to solve
        problem_type: Type of problem (logical/mathematical/analytical)
        considerations: Additional factors to consider

    Returns:
        Solution with dynamic reasoning steps
    """
    if considerations is None:
        considerations = ["Check assumptions", "Consider edge cases", "Verify result"]

    # Generate reasoning steps based on problem type
    step_templates = {
        "logical": [
            ["Step 1: Identify the premises", "What facts are we given?"],
            ["Step 2: Determine the logical relationships", "How do the facts connect?"],
            ["Step 3: Apply logical rules", "What can we deduce?"],
            ["Step 4: Draw conclusions", "What follows logically?"]
        ],
        "mathematical": [
            ["Step 1: Identify what to find", "What is the unknown?"],
            ["Step 2: List given information", "What do we know?"],
            ["Step 3: Choose a method", "What approach will work?"],
            ["Step 4: Execute calculations", "Work through the math"],
            ["Step 5: Verify the answer", "Does it make sense?"]
        ],
        "analytical": [
            ["Step 1: Define the problem", "What exactly are we analyzing?"],
            ["Step 2: Gather relevant data", "What information is important?"],
            ["Step 3: Identify patterns", "What trends or relationships exist?"],
            ["Step 4: Draw insights", "What do the patterns tell us?"],
            ["Step 5: Make recommendations", "What actions follow?"]
        ]
    }

    reasoning_steps = step_templates.get(problem_type, step_templates["analytical"])

    return {
        "computed_fields": {
            "reasoning_steps": reasoning_steps
        }
    }
