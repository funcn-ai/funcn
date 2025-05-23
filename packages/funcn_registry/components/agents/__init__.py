"""Funcn Registry Agents.

Collection of advanced AI agents for various tasks including web search,
research, hallucination detection, data analysis, and more.
"""

# Existing agents
# New advanced agents
# Enhanced agents with advanced prompt engineering
from . import (
    academic_research,
    code_generation_execution,
    dataset_builder,
    document_segmentation,
    enhanced_knowledge_graph,
    hallucination_detector,
    knowledge_graph,
    market_intelligence,
    pii_scrubbing,
    recruiting_assistant,
    research_assistant,
    sales_intelligence,
    sourcing_assistant,
    text_summarization,
    web_search,
)

__all__ = [
    # Existing agents
    "academic_research",
    "dataset_builder",
    "hallucination_detector",
    "market_intelligence",
    "recruiting_assistant",
    "research_assistant",
    "sales_intelligence",
    "sourcing_assistant",
    "web_search",
    # New advanced agents
    "code_generation_execution",
    "document_segmentation",
    "knowledge_graph",
    "pii_scrubbing",
    # Enhanced agents
    "text_summarization",
    "enhanced_knowledge_graph",
]
