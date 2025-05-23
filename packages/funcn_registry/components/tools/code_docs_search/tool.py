"""Code Documentation Search Tool for technical documentation retrieval and analysis."""

import aiofiles
import ast
import asyncio
import json
import markdown
import re
import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional, Union


class DocumentationMatch(BaseModel):
    """Represents a match found in technical documentation."""

    file_path: str = Field(..., description="Path to the documentation file")
    title: str | None = Field(None, description="Title of the documentation section")
    content: str = Field(..., description="Content containing the match")
    match_type: str = Field(..., description="Type of match: function, class, method, example, etc.")
    language: str | None = Field(None, description="Programming language if code block")
    line_number: int | None = Field(None, description="Line number where match starts")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    context: str | None = Field(None, description="Surrounding context of the match")


class CodeDocsSearchResult(BaseModel):
    """Result of code documentation search operation."""

    success: bool = Field(..., description="Whether the search was successful")
    search_query: str = Field(..., description="The search query used")
    total_matches: int = Field(..., description="Total number of matches found")
    matches: list[DocumentationMatch] = Field(default_factory=list, description="List of documentation matches")
    searched_files: int = Field(0, description="Number of files searched")
    search_time: float = Field(..., description="Time taken to search in seconds")
    error: str | None = Field(None, description="Error message if search failed")
    file_types_searched: list[str] = Field(default_factory=list, description="File types that were searched")


def validate_search_path(search_path: str) -> str:
    """Ensure the search path exists."""
    path = Path(search_path)
    if not path.exists():
        raise ValueError(f"Search path does not exist: {search_path}")
    return str(path.absolute())


def calculate_relevance_score(
    content: str,
    file_path: str,
    match_type: str,
    search_query: str,
    search_mode: str,
    prioritize_readme: bool
) -> float:
    """Calculate relevance score for a match."""
    score = 0.5  # Base score

    # Boost for README files
    if prioritize_readme and "readme" in file_path.lower():
        score += 0.2

    # Boost for exact matches
    if search_mode == "exact" and search_query in content:
        score += 0.2

    # Boost for title/header matches
    if match_type in ["header", "title"]:
        score += 0.15

    # Boost for function/class definitions
    if match_type in ["function", "class", "method"]:
        score += 0.1

    return min(score, 1.0)


async def search_markdown_file(
    file_path: Path,
    search_query: str,
    search_mode: str,
    case_sensitive: bool,
    include_examples: bool,
    prioritize_readme: bool,
    context_lines: int
) -> list[DocumentationMatch]:
    """Search in markdown files."""
    matches = []

    try:
        async with aiofiles.open(file_path, encoding='utf-8', errors='ignore') as f:
            content = await f.read()

        # Parse markdown
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # Check headers
            if line.startswith('#') and matches_query(line, search_query, search_mode, case_sensitive):
                matches.append(DocumentationMatch(
                        file_path=str(file_path),
                        title=line.strip('#').strip(),
                        content=line,
                        match_type="header",
                        language=None,
                        line_number=i + 1,
                        relevance_score=calculate_relevance_score(
                            line, str(file_path), "header", search_query, search_mode, prioritize_readme
                        ),
                        context=get_context(lines, i, context_lines)
                    ))

            # Check code blocks
            if line.startswith('```'):
                language = line[3:].strip() if len(line) > 3 else None
                code_lines = []
                j = i + 1

                while j < len(lines) and not lines[j].startswith('```'):
                    code_lines.append(lines[j])
                    j += 1

                code_content = '\n'.join(code_lines)
                if include_examples and matches_query(code_content, search_query, search_mode, case_sensitive):
                    matches.append(DocumentationMatch(
                        file_path=str(file_path),
                        title=None,
                        content=code_content,
                        match_type="code_example",
                        language=language,
                        line_number=i + 1,
                        relevance_score=calculate_relevance_score(
                            code_content, str(file_path), "example", search_query, search_mode, prioritize_readme
                        ),
                        context=get_context(lines, i, context_lines)
                    ))

            # Check regular content
            elif matches_query(line, search_query, search_mode, case_sensitive):
                matches.append(DocumentationMatch(
                    file_path=str(file_path),
                    title=None,
                    content=line,
                    match_type="content",
                    language=None,
                    line_number=i + 1,
                    relevance_score=calculate_relevance_score(
                        line, str(file_path), "content", search_query, search_mode, prioritize_readme
                    ),
                    context=get_context(lines, i, context_lines)
                ))

    except Exception as e:
        # Skip files that can't be read
        pass

    return matches


