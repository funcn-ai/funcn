# funcn

**Production-ready Mirascope components that you can copy and paste into your AI apps.**

A component library for Mirascope-powered applications, providing reusable agents, tools, response models, prompt templates, and evaluation frameworks. Built with the same philosophy as [shadcn/ui](https://ui.shadcn.com) - this is NOT a traditional package dependency, but a collection of components you copy into your project and customize.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/funcn.svg)](https://badge.fury.io/py/funcn)

## Why funcn?

Building AI applications with Mirascope often involves writing the same patterns repeatedly - search tools, web scrapers, document parsers, and agent architectures. funcn provides:

- **Production-Ready Mirascope Components** - Battle-tested agents, tools, and models built with Mirascope best practices
- **Copy & Customize** - Not a dependency, but code you own and can modify
- **Mirascope Native** - Built specifically for Mirascope with proper decorators, response models, and async patterns
- **Smart CLI** - Intelligently places components based on your project configuration
- **Provider Agnostic** - Works with OpenAI, Anthropic, Google, Mistral, and any Mirascope-supported provider
- **Built-in Observability** - Optional Lilypad integration for tracing and monitoring

## How funcn Works

funcn uses a three-tier configuration system:

1. **`funcn.json`** - Your project configuration that tells the CLI where to place components
2. **`component.json`** - Each component's metadata, dependencies, and structure
3. **`funcn.md`** - Component documentation that becomes part of your codebase

When you run `funcn add <component>`, the CLI:

1. Reads your `funcn.json` to understand your project structure
2. Fetches the component's `component.json` to know what files to copy
3. Places files in the correct directories based on component type
4. Installs any required dependencies
5. Applies any customizations (provider, model, Lilypad integration)

📖 **[See the complete configuration flow example](examples/configuration_flow.md)** to understand how all pieces work together.

## Quick Start

### Installation

```bash
# Install the CLI
pip install funcn

# Or with uv (recommended)
uv pip install funcn
```

### Initialize Your Project

```bash
# Create a funcn configuration file
funcn init

# This creates a funcn.json with your project structure
```

Your `funcn.json` might look like:
```json
{
  "$schema": "./funcn.schema.json",
  "agentDirectory": "src/agents",
  "toolDirectory": "src/tools",
  "promptTemplateDirectory": "src/prompts",
  "responseModelDirectory": "src/models",
  "evalDirectory": "src/evals",
  "aliases": {
    "agents": "@/agents",
    "tools": "@/tools",
    "prompts": "@/prompts"
  },
  "defaultProvider": "openai",
  "defaultModel": "gpt-4o-mini",
  "stream": false
}
```

### Add Components

```bash
# Add a PDF search tool to src/tools/pdf_search/
funcn add pdf_search_tool

# Add a web search agent with custom provider to src/agents/web_search/
funcn add web_search_agent --provider anthropic --model claude-3-opus

# Add with observability to src/agents/research_assistant/
funcn add research_assistant_agent --with-lilypad

# Add from a URL
funcn add https://your-registry.com/components/custom_agent.json
```

## Component Architecture

### Directory Structure

Components are organized by type, with each component in its own directory:

```
your_project/
├── funcn.json                 # Your project configuration
├── src/
│   ├── agents/               # Agent components (from agentDirectory)
│   │   ├── research_assistant/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py     # Main agent implementation
│   │   │   └── funcn.md     # Component documentation
│   │   └── web_search/
│   │       ├── __init__.py
│   │       ├── agent.py
│   │       └── funcn.md
│   ├── tools/                # Tool components (from toolDirectory)
│   │   ├── pdf_search/
│   │   │   ├── __init__.py
│   │   │   ├── tool.py      # Main tool implementation
│   │   │   └── funcn.md
│   │   └── csv_search/
│   │       ├── __init__.py
│   │       ├── tool.py
│   │       └── funcn.md
│   ├── prompts/              # Prompt templates (from promptTemplateDirectory)
│   │   └── summarization/
│   │       ├── __init__.py
│   │       ├── prompt.py
│   │       └── funcn.md
│   └── models/               # Response models (from responseModelDirectory)
│       └── research_output/
│           ├── __init__.py
│           ├── model.py
│           └── funcn.md
```

### Component Configuration

Each component includes a `component.json` that defines:

```json
{
  "$schema": "https://funcn.ai/schemas/component.json",
  "name": "pdf_search",
  "version": "0.1.0",
  "type": "tool",  // Determines which directory to use
  "description": "Search within PDF documents using fuzzy matching",
  "files_to_copy": [
    {
      "source": "tool.py",
      "destination": "tool.py",
      "type": "module"
    },
    {
      "source": "__init__.py",
      "destination": "__init__.py",
      "type": "init_file"
    }
  ],
  "target_directory_key": "toolDirectory",  // Which funcn.json key to use
  "python_dependencies": [
    {"name": "PyPDF2", "version": ">=3.0.0"},
    {"name": "fuzzywuzzy", "version": ">=0.18.0"}
  ],
  "supports_lilypad": true,
  "template_variables": {
    "provider": "{{provider}}",
    "model": "{{model}}"
  }
}
```

### Mirascope Integration

All components follow Mirascope best practices:

```python
# Example tool component (functional pattern)
def search_pdf_content(file_path: str, query: str) -> str:
    """Search within a PDF document for the given query."""
    # Tool implementation
    with open(file_path, 'rb') as f:
        # PDF processing logic
        return f"Found {query} in {file_path}"

# Example agent using the tool
@llm.call(provider="{{provider}}", model="{{model}}", tools=[search_pdf_content])
@prompt_template("""
Analyze the following research topic: {topic}
Use the search tool to find relevant information in the provided PDFs.
""")
async def research_topic(topic: str, pdf_files: list[str]) -> str:
    """Research a topic using PDF search tools."""
    ...

# The agent can now call the tool when needed
response = await research_topic("machine learning", ["paper1.pdf", "paper2.pdf"])
if tool := response.tool:
    result = tool.call()  # Executes search_pdf_content with LLM-provided args
```

## Available Components

Components are named with type suffixes in the registry to prevent conflicts, but installed in clean directories:

### Agents

Registry name → Installation directory

- `academic_research_agent` → `agents/academic_research/` - Academic paper research and analysis
- `code_generation_execution_agent` → `agents/code_generation_execution/` - Code generation with execution capabilities
- `dataset_builder_agent` → `agents/dataset_builder/` - Automated dataset creation and curation
- `document_segmentation_agent` → `agents/document_segmentation/` - Intelligent document chunking
- `hallucination_detector_agent` → `agents/hallucination_detector/` - Detect and prevent LLM hallucinations
- `knowledge_graph_agent` → `agents/knowledge_graph/` - Build and query knowledge graphs
- `market_intelligence_agent` → `agents/market_intelligence/` - Market research and competitive analysis
- `pii_scrubbing_agent` → `agents/pii_scrubbing/` - Remove personally identifiable information
- `recruiting_assistant_agent` → `agents/recruiting_assistant/` - Resume screening and candidate matching
- `research_assistant_agent` → `agents/research_assistant/` - General research and information gathering
- `sales_intelligence_agent` → `agents/sales_intelligence/` - Lead qualification and sales insights
- `text_summarization_agent` → `agents/text_summarization/` - Multi-format text summarization
- `web_search_agent` → `agents/web_search/` - Advanced web search with multiple providers

### Tools

Registry name → Installation directory

- `pdf_search_tool` → `tools/pdf_search/` - Search within PDF documents with fuzzy matching
- `csv_search_tool` → `tools/csv_search/` - Query and analyze CSV files
- `code_docs_search_tool` → `tools/code_docs_search/` - Search code documentation
- `code_interpreter_tool` → `tools/code_interpreter/` - Execute Python code safely
- `directory_search_tool` → `tools/directory_search/` - File system navigation and search
- `duckduckgo_search_tool` → `tools/duckduckgo_search/` - Web search via DuckDuckGo
- `exa_search_tool` → `tools/exa_search/` - Neural search with Exa API
- `firecrawl_scrape_tool` → `tools/firecrawl_scrape/` - Advanced web scraping
- `git_repo_search_tool` → `tools/git_repo_search/` - Search within Git repositories
- `json_search_tool` → `tools/json_search/` - Query JSON documents
- `qwant_search_tool` → `tools/qwant_search/` - Privacy-focused web search
- `url_content_parser_tool` → `tools/url_content_parser/` - Extract and parse web content
- `youtube_video_search_tool` → `tools/youtube_video_search/` - Search and analyze YouTube videos

### Prompt Templates (`prompts`)

Mirascope prompt templates:

- **Advanced Techniques** - Chain of thought, few-shot learning
- **Common Patterns** - Reusable prompt patterns
- **Text Processing** - Summarization, extraction, transformation

### Response Models (`models`)

Pydantic models for Mirascope structured outputs

### Evaluations (`evals`)

Mirascope evaluation frameworks for testing LLM applications

## Customization During Installation

The CLI supports customization flags that modify components during installation:

```bash
# These flags customize the component's code
funcn add research_assistant \
  --provider anthropic \          # Sets @llm.call(provider="anthropic")
  --model claude-3-opus \         # Sets @llm.call(model="claude-3-opus")
  --with-lilypad \               # Adds @lilypad.trace() decorators
  --stream                       # Enables streaming responses
```

The CLI uses template variables in the component files to apply these customizations.

## Development

### Prerequisites

- Python 3.12+
- [devbox](https://www.jetpack.io/devbox/) (recommended)
- [task](https://taskfile.dev/) (recommended)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/funcn-ai/funcn
cd funcn

# Install dependencies
task install

# Enter development shell (with devbox)
devbox shell
```

### Running Tests

```bash
# Run all tests
task test

# Run with coverage
task test:coverage
```

## Creating Custom Components

### 1. Choose Component Type and Create Directory

```bash
# For a tool component
mkdir -p packages/funcn_registry/components/tools/my_tool

# For an agent component
mkdir -p packages/funcn_registry/components/agents/my_agent
```

### 2. Create component.json

**Important**: Component names must include a type suffix to avoid registry conflicts:

- Agents: `_agent` (e.g., `research_agent`)
- Tools: `_tool` (e.g., `pdf_search_tool`)
- Prompts: `_prompt` (e.g., `summarization_prompt`)
- Models: `_model` (e.g., `research_output_model`)
- Evals: `_eval` (e.g., `accuracy_eval`)

```json
{
  "$schema": "https://funcn.ai/schemas/component.json",
  "name": "my_search_tool",  // Note the _tool suffix
  "version": "0.1.0",
  "type": "tool",
  "description": "My custom Mirascope tool",
  "files_to_copy": [
    {"source": "tool.py", "destination": "tool.py", "type": "module"},
    {"source": "__init__.py", "destination": "__init__.py", "type": "init_file"}
  ],
  "target_directory_key": "toolDirectory",
  "python_dependencies": [
    {"name": "requests", "version": ">=2.28.0"}
  ],
  "supports_lilypad": true,
  "template_variables": {
    "provider": "{{provider}}",
    "model": "{{model}}"
  }
}
```

### 3. Implement the Component

```python
# tool.py - Mirascope functional tool pattern
def my_search_function(query: str, limit: int = 10) -> list[str]:
    """
    Search for items matching the query.
    
    Args:
        query: The search query string
        limit: Maximum number of results to return
        
    Returns:
        List of matching results
    """
    # Your actual implementation here
    results = []  # Search logic
    return results[:limit]

# Export the tool function
__all__ = ["my_search_function"]
```

For agents that use tools:
```python
# agent.py
from mirascope import llm, prompt_template
from tools.my_search import my_search_function

@llm.call(
    provider="{{provider}}", 
    model="{{model}}", 
    tools=[my_search_function]  # Tools are passed here
)
@prompt_template("Help me find information about: {topic}")
async def research_agent(topic: str) -> str:
    """Agent that can search for information."""
    ...
```

### 4. Create funcn.md Documentation

The `funcn.md` file is a crucial part of each component that serves multiple purposes:

- **Documentation**: Comprehensive guide for using the component
- **Context**: Provides context to LLMs when using the component
- **Examples**: Shows real-world usage patterns
- **Configuration**: Documents available options and customizations

Example `funcn.md` structure:
```markdown
# Component Name

Brief description of what this component does.

## Overview
Detailed explanation of the component's purpose and capabilities.

## Configuration
- `provider`: LLM provider (default: from funcn.json)
- `model`: Model to use (default: from funcn.json)
- Template variables and their effects

## Usage Examples
\```python
# Basic usage
from tools.my_tool import my_tool_function
result = await my_tool_function(...)
\```

## API Reference
Detailed documentation of functions, classes, and parameters.

## Best Practices
Tips for optimal usage with Mirascope.
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Adding Components to the Registry

1. Follow the component structure guidelines
2. Use Mirascope decorators and patterns
3. Include comprehensive tests
4. Document in `funcn.md`
5. Ensure all dependencies are specified
6. Test with multiple LLM providers

## Community

- **Discord**: [Join our community](https://discord.gg/funcn)
- **Twitter**: [@funcn_ai](https://twitter.com/funcn_ai)
- **Blog**: [funcn.ai/blog](https://funcn.ai/blog)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by [shadcn/ui](https://ui.shadcn.com)'s approach to component libraries
- Built specifically for the [Mirascope](https://mirascope.com) ecosystem
- Special thanks to all contributors

---

**funcn** - Build Mirascope applications faster with components you can trust and customize.
