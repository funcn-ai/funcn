# qwant_search_tool

> Privacy-focused web search tools using Qwant search engine. Provides structured search results with no user tracking, using unified models compatible with other search providers.

**Version**: 0.2.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Privacy-focused web search tools using Qwant search engine. Provides structured search results with no user tracking, using unified models compatible with other search providers.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add qwant_search_tool
```

### Dependencies

**Python Dependencies:**
- `httpx` >=0.24.0
- `pydantic` >=2.0.0

**Environment Variables:**
- None required

### Basic Usage

```python
import asyncio
from qwant_search_tools import qwant_search, SearchArgs

async def main():
    # Privacy-focused search
    search_args = SearchArgs(
        query="Python Mirascope library", 
        max_results=5,
        locale="en_US"
    )
    results = await qwant_search(search_args)
    
    print(f"Search provider: {results.provider}")
    print(f"Query: {results.query}")
    for result in results.results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from qwant_search_tools import ToolArgs, ToolResult

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
from qwant_search_tools import tool_function

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
from qwant_search_tools import tool_function, ToolError

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
from qwant_search_tools import tool_function

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

You can now use Qwant search tools in your agents for privacy-focused web searches. No API keys required! The tool uses unified models that work seamlessly with other search providers. Qwant doesn't track users or store search history.

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes



---

**Key Benefits:**
- **Qwant**
- **Web Search**
- **Privacy**
- **Tools**
- **Search Engine**

**Related Components:**
- None

**References:**
- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
