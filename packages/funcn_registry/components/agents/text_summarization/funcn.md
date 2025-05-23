# text_summarization_agent

> Advanced text summarization agent using chain-of-thought reasoning, few-shot learning, and iterative refinement. Supports multiple styles (technical, executive, simple, academic, journalistic) and progressive summarization with validation.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Advanced text summarization agent using chain-of-thought reasoning, few-shot learning, and iterative refinement. Supports multiple styles (technical, executive, simple, academic, journalistic) and progressive summarization with validation.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add text_summarization_agent
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
from text_summarization import (
    summarize_text,
    quick_summary,
    executive_brief,
    multi_style_summary
)

async def main():
    # Sample text
    text = """The breakthrough in quantum computing represents a paradigm shift in computational 
    capabilities. Researchers at MIT have successfully demonstrated a 127-qubit processor that 
    maintains coherence for unprecedented durations. This advancement addresses the fundamental 
    challenge of quantum decoherence that has plagued the field for decades. The implications 
    extend beyond theoretical physics into practical applications including cryptography, 
    drug discovery, and climate modeling. Industry leaders predict commercial viability within 
    five years, though significant engineering challenges remain."""
    
    # Generate summary with validation and refinement
    summary = await summarize_text(
        text=text,
        style="technical",
        validate=True
    )
    print(f"Technical Summary: {summary.summary}")
    print(f"Confidence: {summary.confidence_score}")
    print(f"Key points preserved: {summary.preserved_key_points}")
    
    # Generate progressive summaries
    progressive = await summarize_text(
        text=text,
        progressive=True
    )
    print(f"\nOne sentence: {progressive.one_sentence}")
    print(f"\nParagraph: {progressive.paragraph}")
    print(f"\nKey takeaways:")
    for takeaway in progressive.key_takeaways:
        print(f"  - {takeaway}")
    
    # Quick summary
    quick = await quick_summary(text)
    print(f"\nQuick summary: {quick}")
    
    # Executive brief with metrics
    brief = await executive_brief(text)
    print(f"\nExecutive Brief:")
    print(f"  One-liner: {brief['one_line']}")
    print(f"  Summary: {brief['summary']}")
    print(f"  Confidence: {brief['confidence']}")
    
    # Multi-style summaries
    styles = await multi_style_summary(text, ["technical", "simple", "executive"])
    print(f"\nMulti-style summaries:")
    for style, summary in styles.items():
        print(f"\n{style.capitalize()}: {summary}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Agent Configuration

### Template Variables

- `provider`: `openai`
- `model`: `gpt-4o-mini`
- `style`: `executive`
- `validate`: `True`

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
result_openai = await text_summarization_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await text_summarization_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from text_summarization_agent import text_summarization_agent_custom

result = await text_summarization_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

This agent provides advanced summarization capabilities with multiple techniques:

1. **Chain-of-Thought Analysis**: Analyzes text structure, complexity, and audience before summarization
2. **Few-Shot Learning**: Uses style-specific examples for consistent output
3. **Progressive Summarization**: Creates summaries at multiple detail levels
4. **Validation & Refinement**: Iteratively improves summaries based on quality checks
5. **Multiple Styles**: technical, executive, simple, academic, journalistic

The agent automatically determines optimal summary length and validates accuracy. Set your preferred LLM provider's API key.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add text_summarization_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes



---

**Key Benefits:**
- **Summarization**
- **Text Processing**
- **Agent**
- **Mirascope**
- **Chain Of Thought**

**Related Components:**
- None

**References:**
- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
