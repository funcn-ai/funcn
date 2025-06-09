# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Funcn Development Context

### Project Overview

Funcn is a production-ready component library for Mirascope-powered AI applications. It follows a "copy-and-paste" philosophy similar to shadcn/ui - components are not traditional dependencies but code you copy into your project and customize.

#### Technical Stack

- **Language**: Python 3.12+
- **LLM Framework**: Mirascope (multi-provider support)
- **Data Validation**: Pydantic v2
- **Component System**: Funcn Registry
- **Package Manager**: UV (fast Python package manager)
- **Build System**: Task (taskfile.yml)
- **Environment**: Devbox (reproducible dev environment)
- **Code Quality**: Ruff (linting/formatting), Pre-commit hooks
- **Testing**: Pytest with async support
- **CLI**: Typer framework
- **Observability**: Lilypad (optional)

### Code Standards

**IMPORTANT**: All generated code must follow the standards defined in the `.claude/` directory:

#### Core Standards

- `.claude/standards/code-standards.md` - Comprehensive code style guide
- `.claude/standards/testing-standards.md` - Pytest testing patterns and coverage guidelines
- `.claude/standards/mirascope-lilypad-best-practice-standards.md` - Mirascope patterns and Lilypad observability

#### Workflow & Process

- `.claude/development-workflow.md` - Linear issue tracking and branch management
- `.claude/pre-commit-quick-fixes.md` - Common fixes to apply automatically

#### Claude Code Meta Standards (NEW)

- `.claude/standards/claude-code-meta-standards.md` - Best practices for using Claude Code effectively
- `.claude/standards/meta-prompts-library.md` - Pre-built prompts for meta-programming with Claude
- `.claude/standards/quick-reference.md` - Quick reference for common Claude Code operations
- `.claude/standards/claude-commands.json` - Custom commands for enhanced Claude Code usage

These standards ensure code passes all pre-commit hooks without manual cleanup and follows proper development workflow.

## Development Commands

### Initial Setup

```bash
# Install devbox and project dependencies
task install

# Enter development environment
devbox shell
```

### Common Development Tasks

```bash
# Run tests
task test
pytest                           # Run all tests
pytest tests/test_specific.py   # Run specific test file
pytest -k "test_function_name"  # Run specific test by name
pytest -m unit                  # Run tests by marker (unit, integration, e2e, benchmark)

# Code quality
task lint                       # Run ruff linter with fixes
task format                     # Format code with ruff
task pre-commit                 # Run all pre-commit hooks

# UV package management
task uv:sync                    # Sync dependencies with lockfile
task uv:lock                    # Update lockfile
task uv:update-deps            # Upgrade all dependencies

# Cleanup
task pyclean                    # Remove .pyc and __pycache__
task pyclean dry-run          # Preview what would be cleaned
```

### Docker Commands

```bash
task docker:build              # Build development image
task docker:up                 # Start services (includes Redis)
task docker:down               # Stop services
```

## Project Architecture

### Component Registry Structure

```
packages/funcn_registry/
└── components/
    ├── agents/              # AI agents with specific capabilities
    ├── tools/               # Utility functions for agents
    ├── prompt_templates/    # Reusable prompt patterns
    ├── response_models/     # Pydantic models for structured outputs
    └── evals/              # Evaluation frameworks
```

### Component Anatomy

Each component follows a consistent structure:
```
component_name/
├── component.json          # Metadata, dependencies, configuration
├── agent.py/tool.py       # Main implementation
├── funcn.md               # Documentation (copied to user's project)
└── __init__.py            # Python package file
```

### CLI Tool (`funcn`)

The CLI manages component installation:

- Reads `funcn.json` for project configuration
- Fetches components from the registry
- Places files in configured directories
- Applies template variables (provider, model)
- Installs Python dependencies

### Configuration Flow

1. **funcn.json** - User's project configuration (directories, defaults)
2. **component.json** - Component metadata (files, dependencies, template vars)
3. **Template Variables** - Applied during installation ({{provider}}, {{model}})

## Development Principles

### Mirascope Best Practices

