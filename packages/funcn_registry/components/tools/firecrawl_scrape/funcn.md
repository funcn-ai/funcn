# firecrawl_scrape_tool

> Firecrawl-powered web scraping tool that extracts clean, structured content from websites. Handles JavaScript-rendered pages and provides multiple output formats including Markdown, HTML, and screenshots.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Firecrawl-powered web scraping tool that extracts clean, structured content from websites. Handles JavaScript-rendered pages and provides multiple output formats including Markdown, HTML, and screenshots.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add firecrawl_scrape
```

### Dependencies

**Python Dependencies:**
- `firecrawl-py` >=0.0.16
- `pydantic` >=2.0.0

**Environment Variables:**
- `FIRECRAWL_API_KEY`: API key for Firecrawl services (**Required**)

### Basic Usage

```python
import asyncio
from firecrawl_scrape import scrape_website, FirecrawlScrapeArgs

async def main():
    # Basic scrape for main content
    scrape_args = FirecrawlScrapeArgs(
        url="https://example.com/article",
        formats=["markdown", "links"],
        only_main_content=True
    )
    
    response = await scrape_website(scrape_args)
    
    if response.success:
        print(f"Title: {response.metadata.title if response.metadata else 'N/A'}")
        print(f"\nContent (Markdown):\n{response.markdown[:500]}...")
        print(f"\nFound {len(response.links)} links")
    else:
        print(f"Error: {response.error}")
    
    # Advanced scrape with specific selectors
    advanced_args = FirecrawlScrapeArgs(
        url="https://news.ycombinator.com",
        formats=["html", "content", "screenshot"],
        include_tags=[".athing", ".title"],
        exclude_tags=[".spacer", ".morelink"],
        wait_for=2000,  # Wait 2 seconds for dynamic content
        screenshot=True
    )
    
    advanced_response = await scrape_website(advanced_args)
    
    if advanced_response.success:
        print(f"\nExtracted {len(advanced_response.content.split())} words")
        if advanced_response.screenshot:
            print("Screenshot captured successfully")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from firecrawl_scrape import ToolArgs, ToolResult

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
from firecrawl_scrape import tool_function

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
from firecrawl_scrape import tool_function, ToolError

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
from firecrawl_scrape import tool_function

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

The Firecrawl scraping tool is now available for extracting structured content from websites. Make sure to set your FIRECRAWL_API_KEY environment variable.

Key features:
1. **Multiple output formats**: Markdown, HTML, plain text, links, and screenshots
2. **JavaScript support**: Handles dynamic content with configurable wait times
3. **Content filtering**: Include/exclude specific elements using CSS selectors
4. **Main content extraction**: Automatically removes navigation, ads, and other non-content elements
5. **Rich metadata**: Extracts Open Graph, Twitter Card, and standard meta tags

This tool is ideal for:
- Content extraction for analysis
- Building datasets from web content
- Monitoring website changes
- Creating readable versions of web pages
- Extracting structured data from JavaScript-heavy sites

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes



---

**Key Benefits:**
- **Web-Scraping**
- **Firecrawl**
- **Content-Extraction**
- **Javascript**
- **Markdown**

**Related Components:**
- None

**References:**
- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
