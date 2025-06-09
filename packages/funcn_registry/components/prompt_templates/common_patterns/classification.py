"""
Classification patterns using Mirascope.

Common patterns for text classification tasks including sentiment analysis,
multi-label classification, and hierarchical categorization.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field

# Basic text classification


class TextClassification(BaseModel):
    """Model for text classification results."""

    text: str = Field(..., description="Input text")
    category: str = Field(..., description="Assigned category")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence")
    reasoning: str = Field(..., description="Reasoning for classification")
    alternative_categories: list[str] = Field(..., description="Other possible categories")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=TextClassification)
@prompt_template(
    """
    Classify this text into one of the following categories:
    {categories:list}

    Text: {text}

    Consider:
    - Primary theme and content
    - Context and tone
    - Best fit among available categories

    Provide the classification with confidence and reasoning.
    """
)
def classify_text(text: str, categories: list[str]):
    """
    Basic single-label text classification.

    Args:
        text: Text to classify
        categories: Available categories

    Returns:
        TextClassification with category assignment
    """
    pass


# Sentiment classification


class SentimentAnalysis(BaseModel):
    """Model for sentiment analysis."""

    sentiment: str = Field(..., description="Overall sentiment")
    polarity_score: float = Field(..., ge=-1, le=1, description="Polarity score (-1 to 1)")
    emotions: dict[str, float] = Field(..., description="Emotion scores")
    aspects: dict[str, str] = Field(..., description="Aspect-based sentiments")
    confidence: float = Field(..., ge=0, le=1, description="Analysis confidence")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=SentimentAnalysis, call_params={"temperature": 0.2})
@prompt_template(
    """
    Analyze the sentiment of this text:

    {text}

    Provide:
    1. Overall sentiment (positive/negative/neutral/mixed)
    2. Polarity score (-1 very negative to +1 very positive)
    3. Emotion breakdown (joy, anger, fear, sadness, surprise, disgust)
    4. Aspect-based sentiment for mentioned topics
    5. Confidence in analysis

    Consider context, sarcasm, and nuanced expressions.
    """
)
def classify_sentiment(text: str):
    """
    Comprehensive sentiment analysis.

    Args:
        text: Text to analyze

    Returns:
        SentimentAnalysis with detailed sentiment breakdown
    """
    pass


# Multi-label classification


class MultiLabelClassification(BaseModel):
    """Model for multi-label classification."""

    text: str = Field(..., description="Input text")
    labels: list[str] = Field(..., description="Assigned labels")
    label_scores: dict[str, float] = Field(..., description="Confidence per label")
    primary_label: str = Field(..., description="Most relevant label")
    reasoning: dict[str, str] = Field(..., description="Reasoning per label")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=MultiLabelClassification)
@prompt_template(
    """
    Assign all applicable labels to this text:

    Available labels: {labels:list}

    Text: {text}

    Instructions:
    - Select ALL labels that apply
    - Score each label's relevance (0-1)
    - Identify the primary label
    - Explain why each label applies

    Threshold: {threshold} (minimum score to assign label)
    """
)
def classify_multi_label(text: str, labels: list[str], threshold: float = 0.5):
    """
    Multi-label classification with scoring.

    Args:
        text: Text to classify
        labels: Available labels
        threshold: Minimum score to assign label

    Returns:
        MultiLabelClassification with all applicable labels
    """
    pass


# Hierarchical classification


class HierarchicalClassification(BaseModel):
    """Model for hierarchical classification."""

    primary_category: str = Field(..., description="Top-level category")
    subcategory: str = Field(..., description="Second-level category")
    fine_category: str | None = Field(None, description="Fine-grained category")
    path: list[str] = Field(..., description="Full hierarchical path")
    confidence_path: dict[str, float] = Field(..., description="Confidence at each level")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=HierarchicalClassification)
@prompt_template(
    """
    Classify this text hierarchically:

    Text: {text}

    Taxonomy:
    {taxonomy:lists}

    Navigate the hierarchy:
    1. Select primary category
    2. Select appropriate subcategory
    3. If applicable, select fine-grained category

    Provide confidence at each level.
    """
)
def classify_hierarchical(text: str, taxonomy: dict[str, dict]) -> BaseDynamicConfig:
    """
    Hierarchical classification through taxonomy.

    Args:
        text: Text to classify
        taxonomy: Hierarchical category structure

    Returns:
        HierarchicalClassification with full path
    """
    formatted_taxonomy = []
    for primary, subcats in taxonomy.items():
        formatted_taxonomy.append([f"{primary}:"])
        for subcat, fine_cats in subcats.items():
            formatted_taxonomy.append([f"  - {subcat}"])
            if fine_cats:
                for fine in fine_cats:
                    formatted_taxonomy.append([f"    * {fine}"])

    return {"computed_fields": {"taxonomy": formatted_taxonomy}}


# Intent classification


class IntentClassification(BaseModel):
    """Model for intent classification."""

    primary_intent: str = Field(..., description="Primary user intent")
    secondary_intents: list[str] = Field(..., description="Secondary intents")
    entities: dict[str, str] = Field(..., description="Extracted entities")
    action_required: str = Field(..., description="Suggested action")
    urgency: str = Field(..., description="Urgency level (low/medium/high)")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=IntentClassification, call_params={"temperature": 0.1})
@prompt_template(
    """
    Classify the intent of this user input:

    Input: {user_input}
    Context: {context}

    Available intents: {intents:list}

    Analyze:
    1. Primary intent
    2. Any secondary intents
    3. Key entities mentioned
    4. Required action
    5. Urgency level

    Consider user's goal and context.
    """
)
def classify_intent(user_input: str, intents: list[str], context: str = "general conversation"):
    """
    User intent classification for conversational AI.

    Args:
        user_input: User's input text
        intents: Available intent categories
        context: Conversation context

    Returns:
        IntentClassification with actionable insights
    """
    pass
