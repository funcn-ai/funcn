# multi_agent_coordinator
> Orchestrates multiple specialized agents to solve complex tasks through intelligent task decomposition, agent selection, and result synthesis

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Orchestrates multiple specialized agents to solve complex tasks through intelligent task decomposition, agent selection, and result synthesis

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
sygaldry add multi_agent_coordinator
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- `agents.web_search`
- `agents.text_summarization`
- `agents.research_assistant`
- `agents.hallucination_detector`
- `agents.knowledge_graph`
- `agents.code_generation_execution`

**Python Dependencies:**

- `mirascope>=1.24.0`
- `pydantic>=2.0.0`
- `asyncio`

**Environment Variables:**

- `OPENAI_API_KEY`: OpenAI API key for LLM calls (**Required**)

### Basic Usage

```python
from multi_agent_coordinator import multi_agent_coordinator, multi_agent_coordinator_stream

# Example 1: Coordinate agents for complex research task
result = await multi_agent_coordinator(
    task="Research the impact of AI on healthcare and create a comprehensive report",
    context="Focus on diagnostic accuracy, patient outcomes, and ethical considerations",
    requirements="Include recent studies, real-world implementations, and future predictions",
    max_parallel_tasks=3
)

print(f"Final Answer: {result.final_answer}")
print(f"Quality Score: {result.quality_score}")
print(f"Agents Used: {', '.join(result.agents_used)}")

# Example 2: Stream the coordination process
async for update in multi_agent_coordinator_stream(
    task="Analyze market trends for renewable energy investments",
    context="Focus on solar, wind, and battery storage sectors"
):
    print(update, end='')
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

The Multi-Agent Coordinator requires access to other specialized agents. Ensure you have installed the required agent dependencies listed above. Configure your OpenAI API key for optimal performance.

## Migration Notes

---

**Key Benefits:**

- **Orchestration**
- **Multi-Agent**
- **Task-Decomposition**
- **Coordination**
- **Complex-Tasks**

**Related Components:**

- `agents.web_search`
- `agents.text_summarization`
- `agents.research_assistant`
- `agents.hallucination_detector`
- `agents.knowledge_graph`
- `agents.code_generation_execution`

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await multi_agent_coordinator(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await multi_agent_coordinator(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from multi_agent_coordinator import multi_agent_coordinator_custom

result = await multi_agent_coordinator_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `sygaldry add multi_agent_coordinator` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries
