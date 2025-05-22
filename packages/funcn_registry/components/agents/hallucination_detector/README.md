# Hallucination Detector Agent

An AI-powered agent that detects potential hallucinations in text by extracting factual claims and verifying them using Exa's neural search capabilities.

## Overview

The Hallucination Detector Agent helps identify potentially false or unsupported statements in text by:

1. **Extracting Claims**: Identifies factual claims that can be verified
2. **Searching for Evidence**: Uses Exa's AI-powered search to find relevant sources
3. **Verifying Claims**: Analyzes evidence to determine if claims are supported, refuted, or lack sufficient evidence
4. **Providing Scores**: Returns confidence scores and an overall hallucination score

## Prerequisites

- `EXA_API_KEY`: Required for Exa search functionality
- `OPENAI_API_KEY`: Required for LLM-based claim extraction and analysis

## Installation

```bash
# The agent is part of the funcn_registry
# Ensure you have the required dependencies:
pip install mirascope exa-py
```

## Usage

### Basic Hallucination Detection

```python
from hallucination_detector import detect_hallucinations

# Analyze text for potential hallucinations
text = """
The Eiffel Tower was built in 1889 in Paris, France. 
It stands at 330 meters tall and is made entirely of gold.
It was designed by Gustave Eiffel for the World's Fair.
"""

result = await detect_hallucinations(text)

print(f"Hallucination Score: {result.hallucination_score}")
print(f"Overall Assessment: {result.overall_assessment}")
print(f"Summary: {result.summary}")

# Detailed results for each claim
for verification in result.claims_verified:
    print(f"\nClaim: {verification.claim}")
    print(f"Assessment: {verification.assessment}")
    print(f"Confidence: {verification.confidence_score}")
    print(f"Supporting sources: {verification.supporting_sources}")
    print(f"Refuting sources: {verification.refuting_sources}")
```

### Quick Check

For a simpler interface:

```python
from hallucination_detector import detect_hallucinations_quick

quick_result = await detect_hallucinations_quick(text)

if quick_result["is_hallucinated"]:
    print(f"Warning: Text likely contains hallucinations! Score: {quick_result['score']}")
else:
    print(f"Text appears accurate. Score: {quick_result['score']}")
```

### Single Statement Verification

To verify individual statements:

```python
from hallucination_detector import verify_single_statement

verification = await verify_single_statement(
    "The speed of light is 299,792,458 meters per second."
)

print(f"Statement: {verification.claim}")
print(f"Assessment: {verification.assessment}")
print(f"Confidence: {verification.confidence_score}")
```

## Configuration Options

- `llm_provider`: LLM provider to use (default: "openai")
- `model`: Specific model to use (default: "gpt-4o-mini")
- `search_type`: Exa search type - "neural" or "keyword" (default: "neural")
- `max_sources_per_claim`: Maximum sources to search per claim (default: 5)

## Response Models

### HallucinationDetectionResponse

- `claims_extracted`: Total number of claims found
- `claims_verified`: List of ClaimVerification objects
- `overall_assessment`: Overall accuracy assessment
- `hallucination_score`: Score from 0 (no hallucinations) to 1 (all hallucinations)
- `summary`: Human-readable summary

### ClaimVerification

- `claim`: The claim being verified
- `assessment`: "supported", "refuted", or "insufficient_evidence"
- `confidence_score`: Confidence from 0 to 1
- `supporting_sources`: URLs supporting the claim
- `refuting_sources`: URLs refuting the claim
- `summary`: Brief evidence summary

## How It Works

1. **Claim Extraction**: Uses an LLM to identify verifiable factual claims in the text
2. **Evidence Search**: For each claim, searches for relevant sources using Exa's neural search
3. **Verification**: Analyzes the evidence to determine if claims are supported or refuted
4. **Scoring**: Calculates an overall hallucination score based on verification results

## Best Practices

- **Text Length**: Works best with texts containing clear factual claims
- **Search Quality**: Neural search provides better semantic understanding than keyword search
- **API Limits**: Be mindful of API rate limits when processing large texts
- **Error Handling**: The agent handles errors gracefully, marking failed verifications as "insufficient_evidence"

## Examples

### News Article Verification

```python
news_article = """
Recent studies show that drinking coffee can extend your lifespan by 50 years.
The research was conducted at Harvard University over a period of 100 years.
"""

result = await detect_hallucinations(news_article)
# Likely to flag the extreme claims as potential hallucinations
```

### Scientific Text Checking

```python
scientific_text = """
Water boils at 100°C at sea level atmospheric pressure.
The molecular formula of water is H2O.
"""

result = await detect_hallucinations(scientific_text)
# Should verify these well-established facts as supported
```

## Limitations

- Requires internet access for source verification
- Dependent on the quality of available online sources
- May struggle with very recent events not yet indexed
- Cannot verify claims about private or unpublished information

## Error Handling

The agent handles errors gracefully:

- Missing API keys return informative error messages
- Failed searches mark claims as "insufficient_evidence"
- Network errors are caught and reported in the verification summary 
