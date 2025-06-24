"""Test suite for mdx_search_tool following best practices."""

import pytest
from packages.funcn_registry.components.tools.mdx_search.tool import (
    MDXSearchResult,
    extract_mdx_components,
    find_documentation_sections,
    search_mdx_files,
    search_mdx_with_metadata,
)
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest


class TestMDXSearchTool(BaseToolTest):
    """Test mdx_search_tool component."""
    
    component_name = "mdx_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/mdx_search")
    
    def create_test_mdx(self, file_path: Path, content: str) -> Path:
        """Create a test MDX file with specified content."""
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def get_component_function(self):
        """Import the tool function."""
        return search_mdx_files
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "query": "installation",
                "search_in": ["content", "frontmatter"],
                "case_sensitive": False
            },
            {
                "query": "Button",
                "search_in": ["components"],
                "case_sensitive": True
            },
            {
                "query": "configuration",
                "search_in": ["content", "headings"],
                "max_results": 10
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, MDXSearchResult)
        assert isinstance(output.success, bool)
        assert isinstance(output.matches, list)
        assert output.query == input_data["query"]
        
        for match in output.matches:
            assert hasattr(match, "file_path")
            assert hasattr(match, "match_type")
            assert hasattr(match, "line_number")
    
    @pytest.mark.asyncio
    async def test_search_mdx_content(self, tmp_path):
        """Test searching in MDX content sections."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """---
title: Getting Started
author: Test Author
---

# Getting Started

This is the introduction to our documentation.

## Installation

To install the package, run:

```bash
npm install my-package
```

## Configuration

Configure the package by creating a config file.

<CodeExample>
  const config = {
    theme: 'dark',
    language: 'en'
  };
</CodeExample>
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Search for content
        result = await search_mdx_files(
            query="installation",
            search_path=str(tmp_path),
            search_in=["content", "headings"],
            case_sensitive=False
        )
        
        assert result.success
        assert result.total_matches >= 1  # Should find at least in heading
        # Should find in the Installation section
        assert any("installation" in match.content.lower() for match in result.matches)
    
    @pytest.mark.asyncio
    async def test_search_frontmatter(self, tmp_path):
        """Test searching in MDX frontmatter."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """---
title: API Reference
description: Complete API documentation
tags: [api, reference, docs]
author: John Doe
date: 2024-01-01
version: 2.0.0
---

# API Reference

Documentation content here.
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Search in frontmatter
        result = await search_mdx_files(
            query="John Doe",
            search_path=str(tmp_path),
            search_in=["frontmatter"],
            case_sensitive=True
        )
        
        assert result.success
        assert result.total_matches >= 1
        assert any(match.match_type == "frontmatter" for match in result.matches)
        assert any("John Doe" in str(match.frontmatter) for match in result.matches)
    
    @pytest.mark.asyncio
    async def test_search_jsx_components(self, tmp_path):
        """Test searching in JSX components."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """# Component Documentation

<Alert type="warning">
  This is a warning message about deprecated features.
</Alert>

<CodeBlock language="javascript">
  function example() {
    return "Hello World";
  }
</CodeBlock>

<Tabs>
  <Tab label="React">
    React implementation
  </Tab>
  <Tab label="Vue">
    Vue implementation
  </Tab>
</Tabs>
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Search for JSX components
        result = await search_mdx_files(
            query="Alert",
            search_path=str(tmp_path),
            search_in=["components"],
            case_sensitive=True
        )
        
        assert result.success
        assert result.total_matches >= 1
        assert any("Alert" in match.content for match in result.matches)
        
        # Search for component props
        result = await search_mdx_files(
            query="warning",
            search_path=str(tmp_path),
            search_in=["components"],
            case_sensitive=True
        )
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_case_sensitivity(self, tmp_path):
        """Test case-sensitive vs case-insensitive search."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """---
title: Case Test
---

# UPPERCASE heading

This contains MixedCase and lowercase text.

<Component PropName="Value" />
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Case-insensitive search
        result_insensitive = await search_mdx_files(
            query="uppercase",
            search_path=str(tmp_path),
            search_in=["content", "headings"],
            case_sensitive=False
        )
        
        # Case-sensitive search
        result_sensitive = await search_mdx_files(
            query="uppercase",
            search_path=str(tmp_path),
            search_in=["content", "headings"],
            case_sensitive=True
        )
        
        # Case-insensitive should find more matches
        assert result_insensitive.total_matches >= result_sensitive.total_matches
        assert result_insensitive.total_matches >= 2  # In heading and content
    
    @pytest.mark.asyncio
    async def test_code_block_search(self, tmp_path):
        """Test searching within code blocks."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """# Code Examples

