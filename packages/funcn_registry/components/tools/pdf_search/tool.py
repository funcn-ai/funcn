from __future__ import annotations

import asyncio
import os
import PyPDF2
from fuzzywuzzy import fuzz, process
from pathlib import Path

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field
from typing import Optional


class PDFSearchArgs(BaseModel):
    """Arguments for PDF search operations."""

    file_path: str = Field(..., description="Path to the PDF file to search")
    query: str = Field(..., description="Search query to find within the PDF")
    max_results: int = Field(default=10, description="Maximum number of results to return")
    context_chars: int = Field(default=200, description="Number of characters to include as context around matches")
    fuzzy_threshold: int = Field(default=80, description="Fuzzy matching threshold (0-100)")


class PDFSearchResult(BaseModel):
    """Result from a PDF search operation."""

    page_number: int = Field(..., description="Page number where the match was found")
    match_score: float = Field(..., description="Match score (0-100)")
    text: str = Field(..., description="Matched text with context")
    excerpt: str = Field(..., description="The exact matched portion")


class PDFSearchResponse(BaseModel):
    """Response from PDF search tool."""

    results: list[PDFSearchResult] = Field(default_factory=list, description="List of search results")
    total_pages: int = Field(..., description="Total number of pages in the PDF")
    error: str | None = Field(None, description="Error message if search failed")


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def search_pdf_content(args: PDFSearchArgs) -> PDFSearchResponse:
    """Search for text within a PDF file using fuzzy matching.

    This function extracts text from PDF files and performs fuzzy string matching
    to find relevant content based on the search query.
    """
    try:
        # Validate file exists
        file_path = Path(args.file_path)
        if not file_path.exists():
            return PDFSearchResponse(
                results=[],
                total_pages=0,
                error=f"PDF file not found: {args.file_path}"
            )

        # Run PDF extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _extract_and_search, file_path, args)

        return results

    except Exception as e:
        return PDFSearchResponse(
            results=[],
            total_pages=0,
            error=f"Error searching PDF: {str(e)}"
        )


def _extract_and_search(file_path: Path, args: PDFSearchArgs) -> PDFSearchResponse:
    """Extract text from PDF and perform search (sync function for thread pool)."""
    results = []
    total_pages = 0

    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()

                if not page_text:
                    continue

                # Split into sentences/chunks for better matching
                # Simple split by periods and newlines
                chunks = []
                current_chunk = ""

                for char in page_text:
                    current_chunk += char
                    if char in '.!?\n' and len(current_chunk) > 50:
                        chunks.append(current_chunk.strip())
                        current_chunk = ""

                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Find matches in chunks
                for chunk in chunks:
                    # Use fuzzy matching to find similar text
                    match_score = fuzz.partial_ratio(args.query.lower(), chunk.lower())

                    if match_score >= args.fuzzy_threshold:
                        # Find the best matching substring
                        words = chunk.split()
                        best_match = ""
                        best_score = 0

                        # Try different word combinations
                        query_words = len(args.query.split())
                        for i in range(len(words) - query_words + 1):
                            substring = " ".join(words[i:i + query_words])
                            score = fuzz.ratio(args.query.lower(), substring.lower())
                            if score > best_score:
                                best_score = score
                                best_match = substring

                        # Get context around the match
                        chunk_index = chunk.lower().find(best_match.lower())
                        if chunk_index == -1:
                            chunk_index = 0

                        start = max(0, chunk_index - args.context_chars // 2)
                        end = min(len(chunk), chunk_index + len(best_match) + args.context_chars // 2)

                        context_text = chunk[start:end].strip()
                        if start > 0:
                            context_text = "..." + context_text
                        if end < len(chunk):
                            context_text = context_text + "..."

                        results.append(PDFSearchResult(
                            page_number=page_num,
                            match_score=match_score,
                            text=context_text,
                            excerpt=best_match
                        ))

        # Sort by match score and limit results
        results.sort(key=lambda x: x.match_score, reverse=True)
        results = results[:args.max_results]

        return PDFSearchResponse(
            results=results,
            total_pages=total_pages,
            error=None
        )

    except Exception as e:
        return PDFSearchResponse(
            results=[],
            total_pages=0,
            error=f"Error processing PDF: {str(e)}"
        )
