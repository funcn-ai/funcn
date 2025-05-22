"""MDX Search Tool for searching MDX documentation files with JSX component support."""

from .tool import (
    MDXComponent,
    MDXMatch,
    MDXSearchResult,
    extract_mdx_components,
    find_documentation_sections,
    search_mdx_files,
    search_mdx_with_metadata,
)

__all__ = [
    "search_mdx_files",
    "extract_mdx_components",
    "find_documentation_sections",
    "search_mdx_with_metadata",
    "MDXSearchResult",
    "MDXMatch",
    "MDXComponent"
]
