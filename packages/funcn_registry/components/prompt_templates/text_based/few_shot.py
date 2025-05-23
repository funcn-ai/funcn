"""
Few-shot prompting examples using Mirascope.

Few-shot prompting provides the model with examples of the desired input-output
pattern before asking it to perform a similar task. This helps the model
understand the expected format and behavior.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field
from typing import List, Tuple


class ClassificationResult(BaseModel):
    """Model for classification outputs."""

    text: str = Field(..., description="The input text")
    category: str = Field(..., description="The assigned category")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence")
    reasoning: str = Field(..., description="Explanation for the classification")


class GeneratedContent(BaseModel):
    """Model for generated content."""

    content: str = Field(..., description="The generated content")
    style: str = Field(..., description="The style used")
    word_count: int = Field(..., description="Word count of generated content")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ClassificationResult)
@prompt_template(
    """
    Classify the sentiment of customer reviews. Here are some examples:

    Example 1:
    Review: "This product exceeded my expectations! Great quality and fast shipping."
    Sentiment: positive
    Reasoning: Expresses satisfaction with quality and service

    Example 2:
    Review: "Completely disappointed. The item broke after one use."
    Sentiment: negative
    Reasoning: Expresses dissatisfaction and product failure

    Example 3:
    Review: "It's okay, does what it's supposed to but nothing special."
    Sentiment: neutral
    Reasoning: Neither particularly positive nor negative, functional but unremarkable

    Now classify this review:
    Review: "{review}"

    Provide the sentiment classification with reasoning and confidence score.
    """
)
def few_shot_classification(review: str):
    """
    Basic few-shot classification example.

    This demonstrates:
    1. Clear example format
    2. Consistent structure across examples
    3. Explanation of reasoning in examples

    Args:
        review: Customer review to classify

    Returns:
        ClassificationResult with sentiment and reasoning
    """
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=GeneratedContent)
@prompt_template(
    """
    Generate a product description in the requested style. Here are examples:

    Example 1 - Technical Style:
    Input: Wireless headphones
    Output: "Advanced Bluetooth 5.0 wireless headphones featuring 40mm dynamic drivers,
    active noise cancellation, and 30-hour battery life. Frequency response: 20Hz-20kHz.
    Impedance: 32Ω. Includes USB-C fast charging."

    Example 2 - Marketing Style:
    Input: Coffee maker
    Output: "Transform your mornings with our revolutionary coffee maker! Experience
    barista-quality brews at the touch of a button. Wake up to the rich aroma of
    perfectly crafted coffee that energizes your day."

    Example 3 - Minimalist Style:
    Input: Notebook
    Output: "Simple. Elegant. 200 pages of premium paper. Leather cover. Made to last."

    Now generate a description for:
    Product: {product}
    Style: {style}
    """
)
def few_shot_generation(product: str, style: str):
    """
    Few-shot content generation with style examples.

    Demonstrates:
    1. Multiple style examples
    2. Consistent input-output format
    3. Style-specific generation

    Args:
        product: Product to describe
        style: Desired style (technical/marketing/minimalist)

    Returns:
        GeneratedContent with styled description
    """
    pass


# Dynamic few-shot with computed examples

class Example(BaseModel):
    """Model for dynamic examples."""

    input: str = Field(..., description="Example input")
    output: str = Field(..., description="Example output")
    explanation: str = Field(..., description="Why this output is correct")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    {task_description}

    Here are {num_examples} examples:

    {examples:lists}

    Now apply the same approach to:
    Input: {input}
    """
)
def dynamic_few_shot(
    task_description: str,
    examples: list[Example],
    input: str
) -> BaseDynamicConfig:
    """
    Dynamic few-shot prompting with variable examples.

    This advanced pattern allows:
    1. Variable number of examples
    2. Dynamic example selection
    3. Computed fields for formatting

    Args:
        task_description: Description of the task
        examples: List of examples to use
        input: New input to process

    Returns:
        Dynamic configuration with formatted examples
    """
    formatted_examples = []
    for i, example in enumerate(examples, 1):
        formatted_examples.append([
            f"Example {i}:",
            f"Input: {example.input}",
            f"Output: {example.output}",
            f"Explanation: {example.explanation}",
            ""  # Empty line for spacing
        ])

    return {
        "computed_fields": {
            "num_examples": len(examples),
            "examples": formatted_examples
        }
    }


