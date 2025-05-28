# sales_intelligence_agent
> Sales intelligence agent for finding targeted business contacts and companies using Exa websets. Perfect for sales prospecting, lead generation, and market intelligence.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Sales intelligence agent for finding targeted business contacts and companies using Exa websets. Perfect for sales prospecting, lead generation, and market intelligence.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add sales_intelligence_agent
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
from sales_intelligence import sales_intelligence_agent, find_sales_leaders

# Find sales leaders in Europe
result = await find_sales_leaders(
    company_size="less than 500 employees",
    location="Europe"
)

# Find marketing agencies
result = await sales_intelligence_agent(
    role_or_company="Marketing agency",
    company_size="less than 30 employees",
    location="US"
)
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

- None

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

Make sure to set your EXA_API_KEY environment variable before using this agent.

## Migration Notes

---

**Key Benefits:**

- **Sales**
- **Prospecting**
- **Leads**
- **B2B**
- **Exa**

**Related Components:**

- `exa_websets`

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add sales_intelligence_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

### Custom Configuration

```python
# Custom configuration example
from sales_intelligence_agent import sales_intelligence_agent_custom

result = await sales_intelligence_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await sales_intelligence_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await sales_intelligence_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```
