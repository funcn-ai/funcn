# xml_search_tool

> XML data processing tool with XPath queries, namespace support, validation, and advanced search capabilities

**Version**: 0.1.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

XML data processing tool with XPath queries, namespace support, validation, and advanced search capabilities

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add xml_search_tool
```

### Dependencies

**Python Dependencies:**

- `mirascope[openai]` >=1.24.0
- `pydantic` >=2.0.0
- `lxml` >=4.9.0
- `aiofiles` >=23.0.0

**Environment Variables:**

- None required

### Basic Usage

```python
from ai_tools.xml_search import XMLSearchTool, search_xml_xpath, find_xml_elements

async def main():
    # XPath search
    result = await search_xml_xpath(
        file_path="data.xml",
        xpath="//book[@category='fiction']/title"
    )
    
    # Find elements by attributes
    products = await find_xml_elements(
        file_path="catalog.xml",
        tag_names=["product"],
        attributes={"status": "active", "type": "electronics"}
    )
    
    # Validate XML against schema
    validation = await validate_xml_file(
        file_path="document.xml",
        xsd_schema_path="schema.xsd"
    )
```

## Tool Configuration

- `default_namespace_aware`: `True`
- `default_case_sensitive`: `True`
- `default_validate`: `False`
- `default_include_children`: `True`

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from xml_search_tool import ToolArgs, ToolResult

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
from xml_search_tool import tool_function

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
from xml_search_tool import tool_function, ToolError

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
from xml_search_tool import tool_function

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

You can now import the XML search tool with `from ai_tools.xml_search import XMLSearchTool`. The tool provides XPath queries, namespace handling, element search by text/attributes, and XML validation against XSD schemas.

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes

---

**Key Benefits:**

- **Xml**
- **Xpath**
- **Search**
- **Validation**
- **Xsd**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
