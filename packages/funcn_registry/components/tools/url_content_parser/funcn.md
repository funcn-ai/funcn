# url_content_parser_tool
> URL content parsing tool that extracts clean text content from web pages. Removes scripts, styles, and other noise to provide readable text content.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

URL content parsing tool that extracts clean text content from web pages. Removes scripts, styles, and other noise to provide readable text content.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add url_content_parser_tool
```

### Dependencies

**Python Dependencies:**

- `httpx` >=0.24.0
- `beautifulsoup4` >=4.0.0
- `pydantic` >=2.0.0

**Environment Variables:**

- None required

### Basic Usage

```python
import asyncio
from url_content_parser import parse_url_content, URLParseArgs

async def main():
    # Parse content from a webpage
    parse_args = URLParseArgs(
        url="https://example.com/article",
        max_chars=5000
    )
    content = await parse_url_content(parse_args)
    print(content)

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from url_content_parser_tool import ToolArgs, ToolResult

# Input model defines the expected parameters
args = ToolArgs(
    param1="value1",
    param2="value2"
)

# Output model provides structured results
result: ToolResult = await tool_function(args)
```

## Integration with Agents

## Integration with Mirascope

This tool follows Mirascope best practices:

- Uses Pydantic models for structured inputs and outputs
- Supports async/await patterns for optimal performance
- Compatible with all Mirascope LLM providers
- Includes comprehensive error handling
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## API Reference

See component source code for detailed API documentation.

## Advanced Examples

Check the examples directory for advanced usage patterns.

## Troubleshooting

You can now use the URL content parser tool in your agents to extract clean text content from web pages. This tool is commonly used alongside search tools to analyze specific web pages found in search results.

## Migration Notes

---

**Key Benefits:**

- **Url**
- **Content**
- **Parsing**
- **Web Scraping**
- **Text Extraction**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

### Tool Chaining

```python
# Chain multiple tools together
from funcn_registry.tools import tool1, tool2

async def chained_workflow(input_data):
    result1 = await tool1(input_data)
    result2 = await tool2(result1.output)
    return result2
```

### Error Handling

```python
from url_content_parser_tool import tool_function, ToolError

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
from url_content_parser_tool import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from url_content_parser_tool import tool_function

@llm.call(provider="openai", model="gpt-4o-mini", tools=[tool_function])
@prompt_template("Use the tool to help answer: {query}")
def agent_with_tool(query: str): ...

response = agent_with_tool("your question")
if response.tool:
    result = response.tool.call()
    print(result)
```

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

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations
