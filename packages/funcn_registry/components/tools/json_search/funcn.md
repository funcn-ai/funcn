# json_search_tool
> JSON search tool for searching and querying within JSON files and data structures. Supports JSONPath expressions, fuzzy matching, and searching in both keys and values.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

JSON search tool for searching and querying within JSON files and data structures. Supports JSONPath expressions, fuzzy matching, and searching in both keys and values.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add json_search_tool
```

### Dependencies

**Python Dependencies:**

- `jsonpath-ng` >=1.6.0
- `fuzzywuzzy` >=0.18.0
- `python-Levenshtein` >=0.12.0
- `pydantic` >=2.0.0

**Environment Variables:**

- None required

### Basic Usage

```python
import asyncio
from json_search import search_json_content, JSONSearchArgs

async def main():
    # Search in a JSON file
    file_search = JSONSearchArgs(
        file_path="config/settings.json",
        query="api_key",
        search_keys=True,  # Also search in keys
        max_results=5
    )
    
    response = await search_json_content(file_search)
    
    # Search with JSONPath filtering
    api_search = JSONSearchArgs(
        file_path="data/api_response.json",
        query="John",
        json_path="$.users[*].profile",  # Only search in user profiles
        fuzzy_threshold=90
    )
    
    api_response = await search_json_content(api_search)
    
    # Search in JSON data directly
    data = {
        "users": [
            {"name": "John Doe", "email": "john@example.com"},
            {"name": "Jane Smith", "email": "jane@example.com"}
        ],
        "settings": {
            "notifications": {"email": True, "sms": False}
        }
    }
    
    data_search = JSONSearchArgs(
        json_data=data,
        query="email",
        search_keys=True,
        exact_match=False
    )
    
    data_response = await search_json_content(data_search)
    
    if data_response.error:
        print(f"Error: {data_response.error}")
    else:
        print(f"Found {len(data_response.results)} matches in {data_response.total_elements} elements")
        print(f"Search scope: {data_response.search_scope}")
        
        for result in data_response.results:
            print(f"\nPath: {result.path}")
            print(f"Value: {result.value}")
            print(f"Score: {result.match_score}%")
            if result.context:
                print(f"Context: {result.context}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from json_search_tool import ToolArgs, ToolResult

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

The JSON search tool is now available for searching within JSON files and data structures. Key features:

1. **JSONPath expressions**: Use standard JSONPath syntax to narrow search scope
2. **Fuzzy matching**: Find approximate matches with configurable threshold
3. **Key/value searching**: Search in object keys, values, or both
4. **Direct data or file input**: Search JSON files or provide data directly
5. **Context extraction**: Get the parent object containing matches
6. **Async operation**: Non-blocking searches for better performance

JSONPath examples:

- `$.users[*].name` - All user names
- `$.data[?(@.price > 100)]` - Items with price > 100
- `$..email` - All email fields at any depth
- `$.config.database.*` - All database config values

This tool is ideal for:

- Configuration file searching
- API response analysis
- Log file investigation
- Data structure exploration

## Migration Notes

---

**Key Benefits:**

- **Json**
- **Search**
- **Jsonpath**
- **Query**
- **Fuzzy-Matching**

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
from json_search_tool import tool_function, ToolError

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
from json_search_tool import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from json_search_tool import tool_function

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
