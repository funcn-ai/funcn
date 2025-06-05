from __future__ import annotations

from lilypad import trace
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


# Response models for structured outputs
class Entity(BaseModel):
    """A knowledge graph entity."""

    id: str = Field(..., description="Unique identifier for the entity")
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type (e.g., Person, Organization, Location, Event)")
    properties: dict[str, Any] = Field(default_factory=dict, description="Additional properties of the entity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for entity extraction")


class Relationship(BaseModel):
    """A relationship between two entities."""

    source_id: str = Field(..., description="ID of the source entity")
    target_id: str = Field(..., description="ID of the target entity")
    relationship_type: str = Field(..., description="Type of relationship (e.g., works_for, located_in, married_to)")
    properties: dict[str, Any] = Field(default_factory=dict, description="Additional properties of the relationship")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for relationship extraction")


class KnowledgeGraph(BaseModel):
    """A complete knowledge graph."""

    entities: list[Entity] = Field(..., description="List of entities in the graph")
    relationships: list[Relationship] = Field(..., description="List of relationships between entities")
    summary: str = Field(..., description="Summary of the knowledge graph")
    domain: str = Field(..., description="Domain or topic of the knowledge graph")


class TripleStatement(BaseModel):
    """A triple statement in the form (subject, predicate, object)."""

    subject: str = Field(..., description="Subject of the triple")
    predicate: str = Field(..., description="Predicate/relationship")
    object: str = Field(..., description="Object of the triple")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class EntityExtractionResponse(BaseModel):
    """Response for entity extraction step."""

    entities: list[Entity] = Field(..., description="Extracted entities")
    entity_mentions: dict[str, list[str]] = Field(default_factory=dict, description="Map of entity ID to text mentions")


class RelationshipExtractionResponse(BaseModel):
    """Response for relationship extraction step."""

    relationships: list[Relationship] = Field(..., description="Extracted relationships")
    triple_statements: list[TripleStatement] = Field(default_factory=list, description="Triple representations")


class GraphEnrichmentResponse(BaseModel):
    """Response for graph enrichment step."""

    enriched_entities: list[Entity] = Field(..., description="Entities with enriched properties")
    inferred_relationships: list[Relationship] = Field(..., description="Additional inferred relationships")
    graph_metrics: dict[str, Any] = Field(default_factory=dict, description="Graph analysis metrics")


# Step 1: Extract entities from text
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=EntityExtractionResponse,
)
@prompt_template(
    """
    You are an expert in knowledge extraction and named entity recognition.

    Extract all entities from the following text:

    Text: "{text}"

    Entity types to look for:
    - Person: individuals, including historical figures, celebrities, etc.
    - Organization: companies, institutions, governments, groups
    - Location: countries, cities, landmarks, geographical features
    - Event: historical events, meetings, conferences, incidents
    - Product: products, services, technologies
    - Concept: abstract concepts, theories, ideologies
    - Date/Time: specific dates, time periods, eras
    - Other: any other notable entities

    For each entity:
    1. Assign a unique ID (e.g., "person_1", "org_2")
    2. Identify the entity name as it appears
    3. Classify its type
    4. Extract relevant properties (e.g., role, description, date)
    5. Note all text mentions/variations
    6. Assign confidence score (0.0-1.0)

    Be comprehensive and extract ALL entities, even if mentioned only once.
    """
)
async def extract_entities(text: str):
    """Extract entities from text."""
    pass


# Step 2: Extract relationships between entities
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=RelationshipExtractionResponse,
)
@prompt_template(
    """
    You are an expert in relationship extraction and knowledge graph construction.

    Given the text and extracted entities, identify all relationships:

    Text: "{text}"

    Entities found:
    {entities}

    Common relationship types:
    - Professional: works_for, manages, colleague_of, founded, owns
    - Personal: married_to, child_of, sibling_of, friend_of
    - Spatial: located_in, headquartered_in, lives_in, near
    - Temporal: happened_before, happened_after, concurrent_with
    - Causal: caused_by, leads_to, prevents, enables
    - Part-whole: part_of, contains, member_of, belongs_to
    - Other: any domain-specific relationships

    For each relationship:
    1. Identify source and target entities (use their IDs)
    2. Determine relationship type
    3. Extract any properties (e.g., start_date, end_date, role)
    4. Create triple statements (subject, predicate, object)
    5. Assign confidence score

    Look for both explicit and implicit relationships in the text.
    """
)
async def extract_relationships(text: str, entities: str):
    """Extract relationships between entities."""
    pass


# Step 3: Enrich and analyze the knowledge graph
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=GraphEnrichmentResponse,
)
@prompt_template(
    """
    You are an expert in knowledge graph analysis and enrichment.

    Given the extracted knowledge graph, enrich and analyze it:

    Entities:
    {entities}

    Relationships:
    {relationships}

    Domain: {domain}

    Tasks:
    1. Enrich entities with additional inferred properties
    2. Identify missing or implicit relationships
    3. Resolve entity coreferences and merge duplicates
    4. Add hierarchical relationships where applicable
    5. Calculate graph metrics:
       - Node centrality (most connected entities)
       - Clustering coefficient
       - Path analysis
       - Community detection

    Consider domain-specific patterns and common knowledge to infer additional information.
    """
)
async def enrich_knowledge_graph(entities: str, relationships: str, domain: str):
    """Enrich and analyze the knowledge graph."""
    pass


# Main knowledge graph extraction function
@trace()
async def extract_knowledge_graph(
    text: str,
    domain: str = "general",
    extraction_depth: Literal["shallow", "standard", "deep"] = "standard",
    include_metrics: bool = True,
    merge_similar_entities: bool = True,
    confidence_threshold: float = 0.6,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> KnowledgeGraph:
    """
    Extract a knowledge graph from text.

    This agent extracts entities and relationships from text to build
    a structured knowledge graph representation.

    Args:
        text: Text to extract knowledge from
        domain: Domain context for extraction
        extraction_depth: How deeply to analyze the text
        include_metrics: Whether to calculate graph metrics
        merge_similar_entities: Whether to merge similar entities
        confidence_threshold: Minimum confidence for inclusion
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        KnowledgeGraph with entities, relationships, and analysis
    """
    # Step 1: Extract entities
    entity_response = await extract_entities(text)

    # Filter by confidence
    filtered_entities = [e for e in entity_response.entities if e.confidence >= confidence_threshold]

    if not filtered_entities:
        return KnowledgeGraph(entities=[], relationships=[], summary="No entities found in the text.", domain=domain)

    # Step 2: Extract relationships
    entities_str = "\n".join([f"- {e.id}: {e.name} ({e.type})" for e in filtered_entities])

    relationship_response = await extract_relationships(text=text, entities=entities_str)

    # Filter relationships by confidence
    filtered_relationships = [r for r in relationship_response.relationships if r.confidence >= confidence_threshold]

    # Step 3: Enrich if deep extraction is requested
    if extraction_depth == "deep" or include_metrics:
        entities_json = str([e.model_dump() for e in filtered_entities])
        relationships_json = str([r.model_dump() for r in filtered_relationships])

        enrichment_response = await enrich_knowledge_graph(
            entities=entities_json, relationships=relationships_json, domain=domain
        )

        # Update entities with enriched versions
        entity_map = {e.id: e for e in enrichment_response.enriched_entities}
        filtered_entities = [entity_map.get(e.id, e) for e in filtered_entities]

        # Add inferred relationships
        filtered_relationships.extend(enrichment_response.inferred_relationships)

    # Generate summary
    summary = f"Knowledge graph for {domain} domain with {len(filtered_entities)} entities and {len(filtered_relationships)} relationships."

    return KnowledgeGraph(entities=filtered_entities, relationships=filtered_relationships, summary=summary, domain=domain)


# Convenience functions
async def extract_entities_only(text: str) -> list[dict[str, Any]]:
    """
    Extract only entities from text.

    Returns a list of entity dictionaries.
    """
    result = await extract_knowledge_graph(text=text, extraction_depth="shallow")

    return [{"name": e.name, "type": e.type, "properties": e.properties} for e in result.entities]


async def extract_triples(text: str) -> list[tuple[str, str, str]]:
    """
    Extract knowledge as triple statements.

    Returns list of (subject, predicate, object) tuples.
    """
    result = await extract_knowledge_graph(text)

    triples = []
    entity_map = {e.id: e.name for e in result.entities}

    for rel in result.relationships:
        subject = entity_map.get(rel.source_id, rel.source_id)
        object = entity_map.get(rel.target_id, rel.target_id)
        triples.append((subject, rel.relationship_type, object))

    return triples


async def build_domain_graph(texts: list[str], domain: str) -> KnowledgeGraph:
    """
    Build a knowledge graph from multiple texts in a domain.

    Combines knowledge from multiple sources.
    """
    all_entities = []
    all_relationships = []
    entity_id_map = {}

    for i, text in enumerate(texts):
        graph = await extract_knowledge_graph(text=text, domain=domain, extraction_depth="deep")

        # Remap entity IDs to avoid conflicts
        for entity in graph.entities:
            new_id = f"{entity.id}_doc{i}"
            entity_id_map[entity.id] = new_id
            entity.id = new_id
            all_entities.append(entity)

        # Update relationship IDs
        for rel in graph.relationships:
            rel.source_id = entity_id_map.get(rel.source_id, rel.source_id)
            rel.target_id = entity_id_map.get(rel.target_id, rel.target_id)
            all_relationships.append(rel)

    return KnowledgeGraph(
        entities=all_entities,
        relationships=all_relationships,
        summary=f"Combined knowledge graph from {len(texts)} documents in {domain} domain.",
        domain=domain,
    )


async def visualize_graph_data(text: str, format: Literal["cytoscape", "d3", "graphviz"] = "cytoscape") -> dict[str, Any]:
    """
    Extract knowledge graph in a format ready for visualization.

    Returns data formatted for the specified visualization library.
    """
    graph = await extract_knowledge_graph(text)

    if format == "cytoscape":
        # Format for Cytoscape.js
        nodes = [{"data": {"id": e.id, "label": e.name, "type": e.type, **e.properties}} for e in graph.entities]

        edges = [
            {
                "data": {
                    "id": f"{r.source_id}_{r.target_id}",
                    "source": r.source_id,
                    "target": r.target_id,
                    "label": r.relationship_type,
                    **r.properties,
                }
            }
            for r in graph.relationships
        ]

        return {"nodes": nodes, "edges": edges}

    # Add other formats as needed
    return {"entities": graph.entities, "relationships": graph.relationships}
