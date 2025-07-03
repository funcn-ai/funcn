# youtube_video_search_tool
> YouTube video search and transcript extraction tool for content analysis and research

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

YouTube video search and transcript extraction tool for content analysis and research

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
sygaldry add youtube_video_search_tool
```

### Dependencies

**Python Dependencies:**

- `mirascope[openai]` >=1.24.0
- `pydantic` >=2.0.0
- `httpx` >=0.25.0
- `youtube-transcript-api` >=0.6.0

**Environment Variables:**

- `YOUTUBE_API_KEY`: YouTube Data API v3 key (**Required**)

### Basic Usage

```python
from ai_tools.youtube_video_search import search_youtube_videos, get_video_transcript, analyze_video_content
import os

async def main():
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    # Search for videos
    results = await search_youtube_videos(
        query="machine learning tutorial",
        api_key=api_key,
        max_results=5
    )
    
    # Get transcript for a video
    if results.videos:
        video_id = results.videos[0].video_id
        success, segments, error = await get_video_transcript(
            video_id=video_id,
            languages=["en"]
        )
        
        if success:
            print(f"Transcript has {len(segments)} segments")
    
    # Analyze video content
    analysis = await analyze_video_content(
        video_id="dQw4w9WgXcQ",
        api_key=api_key,
        include_stats=True
    )
```

## Tool Configuration

- `default_max_results`: `10`
- `default_order`: `relevance`
- `default_region_code`: `US`
- `default_language`: `en`

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from youtube_video_search_tool import ToolArgs, ToolResult

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

You can now import YouTube search functions with `from ai_tools.youtube_video_search import search_youtube_videos`. Make sure to set your YOUTUBE_API_KEY environment variable. The tool provides video search, transcript extraction, and content analysis capabilities.

## Migration Notes

---

**Key Benefits:**

- **Youtube**
- **Video**
- **Search**
- **Transcript**
- **Captions**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)

### Tool Chaining

```python
# Chain multiple tools together
from sygaldry_registry.tools import tool1, tool2

async def chained_workflow(input_data):
    result1 = await tool1(input_data)
    result2 = await tool2(result1.output)
    return result2
```

### Error Handling

```python
from youtube_video_search_tool import tool_function, ToolError

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
from youtube_video_search_tool import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from youtube_video_search_tool import tool_function

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
