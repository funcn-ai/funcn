# recruiting_assistant_agent

> Recruiting assistant for finding qualified candidates using Exa websets. Helps with technical recruiting, sales hiring, and executive search.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Recruiting assistant for finding qualified candidates using Exa websets. Helps with technical recruiting, sales hiring, and executive search.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add recruiting_assistant_agent
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- `exa_websets`

**Python Dependencies:**

- `mirascope>=1.24.0`
- `pydantic>=2.0.0`

**Environment Variables:**

- ``: API key for Exa (**Required**)

### Basic Usage

```python
from recruiting_assistant import recruiting_assistant_agent, find_engineers_with_opensource

# Find engineers with open source experience
result = await find_engineers_with_opensource(
    skills=["Python", "FastAPI", "async"],
    startup_experience=True
)

# Find ML engineers from top universities
result = await recruiting_assistant_agent(
    role="ML Software Engineer",
    education="PhD from top 20 US university",
    skills=["machine learning", "deep learning"]
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
result_openai = await recruiting_assistant_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await recruiting_assistant_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from recruiting_assistant_agent import recruiting_assistant_agent_custom

result = await recruiting_assistant_agent_custom(
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
- **Dependency Conflicts**: Run `funcn add recruiting_assistant_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes

---

**Key Benefits:**

- **Recruiting**
- **Hiring**
- **Candidates**
- **Talent**
- **Hr**

**Related Components:**

- `exa_websets`

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
