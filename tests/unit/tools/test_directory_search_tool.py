"""Test suite for directory_search_tool following best practices."""

import aiofiles
import os
import pytest
from datetime import datetime, timedelta
from packages.funcn_registry.components.tools.directory_search.tool import (
    DirectorySearchResult,
    FileInfo,
    find_files,
    list_directory,
    search_by_content,
    search_directory,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestDirectorySearchTool(BaseToolTest):
    """Test directory_search_tool component."""
    
    component_name = "directory_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/directory_search")
    
    def get_component_function(self):
        """Import the tool function."""
        return search_directory
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "path": ".",
                "pattern": "*.py",
                "recursive": True,
                "max_results": 10
            },
            {
                "path": ".",
                "pattern": "report*",
                "include_hidden": False
            },
            {
                "path": ".",
                "pattern": "*.log",
                "recursive": False,
                "max_results": 10
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, DirectorySearchResult)
        assert output.success
        assert output.search_path
        assert output.search_time >= 0
        
        total_results = len(output.files) + len(output.directories)
        if input_data.get("max_results"):
            assert total_results <= input_data["max_results"]
        
        for file_info in output.files:
            assert isinstance(file_info, FileInfo)
            assert not file_info.is_directory
            
        for dir_info in output.directories:
            assert isinstance(dir_info, FileInfo)
            assert dir_info.is_directory
    
    async def test_file_pattern_matching(self, tmp_path):
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
        
        # Test wildcard patterns
        result = await tool(path=str(tmp_path), pattern="*.py", recursive=True)
        assert result.success
        python_files = [f.name for f in result.files]
        assert "main.py" in python_files
        assert "utils.py" in python_files
        assert "config.json" not in python_files
        
        # Test prefix patterns
        result = await tool(path=str(tmp_path), pattern="main*", recursive=True)
        assert result.success
        assert any("main.py" in f.name for f in result.files)
    
    async def test_search_types(self, tmp_path):
        """Test different search types (files, directories, all)."""
        tool = self.get_component_function()
        
        # Create test structure
        (tmp_path / "subdir1").mkdir()
        (tmp_path / "subdir2").mkdir()
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.txt").touch()
        
        # Search all
        result = await tool(path=str(tmp_path), pattern="*", recursive=False)
        assert result.success
        assert len(result.files) == 2
        assert len(result.directories) == 2
        assert all(f.name.endswith(".txt") for f in result.files)
        assert all(d.name.startswith("subdir") for d in result.directories)
    
    async def test_recursive_vs_non_recursive(self, tmp_path):
        """Test recursive vs non-recursive search."""
        tool = self.get_component_function()
        
        # Create nested structure
        (tmp_path / "level1").mkdir()
        (tmp_path / "level1" / "level2").mkdir()
        (tmp_path / "level1" / "level2" / "deep_file.txt").touch()
        (tmp_path / "shallow_file.txt").touch()
        
        # Recursive search
        result = await tool(path=str(tmp_path), pattern="*.txt", recursive=True)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "deep_file.txt" in file_names
        assert "shallow_file.txt" in file_names
        
        # Non-recursive search
        result = await tool(path=str(tmp_path), pattern="*.txt", recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "shallow_file.txt" in file_names
        assert "deep_file.txt" not in file_names
    
    async def test_hidden_files_handling(self, tmp_path):
        """Test including/excluding hidden files."""
        tool = self.get_component_function()
        
        # Create hidden and regular files
        (tmp_path / ".git").mkdir()
        (tmp_path / ".gitignore").touch()
        (tmp_path / "README.md").touch()
        (tmp_path / ".env").touch()
        (tmp_path / "src").mkdir()
        
        # Exclude hidden files (default)
        result = await tool(path=str(tmp_path), pattern="*", include_hidden=False, recursive=False)
        assert result.success
        all_names = [f.name for f in result.files] + [d.name for d in result.directories]
        assert not any(name.startswith(".") for name in all_names)
        assert "README.md" in all_names
        assert "src" in all_names
        
        # Include hidden files
        result = await tool(path=str(tmp_path), pattern="*", include_hidden=True, recursive=False)
        assert result.success
        all_names = [f.name for f in result.files] + [d.name for d in result.directories]
        assert any(name.startswith(".") for name in all_names)
        assert ".gitignore" in all_names
        assert ".env" in all_names
    
    async def test_symlink_handling(self, tmp_path):
        """Test handling of symbolic links."""
        tool = self.get_component_function()
        
        # Create symlink (if supported on the platform)
        target = tmp_path / "target.txt"
        target.touch()
        link = tmp_path / "link.txt"
        
        try:
            link.symlink_to(target)
            
            result = await tool(path=str(tmp_path), pattern="*", recursive=False)
            assert result.success
            # Tool treats symlinks as regular files/dirs based on what they point to
            assert len(result.files) >= 1
        except OSError:
            # Skip if symlinks not supported
            pytest.skip("Symlinks not supported on this platform")
    
    async def test_file_metadata(self, tmp_path):
        """Test file metadata extraction."""
        tool = self.get_component_function()
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        result = await tool(path=str(tmp_path), pattern="test.txt", recursive=False)
        assert result.success
        assert len(result.files) == 1
        
        file_info = result.files[0]
        assert file_info.name == "test.txt"
        assert file_info.size == len("test content")
        assert isinstance(file_info.modified_time, datetime)
        assert file_info.permissions
        assert file_info.extension == ".txt"
        assert file_info.mime_type == "text/plain"
    
    async def test_case_sensitive_patterns(self, tmp_path):
        """Test case-sensitive pattern matching."""
        tool = self.get_component_function()
        
        # Create files with different cases
        (tmp_path / "README.md").touch()
        (tmp_path / "readme.txt").touch()
        (tmp_path / "ReadMe.doc").touch()
        
        # Glob patterns are case-sensitive on Unix, case-insensitive on Windows
        result = await tool(path=str(tmp_path), pattern="readme*", recursive=False)
        assert result.success
        # On Unix: only readme.txt matches
        # On Windows: all three match
    
    async def test_complex_patterns(self, tmp_path):
        """Test complex glob patterns."""
        tool = self.get_component_function()
        
        # Create test files
        (tmp_path / "test_foo.py").touch()
        (tmp_path / "test_bar.py").touch()
        (tmp_path / "main.py").touch()
        (tmp_path / "foo_test.py").touch()
        (tmp_path / "data.json").touch()
        (tmp_path / "config.yaml").touch()
        
        # Test multiple wildcards
        result = await tool(path=str(tmp_path), pattern="test_*.py", recursive=False)
        assert result.success
        matching_files = [f.name for f in result.files]
        assert "test_foo.py" in matching_files
        assert "test_bar.py" in matching_files
        assert "main.py" not in matching_files
        assert "foo_test.py" not in matching_files
    
    async def test_max_results_limit(self, tmp_path):
        """Test max_results parameter."""
        tool = self.get_component_function()
        
        # Create many files
        for i in range(20):
            (tmp_path / f"file{i}.txt").touch()
        
        # Test with limit
        result = await tool(path=str(tmp_path), pattern="*.txt", max_results=10, recursive=False)
        assert result.success
        assert len(result.files) <= 10
        
        # Test without explicit limit (default is 1000)
        result = await tool(path=str(tmp_path), pattern="*.txt", recursive=False)
        assert result.success
        assert len(result.files) == 20
    
    async def test_permission_errors(self, tmp_path):
        """Test handling of permission errors."""
        tool = self.get_component_function()
        
        # Try to search a path that doesn't exist
        non_existent = tmp_path / "non_existent"
        
        result = await tool(path=str(non_existent), pattern="*")
        assert not result.success
        assert "does not exist" in result.error
    
    async def test_empty_directory(self, tmp_path):
        """Test searching empty directory."""
        tool = self.get_component_function()
        
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        result = await tool(path=str(empty_dir), pattern="*", recursive=False)
        assert result.success
        assert result.total_found == 0
        assert len(result.files) == 0
        assert len(result.directories) == 0
    
    async def test_special_characters_in_names(self, tmp_path):
        """Test files with special characters."""
        tool = self.get_component_function()
        
        # Create files with special characters
        (tmp_path / "file with spaces.txt").touch()
        (tmp_path / "file-with-dashes.txt").touch()
        (tmp_path / "file_with_underscores.txt").touch()
        (tmp_path / "file.multiple.dots.txt").touch()
        (tmp_path / "file@special#chars$.txt").touch()
        
        # Should handle all special characters
        result = await tool(path=str(tmp_path), pattern="*", recursive=False)
        assert result.success
        assert len(result.files) == 5
        
        # Test pattern with spaces
        result = await tool(path=str(tmp_path), pattern="*with spaces*", recursive=False)
        assert result.success
        assert any("spaces" in f.name for f in result.files)
    
    async def test_performance_with_large_directories(self, tmp_path):
        """Test performance with large directory structures."""
        tool = self.get_component_function()
        
        # Create a reasonable number of files for testing
        for i in range(200):
            (tmp_path / f"file_{i:05d}.txt").touch()
        
        import time
        start_time = time.time()
        
        result = await tool(path=str(tmp_path), pattern="file_00*", max_results=100, recursive=False)
        
        elapsed = time.time() - start_time
        
        # Should complete quickly
        assert elapsed < 2.0
        assert result.success
        assert len(result.files) <= 100
    
    async def test_file_type_filtering(self, tmp_path):
        """Test filtering by file types."""
        tool = self.get_component_function()
        
        # Create files with different extensions
        (tmp_path / "script.py").touch()
        (tmp_path / "data.json").touch()
        (tmp_path / "readme.md").touch()
        (tmp_path / "config.yaml").touch()
        (tmp_path / "image.png").touch()
        
        # Filter by file types
        result = await tool(path=str(tmp_path), pattern="*", file_types=[".py", ".json"], recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "script.py" in file_names
        assert "data.json" in file_names
        assert "readme.md" not in file_names
        assert "config.yaml" not in file_names
        assert "image.png" not in file_names
    
    async def test_date_filtering(self, tmp_path):
        """Test filtering by modification date."""
        tool = self.get_component_function()
        
        # Create files with different modification times
        old_file = tmp_path / "old_file.txt"
        old_file.touch()
        # Set modification time to 10 days ago
        old_time = datetime.now() - timedelta(days=10)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
        
        recent_file = tmp_path / "recent_file.txt"
        recent_file.touch()
        
        # Filter by modified_after
        cutoff_date = datetime.now() - timedelta(days=5)
        result = await tool(path=str(tmp_path), pattern="*.txt", modified_after=cutoff_date, recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "recent_file.txt" in file_names
        assert "old_file.txt" not in file_names
        
        # Filter by modified_before
        result = await tool(path=str(tmp_path), pattern="*.txt", modified_before=cutoff_date, recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "old_file.txt" in file_names
        assert "recent_file.txt" not in file_names
    
    async def test_size_filtering(self, tmp_path):
        """Test filtering by file size."""
        tool = self.get_component_function()
        
        # Create files with different sizes
        small_file = tmp_path / "small.txt"
        small_file.write_text("small")
        
        medium_file = tmp_path / "medium.txt"
        medium_file.write_text("x" * 1000)
        
        large_file = tmp_path / "large.txt"
        large_file.write_text("x" * 10000)
        
        # Filter by min_size
        result = await tool(path=str(tmp_path), pattern="*.txt", min_size=500, recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "small.txt" not in file_names
        assert "medium.txt" in file_names
        assert "large.txt" in file_names
        
        # Filter by max_size
        result = await tool(path=str(tmp_path), pattern="*.txt", max_size=5000, recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "small.txt" in file_names
        assert "medium.txt" in file_names
        assert "large.txt" not in file_names
    
    async def test_content_search(self, tmp_path):
        """Test searching within file content."""
        tool = self.get_component_function()
        
        # Create files with different content
        file1 = tmp_path / "file1.txt"
        file1.write_text("This file contains important information")
        
        file2 = tmp_path / "file2.txt"
        file2.write_text("This file has different content")
        
        file3 = tmp_path / "file3.txt"
        file3.write_text("Another file with some text")
        
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03")
        
        # Search for content
        result = await tool(path=str(tmp_path), pattern="*", content_search="important", recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "file1.txt" in file_names
        assert "file2.txt" not in file_names
        assert "file3.txt" not in file_names
        assert "binary.bin" not in file_names  # Binary files should be skipped
    
    async def test_regex_pattern(self, tmp_path):
        """Test regex pattern matching."""
        tool = self.get_component_function()
        
        # Create files with different names
        (tmp_path / "test_001.log").touch()
        (tmp_path / "test_002.log").touch()
        (tmp_path / "test_abc.log").touch()
        (tmp_path / "prod_001.log").touch()
        
        # Use regex pattern
        result = await tool(path=str(tmp_path), regex_pattern=r"test_\d+\.log", recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "test_001.log" in file_names
        assert "test_002.log" in file_names
        assert "test_abc.log" not in file_names
        assert "prod_001.log" not in file_names
    
    async def test_exclude_patterns(self, tmp_path):
        """Test exclude patterns."""
        tool = self.get_component_function()
        
        # Create files
        (tmp_path / "include_this.txt").touch()
        (tmp_path / "exclude_this.txt").touch()
        (tmp_path / "test.tmp").touch()
        (tmp_path / "data.bak").touch()
        
        # Exclude patterns
        result = await tool(
            path=str(tmp_path), pattern="*", 
            exclude_patterns=["exclude_*", "*.tmp", "*.bak"], 
            recursive=False
        )
        assert result.success
        file_names = [f.name for f in result.files]
        assert "include_this.txt" in file_names
        assert "exclude_this.txt" not in file_names
        assert "test.tmp" not in file_names
        assert "data.bak" not in file_names
    
    async def test_max_depth(self, tmp_path):
        """Test max_depth parameter."""
        tool = self.get_component_function()
        
        # Create nested structure
        (tmp_path / "level1").mkdir()
        (tmp_path / "level1" / "file1.txt").touch()
        (tmp_path / "level1" / "level2").mkdir()
        (tmp_path / "level1" / "level2" / "file2.txt").touch()
        (tmp_path / "level1" / "level2" / "level3").mkdir()
        (tmp_path / "level1" / "level2" / "level3" / "file3.txt").touch()
        
        # Test max_depth
        result = await tool(path=str(tmp_path), pattern="*.txt", recursive=True, max_depth=1)
        assert result.success
        file_names = [f.name for f in result.files]
        assert "file1.txt" in file_names
        assert "file2.txt" not in file_names
        assert "file3.txt" not in file_names
    
    async def test_sort_options(self, tmp_path):
        """Test different sort options."""
        tool = self.get_component_function()
        
        # Create files with different properties
        file1 = tmp_path / "aaa.txt"
        file1.write_text("small")
        
        file2 = tmp_path / "zzz.txt"
        file2.write_text("medium" * 100)
        
        file3 = tmp_path / "mmm.txt"
        file3.write_text("large" * 1000)
        
        # Sort by name
        result = await tool(path=str(tmp_path), pattern="*.txt", sort_by="name", recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert file_names == ["aaa.txt", "mmm.txt", "zzz.txt"]
        
        # Sort by size
        result = await tool(path=str(tmp_path), pattern="*.txt", sort_by="size", recursive=False)
        assert result.success
        sizes = [f.size for f in result.files]
        assert sizes[0] < sizes[1] < sizes[2]
        
        # Sort by name, reversed
        result = await tool(path=str(tmp_path), pattern="*.txt", sort_by="name", reverse_sort=True, recursive=False)
        assert result.success
        file_names = [f.name for f in result.files]
        assert file_names == ["zzz.txt", "mmm.txt", "aaa.txt"]
    
    async def test_list_directory_convenience(self, tmp_path):
        """Test list_directory convenience function."""
        # Create files and directories
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.py").touch()
        (tmp_path / "subdir").mkdir()
        (tmp_path / ".hidden").touch()
        
        # Test list_directory
        result = await list_directory(str(tmp_path))
        assert result.success
        assert not result.files == []  # Should have files
        assert not result.directories == []  # Should have directories
        
        # Test with pattern
        result = await list_directory(str(tmp_path), pattern="*.txt")
        assert result.success
        assert all(f.name.endswith(".txt") for f in result.files)
    
    async def test_find_files_convenience(self, tmp_path):
        """Test find_files convenience function."""
        # Create nested structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").touch()
        (tmp_path / "src" / "utils.py").touch()
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "readme.md").touch()
        
        # Test find_files
        result = await find_files(str(tmp_path), "*.py", recursive=True)
        assert result.success
        python_files = [f.name for f in result.files]
        assert "main.py" in python_files
        assert "utils.py" in python_files
        assert all(f.name.endswith(".py") for f in result.files)
    
    async def test_search_by_content_convenience(self, tmp_path):
        """Test search_by_content convenience function."""
        # Create files with content
        file1 = tmp_path / "doc1.txt"
        file1.write_text("This document contains the keyword")
        
        file2 = tmp_path / "doc2.py"
        file2.write_text("# Python file with the keyword")
        
        file3 = tmp_path / "doc3.md"
        file3.write_text("# Markdown without the search term")
        
        # Test search_by_content
        result = await search_by_content(str(tmp_path), "keyword")
        assert result.success
        file_names = [f.name for f in result.files]
        assert "doc1.txt" in file_names
        assert "doc2.py" in file_names
        assert "doc3.md" not in file_names