1. **Decorators**: Use `@llm.call()` for LLM calls, `@prompt_template()` for prompts
2. **Response Models**: Define Pydantic models for structured outputs
3. **Async First**: Use `async def` for all LLM calls and tools
4. **Multi-Provider**: Support all Mirascope providers (OpenAI, Anthropic, Google, etc.)
5. **Error Handling**: Implement comprehensive validation and error recovery
6. **Tool Pattern**: Tools are functions, not classes

### Component Requirements

- Must include `component.json` with proper metadata
- Component names must have type suffix (`_agent`, `_tool`, etc.)
- Include comprehensive `funcn.md` documentation
- Support template variables for customization
- Follow semantic versioning
- Test with multiple providers

### Code Quality Standards

- Type hints for all function parameters and returns
- Google-style docstrings
- Comprehensive unit tests
- Ruff formatting (130 char line length)
- No unused imports (auto-fixed by ruff)
- Proper async/await usage

## Available Components

- **text_summarization_agent** (agent): Advanced text summarization agent using chain-of-thought reasoning, few-shot learning, and iterative refinement. Supports multiple styles (technical, executive, simple, academic, journalistic) and progressive summarization with validation.
- **multi_source_news_verification** (agent): Advanced multi-source news verification agent with comprehensive fact-checking tools including academic search, government data verification, social media verification, and expert source validation for combating misinformation
- **multi_agent_coordinator** (agent): Orchestrates multiple specialized agents to solve complex tasks through intelligent task decomposition, agent selection, and result synthesis
- **recruiting_assistant_agent** (agent): Recruiting assistant for finding qualified candidates using Exa websets. Helps with technical recruiting, sales hiring, and executive search.
- **game_theory_analysis** (agent): Analyzes complex strategic situations using game theory principles, identifying equilibria, predicting outcomes, and providing actionable recommendations
- **enhanced_knowledge_graph_agent** (agent): Enhanced knowledge graph extraction using advanced prompt engineering. Features meta-reasoning for strategy planning, chain-of-thought entity extraction with detailed reasoning, multi-pass relationship detection, and self-consistency validation for high-accuracy results.
- **document_segmentation_agent** (agent): Agent for intelligently segmenting documents into logical parts. Supports multiple strategies including semantic, structural, hybrid, and fixed-size segmentation. Features document structure analysis, segment summarization, and optimized chunking for vector embeddings.
- **knowledge_graph_agent** (agent): Agent for extracting structured knowledge from text by identifying entities and their relationships. Builds comprehensive knowledge graph representations with support for hierarchical relationships, graph enrichment, and visualization-ready outputs.
- **prompt_engineering_optimizer** (agent): Advanced prompt optimization agent that analyzes, generates variants, performs A/B testing, and delivers production-ready optimized prompts with comprehensive documentation
- **academic_research_agent** (agent): Academic research agent for finding research papers using Exa websets. Perfect for academics, researchers, and anyone needing to discover scholarly publications.
- **game_playing_catan** (agent): Multi-model turn-based Settlers of Catan game agent supporting AI vs AI, human vs AI, or mixed gameplay with resource management, trading, and strategic building
- **research_assistant_agent** (agent): AI-powered research agent that conducts comprehensive research using Exa search
- **pii_scrubbing_agent** (agent): Agent for detecting and removing Personally Identifiable Information (PII) from text. Combines regex patterns and LLM analysis for comprehensive PII detection. Supports multiple scrubbing methods including masking, redaction, generalization, and synthetic data replacement.
- **dataset_builder_agent** (agent): AI-powered dataset builder that creates curated data collections using Exa Websets with custom criteria and enrichments
- **dnd_game_master** (agent): A comprehensive D&D 5e game master agent with full rules enforcement and persistent campaign state. Features SQLite-based state persistence for multi-session campaigns, fair dice rolling with modifiers, complete D&D 5e API integration, multi-model orchestration, turn-based combat with positioning, spell slot tracking, condition management, death saves, XP/leveling, exhaustion, skill proficiencies, inventory management, and dynamic roleplay with human-in-the-loop support.
- **multi_platform_social_media_manager** (agent): Enhanced multi-platform social media campaign manager with trend analysis, engagement prediction, and real-time adaptation capabilities for comprehensive campaign orchestration
- **decision_quality_assessor** (agent): Comprehensive decision quality assessment agent that analyzes context, evaluates alternatives, detects cognitive biases, and provides actionable recommendations for better decision-making
- **sales_intelligence_agent** (agent): Sales intelligence agent for finding targeted business contacts and companies using Exa websets. Perfect for sales prospecting, lead generation, and market intelligence.
- **market_intelligence_agent** (agent): Market intelligence agent for tracking investment opportunities and market trends using Exa websets. Perfect for VCs, analysts, and business development professionals.
- **web_search_agent** (agent): Unified web search agent supporting multiple providers (DuckDuckGo, Qwant, Exa, Nimble) with configurable search strategies. Features privacy-focused, AI-powered semantic search, structured data extraction, comprehensive, and auto-selection modes.
- **game_playing_diplomacy** (agent): Multi-model turn-based Diplomacy game agent supporting AI vs AI, human vs AI, or mixed gameplay with sophisticated diplomatic negotiation and strategic planning
- **hallucination_detector_agent** (agent): AI-powered hallucination detection agent that verifies factual claims using Exa search
- **dynamic_learning_path** (agent): Generates personalized, adaptive learning paths based on individual skills, goals, and learning preferences with comprehensive resource curation
- **sourcing_assistant_agent** (agent): Sourcing assistant for finding suppliers, manufacturers, and solutions using Exa websets. Perfect for procurement, supply chain management, and technology sourcing.
- **code_generation_execution_agent** (agent): Agent for generating and safely executing Python code. Analyzes code for safety, supports multiple safety levels, and provides recommendations for improvement. Features sandboxed execution environment and comprehensive code analysis.
- **docx_search_tool** (tool): Microsoft Word document search and content extraction tool with advanced text search, regex support, and metadata extraction
- **directory_search_tool** (tool): Advanced file system navigation and search tool with pattern matching, content search, and filtering capabilities
- **sqlalchemy_db** (tool): SQLAlchemy ORM tool for advanced database operations and agent state management
- **firecrawl_scrape_tool** (tool): Firecrawl-powered web scraping tool that extracts clean, structured content from websites. Handles JavaScript-rendered pages and provides multiple output formats including Markdown, HTML, and screenshots.
- **git_repo_search_tool** (tool): Git repository search tool for searching code, files, and commits in both local Git repositories and GitHub. Supports pattern matching, file filtering, and commit history search.
- **code_interpreter_tool** (tool): Safe Python code execution tool with sandboxing, timeout controls, and variable capture
- **pg_search_tool** (tool): PostgreSQL database search and query tool with full-text search, connection pooling, and schema introspection
- **dice_roller** (tool): A fair and transparent dice rolling tool for tabletop RPGs. Supports all standard dice types (d4-d100), modifiers, advantage/disadvantage, and provides detailed roll results with timestamps.
- **mdx_search_tool** (tool): MDX documentation search tool with JSX component parsing, frontmatter support, and section extraction
- **csv_search_tool** (tool): CSV search tool for searching and filtering structured data within CSV files. Supports column-specific searches, data filtering, and both exact and fuzzy matching capabilities.
- **code_docs_search_tool** (tool): Technical documentation search tool for API docs, README files, code comments, docstrings, and code examples
- **json_search_tool** (tool): JSON search tool for searching and querying within JSON files and data structures. Supports JSONPath expressions, fuzzy matching, and searching in both keys and values.
- **pdf_search_tool** (tool): PDF search tool that enables searching for text within PDF documents using fuzzy matching. Extracts text from PDFs and provides context-aware search results with page numbers and match scores.
- **exa_websets_tool** (tool): Advanced web data collection tools using Exa Websets. Create curated collections of web data with search criteria and structured enrichments for building datasets.
- **dnd_5e_api** (tool): A comprehensive tool for accessing official D&D 5th Edition content via the D&D 5e API. Provides detailed information about spells, classes, monsters, equipment, races, feats, skills, conditions, magic items, and more. Includes advanced search with filters and support for all SRD content types.
- **url_content_parser_tool** (tool): URL content parsing tool that extracts clean text content from web pages. Removes scripts, styles, and other noise to provide readable text content.
- **sqlite_db** (tool): SQLite database tool for persistent agent state storage
- **nimble_search_tool** (tool): Multi-API search tool using Nimble's Web, SERP, and Maps APIs for comprehensive search capabilities
- **qwant_search_tool** (tool): Privacy-focused web search tools using Qwant search engine. Provides structured search results with no user tracking, using unified models compatible with other search providers.
- **duckduckgo_search_tool** (tool): DuckDuckGo web search tools with clean, structured results. Provides comprehensive search coverage using the duckduckgo-search library.
- **exa_search_tools** (tool): AI-powered search tools using Exa. Features neural search, direct Q&A, and similarity search with advanced filtering and relevance scoring.
- **youtube_video_search_tool** (tool): YouTube video search and transcript extraction tool for content analysis and research
- **xml_search_tool** (tool): XML data processing tool with XPath queries, namespace support, validation, and advanced search capabilities

