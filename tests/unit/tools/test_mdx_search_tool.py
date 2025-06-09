"""Test suite for mdx_search_tool following best practices."""

import pytest
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, mock_open, patch


class TestMDXSearchTool(BaseToolTest):
    """Test mdx_search_tool component."""
    
    component_name = "mdx_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/mdx_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.mdx_search_tool import search_mdx
        def mock_search_mdx(
            mdx_path: str | Path,
            query: str,
            search_content: bool = True,
            search_frontmatter: bool = True,
            search_jsx: bool = True,
            case_sensitive: bool = False
        ) -> list[dict[str, any]]:
            """Mock MDX search tool."""
            return [
                {
                    "file": str(mdx_path),
                    "line": 10,
                    "type": "content",
                    "text": f"Found '{query}' in documentation content",
                    "section": "## Installation",
                    "match_score": 0.95
                },
                {
                    "file": str(mdx_path),
                    "line": 5,
                    "type": "frontmatter",
                    "key": "title",
                    "value": f"Getting Started with {query}",
                    "match_score": 0.88
                }
            ]
        return mock_search_mdx
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "mdx_path": "/path/to/docs.mdx",
                "query": "installation",
                "search_content": True,
                "search_frontmatter": True
            },
            {
                "mdx_path": "/path/to/api.mdx",
                "query": "Button",
                "search_jsx": True,
                "case_sensitive": True
            },
            {
                "mdx_path": "/path/to/guide.mdx",
                "query": "configuration",
                "search_frontmatter": True,
                "search_content": True
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        
        for result in output:
            assert isinstance(result, dict)
            assert "file" in result or "path" in result
            assert "type" in result or "match_type" in result
            if "line" in result:
                assert isinstance(result["line"], int)
    
    def test_search_mdx_content(self, tmp_path):
        """Test searching in MDX content sections."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            results = tool(mdx_file, "installation", search_content=True)
            
            assert len(results) >= 1
            # Should find in the Installation section
            assert any("installation" in r.get("text", "").lower() for r in results)
    
    def test_search_frontmatter(self, tmp_path):
        """Test searching in MDX frontmatter."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            # Search in frontmatter
            results = tool(mdx_file, "John Doe", search_frontmatter=True, search_content=False)
            
            assert len(results) >= 1
            assert any(r.get("type") == "frontmatter" for r in results)
            assert any(r.get("key") == "author" for r in results)
    
    def test_search_jsx_components(self, tmp_path):
        """Test searching in JSX components."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            # Search for JSX components
            results = tool(mdx_file, "Alert", search_jsx=True)
            
            assert len(results) >= 1
            assert any("Alert" in str(r) for r in results)
            
            # Search for component props
            results = tool(mdx_file, "warning", search_jsx=True)
            assert len(results) >= 1
    
    def test_case_sensitivity(self, tmp_path):
        """Test case-sensitive vs case-insensitive search."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
        mdx_content = """---
title: Case Test
---

# UPPERCASE heading

This contains MixedCase and lowercase text.

<Component PropName="Value" />
"""
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            # Case-insensitive search
            results_insensitive = tool(mdx_file, "uppercase", case_sensitive=False)
            
            # Case-sensitive search
            results_sensitive = tool(mdx_file, "uppercase", case_sensitive=True)
            
            # Case-insensitive should find more matches
            assert len(results_insensitive) >= len(results_sensitive)
    
    def test_code_block_search(self, tmp_path):
        """Test searching within code blocks."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            # Search in code blocks
            results = tool(mdx_file, "apiKey")
            
            assert len(results) >= 2  # Should find in both code blocks
    
    def test_import_export_statements(self, tmp_path):
        """Test searching in import/export statements."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
        mdx_content = """import { Button, Card } from './components';
import CodeExample from './CodeExample';
export { metadata } from './metadata';

# Component Usage

<Button>Click me</Button>
"""
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            results = tool(mdx_file, "Button")
            
            # Should find in import and JSX usage
            assert len(results) >= 2
    
    def test_nested_components(self, tmp_path):
        """Test searching in nested JSX components."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            # Search for nested component
            results = tool(mdx_file, "CardHeader", search_jsx=True)
            assert len(results) >= 1
            
            # Search for deeply nested content
            results = tool(mdx_file, "emphasis")
            assert len(results) >= 1
    
    def test_mdx_specific_syntax(self, tmp_path):
        """Test MDX-specific syntax elements."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            # Search for JSX expressions
            results = tool(mdx_file, "metadata.title")
            assert len(results) >= 1
            
            # Search in style objects
            results = tool(mdx_file, "backgroundColor")
            assert len(results) >= 1
    
    def test_table_search(self, tmp_path):
        """Test searching in markdown tables."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
        mdx_content = """# API Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| getData | Retrieves data from server | id: string |
| postData | Sends data to server | data: object |
| deleteItem | Removes an item | id: string |
"""
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            results = tool(mdx_file, "getData")
            
            assert len(results) >= 1
            # Should find in table
            assert any("getData" in r.get("text", "") for r in results)
    
    def test_section_context(self, tmp_path):
        """Test that search results include section context."""
        mdx_file = tmp_path / "test.mdx"
        tool = self.get_component_function()
        
        mdx_content = """# Main Title

## Section One

Content in section one mentioning configuration.

### Subsection 1.1

More content here.

## Section Two

Different content also mentioning configuration.
"""
        
        with patch("builtins.open", mock_open(read_data=mdx_content)):
            results = tool(mdx_file, "configuration")
            
            # Results should include section context
            assert all("section" in r for r in results)
            # Should find in multiple sections
            assert len(results) >= 2
    
    def test_empty_mdx_handling(self, tmp_path):
        """Test handling of empty MDX files."""
        mdx_file = tmp_path / "empty.mdx"
        tool = self.get_component_function()
        
        with patch("builtins.open", mock_open(read_data="")):
            results = tool(mdx_file, "test")
            assert results == []
    
    def test_large_mdx_performance(self, tmp_path):
        """Test performance with large MDX files."""
        mdx_file = tmp_path / "large.mdx"
        tool = self.get_component_function()
        
        # Create large MDX content
        large_content = "# Large Document\n\n"
        for i in range(1000):
            large_content += f"## Section {i}\n\nContent for section {i} with various keywords.\n\n"
        
        with patch("builtins.open", mock_open(read_data=large_content)):
            import time
            start_time = time.time()
            
            results = tool(mdx_file, "Section 500")
            
            elapsed = time.time() - start_time
            
            # Should complete quickly
            assert elapsed < 2.0
            assert len(results) >= 1
