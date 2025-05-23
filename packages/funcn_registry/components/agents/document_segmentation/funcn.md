# document_segmentation_agent

> Agent for intelligently segmenting documents into logical parts. Supports multiple strategies including semantic, structural, hybrid, and fixed-size segmentation. Features document structure analysis, segment summarization, and optimized chunking for vector embeddings.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Agent for intelligently segmenting documents into logical parts. Supports multiple strategies including semantic, structural, hybrid, and fixed-size segmentation. Features document structure analysis, segment summarization, and optimized chunking for vector embeddings.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add document_segmentation_agent
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
from document_segmentation import (
    segment_document,
    quick_segment,
    extract_sections,
    chunk_for_embedding
)

async def main():
    # Sample document
    document = """# Introduction
    This is a comprehensive guide to machine learning...
    
    ## Chapter 1: Fundamentals
    Machine learning is a subset of artificial intelligence...
    
    ### 1.1 Supervised Learning
    In supervised learning, we train models on labeled data...
    
    ## Chapter 2: Advanced Topics
    Deep learning extends traditional machine learning...
    
    ## Conclusion
    Machine learning continues to evolve rapidly..."""
    
    # Full document segmentation with auto-detection
    result = await segment_document(
        document=document,
        segmentation_method="auto",
        generate_summaries=True
    )
    
    print(f"Segmentation Summary: {result.summary}")
    print(f"Document Type: {result.document_structure.document_type}")
    print(f"\nSegments ({result.total_segments}):")
    for seg in result.segments:
        print(f"  - {seg.id}: {seg.title} ({seg.segment_type}, {len(seg.content)} chars)")
        if "summary" in seg.metadata:
            print(f"    Summary: {seg.metadata['summary']}")
    
    # Quick segmentation
    quick_segments = await quick_segment(document, max_segments=5)
    print(f"\nQuick segments: {quick_segments}")
    
    # Extract specific sections
    sections = await extract_sections(
        document=document,
        section_types=["introduction", "conclusion"]
    )
    print(f"\nExtracted sections: {list(sections.keys())}")
    
    # Chunk for embeddings
    chunks = await chunk_for_embedding(
        document=document,
        chunk_size=256,
        overlap=50
    )
    print(f"\nEmbedding chunks: {len(chunks)} chunks created")
    print(f"First chunk: {chunks[0]}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Agent Configuration

### Template Variables

- `provider`: `openai`
- `model`: `gpt-4o-mini`
- `segmentation_method`: `auto`
- `generate_summaries`: `True`

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
result_openai = await document_segmentation_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await document_segmentation_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from document_segmentation_agent import document_segmentation_agent_custom

result = await document_segmentation_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

This agent segments documents using various strategies: 'auto' (intelligent detection), 'semantic' (topic-based), 'structural' (heading-based), 'hybrid' (combined), or 'fixed_size' (character count). It analyzes document structure (research papers, reports, articles) and can generate summaries for each segment. The chunk_for_embedding function creates overlapping chunks optimized for vector databases. Set your preferred LLM provider's API key.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add document_segmentation_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes



---

**Key Benefits:**
- **Document Processing**
- **Segmentation**
- **Chunking**
- **Agent**
- **Mirascope**

**Related Components:**
- None

**References:**
- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
