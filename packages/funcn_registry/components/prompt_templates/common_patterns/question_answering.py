"""
Question answering patterns using Mirascope.

Common patterns for different types of question answering tasks including
factual QA, reasoning-based QA, and context-based QA.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field
from typing import Optional

# Factual question answering


class FactualAnswer(BaseModel):
    """Model for factual QA results."""

    question: str = Field(..., description="The question asked")
    answer: str = Field(..., description="Direct answer")
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence")
    answer_type: str = Field(..., description="Type of answer (fact/definition/explanation)")
    sources: list[str] = Field(..., description="Information sources used")
    caveats: list[str] = Field(..., description="Important caveats or limitations")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=FactualAnswer, call_params={"temperature": 0.1})
@prompt_template(
    """
    Answer this factual question precisely:

    Question: {question}

    Domain: {domain}
    Required depth: {depth_level}

    Provide:
    1. Direct, accurate answer
    2. Confidence level
    3. Answer type (fact/definition/explanation)
    4. Information sources
    5. Any important caveats

    Be concise but complete. Acknowledge if uncertain.
    """
)
def answer_factual(question: str, domain: str = "general knowledge", depth_level: str = "standard"):
    """
    Answer factual questions with confidence scoring.

    Args:
        question: Factual question to answer
        domain: Knowledge domain
        depth_level: Detail level (brief/standard/detailed)

    Returns:
        FactualAnswer with direct response
    """
    pass


# Reasoning-based question answering


class ReasonedAnswer(BaseModel):
    """Model for reasoning-based answers."""

    question: str = Field(..., description="The question asked")
    reasoning_steps: list[str] = Field(..., description="Step-by-step reasoning")
    final_answer: str = Field(..., description="Concluded answer")
    assumptions: list[str] = Field(..., description="Assumptions made")
    alternative_answers: list[str] = Field(..., description="Other possible answers")
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ReasonedAnswer)
@prompt_template(
    """
    Answer this question through logical reasoning:

    Question: {question}

    Context: {context}

    Approach:
    1. Identify what's being asked
    2. List relevant information
    3. Apply logical reasoning
    4. Consider alternatives
    5. Reach a conclusion

    Show your reasoning process clearly.
    """
)
def answer_reasoning(question: str, context: str = ""):
    """
    Answer questions requiring logical reasoning.

    Args:
        question: Question requiring reasoning
        context: Additional context

    Returns:
        ReasonedAnswer with reasoning steps
    """
    pass


# Context-based question answering


class ContextualAnswer(BaseModel):
    """Model for context-based answers."""

    question: str = Field(..., description="The question asked")
    answer: str = Field(..., description="Answer based on context")
    supporting_quotes: list[str] = Field(..., description="Relevant quotes from context")
    answer_location: str = Field(..., description="Where in context answer was found")
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence")
    context_sufficient: bool = Field(..., description="Whether context had enough info")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ContextualAnswer, call_params={"temperature": 0.2})
@prompt_template(
    """
    Answer this question based only on the provided context:

    Context:
    {context}

    Question: {question}

    Instructions:
    - Use only information from the context
    - Quote relevant passages
    - Indicate where the answer was found
    - If context insufficient, state clearly

    Do not use external knowledge.
    """
)
def answer_contextual(question: str, context: str):
    """
    Answer questions based on provided context.

    Args:
        question: Question to answer
        context: Context containing answer

    Returns:
        ContextualAnswer with supporting evidence
    """
    pass


# Multi-hop question answering


class MultiHopAnswer(BaseModel):
    """Model for multi-hop reasoning answers."""

    question: str = Field(..., description="Complex question")
    sub_questions: list[str] = Field(..., description="Decomposed sub-questions")
    intermediate_answers: dict[str, str] = Field(..., description="Answers to sub-questions")
    reasoning_chain: list[str] = Field(..., description="Chain of reasoning")
    final_answer: str = Field(..., description="Synthesized final answer")
    evidence_used: list[str] = Field(..., description="Evidence for each hop")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=MultiHopAnswer)
@prompt_template(
    """
    Answer this complex question requiring multiple reasoning steps:

    Question: {question}

    Available Information:
    {information}

    Approach:
    1. Break down into sub-questions
    2. Answer each sub-question
    3. Connect the answers
    4. Synthesize final answer

    Show how each piece of information contributes.
    """
)
def answer_multi_hop(question: str, information: str):
    """
    Answer complex multi-hop reasoning questions.

    Args:
        question: Complex question
        information: Available information

    Returns:
        MultiHopAnswer with reasoning chain
    """
    pass


# Comparative question answering


class ComparativeAnswer(BaseModel):
    """Model for comparative answers."""

    question: str = Field(..., description="Comparative question")
    entities_compared: list[str] = Field(..., description="Entities being compared")
    comparison_criteria: list[str] = Field(..., description="Criteria used")
    comparison_table: dict[str, dict[str, str]] = Field(..., description="Comparison details")
    summary: str = Field(..., description="Summary of comparison")
    recommendation: str | None = Field(None, description="Recommendation if applicable")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ComparativeAnswer)
@prompt_template(
    """
    Answer this comparative question:

    Question: {question}

    Context: {context}

    Provide:
    1. Entities being compared
    2. Comparison criteria
    3. Detailed comparison table
    4. Summary of findings
    5. Recommendation (if applicable)

    Be objective and balanced in comparison.
    """
)
def answer_comparative(question: str, context: str = ""):
    """
    Answer questions requiring comparison.

    Args:
        question: Comparative question
        context: Additional context

    Returns:
        ComparativeAnswer with detailed comparison
    """
    pass


# Dynamic QA with follow-up handling


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template(
    """
    Answer this question considering the conversation history:

    Previous Q&A:
    {qa_history:lists}

    Current Question: {question}

    Consider:
    - Reference to previous answers
    - Clarifications needed
    - Building on prior context

    Provide a coherent answer that acknowledges the conversation flow.
    """
)
def answer_with_history(question: str, qa_history: list[dict[str, str]]) -> BaseDynamicConfig:
    """
    Answer questions with conversation history.

    Args:
        question: Current question
        qa_history: Previous Q&A pairs

    Returns:
        Answer considering conversation context
    """
    formatted_history = []
    for qa in qa_history:
        formatted_history.append([f"Q: {qa['question']}", f"A: {qa['answer']}", ""])

    return {"computed_fields": {"qa_history": formatted_history}}
