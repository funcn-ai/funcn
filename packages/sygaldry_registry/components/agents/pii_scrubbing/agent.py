from __future__ import annotations

import re
from lilypad import trace
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


# Response models for structured outputs
class PIIEntity(BaseModel):
    """A detected PII entity."""

    text: str = Field(..., description="The PII text found")
    entity_type: str = Field(..., description="Type of PII (e.g., 'email', 'phone', 'ssn', 'name')")
    start_index: int = Field(..., description="Starting position in the text")
    end_index: int = Field(..., description="Ending position in the text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of detection")
    replacement: str = Field(..., description="Suggested replacement text")


class PIIDetectionResponse(BaseModel):
    """Response containing detected PII entities."""

    entities: list[PIIEntity] = Field(..., description="List of detected PII entities")
    pii_types_found: list[str] = Field(..., description="Unique types of PII found")
    total_pii_count: int = Field(..., description="Total number of PII instances found")
    risk_level: Literal["low", "medium", "high", "critical"] = Field(..., description="Overall risk level")


class ScrubbedTextResponse(BaseModel):
    """Response containing scrubbed text and metadata."""

    original_text: str = Field(..., description="Original text before scrubbing")
    scrubbed_text: str = Field(..., description="Text with PII removed or masked")
    entities_removed: list[PIIEntity] = Field(..., description="List of PII entities that were removed")
    scrubbing_method: str = Field(..., description="Method used for scrubbing")
    reversible: bool = Field(..., description="Whether the scrubbing can be reversed")
    mapping: dict[str, str] | None = Field(default=None, description="Mapping of original to scrubbed values if reversible")


# Regex patterns for common PII
PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone_us": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
    "ssn": r'\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b',
    "credit_card": r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b',
    "ip_address": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
    "date_of_birth": r'\b(?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12][0-9]|3[01])[-/](?:19|20)\d{2}\b',
}


# Tool for regex-based PII detection
@trace()
async def detect_pii_regex(text: str) -> list[PIIEntity]:
    """
    Detect PII using regex patterns.

    Args:
        text: Text to scan for PII

    Returns:
        List of detected PII entities
    """
    entities = []

    for pii_type, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, text):
            entities.append(
                PIIEntity(
                    text=match.group(),
                    entity_type=pii_type,
                    start_index=match.start(),
                    end_index=match.end(),
                    confidence=0.9,  # High confidence for regex matches
                    replacement=f"[{pii_type.upper()}]",
                )
            )

    return entities


# Step 1: Detect PII using LLM
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=PIIDetectionResponse,
)
@prompt_template(
    """
    You are a privacy expert specializing in detecting Personally Identifiable Information (PII).

    Analyze the following text and identify ALL instances of PII:

    Text to analyze:
    "{text}"

    Look for these types of PII:
    1. Names (first, last, full names)
    2. Email addresses
    3. Phone numbers (various formats)
    4. Social Security Numbers (SSN)
    5. Credit card numbers
    6. Physical addresses
    7. Date of birth
    8. Driver's license numbers
    9. Passport numbers
    10. Bank account numbers
    11. Medical record numbers
    12. IP addresses
    13. Vehicle identification numbers (VIN)
    14. Biometric data references
    15. Any other identifying information

    For each PII instance found:
    - Identify the exact text
    - Classify its type
    - Determine confidence level (0.0-1.0)
    - Suggest an appropriate replacement
    - Note its position in the text

    Assess the overall risk level based on:
    - Quantity of PII found
    - Sensitivity of PII types
    - Potential for identity theft or privacy breach
    """
)
async def detect_pii_llm(text: str):
    """Detect PII using LLM analysis."""
    pass


# Step 2: Scrub PII from text
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=ScrubbedTextResponse,
)
@prompt_template(
    """
    You are a privacy expert tasked with removing PII from text.

    Original text:
    "{text}"

    Detected PII entities:
    {entities}

    Scrubbing method: {method}
    Options:
    - "mask": Replace with generic placeholders (e.g., [EMAIL], [PHONE])
    - "redact": Replace with asterisks or similar characters
    - "generalize": Replace with less specific information
    - "synthetic": Replace with realistic but fake data

    Requirements:
    1. Remove or mask ALL identified PII
    2. Maintain text readability and structure
    3. Preserve non-PII content exactly
    4. Keep the context meaningful where possible
    5. If using synthetic data, make it realistic but clearly not real

    Return the scrubbed text along with details about what was removed.
    """
)
async def scrub_pii(text: str, entities: str, method: str):
    """Scrub PII from text using specified method."""
    pass


