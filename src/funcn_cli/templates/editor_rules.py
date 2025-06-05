"""Templates for generating editor-specific rule files."""

from __future__ import annotations

CURSOR_RULES_TEMPLATE = """# Funcn Development Rules

You are an expert in Python, Mirascope, and the Funcn AI framework.

## Core Principles

- Write clean, maintainable Python code following PEP 8
- Use Mirascope's functional patterns with `@prompt_template` decorators
- Implement Pydantic models for all LLM responses
- Prefer async/await patterns for optimal performance
- Follow the component structure defined in component.json files

## Mirascope Best Practices

- Always use `@prompt_template` decorators for prompt construction
- Define Pydantic response models for structured outputs
- Use async functions for all LLM calls and tools
- Implement proper error handling and validation
- Include comprehensive docstrings and type hints

## Component Development

- Follow the funcn component structure with proper JSON manifests
- Implement registry dependencies correctly
- Include comprehensive examples and documentation
- Test all functionality before committing
- Support multiple LLM providers when possible

## Available Components

{available_components}

## Environment Setup

Make sure these environment variables are set:
{environment_variables}

## Code Quality

- Use type hints for all function parameters and return values
- Write comprehensive tests for all functionality
- Follow the established patterns in existing components
- Include proper error handling and logging
"""

WINDSURF_RULES_TEMPLATE = """# Funcn AI Development Guidelines

## Project Context
This is a Funcn AI project using Mirascope for LLM integration.

## Key Technologies
- Python 3.12+
- Mirascope for LLM calls and prompt templates
- Pydantic for data validation and response models
- FastAPI for web services
- Lilypad for observability (when enabled)

## Development Patterns

### Mirascope Integration
- Use `@prompt_template` decorators for all prompts
- Implement `response_model` with Pydantic classes
- Prefer async patterns: `async def` for LLM calls
- Use functional tools, not class-based tools

### Component Structure
{component_structure}

### Best Practices
- Follow type hints strictly
- Implement comprehensive error handling
- Include detailed docstrings
- Write tests for all functionality
- Support multiple LLM providers

## Available Components
{available_components}
"""

CLINE_RULES_TEMPLATE = """# Funcn Development Guidelines

## Overview
You're working with a Funcn AI project that uses Mirascope for LLM integrations.

## Core Technologies
- **Python 3.12+**: Primary language
- **Mirascope**: LLM calls and prompt templates
- **Pydantic**: Data validation and response models
- **Funcn Registry**: Component management system

## Development Standards

### Mirascope Patterns
- Use `@prompt_template` decorators for all prompts
- Define Pydantic `response_model` for structured outputs
- Implement async/await patterns for performance
- Support multiple LLM providers (OpenAI, Anthropic, etc.)

### Code Quality
- Type hints for all function signatures
- Comprehensive error handling
- Detailed docstrings following Google style
- Unit tests for all functionality

### Component Development
- Follow the funcn component structure
- Include proper component.json manifests
- Document registry dependencies
- Provide clear usage examples

## Available Components
{available_components}

## Environment Configuration
{environment_variables}
"""

CLAUDE_RULES_TEMPLATE = """# Funcn Development Context

## Project Overview
This is a Funcn AI framework project that provides reusable components for LLM-powered applications.

## Technical Stack
- **Language**: Python 3.12+
- **LLM Framework**: Mirascope
- **Data Validation**: Pydantic
- **Component System**: Funcn Registry
- **Observability**: Lilypad (optional)

## Development Principles

### Mirascope Best Practices
1. **Prompt Templates**: Always use `@prompt_template` decorators
2. **Response Models**: Define Pydantic models for structured LLM outputs
3. **Async Patterns**: Use `async def` for all LLM calls and tools
4. **Multi-Provider**: Support OpenAI, Anthropic, Google, etc.
5. **Error Handling**: Implement comprehensive validation and error recovery

### Component Architecture
- Each component has a `component.json` manifest
- Components can depend on other registry components
- Include comprehensive documentation and examples
- Follow semantic versioning

### Code Quality Standards
- Type hints for all function parameters and returns
- Google-style docstrings
- Comprehensive unit tests
- PEP 8 code formatting
- Proper logging and error handling

## Available Components

{available_components}

## Environment Setup

{environment_variables}

## Common Patterns

### Basic Agent Structure
```python
from mirascope.core import BaseModel, prompt_template
from mirascope.integrations.openai import OpenAICall

class ResponseModel(BaseModel):
    answer: str
    confidence: float

@OpenAICall("gpt-4o-mini", response_model=ResponseModel)
@prompt_template("Answer this question: {{question}}")
def my_agent(question: str): ...
```

### Tool Implementation
```python
from mirascope.core import tool

@tool
def search_web(query: str) -> str:
    \"\"\"Search the web for information.\"\"\"
    # Implementation here
    return "search results"
```
"""

