"""Code Documentation Search Tool for technical documentation retrieval and analysis."""

from .tool import (
    CodeDocsSearchResult,
    DocumentationMatch,
    find_code_examples,
    search_api_docs,
    search_code_documentation,
    search_documentation,
)

__all__ = [
    "search_code_documentation",
    "search_documentation",
    "find_code_examples",
    "search_api_docs",
    "CodeDocsSearchResult",
    "DocumentationMatch"
]
