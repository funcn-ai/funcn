"""Templates for generating funcn.md documentation files."""

from __future__ import annotations

import re
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
        authors = ", ".join(
            [f"{a.get('name', '')} <{a.get('email', '')}>" if a.get('email') else a.get('name', '') for a in authors_list]
        )
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

    # Format the template and apply markdown cleanup
    formatted_content = template.format(
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
        references=references,
    )

    # Clean up markdown spacing issues
    return _clean_markdown_spacing(formatted_content)


def generate_template_funcn_md(component_name: str) -> str:
    """Generate a template funcn.md for new components."""
    return TEMPLATE_FUNCN_MD.format(component_name=component_name)


def merge_with_existing_funcn_md(existing_content: str, new_content: str, component_data: dict) -> str:
    """
    Merge existing funcn.md content with newly generated content.

    This function preserves user customizations while updating auto-generated sections.
    It identifies sections that should be preserved vs updated based on markers and content analysis.

    Args:
        existing_content: The current funcn.md content
        new_content: The newly generated funcn.md content
        component_data: Component metadata for context

    Returns:
        Merged content preserving user customizations
    """

    # Sections that are typically auto-generated and should be updated
    AUTO_GENERATED_SECTIONS = {
        "## Quick Start",
        "### Installation",
        "### Dependencies",
        "**Python Dependencies:**",
        "**Environment Variables:**",
        "**Registry Dependencies:**",
        "## Integration with Mirascope",
        "## Troubleshooting",  # This often contains auto-generated post_add_instructions
    }

    # Sections that should be preserved if they contain user customizations
    USER_CUSTOMIZABLE_SECTIONS = {
        "## Overview",
        "### Basic Usage",
        "## Configuration",
        "### Advanced Configuration",
        "## API Reference",
        "## Advanced Examples",
        "### Custom Configuration",
        "### Multi-Provider Usage",
        "### Error Handling",
        "### Batch Processing",
        "## Migration Notes",
    }

    # Parse both documents into sections
    existing_sections = _parse_markdown_sections(existing_content)
    new_sections = _parse_markdown_sections(new_content)

    # Start with the header from new content (version, type, etc. may have changed)
    result_sections = {}

    # Get the header (everything before first ##)
    new_header = _extract_header(new_content)
    existing_header = _extract_header(existing_content)

    # Use new header but preserve any custom description if it's significantly different
    if existing_header and new_header:
        result_header = _merge_headers(existing_header, new_header, component_data)
    else:
        result_header = new_header or existing_header

    # Process each section
    for section_key in set(existing_sections.keys()) | set(new_sections.keys()):
        existing_section = existing_sections.get(section_key, "")
        new_section = new_sections.get(section_key, "")

        # Determine if this section should be auto-updated or preserved
        should_auto_update = any(auto_section in section_key for auto_section in AUTO_GENERATED_SECTIONS)
        is_user_customizable = any(user_section in section_key for user_section in USER_CUSTOMIZABLE_SECTIONS)

        if should_auto_update and new_section:
            # Use new content for auto-generated sections
            result_sections[section_key] = new_section
        elif existing_section and is_user_customizable:
            # Check if existing section has been customized
            if _appears_customized(existing_section, component_data):
                # Preserve user customizations
                result_sections[section_key] = existing_section
            elif new_section:
                # Use new content if existing appears to be boilerplate
                result_sections[section_key] = new_section
            else:
                # Keep existing if no new content
                result_sections[section_key] = existing_section
        elif new_section:
            # Use new content for new sections
            result_sections[section_key] = new_section
        elif existing_section:
            # Preserve existing content for sections not in new content
            result_sections[section_key] = existing_section

    # Reconstruct the document
    result_content = result_header + "\n\n"

    # Add sections in a logical order
    section_order = [
        "## Overview",
        "## Quick Start",
        "### Installation",
        "### Dependencies",
        "### Basic Usage",
        "## Configuration",
        "## Tool Configuration",  # For tools
        "## Agent Configuration",  # For agents
        "## Agent Architecture",  # For agents
        "### Template Variables",
        "### Advanced Configuration",
        "### Input/Output Models",  # For tools
        "### LLM Provider Configuration",  # For agents
        "## Integration with Agents",  # For tools
        "## Integration with Mirascope",
        "## API Reference",
        "## Advanced Examples",
        "## Troubleshooting",
        "## Migration Notes",
    ]

    # Add sections in order, then add any remaining sections
    added_sections = set()
    for section_key in section_order:
        if section_key in result_sections:
            result_content += result_sections[section_key] + "\n\n"
            added_sections.add(section_key)

    # Add any remaining sections that weren't in the standard order
    for section_key, section_content in result_sections.items():
        if section_key not in added_sections:
            result_content += section_content + "\n\n"

    # Clean up markdown spacing and return
    final_content = result_content.rstrip() + "\n"
    return _clean_markdown_spacing(final_content)


def _parse_markdown_sections(content: str) -> dict[str, str]:
    """Parse markdown content into sections based on headers."""
    sections = {}
    current_section = ""
    current_content: list[str] = []

    lines = content.split('\n')

    for line in lines:
        # Check if this is a header (## or ###)
        if line.startswith('## ') or line.startswith('### '):
            # Save previous section if it exists
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()

            # Start new section
            current_section = line.strip()
            current_content = [line]
        elif current_section:
            # Add to current section
            current_content.append(line)

    # Save the last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections


def _extract_header(content: str) -> str:
    """Extract the header section (everything before the first ##)."""
    lines = content.split('\n')
    header_lines = []

    for line in lines:
        if line.startswith('## '):
            break
        header_lines.append(line)

    return '\n'.join(header_lines).strip()