SOURCEGRAPH_RULES_TEMPLATE = """# Funcn Codebase Memory

## Overview
The Funcn AI framework provides reusable components for building LLM-powered applications using Mirascope.

## Key Architecture
- **Component System**: Registry-based components with JSON manifests
- **LLM Integration**: Mirascope for provider-agnostic LLM calls
- **Type Safety**: Pydantic models for all data structures
- **Async First**: All LLM operations use async/await

## Component Categories
{component_categories}

## Available Components
{available_components}

## Development Patterns
- Use `@prompt_template` decorators for all prompts
- Define Pydantic response models for structured outputs
- Implement async functions for LLM calls
- Support multiple LLM providers
- Include comprehensive error handling

## Environment Variables
{environment_variables}

## Common Issues
- Always await async LLM calls
- Include proper type hints
- Follow the component.json manifest structure
- Test with multiple LLM providers
"""

OPENAI_CODEX_RULES_TEMPLATE = """# Funcn Development Guidelines

## Context
Funcn is an AI framework for building LLM-powered applications with reusable components.

## Core Technologies
- Python 3.12+ with type hints
- Mirascope for LLM integration
- Pydantic for data validation
- Component-based architecture

## Development Standards

### Mirascope Integration
- Use `@prompt_template` decorators
- Define Pydantic response models
- Implement async/await patterns
- Support multiple LLM providers

### Component Structure
- component.json manifest required
- Registry dependencies managed
- Documentation in funcn.md format
- Comprehensive examples included

## Available Components
{available_components}

## Environment Setup
{environment_variables}

## Best Practices
- Type all function signatures
- Use async for LLM calls
- Include error handling
- Write comprehensive tests
"""

AMP_CODE_RULES_TEMPLATE = """# Funcn Development Guide

## Project Context
Funcn AI framework using Mirascope for LLM-powered component development.

## Core Stack
- **Python 3.12+**: Primary language with full type hinting
- **Mirascope**: LLM calls, prompt templates, and multi-provider support
- **Pydantic**: Data validation and response models
- **Funcn Registry**: Component management and distribution

## Development Standards

### Mirascope Patterns
- `@prompt_template` decorators for all prompts
- Pydantic `response_model` for structured LLM outputs
- Async/await for all LLM operations
- Multi-provider LLM support (OpenAI, Anthropic, Google)

### Component Development
- component.json manifest defines structure
- Registry dependencies for component reuse
- funcn.md documentation for human consumption
- Comprehensive testing and examples

### Code Quality
- Complete type hints on all functions
- Google-style docstrings
- Comprehensive error handling
- PEP 8 formatting

## Available Components

{available_components}

## Environment Configuration

{environment_variables}

## Common Tasks
- Adding new components to registry
- Implementing Mirascope agents and tools
- Managing LLM provider configurations
- Testing multi-provider compatibility
"""


def generate_editor_rules(editor: str, components: list[dict]) -> str:
    """Generate editor-specific rules content."""

    # Format available components
    if components:
        available_components = "\n".join(
            [
                f"- **{comp.get('name', 'Unknown')}** ({comp.get('type', 'unknown')}): {comp.get('description', 'No description')}"
                for comp in components
            ]
        )
    else:
        available_components = "- No components found"

    # Extract unique environment variables from all components
    env_vars = set()
    for comp in components:
        for env_var in comp.get("environment_variables", []):
            env_vars.add((env_var.get("name", ""), env_var.get("description", "")))

    if env_vars:
        environment_variables = "\n".join([f"- {name}: {desc}" for name, desc in sorted(env_vars) if name])
    else:
        environment_variables = "- No specific environment variables required"

    # Component categories for Sourcegraph
    if editor == "sourcegraph":
        categories: dict[str, list[str]] = {}
        for comp in components:
            comp_type = comp.get("type", "unknown")
            if comp_type not in categories:
                categories[comp_type] = []
            categories[comp_type].append(comp.get("name", "Unknown"))

        component_categories = "\n".join(
            [f"- **{cat_type.title()}**: {', '.join(comps)}" for cat_type, comps in categories.items()]
        )
    else:
        component_categories = ""

    # Component structure info
    component_structure = "Standard funcn component with component.json manifest"

    # Select the appropriate template
    templates = {
        "cursor": CURSOR_RULES_TEMPLATE,
        "windsurf": WINDSURF_RULES_TEMPLATE,
        "cline": CLINE_RULES_TEMPLATE,
        "claude": CLAUDE_RULES_TEMPLATE,
        "sourcegraph": SOURCEGRAPH_RULES_TEMPLATE,
        "openai_codex": OPENAI_CODEX_RULES_TEMPLATE,
        "amp_code": AMP_CODE_RULES_TEMPLATE,
    }

    template = templates.get(editor, CURSOR_RULES_TEMPLATE)

    return template.format(
        available_components=available_components,
        environment_variables=environment_variables,
        component_structure=component_structure,
        component_categories=component_categories,
    )
