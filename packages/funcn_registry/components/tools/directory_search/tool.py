"""Directory Search Tool for file system navigation and search."""

import aiofiles
import asyncio
import fnmatch
import glob
import mimetypes
import os
import re
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Optional, Union


class FileInfo(BaseModel):
    """Information about a file or directory."""

    path: str = Field(..., description="Full path to the file or directory")
    name: str = Field(..., description="Name of the file or directory")
    is_directory: bool = Field(..., description="Whether this is a directory")
    size: int = Field(..., description="Size in bytes")
    modified_time: datetime = Field(..., description="Last modification time")
    created_time: datetime | None = Field(None, description="Creation time")
    permissions: str = Field(..., description="File permissions in octal format")
    mime_type: str | None = Field(None, description="MIME type for files")
    extension: str | None = Field(None, description="File extension")

    @classmethod
    def from_path(cls, path: str | Path) -> "FileInfo":
        """Create FileInfo from a file path."""
        path = Path(path)
        stat = path.stat()

        # Get MIME type for files
        mime_type = None
        extension = None
        if path.is_file():
            mime_type, _ = mimetypes.guess_type(str(path))
            extension = path.suffix.lower() if path.suffix else None

        return cls(
            path=str(path.absolute()),
            name=path.name,
            is_directory=path.is_dir(),
            size=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            created_time=datetime.fromtimestamp(stat.st_ctime) if hasattr(stat, 'st_ctime') else None,
            permissions=oct(stat.st_mode)[-3:],
            mime_type=mime_type,
            extension=extension,
        )


class DirectorySearchResult(BaseModel):
    """Result of directory search operation."""

    success: bool = Field(..., description="Whether the search was successful")
    search_path: str = Field(..., description="Path that was searched")
    total_found: int = Field(..., description="Total number of items found")
    files: list[FileInfo] = Field(default_factory=list, description="List of files found")
    directories: list[FileInfo] = Field(default_factory=list, description="List of directories found")
    error: str | None = Field(None, description="Error message if search failed")
    search_time: float = Field(..., description="Time taken to search in seconds")
    applied_filters: dict[str, Any] = Field(default_factory=dict, description="Filters that were applied")


async def search_directory(
    path: str = ".",
    pattern: str | None = None,
    regex_pattern: str | None = None,
    recursive: bool = False,
    max_depth: int | None = None,
    include_hidden: bool = False,
    file_types: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
    modified_after: datetime | None = None,
    modified_before: datetime | None = None,
    content_search: str | None = None,
    max_results: int = 1000,
    sort_by: str = "name",
    reverse_sort: bool = False,
) -> DirectorySearchResult:
    """Search and navigate the file system with advanced filtering.

    Args:
        path: Directory path to search in
        pattern: File name pattern (supports glob patterns)
        regex_pattern: Regular expression pattern for file names
        recursive: Whether to search recursively
        max_depth: Maximum recursion depth
        include_hidden: Whether to include hidden files/directories
        file_types: List of file extensions to include (e.g., ['.py', '.txt'])
        exclude_patterns: Patterns to exclude from results
        min_size: Minimum file size in bytes
        max_size: Maximum file size in bytes
        modified_after: Only files modified after this date
        modified_before: Only files modified before this date
        content_search: Search for this text within files
        max_results: Maximum number of results to return
        sort_by: Sort results by: name, size, modified, created
        reverse_sort: Reverse the sort order

    Returns:
        DirectorySearchResult with files and directories found
    """
    start_time = asyncio.get_event_loop().time()

    try:
        base_path = Path(path)
        if not base_path.exists():
            raise ValueError(f"Path does not exist: {path}")

        base_path = base_path.absolute()

        # Perform the search
        files, directories = await _search_directory_recursive(
            base_path=base_path,
            pattern=pattern,
            regex_pattern=regex_pattern,
            recursive=recursive,
            max_depth=max_depth,
            include_hidden=include_hidden,
            file_types=file_types,
            exclude_patterns=exclude_patterns,
            min_size=min_size,
            max_size=max_size,
            modified_after=modified_after,
            modified_before=modified_before,
            content_search=content_search,
            max_results=max_results,
            current_depth=0,
        )

        # Sort results
        files = _sort_results(files, sort_by, reverse_sort)
        directories = _sort_results(directories, sort_by, reverse_sort)

        # Limit results
        files = files[:max_results]
        directories = directories[: max(0, max_results - len(files))]

        search_time = asyncio.get_event_loop().time() - start_time

        return DirectorySearchResult(
            success=True,
            search_path=str(base_path),
            total_found=len(files) + len(directories),
            files=files,
            directories=directories,
            error=None,
            search_time=search_time,
            applied_filters={
                "pattern": pattern,
                "regex": regex_pattern,
                "recursive": recursive,
                "file_types": file_types,
                "content_search": content_search,
                "size_range": (min_size, max_size),
                "date_range": (modified_after, modified_before),
            },
        )

    except Exception as e:
        search_time = asyncio.get_event_loop().time() - start_time
        return DirectorySearchResult(
            success=False,
            search_path=path,
            total_found=0,
            files=[],
            directories=[],
            error=str(e),
            search_time=search_time,
            applied_filters={},
        )


