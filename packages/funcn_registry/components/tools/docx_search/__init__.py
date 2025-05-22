"""DOCX Search Tool for Word document processing and search."""

from .tool import (
    DocumentSection,
    DOCXSearchResult,
    extract_docx_headings,
    process_docx_document,
    search_docx,
    search_docx_with_regex,
)

__all__ = [
    "process_docx_document",
    "search_docx",
    "extract_docx_headings",
    "search_docx_with_regex",
    "DOCXSearchResult",
    "DocumentSection"
]
