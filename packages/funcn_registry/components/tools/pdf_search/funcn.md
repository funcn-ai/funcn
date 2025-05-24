# pdf_search_tool

> PDF search tool that enables searching for text within PDF documents using fuzzy matching. Extracts text from PDFs and provides context-aware search results with page numbers and match scores.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

PDF search tool that enables searching for text within PDF documents using fuzzy matching. Extracts text from PDFs and provides context-aware search results with page numbers and match scores.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add pdf_search_tool
```

### Dependencies

**Python Dependencies:**
- `PyPDF2` >=3.0.0
- `fuzzywuzzy` >=0.18.0
- `python-Levenshtein` >=0.12.0
- `pydantic` >=2.0.0

**Environment Variables:**
- None required

### Basic Usage

```python
import asyncio
from pdf_search import search_pdf_content, PDFSearchArgs

async def main():
    # Search for text in a PDF file
    search_args = PDFSearchArgs(
        file_path="documents/research_paper.pdf",
        query="machine learning algorithms",
        max_results=5,
        context_chars=300,
        fuzzy_threshold=75
    )
    
    response = await search_pdf_content(search_args)
    
    if response.error:
        print(f"Error: {response.error}")
    else:
        print(f"Found {len(response.results)} matches in {response.total_pages} pages")
        for result in response.results:
            print(f"\nPage {result.page_number} (Score: {result.match_score}%)")
            print(f"Match: '{result.excerpt}'")
            print(f"Context: {result.text}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from pdf_search import ToolArgs, ToolResult

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
from pdf_search import tool_function

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
from pdf_search import tool_function, ToolError

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
from pdf_search import tool_function

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

The PDF search tool is now available for searching text within PDF documents. It uses fuzzy matching to find relevant content even with slight variations. Key features:

1. Fuzzy text matching with configurable threshold
2. Context extraction around matches
3. Page number tracking
4. Async operation for non-blocking searches
5. Structured response with match scores

Note: python-Levenshtein is optional but recommended for better performance with fuzzy matching.

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes



---

**Key Benefits:**
- **Pdf**
- **Search**
- **Document**
- **Text-Extraction**
- **Fuzzy-Matching**

**Related Components:**
- None

**References:**
- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
