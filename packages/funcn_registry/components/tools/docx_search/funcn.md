# docx_search_tool
> Microsoft Word document search and content extraction tool with advanced text search, regex support, and metadata extraction

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

Microsoft Word document search and content extraction tool with advanced text search, regex support, and metadata extraction

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add docx_search_tool
```

### Dependencies

**Python Dependencies:**

- `mirascope[openai]` >=1.24.0
- `pydantic` >=2.0.0
- `python-docx` >=0.8.11
- `aiofiles` >=23.0.0

**Environment Variables:**

- None required

### Basic Usage

```python
from ai_tools.docx_search import DOCXSearchTool, search_docx, extract_docx_headings

async def main():
    # Search for text in a document
    result = await search_docx(
        file_path="report.docx",
        search_text="quarterly revenue",
        include_tables=True
    )
    print(f"Found {result.total_matches} matches")
    
    # Extract all headings
    headings = await extract_docx_headings(
        file_path="report.docx",
        heading_level=2  # Only level 2 headings
    )
    
    # Search with regex
    dates = await search_docx_with_regex(
        file_path="report.docx",
        pattern=r"\d{4}-\d{2}-\d{2}"
    )
```

## Tool Configuration

- `default_case_sensitive`: `False`
- `default_include_tables`: `True`
- `default_extract_metadata`: `True`
- `default_max_context_chars`: `200`

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from docx_search_tool import ToolArgs, ToolResult

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

You can now import the DOCX search tool with `from ai_tools.docx_search import DOCXSearchTool`. The tool provides powerful Word document search capabilities including text search, regex patterns, heading extraction, table search, and metadata extraction. Use the convenience functions for common operations.

## Migration Notes

---

**Key Benefits:**

- **Docx**
- **Word**
- **Document**
- **Search**
- **Text-Extraction**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

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

### Error Handling

```python
from docx_search_tool import tool_function, ToolError

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
from docx_search_tool import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
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

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from docx_search_tool import tool_function

@llm.call(provider="openai", model="gpt-4o-mini", tools=[tool_function])
@prompt_template("Use the tool to help answer: {query}")
def agent_with_tool(query: str): ...

response = agent_with_tool("your question")
if response.tool:
    result = response.tool.call()
    print(result)
```
