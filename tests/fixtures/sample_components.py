"""Sample component fixtures for testing the component system."""

import json
from funcn_cli.core.models import ComponentManifest, RegistryComponentEntry
from pathlib import Path


def create_sample_agent_files(component_dir: Path) -> None:
    """Create sample agent component files in the given directory."""
    # Create component.json
    component_json = {
        "name": "sample_agent",
        "type": "agent",
        "version": "0.1.0",
        "description": "A sample agent for testing",
        "author": "Test Author",
        "tags": ["test", "sample"],
        "dependencies": ["mirascope>=1.0.0", "pydantic>=2.0.0"],
        "mirascope_providers": ["openai", "anthropic", "google"],
        "config": {
            "min_python_version": "3.12",
            "dependencies": [{"name": "mirascope", "version": ">=1.0.0"}, {"name": "pydantic", "version": ">=2.0.0"}],
            "files": [
                {"src": "agent.py", "dest": "agent.py"},
                {"src": "funcn.md", "dest": "funcn.md"},
                {"src": "__init__.py", "dest": "__init__.py"},
            ],
            "template_variables": ["provider", "model"],
            "post_install_message": "Sample agent installed successfully!",
        },
    }

    with open(component_dir / "component.json", "w") as f:
        json.dump(component_json, f, indent=2)

    # Create agent.py
    agent_code = '''"""Sample agent implementation for testing."""

from typing import List

from mirascope.core import Messages, prompt_template
from mirascope.{{provider}} import {{provider}}
from pydantic import BaseModel


class AnalysisResult(BaseModel):
    """Result of the analysis."""

    summary: str
    key_points: List[str]
    confidence: float


@{{provider}}.call(model="{{model}}", response_model=AnalysisResult)
@prompt_template()
async def sample_agent(text: str) -> Messages.Type:
    """Analyze the given text and extract key information.

    Args:
        text: The text to analyze

    Returns:
        AnalysisResult with summary and key points
    """
    return Messages.User(f"""
    Analyze the following text and provide:
    1. A brief summary
    2. Key points (3-5 bullet points)
    3. Your confidence level (0-1)

    Text: {text}
    """)


# For testing without LLM calls
def sample_agent_sync(text: str) -> str:
    """Synchronous version for unit testing."""
    return f"Analysis of: {text[:50]}..."
'''

    with open(component_dir / "agent.py", "w") as f:
        f.write(agent_code)

    # Create __init__.py
    init_code = '''"""Sample agent exports."""

from .agent import sample_agent, sample_agent_sync

__all__ = ["sample_agent", "sample_agent_sync"]
'''

    with open(component_dir / "__init__.py", "w") as f:
        f.write(init_code)

    # Create funcn.md
    funcn_md = """# Sample Agent

A sample agent component for testing the funcn system.

## Overview

This agent analyzes text and extracts key information including:
- Summary of the content
- Key points (3-5 bullet points)
- Confidence level of the analysis

## Usage

```python
from agents.sample_agent import sample_agent

# Analyze some text
result = await sample_agent("Your text here...")

# Access the structured output
print(f"Summary: {result.summary}")
print(f"Key Points: {result.key_points}")
print(f"Confidence: {result.confidence}")
```

## Configuration

The agent supports multiple LLM providers:
- OpenAI (gpt-4, gpt-3.5-turbo)
- Anthropic (claude-3-opus, claude-3-sonnet)
- Google (gemini-pro)

## Requirements

- Python 3.12+
- mirascope >= 1.0.0
- pydantic >= 2.0.0
"""

    with open(component_dir / "funcn.md", "w") as f:
        f.write(funcn_md)


