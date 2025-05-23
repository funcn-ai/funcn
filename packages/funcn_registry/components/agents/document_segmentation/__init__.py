"""Document Segmentation Agent.

This agent analyzes and segments documents into logical parts using various
strategies for optimal processing and understanding.
"""

from .agent import (
    DocumentSegment,
    DocumentStructure,
    SegmentationResult,
    SegmentationStrategy,
    SegmentSummary,
    chunk_for_embedding,
    extract_sections,
    quick_segment,
    segment_by_structure,
    segment_document,
)

__all__ = [
    "segment_document",
    "quick_segment",
    "extract_sections",
    "chunk_for_embedding",
    "segment_by_structure",
    "DocumentSegment",
    "SegmentationStrategy",
    "DocumentStructure",
    "SegmentationResult",
    "SegmentSummary",
]
