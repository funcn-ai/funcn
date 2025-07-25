# code_generation_execution_agent
> Agent for generating and safely executing Python code. Analyzes code for safety, supports multiple safety levels, and provides recommendations for improvement. Features sandboxed execution environment and comprehensive code analysis.

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Agent for generating and safely executing Python code. Analyzes code for safety, supports multiple safety levels, and provides recommendations for improvement. Features sandboxed execution environment and comprehensive code analysis.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
sygaldry add code_generation_execution_agent
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
from code_generation_execution import (
    generate_and_execute_code,
    generate_code_snippet,
    safe_execute_task
)

async def main():
    # Generate and execute code with moderate safety level
    result = await generate_and_execute_code(
        task="Create a function to calculate fibonacci numbers",
        requirements="Must be efficient for large numbers",
        constraints="Use memoization",
        auto_execute=True,
        safety_level="moderate"
    )
    
    print(f"Generated code:\n{result.generated_code.code}")
    print(f"\nSafety analysis: {result.code_analysis}")
    if result.execution_result:
        print(f"\nExecution output: {result.execution_result.output}")
    print(f"\nRecommendations: {result.recommendations}")
    
    # Generate code snippet without execution
    snippet = await generate_code_snippet(
        "Sort a list of dictionaries by multiple keys"
    )
    print(f"\nCode snippet:\n{snippet}")
    
    # Safe execution with strict safety level
    safe_result = await safe_execute_task(
        task="Generate prime numbers up to 100",
        safety_level="strict"
    )
    print(f"\nSafe execution result: {safe_result}")

if __name__ == "__main__":
    asyncio.run(main())
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
- `safety_level`: `moderate`

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

This agent generates and optionally executes Python code in a sandboxed environment. Configure safety levels: 'strict' (limited imports, no file/network/system operations), 'moderate' (no system calls), or 'permissive' (fewer restrictions). The agent analyzes code for safety concerns before execution. Set your preferred LLM provider's API key.

## Migration Notes

---

**Key Benefits:**

- **Code Generation**
- **Code Execution**
- **Agent**
- **Mirascope**
- **Python**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await code_generation_execution_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await code_generation_execution_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from code_generation_execution_agent import code_generation_execution_agent_custom

result = await code_generation_execution_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `sygaldry add code_generation_execution_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries
