# sygaldry

**Beautiful, production-ready Mirascope components that you can copy and paste into your AI apps.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

## What is sygaldry

sygaldry is a component library specifically designed for Mirascope applications. Instead of being another framework, it's a CLI tool that helps you add production-ready Mirascope components directly to your codebase - components you own and can customize.

Inspired by [shadcn/ui](https://ui.shadcn.com)'s philosophy, sygaldry provides:

- **Pre-built Mirascope Agents** - Research assistants, code generators, data analysts, and more
- **Modular Mirascope Tools** - PDF search, web scraping, API integrations, document parsing
- **Optimized Prompt Templates** - Battle-tested Mirascope prompt templates
- **Response Models** - Pydantic models for Mirascope structured outputs
- **Evaluation Frameworks** - Test and validate your Mirascope applications

## Why sygaldry

### The Problem

Every Mirascope project involves writing the same patterns: PDF parsers, web scrapers, search tools, and agent architectures. You implement the same decorators, response models, and async patterns repeatedly.

### The Solution

sygaldry provides a registry of production-ready Mirascope components that follow best practices. Add them with a single command, customize the provider and model, and get clean code that becomes part of your project.

## How It Works

sygaldry uses a smart configuration system:

1. **Your Project Config (`sygaldry.json`)** - Tells sygaldry where to place components
2. **Component Metadata (`component.json`)** - Defines what files to copy and dependencies
3. **Component Documentation (`sygaldry.md`)** - Becomes part of your codebase

When you add a component:

- The CLI reads your project structure from `sygaldry.json`
- Downloads the component based on its `component.json`
- Places files in the correct directories by component type
- Applies your customizations (provider, model, Lilypad tracing)
- Installs required dependencies

## Installation

```bash
pip install sygaldry-cli
```

Or with uv (recommended):
```bash
uv pip install sygaldry-cli-cli
```

## Quick Start

### 1. Initialize your project

```bash
sygaldry init
```
This creates a `sygaldry.json` configuration file that maps component types to directories:
```json
{
  "agentDirectory": "src/agents",
  "toolDirectory": "src/tools",
  "promptTemplateDirectory": "src/prompts",
  "responseModelDirectory": "src/models",
  "defaultProvider": "openai",
  "defaultModel": "gpt-4o-mini"
}
```

### 2. Add components

```bash
# Add a PDF search tool to src/tools/pdf_search/
sygaldry add pdf_search_tool

# Add a research agent with Claude to src/agents/research_assistant/
sygaldry add research_assistant_agent --provider anthropic --model claude-3-opus

# Add with Lilypad observability
sygaldry add web_search_tool --with-lilypad
```

### 3. Use in your code

```python
from tools.pdf_search import search_pdf_content, PDFSearchArgs
from agents.research_assistant import research_topic

# Components are now part of YOUR codebase with proper Mirascope decorators
result = await search_pdf_content(PDFSearchArgs(
    file_path="research.pdf",
    query="machine learning"
))

# Agent with your chosen provider/model
research = await research_topic(
    topic="quantum computing",
    sources=["arxiv", "scholar"]
)
```

## Component Structure

Each component lives in its own directory, organized by type:

```
your_project/
├── sygaldry.json
├── src/
│   ├── agents/
│   │   └── research_assistant/
│   │       ├── __init__.py
│   │       ├── agent.py      # Mirascope agent implementation
│   │       └── sygaldry.md      # Documentation
│   ├── tools/
│   │   └── pdf_search/
│   │       ├── __init__.py
│   │       ├── tool.py       # Mirascope tool implementation
│   │       └── sygaldry.md
│   └── prompts/
│       └── summarization/
│           ├── __init__.py
│           ├── prompt.py     # Mirascope prompt template
│           └── sygaldry.md
```

## Available Components

Components use type suffixes to prevent naming conflicts:

### Agents

- `academic_research_agent` - Academic paper research with Mirascope agents
- `code_generation_execution_agent` - Generate and execute code safely
- `dataset_builder_agent` - Create datasets from various sources
- `hallucination_detector_agent` - Detect and prevent LLM hallucinations
- `market_intelligence_agent` - Market research and analysis
- `research_assistant_agent` - General-purpose research agent
- `sales_intelligence_agent` - Lead scoring and sales insights
- And many more...

### Tools

- `pdf_search_tool` - Fuzzy search within PDFs using Mirascope tools
- `web_search_tool` - Multi-provider web search
- `code_interpreter_tool` - Safe Python code execution
- `firecrawl_scrape_tool` - Advanced web scraping
- `git_repo_search_tool` - Search code repositories
- And many more...

## Key Features

### Mirascope Native

Components use proper Mirascope patterns - tools as functions, `@llm.call` with tools parameter, `@prompt_template` decorators, and async patterns.

### Provider Agnostic

Works with any Mirascope-supported provider - OpenAI, Anthropic, Google, Mistral, Groq, and more. Switch providers with a flag.

### Smart Dependencies

Each component declares its dependencies. The CLI handles installation automatically.

### Observability Ready

Optional Lilypad integration adds `@lilypad.trace()` decorators for tracing and monitoring.

### Best Practices Built-in

All components follow Mirascope best practices for prompts, tools, response models, and error handling.

## Example: Building a Research App

```bash
# Initialize project
sygaldry init

# Add Mirascope components
sygaldry add research_assistant_agent --provider openai
sygaldry add pdf_search_tool
sygaldry add web_search_tool --with-lilypad

# Your app is ready!
```

```python
# main.py - Clean Mirascope code
from agents.research_assistant import research_topic
from tools.pdf_search import search_pdf_content

# Components already configured with your provider/model
results = await research_topic("quantum computing applications")
pdf_insights = await search_pdf_content(...)
```

## Documentation

For comprehensive documentation, visit [sygaldry.ai/docs](https://sygaldry.ai/docs)

## Community

- GitHub: [github.com/sygaldry-ai/sygaldry](https://github.com/sygaldry-ai/sygaldry)
- Discord: [discord.gg/sygaldry](https://discord.gg/sygaldry)
- Twitter: [@sygaldry_ai](https://twitter.com/sygaldry_ai)

## License

MIT License - you're free to use sygaldry components in any project, commercial or otherwise.

---

**Stop writing boilerplate. Start building with Mirascope best practices.** 
