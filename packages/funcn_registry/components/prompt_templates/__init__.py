"""
Mirascope Prompt Engineering Templates and Patterns

This module provides a comprehensive collection of prompt engineering examples and patterns
using Mirascope's functional approach. These templates serve as guides and examples for
AI agents and developers to adapt to specific use cases.

The templates are organized into categories:

1. **Text-Based Prompts** - Fundamental prompting techniques
   - Zero-shot prompting
   - Few-shot learning
   - Role-based prompts
   - Chain-of-thought prompting
   - Structured output generation

2. **Chaining-Based Prompts** - Dynamic prompt composition
   - Sequential chains
   - Parallel execution
   - Conditional flows
   - Iterative refinement
   - Multi-step reasoning

3. **Common Patterns** - Reusable prompt patterns
   - Summarization
   - Classification
   - Information extraction
   - Question answering
   - Content generation

4. **Advanced Techniques** - Sophisticated prompting strategies
   - Tree-of-thought
   - Self-consistency
   - Chain of verification
   - Rephrase and respond
   - Meta-prompting

Each template demonstrates:
- Proper use of @prompt_template decorators
- Dynamic configuration with computed fields
- Response model validation with Pydantic
- Async/parallel execution patterns
- Error handling and retries
- Integration with Lilypad for observability

These templates follow Mirascope best practices:
- Functional, declarative style
- Strong typing throughout
- Modular and composable design
- Clear documentation and examples
"""

# Text-based prompt techniques
# Advanced techniques
from .advanced_techniques import (
    chain_of_verification,
    meta_prompting,
    rephrase_and_respond,
    self_consistency,
    tree_of_thought,
)

# Chaining-based patterns
from .chaining_based import (
    conditional_chain,
    iterative_chain,
    multi_step_reasoning,
    parallel_chain,
    sequential_chain,
)

# Common prompt patterns
from .common_patterns import (
    classification,
    content_generation,
    extraction,
    question_answering,
    summarization,
)
from .text_based import (
    chain_of_thought,
    few_shot,
    role_based,
    structured_output,
    zero_shot,
)

__all__ = [
    # Text-based
    "zero_shot",
    "few_shot",
    "role_based",
    "chain_of_thought",
    "structured_output",
    # Chaining-based
    "sequential_chain",
    "parallel_chain",
    "conditional_chain",
    "iterative_chain",
    "multi_step_reasoning",
    # Common patterns
    "summarization",
    "classification",
    "extraction",
    "question_answering",
    "content_generation",
    # Advanced techniques
    "tree_of_thought",
    "self_consistency",
    "chain_of_verification",
    "rephrase_and_respond",
    "meta_prompting",
]
