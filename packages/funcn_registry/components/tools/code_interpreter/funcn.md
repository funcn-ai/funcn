# code_interpreter

> Safe Python code execution tool with sandboxing, timeout controls, and variable capture

**Version**: 0.1.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Safe Python code execution tool with sandboxing, timeout controls, and variable capture

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add code_interpreter
```

### Dependencies

**Python Dependencies:**

- `mirascope[openai]` >=1.24.0
- `pydantic` >=2.0.0

**Environment Variables:**

- None required

### Basic Usage

```python
from ai_tools.code_interpreter import CodeInterpreterTool, execute_code

async def main():
    # Execute code safely
    result = await execute_code(
        code="""\nimport math\nx = math.pi * 2\nprint(f'2π = {x}')\nresult = [i**2 for i in range(5)]\n""",
        timeout_seconds=10
    )
    
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    print(f"Variables: {result.variables}")
    print(f"Execution time: {result.execution_time:.2f}s")
```

## Tool Configuration

- `default_timeout`: `30`
- `default_use_subprocess`: `True`
- `default_capture_variables`: `True`

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from code_interpreter import ToolArgs, ToolResult

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
from code_interpreter import tool_function

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
from code_interpreter import tool_function, ToolError

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
from code_interpreter import tool_function

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
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## Troubleshooting

You can now import the code interpreter with `from ai_tools.code_interpreter import CodeInterpreterTool`. The tool provides safe Python code execution with subprocess isolation, timeout controls, and restricted imports. Use `execute_code()` for simple execution or the full tool class for more control.

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes

---

**Key Benefits:**

- **Code-Execution**
- **Interpreter**
- **Sandbox**
- **Python**
- **Safety**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