# Main PII scrubbing function
@trace()
async def scrub_pii_from_text(
    text: str,
    detection_method: Literal["llm", "regex", "hybrid"] = "hybrid",
    scrubbing_method: Literal["mask", "redact", "generalize", "synthetic"] = "mask",
    pii_types_to_detect: list[str] | None = None,
    custom_patterns: dict[str, str] | None = None,
    confidence_threshold: float = 0.7,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
) -> ScrubbedTextResponse:
    """
    Detect and remove PII from text.

    This agent combines regex patterns and LLM analysis to detect PII,
    then removes or masks it according to the specified method.

    Args:
        text: Text to scrub
        detection_method: Method for detecting PII
        scrubbing_method: Method for removing/masking PII
        pii_types_to_detect: Specific PII types to look for
        custom_patterns: Additional regex patterns to use
        confidence_threshold: Minimum confidence for PII detection
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        ScrubbedTextResponse with cleaned text and metadata
    """
    all_entities = []

    # Step 1: Detect PII using specified method
    if detection_method in ["regex", "hybrid"]:
        # Use regex detection
        regex_entities = await detect_pii_regex(text)
        all_entities.extend(regex_entities)

    if detection_method in ["llm", "hybrid"]:
        # Use LLM detection
        llm_response = await detect_pii_llm(text)
        all_entities.extend(llm_response.entities)

    # Remove duplicates and filter by confidence
    unique_entities = []
    seen_positions = set()

    for entity in all_entities:
        if entity.confidence >= confidence_threshold:
            pos_key = (entity.start_index, entity.end_index)
            if pos_key not in seen_positions:
                seen_positions.add(pos_key)
                unique_entities.append(entity)

    # Sort entities by position for proper replacement
    unique_entities.sort(key=lambda e: e.start_index)

    # Step 2: Scrub the PII
    if unique_entities:
        entities_str = "\n".join(
            [f"- {e.entity_type}: '{e.text}' at position {e.start_index}-{e.end_index}" for e in unique_entities]
        )

        scrubbed_response = await scrub_pii(text=text, entities=entities_str, method=scrubbing_method)

        return scrubbed_response
    else:
        # No PII found
        return ScrubbedTextResponse(
            original_text=text,
            scrubbed_text=text,
            entities_removed=[],
            scrubbing_method=scrubbing_method,
            reversible=False,
            mapping=None,
        )


# Convenience functions
async def quick_scrub(text: str) -> str:
    """
    Quick PII scrubbing with default settings.

    Returns just the scrubbed text.
    """
    result = await scrub_pii_from_text(text)
    return result.scrubbed_text


async def detect_pii_only(text: str, method: Literal["llm", "regex", "hybrid"] = "hybrid") -> dict[str, Any]:
    """
    Only detect PII without scrubbing.

    Returns a simplified dictionary with detection results.
    """
    result = await scrub_pii_from_text(
        text=text,
        detection_method=method,
        scrubbing_method="mask",  # Won't be used
    )

    return {
        "pii_found": len(result.entities_removed) > 0,
        "pii_count": len(result.entities_removed),
        "pii_types": list(set(e.entity_type for e in result.entities_removed)),
        "entities": [{"text": e.text, "type": e.entity_type, "confidence": e.confidence} for e in result.entities_removed],
    }


async def scrub_with_mapping(
    text: str, scrubbing_method: Literal["mask", "synthetic"] = "synthetic"
) -> tuple[str, dict[str, str]]:
    """
    Scrub PII and return mapping for potential reversal.

    Returns tuple of (scrubbed_text, mapping_dict).
    """
    result = await scrub_pii_from_text(text=text, scrubbing_method=scrubbing_method)

    return result.scrubbed_text, result.mapping or {}
