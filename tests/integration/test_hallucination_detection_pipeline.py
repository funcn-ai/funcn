"""Integration tests for hallucination detection agent pipeline.

Tests real-world scenarios where the hallucination detection agent
uses multiple tools to verify claims, extract facts, and identify
potential misinformation in AI-generated content.
"""

import asyncio
import pytest

# Import the actual hallucination detection functions
from packages.sygaldry_registry.components.agents.hallucination_detector.agent import (
    ClaimVerification,
    HallucinationDetectionResponse,
    detect_hallucinations,
    detect_hallucinations_quick,
    verify_single_statement,
)

# Import search tools used by the agent
from packages.sygaldry_registry.components.tools.exa_search.tool import (
    AnswerArgs as ExaAnswerArgs,
    SearchArgs as ExaSearchArgs,
    exa_answer,
    exa_search,
)
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch


class TestHallucinationDetectionPipeline:
    """Test hallucination detection agent with integrated fact-checking tools."""

    @pytest.mark.asyncio
    async def test_scientific_claim_verification_pipeline(self):
        """Test verifying scientific claims using multiple sources.

        Simulates checking a claim about a scientific discovery using
        academic sources, news articles, and official publications.
        """
        test_content = """
        Recent breakthrough: Scientists at MIT have developed a room-temperature
        superconductor using a graphene-based compound called GrapheneX-77.
        The material maintains superconductivity up to 25°C (77°F) at ambient pressure.
        This discovery could revolutionize energy transmission and quantum computing.
        """

        # Mock the Exa search responses for fact-checking
        with patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_search") as mock_search, \
             patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_answer") as mock_answer:

            # Mock search results - no real GrapheneX-77 exists
            mock_search.side_effect = [
                # First search for the superconductor claim
                {
                    "results": [
                        {
                            "title": "Room Temperature Superconductors: Current State",
                            "url": "https://physics.org/superconductors",
                            "published_date": "2024-01-15",
                            "text": "Despite many claims, no verified room-temperature superconductor at ambient pressure exists..."
                        },
                        {
                            "title": "MIT Research Updates",
                            "url": "https://mit.edu/research",
                            "published_date": "2024-01-20",
                            "text": "Current MIT superconductor research focuses on high-pressure systems..."
                        }
                    ],
                    "autoprompt_string": "MIT GrapheneX-77 room temperature superconductor"
                },
                # Second search for GrapheneX-77 specifically
                {
                    "results": [],  # No results found for this fictional material
                    "autoprompt_string": "GrapheneX-77 superconductor material"
                }
            ]

            # Mock answer for direct verification
            mock_answer.return_value = {
                "answer": "No verified room-temperature superconductor at ambient pressure has been discovered as of 2024.",
                "sources": ["https://nature.com/superconductors-review", "https://science.org/materials"]
            }

            # Run hallucination detection
            result = await detect_hallucinations(test_content)

            # Verify the detection worked correctly
            assert isinstance(result, HallucinationDetectionResponse)
            assert result.claims_extracted > 0  # Should extract claims about superconductor
            assert result.hallucination_score > 0.5  # Should detect as likely hallucination
            assert "refuted" in str(result.claims_verified).lower() or "insufficient" in str(result.claims_verified).lower()
            assert result.overall_assessment in ["mostly inaccurate", "highly inaccurate", "mixed accuracy"]

    @pytest.mark.asyncio
    async def test_news_event_verification_with_temporal_awareness(self):
        """Test verifying news claims with temporal context awareness."""
        test_content = """
        Breaking news: The United Nations announced today that global carbon emissions
        dropped by 15% in 2024, marking the largest single-year decrease in history.
        This achievement is attributed to widespread adoption of renewable energy.
        """

        with patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_search") as mock_search:
            # Mock search with temporal results
            mock_search.return_value = {
                "results": [
                    {
                        "title": "UN Climate Report 2024",
                        "url": "https://un.org/climate-2024",
                        "published_date": "2024-01-10",
                        "text": "Global emissions data for 2024 will be released in early 2025..."
                    },
                    {
                        "title": "Carbon Emissions Tracking",
                        "url": "https://climate.gov/emissions",
                        "published_date": "2023-12-20",
                        "text": "2023 saw a 2% reduction in global carbon emissions..."
                    }
                ],
                "autoprompt_string": "UN global carbon emissions 15% decrease 2024"
            }

            # Use quick check for simple true/false
            result = await detect_hallucinations_quick(test_content)

            # Should detect temporal impossibility (can't have full 2024 data yet)
            assert isinstance(result, dict)
            assert result["score"] > 0.3  # Some uncertainty due to temporal issue
            assert result["claims_checked"] > 0

    @pytest.mark.asyncio
    async def test_statistical_claim_verification_with_sources(self):
        """Test verifying statistical claims with proper source attribution."""
        test_claim = "According to the WHO, 1 in 4 people globally will experience mental health issues in their lifetime."

        with patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_search") as mock_search, \
             patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_answer") as mock_answer:

            # Mock finding supporting evidence
            mock_search.return_value = {
                "results": [
                    {
                        "title": "WHO Mental Health Statistics",
                        "url": "https://who.int/mental-health/stats",
                        "text": "WHO estimates that 1 in 4 people will be affected by mental health disorders at some point in their lives.",
                        "score": 0.95
                    }
                ],
                "autoprompt_string": "WHO 1 in 4 mental health statistics"
            }

            mock_answer.return_value = {
                "answer": "Yes, the WHO states that 1 in 4 people globally will experience mental health issues in their lifetime.",
                "sources": ["https://who.int/factsheets/mental-disorders"]
            }

            # Verify single statement
            verification = await verify_single_statement(test_claim)

            # Should be verified as accurate
            assert isinstance(verification, ClaimVerification)
            assert verification.assessment == "supported"
            assert verification.confidence_score > 0.8
            assert len(verification.supporting_sources) > 0
            assert "who.int" in str(verification.supporting_sources)

    @pytest.mark.asyncio
    async def test_multi_claim_document_verification(self):
        """Test verifying a document with multiple claims of varying accuracy."""
        test_document = """
        Technology Report 2024:

        1. Python is the most popular programming language according to Stack Overflow's 2023 survey.
        2. Quantum computers can now break all existing encryption methods.
        3. 5G networks have been deployed in over 100 countries worldwide.
        4. AI can perfectly predict stock market movements with 99% accuracy.
        5. Electric vehicle sales grew by approximately 35% globally in 2023.
        """

        # Mock different verification results for each claim
        search_responses = [
            # Claim 1: Python popularity (TRUE)
            {
                "results": [{
                    "title": "Stack Overflow Developer Survey 2023",
                    "url": "https://stackoverflow.com/survey/2023",
                    "text": "Python remains the most popular language for the 5th year..."
                }],
                "autoprompt_string": "Python most popular Stack Overflow 2023"
            },
            # Claim 2: Quantum breaking encryption (FALSE)
            {
                "results": [{
                    "title": "Quantum Computing and Cryptography",
                    "url": "https://crypto.org/quantum",
                    "text": "Current quantum computers cannot break modern encryption..."
                }],
                "autoprompt_string": "Quantum computers break encryption"
            },
            # Claim 3: 5G deployment (TRUE)
            {
                "results": [{
                    "title": "Global 5G Deployment Status",
                    "url": "https://gsma.com/5g-deployment",
                    "text": "5G networks operational in 105 countries as of 2024..."
                }],
                "autoprompt_string": "5G networks 100 countries deployment"
            },
            # Claim 4: AI stock prediction (FALSE)
            {
                "results": [{
                    "title": "AI in Financial Markets",
                    "url": "https://fintech.org/ai-trading",
                    "text": "No AI system can predict markets with such accuracy due to complexity..."
                }],
                "autoprompt_string": "AI predict stock market 99% accuracy"
            },
            # Claim 5: EV sales growth (TRUE)
            {
                "results": [{
                    "title": "Global EV Sales Report 2023",
                    "url": "https://ev-sales.org/2023",
                    "text": "Electric vehicle sales increased by 36% globally in 2023..."
                }],
                "autoprompt_string": "Electric vehicle sales growth 35% 2023"
            }
        ]

        with patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_search") as mock_search:
            mock_search.side_effect = search_responses

            # Run full hallucination detection
            result = await detect_hallucinations(test_document)

            # Verify mixed results
            assert result.claims_extracted >= 5
            assert 0.3 < result.hallucination_score < 0.6  # Mixed accuracy
            assert result.overall_assessment in ["mixed accuracy", "mostly accurate"]

            # Check that both supported and refuted claims exist
            verifications = result.claims_verified
            assert any(v.assessment == "supported" for v in verifications)
            assert any(v.assessment == "refuted" for v in verifications)

    @pytest.mark.asyncio
    async def test_realtime_fact_checking_with_retries(self):
        """Test real-time fact checking with network failures and retries."""
        test_statement = "The James Webb Space Telescope discovered water on exoplanet K2-18b."

        call_count = 0

        async def mock_search_with_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call fails
                raise Exception("Network timeout")
            # Second call succeeds
            return {
                "results": [{
                    "title": "JWST Discovers Water Vapor on K2-18b",
                    "url": "https://nasa.gov/jwst/k2-18b",
                    "text": "The James Webb Space Telescope detected water vapor in the atmosphere of K2-18b...",
                    "published_date": "2023-09-11"
                }],
                "autoprompt_string": "James Webb telescope water K2-18b"
            }

        with patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_search", side_effect=mock_search_with_failure):
            # The agent should handle the error gracefully
            result = await detect_hallucinations(test_statement)

            # Should still provide results despite initial failure
            assert result.claims_extracted > 0
            # Might show as insufficient evidence due to search failure
            # or supported if retry succeeded
            assert result.hallucination_score <= 0.5 or "insufficient_evidence" in str(result.claims_verified)

    @pytest.mark.asyncio
    async def test_comparative_claim_verification(self):
        """Test verifying comparative and superlative claims."""
        test_claims = """
        1. ChatGPT is the fastest-growing consumer application in history.
        2. Mount Everest is getting taller every year due to tectonic activity.
        3. The Pacific Ocean contains more plastic than all other oceans combined.
        """

        with patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_search") as mock_search, \
             patch("packages.sygaldry_registry.components.agents.hallucination_detector.agent.exa_answer") as mock_answer:

            # Mock comprehensive searches for comparative claims
            mock_search.side_effect = [
                # ChatGPT growth claim
                {
                    "results": [{
                        "title": "ChatGPT Growth Analysis",
                        "url": "https://techcrunch.com/chatgpt-growth",
                        "text": "ChatGPT reached 100 million users in 2 months, making it the fastest-growing consumer app...",
                        "score": 0.92
                    }],
                    "autoprompt_string": "ChatGPT fastest growing consumer application history"
                },
                # Mount Everest height
                {
                    "results": [{
                        "title": "Everest Height Changes",
                        "url": "https://geology.com/everest",
                        "text": "Mount Everest grows approximately 4mm per year due to tectonic plate movement...",
                        "score": 0.88
                    }],
                    "autoprompt_string": "Mount Everest growing taller tectonic activity"
                },
                # Pacific Ocean plastic
                {
                    "results": [{
                        "title": "Ocean Plastic Distribution",
                        "url": "https://oceanplastic.org/stats",
                        "text": "The Pacific hosts the largest concentration, but not more than all others combined...",
                        "score": 0.85
                    }],
                    "autoprompt_string": "Pacific Ocean plastic more than other oceans combined"
                }
            ]

            result = await detect_hallucinations(test_claims)

            # Should show mixed results
            assert result.claims_extracted >= 3
            assert len(result.claims_verified) >= 3
            # At least one claim (Pacific plastic) should be marked as refuted or needs clarification
            assert any(v.assessment in ["refuted", "insufficient_evidence"] for v in result.claims_verified)