async def search_python_file(
    file_path: Path,
    search_query: str,
    search_mode: str,
    case_sensitive: bool,
    include_docstrings: bool,
    include_code_comments: bool,
    prioritize_readme: bool,
    context_lines: int
) -> list[DocumentationMatch]:
    """Search in Python files for docstrings and comments."""
    matches = []

    try:
        async with aiofiles.open(file_path, encoding='utf-8', errors='ignore') as f:
            content = await f.read()

        # Parse AST to find docstrings
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                docstring = None
                node_type = None
                node_name = None

                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    node_type = "function"
                    node_name = node.name
                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    node_type = "class"
                    node_name = node.name
                elif isinstance(node, ast.AsyncFunctionDef):
                    docstring = ast.get_docstring(node)
                    node_type = "async_function"
                    node_name = node.name

                if docstring and node_type and include_docstrings and matches_query(docstring, search_query, search_mode, case_sensitive):
                    matches.append(DocumentationMatch(
                        file_path=str(file_path),
                        title=f"{node_type}: {node_name}",
                        content=docstring,
                        match_type=node_type,
                        language="python",
                        line_number=node.lineno if hasattr(node, 'lineno') else None,
                        relevance_score=calculate_relevance_score(
                            docstring, str(file_path), node_type, search_query, search_mode, prioritize_readme
                        ),
                        metadata={"name": node_name, "type": node_type},
                        context=None
                    ))

        except SyntaxError:
            # If AST parsing fails, fall back to regex
            pass

        # Search for comments
        if include_code_comments:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '#' in line:
                    comment = line.split('#', 1)[1].strip()
                    if matches_query(comment, search_query, search_mode, case_sensitive):
                        matches.append(DocumentationMatch(
                            file_path=str(file_path),
                            title=None,
                            content=comment,
                            match_type="comment",
                            language="python",
                            line_number=i + 1,
                            relevance_score=calculate_relevance_score(
                                comment, str(file_path), "comment", search_query, search_mode, prioritize_readme
                            ),
                            context=get_context(lines, i, context_lines)
                        ))

    except Exception as e:
        # Skip files that can't be read
        pass

    return matches


async def search_javascript_file(
    file_path: Path,
    search_query: str,
    search_mode: str,
    case_sensitive: bool,
    include_code_comments: bool,
    prioritize_readme: bool,
    context_lines: int
) -> list[DocumentationMatch]:
    """Search in JavaScript/TypeScript files for JSDoc and comments."""
    matches = []

    try:
        async with aiofiles.open(file_path, encoding='utf-8', errors='ignore') as f:
            content = await f.read()

        lines = content.split('\n')

        # Search for JSDoc comments
        in_jsdoc = False
        jsdoc_lines = []
        jsdoc_start = 0

        for i, line in enumerate(lines):
            if '/**' in line:
                in_jsdoc = True
                jsdoc_start = i
                jsdoc_lines = [line]
            elif in_jsdoc:
                jsdoc_lines.append(line)
                if '*/' in line:
                    in_jsdoc = False
                    jsdoc_content = '\n'.join(jsdoc_lines)

                    if matches_query(jsdoc_content, search_query, search_mode, case_sensitive):
                        # Try to find the associated function/class
                        next_line_idx = i + 1
                        if next_line_idx < len(lines):
                            next_line = lines[next_line_idx].strip()
                            title = extract_js_signature(next_line)
                        else:
                            title = None

                        matches.append(DocumentationMatch(
                            file_path=str(file_path),
                            title=title,
                            content=jsdoc_content,
                            match_type="jsdoc",
                            language="javascript",
                            line_number=jsdoc_start + 1,
                            relevance_score=calculate_relevance_score(
                                jsdoc_content, str(file_path), "jsdoc", search_query, search_mode, prioritize_readme
                            ),
                            context=None
                        ))

            # Search for regular comments
            if include_code_comments and '//' in line:
                comment = line.split('//', 1)[1].strip()
                if matches_query(comment, search_query, search_mode, case_sensitive):
                    matches.append(DocumentationMatch(
                        file_path=str(file_path),
                        title=None,
                        content=comment,
                        match_type="comment",
                        language="javascript",
                        line_number=i + 1,
                        relevance_score=calculate_relevance_score(
                            comment, str(file_path), "comment", search_query, search_mode, prioritize_readme
                        ),
                        context=get_context(lines, i, context_lines)
                    ))

    except Exception:
        pass

    return matches


