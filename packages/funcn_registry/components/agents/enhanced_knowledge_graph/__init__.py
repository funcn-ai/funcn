"""Enhanced Knowledge Graph Agent.

This agent uses advanced prompt engineering techniques including meta-reasoning,
chain-of-thought extraction, multi-pass relationship detection, and self-consistency
validation to create highly accurate knowledge graphs with reasoning explanations.
"""

from .agent import (
    ConsistencyCheck,
    EntityWithReasoning,
    ExtractionPlan,
    RelationshipWithReasoning,
    extract_enhanced_knowledge_graph,
)

__all__ = [
    "extract_enhanced_knowledge_graph",
    "EntityWithReasoning",
    "RelationshipWithReasoning",
    "ExtractionPlan",
    "ConsistencyCheck",
]
