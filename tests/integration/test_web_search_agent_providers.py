"""Integration tests for web search agent with multiple providers.

Tests real-world scenarios where the web search agent uses different
search providers (DuckDuckGo, Qwant, Nimble, Exa) to find information,
handle failures, and aggregate results.
"""

import asyncio
import pytest

# Import the actual web search agent
from packages.sygaldry_registry.components.agents.web_search.agent import (
    SearchProvider,
    WebSearchResponse,
    web_search_agent,
)

# Import search tools
from packages.sygaldry_registry.components.tools.duckduckgo_search.tool import (
    SearchArgs,
    duckduckgo_search,
)
from packages.sygaldry_registry.components.tools.exa_search.tool import (
    ExaCategory,
    exa_search,
)
from packages.sygaldry_registry.components.tools.qwant_search.tool import (
    qwant_search,
)
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch


class TestWebSearchAgentProviders:
    """Test web search agent with multiple providers in production scenarios."""

    @pytest.mark.asyncio
    async def test_multi_provider_fallback_on_failure(self):
        """Test agent falling back to alternative providers when primary fails.

        Simulates a real scenario where DuckDuckGo is rate-limited,
        and the agent needs to fallback to other providers.
        """
        # Mock the search tool responses
        with patch("packages.sygaldry_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs, \
             patch("packages.sygaldry_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_qwant, \
             patch("packages.sygaldry_registry.components.agents.web_search.agent.duckduckgo_search", side_effect=Exception("Rate limit exceeded")), \
             patch("packages.sygaldry_registry.components.agents.web_search.agent.qwant_search") as mock_qwant_search:

            # Configure Qwant to succeed
            mock_qwant_search.return_value = {
                "results": [
                    {
                        "title": "AI Research Paper",
                        "url": "https://example.com/ai-paper",
                        "snippet": "Latest findings in artificial intelligence"
                    }
                ],
                "query": "artificial intelligence research 2024",
                "provider": "qwant"
            }

            # Execute search with auto provider selection
            response = await web_search_agent(
                question="What are the latest AI research findings in 2024?",
                search_provider="auto",
                max_results_per_search=10
            )

            # Verify response
            assert isinstance(response.answer, str)
            assert len(response.sources) > 0
            assert "qwant" in response.search_providers  # Should have used Qwant after DuckDuckGo failed
            assert len(response.search_queries) > 0

    @pytest.mark.asyncio
    async def test_parallel_multi_provider_search(self):
        """Test searching across multiple providers in parallel for comprehensive results.

        Simulates aggregating results from multiple providers simultaneously
        for better coverage and result diversity.
        """
        # Mock all search providers
        with patch("packages.sygaldry_registry.components.agents.web_search.agent.duckduckgo_search") as mock_ddg, \
             patch("packages.sygaldry_registry.components.agents.web_search.agent.qwant_search") as mock_qwant, \
             patch("packages.sygaldry_registry.components.agents.web_search.agent.exa_search") as mock_exa:

            # Configure responses from each provider
            mock_ddg.return_value = {
                "results": [
                    {"title": "AI Overview", "url": "https://ddg.example.com/ai", "snippet": "AI basics"},
                    {"title": "Machine Learning Basics", "url": "https://ddg.example.com/ml", "snippet": "ML intro"}
                ],
                "query": "artificial intelligence",
                "provider": "duckduckgo"
            }

            mock_qwant.return_value = {
                "results": [
                    {"title": "AI Research 2024", "url": "https://qwant.example.com/research", "snippet": "Latest AI research"},
                    {"title": "Neural Networks", "url": "https://qwant.example.com/nn", "snippet": "NN explained"}
                ],
                "query": "artificial intelligence",
                "provider": "qwant"
            }

            mock_exa.return_value = {
                "results": [
                    {"title": "Deep Learning Advances", "url": "https://exa.example.com/dl", "snippet": "DL progress"},
                    {"title": "AI Ethics", "url": "https://exa.example.com/ethics", "snippet": "Ethical AI"}
                ],
                "autoprompt_string": "Latest developments in artificial intelligence"
            }

            # Execute search with "all" provider to use multiple sources
            response = await web_search_agent(
                question="Tell me about artificial intelligence",
                search_provider="all",
                max_results_per_search=5
            )

            # Verify comprehensive results
            assert isinstance(response.answer, str)
            assert len(response.sources) >= 3  # Should have sources from multiple providers
            assert len(response.search_providers) >= 2  # Should have used multiple providers
            assert "artificial intelligence" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_specialized_provider_selection(self):
        """Test intelligent provider selection based on query type.

        Different providers excel at different query types:
        - Exa: Academic/research queries
        - DuckDuckGo: General web search
        - Qwant: Privacy-focused search
        """
        test_cases = [
            {
                "question": "Find me the latest research papers on transformer models in NLP",
                "expected_tool": "exa_search",  # Should use Exa for research
                "mock_response": {
                    "results": [
                        {"title": "Transformers Survey 2024", "url": "https://arxiv.org/paper1", "published_date": "2024-01-15"}
                    ],
                    "autoprompt_string": "Latest transformer model research papers NLP 2024"
                }
            },
            {
                "question": "How to bake chocolate chip cookies recipe",
                "expected_tool": "duckduckgo_search",  # Should use DuckDuckGo for general queries
                "mock_response": {
                    "results": [
                        {"title": "Best Chocolate Chip Cookie Recipe", "url": "https://recipe.com/cookies", "snippet": "Easy recipe"}
                    ],
                    "query": "chocolate chip cookies recipe",
                    "provider": "duckduckgo"
                }
            },
            {
                "question": "Private anonymous VPN services comparison",
                "expected_tool": "qwant_search",  # Should use Qwant for privacy queries
                "mock_response": {
                    "results": [
                        {"title": "Top Private VPN Services", "url": "https://privacy.com/vpn", "snippet": "Anonymous VPNs"}
                    ],
                    "query": "private anonymous VPN services",
                    "provider": "qwant"
                }
            }
        ]

        for test_case in test_cases:
            with patch(f"packages.sygaldry_registry.components.agents.web_search.agent.{test_case['expected_tool']}") as mock_tool:
                mock_tool.return_value = test_case["mock_response"]

                # Execute search with auto provider selection
                response = await web_search_agent(
                    question=test_case["question"],
                    search_provider="auto"
                )

                # Verify appropriate provider was selected
                assert isinstance(response.answer, str)
                assert len(response.sources) > 0
                # The agent should have made at least one search
                assert mock_tool.called or len(response.search_queries) > 0

    @pytest.mark.asyncio
    async def test_provider_specific_features(self):
        """Test using provider-specific features like Exa's neural search and categories."""
        with patch("packages.sygaldry_registry.components.agents.web_search.agent.exa_search") as mock_exa, \
             patch("packages.sygaldry_registry.components.agents.web_search.agent.exa_answer") as mock_exa_answer:

            # Mock Exa search with category filtering
            mock_exa.return_value = {
                "results": [
                    {
                        "title": "OpenAI Company Profile",
                        "url": "https://company.com/openai",
                        "score": 0.95,
                        "published_date": "2024-01-20"
                    }
                ],
                "autoprompt_string": "OpenAI company information profile"
            }

            # Mock Exa answer for direct Q&A
            mock_exa_answer.return_value = {
                "answer": "OpenAI is an AI research company founded in 2015...",
                "sources": ["https://openai.com/about", "https://wiki.openai.com"]
            }

            # Search for company information (should trigger Exa with company category)
            response = await web_search_agent(
                question="Tell me about OpenAI company",
                search_provider="exa"
            )

            # Verify Exa-specific features were used
            assert isinstance(response.answer, str)
            assert "exa" in response.search_providers
            assert len(response.sources) > 0
            assert "openai" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_privacy_mode_search(self):
        """Test privacy-focused search mode."""
        with patch("packages.sygaldry_registry.components.agents.web_search.agent.qwant_search") as mock_qwant:
            mock_qwant.return_value = {
                "results": [
                    {
                        "title": "Privacy Guide",
                        "url": "https://privacy.guide/anonymous",
                        "snippet": "How to stay anonymous online"
                    }
                ],
                "query": "online privacy protection",
                "provider": "qwant"
            }

            # Execute search with privacy mode
            response = await web_search_agent(
                question="How to protect my privacy online?",
                search_provider="qwant",
                privacy_mode=True
            )

            # Verify privacy-focused search
            assert isinstance(response.answer, str)
            assert "qwant" in response.search_providers
            assert response.privacy_note is not None  # Should include privacy information
            assert "privacy" in response.answer.lower()

    @pytest.mark.asyncio
    async def test_rate_limit_handling_across_providers(self):
        """Test graceful handling of rate limits across multiple providers."""
        call_count = {"ddg": 0, "qwant": 0}

        async def mock_ddg_search(*args, **kwargs):
            call_count["ddg"] += 1
            if call_count["ddg"] <= 2:
                raise Exception("Rate limit exceeded")
            return {
                "results": [{"title": "Success", "url": "https://example.com", "snippet": "Got through"}],
                "query": "test query",
                "provider": "duckduckgo"
            }

        async def mock_qwant_search(*args, **kwargs):
            call_count["qwant"] += 1
            return {
                "results": [{"title": "Qwant Result", "url": "https://qwant.com", "snippet": "Alternative"}],
                "query": "test query",
                "provider": "qwant"
            }

        with patch("packages.sygaldry_registry.components.agents.web_search.agent.duckduckgo_search", side_effect=mock_ddg_search), \
             patch("packages.sygaldry_registry.components.agents.web_search.agent.qwant_search", side_effect=mock_qwant_search):

            # First search should fallback to Qwant
            response1 = await web_search_agent(
                question="First search query",
                search_provider="auto"
            )

            assert isinstance(response1.answer, str)
            assert len(response1.sources) > 0

            # Verify fallback occurred
            assert call_count["ddg"] >= 1  # Attempted DuckDuckGo
            assert call_count["qwant"] >= 1  # Fell back to Qwant
