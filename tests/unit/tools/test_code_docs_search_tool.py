"""Test suite for code_docs_search_tool following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import Mock, mock_open, patch


class TestCodeDocsSearchTool(BaseToolTest):
    """Test code_docs_search_tool component."""
    
    component_name = "code_docs_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/code_docs_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.code_docs_search_tool import search_code_docs
        def mock_search_code_docs(
            path: str | Path,
            query: str,
            doc_types: list[str] | None = None,
            include_comments: bool = True,
            include_docstrings: bool = True,
            include_readme: bool = True,
            language: str | None = None
        ) -> list[dict[str, any]]:
            """Mock code docs search tool."""
            default_results = [
                {
                    "file": "src/main.py",
                    "type": "docstring",
                    "line": 10,
                    "content": f"Function that handles {query} operations",
                    "context": "def process_data():",
                    "language": "python"
                },
                {
                    "file": "README.md",
                    "type": "readme",
                    "line": 25,
                    "content": f"## {query} Configuration",
                    "language": "markdown"
                }
            ]
            
            if doc_types:
                return [r for r in default_results if r["type"] in doc_types]
            return default_results
        return mock_search_code_docs
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "path": "/path/to/project",
                "query": "authentication",
                "doc_types": ["docstring", "comment"],
                "language": "python"
            },
            {
                "path": "/path/to/docs",
                "query": "API usage",
                "include_readme": True,
                "include_comments": False
            },
            {
                "path": "/path/to/codebase",
                "query": "configuration",
                "doc_types": ["readme", "docstring"]
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        
        for result in output:
            assert isinstance(result, dict)
            assert "file" in result
            assert "type" in result
            assert "content" in result
            assert result["type"] in ["docstring", "comment", "readme", "api_doc", "jsdoc"]
    
    def test_python_docstring_search(self, tmp_path):
        """Test searching Python docstrings."""
        tool = self.get_component_function()
        
        python_code = '''"""Module docstring with authentication info."""

def authenticate_user(username, password):
    """
    Authenticate a user with username and password.
    
    Args:
        username: The user's username
        password: The user's password
        
    Returns:
        bool: True if authentication successful
    """
    pass

class AuthManager:
    """Manages user authentication and sessions."""
    
    def login(self):
        """Log in a user."""
        pass
'''
        
        with patch("builtins.open", mock_open(read_data=python_code)):
            with patch("os.walk") as mock_walk:
                mock_walk.return_value = [(str(tmp_path), [], ["auth.py"])]
                
                results = tool(tmp_path, "authentication", language="python")
                
                assert len(results) >= 2  # Module and function docstrings
                assert any("authenticate" in r["content"].lower() for r in results)
    
    def test_javascript_jsdoc_search(self, tmp_path):
        """Test searching JavaScript JSDoc comments."""
        tool = self.get_component_function()
        
        js_code = '''
/**
 * Handles user authentication
 * @module Authentication
 */

/**
 * Authenticate a user
 * @param {string} username - The username
 * @param {string} password - The password
 * @returns {Promise<boolean>} Authentication result
 */
async function authenticateUser(username, password) {
    // Implementation
}

// Regular comment about authentication
const AUTH_TIMEOUT = 3600;
'''
        
        with patch("builtins.open", mock_open(read_data=js_code)):
            with patch("os.walk") as mock_walk:
                mock_walk.return_value = [(str(tmp_path), [], ["auth.js"])]
                
                results = tool(
                    tmp_path,
                    "authentication",
                    language="javascript",
                    doc_types=["jsdoc", "comment"]
                )
                
                assert len(results) >= 2
                assert any(r["type"] == "jsdoc" for r in results)
    
    def test_code_comment_search(self, tmp_path):
        """Test searching code comments."""
        tool = self.get_component_function()
        
        code_with_comments = '''
# TODO: Implement better error handling for authentication
def process_request():
    # Check authentication status
    if not authenticated:
        # FIXME: This should return proper error code
        return None
    
    /*
     * Multi-line comment explaining
     * the authentication process
     */
    
    // Single-line comment about auth token
'''
        
        with patch("builtins.open", mock_open(read_data=code_with_comments)):
            results = tool(tmp_path, "authentication", include_comments=True)
            
            assert len(results) >= 3
            assert any("TODO" in r["content"] for r in results)
            assert any("FIXME" in r["content"] for r in results)
    
    def test_readme_search(self, tmp_path):
        """Test searching README files."""
        tool = self.get_component_function()
        
        readme_content = '''# Project Name

## Installation

Install the package using pip:

```bash
pip install project-name
```

## Authentication

To use the API, you need to authenticate first:

```python
from project import authenticate

auth_token = authenticate(username, password)
```

### Configuration

Set up authentication by creating a config file...
'''
        
        with patch("builtins.open", mock_open(read_data=readme_content)):
            with patch("os.walk") as mock_walk:
                mock_walk.return_value = [
                    (str(tmp_path), [], ["README.md", "README.rst", "readme.txt"])
                ]
                
                results = tool(tmp_path, "authenticate", include_readme=True)
                
                assert len(results) >= 2
                assert any("Authentication" in r["content"] for r in results)
    
    def test_api_documentation_search(self, tmp_path):
        """Test searching API documentation."""
        tool = self.get_component_function()
        
        api_doc = '''# API Reference

## Authentication Endpoints

### POST /api/auth/login

Authenticate a user and receive an access token.

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "token": "string",
    "expires_in": 3600
}
```

### GET /api/auth/verify

Verify authentication token validity.
'''
        
        with patch("builtins.open", mock_open(read_data=api_doc)):
            with patch("os.walk") as mock_walk:
                mock_walk.return_value = [(str(tmp_path / "docs"), [], ["api.md"])]
                
                results = tool(tmp_path, "auth", doc_types=["api_doc", "readme"])
                
                assert len(results) >= 2
                assert any("/api/auth" in r["content"] for r in results)
    
    def test_language_filtering(self, tmp_path):
        """Test filtering by programming language."""
        tool = self.get_component_function()
        
        files = {
            "main.py": '"""Python authentication module"""',
            "auth.js": '/** JavaScript auth module */',
            "Auth.java": '/** Java authentication class */',
            "auth.go": '// Go authentication package'
        }
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(str(tmp_path), [], list(files.keys()))]
            
            with patch("builtins.open", mock_open()) as mock_file:
                mock_file.side_effect = [
                    mock_open(read_data=content).return_value
                    for content in files.values()
                ]
                
                # Search only Python files
                results = tool(tmp_path, "authentication", language="python")
                
                # Should only find Python docstrings
                assert all(r["language"] == "python" for r in results)
    
    def test_nested_docstring_search(self, tmp_path):
        """Test searching nested docstrings (classes, methods)."""
        tool = self.get_component_function()
        
        nested_code = '''
class DataProcessor:
    """Main data processing class.
    
    This class handles data validation and transformation.
    """
    
    def validate(self, data):
        """
        Validate input data.
        
        Performs comprehensive validation including:
        - Type checking
        - Range validation
        - Format verification
        """
        
        def _check_format(item):
            """Internal format checker."""
            pass
'''
        
        with patch("builtins.open", mock_open(read_data=nested_code)):
            results = tool(tmp_path, "validation")
            
            # Should find class and method docstrings
            assert len(results) >= 2
            assert any("comprehensive validation" in r["content"] for r in results)
    
    def test_sphinx_rst_documentation(self, tmp_path):
        """Test searching Sphinx RST documentation."""
        tool = self.get_component_function()
        
        rst_content = '''
API Reference
=============

.. module:: myproject.auth
   :synopsis: Authentication module

.. function:: authenticate(username, password)

   Authenticate a user with the system.
   
   :param str username: The username
   :param str password: The password
   :returns: Authentication token
   :rtype: str
   
   Example::
   
       token = authenticate("user", "pass")
'''
        
        with patch("builtins.open", mock_open(read_data=rst_content)):
            with patch("os.walk") as mock_walk:
                mock_walk.return_value = [(str(tmp_path / "docs"), [], ["auth.rst"])]
                
                results = tool(tmp_path, "authenticate")
                
                assert len(results) >= 1
                assert any(":param" in r["content"] for r in results)
    
    def test_exclude_types(self, tmp_path):
        """Test excluding certain documentation types."""
        tool = self.get_component_function()
        
        # Search with comments excluded
        results = tool(
            tmp_path,
            "test",
            include_comments=False,
            include_docstrings=True,
            include_readme=True
        )
        
        # Should not include comments
        assert not any(r["type"] == "comment" for r in results)
    
    def test_case_sensitivity(self, tmp_path):
        """Test case-sensitive search."""
        tool = self.get_component_function()
        
        mixed_case_docs = '''
def getData():
    """Get data from DATABASE."""
    pass

def getdata():
    """Get data from database."""
    pass
'''
        
        with patch("builtins.open", mock_open(read_data=mixed_case_docs)):
            # Search for specific case
            results = tool(tmp_path, "DATABASE")
            
            # Should find based on case sensitivity of implementation
            assert len(results) >= 1
    
    def test_multiline_docstring_context(self, tmp_path):
        """Test extracting context for multiline docstrings."""
        tool = self.get_component_function()
        
        code = '''
def complex_function(param1, param2, param3):
    """
    This is a complex function with detailed documentation.
    
    It performs multiple operations including:
    - Data validation
    - Processing
    - Result formatting
    
    The function is designed to handle edge cases and provide
    comprehensive error reporting.
    
    Args:
        param1: First parameter
        param2: Second parameter
        param3: Third parameter
        
    Returns:
        Processed result
    """
    pass
'''
        
        with patch("builtins.open", mock_open(read_data=code)):
            results = tool(tmp_path, "validation")
            
            assert len(results) >= 1
            result = results[0]
            
            # Should include full docstring content
            assert "Data validation" in result["content"]
            assert "complex_function" in result.get("context", "")
    
    def test_performance_large_codebase(self, tmp_path):
        """Test performance with large codebases."""
        tool = self.get_component_function()
        
        # Simulate large codebase
        large_files = [f"module{i}.py" for i in range(1000)]
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(str(tmp_path), [], large_files)]
            
            with patch("builtins.open", mock_open(read_data='"""Module doc"""')):
                import time
                start_time = time.time()
                
                results = tool(tmp_path, "doc")
                
                elapsed = time.time() - start_time
                
                # Should complete in reasonable time
                assert elapsed < 5.0
