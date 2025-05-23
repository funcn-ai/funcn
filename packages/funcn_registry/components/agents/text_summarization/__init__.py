"""Text Summarization Agent.

This agent uses advanced prompt engineering techniques including chain-of-thought reasoning,
few-shot learning, and iterative refinement to generate high-quality summaries in multiple styles.
"""

from .agent import (
    KeyPoint,
    ProgressiveSummary,
    Summary,
    SummaryAnalysis,
    SummaryValidation,
    executive_brief,
    multi_style_summary,
    quick_summary,
    summarize_text,
)

__all__ = [
    "summarize_text",
    "quick_summary",
    "executive_brief",
    "multi_style_summary",
    "KeyPoint",
    "SummaryAnalysis",
    "Summary",
    "ProgressiveSummary",
    "SummaryValidation",
]
