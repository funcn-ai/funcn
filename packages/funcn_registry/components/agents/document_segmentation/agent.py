from __future__ import annotations

import re
from collections import defaultdict
from lilypad import trace
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


# Response models for structured outputs
class DocumentSegment(BaseModel):
    """A segment of a document."""

    id: str = Field(..., description="Unique identifier for the segment")
    title: str = Field(..., description="Title or heading of the segment")
    content: str = Field(..., description="Content of the segment")
    segment_type: str = Field(..., description="Type of segment (e.g., introduction, methodology, results)")
    start_position: int = Field(..., description="Starting character position in original document")
    end_position: int = Field(..., description="Ending character position in original document")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    parent_id: str | None = Field(default=None, description="ID of parent segment if hierarchical")
    child_ids: list[str] = Field(default_factory=list, description="IDs of child segments")


class SegmentationStrategy(BaseModel):
    """Strategy for document segmentation."""

    method: Literal["semantic", "structural", "hybrid", "fixed_size"] = Field(..., description="Segmentation method")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Method-specific parameters")
    segment_types: list[str] = Field(..., description="Expected segment types for this document")


class DocumentStructure(BaseModel):
    """Analyzed document structure."""

    document_type: str = Field(..., description="Type of document (e.g., research_paper, report, article)")
    has_sections: bool = Field(..., description="Whether document has clear sections")
    has_chapters: bool = Field(..., description="Whether document has chapters")
    has_paragraphs: bool = Field(..., description="Whether document has paragraphs")
    estimated_segments: int = Field(..., description="Estimated number of segments")
    recommended_strategy: SegmentationStrategy = Field(..., description="Recommended segmentation strategy")


class SegmentationResult(BaseModel):
    """Complete result of document segmentation."""

    segments: list[DocumentSegment] = Field(..., description="List of document segments")
    document_structure: DocumentStructure = Field(..., description="Analyzed document structure")
    hierarchy: dict[str, list[str]] = Field(default_factory=dict, description="Hierarchical structure of segments")
    summary: str = Field(..., description="Summary of segmentation results")
    total_segments: int = Field(..., description="Total number of segments created")


class SegmentSummary(BaseModel):
    """Summary of a document segment."""

    segment_id: str = Field(..., description="ID of the segment")
    summary: str = Field(..., description="Concise summary of the segment")
    key_points: list[str] = Field(..., description="Key points from the segment")
    topics: list[str] = Field(..., description="Main topics covered")


# Tool for structural segmentation using regex and patterns
@trace()
async def segment_by_structure(text: str, min_segment_length: int = 100) -> list[DocumentSegment]:
    """
    Segment document based on structural elements like headings and paragraphs.

    Args:
        text: Document text to segment
        min_segment_length: Minimum length for a segment

    Returns:
        List of document segments
    """
    segments = []

    # Common heading patterns
    heading_patterns = [
        r'^#{1,6}\s+(.+)$',  # Markdown headings
        r'^([A-Z][^.!?]*[:.])$',  # Title case lines ending with colon
        r'^(\d+\.?\s+[A-Z].+)$',  # Numbered sections
        r'^([A-Z]+(?:\s+[A-Z]+)*)\s*$',  # All caps headings
        r'^Chapter\s+\d+',  # Chapter headings
        r'^Section\s+\d+',  # Section headings
    ]

    lines = text.split('\n')
    current_segment: list[str] = []
    current_title = "Introduction"
    start_pos = 0
    segment_counter = 0

    for i, line in enumerate(lines):
        # Check if line matches any heading pattern
        is_heading = False
        for pattern in heading_patterns:
            if re.match(pattern, line.strip(), re.MULTILINE):
                is_heading = True

                # Save current segment if it has content
                if current_segment and len('\n'.join(current_segment)) >= min_segment_length:
                    segment_counter += 1
                    segments.append(
                        DocumentSegment(
                            id=f"seg_{segment_counter}",
                            title=current_title,
                            content='\n'.join(current_segment).strip(),
                            segment_type="section",
                            start_position=start_pos,
                            end_position=start_pos + len('\n'.join(current_segment)),
                            metadata={"line_start": i - len(current_segment), "line_end": i},
                        )
                    )
                    start_pos += len('\n'.join(current_segment)) + 1

                # Start new segment
                current_title = line.strip()
                current_segment = []
                break

        if not is_heading:
            current_segment.append(line)

    # Add final segment
    if current_segment and len('\n'.join(current_segment)) >= min_segment_length:
        segment_counter += 1
        segments.append(
            DocumentSegment(
                id=f"seg_{segment_counter}",
                title=current_title,
                content='\n'.join(current_segment).strip(),
                segment_type="section",
                start_position=start_pos,
                end_position=len(text),
                metadata={"line_start": len(lines) - len(current_segment), "line_end": len(lines)},
            )
        )

    return segments


