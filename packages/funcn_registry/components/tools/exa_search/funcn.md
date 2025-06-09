# exa_search_tools
> AI-powered search tools using Exa. Features neural search, direct Q&A, and similarity search with advanced filtering and relevance scoring.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

AI-powered search tools using Exa. Features neural search, direct Q&A, and similarity search with advanced filtering and relevance scoring.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add exa_search_tools
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
from exa_search_tools import exa_search, exa_answer, exa_find_similar, SearchArgs, AnswerArgs, FindSimilarArgs

async def main():
    # Neural search with category filter
    search_args = SearchArgs(
        query="Latest breakthroughs in quantum computing",
        max_results=5,
        search_type="neural",
        category="research paper",
        start_published_date="2023-01-01"
    )
    search_results = await exa_search(search_args)
    
    print(f"Search provider: {search_results.provider}")
    print(f"Autoprompt suggestion: {search_results.autoprompt_string}")
    for result in search_results.results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Score: {result.score}")
        print("---")
    
    # Get direct answer to a question
    answer_args = AnswerArgs(
        query="What are the main benefits of GraphQL over REST APIs?",
        include_citations=True
    )
    answer_result = await exa_answer(answer_args)
    
    print(f"\nAnswer: {answer_result.answer}")
    print(f"\nCitations:")
    for citation in answer_result.citations:
        print(f"- {citation.title} ({citation.url})")
    
    # Find similar pages
    similar_args = FindSimilarArgs(
        url="https://openai.com/blog/gpt-4",
        max_results=5,
        exclude_source_domain=True
    )
    similar_results = await exa_find_similar(similar_args)
    
    print(f"\nPages similar to GPT-4 announcement:")
    for result in similar_results.results:
        print(f"- {result.title} ({result.url})")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from exa_search_tools import ToolArgs, ToolResult

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

You now have access to Exa's AI-powered search capabilities! Set your EXA_API_KEY environment variable before using. Exa provides:

1. **Neural Search** - Semantic search that understands context
2. **Direct Answers** - Get answers with citations, not just links
3. **Find Similar** - Discover related content based on any URL

The search function uses unified models compatible with other providers, while maintaining access to Exa's advanced features like categories, date filtering, and relevance scoring.

## Migration Notes

---

**Key Benefits:**

- **Exa**
- **Web Search**
- **Ai Search**
- **Neural Search**
- **Semantic Search**

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
from exa_search_tools import tool_function, ToolError

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
from exa_search_tools import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from exa_search_tools import tool_function

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
