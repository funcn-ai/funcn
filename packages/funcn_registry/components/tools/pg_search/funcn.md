# pg_search_tool
> PostgreSQL database search and query tool with full-text search, connection pooling, and schema introspection

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

PostgreSQL database search and query tool with full-text search, connection pooling, and schema introspection

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add pg_search_tool
```

### Dependencies

**Python Dependencies:**

- `mirascope[openai]` >=1.24.0
- `pydantic` >=2.0.0
- `asyncpg` >=0.29.0

**Environment Variables:**

- `DATABASE_URL`: PostgreSQL connection string (Optional)

### Basic Usage

```python
from ai_tools.pg_search import PGSearchTool, query_postgres, search_table
import os

async def main():
    conn_string = os.getenv("DATABASE_URL")
    
    # Execute a custom query
    result = await query_postgres(
        connection_string=conn_string,
        query="SELECT * FROM users WHERE created_at > '2024-01-01'",
        limit=10
    )
    
    # Search in table columns
    search_result = await search_table(
        connection_string=conn_string,
        table_name="products",
        search_text="laptop",
        search_columns=["name", "description"]
    )
    
    # Full-text search
    fts_result = await full_text_search(
        connection_string=conn_string,
        table_name="articles",
        search_text="machine learning",
        search_columns=["title", "content"]
    )
```

## Tool Configuration

- `default_limit`: `100`
- `default_pool_size`: `10`
- `default_query_timeout`: `30`
- `default_use_full_text_search`: `False`

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from pg_search_tool import ToolArgs, ToolResult

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

You can now import the PostgreSQL search tool with `from ai_tools.pg_search import PGSearchTool`. The tool provides safe query execution, full-text search, and connection pooling. Make sure to set your DATABASE_URL or provide the connection string directly.

## Migration Notes

---

**Key Benefits:**

- **Postgresql**
- **Database**
- **Sql**
- **Search**
- **Full-Text-Search**

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
from pg_search_tool import tool_function, ToolError

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
from pg_search_tool import tool_function

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
from pg_search_tool import tool_function

@llm.call(provider="openai", model="gpt-4o-mini", tools=[tool_function])
@prompt_template("Use the tool to help answer: {query}")
def agent_with_tool(query: str): ...

response = agent_with_tool("your question")
if response.tool:
    result = response.tool.call()
    print(result)
```