async def _search_directory_recursive(
    base_path: Path,
    pattern: str | None,
    regex_pattern: str | None,
    recursive: bool,
    max_depth: int | None,
    include_hidden: bool,
    file_types: list[str] | None,
    exclude_patterns: list[str] | None,
    min_size: int | None,
    max_size: int | None,
    modified_after: datetime | None,
    modified_before: datetime | None,
    content_search: str | None,
    max_results: int,
    current_depth: int,
) -> tuple[list[FileInfo], list[FileInfo]]:
    """Recursively search a directory."""
    files: list[FileInfo] = []
    directories: list[FileInfo] = []

    try:
        # Get all items in directory
        items = list(base_path.iterdir())

        for item in items:
            try:
                file_info = FileInfo.from_path(item)

                # For directories in recursive mode, don't apply pattern matching
                # as we need to search inside them
                if not (file_info.is_directory and recursive):
                    # Check name pattern
                    if pattern and not fnmatch.fnmatch(file_info.name, pattern):
                        continue

                    # Check regex pattern
                    if regex_pattern and not re.match(regex_pattern, file_info.name):
                        continue

                # Check other filters
                if not _matches_filters(
                    file_info, file_types, exclude_patterns, min_size, max_size, modified_after, modified_before, include_hidden
                ):
                    continue

                # Check content for files
                if file_info.is_directory:
                    directories.append(file_info)

                    # Recursive search
                    if recursive and (max_depth is None or current_depth < max_depth):
                        sub_files, sub_dirs = await _search_directory_recursive(
                            base_path=item,
                            pattern=pattern,
                            regex_pattern=regex_pattern,
                            recursive=recursive,
                            max_depth=max_depth,
                            include_hidden=include_hidden,
                            file_types=file_types,
                            exclude_patterns=exclude_patterns,
                            min_size=min_size,
                            max_size=max_size,
                            modified_after=modified_after,
                            modified_before=modified_before,
                            content_search=content_search,
                            max_results=max_results,
                            current_depth=current_depth + 1,
                        )
                        files.extend(sub_files[: max(0, max_results - len(files))])
                        directories.extend(sub_dirs[: max(0, max_results - len(directories))])
                else:
                    # Check content if specified
                    if await _check_content(str(item), content_search):
                        files.append(file_info)

                # Check result limit
                if len(files) + len(directories) >= max_results:
                    break

            except (PermissionError, OSError):
                # Skip files/directories we can't access
                continue

    except (PermissionError, OSError):
        # Skip directories we can't read
        pass

    return files, directories


def _matches_filters(
    file_info: FileInfo,
    file_types: list[str] | None,
    exclude_patterns: list[str] | None,
    min_size: int | None,
    max_size: int | None,
    modified_after: datetime | None,
    modified_before: datetime | None,
    include_hidden: bool,
) -> bool:
    """Check if a file matches all specified filters."""
    # Check file type filter
    if file_types and not file_info.is_directory and not any(file_info.name.endswith(ext) for ext in file_types):
        return False

    # Check exclude patterns
    if exclude_patterns:
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_info.name, pattern):
                return False

    # Check size filters (only for files)
    if not file_info.is_directory:
        if min_size is not None and file_info.size < min_size:
            return False
        if max_size is not None and file_info.size > max_size:
            return False

    # Check date filters
    if modified_after and file_info.modified_time < modified_after:
        return False
    if modified_before and file_info.modified_time > modified_before:
        return False

    # Check hidden files - exclude if hidden and not explicitly included
    return not file_info.name.startswith('.') or include_hidden


async def _check_content(file_path: str, content_search: str | None) -> bool:
    """Check if file contains the search text."""
    if not content_search:
        return True

    try:
        # Only search in text files
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and not mime_type.startswith('text/'):
            return False

        # Read file asynchronously
        async with aiofiles.open(file_path, encoding='utf-8', errors='ignore') as f:
            content = await f.read()
            return content_search.lower() in content.lower()
    except Exception:
        return False


def _sort_results(items: list[FileInfo], sort_by: str, reverse_sort: bool) -> list[FileInfo]:
    """Sort results based on sort_by parameter."""
    sort_keys = {
        "name": lambda x: x.name.lower(),
        "size": lambda x: x.size,
        "modified": lambda x: x.modified_time,
        "created": lambda x: x.created_time or x.modified_time,
    }

    key_func = sort_keys.get(sort_by, sort_keys["name"])
    return sorted(items, key=key_func, reverse=reverse_sort)


# Convenience functions
async def list_directory(
    path: str = ".", pattern: str | None = None, include_hidden: bool = False, sort_by: str = "name"
) -> DirectorySearchResult:
    """List contents of a directory with optional filtering.

    Args:
        path: Directory path to list
        pattern: Optional file name pattern
        include_hidden: Whether to include hidden files
        sort_by: Sort results by name, size, modified, or created

    Returns:
        DirectorySearchResult with files and directories
    """
    return await search_directory(path=path, pattern=pattern, include_hidden=include_hidden, sort_by=sort_by, recursive=False)


async def find_files(
    path: str = ".",
    pattern: str = "*",
    recursive: bool = True,
    file_types: list[str] | None = None,
    content_search: str | None = None,
    max_results: int = 100,
) -> DirectorySearchResult:
    """Find files matching specified criteria.

    Args:
        path: Base directory to search
        pattern: File name pattern (glob)
        recursive: Whether to search recursively
        file_types: List of file extensions to include
        content_search: Text to search within files
        max_results: Maximum number of results

    Returns:
        DirectorySearchResult with matching files
    """
    return await search_directory(
        path=path,
        pattern=pattern,
        recursive=recursive,
        file_types=file_types,
        content_search=content_search,
        max_results=max_results,
    )


async def search_by_content(
    path: str, search_text: str, file_types: list[str] | None = None, recursive: bool = True
) -> DirectorySearchResult:
    """Search for files containing specific text.

    Args:
        path: Directory to search in
        search_text: Text to search for
        file_types: Limit to specific file types
        recursive: Whether to search recursively

    Returns:
        DirectorySearchResult with files containing the text
    """
    return await search_directory(
        path=path,
        content_search=search_text,
        file_types=file_types or ['.txt', '.py', '.md', '.json', '.yaml', '.yml'],
        recursive=recursive,
    )
