"""
Hallucination Detector Agent

An AI-powered agent that detects potential hallucinations in text by:
1. Extracting factual claims from the text
2. Verifying each claim using Exa's AI-powered search
3. Providing an overall assessment with confidence scores

Uses Exa's neural search capabilities to find supporting or refuting evidence
for each claim, helping identify potentially false or unsupported statements.
"""

from .agent import (
    ClaimVerification,
    # Response models
    ExtractedClaimsResponse,
    HallucinationDetectionResponse,
    analyze_hallucinations,
    detect_hallucinations,
    detect_hallucinations_quick,
    extract_claims,
    verify_claim,
    verify_single_statement,
)

__all__ = [
    "detect_hallucinations",
    "detect_hallucinations_quick",
    "verify_single_statement",
    "extract_claims",
    "verify_claim",
    "analyze_hallucinations",
    "ExtractedClaimsResponse",
    "ClaimVerification",
    "HallucinationDetectionResponse",
]
