# research_assistant_agent
> AI-powered research agent that conducts comprehensive research using Exa search

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

AI-powered research agent that conducts comprehensive research using Exa search

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add research_assistant_agent
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
from ai_agents.research_assistant import research_topic, research_company

async def main():
    # General topic research
    report = await research_topic('artificial intelligence in healthcare')
    print(f"Title: {report.title}")
    print(f"Summary: {report.executive_summary}")
    
    # Company research
    company_report = await research_company('OpenAI')
    
    # Quick summary
    summary = await quick_research_summary('latest AI regulations')
    print(f"Summary: {summary['summary']}")
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
- `depth`: `comprehensive`
- `style`: `professional`
- `audience`: `general business`
- `num_queries`: `5`
- `target_words`: `1000`

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

You can now import the research assistant with `from ai_agents.research_assistant import research_topic`. Make sure to set your EXA_API_KEY and OPENAI_API_KEY environment variables. The agent provides:

1. `research_topic()` - General research on any topic
2. `research_company()` - Specialized company analysis
3. `research_technology()` - Technology deep dives
4. `research_market()` - Market/industry analysis
5. `quick_research_summary()` - Fast summaries

For optional tracing, install lilypad: `pip install lilypad`.

## Migration Notes

---

**Key Benefits:**

- **Research**
- **Exa**
- **Report-Generation**
- **Analysis**
- **Market-Research**

**Related Components:**

- `exa_search`

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await research_assistant_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await research_assistant_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from research_assistant_agent import research_assistant_agent_custom

result = await research_assistant_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add research_assistant_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries
