# csv_search_tool
> CSV search tool for searching and filtering structured data within CSV files. Supports column-specific searches, data filtering, and both exact and fuzzy matching capabilities.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

CSV search tool for searching and filtering structured data within CSV files. Supports column-specific searches, data filtering, and both exact and fuzzy matching capabilities.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add csv_search_tool
```

### Dependencies

**Python Dependencies:**

- `pandas` >=2.0.0
- `fuzzywuzzy` >=0.18.0
- `python-Levenshtein` >=0.12.0
- `pydantic` >=2.0.0

**Environment Variables:**

- None required

### Basic Usage

```python
import asyncio
from csv_search import search_csv_content, CSVSearchArgs

async def main():
    # Basic search across all columns
    search_args = CSVSearchArgs(
        file_path="data/customers.csv",
        query="John Smith",
        max_results=10
    )
    
    response = await search_csv_content(search_args)
    
    # Search with column filters
    filtered_search = CSVSearchArgs(
        file_path="data/sales.csv",
        query="laptop",
        columns=["product_name", "description"],
        filters={
            "price": ">500",
            "status": "completed",
            "year": "2024"
        },
        exact_match=False,
        fuzzy_threshold=75
    )
    
    filtered_response = await search_csv_content(filtered_search)
    
    if filtered_response.error:
        print(f"Error: {filtered_response.error}")
    else:
        print(f"Found {len(filtered_response.results)} matches")
        print(f"Searched {filtered_response.filtered_count} rows after filtering (total: {filtered_response.total_rows})")
        
        for result in filtered_response.results:
            print(f"\nRow {result.row_index}:")
            print(f"Matched in columns: {', '.join(result.matched_columns)}")
            print(f"Match scores: {result.match_scores}")
            print(f"Data: {result.row_data}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from csv_search_tool import ToolArgs, ToolResult

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

The CSV search tool is now available for searching and filtering structured data. Key features:

1. **Column-specific searches**: Target specific columns for more precise results
2. **Advanced filtering**: Use comparison operators (>, <, >=, <=, !=) for numeric columns
3. **Fuzzy matching**: Find approximate matches with configurable threshold
4. **Exact matching**: Option for precise string matching
5. **Case sensitivity**: Configurable case-sensitive or case-insensitive search
6. **Async operation**: Non-blocking searches for better performance

Filter syntax examples:

- `{'age': '>30'}` - Age greater than 30
- `{'status': 'active'}` - Exact match for 'active'
- `{'price': '<=100'}` - Price less than or equal to 100
- `{'category': '!=deprecated'}` - Category not equal to 'deprecated'

## Migration Notes

---

**Key Benefits:**

- **Csv**
- **Search**
- **Data**
- **Structured-Data**
- **Filtering**

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
from csv_search_tool import tool_function, ToolError

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
from csv_search_tool import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from csv_search_tool import tool_function

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