def extract_js_signature(line: str) -> str | None:
    """Extract JavaScript function/class signature."""
    patterns = [
        r'function\s+(\w+)',
        r'class\s+(\w+)',
        r'const\s+(\w+)\s*=\s*\(',
        r'let\s+(\w+)\s*=\s*\(',
        r'var\s+(\w+)\s*=\s*\(',
    ]

    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            return match.group(1)

    return None


def matches_query(text: str, search_query: str, search_mode: str, case_sensitive: bool) -> bool:
    """Check if text matches the search query."""
    if not text:
        return False

    if not case_sensitive:
        text = text.lower()
        query = search_query.lower()
    else:
        query = search_query

    if search_mode == "exact":
        return query in text
    elif search_mode == "fuzzy":
        # Simple fuzzy match - all words in query should be in text
        query_words = query.split()
        return all(word in text for word in query_words)
    else:  # semantic - for now, same as fuzzy
        query_words = query.split()
        return all(word in text for word in query_words)


def get_context(lines: list[str], index: int, context_lines: int) -> str:
    """Get context lines around a match."""
    start = max(0, index - context_lines)
    end = min(len(lines), index + context_lines + 1)
    return '\n'.join(lines[start:end])


async def search_file(
    file_path: Path,
    search_query: str,
    search_mode: str,
    case_sensitive: bool,
    include_code_comments: bool,
    include_docstrings: bool,
    include_examples: bool,
    prioritize_readme: bool,
    context_lines: int
) -> list[DocumentationMatch]:
    """Search in a single file based on its type."""
    extension = file_path.suffix.lower()[1:]  # Remove the dot

    if extension in ['md', 'markdown']:
        return await search_markdown_file(
            file_path, search_query, search_mode, case_sensitive,
            include_examples, prioritize_readme, context_lines
        )
    elif extension == 'py':
        return await search_python_file(
            file_path, search_query, search_mode, case_sensitive,
            include_docstrings, include_code_comments, prioritize_readme, context_lines
        )
    elif extension in ['js', 'ts', 'jsx', 'tsx']:
        return await search_javascript_file(
            file_path, search_query, search_mode, case_sensitive,
            include_code_comments, prioritize_readme, context_lines
        )
    else:
        # Generic text search for other files
        matches = []
        try:
            async with aiofiles.open(file_path, encoding='utf-8', errors='ignore') as f:
                content = await f.read()

            lines = content.split('\n')
            for i, line in enumerate(lines):
                if matches_query(line, search_query, search_mode, case_sensitive):
                    matches.append(DocumentationMatch(
                        file_path=str(file_path),
                        title=None,
                        content=line,
                        match_type="content",
                        language=None,
                        line_number=i + 1,
                        relevance_score=calculate_relevance_score(
                            line, str(file_path), "content", search_query, search_mode, prioritize_readme
                        ),
                        context=get_context(lines, i, context_lines)
                    ))
        except Exception:
            pass

        return matches


