"""Common prompt patterns using Mirascope."""

from .classification import classify_multi_label, classify_sentiment, classify_text
from .content_generation import generate_creative, generate_structured, generate_technical
from .extraction import extract_entities, extract_key_points, extract_relationships
from .question_answering import answer_contextual, answer_factual, answer_reasoning
from .summarization import summarize_abstractive, summarize_bullets, summarize_extractive

__all__ = [
    # Summarization
    "summarize_extractive",
    "summarize_abstractive",
    "summarize_bullets",
    # Classification
    "classify_text",
    "classify_sentiment",
    "classify_multi_label",
    # Extraction
    "extract_entities",
    "extract_relationships",
    "extract_key_points",
    # Question Answering
    "answer_factual",
    "answer_reasoning",
    "answer_contextual",
    # Content Generation
    "generate_creative",
    "generate_technical",
    "generate_structured",
]
