# knowledge_graph_agent

> Agent for extracting structured knowledge from text by identifying entities and their relationships. Builds comprehensive knowledge graph representations with support for hierarchical relationships, graph enrichment, and visualization-ready outputs.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Agent for extracting structured knowledge from text by identifying entities and their relationships. Builds comprehensive knowledge graph representations with support for hierarchical relationships, graph enrichment, and visualization-ready outputs.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add knowledge_graph_agent
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**
- None

**Python Dependencies:**
- `mirascope` >=1.24.0
- `pydantic` >=2.0.0
- `lilypad` >=0.1.0

**Environment Variables:**
- `OPENAI_API_KEY`: API key for OpenAI services (if using OpenAI provider). (Optional)
- `ANTHROPIC_API_KEY`: API key for Anthropic services (if using Anthropic provider). (Optional)
- `GOOGLE_API_KEY`: API key for Google services (if using Google provider). (Optional)

### Basic Usage

```python
import asyncio
from knowledge_graph import (
    extract_knowledge_graph,
    extract_entities_only,
    extract_triples,
    build_domain_graph,
    visualize_graph_data
)

async def main():
    # Sample text for knowledge extraction
    text = """Apple Inc., founded by Steve Jobs and Steve Wozniak in 1976, is headquartered 
    in Cupertino, California. Tim Cook has served as CEO since 2011. The company's 
    flagship products include the iPhone, iPad, and Mac computers. Apple acquired 
    Beats Electronics in 2014 for $3 billion."""
    
    # Extract full knowledge graph
    graph = await extract_knowledge_graph(
        text=text,
        domain="technology",
        extraction_depth="deep"
    )
    
    print(f"Knowledge Graph Summary: {graph.summary}")
    print(f"\nEntities ({len(graph.entities)}):")
    for entity in graph.entities:
        print(f"  - {entity.name} ({entity.type}): {entity.properties}")
    
    print(f"\nRelationships ({len(graph.relationships)}):")
    for rel in graph.relationships:
        print(f"  - {rel.source_id} --[{rel.relationship_type}]--> {rel.target_id}")
    
    # Extract only entities
    entities = await extract_entities_only(text)
    print(f"\nEntity extraction only: {entities}")
    
    # Extract as triples
    triples = await extract_triples(text)
    print(f"\nTriple statements:")
    for s, p, o in triples:
        print(f"  - ({s}, {p}, {o})")
    
    # Visualize for Cytoscape
    viz_data = await visualize_graph_data(text, format="cytoscape")
    print(f"\nVisualization data (nodes: {len(viz_data['nodes'])}, edges: {len(viz_data['edges'])})")
    
    # Build domain graph from multiple texts
    texts = [text, "Microsoft was founded by Bill Gates and Paul Allen."]
    domain_graph = await build_domain_graph(texts, domain="technology")
    print(f"\nDomain graph: {domain_graph.summary}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Agent Configuration

### Template Variables

- `provider`: `openai`
- `model`: `gpt-4o-mini`
- `extraction_depth`: `standard`
- `domain`: `general`

### LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models
- **Groq**: Set `GROQ_API_KEY` for Groq models

Configure the provider and model using template variables or function parameters.

### Advanced Configuration

Configure template variables using CLI options or environment variables.

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with funcn tools for enhanced capabilities
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## Integration with Mirascope

This agent follows Mirascope best practices:

- Uses `@prompt_template` decorators for all prompts
- Implements Pydantic response models for structured outputs
- Supports async/await patterns for optimal performance
- Compatible with multiple LLM providers
- Includes comprehensive error handling
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## API Reference

See component source code for detailed API documentation.

## Advanced Examples

Check the examples directory for advanced usage patterns.

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await knowledge_graph_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await knowledge_graph_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from knowledge_graph_agent import knowledge_graph_agent_custom

result = await knowledge_graph_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

This agent extracts entities (Person, Organization, Location, Event, Product, Concept) and their relationships from text. Extraction depths: 'shallow' (entities only), 'standard' (entities + relationships), 'deep' (with enrichment and graph metrics). The agent can merge knowledge from multiple documents and output visualization-ready formats (Cytoscape, D3). Set your preferred LLM provider's API key.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add knowledge_graph_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes



---

**Key Benefits:**
- **Knowledge Graph**
- **Entity Extraction**
- **Relationship Extraction**
- **Agent**
- **Mirascope**

**Related Components:**
- None

**References:**
- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
