"""Templates for generating funcn.md documentation files."""

from __future__ import annotations

from .component_type_templates import COMPONENT_TYPE_TEMPLATES, get_template_for_type

LILYPAD_SECTION = """
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing"""

TEMPLATE_FUNCN_MD = """# {component_name}

> A brief description of what this component does.

**Version**: 1.0.0 | **Type**: agent | **License**: MIT
**Authors**: Your Name <your.email@example.com> | **Repository**: https://github.com/your-org/your-repo

## Overview

Provide a detailed description of the component, its purpose, and key use cases.

## Quick Start

### Installation

```bash
funcn add {component_name}
```

### Dependencies

This component requires the following dependencies:

**Registry Dependencies:**
- List any funcn registry components this depends on

**Python Dependencies:**
- List Python packages required

**Environment Variables:**
- `REQUIRED_API_KEY`: Description of what this is for (Required)
- `OPTIONAL_CONFIG`: Description of optional configuration (Optional)

### Basic Usage

```python
# Add basic usage example here
from {component_name} import main_function

result = await main_function("example input")
print(result)
```

## Configuration

### Template Variables

- `provider`: The LLM provider to use (default: openai)
- `model`: The specific model to use (default: gpt-4o-mini)

### Advanced Configuration

Configure template variables using CLI options or environment variables.

## Integration with Mirascope

This component follows Mirascope best practices:

- Uses `@prompt_template` decorators for all prompts
- Implements Pydantic response models for structured outputs
- Supports async/await patterns for optimal performance
- Compatible with multiple LLM providers
- Includes comprehensive error handling

## API Reference

Document the main functions and classes here.

## Advanced Examples

Provide more complex usage examples.

## Troubleshooting

Common issues and their solutions.

## Migration Notes

Any breaking changes or migration guidance.

---

**Key Benefits:**
- List the key benefits of using this component

**Related Components:**
- List related funcn components

**References:**
- Links to relevant documentation
"""

