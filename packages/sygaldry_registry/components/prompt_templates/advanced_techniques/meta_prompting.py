"""
Meta-prompting technique using Mirascope.

Advanced technique where the model generates or optimizes prompts for itself,
enabling dynamic prompt engineering and self-improvement.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field

# Prompt generation


class GeneratedPrompt(BaseModel):
    """Model for generated prompts."""

    task_description: str = Field(..., description="Task the prompt is for")
    generated_prompt: str = Field(..., description="The generated prompt")
    key_elements: list[str] = Field(..., description="Key elements included")
    expected_output_format: str = Field(..., description="Expected output format")
    optimization_notes: list[str] = Field(..., description="Optimization considerations")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=GeneratedPrompt)
@prompt_template(
    """
    Generate an optimal prompt for this task:

    Task: {task}
    Context: {context}
    Constraints: {constraints:list}

    Create a prompt that:
    1. Clearly defines the task
    2. Provides necessary context
    3. Specifies output format
    4. Includes helpful examples if needed
    5. Guides toward high-quality responses

    Consider prompt engineering best practices.
    """
)
def generate_prompt(task: str, context: str = "", constraints: list[str] = None):
    """
    Generate an optimized prompt for a task.

    Features:
    1. Task analysis
    2. Prompt structure optimization
    3. Best practices application

    Args:
        task: Task description
        context: Additional context
        constraints: Any constraints

    Returns:
        GeneratedPrompt with optimized prompt
    """
    if constraints is None:
        constraints = []
    pass


# Prompt optimization


class OptimizedPrompt(BaseModel):
    """Model for optimized prompts."""

    original_prompt: str = Field(..., description="Original prompt")
    issues_identified: list[str] = Field(..., description="Issues in original")
    optimized_prompt: str = Field(..., description="Optimized version")
    improvements: list[str] = Field(..., description="Improvements made")
    effectiveness_score: float = Field(..., ge=0, le=1, description="Expected effectiveness")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=OptimizedPrompt)
@prompt_template(
    """
    Optimize this prompt for better results:

    Original prompt:
    {original_prompt}

    Task goal: {goal}

    Analyze and improve:
    1. Clarity and specificity
    2. Structure and flow
    3. Context and examples
    4. Output guidance
    5. Edge case handling

    Explain each improvement made.
    """
)
def optimize_prompt(original_prompt: str, goal: str):
    """
    Optimize an existing prompt.

    Features:
    1. Prompt analysis
    2. Systematic improvement
    3. Effectiveness scoring

    Args:
        original_prompt: Prompt to optimize
        goal: What the prompt should achieve

    Returns:
        OptimizedPrompt with improvements
    """
    pass


# Prompt engineering assistant


class PromptEngineeringAdvice(BaseModel):
    """Model for prompt engineering advice."""

    task_type: str = Field(..., description="Type of task")
    recommended_structure: str = Field(..., description="Recommended prompt structure")
    key_components: list[str] = Field(..., description="Essential components to include")
    examples: list[str] = Field(..., description="Example prompts")
    common_pitfalls: list[str] = Field(..., description="Pitfalls to avoid")
    advanced_techniques: list[str] = Field(..., description="Advanced techniques to consider")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=PromptEngineeringAdvice)
@prompt_template(
    """
    Provide prompt engineering advice for this task type:

    Task type: {task_type}
    Specific requirements: {requirements:list}
    Target model: {model}

    Provide comprehensive guidance including:
    1. Optimal prompt structure
    2. Essential components
    3. Concrete examples
    4. Common mistakes to avoid
    5. Advanced techniques

    Focus on practical, actionable advice.
    """
)
def prompt_engineering_assistant(task_type: str, requirements: list[str] = None, model: str = "general LLM"):
    """
    Get prompt engineering advice for a task.

    Features:
    1. Task-specific guidance
    2. Best practices
    3. Example templates

    Args:
        task_type: Type of task
        requirements: Specific requirements
        model: Target model

    Returns:
        PromptEngineeringAdvice with guidance
    """
    if requirements is None:
        requirements = []
    pass


# Dynamic prompt adaptation


class AdaptivePrompt(BaseModel):
    """Model for adaptive prompts."""

    base_prompt: str = Field(..., description="Base prompt template")
    adaptations: dict[str, str] = Field(..., description="Context-specific adaptations")
    selection_criteria: dict[str, str] = Field(..., description="When to use each adaptation")
    fallback_prompt: str = Field(..., description="Fallback for edge cases")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=AdaptivePrompt)
@prompt_template(
    """
    Create an adaptive prompt system for:

    Task: {task}
    Contexts: {contexts:list}

    Design:
    1. A flexible base prompt
    2. Adaptations for each context
    3. Clear selection criteria
    4. Robust fallback option

    The system should handle various scenarios gracefully.
    """
)
def create_adaptive_prompt(task: str, contexts: list[str]):
    """
    Create adaptive prompt system.

    Features:
    1. Context-aware prompting
    2. Dynamic adaptation
    3. Fallback handling

    Args:
        task: Core task
        contexts: Different contexts to handle

    Returns:
        AdaptivePrompt system
    """
    pass


# Self-improving prompts


class SelfImprovingPrompt(BaseModel):
    """Model for self-improving prompts."""

    current_prompt: str = Field(..., description="Current prompt version")
    performance_analysis: str = Field(..., description="Performance analysis")
    identified_improvements: list[str] = Field(..., description="Improvements to make")
    next_version: str = Field(..., description="Improved prompt version")
    learning_notes: list[str] = Field(..., description="Learnings for future iterations")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Analyze prompt performance and suggest improvements:

    Current prompt:
    {current_prompt}

    Performance data:
    {performance_data:lists}

    Based on the results:
    1. What worked well?
    2. What didn't work?
    3. What improvements would help?

    Generate an improved version.
    """
)
def analyze_prompt_performance(current_prompt: str, performance_data: list[dict]) -> BaseDynamicConfig:
    """Analyze prompt performance."""
    formatted_data = []
    for data in performance_data:
        formatted_data.append(
            [
                f"Input: {data['input']}",
                f"Output: {data['output']}",
                f"Quality: {data['quality']}",
                f"Issues: {data.get('issues', 'None')}",
                "",
            ]
        )

    return {"computed_fields": {"performance_data": formatted_data}}


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=SelfImprovingPrompt)
@prompt_template(
    """
    Create next iteration of this self-improving prompt:

    Analysis: {analysis}

    Current version: {current_prompt}
    Iteration: {iteration}

    Incorporate learnings to create a better version.
    Document what you learned for future iterations.
    """
)
def create_improved_version(analysis: str, current_prompt: str, iteration: int):
    """Create improved prompt version."""
    pass