Here's how to use the API:

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
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Search in code blocks
        result = await search_mdx_files(
            query="apiKey",
            search_path=str(tmp_path),
            search_in=["code"],
            case_sensitive=True
        )
        
        assert result.success
        assert result.total_matches >= 1  # Should find in code blocks
    
    @pytest.mark.asyncio
    async def test_import_export_statements(self, tmp_path):
        """Test searching in import/export statements."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """import { Button, Card } from './components';
import CodeExample from './CodeExample';
export { metadata } from './metadata';

# Component Usage

<Button>Click me</Button>
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Search in content and components
        result = await search_mdx_files(
            query="Button",
            search_path=str(tmp_path),
            search_in=["content", "components"],
            case_sensitive=True
        )
        
        assert result.success
        # Should find in import and JSX usage
        assert result.total_matches >= 2
    
    @pytest.mark.asyncio
    async def test_nested_components(self, tmp_path):
        """Test searching in nested JSX components."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """# Nested Components

<Card>
  <CardHeader>
    <Title>Important Information</Title>
  </CardHeader>
  <CardBody>
    <Alert severity="info">
      This is nested content with <strong>emphasis</strong>.
    </Alert>
  </CardBody>
</Card>
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Search for nested component
        result = await search_mdx_files(
            query="CardHeader",
            search_path=str(tmp_path),
            search_in=["components"],
            case_sensitive=True
        )
        assert result.success
        assert result.total_matches >= 1
        
        # Search for deeply nested content
        result = await search_mdx_files(
            query="emphasis",
            search_path=str(tmp_path),
            search_in=["content"],
            case_sensitive=True
        )
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_mdx_specific_syntax(self, tmp_path):
        """Test MDX-specific syntax elements."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """export const metadata = {
  title: 'MDX Page',
  description: 'Testing MDX features'
};

# {metadata.title}

<div style={{backgroundColor: 'blue', padding: '20px'}}>
  Styled content with JSX expressions
</div>

{/* This is an MDX comment */}
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Search for JSX expressions
        result = await search_mdx_files(
            query="metadata.title",
            search_path=str(tmp_path),
            search_in=["content"],
            case_sensitive=True
        )
        assert result.success
        assert result.total_matches >= 1
        
        # Search in style objects
        result = await search_mdx_files(
            query="backgroundColor",
            search_path=str(tmp_path),
            search_in=["content"],
            case_sensitive=True
        )
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_table_search(self, tmp_path):
        """Test searching in markdown tables."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """# API Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| getData | Retrieves data from server | id: string |
| postData | Sends data to server | data: object |
| deleteItem | Removes an item | id: string |
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        result = await search_mdx_files(
            query="getData",
            search_path=str(tmp_path),
            search_in=["content"],
            case_sensitive=True
        )
        
        assert result.success
        assert result.total_matches >= 1
        # Should find in table
        assert any("getData" in match.content for match in result.matches)
    
    @pytest.mark.asyncio
    async def test_section_context(self, tmp_path):
        """Test that search results include section context."""
        mdx_file = tmp_path / "test.mdx"
        
        mdx_content = """# Main Title

## Section One

Content in section one mentioning configuration.

### Subsection 1.1

More content here.

## Section Two

Different content also mentioning configuration.
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        result = await search_mdx_files(
            query="configuration",
            search_path=str(tmp_path),
            search_in=["content"],
            case_sensitive=False
        )
        
        assert result.success
        # Should find in multiple sections
        assert result.total_matches >= 2
        # Results should include section context
        for match in result.matches:
            assert match.section is not None or match.match_type == "heading"
    
    @pytest.mark.asyncio
    async def test_empty_mdx_handling(self, tmp_path):
        """Test handling of empty MDX files."""
        mdx_file = tmp_path / "empty.mdx"
        
        self.create_test_mdx(mdx_file, "")
        
        result = await search_mdx_files(
            query="test",
            search_path=str(tmp_path),
            search_in=["content"],
            case_sensitive=False
        )
        
        assert result.success
        assert result.total_matches == 0
    
    @pytest.mark.asyncio
    async def test_large_mdx_performance(self, tmp_path):
        """Test performance with large MDX files."""
        mdx_file = tmp_path / "large.mdx"
        
        # Create large MDX content
        large_content = "# Large Document\n\n"
        for i in range(1000):
            large_content += f"## Section {i}\n\nContent for section {i} with various keywords.\n\n"
        
        self.create_test_mdx(mdx_file, large_content)
        
        import time
        start_time = time.time()
        
        result = await search_mdx_files(
            query="Section 500",
            search_path=str(tmp_path),
            search_in=["content", "headings"],
            case_sensitive=True
        )
        
        elapsed = time.time() - start_time
        
        assert result.success
        # Should complete quickly
        assert elapsed < 2.0
        assert result.total_matches >= 1
    
    @pytest.mark.asyncio
    async def test_extract_mdx_components(self, tmp_path):
        """Test extracting components from MDX files."""
        mdx_file = tmp_path / "components.mdx"
        
        mdx_content = """# Component Demo