def generate_funcn_md(component_json: dict, existing_readme: str = None) -> str:
    """Generate funcn.md content from component.json data using type-specific templates."""

    # Extract data from component.json
    component_name = component_json.get("name", "")
    description = component_json.get("description", "")
    version = component_json.get("version", "")
    component_type = component_json.get("type", "")
    license_info = component_json.get("license", "")

    # Get the appropriate template for this component type
    template = get_template_for_type(component_type)

    # Format authors
    authors_list = component_json.get("authors", [])
    if authors_list:
        authors = ", ".join([
            f"{a.get('name', '')} <{a.get('email', '')}>" if a.get('email')
            else a.get('name', '')
            for a in authors_list
        ])
    else:
        authors = "Funcn Project <info@funcn.ai>"

    repository_url = component_json.get("repository_url", "")

    # Format dependencies
    registry_deps = component_json.get("registry_dependencies", [])
    if registry_deps:
        registry_dependencies = "\n".join([f"- `{dep}`" for dep in registry_deps])
    else:
        registry_dependencies = "- None"

    python_deps = component_json.get("python_dependencies", [])
    if python_deps:
        python_dep_lines = []
        for dep in python_deps:
            if isinstance(dep, dict):
                # Handle dictionary format: {"name": "package", "version": ">=1.0.0"}
                python_dep_lines.append(f"- `{dep.get('name', '')}` {dep.get('version', '')}")
            elif isinstance(dep, str):
                # Handle string format: "package>=1.0.0"
                python_dep_lines.append(f"- `{dep}`")
            else:
                # Fallback for any other format
                python_dep_lines.append(f"- `{str(dep)}`")
        python_dependencies = "\n".join(python_dep_lines)
    else:
        python_dependencies = "- Standard library only"

    # Format environment variables
    env_vars = component_json.get("environment_variables", [])
    if env_vars:
        env_var_lines = []
        for env in env_vars:
            required = "**Required**" if env.get("required", False) else "Optional"
            env_var_lines.append(f"- `{env.get('name', '')}`: {env.get('description', '')} ({required})")
        environment_variables = "\n".join(env_var_lines)
    else:
        environment_variables = "- None required"

    # Template variables
    template_vars = component_json.get("template_variables", {})
    if template_vars:
        template_var_lines = []
        for key, value in template_vars.items():
            template_var_lines.append(f"- `{key}`: `{value}`")
        template_variables = "\n".join(template_var_lines)
    else:
        template_variables = "- None"

    # Example usage - clean up the code block
    example_usage = component_json.get("example_usage", "")
    if not example_usage:
        # Generate type-specific default usage examples
        if component_type == "agent":
            example_usage = f"""```python
import asyncio
from {component_name} import {component_name}

async def main():
    # Basic agent usage
    response = await {component_name}(
        query="Your question here",
        provider="openai",
        model="gpt-4o-mini"
    )
    print(f"Response: {{response.answer}}")

if __name__ == "__main__":
    asyncio.run(main())
```"""
        elif component_type == "tool":
            example_usage = f"""```python
import asyncio
from {component_name} import tool_function, ToolArgs

async def main():
    # Basic tool usage
    args = ToolArgs(
        param1="value1",
        param2="value2"
    )
    result = await tool_function(args)
    print(f"Result: {{result}}")

if __name__ == "__main__":
    asyncio.run(main())
```"""
        else:
            example_usage = f"""```python
# Basic usage example
from {component_name} import main_function

result = await main_function("example input")
print(result)
```"""

    # Lilypad support
    lilypad_support = LILYPAD_SECTION if component_json.get("supports_lilypad", False) else ""

    # Advanced configuration
    advanced_config = "Configure template variables using CLI options or environment variables."

    # API reference
    api_reference = "See component source code for detailed API documentation."

    # Advanced examples
    advanced_examples = "Check the examples directory for advanced usage patterns."

    # Troubleshooting from post_add_instructions
    troubleshooting = component_json.get("post_add_instructions", "No known issues.")

    # Migration notes
    migration_notes = ""

    # Key benefits from tags
    tags = component_json.get("tags", [])
    if tags:
        key_benefits = "\n".join([f"- **{tag.replace('_', ' ').title()}**" for tag in tags[:5]])
    else:
        key_benefits = "- **High Performance**: Optimized for production use"

    # Related components (from registry dependencies)
    if registry_deps:
        related_components = "\n".join([f"- `{dep}`" for dep in registry_deps])
    else:
        related_components = "- None"

    # References
    references = f"""- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry]({repository_url})"""

    # Use existing README content if available for detailed description
    detailed_description = description
    if existing_readme:
        # Try to extract a better description from existing README
        lines = existing_readme.split('\n')
        # Look for content after the first heading
        for i, line in enumerate(lines):
            if line.startswith('# ') and i < len(lines) - 1:
                # Take next few lines as detailed description
                desc_lines = []
                for j in range(i + 1, min(i + 6, len(lines))):
                    if lines[j].strip() and not lines[j].startswith('#'):
                        desc_lines.append(lines[j].strip())
                    elif lines[j].startswith('#'):
                        break
                if desc_lines:
                    detailed_description = ' '.join(desc_lines)
                break

    return template.format(
        component_name=component_name,
        description=description,
        version=version,
        type=component_type,
        license=license_info,
        authors=authors,
        repository_url=repository_url,
        detailed_description=detailed_description,
        registry_dependencies=registry_dependencies,
        python_dependencies=python_dependencies,
        environment_variables=environment_variables,
        example_usage=example_usage,
        template_variables=template_variables,
        advanced_configuration=advanced_config,
        lilypad_support=lilypad_support,
        api_reference=api_reference,
        advanced_examples=advanced_examples,
        troubleshooting=troubleshooting,
        migration_notes=migration_notes,
        key_benefits=key_benefits,
        related_components=related_components,
        references=references
    )

def generate_template_funcn_md(component_name: str) -> str:
    """Generate a template funcn.md for new components."""
    return TEMPLATE_FUNCN_MD.format(component_name=component_name)
