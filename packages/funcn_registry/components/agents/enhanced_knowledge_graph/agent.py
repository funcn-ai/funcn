from __future__ import annotations

import json
from lilypad import trace
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


# Enhanced response models with reasoning
class EntityWithReasoning(BaseModel):
    """Entity with extraction reasoning."""
    entity: str = Field(..., description="The entity name")
    type: str = Field(..., description="Entity type")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Why this was identified as an entity")
    context_clues: list[str] = Field(..., description="Context clues used")


class RelationshipWithReasoning(BaseModel):
    """Relationship with extraction reasoning."""
    source: str = Field(..., description="Source entity")
    target: str = Field(..., description="Target entity")
    relationship: str = Field(..., description="Relationship type")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Why this relationship exists")
    evidence: str = Field(..., description="Text evidence for the relationship")


class ExtractionPlan(BaseModel):
    """Plan for knowledge extraction."""
    extraction_strategy: str = Field(..., description="Strategy for extraction")
    entity_categories: list[str] = Field(..., description="Entity categories to focus on")
    relationship_patterns: list[str] = Field(..., description="Relationship patterns to look for")
    complexity_assessment: str = Field(..., description="Assessment of text complexity")
    special_considerations: list[str] = Field(..., description="Special considerations for this text")


class ConsistencyCheck(BaseModel):
    """Results of consistency checking."""
    consistent_entities: list[str] = Field(..., description="Entities found consistently")
    conflicting_entities: list[tuple[str, str]] = Field(..., description="Conflicting entity interpretations")
    consistent_relationships: list[str] = Field(..., description="Consistently found relationships")
    confidence_boost: float = Field(..., description="Confidence boost from consistency")


# Step 1: Plan extraction strategy (meta-reasoning)
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=ExtractionPlan,
)
@prompt_template(
    """
    You are a knowledge extraction strategist. Plan the best approach for extracting knowledge from this text.

    Text preview: "{text_preview}"
    Domain: {domain}

    Consider:
    1. What type of text is this? (narrative, technical, news, academic)
    2. What entity types are likely present?
    3. What relationship patterns should we look for?
    4. Any domain-specific considerations?
    5. Potential challenges in extraction?

    Examples of good extraction strategies:
    - Technical text → Focus on: systems, components, specifications, dependencies
    - Business text → Focus on: companies, people, roles, transactions, partnerships
    - Scientific text → Focus on: concepts, methods, findings, researchers, institutions

    Create a comprehensive extraction plan.
    """
)
async def plan_extraction(text_preview: str, domain: str):
    """Plan extraction strategy using meta-reasoning."""
    pass


# Step 2: Extract entities with reasoning (CoT + Few-shot)
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=list[EntityWithReasoning],
)
@prompt_template(
    """
    Extract entities with detailed reasoning. Think step-by-step for each entity.

    Text: "{text}"
    Strategy: {strategy}
    Entity categories: {categories}

    For each entity, explain:
    1. Why it's an entity (not just a common noun)
    2. How you determined its type
    3. What context clues you used
    4. Your confidence level

    Examples with reasoning:

    Text: "Apple Inc. was founded by Steve Jobs in Cupertino."
    Extracted:
    - Entity: "Apple Inc.", Type: Organization
      Reasoning: "Inc." suffix indicates company, capitalized, acts as subject
      Context clues: ["Inc. suffix", "was founded", "company actions"]

    - Entity: "Steve Jobs", Type: Person
      Reasoning: Full name format, founder role, human action verb
      Context clues: ["founded by", "person name pattern", "historical figure"]

    - Entity: "Cupertino", Type: Location
      Reasoning: Place where founding occurred, geographic preposition "in"
      Context clues: ["in <location>", "place of action", "city name"]

    Now extract with similar detailed reasoning:
    """
)
async def extract_entities_with_reasoning(
    text: str,
    strategy: str,
    categories: str
):
    """Extract entities with chain-of-thought reasoning."""
    pass


# Step 3: Multi-pass relationship extraction
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=list[RelationshipWithReasoning],
)
@prompt_template(
    """
    Extract relationships between entities. Use multi-pass reasoning.

    Text: "{text}"
    Entities found: {entities}
    Relationship patterns: {patterns}

    Pass 1: Identify explicit relationships (stated directly)
    Pass 2: Infer implicit relationships (from context)
    Pass 3: Deduce transitive relationships (if A→B and B→C, then A→C)

    For each relationship:
    1. Quote the evidence from text
    2. Explain your reasoning
    3. Rate your confidence

    Example reasoning:
    Text: "Tim Cook, CEO of Apple, announced the iPhone 15 in Cupertino."

    Explicit: Tim Cook --[role]--> CEO (Evidence: "CEO of Apple")
    Implicit: Tim Cook --[works_at]--> Apple (Reasoning: CEO role implies employment)
    Implicit: iPhone 15 --[made_by]--> Apple (Reasoning: CEO announces company products)
    Spatial: announcement --[location]--> Cupertino (Evidence: "in Cupertino")

    Extract relationships with similar reasoning:
    """
)
async def extract_relationships_multipass(
    text: str,
    entities: str,
    patterns: str
):
    """Extract relationships using multi-pass reasoning."""
    pass


