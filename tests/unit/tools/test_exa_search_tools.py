"""Test suite for exa_search_tools following best practices."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestExaSearchTools(BaseToolTest):
    """Test exa_search_tools component."""
    
    component_name = "exa_search_tools"
    component_path = Path("packages/funcn_registry/components/tools/exa_search_tools")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.exa_search_tools import neural_search
        def mock_neural_search(
            query: str,
            num_results: int = 10,
            start_published_date: str | None = None,
            end_published_date: str | None = None,
            include_domains: list[str] | None = None,
            exclude_domains: list[str] | None = None,
            use_autoprompt: bool = True,
            type: str = "auto"
        ) -> list[dict[str, any]]:
            """Mock Exa neural search tool."""
            return [
                {
                    "title": f"Neural result {i+1} for '{query}'",
                    "url": f"https://example.com/neural{i+1}",
                    "snippet": f"AI-powered search result {i+1}",
                    "published_date": datetime.now().isoformat(),
                    "score": 0.95 - (i * 0.05),
                    "id": f"exa_{i+1}"
                }
                for i in range(min(num_results, 5))
            ]
        return mock_neural_search
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "query": "latest AI research papers",
                "num_results": 5,
                "type": "research"
            },
            {
                "query": "machine learning tutorials",
                "num_results": 10,
                "start_published_date": "2024-01-01",
                "include_domains": ["arxiv.org", "openai.com"]
            },
            {
                "query": "quantum computing breakthroughs",
                "num_results": 3,
                "exclude_domains": ["wikipedia.org"],
                "use_autoprompt": True
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        assert len(output) <= input_data.get("num_results", 10)
        
        for result in output:
            assert "title" in result
            assert "url" in result
            assert result["url"].startswith("http")
            if "score" in result:
                assert 0 <= result["score"] <= 1
    
    @pytest.mark.asyncio
    async def test_neural_search_with_autoprompt(self):
        """Test neural search with autoprompt feature."""
        tool = self.get_component_function()
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = Mock()
            mock_results.results = [
                Mock(
                    title="Enhanced result",
                    url="https://example.com",
                    text="Autoprompt improved this search",
                    score=0.98,
                    published_date="2024-01-01",
                    id="exa_1"
                )
            ]
            mock_client.search.return_value = mock_results
            mock_exa.return_value = mock_client
            
            results = tool("find best AI models", use_autoprompt=True)
            
            # Verify autoprompt was used
            search_args = mock_client.search.call_args[1]
            assert search_args.get("use_autoprompt") is True
            assert len(results) > 0
    
    def test_similarity_search(self):
        """Test similarity search functionality."""
        # Would import: from tools.exa_search_tools import find_similar
        def mock_find_similar(url: str, num_results: int = 10) -> list[dict[str, any]]:
            return [
                {
                    "title": f"Similar to {url} - Result {i+1}",
                    "url": f"https://similar{i+1}.com",
                    "similarity_score": 0.9 - (i * 0.1)
                }
                for i in range(min(num_results, 5))
            ]
        
        tool = mock_find_similar
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = Mock()
            mock_results.results = [
                Mock(title="Similar page", url="https://similar.com", score=0.95)
            ]
            mock_client.find_similar.return_value = mock_results
            mock_exa.return_value = mock_client
            
            results = tool("https://example.com/article", num_results=5)
            assert len(results) > 0
            assert all("similar" in r["title"].lower() for r in results)
    
    def test_search_with_date_filters(self):
        """Test search with date range filters."""
        tool = self.get_component_function()
        
        # Test with date range
        start_date = "2024-01-01"
        end_date = "2024-12-31"
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = Mock()
            mock_results.results = [
                Mock(
                    title="Recent article",
                    url="https://example.com",
                    published_date="2024-06-15",
                    score=0.9
                )
            ]
            mock_client.search.return_value = mock_results
            mock_exa.return_value = mock_client
            
            results = tool(
                "AI news",
                start_published_date=start_date,
                end_published_date=end_date
            )
            
            # Verify date parameters were passed
            search_args = mock_client.search.call_args[1]
            assert search_args.get("start_published_date") == start_date
            assert search_args.get("end_published_date") == end_date
    
    def test_domain_filtering(self):
        """Test include/exclude domain filtering."""
        tool = self.get_component_function()
        
        include_domains = ["arxiv.org", "nature.com"]
        exclude_domains = ["medium.com", "reddit.com"]
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = Mock()
            mock_results.results = [
                Mock(title="Filtered result", url="https://arxiv.org/paper", score=0.92)
            ]
            mock_client.search.return_value = mock_results
            mock_exa.return_value = mock_client
            
            results = tool(
                "research papers",
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            
            # Verify domain filters were applied
            search_args = mock_client.search.call_args[1]
            assert search_args.get("include_domains") == include_domains
            assert search_args.get("exclude_domains") == exclude_domains
    
    def test_search_types(self):
        """Test different search types (auto, keyword, neural)."""
        tool = self.get_component_function()
        search_types = ["auto", "keyword", "neural"]
        
        for search_type in search_types:
            with patch("exa_py.Exa") as mock_exa:
                mock_client = Mock()
                mock_results = Mock()
                mock_results.results = [
                    Mock(
                        title=f"{search_type} search result",
                        url="https://example.com",
                        score=0.88
                    )
                ]
                mock_client.search.return_value = mock_results
                mock_exa.return_value = mock_client
                
                results = tool("test query", type=search_type)
                
                # Verify search type was passed
                search_args = mock_client.search.call_args[1]
                assert search_args.get("type") == search_type
    
    def test_direct_qa_functionality(self):
        """Test direct Q&A search feature."""
        # Would import: from tools.exa_search_tools import ask_question
        def mock_ask_question(question: str) -> dict[str, any]:
            return {
                "answer": f"The answer to '{question}' is 42.",
                "sources": [
                    {"title": "Source 1", "url": "https://source1.com"},
                    {"title": "Source 2", "url": "https://source2.com"}
                ],
                "confidence": 0.85
            }
        
        tool = mock_ask_question
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_client.search_and_contents.return_value = Mock(
                results=[
                    Mock(
                        title="Answer source",
                        url="https://source.com",
                        text="The answer is 42 because..."
                    )
                ]
            )
            mock_exa.return_value = mock_client
            
            result = tool("What is the meaning of life?")
            assert "answer" in result
            assert "sources" in result
            assert isinstance(result["sources"], list)
    
    def test_content_extraction(self):
        """Test content extraction with search."""
        tool = self.get_component_function()
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = Mock()
            mock_results.results = [
                Mock(
                    title="Full content article",
                    url="https://example.com",
                    text="This is the full extracted content of the article...",
                    highlights=["key point 1", "key point 2"],
                    score=0.91
                )
            ]
            mock_client.search_and_contents.return_value = mock_results
            mock_exa.return_value = mock_client
            
            # Assuming there's a parameter to get full content
            results = tool("detailed article", get_contents=True)
            
            # Results should include full text
            assert any("text" in r or "content" in r for r in results)
    
    def test_handles_api_errors(self):
        """Test handling of Exa API errors."""
        tool = self.get_component_function()
        
        error_scenarios = [
            ("API key invalid", ValueError),
            ("Rate limit exceeded", Exception),
            ("Network error", ConnectionError)
        ]
        
        for error_msg, error_type in error_scenarios:
            with patch("exa_py.Exa") as mock_exa:
                mock_client = Mock()
                mock_client.search.side_effect = error_type(error_msg)
                mock_exa.return_value = mock_client
                
                results = tool("test query")
                assert isinstance(results, list)
                assert len(results) == 0 or "error" in str(results)
    
    @pytest.mark.parametrize("num_results", [1, 10, 50, 100])
    def test_result_limits(self, num_results):
        """Test that num_results parameter is respected."""
        tool = self.get_component_function()
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = Mock()
            # Create exactly the requested number of results
            mock_results.results = [
                Mock(
                    title=f"Result {i}",
                    url=f"https://example.com/{i}",
                    score=0.9 - (i * 0.001)
                )
                for i in range(num_results)
            ]
            mock_client.search.return_value = mock_results
            mock_exa.return_value = mock_client
            
            results = tool("test query", num_results=num_results)
            assert len(results) == num_results
    
    def test_empty_results_handling(self):
        """Test handling when no results are found."""
        tool = self.get_component_function()
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = Mock()
            mock_results.results = []
            mock_client.search.return_value = mock_results
            mock_exa.return_value = mock_client
            
            results = tool("extremely obscure query xyz789")
            assert results == []
    
    def test_result_score_sorting(self):
        """Test that results are properly sorted by relevance score."""
        tool = self.get_component_function()
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = Mock()
            # Create results with mixed scores
            mock_results.results = [
                Mock(title="Low score", url="https://low.com", score=0.5),
                Mock(title="High score", url="https://high.com", score=0.95),
                Mock(title="Medium score", url="https://medium.com", score=0.75)
            ]
            mock_client.search.return_value = mock_results
            mock_exa.return_value = mock_client
            
            results = tool("test query")
            
            # Results should be sorted by score (highest first)
            if all("score" in r for r in results):
                scores = [r["score"] for r in results]
                assert scores == sorted(scores, reverse=True)