<Button variant="primary" onClick={handleClick}>
  Click me
</Button>

<Card title="Sample Card">
  <CardHeader>Header</CardHeader>
  <CardBody>Content</CardBody>
</Card>

<Button variant="secondary">Another Button</Button>
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Extract all components
        components = await extract_mdx_components(str(mdx_file))
        
        assert "Button" in components
        assert len(components["Button"]) == 2
        assert components["Button"][0].props.get("variant") == "primary"
        
        # Extract specific components
        components = await extract_mdx_components(str(mdx_file), ["Card"])
        assert "Card" in components
        assert "Button" not in components
    
    @pytest.mark.asyncio
    async def test_find_documentation_sections(self, tmp_path):
        """Test finding documentation sections by pattern."""
        mdx_file = tmp_path / "docs.mdx"
        
        mdx_content = """---
title: API Documentation
---

# API Reference

## Authentication

Details about authentication.

### API Keys

How to use API keys.

## Rate Limiting

Information about rate limits.

### Handling Rate Limits

Best practices for rate limit handling.
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Find all level 2 sections
        sections = await find_documentation_sections(
            search_path=str(tmp_path),
            min_level=2,
            max_level=2,
            include_content=True
        )
        
        assert len(sections) == 2
        assert any(s["heading"] == "Authentication" for s in sections)
        assert any(s["heading"] == "Rate Limiting" for s in sections)
        
        # Find sections with pattern
        sections = await find_documentation_sections(
            search_path=str(tmp_path),
            heading_pattern=r".*Limit.*",
            include_content=True
        )
        
        assert len(sections) >= 1
        assert any("Limit" in s["heading"] for s in sections)
    
    @pytest.mark.asyncio
    async def test_search_mdx_with_metadata(self, tmp_path):
        """Test searching with metadata filters."""
        # Create multiple MDX files with different metadata
        mdx1 = tmp_path / "post1.mdx"
        mdx2 = tmp_path / "post2.mdx"
        
        mdx_content1 = """---
title: First Post
author: John Doe
tags: [tutorial, javascript]
date: 2024-01-15
---

# First Post

This is a tutorial about JavaScript.
"""
        
        mdx_content2 = """---
title: Second Post
author: Jane Smith
tags: [guide, python]
date: 2024-02-01
---

# Second Post

This is a guide about Python.
"""
        
        self.create_test_mdx(mdx1, mdx_content1)
        self.create_test_mdx(mdx2, mdx_content2)
        
        # Search with metadata filter
        result = await search_mdx_with_metadata(
            query="Post",
            search_path=str(tmp_path),
            metadata_filters={"author": "John Doe"}
        )
        
        assert result.success
        # Should find matches only from John Doe's post
        assert all(match.frontmatter["author"] == "John Doe" for match in result.matches)
        # Should not find matches from Jane Smith's post
        assert not any("post2.mdx" in match.file_path for match in result.matches)
        
        # Search with tag filter
        result = await search_mdx_with_metadata(
            query="about",
            search_path=str(tmp_path),
            tags_filter=["tutorial"]
        )
        
        assert result.success
        assert result.total_matches == 1
        assert "tutorial" in result.matches[0].frontmatter["tags"]
    
    @pytest.mark.asyncio
    async def test_headings_search(self, tmp_path):
        """Test searching specifically in headings."""
        mdx_file = tmp_path / "headings.mdx"
        
        mdx_content = """# Introduction to Testing

## Setting Up Tests

Content about setting up tests.

### Unit Tests

How to write unit tests.

### Integration Tests

How to write integration tests.

## Running Tests

How to run your test suite.
"""
        
        self.create_test_mdx(mdx_file, mdx_content)
        
        # Search in headings only
        result = await search_mdx_files(
            query="Tests",
            search_path=str(tmp_path),
            search_in=["headings"],
            case_sensitive=True
        )
        
        assert result.success
        assert result.total_matches >= 3
        assert all(match.match_type == "heading" for match in result.matches)
    
    @pytest.mark.asyncio
    async def test_exclude_patterns(self, tmp_path):
        """Test file exclusion patterns."""
        # Create files in different directories
        (tmp_path / "docs").mkdir()
        (tmp_path / "drafts").mkdir()
        
        doc_file = tmp_path / "docs" / "published.mdx"
        draft_file = tmp_path / "drafts" / "draft.mdx"
        
        content = "# Test Document\n\nThis contains the search term."
        
        self.create_test_mdx(doc_file, content)
        self.create_test_mdx(draft_file, content)
        
        # Search excluding drafts
        result = await search_mdx_files(
            query="search term",
            search_path=str(tmp_path),
            exclude_patterns=[r"drafts/"],
            case_sensitive=False
        )
        
        assert result.success
        assert result.total_matches == 1
        assert "drafts" not in result.matches[0].file_path
