from __future__ import annotations

import json
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Optional

# Import Exa search tools
try:
    from exa_search_tools import AnswerArgs, ExaCategory, SearchArgs, exa_answer, exa_search
except ImportError:
    # Fallback imports for when tools aren't available yet
    ExaCategory = None
    SearchArgs = None
    exa_search = None
    exa_answer = None
    AnswerArgs = None


# Response models for structured outputs
class ExtractedClaim(BaseModel):
    """A single extracted claim from text."""
    claim: str = Field(..., description="A single, verifiable statement extracted from the text")


class ExtractedClaimsResponse(BaseModel):
    """Response containing all extracted claims."""
    claims: list[str] = Field(..., description="List of factual claims extracted from the text")


class ClaimVerification(BaseModel):
    """Verification result for a single claim."""
    claim: str = Field(..., description="The claim being verified")
    assessment: str = Field(..., description="Assessment: 'supported', 'refuted', or 'insufficient_evidence'")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    supporting_sources: list[str] = Field(default_factory=list, description="URLs of sources supporting the claim")
    refuting_sources: list[str] = Field(default_factory=list, description="URLs of sources refuting the claim")
    summary: str = Field(..., description="Brief summary of the evidence found")


class HallucinationDetectionResponse(BaseModel):
    """Complete hallucination detection response."""
    claims_extracted: int = Field(..., description="Total number of claims extracted")
    claims_verified: list[ClaimVerification] = Field(..., description="Verification results for each claim")
    overall_assessment: str = Field(..., description="Overall assessment of the text's accuracy")
    hallucination_score: float = Field(..., ge=0.0, le=1.0, description="Overall hallucination score (0=no hallucinations, 1=all hallucinations)")
    summary: str = Field(..., description="Summary of the hallucination detection results")


# Step 1: Extract claims from text
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=ExtractedClaimsResponse,
)
@prompt_template(
    """
    You are an expert at extracting claims from text.
    Your task is to identify and list all claims present, true or false,
    in the given text. Each claim should be a single, verifiable statement.

    Focus on factual claims that can be verified against external sources.
    Exclude opinions, subjective statements, or claims about future predictions.

    Text to analyze:
    {text}
    """
)
async def extract_claims(text: str):
    """Extract factual claims from the text using an LLM."""
    pass


# Step 2: Search for evidence and verify a single claim
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=ClaimVerification,
    tools=[exa_search, exa_answer] if exa_search else [],
)
@prompt_template(
    """
    You are an expert fact-checker. Your task is to verify the following claim
    by searching for evidence using Exa's AI-powered search.

    Claim to verify: "{claim}"

    Instructions:
    1. First, use exa_search to find relevant sources about this claim
       - Use neural search for semantic understanding
       - Search for multiple perspectives
       - Look for authoritative sources

    2. If needed, use exa_answer to get direct answers about specific aspects

    3. Analyze the evidence to determine if the claim is:
       - "supported": Multiple reliable sources confirm the claim
       - "refuted": Multiple reliable sources contradict the claim
       - "insufficient_evidence": Not enough reliable information found

    4. Provide a confidence score (0.0 to 1.0) based on:
       - Number of sources found
       - Quality and authority of sources
       - Consistency of information across sources

    5. List supporting and refuting source URLs separately

    6. Provide a brief summary of the evidence found
    """
)
async def verify_claim(claim: str):
    """Verify a single claim using Exa search."""
    pass


# Step 3: Main hallucination detector
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=HallucinationDetectionResponse,
)
@prompt_template(
    """
    You are analyzing the results of a hallucination detection process.

    Original text analyzed:
    {original_text}

    Verification results for each claim:
    {verification_results}

    Based on these results:
    1. Count the total number of claims extracted
    2. Analyze the verification results
    3. Provide an overall assessment:
       - "highly accurate": Most claims are supported (>80%)
       - "mostly accurate": Majority of claims are supported (60-80%)
       - "mixed accuracy": Roughly equal supported and refuted claims (40-60%)
       - "mostly inaccurate": Majority of claims are refuted (20-40%)
       - "highly inaccurate": Most claims are refuted (<20%)

    4. Calculate a hallucination score:
       - 0.0 = No hallucinations detected
       - 1.0 = All claims are hallucinations
       - Score = (refuted_claims + 0.5 * insufficient_evidence_claims) / total_claims

    5. Provide a summary of the findings
    """
)
async def analyze_hallucinations(
    original_text: str,
    verification_results: str
):
    """Analyze the overall hallucination detection results."""
    pass


async def detect_hallucinations(
    text: str,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini",
    search_type: str = "neural",
    max_sources_per_claim: int = 5
) -> HallucinationDetectionResponse:
    """
    Detect potential hallucinations in text by fact-checking claims.

    This agent extracts factual claims from the input text and verifies
    each claim using Exa's AI-powered search to find supporting or
    refuting evidence.

    Args:
        text: The text to analyze for hallucinations
        llm_provider: LLM provider to use
        model: Specific model to use
        search_type: Exa search type ('neural' or 'keyword')
        max_sources_per_claim: Maximum sources to search per claim

    Returns:
        HallucinationDetectionResponse with detailed verification results
    """
    # Step 1: Extract claims
    claims_response = await extract_claims(text)
    claims = claims_response.claims

    if not claims:
        return HallucinationDetectionResponse(
            claims_extracted=0,
            claims_verified=[],
            overall_assessment="no claims found",
            hallucination_score=0.0,
            summary="No verifiable claims were found in the text."
        )

    # Step 2: Verify each claim
    verification_results = []
    for claim in claims:
        try:
            verification = await verify_claim(claim)
            verification_results.append(verification)
        except Exception as e:
            # Handle errors gracefully
            verification_results.append(ClaimVerification(
                claim=claim,
                assessment="insufficient_evidence",
                confidence_score=0.0,
                supporting_sources=[],
                refuting_sources=[],
                summary=f"Error during verification: {str(e)}"
            ))

    # Step 3: Analyze overall results
    verification_json = json.dumps([v.model_dump() for v in verification_results], indent=2)
    final_analysis = await analyze_hallucinations(
        original_text=text,
        verification_results=verification_json
    )

    return final_analysis


# Convenience functions for common use cases
async def detect_hallucinations_quick(text: str) -> dict[str, Any]:
    """
    Quick hallucination check returning a simple dictionary result.

    Returns a dictionary with:
    - is_hallucinated: bool
    - score: float (0-1)
    - summary: str
    """
    result = await detect_hallucinations(text)

    return {
        "is_hallucinated": result.hallucination_score > 0.5,
        "score": result.hallucination_score,
        "summary": result.summary,
        "claims_checked": result.claims_extracted
    }


async def verify_single_statement(statement: str) -> ClaimVerification:
    """
    Verify a single statement without the full hallucination detection pipeline.

    Useful for checking individual facts or claims.
    """
    return await verify_claim(statement)
