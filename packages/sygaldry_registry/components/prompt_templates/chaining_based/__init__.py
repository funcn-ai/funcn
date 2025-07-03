"""Chaining-based prompt engineering patterns using Mirascope."""

from .conditional_chain import conditional_basic, conditional_branching, conditional_dynamic
from .iterative_chain import iterative_convergence, iterative_refinement, iterative_validation
from .multi_step_reasoning import multi_step_analysis, multi_step_decision, multi_step_synthesis
from .parallel_chain import parallel_aggregation, parallel_async, parallel_basic
from .sequential_chain import sequential_basic, sequential_multi_step, sequential_with_context

__all__ = [
    # Sequential chains
    "sequential_basic",
    "sequential_with_context",
    "sequential_multi_step",
    # Parallel chains
    "parallel_basic",
    "parallel_aggregation",
    "parallel_async",
    # Conditional chains
    "conditional_basic",
    "conditional_branching",
    "conditional_dynamic",
    # Iterative chains
    "iterative_refinement",
    "iterative_validation",
    "iterative_convergence",
    # Multi-step reasoning
    "multi_step_analysis",
    "multi_step_synthesis",
    "multi_step_decision",
]
