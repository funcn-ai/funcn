"""Test suite for exa_search_tools following best practices."""

import asyncio
import os
import pytest
from datetime import datetime, timedelta

# Import the actual tool functions and models
from packages.sygaldry_registry.components.tools.exa_search.tool import (
    AnswerArgs,
    AnswerCitation,
    AnswerResponse,
    ExaCategory,
    FindSimilarArgs,
    SearchArgs,
    SearchResponse,
    SearchResult,
    exa_answer,
    exa_find_similar,
    exa_search,
)
from pathlib import Path
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import MagicMock, Mock, patch


class TestExaSearchTools(BaseToolTest):
    """Test exa_search_tools component."""

    component_name = "exa_search_tools"
    component_path = Path("packages/sygaldry_registry/components/tools/exa_search")

    def get_component_function(self):
        """Import the tool function."""
        return exa_search

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            SearchArgs(
                query="latest AI research papers",
                max_results=5,
                search_type="neural",
                category=ExaCategory.RESEARCH_PAPER
            ),
            SearchArgs(
                query="machine learning tutorials",
                max_results=10,
                start_published_date="2024-01-01",
                include_domains=["arxiv.org", "openai.com"]
            ),
            SearchArgs(
                query="quantum computing breakthroughs",
                max_results=3,
                exclude_domains=["wikipedia.org"]
            )
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, SearchResponse)
        assert isinstance(output.results, list)
        assert len(output.results) <= input_data.max_results
        assert output.query == input_data.query
        assert output.provider == "exa"

        for result in output.results:
            assert isinstance(result, SearchResult)
            assert result.title is not None
            assert result.url is not None

    @pytest.mark.asyncio
    async def test_basic_exa_search(self):
        """Test basic Exa search functionality."""
        tool = self.get_component_function()

        # Set API key for test
        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                # Mock Exa client
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title="AI Research Paper",
                        url="https://arxiv.org/paper1",
                        text="Abstract of the paper",
                        published_date="2024-01-15",
                        author="Dr. Smith",
                        score=0.95
                    ),
                    Mock(
                        title="Machine Learning Study",
                        url="https://research.com/study",
                        text="Study findings",
                        published_date="2024-02-01",
                        author="Prof. Johnson",
                        score=0.88
                    )
                ]
                mock_results.autoprompt_string = "Enhanced query: AI research papers 2024"
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(query="AI research", max_results=5)
                response = await tool(args)

                assert isinstance(response, SearchResponse)
                assert len(response.results) == 2
                assert response.query == "AI research"
                assert response.provider == "exa"
                assert response.autoprompt_string == "Enhanced query: AI research papers 2024"

                # Check first result
                assert response.results[0].title == "AI Research Paper"
                assert response.results[0].url == "https://arxiv.org/paper1"
                assert response.results[0].snippet == "Abstract of the paper"
                assert response.results[0].score == 0.95

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        """Test handling when API key is missing."""
        tool = self.get_component_function()

        # Ensure no API key is set
        with patch.dict(os.environ, {"EXA_API_KEY": ""}, clear=True):
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)

            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "API Key Missing" in response.results[0].title
            assert "EXA_API_KEY environment variable is required" in response.results[0].snippet

    @pytest.mark.asyncio
    async def test_search_with_category(self):
        """Test search with category filtering."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title="Research Paper on AI",
                        url="https://research.com/paper",
                        text="Academic paper content",
                        published_date="2024-03-01",
                        author="Academic Author",
                        score=0.92
                    )
                ]
                mock_results.autoprompt_string = None
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(
                    query="artificial intelligence",
                    max_results=5,
                    category=ExaCategory.RESEARCH_PAPER
                )
                response = await tool(args)

                # Verify category was passed to search
                mock_client.search.assert_called_once()
                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["category"] == "research paper"

    @pytest.mark.asyncio
    async def test_search_with_date_filters(self):
        """Test search with date range filters."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title="Recent Article",
                        url="https://news.com/article",
                        text="Article content",
                        published_date="2024-06-15",
                        author=None,
                        score=0.85
                    )
                ]
                mock_results.autoprompt_string = None
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(
                    query="AI news",
                    start_published_date="2024-01-01",
                    end_published_date="2024-12-31"
                )
                response = await tool(args)

                # Verify date parameters were passed
                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["start_published_date"] == "2024-01-01"
                assert call_kwargs["end_published_date"] == "2024-12-31"

    @pytest.mark.asyncio
    async def test_domain_filtering(self):
        """Test include/exclude domain filtering."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title="ArXiv Paper",
                        url="https://arxiv.org/paper123",
                        text="Paper abstract",
                        published_date=None,
                        author=None,
                        score=0.91
                    )
                ]
                mock_results.autoprompt_string = None
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(
                    query="research papers",
                    include_domains=["arxiv.org", "nature.com"],
                    exclude_domains=["medium.com", "reddit.com"]
                )
                response = await tool(args)

                # Verify domain filters were applied
                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["include_domains"] == ["arxiv.org", "nature.com"]
                assert call_kwargs["exclude_domains"] == ["medium.com", "reddit.com"]

    @pytest.mark.asyncio
    async def test_search_types(self):
        """Test different search types (auto, keyword, neural)."""
        tool = self.get_component_function()

        search_types = ["auto", "keyword", "neural"]

        for search_type in search_types:
            with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_results = Mock()
                    mock_results.results = [
                        Mock(
                            title=f"{search_type} search result",
                            url="https://example.com",
                            text="Content",
                            published_date=None,
                            author=None,
                            score=0.88
                        )
                    ]
                    mock_results.autoprompt_string = None
                    mock_client.search.return_value = mock_results
                    mock_exa.return_value = mock_client

                    args = SearchArgs(query="test query", search_type=search_type)
                    response = await tool(args)

                    # Verify search type was passed (auto is converted to None)
                    call_kwargs = mock_client.search.call_args[1]
                    expected_type = None if search_type == "auto" else search_type
                    assert call_kwargs["type"] == expected_type

    @pytest.mark.asyncio
    async def test_find_similar_functionality(self):
        """Test find similar pages functionality."""
        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title="Similar Article 1",
                        url="https://similar1.com",
                        text="",
                        published_date="2024-01-10",
                        author="Author 1",
                        score=0.92
                    ),
                    Mock(
                        title="Similar Article 2",
                        url="https://similar2.com",
                        text="",
                        published_date="2024-01-15",
                        author="Author 2",
                        score=0.88
                    )
                ]
                mock_results.autoprompt_string = "Finding similar content"
                mock_client.find_similar.return_value = mock_results
                mock_exa.return_value = mock_client

                args = FindSimilarArgs(
                    url="https://example.com/article",
                    max_results=5,
                    exclude_source_domain=True
                )
                response = await exa_find_similar(args)

                assert isinstance(response, SearchResponse)
                assert len(response.results) == 2
                assert response.query == "Similar to: https://example.com/article"
                assert response.provider == "exa"

                # Verify parameters
                call_kwargs = mock_client.find_similar.call_args[1]
                assert call_kwargs["url"] == "https://example.com/article"
                assert call_kwargs["exclude_source_domain"] is True

    @pytest.mark.asyncio
    async def test_answer_functionality(self):
        """Test direct Q&A functionality."""
        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_answer_result = Mock()
                mock_answer_result.answer = "The capital of France is Paris."
                mock_answer_result.citations = [
                    Mock(
                        url="https://source1.com",
                        title="Geography Facts",
                        published_date="2024-01-01",
                        author="Geo Expert",
                        text="Paris is the capital city of France..."
                    ),
                    Mock(
                        url="https://source2.com",
                        title="World Capitals",
                        published_date="2024-02-01",
                        author=None,
                        text="France's capital is Paris..."
                    )
                ]
                mock_client.answer.return_value = mock_answer_result
                mock_exa.return_value = mock_client

                args = AnswerArgs(
                    query="What is the capital of France?",
                    include_citations=True
                )
                response = await exa_answer(args)

                assert isinstance(response, AnswerResponse)
                assert response.answer == "The capital of France is Paris."
                assert len(response.citations) == 2
                assert response.query == "What is the capital of France?"
                assert response.provider == "exa"

                # Check citations
                assert response.citations[0].url == "https://source1.com"
                assert response.citations[0].title == "Geography Facts"
                assert response.citations[1].author is None

    @pytest.mark.asyncio
    async def test_handles_api_errors(self):
        """Test handling of Exa API errors."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_client.search.side_effect = Exception("API rate limit exceeded")
                mock_exa.return_value = mock_client

                args = SearchArgs(query="test query")
                response = await tool(args)

                assert isinstance(response, SearchResponse)
                assert len(response.results) == 1
                assert "Search Error for: test query" in response.results[0].title
                assert "API rate limit exceeded" in response.results[0].snippet

    @pytest.mark.asyncio
    async def test_empty_results_handling(self):
        """Test handling when no results are found."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = []
                mock_results.autoprompt_string = None
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(query="extremely obscure query xyz789")
                response = await tool(args)

                assert response.results == []
                assert response.query == "extremely obscure query xyz789"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("max_results", [1, 5, 10, 20])
    async def test_result_limits(self, max_results):
        """Test that max_results parameter is respected."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                # Create exactly the requested number of results
                mock_results.results = [
                    Mock(
                        title=f"Result {i}",
                        url=f"https://example.com/{i}",
                        text=f"Content {i}",
                        published_date=None,
                        author=None,
                        score=0.9 - (i * 0.01)
                    )
                    for i in range(max_results)
                ]
                mock_results.autoprompt_string = None
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(query="test query", max_results=max_results)
                response = await tool(args)

                assert len(response.results) == max_results
                # Verify num_results parameter was passed
                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["num_results"] == max_results

    @pytest.mark.asyncio
    async def test_missing_fields_handling(self):
        """Test handling of missing fields in results."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                # Results with various missing fields
                mock_results.results = [
                    Mock(
                        title=None,  # Missing title
                        url="https://notitle.com",
                        text="Content",
                        published_date=None,
                        author=None,
                        score=None
                    ),
                    Mock(
                        title="Has Title",
                        url="https://example.com",
                        text=None,  # Missing text
                        published_date="2024-01-01",
                        author="Author",
                        score=0.85
                    )
                ]
                mock_results.autoprompt_string = None
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(query="test query")
                response = await tool(args)

                assert len(response.results) == 2
                assert response.results[0].title == ""  # None converted to empty string
                assert response.results[0].snippet == "Content"
                assert response.results[1].snippet == ""  # Missing text handled by getattr in tool

    @pytest.mark.asyncio
    async def test_concurrent_searches(self):
        """Test multiple concurrent searches."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                call_count = 0

                def create_client():
                    nonlocal call_count
                    call_count += 1
                    client = Mock()
                    results = Mock()
                    results.results = [
                        Mock(
                            title=f"Concurrent Result {call_count}",
                            url=f"https://example.com/{call_count}",
                            text=f"Content {call_count}",
                            published_date=None,
                            author=None,
                            score=0.9
                        )
                    ]
                    results.autoprompt_string = None
                    client.search.return_value = results
                    return client

                mock_exa.side_effect = create_client

                # Run multiple searches concurrently
                queries = ["query1", "query2", "query3", "query4", "query5"]
                tasks = [tool(SearchArgs(query=q, max_results=3)) for q in queries]

                responses = await asyncio.gather(*tasks)

                # All should succeed
                assert len(responses) == 5
                for i, response in enumerate(responses):
                    assert isinstance(response, SearchResponse)
                    assert response.query == queries[i]
                    assert len(response.results) > 0

    @pytest.mark.asyncio
    async def test_special_characters_in_query(self):
        """Test queries with special characters."""
        tool = self.get_component_function()

        special_queries = [
            "C++ programming tutorials",
            "email@example.com search",
            "price: $100-$200",
            "AI & Machine Learning",
            '"exact phrase search"',
            "café résumé unicode"
        ]

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            for query in special_queries:
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_results = Mock()
                    mock_results.results = [
                        Mock(
                            title=f"Result for {query}",
                            url="https://example.com",
                            text="Content",
                            published_date=None,
                            author=None,
                            score=0.9
                        )
                    ]
                    mock_results.autoprompt_string = None
                    mock_client.search.return_value = mock_results
                    mock_exa.return_value = mock_client

                    args = SearchArgs(query=query)
                    response = await tool(args)

                    assert isinstance(response, SearchResponse)
                    assert response.query == query

    @pytest.mark.asyncio
    async def test_category_with_find_similar(self):
        """Test find similar with category filtering."""
        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title="Similar Research Paper",
                        url="https://arxiv.org/similar",
                        text="",
                        published_date="2024-03-01",
                        author="Dr. Similar",
                        score=0.89
                    )
                ]
                mock_results.autoprompt_string = None
                mock_client.find_similar.return_value = mock_results
                mock_exa.return_value = mock_client

                args = FindSimilarArgs(
                    url="https://example.com/paper",
                    category=ExaCategory.RESEARCH_PAPER,
                    max_results=5
                )
                response = await exa_find_similar(args)

                # Verify category was passed
                call_kwargs = mock_client.find_similar.call_args[1]
                assert call_kwargs["category"] == "research paper"

    @pytest.mark.asyncio
    async def test_answer_without_citations(self):
        """Test answer API without citations."""
        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_answer_result = Mock()
                mock_answer_result.answer = "Simple answer without sources."
                # No citations attribute when include_citations is False
                delattr(mock_answer_result, 'citations') if hasattr(mock_answer_result, 'citations') else None
                mock_client.answer.return_value = mock_answer_result
                mock_exa.return_value = mock_client

                args = AnswerArgs(
                    query="Simple question?",
                    include_citations=False
                )
                response = await exa_answer(args)

                assert response.answer == "Simple answer without sources."
                assert response.citations == []

    @pytest.mark.asyncio
    async def test_performance_with_many_results(self):
        """Test performance with a large number of results."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                # Create many results
                mock_results.results = [
                    Mock(
                        title=f"Result {i}",
                        url=f"https://example.com/{i}",
                        text=f"Content {i}",
                        published_date=None,
                        author=None,
                        score=0.9 - (i * 0.001)
                    )
                    for i in range(100)
                ]
                mock_results.autoprompt_string = None
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                import time
                start = time.time()

                args = SearchArgs(query="test query", max_results=100)
                response = await tool(args)

                duration = time.time() - start

                assert len(response.results) == 100
                assert duration < 2.0  # Should process quickly

    @pytest.mark.asyncio
    async def test_exception_in_thread(self):
        """Test handling exceptions in thread execution."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                # Simulate exception during search
                mock_exa.side_effect = ValueError("Invalid API key format")

                args = SearchArgs(query="test query")
                response = await tool(args)

                assert len(response.results) == 1
                assert "Search Error" in response.results[0].title
                assert "Invalid API key format" in response.results[0].snippet

    @pytest.mark.asyncio
    async def test_all_category_types(self):
        """Test all available category types."""
        tool = self.get_component_function()

        categories = [
            ExaCategory.COMPANY,
            ExaCategory.RESEARCH_PAPER,
            ExaCategory.NEWS,
            ExaCategory.LINKEDIN_PROFILE,
            ExaCategory.GITHUB,
            ExaCategory.TWEET,
            ExaCategory.MOVIE,
            ExaCategory.SONG,
            ExaCategory.PERSONAL_SITE,
            ExaCategory.PDF,
            ExaCategory.FINANCIAL_REPORT
        ]

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            for category in categories:
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_results = Mock()
                    mock_results.results = [
                        Mock(
                            title=f"{category.value} result",
                            url=f"https://example.com/{category.value}",
                            text="Category-specific content",
                            published_date=None,
                            author=None,
                            score=0.9
                        )
                    ]
                    mock_results.autoprompt_string = None
                    mock_client.search.return_value = mock_results
                    mock_exa.return_value = mock_client

                    args = SearchArgs(
                        query=f"test {category.value}",
                        category=category
                    )
                    response = await tool(args)

                    assert len(response.results) > 0
                    # Verify category was passed correctly
                    call_kwargs = mock_client.search.call_args[1]
                    assert call_kwargs["category"] == category.value

    @pytest.mark.asyncio
    async def test_empty_query_handling(self):
        """Test handling of empty or whitespace-only queries."""
        tool = self.get_component_function()

        empty_queries = ["", "   ", "\t\n", " " * 100]

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            for query in empty_queries:
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_results = Mock()
                    mock_results.results = []
                    mock_results.autoprompt_string = None
                    mock_client.search.return_value = mock_results
                    mock_exa.return_value = mock_client

                    args = SearchArgs(query=query)
                    response = await tool(args)

                    assert isinstance(response, SearchResponse)
                    assert response.query == query

    @pytest.mark.asyncio
    async def test_very_long_query(self):
        """Test handling of extremely long queries."""
        tool = self.get_component_function()

        # Create a very long query
        long_query = " ".join([f"keyword{i}" for i in range(1000)])

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title="Long query result",
                        url="https://example.com",
                        text="Content",
                        published_date=None,
                        author=None,
                        score=0.8
                    )
                ]
                mock_results.autoprompt_string = "Truncated query"
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(query=long_query, max_results=5)
                response = await tool(args)

                assert isinstance(response, SearchResponse)
                assert response.query == long_query
                assert len(response.results) > 0

    @pytest.mark.asyncio
    async def test_invalid_date_formats(self):
        """Test handling of invalid date formats."""
        tool = self.get_component_function()

        invalid_dates = [
            ("2024-13-01", "2024-12-31"),  # Invalid month
            ("2024-01-32", "2024-12-31"),  # Invalid day
            ("01-01-2024", "31-12-2024"),  # Wrong format
            ("2024/01/01", "2024/12/31"),  # Wrong delimiter
            ("January 1, 2024", "December 31, 2024"),  # Text format
            ("2024", "2025"),  # Year only
        ]

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            for start_date, end_date in invalid_dates:
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    # Exa might handle or reject invalid dates
                    mock_client.search.side_effect = ValueError(f"Invalid date format: {start_date}")
                    mock_exa.return_value = mock_client

                    args = SearchArgs(
                        query="test",
                        start_published_date=start_date,
                        end_published_date=end_date
                    )
                    response = await tool(args)

                    assert isinstance(response, SearchResponse)
                    assert len(response.results) == 1
                    assert "Error" in response.results[0].title

    @pytest.mark.asyncio
    async def test_malformed_urls_find_similar(self):
        """Test find similar with malformed URLs."""
        malformed_urls = [
            "not-a-url",
            "http://",
            "https://",
            "ftp://example.com",
            "javascript:alert('test')",
            "data:text/html,<h1>test</h1>",
            "example.com",  # Missing protocol
            "http://example..com",
            "http://example.com:99999",  # Invalid port
            "http://[invalid-ipv6",
        ]

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            for url in malformed_urls:
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_client.find_similar.side_effect = ValueError(f"Invalid URL: {url}")
                    mock_exa.return_value = mock_client

                    args = FindSimilarArgs(url=url)
                    response = await exa_find_similar(args)

                    assert isinstance(response, SearchResponse)
                    assert "Error" in response.results[0].title or "error" in response.results[0].snippet.lower()

    @pytest.mark.asyncio
    async def test_unicode_emoji_in_queries(self):
        """Test handling of Unicode and emoji in queries and URLs."""
        tool = self.get_component_function()

        unicode_tests = [
            "café résumé naïve 北京 🍕🎉",
            "🚀 rocket science 🧪",
            "математика физика",
            "🐍 Python programming 💻",
            "日本語 プログラミング",
            "العربية برمجة",
            "한국어 코딩",
        ]

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            for query in unicode_tests:
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_results = Mock()
                    mock_results.results = [
                        Mock(
                            title=f"Result for {query}",
                            url="https://example.com/unicode",
                            text="Unicode content",
                            published_date=None,
                            author="Unicode Author 🌍",
                            score=0.9
                        )
                    ]
                    mock_results.autoprompt_string = None
                    mock_client.search.return_value = mock_results
                    mock_exa.return_value = mock_client

                    args = SearchArgs(query=query)
                    response = await tool(args)

                    assert isinstance(response, SearchResponse)
                    assert response.query == query
                    assert len(response.results) > 0

    @pytest.mark.asyncio
    async def test_network_timeout_simulation(self):
        """Test handling of network timeouts."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()

                # Simulate timeout
                import asyncio
                async def timeout_func(*args, **kwargs):
                    await asyncio.sleep(10)  # Long delay

                mock_client.search.side_effect = TimeoutError("Request timed out")
                mock_exa.return_value = mock_client

                args = SearchArgs(query="timeout test")
                response = await tool(args)

                assert isinstance(response, SearchResponse)
                assert len(response.results) == 1
                assert "Error" in response.results[0].title
                assert "timed out" in response.results[0].snippet.lower()

    @pytest.mark.asyncio
    async def test_thread_pool_executor_error(self):
        """Test handling of thread pool executor errors."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                # Simulate thread pool error
                with patch("asyncio.to_thread") as mock_to_thread:
                    mock_to_thread.side_effect = RuntimeError("Thread pool exhausted")

                    args = SearchArgs(query="thread error test")
                    response = await tool(args)

                    assert isinstance(response, SearchResponse)
                    assert len(response.results) == 1
                    assert "Error" in response.results[0].title

    @pytest.mark.asyncio
    async def test_json_serialization_edge_cases(self):
        """Test handling of values that are difficult to JSON serialize."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()

                # Create results with problematic values
                import datetime
                import decimal

                mock_results.results = [
                    Mock(
                        title="Result with special values",
                        url="https://example.com",
                        text="Content",
                        published_date=datetime.datetime.now(),  # datetime object
                        author=None,
                        score=decimal.Decimal("0.95")  # Decimal object
                    )
                ]
                mock_results.autoprompt_string = None
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(query="special values test")
                response = await tool(args)

                assert isinstance(response, SearchResponse)
                assert len(response.results) > 0
                # Should handle conversion gracefully

    @pytest.mark.asyncio
    async def test_search_with_all_parameters(self):
        """Test search with all possible parameters set."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title="Comprehensive result",
                        url="https://research.com/paper",
                        text="Full parameter search",
                        published_date="2024-06-15",
                        author="Dr. Complete",
                        score=0.99
                    )
                ]
                mock_results.autoprompt_string = "Enhanced comprehensive query"
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(
                    query="comprehensive test query",
                    max_results=10,
                    search_type="neural",
                    category=ExaCategory.RESEARCH_PAPER,
                    start_published_date="2024-01-01",
                    end_published_date="2024-12-31",
                    include_domains=["arxiv.org", "nature.com", "science.org"],
                    exclude_domains=["blog.com", "forum.com", "reddit.com"]
                )
                response = await tool(args)

                assert isinstance(response, SearchResponse)
                assert len(response.results) == 1

                # Verify all parameters were passed
                call_kwargs = mock_client.search.call_args[1]
                assert call_kwargs["query"] == "comprehensive test query"
                assert call_kwargs["num_results"] == 10
                assert call_kwargs["type"] == "neural"
                assert call_kwargs["category"] == "research paper"
                assert call_kwargs["start_published_date"] == "2024-01-01"
                assert call_kwargs["end_published_date"] == "2024-12-31"
                assert len(call_kwargs["include_domains"]) == 3
                assert len(call_kwargs["exclude_domains"]) == 3

    @pytest.mark.asyncio
    async def test_answer_api_error_variations(self):
        """Test various error scenarios for answer API."""
        error_scenarios = [
            Exception("Rate limit exceeded"),
            ValueError("Invalid query format"),
            RuntimeError("Internal server error"),
            ConnectionError("Network connection failed"),
            TimeoutError("Request timed out"),
        ]

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            for error in error_scenarios:
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_client.answer.side_effect = error
                    mock_exa.return_value = mock_client

                    args = AnswerArgs(query="What causes errors?")
                    response = await exa_answer(args)

                    assert isinstance(response, AnswerResponse)
                    assert "Error" in response.answer
                    assert str(error) in response.answer

    @pytest.mark.asyncio
    async def test_find_similar_with_text_instead_of_url(self):
        """Test find similar when user provides text instead of URL."""
        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                # Should handle gracefully or convert to search
                mock_client.find_similar.side_effect = ValueError("Invalid URL format")
                mock_exa.return_value = mock_client

                args = FindSimilarArgs(
                    url="This is not a URL but some text content",
                    max_results=5
                )
                response = await exa_find_similar(args)

                assert isinstance(response, SearchResponse)
                assert "Error" in response.results[0].title

    @pytest.mark.asyncio
    async def test_response_field_validation(self):
        """Test that all response fields are properly validated."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()

                # Result with all fields populated
                mock_results.results = [
                    Mock(
                        title="Complete Result",
                        url="https://example.com/complete",
                        text="Full content with all fields",
                        published_date="2024-07-01",
                        author="Complete Author",
                        score=0.987654321  # High precision score
                    )
                ]
                mock_results.autoprompt_string = "Auto-enhanced query string"
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(query="complete field test")
                response = await tool(args)

                # Validate response structure
                assert isinstance(response, SearchResponse)
                assert isinstance(response.results, list)
                assert isinstance(response.query, str)
                assert isinstance(response.provider, str)
                assert response.autoprompt_string is None or isinstance(response.autoprompt_string, str)

                # Validate result fields
                result = response.results[0]
                assert isinstance(result.title, str)
                assert isinstance(result.url, str)
                assert isinstance(result.snippet, str)
                assert result.published_date is None or isinstance(result.published_date, str)
                assert result.author is None or isinstance(result.author, str)
                assert result.score is None or isinstance(result.score, float)

    @pytest.mark.asyncio
    async def test_memory_handling_large_responses(self):
        """Test memory handling with very large response sets."""
        tool = self.get_component_function()

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()

                # Create a large number of results with substantial content
                large_text = "x" * 10000  # 10KB of text per result
                mock_results.results = [
                    Mock(
                        title=f"Large Result {i}",
                        url=f"https://example.com/large/{i}",
                        text=large_text,
                        published_date="2024-01-01",
                        author=f"Author {i}",
                        score=0.9 - (i * 0.001)
                    )
                    for i in range(1000)  # 1000 results
                ]
                mock_results.autoprompt_string = "Large dataset query"
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client

                args = SearchArgs(query="large dataset test", max_results=1000)

                # Should handle without memory issues
                response = await tool(args)

                assert isinstance(response, SearchResponse)
                assert len(response.results) == 1000

                # Verify memory-efficient handling
                assert all(isinstance(r.snippet, str) for r in response.results)

    @pytest.mark.asyncio
    async def test_domain_filter_edge_cases(self):
        """Test edge cases in domain filtering."""
        tool = self.get_component_function()

        domain_tests = [
            # Empty lists
            ([], []),
            # Single domain
            (["example.com"], None),
            (None, ["spam.com"]),
            # Many domains
            ([f"site{i}.com" for i in range(50)], None),
            # Special characters in domains
            (["sub.domain.com", "domain-with-dash.com", "domain_underscore.com"], None),
            # International domains
            (["例え.jp", "مثال.com", "пример.ru"], None),
        ]

        with patch.dict(os.environ, {"EXA_API_KEY": "test_key"}):
            for include_domains, exclude_domains in domain_tests:
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_results = Mock()
                    mock_results.results = [
                        Mock(
                            title="Domain filter result",
                            url="https://allowed.com/page",
                            text="Content",
                            published_date=None,
                            author=None,
                            score=0.85
                        )
                    ]
                    mock_results.autoprompt_string = None
                    mock_client.search.return_value = mock_results
                    mock_exa.return_value = mock_client

                    args = SearchArgs(
                        query="domain test",
                        include_domains=include_domains,
                        exclude_domains=exclude_domains
                    )
                    response = await tool(args)

                    assert isinstance(response, SearchResponse)
                    # Verify domains were passed correctly
                    call_kwargs = mock_client.search.call_args[1]
                    if include_domains is not None:
                        assert call_kwargs["include_domains"] == include_domains
                    if exclude_domains is not None:
                        assert call_kwargs["exclude_domains"] == exclude_domains
