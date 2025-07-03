"""Tests for sygaldry.md merging functionality."""

import pytest
from src.sygaldry_cli.templates.sygaldry_md_template import merge_with_existing_sygaldry_md


def test_merge_preserves_custom_overview():
    """Test that custom overview sections are preserved."""
    existing_content = """# test_component

> Custom description that user wrote

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

This is a custom overview that the user wrote with specific details
about their use case and implementation notes.

## Quick Start

### Installation

```bash
sygaldry add test_component
```

## Advanced Examples

Custom examples that the user added:

```python
# User's custom example
result = custom_function()
```
"""

    new_content = """# test_component

> Auto-generated description from component.json

**Version**: 0.2.0 | **Type**: tool | **License**: MIT

## Overview

Auto-generated overview from component.json

## Quick Start

### Installation

```bash
sygaldry add test_component
```

### Dependencies

**Python Dependencies:**
- `pydantic` >=2.0.0

## Advanced Examples

Auto-generated examples
"""

    component_data = {
        "name": "test_component",
        "description": "Auto-generated description from component.json",
        "version": "0.2.0",
    }

    result = merge_with_existing_sygaldry_md(existing_content, new_content, component_data)

    # Should preserve custom overview
    assert "This is a custom overview that the user wrote" in result

    # Should update version in header
    assert "**Version**: 0.2.0" in result

    # Should add new dependencies section
    assert "**Python Dependencies:**" in result
    assert "`pydantic` >=2.0.0" in result

    # Should preserve custom examples
    assert "Custom examples that the user added" in result
    assert "result = custom_function()" in result


def test_merge_updates_auto_generated_sections():
    """Test that auto-generated sections are properly updated."""
    existing_content = """# test_component

> Description

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Quick Start

### Installation

```bash
sygaldry add test_component
```

### Dependencies

**Python Dependencies:**
- `old_package` >=1.0.0

## Integration with Mirascope

Old integration info
"""

    new_content = """# test_component

> Description

**Version**: 0.2.0 | **Type**: tool | **License**: MIT

## Quick Start

### Installation

```bash
sygaldry add test_component
```

### Dependencies

**Python Dependencies:**
- `new_package` >=2.0.0
- `another_package` >=1.0.0

## Integration with Mirascope

Updated integration info with new features
"""

    component_data = {"name": "test_component", "description": "Description", "version": "0.2.0"}

    result = merge_with_existing_sygaldry_md(existing_content, new_content, component_data)

    # Should update dependencies (auto-generated section)
    assert "`new_package` >=2.0.0" in result
    assert "`another_package` >=1.0.0" in result
    assert "`old_package` >=1.0.0" not in result

    # Should update integration section (auto-generated)
    assert "Updated integration info with new features" in result
    assert "Old integration info" not in result


def test_merge_preserves_custom_sections():
    """Test that completely custom sections are preserved."""
    existing_content = """# test_component

> Description

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

Standard overview

## Custom Section

This is a completely custom section that the user added
with their own content and examples.

### Custom Subsection

More custom content here.

## API Reference

Custom API documentation
"""

    new_content = """# test_component

> Description

**Version**: 0.2.0 | **Type**: tool | **License**: MIT

## Overview

Updated overview

## API Reference

Auto-generated API reference
"""

    component_data = {"name": "test_component", "description": "Description", "version": "0.2.0"}

    result = merge_with_existing_sygaldry_md(existing_content, new_content, component_data)

    # Should preserve custom sections
    assert "## Custom Section" in result
    assert "This is a completely custom section" in result
    assert "### Custom Subsection" in result

    # Should preserve custom API reference (appears customized)
    assert "Custom API documentation" in result


if __name__ == "__main__":
    pytest.main([__file__])