# Advanced few-shot with contextual examples

class ContextualExample(BaseModel):
    """Model for contextual examples."""

    context: str = Field(..., description="Context of the example")
    question: str = Field(..., description="Question asked")
    answer: str = Field(..., description="Answer provided")
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence")


class ContextualAnswer(BaseModel):
    """Model for contextual answers."""

    answer: str = Field(..., description="The answer")
    sources: list[str] = Field(..., description="Parts of context used")
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ContextualAnswer)
@prompt_template(
    """
    Answer questions based on provided context. Here are examples:

    Example 1:
    Context: "Python was created by Guido van Rossum and first released in 1991.
    It emphasizes code readability and uses significant indentation."
    Question: "Who created Python?"
    Answer: "Guido van Rossum"
    Sources: ["Python was created by Guido van Rossum"]
    Confidence: 1.0

    Example 2:
    Context: "The Earth orbits the Sun at an average distance of 93 million miles.
    This distance is called an Astronomical Unit (AU)."
    Question: "How far is Earth from the Sun?"
    Answer: "93 million miles (1 AU)"
    Sources: ["The Earth orbits the Sun at an average distance of 93 million miles",
              "This distance is called an Astronomical Unit (AU)"]
    Confidence: 1.0

    Example 3:
    Context: "Machine learning models can be supervised or unsupervised.
    Supervised learning uses labeled data."
    Question: "What is deep learning?"
    Answer: "The context doesn't contain information about deep learning specifically."
    Sources: []
    Confidence: 0.0

    Now answer:
    Context: "{context}"
    Question: "{question}"
    """
)
def few_shot_contextual_qa(context: str, question: str):
    """
    Few-shot question answering with context.

    Demonstrates:
    1. Context-based examples
    2. Source attribution
    3. Confidence scoring
    4. Handling missing information

    Args:
        context: The context to search
        question: Question to answer

    Returns:
        ContextualAnswer with sources and confidence
    """
    pass


# Few-shot with adaptive examples

@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    call_params={"temperature": 0.2}  # Lower temperature for consistency
)
@prompt_template(
    """
    Task: {task}

    I'll show you {example_type} examples:

    {adaptive_examples:lists}

    Key patterns to notice:
    {patterns:list}

    Now apply these patterns to:
    {input}

    Remember to:
    - Follow the same format as the examples
    - Apply the identified patterns
    - Maintain consistency with the example style
    """
)
def few_shot_adaptive(
    task: str,
    input: str,
    example_type: str = "similar",
    examples: list[tuple[str, str]] = None,
    patterns: list[str] = None
) -> BaseDynamicConfig:
    """
    Adaptive few-shot prompting with pattern recognition.

    Advanced features:
    1. Adaptive example selection
    2. Pattern highlighting
    3. Format consistency enforcement

    Args:
        task: Task description
        input: Input to process
        example_type: Type of examples (similar/diverse/progressive)
        examples: List of (input, output) tuples
        patterns: Key patterns to highlight

    Returns:
        Processed result following example patterns
    """
    if examples is None:
        examples = [
            ("Simple input", "Simple output"),
            ("Complex input", "Complex output")
        ]

    if patterns is None:
        patterns = ["Consistent formatting", "Clear structure"]

    formatted_examples = []
    for i, (ex_input, ex_output) in enumerate(examples, 1):
        formatted_examples.append([
            f"Example {i}:",
            f"Input: {ex_input}",
            f"Output: {ex_output}",
            ""
        ])

    return {
        "computed_fields": {
            "adaptive_examples": formatted_examples
        }
    }