async def self_improving_prompt(initial_prompt: str, test_cases: list[dict], iterations: int = 3) -> list[SelfImprovingPrompt]:
    """
    Self-improving prompt through iterations.

    Features:
    1. Performance analysis
    2. Iterative improvement
    3. Learning accumulation

    Args:
        initial_prompt: Starting prompt
        test_cases: Test cases with quality scores
        iterations: Number of improvement iterations

    Returns:
        List of SelfImprovingPrompt iterations
    """
    improvements = []
    current_prompt = initial_prompt

    for i in range(iterations):
        # Analyze performance
        analysis = await analyze_prompt_performance(current_prompt=current_prompt, performance_data=test_cases)

        # Create improved version
        improvement = await create_improved_version(analysis=analysis.content, current_prompt=current_prompt, iteration=i + 1)

        improvements.append(improvement)
        current_prompt = improvement.next_version

        # Update test cases with new results (simplified)
        for test_case in test_cases:
            test_case['quality'] = min(test_case['quality'] + 0.1, 1.0)

    return improvements


# Meta-prompt templates


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Generate a meta-prompt template for {category} tasks:

    The template should:
    1. Be reusable across similar tasks
    2. Include placeholders for customization
    3. Incorporate best practices
    4. Handle edge cases

    Provide both the template and usage instructions.
    """
)
def generate_meta_template(category: str):
    """
    Generate reusable meta-prompt template.

    Features:
    1. Category-specific templates
    2. Customization support
    3. Usage guidance

    Args:
        category: Task category

    Returns:
        Meta-prompt template
    """
    pass
