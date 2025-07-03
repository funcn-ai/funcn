# hallucination_detector_agent
> AI-powered hallucination detection agent that verifies factual claims using Exa search

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

AI-powered hallucination detection agent that verifies factual claims using Exa search

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
sygaldry add hallucination_detector_agent
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- `exa_search`

**Python Dependencies:**

- `mirascope[openai]` >=1.24.0
- `pydantic` >=2.0.0
- `exa-py` >=1.0.0

**Environment Variables:**

- `EXA_API_KEY`: API key for Exa services (**Required**)
- `OPENAI_API_KEY`: API key for OpenAI services (**Required**)

### Basic Usage

```python
from ai_agents.hallucination_detector import detect_hallucinations

async def main():
    text = "The Eiffel Tower was built in 1889 in Paris. It is made entirely of gold."
    result = await detect_hallucinations(text)
    print(f"Hallucination Score: {result.hallucination_score}")
    print(f"Assessment: {result.overall_assessment}")
    
    # Quick check
    quick_result = await detect_hallucinations_quick(text)
    if quick_result["is_hallucinated"]:
        print("Text contains hallucinations!")
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
- `search_type`: `neural`
- `max_sources_per_claim`: `5`

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

You can now import the hallucination detector with `from ai_agents.hallucination_detector import detect_hallucinations`. Make sure to set your EXA_API_KEY and OPENAI_API_KEY environment variables. The agent provides:

1. `detect_hallucinations()` - Full analysis with detailed results
2. `detect_hallucinations_quick()` - Simple true/false check
3. `verify_single_statement()` - Check individual claims

For optional tracing, install lilypad: `pip install lilypad`.

## Migration Notes

---

**Key Benefits:**

- **Hallucination**
- **Fact-Checking**
- **Verification**
- **Exa**
- **Claims**

**Related Components:**

- `exa_search`

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await hallucination_detector_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await hallucination_detector_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from hallucination_detector_agent import hallucination_detector_agent_custom

result = await hallucination_detector_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `sygaldry add hallucination_detector_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries
