# git_repo_search

> Git repository search tool for searching code, files, and commits in both local Git repositories and GitHub. Supports pattern matching, file filtering, and commit history search.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Git repository search tool for searching code, files, and commits in both local Git repositories and GitHub. Supports pattern matching, file filtering, and commit history search.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add git_repo_search
```

### Dependencies

**Python Dependencies:**

- `GitPython` >=3.1.0
- `PyGithub` >=2.1.0
- `pydantic` >=2.0.0

**Environment Variables:**

- `GITHUB_TOKEN`: GitHub personal access token for searching GitHub repositories (Optional)

### Basic Usage

```python
import asyncio
from git_repo_search import search_git_repo, GitRepoSearchArgs

async def main():
    # Search local repository for code
    local_search = GitRepoSearchArgs(
        repo_path="/path/to/repo",
        query="async def",
        search_type="code",
        file_pattern="*.py",
        max_results=20
    )
    
    response = await search_git_repo(local_search)
    
    if response.success:
        print(f"Found {response.total_matches} code matches")
        for match in response.code_matches:
            print(f"\n{match.file_path}:{match.line_number}")
            print(f"  {match.line_content}")
    
    # Search GitHub repository for files
    github_file_search = GitRepoSearchArgs(
        github_repo="openai/gpt-3",
        query="model",
        search_type="file",
        file_pattern="*.json"
    )
    
    github_response = await search_git_repo(github_file_search)
    
    if github_response.success:
        print(f"\nFound {len(github_response.file_matches)} matching files:")
        for file in github_response.file_matches:
            print(f"  {file.file_path} ({file.file_size} bytes)")
    
    # Search commit history
    commit_search = GitRepoSearchArgs(
        repo_path=".",
        query="fix.*bug",
        search_type="commit",
        regex=True,
        max_results=10
    )
    
    commit_response = await search_git_repo(commit_search)
    
    if commit_response.success:
        print(f"\nFound {len(commit_response.commit_matches)} commits:")
        for commit in commit_response.commit_matches:
            print(f"\n{commit.commit_hash[:8]} by {commit.author}")
            print(f"  {commit.message.split('\\n')[0]}")
            print(f"  Files: {', '.join(commit.files_changed[:3])}...")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from git_repo_search import ToolArgs, ToolResult

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
from git_repo_search import tool_function

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
from git_repo_search import tool_function, ToolError

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
from git_repo_search import tool_function

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

The Git repository search tool is now available for searching within Git repositories. Features:

1. **Multi-source support**: Search both local repositories and GitHub
2. **Search types**:
   - `code`: Search for code patterns within files
   - `file`: Search for files by name
   - `commit`: Search commit messages
   - `pattern`: Advanced pattern matching
3. **Advanced options**:
   - File pattern filtering (e.g., `*.py`, `*.js`)
   - Regular expression support
   - Case sensitivity control
   - Context lines for code matches
4. **GitHub integration**: Set GITHUB_TOKEN for GitHub repository searches

Use cases:

- Finding specific code patterns across a codebase
- Locating files by name patterns
- Searching commit history for specific changes
- Code review and analysis
- Documentation searches

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes

---

**Key Benefits:**

- **Git**
- **Github**
- **Code-Search**
- **Repository**
- **Version-Control**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