def create_sample_tool_files(component_dir: Path) -> None:
    """Create sample tool component files in the given directory."""
    # Create component.json
    component_json = {
        "name": "sample_tool",
        "type": "tool",
        "version": "0.1.0",
        "description": "A sample tool for testing",
        "author": "Test Author",
        "tags": ["test", "sample", "search"],
        "dependencies": ["requests>=2.25.0"],
        "config": {
            "min_python_version": "3.12",
            "dependencies": [{"name": "requests", "version": ">=2.25.0"}],
            "files": [
                {"src": "tool.py", "dest": "tool.py"},
                {"src": "funcn.md", "dest": "funcn.md"},
                {"src": "__init__.py", "dest": "__init__.py"},
            ],
            "template_variables": [],
            "post_install_message": "Sample tool installed successfully!",
        },
    }

    with open(component_dir / "component.json", "w") as f:
        json.dump(component_json, f, indent=2)

    # Create tool.py
    tool_code = '''"""Sample tool implementation for testing."""

from typing import Dict, List, Optional

import requests


def search_data(
    query: str,
    limit: int = 10,
    filters: Optional[Dict[str, str]] = None
) -> List[Dict[str, str]]:
    """Search for data matching the query.

    Args:
        query: Search query string
        limit: Maximum number of results
        filters: Optional filters to apply

    Returns:
        List of search results
    """
    # For testing, return mock data
    results = []
    for i in range(min(limit, 5)):
        results.append({
            "id": f"result_{i}",
            "title": f"Result for '{query}' - Item {i + 1}",
            "description": f"This is a sample result matching your query: {query}",
            "relevance": 1.0 - (i * 0.1)
        })

    # Apply filters if provided
    if filters:
        for key, value in filters.items():
            results = [r for r in results if value.lower() in str(r.get(key, "")).lower()]

    return results


def fetch_content(url: str, timeout: int = 30) -> str:
    """Fetch content from a URL.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Content from the URL
    """
    # For testing, return mock content
    if "example.com" in url:
        return f"Mock content from {url}"

    # In real implementation, would use requests
    # response = requests.get(url, timeout=timeout)
    # return response.text

    return f"Content from {url}"


async def search_data_async(
    query: str,
    limit: int = 10
) -> List[Dict[str, str]]:
    """Async version of search_data for testing async patterns."""
    # Simply wrap the sync version for testing
    import asyncio
    await asyncio.sleep(0.1)  # Simulate async operation
    return search_data(query, limit)
'''

    with open(component_dir / "tool.py", "w") as f:
        f.write(tool_code)

    # Create __init__.py
    init_code = '''"""Sample tool exports."""

from .tool import fetch_content, search_data, search_data_async

__all__ = ["search_data", "fetch_content", "search_data_async"]
'''

    with open(component_dir / "__init__.py", "w") as f:
        f.write(init_code)

    # Create funcn.md
    funcn_md = """# Sample Tool

A sample tool component for testing the funcn system.

## Overview

This tool provides functionality for:
- Searching data with query and filters
- Fetching content from URLs
- Async search operations

## Functions

### search_data

Search for data matching a query.

```python
from tools.sample_tool import search_data

# Basic search
results = search_data("python testing")

# Search with limit and filters
results = search_data(
    query="python testing",
    limit=5,
    filters={"title": "pytest"}
)
```

### fetch_content

Fetch content from a URL.

```python
from tools.sample_tool import fetch_content

content = fetch_content("https://example.com/api/data")
```

### search_data_async

Async version of search_data.

```python
from tools.sample_tool import search_data_async

results = await search_data_async("async search", limit=10)
```

## Requirements

- Python 3.12+
- requests >= 2.25.0
"""

    with open(component_dir / "funcn.md", "w") as f:
        f.write(funcn_md)