# Step 4: Self-consistency validation
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=ConsistencyCheck,
)
@prompt_template(
    """
    Validate extraction consistency across multiple interpretations.

    Text: "{text}"

    Extraction attempt 1: {extraction1}
    Extraction attempt 2: {extraction2}
    Extraction attempt 3: {extraction3}

    Compare the three extractions:
    1. Which entities appear in all three?
    2. Which entities have conflicting types/interpretations?
    3. Which relationships are consistent?
    4. What's the overall agreement level?

    Higher consistency = higher confidence in extraction.
    """
)
async def validate_consistency(
    text: str,
    extraction1: str,
    extraction2: str,
    extraction3: str
):
    """Validate extraction consistency."""
    pass


# Enhanced main extraction function
@trace()
async def extract_enhanced_knowledge_graph(
    text: str,
    domain: str = "general",
    use_multi_pass: bool = True,
    use_self_consistency: bool = True,
    num_consistency_checks: int = 3,
    confidence_threshold: float = 0.7,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini"
) -> dict[str, Any]:
    """
    Extract knowledge graph using advanced prompt engineering.

    Features:
    - Meta-reasoning for extraction planning
    - Chain-of-thought entity extraction
    - Multi-pass relationship extraction
    - Self-consistency validation
    - Confidence scoring with reasoning

    Args:
        text: Text to extract from
        domain: Domain context
        use_multi_pass: Use multi-pass extraction
        use_self_consistency: Validate with self-consistency
        num_consistency_checks: Number of extraction attempts for consistency
        confidence_threshold: Minimum confidence threshold
        llm_provider: LLM provider
        model: Model to use

    Returns:
        Enhanced knowledge graph with reasoning and confidence scores
    """
    # Step 1: Plan extraction
    text_preview = text[:500] + "..." if len(text) > 500 else text
    plan = await plan_extraction(text_preview, domain)

    # Step 2: Extract entities with reasoning
    categories_str = ", ".join(plan.entity_categories)
    entities_with_reasoning = await extract_entities_with_reasoning(
        text=text,
        strategy=plan.extraction_strategy,
        categories=categories_str
    )

    # Step 3: Multi-pass relationship extraction if enabled
    if use_multi_pass:
        entities_str = "\n".join([
            f"- {e.entity} ({e.type})"
            for e in entities_with_reasoning
        ])
        patterns_str = ", ".join(plan.relationship_patterns)

        relationships = await extract_relationships_multipass(
            text=text,
            entities=entities_str,
            patterns=patterns_str
        )
    else:
        relationships = []

    # Step 4: Self-consistency validation if enabled
    if use_self_consistency:
        # Run multiple extractions
        extractions = []
        for i in range(num_consistency_checks):
            # Add slight variation to prompt to get different interpretations
            variation = f" (Attempt {i+1}: Focus on {'precision' if i == 0 else 'recall' if i == 1 else 'balance'})"

            entities_attempt = await extract_entities_with_reasoning(
                text=text + variation,
                strategy=plan.extraction_strategy,
                categories=categories_str
            )
            extractions.append(entities_attempt)

        # Validate consistency
        consistency = await validate_consistency(
            text=text,
            extraction1=json.dumps([e.model_dump() for e in extractions[0]]),
            extraction2=json.dumps([e.model_dump() for e in extractions[1]]),
            extraction3=json.dumps([e.model_dump() for e in extractions[2]])
        )

        # Boost confidence for consistent extractions
        for entity in entities_with_reasoning:
            if entity.entity in consistency.consistent_entities:
                entity.confidence = min(1.0, entity.confidence + consistency.confidence_boost)

    # Filter by confidence
    filtered_entities = [
        e for e in entities_with_reasoning
        if e.confidence >= confidence_threshold
    ]

    filtered_relationships = [
        r for r in relationships
        if r.confidence >= confidence_threshold
    ]

    return {
        "extraction_plan": plan.model_dump(),
        "entities": [
            {
                "name": e.entity,
                "type": e.type,
                "confidence": e.confidence,
                "reasoning": e.reasoning,
                "context_clues": e.context_clues
            }
            for e in filtered_entities
        ],
        "relationships": [
            {
                "source": r.source,
                "target": r.target,
                "type": r.relationship,
                "confidence": r.confidence,
                "reasoning": r.reasoning,
                "evidence": r.evidence
            }
            for r in filtered_relationships
        ],
        "consistency_validation": consistency.model_dump() if use_self_consistency else None,
        "metadata": {
            "domain": domain,
            "extraction_strategy": plan.extraction_strategy,
            "total_entities": len(filtered_entities),
            "total_relationships": len(filtered_relationships),
            "avg_confidence": sum(e.confidence for e in filtered_entities) / len(filtered_entities) if filtered_entities else 0
        }
    }