def _merge_headers(existing_header: str, new_header: str, component_data: dict) -> str:
    """Merge headers, preserving custom descriptions while updating metadata."""

    # Extract the title and description from both
    existing_lines = existing_header.split('\n')
    new_lines = new_header.split('\n')

    # Use new title and metadata line (version, type, etc.)
    result_lines = []

    # Find the title line (starts with #)
    new_title = next((line for line in new_lines if line.startswith('# ')), "")
    result_lines.append(new_title)

    # Find the description line (starts with >)
    existing_desc = next((line for line in existing_lines if line.startswith('> ')), "")
    new_desc = next((line for line in new_lines if line.startswith('> ')), "")

    # Use existing description if it appears customized, otherwise use new
    if existing_desc and _appears_customized_description(existing_desc, component_data):
        result_lines.append(existing_desc)
    else:
        result_lines.append(new_desc)

    # Add empty line
    result_lines.append("")

    # Use new metadata line (version, type, etc.)
    new_metadata = next((line for line in new_lines if line.startswith('**Version**')), "")
    if new_metadata:
        result_lines.append(new_metadata)

    return '\n'.join(result_lines)


def _appears_customized(section_content: str, component_data: dict) -> bool:
    """
    Determine if a section appears to have been customized by the user.

    This uses heuristics to detect if content differs significantly from
    what would be auto-generated.
    """

    # Check for common indicators of customization
    customization_indicators = [
        "# Custom",
        "# User",
        "# Note:",
        "# TODO:",
        "# FIXME:",
        "<!-- Custom",
        "<!-- User",
        "**Custom",
        "**Note:",
        "Custom examples",
        "user wrote",
        "specific details",
        "implementation notes",
        "use case",
        "production",
        "custom api",
        "custom section",
        "user added",
        "custom content",
    ]

    # Check string indicators (case insensitive)
    section_lower = section_content.lower()
    if any(indicator.lower() in section_lower for indicator in customization_indicators):
        return True

    # Check length (very long sections likely customized)
    if len(section_content.split('\n')) > 15:
        return True

    # Check for specific examples that don't match component name
    component_name = component_data.get("name", "")
    if component_name and component_name not in section_content and "example" in section_content.lower():
        return True

    # Check if content is significantly different from what would be auto-generated
    # Look for specific patterns that indicate customization
    custom_patterns = [
        "custom_function",
        "our specific",
        "we use",
        "in our",
        "for our",
        "this component provides",
        "when deploying",
        "performance",
        "best when",
    ]

    if any(pattern in section_lower for pattern in custom_patterns):
        return True

    # Check for content that doesn't match typical auto-generated patterns
    auto_generated_patterns = [
        "see component source code",
        "auto-generated",
        "check the examples directory",
        "configure template variables",
        "detailed information on classes",
    ]

    # If it doesn't contain auto-generated patterns and has some content, it might be custom
    has_auto_pattern = any(pattern in section_lower for pattern in auto_generated_patterns)
    has_substantial_content = len(section_content.strip()) > 10

    if not has_auto_pattern and has_substantial_content:
        return True

    return False


def _appears_customized_description(description: str, component_data: dict) -> bool:
    """Check if description appears to be customized vs auto-generated."""

    # If description is significantly different from component.json description
    component_desc = component_data.get("description", "")
    if component_desc and component_desc.lower() not in description.lower():
        # Check if it's not just a case/punctuation difference
        desc_words = set(description.lower().split())
        comp_words = set(component_desc.lower().split())

        # If less than 70% word overlap, consider it customized
        if len(desc_words & comp_words) / max(len(desc_words), len(comp_words)) < 0.7:
            return True

    return False


def _clean_markdown_spacing(content: str) -> str:
    """
    Clean up markdown spacing issues to fix linting problems.

    Fixes:
    - MD032: Ensures blank lines around lists
    - MD012: Removes multiple consecutive blank lines
    """
    lines = content.split('\n')
    cleaned_lines = []

    for i, line in enumerate(lines):
        # Check if current line is a list item
        is_list_item = line.strip().startswith('- ') or line.strip().startswith('* ')

        # Check if previous line exists and is not a list item
        prev_line = lines[i - 1] if i > 0 else ""
        prev_is_list = prev_line.strip().startswith('- ') or prev_line.strip().startswith('* ')
        prev_is_empty = prev_line.strip() == ""
        prev_is_header = prev_line.startswith('#')

        # Check if next line exists and is not a list item
        next_line = lines[i + 1] if i < len(lines) - 1 else ""
        next_is_list = next_line.strip().startswith('- ') or next_line.strip().startswith('* ')
        next_is_empty = next_line.strip() == ""
        next_is_header = next_line.startswith('#')

        # MD032: Add blank line before list if needed
        if is_list_item and not prev_is_list and not prev_is_empty and not prev_is_header and prev_line.strip() != "":
            cleaned_lines.append("")

        # Add the current line
        cleaned_lines.append(line)

        # MD032: Add blank line after list if needed
        if is_list_item and not next_is_list and not next_is_empty and not next_is_header and next_line.strip() != "":
            cleaned_lines.append("")

    # MD012: Remove multiple consecutive blank lines
    final_lines = []
    consecutive_blanks = 0

    for line in cleaned_lines:
        if line.strip() == '':
            consecutive_blanks += 1
            if consecutive_blanks <= 1:  # Allow only one blank line
                final_lines.append(line)
        else:
            consecutive_blanks = 0
            final_lines.append(line)

    return '\n'.join(final_lines)