# Step 1: Analyze document structure
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=DocumentStructure,
)
@prompt_template(
    """
    You are an expert document analyst. Analyze the structure of this document.

    Document preview (first 1000 characters):
    "{document_preview}"

    Document length: {doc_length} characters

    Analyze:
    1. Document type (research paper, report, article, book, etc.)
    2. Structural elements present (sections, chapters, paragraphs)
    3. Estimated number of logical segments
    4. Best segmentation strategy:
       - "semantic": Group by meaning and topic
       - "structural": Use headings and formatting
       - "hybrid": Combine semantic and structural
       - "fixed_size": Fixed character/word count segments

    Consider the document's purpose and how it should be logically divided for processing.
    """
)
async def analyze_document_structure(document_preview: str, doc_length: int):
    """Analyze document structure to determine segmentation strategy."""
    pass


# Step 2: Perform semantic segmentation
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=SegmentationResult,
)
@prompt_template(
    """
    You are an expert in document segmentation. Segment this document semantically.

    Document:
    "{document}"

    Strategy: {strategy}
    Expected segment types: {segment_types}

    Guidelines:
    1. Identify natural topic boundaries
    2. Group related content together
    3. Preserve logical flow and coherence
    4. Create meaningful segment titles
    5. Maintain appropriate segment sizes (not too small or large)
    6. Track parent-child relationships for hierarchical content

    For each segment provide:
    - Unique ID
    - Descriptive title
    - Content
    - Type (introduction, background, methodology, results, discussion, conclusion, etc.)
    - Position information
    - Metadata (key topics, importance, etc.)
    """
)
async def segment_semantically(document: str, strategy: str, segment_types: str):
    """Perform semantic segmentation of document."""
    pass


# Step 3: Summarize segments
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=SegmentSummary,
)
@prompt_template(
    """
    Summarize this document segment concisely.

    Segment title: {title}
    Segment content:
    {content}

    Provide:
    1. A concise summary (2-3 sentences)
    2. 3-5 key points
    3. Main topics covered

    Focus on the most important information and insights.
    """
)
async def summarize_segment(segment_id: str, title: str, content: str):
    """Generate summary for a document segment."""
    pass


