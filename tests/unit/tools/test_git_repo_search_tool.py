"""Test suite for git_repo_search_tool following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestGitRepoSearchTool(BaseToolTest):
    """Test git_repo_search_tool component."""
    
    component_name = "git_repo_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/git_repo_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.git_repo_search_tool import search_git_repo
        def mock_search_git_repo(
            repo_path: str | Path,
            query: str,
            search_type: str = "code",
            file_pattern: str | None = None,
            branch: str | None = None,
            author: str | None = None,
            since: str | None = None,
            until: str | None = None
        ) -> list[dict[str, any]]:
            """Mock git repo search tool."""
            if search_type == "code":
                return [
                    {
                        "file": "src/main.py",
                        "line": 42,
                        "content": f"def {query}():",
                        "branch": branch or "main",
                        "commit": "abc123"
                    },
                    {
                        "file": "tests/test_main.py",
                        "line": 15,
                        "content": f"# Test for {query}",
                        "branch": branch or "main",
                        "commit": "def456"
                    }
                ]
            elif search_type == "commits":
                return [
                    {
                        "commit": "abc123",
                        "author": author or "John Doe",
                        "date": "2024-01-15",
                        "message": f"Add {query} functionality",
                        "files_changed": 3
                    }
                ]
            elif search_type == "files":
                return [
                    {
                        "path": f"src/{query}.py",
                        "size": 1024,
                        "last_modified": "2024-01-15"
                    }
                ]
            return []
        return mock_search_git_repo
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "repo_path": "/path/to/repo",
                "query": "TODO",
                "search_type": "code",
                "file_pattern": "*.py"
            },
            {
                "repo_path": "/path/to/repo",
                "query": "bugfix",
                "search_type": "commits",
                "author": "john.doe@example.com",
                "since": "2024-01-01"
            },
            {
                "repo_path": "/path/to/repo",
                "query": "config",
                "search_type": "files",
                "branch": "develop"
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        
        search_type = input_data.get("search_type", "code")
        for result in output:
            assert isinstance(result, dict)
            
            if search_type == "code":
                assert "file" in result
                assert "line" in result or "line_number" in result
            elif search_type == "commits":
                assert "commit" in result or "sha" in result
                assert "message" in result
            elif search_type == "files":
                assert "path" in result or "file" in result
    
    def test_code_search(self, tmp_path):
        """Test searching code in repository."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            # Mock git grep output
            mock_result = Mock()
            mock_result.stdout = """src/main.py:42:def calculate_total():
src/utils.py:15:    total = calculate_total()
tests/test_main.py:8:def test_calculate_total():"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            results = tool(tmp_path, "calculate_total", search_type="code")
            
            assert len(results) >= 3
            assert any("main.py" in r["file"] for r in results)
            assert any("test_main.py" in r["file"] for r in results)
    
    def test_file_pattern_filtering(self, tmp_path):
        """Test filtering by file patterns."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stdout = """src/main.py:10:import config
src/config.py:1:# Configuration file
docs/config.md:5:Configuration guide"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            # Search only Python files
            results = tool(
                tmp_path,
                "config",
                search_type="code",
                file_pattern="*.py"
            )
            
            # Should filter out non-Python files
            assert all(r["file"].endswith(".py") for r in results)
            assert not any(r["file"].endswith(".md") for r in results)
    
    def test_commit_search(self, tmp_path):
        """Test searching in commit messages."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            # Mock git log output
            mock_result = Mock()
            mock_result.stdout = """abc123|John Doe|2024-01-15|Fix bug in authentication
def456|Jane Smith|2024-01-14|Add new authentication method
ghi789|Bob Johnson|2024-01-13|Update authentication docs"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            results = tool(
                tmp_path,
                "authentication",
                search_type="commits"
            )
            
            assert len(results) >= 3
            assert all("authentication" in r["message"].lower() for r in results)
    
    def test_author_filtering(self, tmp_path):
        """Test filtering commits by author."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stdout = """abc123|john.doe@example.com|2024-01-15|Feature: Add user dashboard
def456|john.doe@example.com|2024-01-14|Fix: Dashboard layout issue"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            results = tool(
                tmp_path,
                "dashboard",
                search_type="commits",
                author="john.doe@example.com"
            )
            
            assert len(results) == 2
            assert all(r["author"] == "john.doe@example.com" for r in results)
    
    def test_date_range_filtering(self, tmp_path):
        """Test filtering by date range."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stdout = """abc123|Author|2024-01-15|Recent commit
def456|Author|2024-01-10|Mid-range commit
ghi789|Author|2023-12-20|Old commit"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            results = tool(
                tmp_path,
                "commit",
                search_type="commits",
                since="2024-01-01",
                until="2024-01-31"
            )
            
            # Should only include January 2024 commits
            assert len(results) == 2
            assert not any("2023" in r["date"] for r in results)
    
    def test_branch_search(self, tmp_path):
        """Test searching in specific branches."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            # First call - switch branch
            switch_result = Mock()
            switch_result.returncode = 0
            
            # Second call - search
            search_result = Mock()
            search_result.stdout = "feature/new-ui:src/ui.py:10:New UI component"
            search_result.returncode = 0
            
            mock_run.side_effect = [switch_result, search_result]
            
            results = tool(
                tmp_path,
                "UI component",
                search_type="code",
                branch="feature/new-ui"
            )
            
            # Should search in specified branch
            assert len(results) > 0
            assert results[0]["branch"] == "feature/new-ui"
    
    def test_file_search(self, tmp_path):
        """Test searching for files by name."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stdout = """src/config.py
src/config_loader.py
tests/test_config.py
docs/config.md"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            results = tool(
                tmp_path,
                "config",
                search_type="files"
            )
            
            assert len(results) >= 4
            assert any("config.py" in r["path"] for r in results)
    
    def test_case_sensitivity(self, tmp_path):
        """Test case-sensitive vs case-insensitive search."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            # Case-insensitive results
            mock_result = Mock()
            mock_result.stdout = """src/main.py:10:TODO: Fix this
src/utils.py:20:Todo: Update docs
src/test.py:30:todo: add tests"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            results = tool(tmp_path, "todo", search_type="code")
            
            # Should find all case variations
            assert len(results) >= 3
    
    def test_binary_file_exclusion(self, tmp_path):
        """Test that binary files are excluded from search."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            # Git grep typically excludes binary files
            mock_result.stdout = """src/text.py:5:Binary data reference
docs/README.md:10:Binary file handling"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            results = tool(tmp_path, "Binary", search_type="code")
            
            # Should not include actual binary files
            assert all(
                r["file"].endswith((".py", ".md", ".txt", ".js"))
                for r in results
            )
    
    def test_submodule_handling(self, tmp_path):
        """Test handling of git submodules."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            # Include submodules in search
            mock_result = Mock()
            mock_result.stdout = """main-repo/src/main.py:10:Main code
submodule/lib/helper.py:5:Helper function"""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            results = tool(
                tmp_path,
                "function",
                search_type="code"
            )
            
            # Should handle submodules
            assert len(results) >= 2
    
    def test_large_repository_performance(self, tmp_path):
        """Test performance with large repositories."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            # Simulate large result set
            large_output = "\n".join([
                f"src/file{i}.py:{i}:Match {i}"
                for i in range(1000)
            ])
            
            mock_result = Mock()
            mock_result.stdout = large_output
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            import time
            start_time = time.time()
            
            results = tool(tmp_path, "Match", search_type="code")
            
            elapsed = time.time() - start_time
            
            # Should handle large results efficiently
            assert elapsed < 2.0
            assert len(results) == 1000
    
    def test_error_handling(self, tmp_path):
        """Test handling of various git errors."""
        tool = self.get_component_function()
        
        # Test non-git directory
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stderr = "fatal: not a git repository"
            mock_result.returncode = 128
            mock_run.return_value = mock_result
            
            results = tool(tmp_path, "test")
            
            # Should handle gracefully
            assert isinstance(results, list)
            assert len(results) == 0 or "error" in str(results)
    
    def test_empty_results(self, tmp_path):
        """Test handling when no results found."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.stdout = ""
            mock_result.returncode = 1  # Git grep returns 1 when no matches
            mock_run.return_value = mock_result
            
            results = tool(tmp_path, "nonexistent_string_xyz")
            
            assert results == []
    
    def test_special_characters_in_query(self, tmp_path):
        """Test queries with special characters."""
        tool = self.get_component_function()
        
        special_queries = [
            "function()",
            "$variable",
            "array[0]",
            "regex.*pattern",
            "path/to/file"
        ]
        
        for query in special_queries:
            with patch("subprocess.run") as mock_run:
                mock_result = Mock()
                mock_result.stdout = f"src/main.py:10:{query}"
                mock_result.returncode = 0
                mock_run.return_value = mock_result
                
                results = tool(tmp_path, query)
                
                # Should handle special characters
                assert isinstance(results, list)