## Environment Setup

- ANTHROPIC_API_KEY: API key for Anthropic services (if using Anthropic provider).
- ANTHROPIC_API_KEY: Anthropic API key for Claude models
- ANTHROPIC_API_KEY: Anthropic API key for Claude-based players
- DATABASE_URL: Database connection URL
- DATABASE_URL: PostgreSQL connection string
- EXA_API_KEY: API key for Exa AI search services (if using Exa provider).
- EXA_API_KEY: API key for Exa services
- EXA_API_KEY: API key for Exa services. Get it from https://exa.ai
- EXA_API_KEY: Exa API key for advanced web search (optional, enhances real-time verification)
- FIRECRAWL_API_KEY: API key for Firecrawl services
- GITHUB_TOKEN: GitHub personal access token for searching GitHub repositories
- GOOGLE_API_KEY: API key for Google services (if using Google provider).
- GOOGLE_API_KEY: Google API key for Gemini models
- GOOGLE_API_KEY: Google API key for Gemini-based players
- MISTRAL_API_KEY: Mistral API key for Mistral models
- NIMBLE_API_KEY: API key for Nimble search services (Web API, SERP API, Maps API) (if using Nimble provider).
- NIMBLE_API_KEY: API key for Nimble services
- OPENAI_API_KEY: API key for OpenAI services
- OPENAI_API_KEY: API key for OpenAI services (if using OpenAI provider).
- OPENAI_API_KEY: OpenAI API key for DM and AI players
- OPENAI_API_KEY: OpenAI API key for GPT models
- OPENAI_API_KEY: OpenAI API key for LLM calls
- YOUTUBE_API_KEY: YouTube Data API v3 key

## Common Patterns

### Tool Implementation (Functional Pattern)

```python
# tools/my_search/tool.py
def search_function(query: str, limit: int = 10) -> list[str]:
    """Search for items matching the query.
    
    Args:
        query: The search query string
        limit: Maximum number of results
        
    Returns:
        List of matching results
    """
    # Implementation
    results = []  # Your search logic here
    return results[:limit]

# Export the function
__all__ = ["search_function"]
```

### Agent Using Tools

```python
# agents/research/agent.py
from mirascope import llm, prompt_template
from mirascope.core import BaseModel
from tools.pdf_search import search_pdf_content
from tools.web_search import search_web

class ResearchOutput(BaseModel):
    summary: str
    sources: list[str]
    confidence: float

@llm.call(
    provider="{{provider}}",
    model="{{model}}",
    response_model=ResearchOutput,
    tools=[search_pdf_content, search_web]  # Tools passed here
)
@prompt_template("""
Research the topic: {topic}

Use the available tools to gather information from PDFs and the web.
Provide a comprehensive summary with sources.
""")
async def research_agent(topic: str) -> ResearchOutput:
    """Conducts research using multiple sources."""
    ...

# Usage
result = await research_agent("quantum computing applications")
if tool := result.tool:
    tool_result = tool.call()  # Execute the tool the LLM wants to use
```

### Component with Lilypad Observability

```python
from lilypad import trace

@trace()  # Added when --with-lilypad flag is used
@llm.call(provider="{{provider}}", model="{{model}}")
@prompt_template("Analyze: {text}")
async def analyze_text(text: str) -> str:
    ...
```

### Testing Components

```python
# tests/test_my_agent.py
import pytest
from agents.my_agent import my_agent

@pytest.mark.asyncio
async def test_my_agent():
    result = await my_agent("test input")
    assert result.confidence > 0.5
    assert len(result.summary) > 0

@pytest.mark.unit
def test_tool_function():
    from tools.my_tool import my_function
    result = my_function("query")
    assert isinstance(result, list)
```