# Main document segmentation function
@trace()
async def segment_document(
    document: str,
    segmentation_method: Literal["auto", "semantic", "structural", "hybrid", "fixed_size"] = "auto",
    target_segment_size: int | None = None,
    min_segment_size: int = 100,
    max_segment_size: int = 5000,
    generate_summaries: bool = True,
    hierarchical: bool = True,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> SegmentationResult:
    """
    Segment a document into logical parts for processing.

    This agent analyzes document structure and segments it using
    appropriate strategies for optimal processing and understanding.

    Args:
        document: Full document text to segment
        segmentation_method: Method to use for segmentation
        target_segment_size: Target size for segments in characters
        min_segment_size: Minimum segment size
        max_segment_size: Maximum segment size
        generate_summaries: Whether to generate summaries for segments
        hierarchical: Whether to create hierarchical structure
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        SegmentationResult with segments and analysis
    """
    # Step 1: Analyze document structure if method is auto
    if segmentation_method == "auto":
        preview = document[:1000]
        structure = await analyze_document_structure(document_preview=preview, doc_length=len(document))
        segmentation_method = structure.recommended_strategy.method
    else:
        # Create default structure
        structure = DocumentStructure(
            document_type="unknown",
            has_sections=True,
            has_chapters=False,
            has_paragraphs=True,
            estimated_segments=len(document) // 1000,
            recommended_strategy=SegmentationStrategy(method=segmentation_method, parameters={}, segment_types=["section"]),
        )

    # Step 2: Perform segmentation based on method
    if segmentation_method == "structural":
        segments = await segment_by_structure(document, min_segment_size)

    elif segmentation_method == "fixed_size":
        # Simple fixed-size segmentation
        segments = []
        chunk_size = target_segment_size or 1000
        for i in range(0, len(document), chunk_size):
            segments.append(
                DocumentSegment(
                    id=f"seg_{i // chunk_size + 1}",
                    title=f"Part {i // chunk_size + 1}",
                    content=document[i : i + chunk_size],
                    segment_type="chunk",
                    start_position=i,
                    end_position=min(i + chunk_size, len(document)),
                    metadata={"chunk_index": i // chunk_size},
                )
            )

    else:  # semantic or hybrid
        # Use LLM for semantic segmentation
        segment_types_str = ", ".join(structure.recommended_strategy.segment_types)
        result = await segment_semantically(document=document, strategy=segmentation_method, segment_types=segment_types_str)
        segments = result.segments
        structure = result.document_structure

    # Step 3: Generate summaries if requested
    if generate_summaries and segments:
        for segment in segments[:10]:  # Limit to first 10 for performance
            try:
                summary = await summarize_segment(
                    segment_id=segment.id,
                    title=segment.title,
                    content=segment.content[:1000],  # Limit content for summary
                )
                segment.metadata["summary"] = summary.summary
                segment.metadata["key_points"] = summary.key_points
                segment.metadata["topics"] = summary.topics
            except Exception as e:
                segment.metadata["summary_error"] = str(e)

    # Build hierarchy if requested
    hierarchy: dict[str, list[str]] = {}
    if hierarchical:
        # Group segments by type or parent
        for segment in segments:
            parent = segment.parent_id or "root"
            if parent not in hierarchy:
                hierarchy[parent] = []
            hierarchy[parent].append(segment.id)

    return SegmentationResult(
        segments=segments,
        document_structure=structure,
        hierarchy=hierarchy,
        summary=f"Document segmented into {len(segments)} parts using {segmentation_method} method.",
        total_segments=len(segments),
    )


# Convenience functions
async def quick_segment(document: str, max_segments: int = 10) -> list[dict[str, Any]]:
    """
    Quick document segmentation with basic info.

    Returns simplified segment list.
    """
    result = await segment_document(document=document, generate_summaries=False, hierarchical=False)

    return [
        {
            "id": seg.id,
            "title": seg.title,
            "length": len(seg.content),
            "type": seg.segment_type,
            "preview": seg.content[:200] + "..." if len(seg.content) > 200 else seg.content,
        }
        for seg in result.segments[:max_segments]
    ]


async def extract_sections(document: str, section_types: list[str]) -> dict[str, str]:
    """
    Extract specific sections from a document.

    Returns dictionary mapping section type to content.
    """
    result = await segment_document(document=document, segmentation_method="semantic")

    sections = {}
    for segment in result.segments:
        if segment.segment_type.lower() in [s.lower() for s in section_types]:
            sections[segment.segment_type] = segment.content

    return sections


async def chunk_for_embedding(document: str, chunk_size: int = 512, overlap: int = 50) -> list[dict[str, Any]]:
    """
    Chunk document for vector embedding with overlap.

    Returns chunks optimized for embedding models.
    """
    chunks = []

    # First segment the document semantically
    result = await segment_document(document=document, segmentation_method="semantic", generate_summaries=False)

    # Then chunk each segment with overlap
    chunk_id = 0
    for segment in result.segments:
        text = segment.content
        for i in range(0, len(text), chunk_size - overlap):
            chunk_id += 1
            chunk_text = text[i : i + chunk_size]

            chunks.append(
                {
                    "id": f"chunk_{chunk_id}",
                    "text": chunk_text,
                    "segment_id": segment.id,
                    "segment_title": segment.title,
                    "start": i,
                    "end": min(i + chunk_size, len(text)),
                    "metadata": {"segment_type": segment.segment_type, "has_overlap": i > 0},
                }
            )

    return chunks
