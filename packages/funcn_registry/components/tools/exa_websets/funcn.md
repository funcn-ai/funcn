# exa_websets_tool
> Advanced web data collection tools using Exa Websets. Create curated collections of web data with search criteria and structured enrichments for building datasets.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

Advanced web data collection tools using Exa Websets. Create curated collections of web data with search criteria and structured enrichments for building datasets.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add exa_websets_tool
```

### Dependencies

**Python Dependencies:**

- `exa-py` >=1.0.0
- `pydantic` >=2.0.0

**Environment Variables:**

- `EXA_API_KEY`: API key for Exa services. Get it from https://exa.ai (**Required**)

### Basic Usage

```python
import asyncio
from exa_websets_tools import (
    exa_create_webset, 
    exa_get_webset, 
    exa_list_webset_items,
    exa_wait_until_idle,
    CreateWebsetArgs,
    WebsetSearchConfig,
    WebsetEnrichmentConfig
)

async def main():
    # Create a webset to find and analyze AI companies
    search_config = WebsetSearchConfig(
        query="AI startup companies founded after 2020",
        count=50  # Target 50 companies
    )
    
    # Define enrichments to extract structured data
    enrichments = [
        WebsetEnrichmentConfig(
            description="Extract company information",
            format="json",
            instructions="Extract: company name, founding year, main product, funding raised, headquarters location"
        ),
        WebsetEnrichmentConfig(
            description="Analyze AI technology focus",
            format="categories",
            options=[{"label": "NLP"}, {"label": "Computer Vision"}, {"label": "Robotics"}, {"label": "MLOps"}]
        )
    ]
    
    # Create the webset
    create_args = CreateWebsetArgs(
        search=search_config,
        enrichments=enrichments,
        metadata={"project": "ai_landscape_analysis"}
    )
    
    webset = await exa_create_webset(create_args)
    print(f"Created webset: {webset.id} (status: {webset.status})")
    
    # Wait for processing to complete
    print("Waiting for webset to process...")
    webset = await exa_wait_until_idle(webset.id)
    print(f"Webset complete! Found {webset.items_count} items")
    
    # List the collected items
    items_response = await exa_list_webset_items(webset.id, limit=10)
    
    print(f"\nFirst 10 companies found:")
    for item in items_response.items:
        print(f"- {item.url}")
        if item.enrichments:
            print(f"  Enrichment data: {item.enrichments[0]}")
    
    # Get full webset details
    full_webset = await exa_get_webset(webset.id)
    print(f"\nWebset searches: {len(full_webset.searches or [])}")
    print(f"Webset enrichments: {len(full_webset.enrichments or [])}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from exa_websets_tool import ToolArgs, ToolResult

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

You now have access to Exa's advanced Websets functionality! Set your EXA_API_KEY environment variable before using.

Websets allow you to:
1. **Define Search Criteria** - Specify what web content to collect
2. **Apply Enrichments** - Extract structured data from collected pages
3. **Build Datasets** - Create curated collections for analysis

Websets are ideal for:

- Market research and competitive analysis
- Building training datasets
- Monitoring industry trends
- Creating knowledge bases

Note: Websets processing can take time depending on the search complexity and enrichments. Use `exa_wait_until_idle()` to wait for completion.

## Migration Notes

---

**Key Benefits:**

- **Exa**
- **Websets**
- **Data Collection**
- **Web Scraping**
- **Enrichment**

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
from exa_websets_tool import tool_function, ToolError

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
from exa_websets_tool import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from exa_websets_tool import tool_function

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