async def search_code_documentation(
    search_query: str,
    search_path: str = ".",
    doc_types: list[str] | None = None,
    search_mode: Literal["exact", "fuzzy", "semantic"] = "fuzzy",
    include_code_comments: bool = True,
    include_docstrings: bool = True,
    include_examples: bool = True,
    max_results: int = 50,
    context_lines: int = 3,
    prioritize_readme: bool = True,
    case_sensitive: bool = False
) -> CodeDocsSearchResult:
    """Search and analyze technical documentation including API docs, README files, and code comments.

    Args:
        search_query: Query to search for in documentation
        search_path: Base path to search for documentation
        doc_types: File extensions to search (defaults to common doc/code types)
        search_mode: Search mode to use - exact, fuzzy, or semantic
        include_code_comments: Whether to search in code comments
        include_docstrings: Whether to search in docstrings
        include_examples: Whether to extract code examples
        max_results: Maximum number of results to return
        context_lines: Number of context lines around matches
        prioritize_readme: Whether to prioritize README files
        case_sensitive: Whether search is case sensitive

    Returns:
        CodeDocsSearchResult with matching documentation
    """
    start_time = asyncio.get_event_loop().time()

    try:
        # Validate search path
        search_path_str = validate_search_path(search_path)
        search_path_obj = Path(search_path_str)

        # Default doc types if not specified
        if doc_types is None:
            doc_types = ["md", "rst", "txt", "py", "js", "ts", "java", "cpp", "go", "rb"]

        all_matches = []
        searched_files = 0
        file_types_searched = set()

        # Collect all files to search
        files_to_search = []
        for doc_type in doc_types:
            for file_path in search_path_obj.rglob(f"*.{doc_type}"):
                if file_path.is_file():
                    files_to_search.append(file_path)
                    file_types_searched.add(doc_type)

        # Search files concurrently
        tasks = []
        for file_path in files_to_search:
            tasks.append(search_file(
                file_path, search_query, search_mode, case_sensitive,
                include_code_comments, include_docstrings, include_examples,
                prioritize_readme, context_lines
            ))
            searched_files += 1

        # Gather results
        results = await asyncio.gather(*tasks)
        for file_matches in results:
            all_matches.extend(file_matches)

        # Sort by relevance score
        all_matches.sort(key=lambda x: x.relevance_score, reverse=True)

        # Limit results
        all_matches = all_matches[:max_results]

        search_time = asyncio.get_event_loop().time() - start_time

        return CodeDocsSearchResult(
            success=True,
            search_query=search_query,
            total_matches=len(all_matches),
            matches=all_matches,
            searched_files=searched_files,
            search_time=search_time,
            error=None,
            file_types_searched=list(file_types_searched)
        )

    except Exception as e:
        search_time = asyncio.get_event_loop().time() - start_time
        return CodeDocsSearchResult(
            success=False,
            search_query=search_query,
            total_matches=0,
            searched_files=0,
            search_time=search_time,
            error=str(e)
        )


# Convenience functions
async def search_documentation(
    query: str,
    path: str = ".",
    doc_types: list[str] | None = None,
    max_results: int = 20
) -> CodeDocsSearchResult:
    """Search for documentation matching a query.

    Args:
        query: Search query
        path: Base path to search
        doc_types: File types to search (defaults to common doc types)
        max_results: Maximum results to return

    Returns:
        CodeDocsSearchResult with matches
    """
    return await search_code_documentation(
        search_query=query,
        search_path=path,
        doc_types=doc_types or ["md", "rst", "txt"],
        max_results=max_results
    )


async def find_code_examples(
    topic: str,
    path: str = ".",
    languages: list[str] | None = None
) -> CodeDocsSearchResult:
    """Find code examples for a specific topic.

    Args:
        topic: Topic to find examples for
        path: Base path to search
        languages: Programming languages to search

    Returns:
        CodeDocsSearchResult with code examples
    """
    doc_types = languages or ["py", "js", "ts", "java", "cpp", "go"]
    return await search_code_documentation(
        search_query=topic,
        search_path=path,
        doc_types=doc_types,
        include_examples=True,
        search_mode="fuzzy"
    )


async def search_api_docs(
    api_name: str,
    path: str = ".",
    include_comments: bool = True
) -> CodeDocsSearchResult:
    """Search for API documentation.

    Args:
        api_name: API name or function to search for
        path: Base path to search
        include_comments: Whether to include code comments

    Returns:
        CodeDocsSearchResult with API documentation
    """
    return await search_code_documentation(
        search_query=api_name,
        search_path=path,
        include_code_comments=include_comments,
        include_docstrings=True,
        prioritize_readme=True
    )
