# nimble_search_tool

> Multi-API search tool using Nimble's Web, SERP, and Maps APIs for comprehensive search capabilities

**Version**: 1.0.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: 

## Overview

Multi-API search tool using Nimble's Web, SERP, and Maps APIs for comprehensive search capabilities

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add nimble_search_tool
```

### Dependencies

**Python Dependencies:**
- Standard library only

**Environment Variables:**
- `NIMBLE_API_KEY`: API key for Nimble services (**Required**)

### Basic Usage

```python
import asyncio
from nimble_search import tool_function, ToolArgs

async def main():
    # Basic tool usage
    args = ToolArgs(
        param1="value1",
        param2="value2"
    )
    result = await tool_function(args)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from nimble_search import ToolArgs, ToolResult

# Input model defines the expected parameters
args = ToolArgs(
    param1="value1",
    param2="value2"
)

# Output model provides structured results
result: ToolResult = await tool_function(args)
```

## Integration with Agents

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from nimble_search import tool_function

@llm.call(provider="openai", model="gpt-4o-mini", tools=[tool_function])
@prompt_template("Use the tool to help answer: {query}")
def agent_with_tool(query: str): ...

response = agent_with_tool("your question")
if response.tool:
    result = response.tool.call()
    print(result)
```

### Tool Chaining

```python
# Chain multiple tools together
from funcn_registry.tools import tool1, tool2

async def chained_workflow(input_data):
    result1 = await tool1(input_data)
    result2 = await tool2(result1.output)
    return result2
```

## API Reference

See component source code for detailed API documentation.

### Function Signature

The main tool function follows this pattern:

```python
async def tool_function(args: ToolArgs) -> ToolResult:
    """
    Tool description and usage.

    Args:
        args: Structured input parameters

    Returns:
        Structured result with typed fields

    Raises:
        ToolError: When operation fails
    """
```

## Advanced Examples

Check the examples directory for advanced usage patterns.

### Error Handling

```python
from nimble_search import tool_function, ToolError

try:
    result = await tool_function(args)
    print(f"Success: {result}")
except ToolError as e:
    print(f"Tool error: {e}")
    # Handle gracefully
```

### Batch Processing

```python
import asyncio
from nimble_search import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## Integration with Mirascope

This tool follows Mirascope best practices:

- Uses Pydantic models for structured inputs and outputs
- Supports async/await patterns for optimal performance
- Compatible with all Mirascope LLM providers
- Includes comprehensive error handling

## Troubleshooting

No known issues.

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes



---

**Key Benefits:**
- **Search**
- **Web**
- **Serp**
- **Maps**
- **Nimble**

**Related Components:**
- None

**References:**
- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry]()
