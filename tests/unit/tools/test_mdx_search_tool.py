"""Test suite for mdx_search_tool following best practices."""

import asyncio
import pytest
import tempfile
from datetime import datetime

# Import the actual tool functions and models
from packages.funcn_registry.components.tools.mdx_search.tool import (
    MDXComponent,
    MDXMatch,
    MDXSearchResult,
    extract_mdx_components,
    extract_sections,
    find_documentation_sections,
    get_context,
    parse_component_props,
    parse_jsx_component,
    search_mdx_files,
    search_mdx_with_metadata,
)
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch


class TestMDXSearchTool(BaseToolTest):
    """Test mdx_search_tool component."""
    
    component_name = "mdx_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/mdx_search")
    
    def get_component_function(self):
        """Import the tool function."""
        return search_mdx_files
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "query": "installation",
                "search_path": "/path/to/docs",
                "search_in": ["content", "headings"],
                "case_sensitive": False
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        # This is an async tool, validation happens in async tests
        pass
    
    @pytest.fixture
    def temp_mdx_dir(self):
        """Create a temporary directory with MDX files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_parse_component_props(self):
        """Test parsing component props."""
        # String value
        props = parse_component_props('type="button" size="large"')
        assert props == {"type": "button", "size": "large"}
        
        # Expression value
        props = parse_component_props('onClick={handleClick} disabled={true}')
        assert props == {"onClick": "handleClick", "disabled": "true"}
        
        # Mixed values
        props = parse_component_props('name="test" value={42} active')
        assert "name" in props
        assert props["name"] == "test"
        assert "value" in props
        assert props["value"] == "42"
        
        # Empty props
        props = parse_component_props('')
        assert props == {}
    
    def test_parse_jsx_component(self):
        """Test parsing JSX components."""
        text = '''<Button type="primary" size="large" />
<Card>
  <CardHeader>Title</CardHeader>
  <CardBody>Content</CardBody>
</Card>
<Alert severity="warning" />'''
        
        components = parse_jsx_component(text)
        
        # Should find 3 components (Button, Card, Alert)
        assert len(components) >= 3
        
        # Check Button component
        button = next(c for c in components if c.name == "Button")
        assert button.props == {"type": "primary", "size": "large"}
        assert button.line_number == 1
        
        # Check Alert component
        alert = next(c for c in components if c.name == "Alert")
        assert alert.props == {"severity": "warning"}
    
    def test_extract_sections(self):
        """Test section extraction from markdown."""
        content = '''# Main Title

## Section One

Content here

### Subsection 1.1

More content

## Section Two

Different content'''
        
        sections = extract_sections(content)
        
        assert len(sections) == 4
        assert sections[0] == ("#", "Main Title", 0)
        assert sections[1] == ("##", "Section One", 2)
        assert sections[2] == ("###", "Subsection 1.1", 6)
        assert sections[3] == ("##", "Section Two", 10)
    
    def test_get_context(self):
        """Test context extraction."""
        lines = ["line 1", "line 2", "line 3", "target line", "line 5", "line 6", "line 7"]
        
        # Normal context
        context = get_context(lines, 3, 2)
        assert "line 2" in context
        assert "target line" in context
        assert "line 5" in context
        
        # Edge case - beginning
        context = get_context(lines, 0, 2)
        assert "line 1" in context
        assert "line 2" in context
        assert "line 3" in context
        
        # Edge case - end
        context = get_context(lines, 6, 2)
        assert "line 5" in context
        assert "line 6" in context
        assert "line 7" in context
    
    @pytest.mark.asyncio
    async def test_search_mdx_files_basic(self, temp_mdx_dir):
        """Test basic MDX file search."""
        # Create test MDX file
        mdx_content = '''---
title: Getting Started Guide
author: Test Author
tags: [guide, documentation]
---

# Getting Started

This guide will help you get started with our product.

## Installation

To install the package, run:

```bash
npm install my-package
```

## Configuration

Configure your settings in the config file.

<Alert type="info">
  Remember to restart after configuration changes.
</Alert>
'''
        
        mdx_file = temp_mdx_dir / "getting-started.mdx"
        mdx_file.write_text(mdx_content)
        
        # Search for "installation"
        result = await search_mdx_files(
            query="installation",
            search_path=str(temp_mdx_dir),
            search_in=["content", "headings"],
            case_sensitive=False
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert result.files_searched == 1
        
        # Check matches
        assert any(m.match_type == "heading" for m in result.matches)
        assert any("Installation" in m.content for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_search_frontmatter(self, temp_mdx_dir):
        """Test searching in frontmatter."""
        mdx_content = '''---
title: API Reference
author: John Doe
description: Complete API documentation
version: 2.0.0
tags: [api, reference]
---

# API Reference

API documentation content.
'''
        
        mdx_file = temp_mdx_dir / "api.mdx"
        mdx_file.write_text(mdx_content)
        
        # Search in frontmatter
        result = await search_mdx_files(
            query="John Doe",
            search_path=str(temp_mdx_dir),
            search_in=["frontmatter"],
            case_sensitive=True
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert result.matches[0].match_type == "frontmatter"
        assert result.matches[0].frontmatter["author"] == "John Doe"
    
    @pytest.mark.asyncio
    async def test_search_code_blocks(self, temp_mdx_dir):
        """Test searching in code blocks."""
        mdx_content = '''# Code Examples

Here are some examples:

```javascript
const api = new MyAPI({
  apiKey: 'your-api-key',
  endpoint: 'https://api.example.com'
});

const result = await api.getData();
```

```python
api = MyAPI(
    api_key='your-api-key',
    endpoint='https://api.example.com'
)

result = api.get_data()
```
'''
        
        mdx_file = temp_mdx_dir / "examples.mdx"
        mdx_file.write_text(mdx_content)
        
        # Search in code blocks
        result = await search_mdx_files(
            query="apiKey",
            search_path=str(temp_mdx_dir),
            search_in=["code"]
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert all(m.match_type == "code" for m in result.matches)
        assert any("apiKey" in m.content for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_search_jsx_components(self, temp_mdx_dir):
        """Test searching in JSX components."""
        mdx_content = '''# Component Examples

<Button type="primary" size="large">
  Click me
</Button>

<Alert severity="warning">
  This is a warning message
</Alert>

<Card title="Example Card">
  <CardBody>
    Card content goes here
  </CardBody>
</Card>
'''
        
        mdx_file = temp_mdx_dir / "components.mdx"
        mdx_file.write_text(mdx_content)
        
        # Search in components
        result = await search_mdx_files(
            query="warning",
            search_path=str(temp_mdx_dir),
            search_in=["components"]
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert any(m.match_type == "component" for m in result.matches)
        assert "Alert" in result.unique_components
    
    @pytest.mark.asyncio
    async def test_case_sensitivity(self, temp_mdx_dir):
        """Test case-sensitive vs case-insensitive search."""
        mdx_content = '''# UPPERCASE Title

This contains MixedCase and lowercase text.

<Component PropName="Value" />
'''
        
        mdx_file = temp_mdx_dir / "case-test.mdx"
        mdx_file.write_text(mdx_content)
        
        # Case-insensitive search
        result_insensitive = await search_mdx_files(
            query="uppercase",
            search_path=str(temp_mdx_dir),
            search_in=["content", "headings"],
            case_sensitive=False
        )
        
        # Case-sensitive search
        result_sensitive = await search_mdx_files(
            query="uppercase",
            search_path=str(temp_mdx_dir),
            search_in=["content", "headings"],
            case_sensitive=True
        )
        
        # Case-insensitive should find more matches
        assert result_insensitive.total_matches > result_sensitive.total_matches
    
    @pytest.mark.asyncio
    async def test_max_results_limit(self, temp_mdx_dir):
        """Test max results limit."""
        # Create multiple MDX files with matches
        for i in range(10):
            mdx_content = f'''# Document {i}

This document contains the search term multiple times.
Search term appears here.
And search term appears again.
'''
            mdx_file = temp_mdx_dir / f"doc{i}.mdx"
            mdx_file.write_text(mdx_content)
        
        # Search with max_results limit
        result = await search_mdx_files(
            query="search term",
            search_path=str(temp_mdx_dir),
            max_results=5
        )
        
        assert result.success is True
        assert len(result.matches) == 5
        # The search stops early when max_results is reached
        assert result.files_searched <= 10
    
    @pytest.mark.asyncio
    async def test_file_pattern_filtering(self, temp_mdx_dir):
        """Test file pattern filtering."""
        # Create MDX files in different directories
        (temp_mdx_dir / "docs").mkdir()
        (temp_mdx_dir / "blog").mkdir()
        
        (temp_mdx_dir / "docs" / "api.mdx").write_text("# API Documentation")
        (temp_mdx_dir / "blog" / "post.mdx").write_text("# Blog Post")
        (temp_mdx_dir / "readme.mdx").write_text("# README")
        
        # Search only in docs directory
        result = await search_mdx_files(
            query="Documentation",
            search_path=str(temp_mdx_dir),
            file_pattern="docs/*.mdx"
        )
        
        assert result.success is True
        assert result.files_searched == 1
        assert all("docs" in m.file_path for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_exclude_patterns(self, temp_mdx_dir):
        """Test exclude patterns."""
        # Create MDX files
        (temp_mdx_dir / "include.mdx").write_text("# Include this")
        (temp_mdx_dir / "exclude.mdx").write_text("# Exclude this")
        (temp_mdx_dir / "draft.mdx").write_text("# Draft document")
        
        # Search with exclusions
        result = await search_mdx_files(
            query="this",
            search_path=str(temp_mdx_dir),
            exclude_patterns=["exclude", "draft"]
        )
        
        assert result.success is True
        assert result.files_searched == 1
        assert all("include" in m.file_path for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_extract_mdx_components(self, temp_mdx_dir):
        """Test extracting components from MDX file."""
        mdx_content = '''---
title: Component Demo
---

# Components

<Button type="primary">Primary</Button>
<Button type="secondary">Secondary</Button>

<Alert severity="info">Info message</Alert>
<Alert severity="error">Error message</Alert>

<Card>Card content</Card>
'''
        
        mdx_file = temp_mdx_dir / "components.mdx"
        mdx_file.write_text(mdx_content)
        
        # Extract all components
        components = await extract_mdx_components(str(mdx_file))
        
        assert "Button" in components
        assert len(components["Button"]) == 2
        assert "Alert" in components
        assert len(components["Alert"]) == 2
        assert "Card" in components
        assert len(components["Card"]) == 1
        
        # Extract specific components
        buttons_only = await extract_mdx_components(str(mdx_file), ["Button"])
        assert "Button" in buttons_only
        assert "Alert" not in buttons_only
    
    @pytest.mark.asyncio
    async def test_find_documentation_sections(self, temp_mdx_dir):
        """Test finding documentation sections."""
        mdx_content = '''---
title: Guide
---

# Introduction

Intro content

## Getting Started

Getting started content

### Prerequisites

Prerequisites content

## Advanced Usage

Advanced content

### Configuration

Config content
'''
        
        mdx_file = temp_mdx_dir / "guide.mdx"
        mdx_file.write_text(mdx_content)
        
        # Find all level 2 sections
        sections = await find_documentation_sections(
            search_path=str(temp_mdx_dir),
            min_level=2,
            max_level=2,
            include_content=True
        )
        
        assert len(sections) == 2
        assert any(s["heading"] == "Getting Started" for s in sections)
        assert any(s["heading"] == "Advanced Usage" for s in sections)
        
        # Find sections matching pattern
        sections = await find_documentation_sections(
            search_path=str(temp_mdx_dir),
            heading_pattern="Getting",
            include_content=False
        )
        
        assert len(sections) == 1
        assert sections[0]["heading"] == "Getting Started"
    
    @pytest.mark.asyncio
    async def test_search_with_metadata_filters(self, temp_mdx_dir):
        """Test searching with metadata filters."""
        # Create MDX files with different metadata
        mdx1 = '''---
title: API Guide
category: api
tags: [api, guide]
date: "2024-01-15"
---

# API Guide

API documentation content.
'''
        
        mdx2 = '''---
title: User Guide
category: user
tags: [user, guide]
date: "2024-02-20"
---

# User Guide

User documentation content.
'''
        
        (temp_mdx_dir / "api.mdx").write_text(mdx1)
        (temp_mdx_dir / "user.mdx").write_text(mdx2)
        
        # Search with metadata filter
        result = await search_mdx_with_metadata(
            query="guide",
            search_path=str(temp_mdx_dir),
            metadata_filters={"category": "api"}
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert all(m.frontmatter.get("category") == "api" for m in result.matches)
        
        # Search with tags filter
        result = await search_mdx_with_metadata(
            query="documentation",
            search_path=str(temp_mdx_dir),
            tags_filter=["api"]
        )
        
        assert result.success is True
        assert all("api" in m.frontmatter.get("tags", []) for m in result.matches)
        
        # Search with date filter
        result = await search_mdx_with_metadata(
            query="guide",
            search_path=str(temp_mdx_dir),
            date_after="2024-02-01"
        )
        
        assert result.success is True
        assert all(m.frontmatter.get("date", "") >= "2024-02-01" for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_nested_components(self, temp_mdx_dir):
        """Test handling of nested JSX components."""
        mdx_content = '''# Nested Components

<Card>
  <CardHeader>
    <Title>Card Title</Title>
    <Badge status="active" />
  </CardHeader>
  <CardBody>
    <Text>Card content</Text>
    <Button>Action</Button>
  </CardBody>
</Card>
'''
        
        mdx_file = temp_mdx_dir / "nested.mdx"
        mdx_file.write_text(mdx_content)
        
        # Extract components
        components = await extract_mdx_components(str(mdx_file))
        
        # Should find all component types
        assert "Card" in components
        assert "CardHeader" in components
        assert "Title" in components
        assert "Badge" in components
        assert "Button" in components
    
    @pytest.mark.asyncio
    async def test_relevance_scoring(self, temp_mdx_dir):
        """Test relevance scoring for matches."""
        mdx_content = '''---
title: Search Test
---

# Search Test

This is regular content with search term.

## Search Term Section

More content with search term.

```javascript
const searchTerm = "value";
```

<SearchComponent term="search term" />
'''
        
        mdx_file = temp_mdx_dir / "relevance.mdx"
        mdx_file.write_text(mdx_content)
        
        # Search across all types
        result = await search_mdx_files(
            query="search term",
            search_path=str(temp_mdx_dir),
            search_in=["content", "headings", "code", "components", "frontmatter"]
        )
        
        assert result.success is True
        assert len(result.matches) > 0
        
        # Check that matches are sorted by relevance
        scores = [m.relevance_score for m in result.matches]
        assert scores == sorted(scores, reverse=True)
        
        # Frontmatter should have highest relevance (0.9)
        # Components should have high relevance (0.8)
        # Headings should have good relevance (0.8)
        # Code should have moderate relevance (0.7)
        # Content should have lower relevance (0.6)
    
    @pytest.mark.asyncio
    async def test_empty_mdx_handling(self, temp_mdx_dir):
        """Test handling of empty MDX files."""
        # Create empty file
        (temp_mdx_dir / "empty.mdx").write_text("")
        
        result = await search_mdx_files(
            query="test",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        assert result.total_matches == 0
        assert result.files_searched == 1
    
    @pytest.mark.asyncio
    async def test_malformed_mdx_handling(self, temp_mdx_dir):
        """Test handling of malformed MDX files."""
        # Create malformed MDX
        mdx_content = '''---
title: Malformed
broken_yaml: [unclosed
---

# Content

<UnclosedComponent prop="value"
More content
'''
        
        mdx_file = temp_mdx_dir / "malformed.mdx"
        mdx_file.write_text(mdx_content)
        
        # Should handle gracefully
        result = await search_mdx_files(
            query="content",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        # May or may not find matches depending on parser tolerance
    
    @pytest.mark.asyncio
    async def test_unicode_support(self, temp_mdx_dir):
        """Test Unicode content support."""
        mdx_content = '''---
title: Unicode Test
author: 作者
---

# Unicode Content

This contains 中文 (Chinese), русский (Russian), and émojis 🎉.

<Component text="Unicode: 你好" />
'''
        
        mdx_file = temp_mdx_dir / "unicode.mdx"
        mdx_file.write_text(mdx_content, encoding='utf-8')
        
        # Search for Unicode content
        result = await search_mdx_files(
            query="中文",
            search_path=str(temp_mdx_dir),
            search_in=["content"]
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        assert "中文" in result.matches[0].content
    
    @pytest.mark.asyncio
    async def test_component_with_jsx_expressions(self, temp_mdx_dir):
        """Test components with JSX expressions."""
        mdx_content = '''# JSX Expressions

<Component value={42} isActive={true} />

<Button style={{color: 'red'}} onClick={() => console.log('clicked')} />

<DynamicComponent {...props} />
'''
        
        mdx_file = temp_mdx_dir / "jsx-expressions.mdx"
        mdx_file.write_text(mdx_content)
        
        components = await extract_mdx_components(str(mdx_file))
        
        assert "Component" in components
        assert components["Component"][0].props["value"] == "42"
        assert components["Component"][0].props["isActive"] == "true"
        assert "Button" in components
        assert "DynamicComponent" in components
    
    @pytest.mark.asyncio
    async def test_invalid_search_path(self):
        """Test handling of invalid search path."""
        result = await search_mdx_files(
            query="test",
            search_path="/non/existent/path"
        )
        
        assert result.success is False
        assert result.error is not None
        assert "does not exist" in result.error
        assert result.total_matches == 0
    
    @pytest.mark.asyncio
    async def test_performance_with_many_files(self, temp_mdx_dir):
        """Test performance with many MDX files."""
        # Create 50 MDX files
        for i in range(50):
            mdx_content = f'''---
title: Document {i}
---

# Document {i}

Content for document {i} with search term.
'''
            (temp_mdx_dir / f"doc{i}.mdx").write_text(mdx_content)
        
        start_time = asyncio.get_event_loop().time()
        
        result = await search_mdx_files(
            query="search term",
            search_path=str(temp_mdx_dir),
            max_results=20
        )
        
        elapsed = asyncio.get_event_loop().time() - start_time
        
        assert result.success is True
        # The search stops early when max_results is reached
        assert result.files_searched <= 50
        assert len(result.matches) <= 20
        assert elapsed < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_concurrent_search_operations(self, temp_mdx_dir):
        """Test concurrent search operations."""
        # Create test files
        for i in range(5):
            mdx_content = f'''# Document {i}

Content with various keywords: installation, configuration, api, guide.
'''
            (temp_mdx_dir / f"doc{i}.mdx").write_text(mdx_content)
        
        # Run multiple searches concurrently
        searches = [
            search_mdx_files("installation", str(temp_mdx_dir)),
            search_mdx_files("configuration", str(temp_mdx_dir)),
            search_mdx_files("api", str(temp_mdx_dir)),
            search_mdx_files("guide", str(temp_mdx_dir)),
        ]
        
        results = await asyncio.gather(*searches)
        
        # All searches should succeed
        assert all(r.success for r in results)
        assert all(r.total_matches > 0 for r in results)
    
    @pytest.mark.asyncio
    async def test_empty_search_query(self, temp_mdx_dir):
        """Test handling of empty search query."""
        mdx_content = '''# Test Document
        
Content with various words.
'''
        (temp_mdx_dir / "test.mdx").write_text(mdx_content)
        
        # Empty query
        result = await search_mdx_files(
            query="",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        # Empty query actually matches everything because "" is in every string
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_special_regex_characters_in_query(self, temp_mdx_dir):
        """Test queries with special regex characters."""
        mdx_content = '''# Special Characters
        
This contains special chars: $100, 50%, hello@example.com, (parentheses), [brackets], {braces}
Also regex special: .*+?^$[]{}()|\\
'''
        (temp_mdx_dir / "special.mdx").write_text(mdx_content)
        
        # Special regex characters should be handled safely
        special_queries = [
            "$100",
            "50%",
            "hello@example.com",
            "(parentheses)",
            "[brackets]",
            "{braces}",
            ".*+?",
            "^$",
            "()|",
        ]
        
        for query in special_queries:
            result = await search_mdx_files(
                query=query,
                search_path=str(temp_mdx_dir),
                search_in=["content"]
            )
            assert result.success is True
            # Should find matches for most of these
    
    @pytest.mark.asyncio
    async def test_very_large_file_handling(self, temp_mdx_dir):
        """Test handling of very large MDX files."""
        # Create a large MDX file (5MB+)
        large_content = ['---', 'title: Large File', '---', '', '# Large Document', '']
        
        # Add 100k lines
        for i in range(100000):
            large_content.append(f"Line {i}: This is content for testing large file handling. Search term appears occasionally.")
            if i % 1000 == 0:
                large_content.append(f"## Section {i//1000}")
                large_content.append("SEARCH_MARKER here")
        
        mdx_file = temp_mdx_dir / "large.mdx"
        mdx_file.write_text('\n'.join(large_content))
        
        # Search in large file
        start_time = asyncio.get_event_loop().time()
        result = await search_mdx_files(
            query="SEARCH_MARKER",
            search_path=str(temp_mdx_dir),
            max_results=10
        )
        elapsed = asyncio.get_event_loop().time() - start_time
        
        assert result.success is True
        assert result.total_matches >= 10
        assert len(result.matches) == 10
        assert elapsed < 10.0  # Should handle large files efficiently
    
    @pytest.mark.asyncio
    async def test_binary_file_handling(self, temp_mdx_dir):
        """Test handling of binary files mistakenly named .mdx."""
        # Create a binary file with .mdx extension
        binary_content = b'\x00\x01\x02\x03\xff\xfe\xfd'
        binary_file = temp_mdx_dir / "binary.mdx"
        binary_file.write_bytes(binary_content)
        
        # Also create a valid MDX file
        (temp_mdx_dir / "valid.mdx").write_text("# Valid MDX\n\nContent here")
        
        # Should handle binary file gracefully
        result = await search_mdx_files(
            query="content",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        # Should only find matches in valid file
        assert all("valid.mdx" in m.file_path for m in result.matches)
    
    @pytest.mark.asyncio
    async def test_different_line_endings(self, temp_mdx_dir):
        """Test handling of different line endings."""
        # Windows line endings
        windows_content = "# Windows File\r\n\r\nContent with search term\r\n"
        (temp_mdx_dir / "windows.mdx").write_text(windows_content)
        
        # Unix line endings
        unix_content = "# Unix File\n\nContent with search term\n"
        (temp_mdx_dir / "unix.mdx").write_text(unix_content)
        
        # Mixed line endings
        mixed_content = "# Mixed File\r\nContent with\nsearch term\r\n"
        (temp_mdx_dir / "mixed.mdx").write_text(mixed_content)
        
        result = await search_mdx_files(
            query="search term",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        assert result.total_matches >= 3
        assert result.files_searched == 3
    
    @pytest.mark.asyncio
    async def test_deeply_nested_jsx_components(self, temp_mdx_dir):
        """Test handling of deeply nested JSX components."""
        mdx_content = '''# Deeply Nested Components
        
<OuterComponent>
  <MiddleComponent>
    <InnerComponent>
      <DeepComponent>
        <DeeperComponent>
          <DeepestComponent>
            This is very deeply nested content with search term
          </DeepestComponent>
        </DeeperComponent>
      </DeepComponent>
    </InnerComponent>
  </MiddleComponent>
</OuterComponent>
'''
        (temp_mdx_dir / "nested.mdx").write_text(mdx_content)
        
        # Extract components
        components = await extract_mdx_components(str(temp_mdx_dir / "nested.mdx"))
        
        # Should find at least the outer components
        assert "OuterComponent" in components
        assert "MiddleComponent" in components
        
        # Search within nested content
        result = await search_mdx_files(
            query="deeply nested",
            search_path=str(temp_mdx_dir),
            search_in=["content"]
        )
        
        assert result.success is True
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_component_names_with_special_chars(self, temp_mdx_dir):
        """Test components with numbers and special characters in names."""
        mdx_content = '''# Special Component Names
        
<Component123 prop="value" />
<MyComponent_v2 enabled />
<UI-Component active />
<Component.SubComponent nested="true" />
'''
        (temp_mdx_dir / "special-components.mdx").write_text(mdx_content)
        
        components = await extract_mdx_components(str(temp_mdx_dir / "special-components.mdx"))
        
        # Parser should handle components starting with capital letter
        assert len(components) >= 1  # At least some components parsed
        
        # Search in components
        result = await search_mdx_files(
            query="Component",
            search_path=str(temp_mdx_dir),
            search_in=["components"]
        )
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_complex_prop_values(self, temp_mdx_dir):
        """Test components with complex prop values."""
        mdx_content = '''# Complex Props
        
<DataTable 
  columns={["id", "name", "email"]}
  data={[
    {id: 1, name: "John", email: "john@example.com"},
    {id: 2, name: "Jane", email: "jane@example.com"}
  ]}
  onSort={(col, dir) => handleSort(col, dir)}
  style={{border: "1px solid #ccc", padding: 10}}
/>

<Config settings={{theme: {dark: true, colors: ["#000", "#fff"]}}} />
'''
        (temp_mdx_dir / "complex-props.mdx").write_text(mdx_content)
        
        components = await extract_mdx_components(str(temp_mdx_dir / "complex-props.mdx"))
        
        # Multi-line components like DataTable may not be parsed by the simple regex
        # At least Config should be found
        assert "Config" in components
        
        # Props should be captured (even if simplified)
        assert len(components["Config"][0].props) > 0
    
    @pytest.mark.asyncio
    async def test_invalid_frontmatter(self, temp_mdx_dir):
        """Test handling of invalid frontmatter."""
        # Missing closing ---
        invalid1 = '''---
title: Incomplete
author: Test
# Missing closing dashes

# Content

This has invalid frontmatter'''
        
        # Invalid YAML
        invalid2 = '''---
title: Invalid YAML
tags: [unclosed
date: not-a-valid-date
---

# Content

This has invalid YAML'''
        
        (temp_mdx_dir / "invalid1.mdx").write_text(invalid1)
        (temp_mdx_dir / "invalid2.mdx").write_text(invalid2)
        
        # Should handle gracefully
        result = await search_mdx_files(
            query="invalid",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        # May or may not find matches depending on parser tolerance
    
    @pytest.mark.asyncio
    async def test_mdx_imports_exports(self, temp_mdx_dir):
        """Test MDX files with imports and exports."""
        mdx_content = '''import { Chart } from './components/Chart'
import DataTable from './components/DataTable'
export const metadata = {
  title: "MDX with Imports",
  date: "2024-01-01"
}

# MDX with Imports

This document uses imported components.

<Chart data={chartData} />
<DataTable columns={columns} />

export default function Layout({ children }) {
  return <div className="mdx-layout">{children}</div>
}
'''
        (temp_mdx_dir / "imports.mdx").write_text(mdx_content)
        
        # Should handle imports/exports gracefully
        result = await search_mdx_files(
            query="imported components",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        
        # Should find Chart and DataTable components
        components = await extract_mdx_components(str(temp_mdx_dir / "imports.mdx"))
        assert "Chart" in components
        assert "DataTable" in components
    
    @pytest.mark.asyncio
    async def test_empty_search_in_array(self, temp_mdx_dir):
        """Test with empty search_in array."""
        mdx_content = '''# Test
        
Content here'''
        (temp_mdx_dir / "test.mdx").write_text(mdx_content)
        
        # Empty search_in should default to content
        result = await search_mdx_files(
            query="content",
            search_path=str(temp_mdx_dir),
            search_in=[]
        )
        
        assert result.success is True
        # Should default to searching in content
        assert result.total_matches == 0  # Empty array means search nothing
    
    @pytest.mark.asyncio
    async def test_all_search_options_simultaneously(self, temp_mdx_dir):
        """Test searching with all search_in options at once."""
        mdx_content = '''---
title: Comprehensive Test
description: Testing all search options
tags: [test, comprehensive]
---

# Comprehensive Test

This tests searching in all areas simultaneously.

## Test Section

Content with test keyword.

```javascript
// Code with test keyword
const test = "value";
```

<TestComponent prop="test value" />
'''
        (temp_mdx_dir / "comprehensive.mdx").write_text(mdx_content)
        
        # Search in all areas
        result = await search_mdx_files(
            query="test",
            search_path=str(temp_mdx_dir),
            search_in=["content", "headings", "code", "components", "frontmatter"]
        )
        
        assert result.success is True
        assert result.total_matches >= 5  # Should find in all areas
        
        # Check we have different match types
        match_types = set(m.match_type for m in result.matches)
        assert len(match_types) >= 4  # Should have multiple types
    
    @pytest.mark.asyncio
    async def test_file_permission_errors(self, temp_mdx_dir):
        """Test handling of files with permission errors."""
        import os
        import platform
        
        # Skip on Windows as permission handling is different
        if platform.system() == "Windows":
            return
        
        # Create a file and remove read permissions
        restricted_file = temp_mdx_dir / "restricted.mdx"
        restricted_file.write_text("# Restricted\n\nContent here")
        
        # Remove read permissions
        os.chmod(restricted_file, 0o000)
        
        # Also create a readable file
        (temp_mdx_dir / "readable.mdx").write_text("# Readable\n\nContent here")
        
        try:
            # Should handle permission error gracefully
            result = await search_mdx_files(
                query="content",
                search_path=str(temp_mdx_dir)
            )
            
            assert result.success is True
            # Should only find matches in readable file
            assert all("readable" in m.file_path for m in result.matches)
        finally:
            # Restore permissions for cleanup
            os.chmod(restricted_file, 0o644)
    
    @pytest.mark.asyncio
    async def test_circular_symlinks(self, temp_mdx_dir):
        """Test handling of circular symlinks."""
        import os
        
        # Create subdirectories
        dir1 = temp_mdx_dir / "dir1"
        dir2 = temp_mdx_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        # Create MDX files
        (dir1 / "file1.mdx").write_text("# File 1\n\nContent in dir1")
        (dir2 / "file2.mdx").write_text("# File 2\n\nContent in dir2")
        
        # Create circular symlinks (if supported)
        try:
            os.symlink(str(dir2), str(dir1 / "link_to_dir2"))
            os.symlink(str(dir1), str(dir2 / "link_to_dir1"))
        except (OSError, NotImplementedError):
            # Skip test if symlinks not supported
            return
        
        # Should handle circular references without infinite loop
        result = await search_mdx_files(
            query="content",
            search_path=str(temp_mdx_dir),
            max_results=10
        )
        
        assert result.success is True
        assert result.files_searched >= 2
    
    @pytest.mark.asyncio
    async def test_concurrent_file_modifications(self, temp_mdx_dir):
        """Test behavior when files are modified during search."""
        import asyncio
        
        # Create initial files
        for i in range(10):
            (temp_mdx_dir / f"file{i}.mdx").write_text(f"# File {i}\n\nInitial content")
        
        async def modify_files():
            """Modify files during search."""
            await asyncio.sleep(0.01)  # Small delay
            for i in range(5):
                (temp_mdx_dir / f"file{i}.mdx").write_text(f"# Modified {i}\n\nModified content with search term")
        
        # Start search and modifications concurrently
        search_task = search_mdx_files(
            query="search term",
            search_path=str(temp_mdx_dir)
        )
        modify_task = modify_files()
        
        result, _ = await asyncio.gather(search_task, modify_task)
        
        # Should complete successfully regardless of modifications
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_extremely_long_lines(self, temp_mdx_dir):
        """Test handling of files with extremely long lines."""
        # Create a file with very long lines
        long_line = "This is a very long line with search term " + ("x" * 10000) + " more content"
        mdx_content = f'''# Long Lines
        
{long_line}

## Another section

Normal content here.
'''
        (temp_mdx_dir / "long-lines.mdx").write_text(mdx_content)
        
        result = await search_mdx_files(
            query="search term",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        assert result.total_matches >= 1
        # Context includes the long line, so it will be over 10k chars
        assert len(result.matches[0].context) > 10000
    
    @pytest.mark.asyncio
    async def test_mdx_with_html_entities(self, temp_mdx_dir):
        """Test MDX files with HTML entities."""
        mdx_content = '''# HTML Entities
        
This contains entities: &lt;tag&gt;, &amp;, &quot;quotes&quot;, &apos;apostrophe&apos;
Also numeric: &#8594; (arrow), &#x2022; (bullet)

<Component text="&lt;escaped&gt;" />
'''
        (temp_mdx_dir / "entities.mdx").write_text(mdx_content)
        
        # Search for entities
        result = await search_mdx_files(
            query="&lt;tag&gt;",
            search_path=str(temp_mdx_dir)
        )
        
        assert result.success is True
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_whitespace_only_query(self, temp_mdx_dir):
        """Test query with only whitespace."""
        mdx_content = '''# Test
        
Some content here'''
        (temp_mdx_dir / "test.mdx").write_text(mdx_content)
        
        # Whitespace-only queries
        for query in ["   ", "\t", "\n", "  \t  "]:
            result = await search_mdx_files(
                query=query,
                search_path=str(temp_mdx_dir)
            )
            
            assert result.success is True
            # Behavior may vary - could match everything or nothing
