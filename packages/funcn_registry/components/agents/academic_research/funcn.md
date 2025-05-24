# academic_research_agent

> Academic research agent for finding research papers using Exa websets. Perfect for academics, researchers, and anyone needing to discover scholarly publications.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Academic research agent for finding research papers using Exa websets. Perfect for academics, researchers, and anyone needing to discover scholarly publications.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add academic_research
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- `exa_websets`

**Python Dependencies:**

- `mirascope>=1.24.0`
- `pydantic>=2.0.0`

**Environment Variables:**

- `EXA_API_KEY`: API key for Exa (**Required**)

### Basic Usage

```python
from academic_research import academic_research_agent, find_papers_by_methodology

# Find papers on cell generation technology
result = await academic_research_agent(
    topic="cell generation technology",
    field="biology",
    journal_requirements=["published in major US journal"]
)

# Find papers disagreeing with transformer methodology
result = await find_papers_by_methodology(
    field="computer_science",
    methodology="transformer based model methodology for AI training",
    disagree_with="transformer"
)
```

## Agent Configuration

### Template Variables

- None

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
result_openai = await academic_research(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await academic_research(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from academic_research import academic_research_custom

result = await academic_research_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

Make sure to set your EXA_API_KEY environment variable before using this agent.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add academic_research` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes

---

**Key Benefits:**

- **Research**
- **Academic**
- **Papers**
- **Science**
- **Publications**

**Related Components:**

- `exa_websets`

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
