"""
Zero-shot prompting examples using Mirascope.

Zero-shot prompting involves asking the model to perform a task without providing
any examples. The model relies solely on its pre-trained knowledge and the
instructions provided in the prompt.
"""

import lilypad
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field


class TranslationResult(BaseModel):
    """Model for translation outputs."""

    original_text: str = Field(..., description="The original text")
    translated_text: str = Field(..., description="The translated text")
    target_language: str = Field(..., description="The target language")
    confidence: float = Field(..., ge=0, le=1, description="Translation confidence score")


class AnalysisResult(BaseModel):
    """Model for analysis outputs."""

    main_topic: str = Field(..., description="The main topic or theme")
    key_points: list[str] = Field(..., description="Key points identified")
    sentiment: str = Field(..., description="Overall sentiment (positive/negative/neutral)")
    summary: str = Field(..., description="Brief summary of the content")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=TranslationResult)
@prompt_template(
    """
    Translate the following text from {source_language} to {target_language}.
    Provide a confidence score for your translation.

    Text: {text}
    """
)
def zero_shot_example(text: str, source_language: str, target_language: str):
    """
    Basic zero-shot example: Translation without examples.

    This demonstrates the simplest form of zero-shot prompting where we give
    the model a clear task without any examples.

    Args:
        text: The text to translate
        source_language: Source language
        target_language: Target language

    Returns:
        TranslationResult with translation and confidence
    """
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=AnalysisResult)
@prompt_template(
    """
    SYSTEM: You are an expert content analyst with deep knowledge across various domains.
    Your analysis should be thorough, objective, and insightful.

    USER: Analyze the following text and provide:
    1. The main topic or theme
    2. Key points (as a list)
    3. Overall sentiment
    4. A brief summary

    Context: {context}

    Text to analyze:
    {text}
    """
)
def zero_shot_with_context(text: str, context: str = "General analysis"):
    """
    Zero-shot with enhanced context and system instructions.

    This example shows how to improve zero-shot performance by:
    1. Setting a clear system role
    2. Providing structured output requirements
    3. Adding optional context

    Args:
        text: The text to analyze
        context: Optional context about the text (e.g., "Scientific paper", "News article")

    Returns:
        AnalysisResult with comprehensive analysis
    """
    pass


# Advanced zero-shot examples with dynamic configuration

class TaskResult(BaseModel):
    """Generic task result model."""

    task_type: str = Field(..., description="The type of task performed")
    result: str = Field(..., description="The task result")
    reasoning: str = Field(..., description="Explanation of the approach taken")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in the result")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=TaskResult)
@prompt_template(
    """
    SYSTEM: You are a versatile AI assistant capable of handling various tasks.
    Always explain your reasoning and provide a confidence score.

    USER: {task_description}

    Additional requirements:
    - {requirement_1}
    - {requirement_2}
    - {requirement_3}

    Input: {input_data}
    """
)
def zero_shot_dynamic(
    task_description: str,
    input_data: str,
    requirement_1: str = "Be concise",
    requirement_2: str = "Be accurate",
    requirement_3: str = "Show your work"
) -> llm.OpenAIDynamicConfig:
    """
    Dynamic zero-shot prompting with configurable requirements.

    This advanced example demonstrates:
    1. Flexible task description
    2. Configurable requirements
    3. Dynamic prompt construction

    Args:
        task_description: Description of the task to perform
        input_data: The data to process
        requirement_1-3: Customizable requirements

    Returns:
        TaskResult with dynamic task execution
    """
    # Could add computed fields here if needed
    return {}


# Practical zero-shot examples

class CodeExplanation(BaseModel):
    """Model for code explanation outputs."""

    language: str = Field(..., description="Programming language")
    purpose: str = Field(..., description="What the code does")
    key_concepts: list[str] = Field(..., description="Key programming concepts used")
    complexity: str = Field(..., description="Complexity level (beginner/intermediate/advanced)")
    improvements: list[str] = Field(..., description="Suggested improvements")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=CodeExplanation)
@prompt_template(
    """
    Explain the following code snippet:

    ```{language}
    {code}
    ```

    Provide:
    1. The programming language
    2. What the code does
    3. Key programming concepts used
    4. Complexity level
    5. Suggested improvements
    """
)
def zero_shot_code_analysis(code: str, language: str = "auto"):
    """
    Zero-shot code analysis and explanation.

    Demonstrates zero-shot prompting for technical tasks without examples.

    Args:
        code: Code snippet to analyze
        language: Programming language (or "auto" to detect)

    Returns:
        CodeExplanation with detailed analysis
    """
    pass


# Best practices example

@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    call_params={"temperature": 0.3}  # Lower temperature for consistency
)
@prompt_template(
    """
    Given the following problem, provide a step-by-step solution:

    Problem: {problem}

    Constraints:
    {constraints:list}

    Format your response as:
    1. Understanding: Restate the problem
    2. Approach: Explain your solution strategy
    3. Solution: Provide the step-by-step solution
    4. Verification: Check your answer
    """
)
def zero_shot_problem_solving(problem: str, constraints: list[str] = None):
    """
    Zero-shot problem solving with structured format.

    Best practices demonstrated:
    1. Clear structure in the prompt
    2. Explicit formatting instructions
    3. Lower temperature for consistency
    4. Verification step included

    Args:
        problem: Problem statement
        constraints: Optional list of constraints

    Returns:
        Structured problem solution
    """
    if constraints is None:
        constraints = ["None specified"]

    return {}
