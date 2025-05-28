# prompt_engineering_optimizer

> Advanced prompt optimization agent that analyzes, generates variants, performs A/B testing, and delivers production-ready optimized prompts with comprehensive documentation

**Version**: 0.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Advanced prompt optimization agent that analyzes, generates variants, performs A/B testing, and delivers production-ready optimized prompts with comprehensive documentation

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add prompt_engineering_optimizer
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
from prompt_engineering_optimizer import prompt_engineering_optimizer, prompt_engineering_optimizer_stream

# Example 1: Optimize a simple prompt
original_prompt = "Write a summary of the text"

result = await prompt_engineering_optimizer(
    prompt=original_prompt,
    task_context="Summarizing technical documentation for developers",
    target_audience="Software engineers",
    success_criteria="Clear, concise summaries that highlight key technical points",
    test_inputs=[
        "Long technical document about microservices architecture...",
        "API documentation for a REST service..."
    ],
    optimization_goals="Improve clarity and ensure technical accuracy"
)

print(f"Original Score: {result.optimization.analysis.overall_score:.2f}")
print(f"Performance Improvement: +{result.performance_improvement:.1f}%")
print(f"\nOptimized Prompt:\n{result.final_prompt}")

# Example 2: Stream the optimization process
async for update in prompt_engineering_optimizer_stream(
    prompt="Generate code based on requirements",
    task_context="Code generation for Python applications",
    enable_ab_testing=True
):
    print(update, end='')

# Example 3: Advanced optimization with multiple test cases
complex_prompt = """
You are an AI assistant. Help the user with their request.
Be helpful and provide good answers.
"""

result = await prompt_engineering_optimizer(
    prompt=complex_prompt,
    task_context="General-purpose AI assistant for customer support",
    target_audience="Non-technical users",
    success_criteria="Accurate, helpful, and empathetic responses",
    test_inputs=[
        "How do I reset my password?",
        "I'm having trouble with my order",
        "Can you explain how this works?"
    ],
    optimization_goals="Improve specificity, add structure, enhance clarity",
    max_variants=6,
    enable_ab_testing=True
)

# Access detailed results
for variant in result.optimization.variants:
    print(f"\nVariant: {variant.variant_name}")
    print(f"Techniques: {', '.join([t.value for t in variant.techniques_applied])}")
    print(f"Performance: {variant.estimated_performance:.2f}")
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
result_openai = await prompt_engineering_optimizer(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await prompt_engineering_optimizer(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from prompt_engineering_optimizer import prompt_engineering_optimizer_custom

result = await prompt_engineering_optimizer_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

The Prompt Engineering Optimizer helps you create high-performance prompts through systematic analysis and testing. Configure your OpenAI API key and provide sample test inputs for best results. The agent will generate multiple optimized variants and help you choose the best one based on empirical testing.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add prompt_engineering_optimizer` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes



---

**Key Benefits:**

- **Prompt-Engineering**
- **Optimization**
- **A-B-Testing**
- **Performance**
- **Analysis**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
