"""Text-based prompt engineering techniques using Mirascope."""

from .chain_of_thought import chain_of_thought_basic, chain_of_thought_math, chain_of_thought_reasoning
from .few_shot import dynamic_few_shot, few_shot_classification, few_shot_generation
from .role_based import role_based_analytical, role_based_creative, role_based_expert
from .structured_output import structured_extraction, structured_generation, structured_validation
from .zero_shot import zero_shot_example, zero_shot_with_context

__all__ = [
    # Zero-shot
    "zero_shot_example",
    "zero_shot_with_context",
    # Few-shot
    "few_shot_classification",
    "few_shot_generation",
    "dynamic_few_shot",
    # Role-based
    "role_based_expert",
    "role_based_creative",
    "role_based_analytical",
    # Chain of thought
    "chain_of_thought_basic",
    "chain_of_thought_math",
    "chain_of_thought_reasoning",
    # Structured output
    "structured_extraction",
    "structured_generation",
    "structured_validation",
]