def create_sample_prompt_template_files(component_dir: Path) -> None:
    """Create sample prompt template component files."""
    # Create component.json
    component_json = {
        "name": "sample_prompt_template",
        "type": "prompt_template",
        "version": "0.1.0",
        "description": "A sample prompt template for testing",
        "author": "Test Author",
        "tags": ["test", "sample", "prompt"],
        "dependencies": ["mirascope>=1.0.0"],
        "config": {
            "min_python_version": "3.12",
            "dependencies": [{"name": "mirascope", "version": ">=1.0.0"}],
            "files": [{"src": "prompt.py", "dest": "prompt.py"}, {"src": "funcn.md", "dest": "funcn.md"}],
            "template_variables": ["style", "language"],
            "post_install_message": "Sample prompt template installed!",
        },
    }

    with open(component_dir / "component.json", "w") as f:
        json.dump(component_json, f, indent=2)

    # Create prompt.py
    prompt_code = '''"""Sample prompt template for testing."""

from mirascope.core import prompt_template


@prompt_template()
def analysis_prompt(text: str, style: str = "{{style}}", language: str = "{{language}}") -> str:
    """Create an analysis prompt with configurable style and language.

    Args:
        text: Text to analyze
        style: Analysis style (formal, casual, technical)
        language: Output language

    Returns:
        Formatted prompt string
    """
    return f"""
    Analyze the following text in a {style} style.
    Provide your response in {language}.

    Text to analyze:
    {text}

    Please include:
    1. Main themes
    2. Key insights
    3. Recommendations
    """


@prompt_template()
def summary_prompt(content: str, max_words: int = 100) -> str:
    """Create a summary prompt.

    Args:
        content: Content to summarize
        max_words: Maximum words in summary

    Returns:
        Formatted prompt string
    """
    return f"""
    Summarize the following content in no more than {max_words} words:

    {content}

    Focus on the most important points and maintain clarity.
    """
'''

    with open(component_dir / "prompt.py", "w") as f:
        f.write(prompt_code)

    # Create funcn.md
    funcn_md = """# Sample Prompt Template

Sample prompt templates for testing the funcn system.

## Templates

### analysis_prompt

Configurable analysis prompt with style and language options.

```python
from prompts.sample_prompt_template import analysis_prompt

prompt = analysis_prompt(
    text="Your text here",
    style="technical",
    language="English"
)
```

### summary_prompt

Simple summary prompt with word limit.

```python
from prompts.sample_prompt_template import summary_prompt

prompt = summary_prompt(
    content="Long content here",
    max_words=50
)
```

## Configuration

Template variables:
- `style`: Analysis style (configured during installation)
- `language`: Output language (configured during installation)
"""

    with open(component_dir / "funcn.md", "w") as f:
        f.write(funcn_md)


class ComponentFixtureFactory:
    """Factory for creating component fixtures."""

    @staticmethod
    def create_all_sample_components(base_path: Path) -> dict[str, Path]:
        """Create all sample components in the given base path.

        Returns:
            Dictionary mapping component names to their paths
        """
        components = {}

        # Create sample agent
        agent_dir = base_path / "sample_agent"
        agent_dir.mkdir(exist_ok=True)
        create_sample_agent_files(agent_dir)
        components["sample_agent"] = agent_dir

        # Create sample tool
        tool_dir = base_path / "sample_tool"
        tool_dir.mkdir(exist_ok=True)
        create_sample_tool_files(tool_dir)
        components["sample_tool"] = tool_dir

        # Create sample prompt template
        prompt_dir = base_path / "sample_prompt_template"
        prompt_dir.mkdir(exist_ok=True)
        create_sample_prompt_template_files(prompt_dir)
        components["sample_prompt_template"] = prompt_dir

        return components

    @staticmethod
    def create_invalid_component(base_path: Path, error_type: str = "missing_json") -> Path:
        """Create an invalid component for error testing.

        Args:
            base_path: Base directory for the component
            error_type: Type of error to create

        Returns:
            Path to the invalid component
        """
        invalid_dir = base_path / f"invalid_{error_type}"
        invalid_dir.mkdir(exist_ok=True)

        if error_type == "missing_json":
            # Create component without component.json
            (invalid_dir / "agent.py").write_text("# Missing component.json")

        elif error_type == "invalid_json":
            # Create component with invalid JSON
            (invalid_dir / "component.json").write_text("{ invalid json }")

        elif error_type == "missing_required":
            # Create component.json missing required fields
            component_json = {
                "name": "invalid_component",
                # Missing "type" field
                "version": "0.1.0",
            }
            with open(invalid_dir / "component.json", "w") as f:
                json.dump(component_json, f)

        elif error_type == "invalid_version":
            # Create component with invalid version format
            component_json = {"name": "invalid_component", "type": "agent", "version": "not-a-version", "config": "invalid-config"}
            with open(invalid_dir / "component.json", "w") as f:
                json.dump(component_json, f)

        return invalid_dir
