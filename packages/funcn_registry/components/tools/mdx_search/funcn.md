# mdx_search

> MDX documentation search tool with JSX component parsing, frontmatter support, and section extraction

**Version**: 0.1.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

MDX documentation search tool with JSX component parsing, frontmatter support, and section extraction

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add mdx_search
```

### Dependencies

**Python Dependencies:**

- `mirascope[openai]` >=1.24.0
- `pydantic` >=2.0.0
- `aiofiles` >=23.0.0
- `python-frontmatter` >=1.0.0
- `markdown` >=3.4.0

**Environment Variables:**

- None required

### Basic Usage

```python
from ai_tools.mdx_search import search_mdx_files, extract_mdx_components, find_documentation_sections

async def main():
    # Search MDX files
    results = await search_mdx_files(
        query="React hooks",
        search_path="./docs",
        search_in=["content", "components", "headings"]
    )
    
    # Extract JSX components
    components = await extract_mdx_components(
        file_path="./docs/components.mdx",
        component_names=["CodeBlock", "Alert"]
    )
    
    # Find documentation sections
    sections = await find_documentation_sections(
        search_path="./docs",
        heading_pattern="API.*Reference",
        min_level=2
    )
    
    # Search with metadata filters
    filtered = await search_mdx_with_metadata(
        query="authentication",
        metadata_filters={"category": "security"},
        tags_filter=["auth", "oauth"]
    )
```

## Tool Configuration

- `default_max_results`: `50`
- `default_case_sensitive`: `False`
- `default_search_in`: `['content']`
- `default_file_pattern`: `**/*.mdx`

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from mdx_search import ToolArgs, ToolResult

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
from mdx_search import tool_function

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
from mdx_search import tool_function, ToolError

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
from mdx_search import tool_function

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

You can now import MDX search functions with `from ai_tools.mdx_search import search_mdx_files`. The tool searches MDX documentation files (Markdown with JSX), extracts components, parses frontmatter, and provides section-based navigation for documentation sites.

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes

---

**Key Benefits:**

- **Mdx**
- **Documentation**
- **Jsx**
- **Markdown**
- **Frontmatter**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
