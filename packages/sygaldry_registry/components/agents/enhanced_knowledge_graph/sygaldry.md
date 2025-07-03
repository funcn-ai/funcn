# enhanced_knowledge_graph_agent
> Enhanced knowledge graph extraction using advanced prompt engineering. Features meta-reasoning for strategy planning, chain-of-thought entity extraction with detailed reasoning, multi-pass relationship detection, and self-consistency validation for high-accuracy results.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Enhanced knowledge graph extraction using advanced prompt engineering. Features meta-reasoning for strategy planning, chain-of-thought entity extraction with detailed reasoning, multi-pass relationship detection, and self-consistency validation for high-accuracy results.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
sygaldry add enhanced_knowledge_graph_agent
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
from enhanced_knowledge_graph import extract_enhanced_knowledge_graph

async def main():
    # Sample text with complex relationships
    text = """Tesla, Inc., led by CEO Elon Musk, announced a partnership with Panasonic 
    to build a new Gigafactory in Nevada. The $5 billion facility will produce batteries 
    for Tesla's electric vehicles, including the Model 3, which was unveiled in 2016. 
    Musk, who also founded SpaceX and co-founded PayPal, stated that the factory will 
    employ over 6,500 workers and aims to reduce battery costs by 30%. The Nevada 
    government offered $1.3 billion in tax incentives to secure the project."""
    
    # Extract enhanced knowledge graph with full features
    result = await extract_enhanced_knowledge_graph(
        text=text,
        domain="business/technology",
        use_multi_pass=True,
        use_self_consistency=True,
        confidence_threshold=0.7
    )
    
    # Display extraction plan
    print("Extraction Strategy:")
    print(f"  Strategy: {result['extraction_plan']['extraction_strategy']}")
    print(f"  Entity Categories: {result['extraction_plan']['entity_categories']}")
    print(f"  Relationship Patterns: {result['extraction_plan']['relationship_patterns']}")
    
    # Display entities with reasoning
    print(f"\nEntities Found ({result['metadata']['total_entities']}):")
    for entity in result['entities']:
        print(f"\n  Entity: {entity['name']}")
        print(f"  Type: {entity['type']}")
        print(f"  Confidence: {entity['confidence']:.2f}")
        print(f"  Reasoning: {entity['reasoning']}")
        print(f"  Context Clues: {entity['context_clues']}")
    
    # Display relationships with evidence
    print(f"\nRelationships Found ({result['metadata']['total_relationships']}):")
    for rel in result['relationships']:
        print(f"\n  {rel['source']} --[{rel['type']}]--> {rel['target']}")
        print(f"  Confidence: {rel['confidence']:.2f}")
        print(f"  Reasoning: {rel['reasoning']}")
        print(f"  Evidence: '{rel['evidence']}'")
    
    # Display consistency validation
    if result['consistency_validation']:
        print(f"\nConsistency Validation:")
        print(f"  Consistent Entities: {result['consistency_validation']['consistent_entities']}")
        print(f"  Confidence Boost: {result['consistency_validation']['confidence_boost']}")
    
    # Display metadata
    print(f"\nMetadata:")
    print(f"  Average Confidence: {result['metadata']['avg_confidence']:.2f}")
    
    # Example without advanced features for comparison
    simple_result = await extract_enhanced_knowledge_graph(
        text=text,
        use_multi_pass=False,
        use_self_consistency=False
    )
    print(f"\nSimple extraction found {len(simple_result['entities'])} entities")
    print(f"Enhanced extraction found {len(result['entities'])} entities")

if __name__ == "__main__":
    asyncio.run(main())
```

## Agent Configuration

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with sygaldry tools for enhanced capabilities
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

### Template Variables

- `provider`: `openai`
- `model`: `gpt-4o-mini`
- `use_multi_pass`: `True`
- `use_self_consistency`: `True`
- `confidence_threshold`: `0.7`

### Advanced Configuration

Configure template variables using CLI options or environment variables.

### LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models
- **Groq**: Set `GROQ_API_KEY` for Groq models

Configure the provider and model using template variables or function parameters.

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

## Troubleshooting

This enhanced agent provides advanced knowledge graph extraction with:

1. **Meta-Reasoning**: Plans extraction strategy based on text type and domain
2. **Chain-of-Thought**: Detailed reasoning for each entity and relationship
3. **Multi-Pass Extraction**: 

   - Pass 1: Explicit relationships
   - Pass 2: Implicit relationships
   - Pass 3: Transitive relationships

4. **Self-Consistency**: Validates through multiple extraction attempts
5. **Confidence Scoring**: Evidence-based confidence with reasoning

The agent provides explanations for all extractions, making results interpretable and debuggable. Set your preferred LLM provider's API key.

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
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await enhanced_knowledge_graph_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await enhanced_knowledge_graph_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from enhanced_knowledge_graph_agent import enhanced_knowledge_graph_agent_custom

result = await enhanced_knowledge_graph_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `sygaldry add enhanced_knowledge_graph_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries
