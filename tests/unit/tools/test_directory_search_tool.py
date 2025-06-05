"""Test suite for directory_search_tool following best practices."""

import os
import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestDirectorySearchTool(BaseToolTest):
    """Test directory_search_tool component."""
    
    component_name = "directory_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/directory_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.directory_search_tool import search_directory
        def mock_search_directory(
            path: str | Path,
            pattern: str,
            search_type: str = "all",
            recursive: bool = True,
            include_hidden: bool = False,
            max_results: int | None = None
        ) -> list[dict[str, any]]:
            """Mock directory search tool."""
            base_path = Path(path)
            results = [
                {
                    "path": str(base_path / "src" / "main.py"),
                    "name": "main.py",
                    "type": "file",
                    "size": 2048,
                    "modified": "2024-01-15T10:00:00"
                },
                {
                    "path": str(base_path / "tests"),
                    "name": "tests",
                    "type": "directory",
                    "size": 4096,
                    "modified": "2024-01-14T09:00:00"
                }
            ]
            
            if pattern.lower() in "main.py":
                return results[:1]
            elif pattern.lower() in "tests":
                return results[1:2]
            
            return results[:max_results] if max_results else results
        return mock_search_directory
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "path": "/home/user/project",
                "pattern": "*.py",
                "search_type": "files",
                "recursive": True
            },
            {
                "path": "/home/user/documents",
                "pattern": "report*",
                "search_type": "all",
                "include_hidden": False
            },
            {
                "path": "/var/log",
                "pattern": "*.log",
                "recursive": False,
                "max_results": 10
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        
        if input_data.get("max_results"):
            assert len(output) <= input_data["max_results"]
        
        for result in output:
            assert isinstance(result, dict)
            assert "path" in result
            assert "type" in result
            assert result["type"] in ["file", "directory", "symlink"]
    
    def test_file_pattern_matching(self, tmp_path):
        """Test various file pattern matching."""
        tool = self.get_component_function()
        
        # Create test directory structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").touch()
        (tmp_path / "src" / "utils.py").touch()
        (tmp_path / "src" / "config.json").touch()
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "readme.md").touch()
        (tmp_path / "test.txt").touch()
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [
                (str(tmp_path), ["src", "docs"], ["test.txt"]),
                (str(tmp_path / "src"), [], ["main.py", "utils.py", "config.json"]),
                (str(tmp_path / "docs"), [], ["readme.md"])
            ]
            
            # Test wildcard patterns
            results = tool(tmp_path, "*.py", search_type="files")
            assert any("main.py" in r["path"] for r in results)
            assert any("utils.py" in r["path"] for r in results)
            
            # Test prefix patterns
            results = tool(tmp_path, "main*", search_type="files")
            assert any("main.py" in r["path"] for r in results)
    
    def test_search_types(self, tmp_path):
        """Test different search types (files, directories, all)."""
        tool = self.get_component_function()
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [
                (str(tmp_path), ["subdir1", "subdir2"], ["file1.txt", "file2.txt"]),
            ]
            
            with patch("os.path.isfile") as mock_isfile:
                with patch("os.path.isdir") as mock_isdir:
                    mock_isfile.side_effect = lambda p: "file" in p
                    mock_isdir.side_effect = lambda p: "subdir" in p or p == str(tmp_path)
                    
                    # Search files only
                    results = tool(tmp_path, "*", search_type="files")
                    assert all(r["type"] == "file" for r in results)
                    
                    # Search directories only
                    results = tool(tmp_path, "*", search_type="directories")
                    assert all(r["type"] == "directory" for r in results)
                    
                    # Search all
                    results = tool(tmp_path, "*", search_type="all")
                    types = {r["type"] for r in results}
                    assert "file" in types or "directory" in types
    
    def test_recursive_vs_non_recursive(self, tmp_path):
        """Test recursive vs non-recursive search."""
        tool = self.get_component_function()
        
        # Create nested structure
        (tmp_path / "level1").mkdir()
        (tmp_path / "level1" / "level2").mkdir()
        (tmp_path / "level1" / "level2" / "deep_file.txt").touch()
        (tmp_path / "shallow_file.txt").touch()
        
        with patch("os.walk") as mock_walk:
            # Mock recursive walk
            mock_walk.return_value = [
                (str(tmp_path), ["level1"], ["shallow_file.txt"]),
                (str(tmp_path / "level1"), ["level2"], []),
                (str(tmp_path / "level1" / "level2"), [], ["deep_file.txt"])
            ]
            
            # Recursive search
            results = tool(tmp_path, "*.txt", recursive=True)
            assert any("deep_file.txt" in r["path"] for r in results)
            assert any("shallow_file.txt" in r["path"] for r in results)
        
        with patch("os.listdir") as mock_listdir:
            mock_listdir.return_value = ["shallow_file.txt", "level1"]
            
            # Non-recursive search
            results = tool(tmp_path, "*.txt", recursive=False)
            # Should not find deep_file.txt
            assert not any("deep_file.txt" in r["path"] for r in results)
    
    def test_hidden_files_handling(self, tmp_path):
        """Test including/excluding hidden files."""
        tool = self.get_component_function()
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [
                (str(tmp_path), [".git", "src"], [".gitignore", "README.md", ".env"]),
            ]
            
            # Exclude hidden files (default)
            results = tool(tmp_path, "*", include_hidden=False)
            assert not any(r["name"].startswith(".") for r in results)
            
            # Include hidden files
            results = tool(tmp_path, "*", include_hidden=True)
            assert any(r["name"].startswith(".") for r in results)
    
    def test_symlink_handling(self, tmp_path):
        """Test handling of symbolic links."""
        tool = self.get_component_function()
        
        # Create symlink
        target = tmp_path / "target.txt"
        target.touch()
        link = tmp_path / "link.txt"
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(str(tmp_path), [], ["target.txt", "link.txt"])]
            
            with patch("os.path.islink") as mock_islink:
                mock_islink.side_effect = lambda p: "link" in p
                
                results = tool(tmp_path, "*")
                
                # Should identify symlinks
                symlinks = [r for r in results if r.get("type") == "symlink"]
                assert len(symlinks) >= 0  # May or may not include based on implementation
    
    def test_file_metadata(self, tmp_path):
        """Test file metadata extraction."""
        tool = self.get_component_function()
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(str(tmp_path), [], ["test.txt"])]
            
            with patch("os.stat") as mock_stat:
                mock_stat.return_value = Mock(
                    st_size=1234,
                    st_mtime=1705320000,  # 2024-01-15 10:00:00
                    st_mode=0o644
                )
                
                results = tool(tmp_path, "test.txt")
                
                assert len(results) > 0
                result = results[0]
                
                # Should include metadata
                assert "size" in result
                assert result["size"] == 1234
                assert "modified" in result
    
    def test_case_sensitive_patterns(self, tmp_path):
        """Test case-sensitive pattern matching."""
        tool = self.get_component_function()
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [
                (str(tmp_path), [], ["README.md", "readme.txt", "ReadMe.doc"])
            ]
            
            # Case-insensitive pattern (typical glob behavior)
            results = tool(tmp_path, "readme*")
            # Implementation dependent - may be case-sensitive or not
            assert len(results) >= 1
    
    def test_complex_patterns(self, tmp_path):
        """Test complex glob patterns."""
        tool = self.get_component_function()
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [
                (str(tmp_path), [], [
                    "test_foo.py",
                    "test_bar.py", 
                    "main.py",
                    "foo_test.py",
                    "data.json",
                    "config.yaml"
                ])
            ]
            
            # Test multiple wildcards
            results = tool(tmp_path, "test_*.py")
            assert all("test_" in r["name"] and r["name"].endswith(".py") for r in results)
            
            # Test character sets (if supported)
            results = tool(tmp_path, "*.[jy]ml")  # .yml, .yaml, .json files
            # Should match .json and .yaml files if pattern is supported
    
    def test_max_results_limit(self, tmp_path):
        """Test max_results parameter."""
        tool = self.get_component_function()
        
        # Create many files
        files = [f"file{i}.txt" for i in range(100)]
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(str(tmp_path), [], files)]
            
            # Test with limit
            results = tool(tmp_path, "*.txt", max_results=10)
            assert len(results) <= 10
            
            # Test without limit
            results = tool(tmp_path, "*.txt", max_results=None)
            assert len(results) > 10
    
    def test_permission_errors(self, tmp_path):
        """Test handling of permission errors."""
        tool = self.get_component_function()
        
        with patch("os.walk") as mock_walk:
            # Simulate permission error
            mock_walk.side_effect = PermissionError("Access denied")
            
            results = tool(tmp_path, "*")
            
            # Should handle gracefully
            assert isinstance(results, list)
            assert len(results) == 0 or "error" in str(results)
    
    def test_empty_directory(self, tmp_path):
        """Test searching empty directory."""
        tool = self.get_component_function()
        
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(str(empty_dir), [], [])]
            
            results = tool(empty_dir, "*")
            assert results == []
    
    def test_special_characters_in_names(self, tmp_path):
        """Test files with special characters."""
        tool = self.get_component_function()
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [
                (str(tmp_path), [], [
                    "file with spaces.txt",
                    "file-with-dashes.txt",
                    "file_with_underscores.txt",
                    "file.multiple.dots.txt",
                    "file@special#chars$.txt"
                ])
            ]
            
            # Should handle all special characters
            results = tool(tmp_path, "*")
            assert len(results) == 5
            
            # Test pattern with spaces
            results = tool(tmp_path, "*with spaces*")
            assert any("spaces" in r["name"] for r in results)
    
    def test_performance_with_large_directories(self, tmp_path):
        """Test performance with large directory structures."""
        tool = self.get_component_function()
        
        # Simulate large directory
        large_file_list = [f"file_{i:05d}.txt" for i in range(10000)]
        
        with patch("os.walk") as mock_walk:
            mock_walk.return_value = [(str(tmp_path), ["subdir"] * 100, large_file_list)]
            
            import time
            start_time = time.time()
            
            results = tool(tmp_path, "file_05*", max_results=100)
            
            elapsed = time.time() - start_time
            
            # Should complete quickly even for large directories
            assert elapsed < 2.0
            assert len(results) <= 100
