# dynamic_learning_path
> Generates personalized, adaptive learning paths based on individual skills, goals, and learning preferences with comprehensive resource curation

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Generates personalized, adaptive learning paths based on individual skills, goals, and learning preferences with comprehensive resource curation

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add dynamic_learning_path
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- None

**Python Dependencies:**

- `mirascope>=1.24.0`
- `pydantic>=2.0.0`
- `asyncio`

**Environment Variables:**

- `OPENAI_API_KEY`: OpenAI API key for LLM calls (**Required**)

### Basic Usage

```python
from dynamic_learning_path import (
    dynamic_learning_path_generator,
    dynamic_learning_path_stream,
    LearningStyle
)

# Example 1: Generate a learning path for Python development
learning_path = await dynamic_learning_path_generator(
    background="Computer Science degree, 2 years of Java experience",
    experience="Built several web applications, familiar with databases",
    learning_goals="Master Python for data science and machine learning",
    available_time="10 hours per week",
    learning_style=LearningStyle.VISUAL,
    budget="Mixed (prefer free resources)",
    career_goals="Transition to ML Engineer role within 6 months"
)

print(f"Learning Path: {learning_path.path_name}")
print(f"Total Duration: {learning_path.total_duration}")
for i, module in enumerate(learning_path.modules, 1):
    print(f"\nModule {i}: {module.module_name}")
    print(f"Duration: {module.estimated_duration}")
    print(f"Resources: {len(module.resources)} curated resources")

# Example 2: Stream the learning path generation
async for update in dynamic_learning_path_stream(
    background="Marketing professional with basic Excel skills",
    experience="5 years in digital marketing, some SQL knowledge",
    learning_goals="Learn data analytics for marketing insights",
    available_time="5 hours per week"
):
    print(update, end='')
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

The Dynamic Learning Path Generator creates personalized learning journeys. Configure your OpenAI API key and consider your learners' backgrounds, goals, and constraints for optimal path generation.

## Migration Notes

---

**Key Benefits:**

- **Education**
- **Learning-Path**
- **Personalization**
- **Skill-Assessment**
- **Adaptive-Learning**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add dynamic_learning_path` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

### Custom Configuration

```python
# Custom configuration example
from dynamic_learning_path import dynamic_learning_path_custom

result = await dynamic_learning_path_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await dynamic_learning_path(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await dynamic_learning_path(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```
