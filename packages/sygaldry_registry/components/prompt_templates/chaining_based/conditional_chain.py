"""
Conditional chaining examples using Mirascope.

Conditional chains dynamically adjust their execution path based on intermediate
results, enabling adaptive and context-aware prompt flows.
"""

import lilypad
from enum import Enum
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field

# Basic conditional routing


class ContentType(str, Enum):
    """Content type enumeration."""

    TECHNICAL = "technical"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    EDUCATIONAL = "educational"


class ClassificationResult(BaseModel):
    """Model for content classification."""

    content_type: ContentType = Field(..., description="Type of content")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence")
    reasoning: str = Field(..., description="Reasoning for classification")


class ProcessedContent(BaseModel):
    """Model for processed content."""

    original: str = Field(..., description="Original content")
    processed: str = Field(..., description="Processed content")
    processing_type: str = Field(..., description="Type of processing applied")
    enhancements: list[str] = Field(..., description="Enhancements made")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ClassificationResult)
@prompt_template(
    """
    Classify this content into one of these types:
    - technical: Code, documentation, technical specifications
    - creative: Stories, poems, artistic content
    - analytical: Data analysis, reports, research
    - educational: Tutorials, explanations, teaching materials

    Content: {content}

    Provide classification with confidence and reasoning.
    """
)
def classify_content(content: str):
    """Classify content type."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ProcessedContent)
@prompt_template(
    """
    Process this {content_type} content with appropriate enhancements:

    Content: {content}

    For {content_type} content, apply:
    {processing_instructions}

    Enhance while maintaining the original intent.
    """
)
def process_by_type(content: str, content_type: ContentType, processing_instructions: str):
    """Process content based on its type."""
    pass


def conditional_basic(content: str) -> ProcessedContent:
    """
    Basic conditional chain based on content type.

    This demonstrates:
    1. Initial classification
    2. Conditional routing
    3. Type-specific processing

    Args:
        content: Content to process

    Returns:
        ProcessedContent with type-specific enhancements
    """
    # Step 1: Classify content
    classification = classify_content(content)

    # Step 2: Route to appropriate processor
    processing_map = {
        ContentType.TECHNICAL: "Add code examples, clarify technical terms, improve structure",
        ContentType.CREATIVE: "Enhance imagery, improve flow, add emotional depth",
        ContentType.ANALYTICAL: "Add data visualizations, strengthen arguments, clarify insights",
        ContentType.EDUCATIONAL: "Add examples, improve clarity, include practice exercises",
    }

    # Step 3: Process based on classification
    processed = process_by_type(
        content=content,
        content_type=classification.content_type,
        processing_instructions=processing_map[classification.content_type],
    )

    return processed


# Advanced conditional branching


class ComplexityLevel(str, Enum):
    """Complexity level enumeration."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


class ComplexityAssessment(BaseModel):
    """Model for complexity assessment."""

    level: ComplexityLevel = Field(..., description="Complexity level")
    factors: list[str] = Field(..., description="Factors contributing to complexity")
    score: float = Field(..., ge=0, le=10, description="Complexity score")


class AdaptedResponse(BaseModel):
    """Model for adapted responses."""

    response: str = Field(..., description="The adapted response")
    adaptation_strategy: str = Field(..., description="Strategy used for adaptation")
    target_audience: str = Field(..., description="Target audience description")
    readability_score: float = Field(..., ge=0, le=100, description="Readability score")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ComplexityAssessment)
@prompt_template(
    """
    Assess the complexity of this topic:

    Topic: {topic}
    Context: {context}

    Consider:
    1. Technical depth required
    2. Prior knowledge needed
    3. Abstract concepts involved
    4. Interdisciplinary connections

    Rate complexity and identify contributing factors.
    """
)
def assess_complexity(topic: str, context: str):
    """Assess topic complexity."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=AdaptedResponse)
@prompt_template(
    """
    Create an explanation of this topic adapted for {complexity_level} level:

    Topic: {topic}
    Audience characteristics: {audience_profile}

    Adaptation guidelines:
    {adaptation_guidelines:list}

    Ensure appropriate depth and accessibility.
    """
)
def create_adapted_explanation(
    topic: str, complexity_level: ComplexityLevel, audience_profile: str, adaptation_guidelines: list[str]
):
    """Create complexity-adapted explanation."""
    pass


def conditional_branching(topic: str, context: str = "general audience") -> AdaptedResponse:
    """
    Conditional branching based on complexity assessment.

    Features:
    1. Dynamic complexity assessment
    2. Multi-branch routing
    3. Audience-adapted responses

    Args:
        topic: Topic to explain
        context: Context for explanation

    Returns:
        AdaptedResponse tailored to complexity
    """
    # Assess complexity
    complexity = assess_complexity(topic, context)

    # Define adaptation strategies
    adaptation_map = {
        ComplexityLevel.SIMPLE: {
            "profile": "general audience with no technical background",
            "guidelines": [
                "Use everyday language",
                "Include relatable examples",
                "Avoid jargon",
                "Focus on practical applications",
            ],
        },
        ComplexityLevel.MODERATE: {
            "profile": "educated audience with some domain knowledge",
            "guidelines": [
                "Balance technical accuracy with clarity",
                "Define key terms",
                "Use analogies for complex concepts",
                "Include some technical details",
            ],
        },
        ComplexityLevel.COMPLEX: {
            "profile": "professionals or advanced students",
            "guidelines": [
                "Include technical depth",
                "Reference relevant theories",
                "Discuss nuances and edge cases",
                "Assume foundational knowledge",
            ],
        },
        ComplexityLevel.EXPERT: {
            "profile": "domain experts and researchers",
            "guidelines": [
                "Focus on cutting-edge aspects",
                "Include mathematical formulations",
                "Discuss open problems",
                "Reference recent research",
            ],
        },
    }

    # Get adaptation strategy
    strategy = adaptation_map[complexity.level]

    # Create adapted explanation
    adapted = create_adapted_explanation(
        topic=topic,
        complexity_level=complexity.level,
        audience_profile=strategy["profile"],
        adaptation_guidelines=strategy["guidelines"],
    )

    return adapted


# Dynamic conditional flow


class DecisionPoint(BaseModel):
    """Model for decision points in conditional flow."""

    decision_id: str = Field(..., description="Unique decision identifier")
    question: str = Field(..., description="Decision question")
    options: dict[str, str] = Field(..., description="Available options")
    selected: str = Field(..., description="Selected option")
    reasoning: str = Field(..., description="Reasoning for selection")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=DecisionPoint)
@prompt_template(
    """
    Make a decision for this scenario:

    Context: {context}
    Decision Point: {decision_id}
    Question: {question}

    Available options:
    {options:lists}

    Previous decisions:
    {previous_decisions:list}

    Select the best option with clear reasoning.
    """
)
def make_decision(
    context: str, decision_id: str, question: str, options: dict[str, str], previous_decisions: list[str]
) -> BaseDynamicConfig:
    """Make a decision at a conditional branch point."""
    formatted_options = []
    for key, desc in options.items():
        formatted_options.append([f"- {key}: {desc}"])

    return {"computed_fields": {"options": formatted_options}}


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Execute action based on decision path:

    Decision Path:
    {decision_path:lists}

    Action Type: {action_type}
    Context: {context}

    Provide comprehensive output for this action.
    """
)
def execute_action(decision_path: list[DecisionPoint], action_type: str, context: str) -> BaseDynamicConfig:
    """Execute action based on decision path."""
    formatted_path = []
    for dp in decision_path:
        formatted_path.append([f"Decision {dp.decision_id}:", f"Q: {dp.question}", f"A: {dp.selected} - {dp.reasoning}", ""])

    return {"computed_fields": {"decision_path": formatted_path}}


def conditional_dynamic(context: str, decision_tree: dict[str, dict]) -> dict:
    """
    Dynamic conditional flow with decision tree.

    Features:
    1. Dynamic decision tree navigation
    2. Context-aware branching
    3. Path tracking and execution

    Args:
        context: Context for decisions
        decision_tree: Tree structure of decisions

    Returns:
        Dict with decision path and final result
    """
    decision_path = []
    current_node = "start"
    previous_decisions: list[str] = []

    # Navigate decision tree
    while current_node in decision_tree:
        node = decision_tree[current_node]

        # Make decision
        decision = make_decision(
            context=context,
            decision_id=current_node,
            question=node["question"],
            options=node["options"],
            previous_decisions=previous_decisions,
        )

        decision_path.append(decision)
        previous_decisions.append(f"{decision.question} -> {decision.selected}")

        # Move to next node
        current_node = node.get("next", {}).get(decision.selected, "end")

    # Execute final action
    final_action = execute_action(
        decision_path=decision_path, action_type=decision_tree.get("final_action", "summary"), context=context
    )

    return {
        "decision_path": decision_path,
        "final_result": final_action.content,
        "path_summary": " -> ".join([d.selected for d in decision_path]),
    }