## Development Workflow

**CRITICAL**: Follow the Linear issue → Sub-issues → Branch → Commits → PR workflow:

1. **Create Linear Issue with Sub-Issues**: Break complex tasks into smaller sub-issues
2. **Checkout Feature Branch**: Use Linear's branch name from main issue
3. **Work Through Sub-Issues**: One commit per sub-issue for clean history
4. **Update Status**: Mark sub-issues complete as you progress
5. **Create Pull Request**: Reference all completed sub-issues

See `.claude/development-workflow.md` for detailed workflow instructions.

### Task Organization Strategy

**Use Two-Level Task Management:**

- **Linear Projects**: For organizing related issues (external tracking)
- **Claude TODOs**: For fine-grained task tracking during coding

Example workflow:
```python
# Create a project for complex features
project = mcp_linear.create_project(
    name="PDF Parser Tool Implementation",
    teamId=team_id,
    description="Add comprehensive PDF parsing capabilities"
)

# Create issues within the project
issues = [
    mcp_linear.create_issue(title="Setup PDF parser structure", projectId=project.id),
    mcp_linear.create_issue(title="Implement core parsing logic", projectId=project.id),
    mcp_linear.create_issue(title="Add error handling", projectId=project.id),
    mcp_linear.create_issue(title="Write comprehensive tests", projectId=project.id)
]

# Work through each issue with focused commits
git checkout -b jayscambler/fun-123
git commit -m "feat: Setup PDF parser structure #FUN-124"
git commit -m "feat: Implement core parsing logic #FUN-125"
git commit -m "feat: Add error handling #FUN-126"
git commit -m "test: Write comprehensive tests #FUN-127"
```

## Pre-commit Compliance

**CRITICAL**: All Python code MUST pass pre-commit hooks. Before generating code:

1. Review `.claude/code-standards.md` for style guidelines
2. Apply fixes from `.claude/pre-commit-quick-fixes.md` automatically
3. Ensure: proper imports, line length ≤130, docstrings first, no debug statements
4. When editing existing files, match their existing style

Key points to remember:

- Line length: 130 characters maximum
- Imports: Sort by type (stdlib, third-party, local) and alphabetically
- No unused imports or variables (use _ prefix if needed)
- End files with single newline
- Use ruff's fix-only mode expectations

## Testing Standards

**IMPORTANT**: Follow the 80/20 testing rule - focus on the critical paths:

1. **Test Structure**: Organize tests by type (unit/integration/e2e)
2. **Coverage Target**: 80% overall, 90%+ for core business logic
3. **Test Priorities**:
   - Happy path first (most important)
   - Common error cases
   - Critical edge cases only
4. **Skip Testing**: Trivial getters, framework code, generated code

Quick testing checklist:
```bash
# Run specific test types
pytest -m unit              # Fast unit tests only
pytest -m integration       # Integration tests
pytest -m "not slow"        # Skip slow tests

# Run with coverage
pytest --cov=funcn_cli --cov-report=html

# Run tests in parallel
pytest -n auto
```

See `.claude/testing-standards.md` for detailed testing patterns and examples.

## Claude Code Meta Usage

### Using Claude Code Effectively

For optimal Claude Code usage in this project, refer to:

1. **Quick Start**: `.claude/standards/quick-reference.md` - Essential commands and shortcuts
2. **Best Practices**: `.claude/standards/claude-code-meta-standards.md` - Comprehensive workflow patterns
3. **Prompt Library**: `.claude/standards/meta-prompts-library.md` - Pre-built prompts for common tasks
4. **Custom Commands**: `.claude/standards/claude-commands.json` - Project-specific Claude commands

### Key Meta Patterns

#### Extended Thinking

```bash
# For complex problems
"think about the best architecture for this feature"
"think harder about why this bug is occurring"
"think more about performance implications"
```

#### Workflow Automation

```bash
# Use custom commands
/meta-analyze    # Deep codebase analysis
/quick-fix       # Fast bug fixes
/workflow-feature # Complete feature implementation
```

#### Multi-Claude Workflows

```bash
# Run parallel Claude sessions for complex tasks
# Terminal 1: Frontend work
# Terminal 2: Backend work
# Terminal 3: Testing
```

See `.claude/standards/` directory for complete meta-programming documentation.
