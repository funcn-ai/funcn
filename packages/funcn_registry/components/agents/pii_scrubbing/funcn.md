# pii_scrubbing_agent
> Agent for detecting and removing Personally Identifiable Information (PII) from text. Combines regex patterns and LLM analysis for comprehensive PII detection. Supports multiple scrubbing methods including masking, redaction, generalization, and synthetic data replacement.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Agent for detecting and removing Personally Identifiable Information (PII) from text. Combines regex patterns and LLM analysis for comprehensive PII detection. Supports multiple scrubbing methods including masking, redaction, generalization, and synthetic data replacement.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add pii_scrubbing_agent
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
from pii_scrubbing import (
    scrub_pii_from_text,
    quick_scrub,
    detect_pii_only,
    scrub_with_mapping
)

async def main():
    # Sample text with PII
    text = """John Doe's email is john.doe@example.com and his phone is 555-123-4567.
    His SSN is 123-45-6789 and he lives at 123 Main St, Anytown, USA.
    Credit card: 4111111111111111, IP: 192.168.1.1"""
    
    # Full PII scrubbing with hybrid detection
    result = await scrub_pii_from_text(
        text=text,
        detection_method="hybrid",
        scrubbing_method="mask"
    )
    print(f"Original: {result.original_text}")
    print(f"\nScrubbed: {result.scrubbed_text}")
    print(f"\nEntities removed: {len(result.entities_removed)}")
    for entity in result.entities_removed:
        print(f"  - {entity.entity_type}: {entity.text} (confidence: {entity.confidence})")
    
    # Quick scrub with defaults
    quick_result = await quick_scrub(text)
    print(f"\nQuick scrub result: {quick_result}")
    
    # Detection only (no scrubbing)
    detection = await detect_pii_only(text, method="hybrid")
    print(f"\nPII Detection: {detection}")
    
    # Scrub with synthetic data and mapping
    scrubbed_text, mapping = await scrub_with_mapping(
        text=text,
        scrubbing_method="synthetic"
    )
    print(f"\nSynthetic scrubbing: {scrubbed_text}")
    print(f"Mapping: {mapping}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Agent Configuration

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with funcn tools for enhanced capabilities
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

### Template Variables

- `provider`: `openai`
- `model`: `gpt-4o-mini`
- `detection_method`: `hybrid`
- `scrubbing_method`: `mask`

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

This agent detects and removes PII using hybrid approaches. Detection methods: 'regex' (fast pattern matching), 'llm' (context-aware detection), or 'hybrid' (both). Scrubbing methods: 'mask' (generic placeholders), 'redact' (asterisks), 'generalize' (less specific), or 'synthetic' (fake but realistic data). The agent handles various PII types including names, emails, phones, SSNs, credit cards, addresses, and more. Set your preferred LLM provider's API key.

## Migration Notes

---

**Key Benefits:**

- **Pii**
- **Privacy**
- **Data Protection**
- **Agent**
- **Mirascope**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add pii_scrubbing_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

### Custom Configuration

```python
# Custom configuration example
from pii_scrubbing_agent import pii_scrubbing_agent_custom

result = await pii_scrubbing_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await pii_scrubbing_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await pii_scrubbing_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```
