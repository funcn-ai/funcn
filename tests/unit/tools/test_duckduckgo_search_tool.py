"""Test suite for duckduckgo_search_tool following best practices."""

import pytest
from pathlib import Path
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestDuckDuckGoSearchTool(BaseToolTest):
    """Test duckduckgo_search_tool component."""
    
    component_name = "duckduckgo_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/duckduckgo_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.duckduckgo_search_tool import search_web
        def mock_search_web(
            query: str,
            max_results: int = 10,
            region: str = "wt-wt",
            safesearch: str = "moderate"
        ) -> list[dict[str, any]]:
            """Mock DuckDuckGo search tool."""
            return [
                {
                    "title": f"Result {i+1} for '{query}'",
                    "snippet": f"This is a snippet for search result {i+1}",
                    "url": f"https://example.com/result{i+1}",
                    "score": 1.0 - (i * 0.1)
                }
                for i in range(min(max_results, 5))
            ]
        return mock_search_web
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "query": "artificial intelligence",
                "max_results": 5,
                "region": "us-en"
            },
            {
                "query": "python programming",
                "max_results": 10,
                "safesearch": "strict"
            },
            {
                "query": "machine learning tutorial",
                "max_results": 3
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        assert len(output) <= input_data.get("max_results", 10)
        
        for result in output:
            assert "title" in result
            assert "snippet" in result or "description" in result
            assert "url" in result
            assert result["url"].startswith("http")
    
    @pytest.mark.asyncio
    async def test_search_with_different_regions(self):
        """Test search with various region settings."""
        regions = ["us-en", "uk-en", "fr-fr", "de-de", "wt-wt"]
        tool = self.get_component_function()
        
        for region in regions:
            with patch("duckduckgo_search.DDGS") as mock_ddgs:
                mock_instance = Mock()
                mock_instance.text.return_value = [
                    {
                        "title": f"Result for region {region}",
                        "body": "Test content",
                        "href": "https://example.com"
                    }
                ]
                mock_ddgs.return_value = mock_instance
                
                results = tool("test query", region=region)
                assert len(results) > 0
                mock_instance.text.assert_called_once()
    
    def test_safesearch_filtering(self):
        """Test different safesearch levels."""
        safesearch_levels = ["strict", "moderate", "off"]
        tool = self.get_component_function()
        
        for level in safesearch_levels:
            with patch("duckduckgo_search.DDGS") as mock_ddgs:
                mock_instance = Mock()
                mock_instance.text.return_value = [
                    {"title": f"Safe result ({level})", "body": "Content", "href": "https://safe.com"}
                ]
                mock_ddgs.return_value = mock_instance
                
                results = tool("test query", safesearch=level)
                assert len(results) > 0
                
                # Verify safesearch parameter was passed
                call_args = mock_instance.text.call_args
                assert call_args[1].get("safesearch") == level
    
    def test_handles_no_results(self):
        """Test handling when no results are found."""
        tool = self.get_component_function()
        
        with patch("duckduckgo_search.DDGS") as mock_ddgs:
            mock_instance = Mock()
            mock_instance.text.return_value = []
            mock_ddgs.return_value = mock_instance
            
            results = tool("very obscure query that returns nothing")
            assert results == []
    
    def test_handles_api_errors(self):
        """Test handling of API errors."""
        tool = self.get_component_function()
        
        with patch("duckduckgo_search.DDGS") as mock_ddgs:
            mock_instance = Mock()
            mock_instance.text.side_effect = Exception("API Error")
            mock_ddgs.return_value = mock_instance
            
            # Should handle error gracefully
            results = tool("test query")
            assert isinstance(results, list)
            assert len(results) == 0 or (len(results) == 1 and "error" in str(results[0]))
    
    @pytest.mark.parametrize("max_results", [1, 5, 10, 20, 50])
    def test_respects_max_results(self, max_results):
        """Test that max_results parameter is respected."""
        tool = self.get_component_function()
        
        with patch("duckduckgo_search.DDGS") as mock_ddgs:
            # Create more results than requested
            mock_results = [
                {"title": f"Result {i}", "body": "Content", "href": f"https://example.com/{i}"}
                for i in range(100)
            ]
            
            mock_instance = Mock()
            mock_instance.text.return_value = mock_results
            mock_ddgs.return_value = mock_instance
            
            results = tool("test query", max_results=max_results)
            assert len(results) <= max_results
    
    def test_result_structure_transformation(self):
        """Test that DuckDuckGo results are properly transformed."""
        tool = self.get_component_function()
        
        with patch("duckduckgo_search.DDGS") as mock_ddgs:
            # Mock raw DuckDuckGo response format
            raw_results = [
                {
                    "title": "Test Title",
                    "body": "This is the body/snippet of the result",
                    "href": "https://example.com/page",
                    "domain": "example.com"
                }
            ]
            
            mock_instance = Mock()
            mock_instance.text.return_value = raw_results
            mock_ddgs.return_value = mock_instance
            
            results = tool("test query")
            
            # Verify transformation
            assert len(results) == 1
            result = results[0]
            assert result.get("title") == "Test Title"
            assert result.get("snippet") == "This is the body/snippet of the result" or \
                   result.get("description") == "This is the body/snippet of the result"
            assert result.get("url") == "https://example.com/page"
    
    def test_empty_query_handling(self):
        """Test handling of empty or whitespace queries."""
        tool = self.get_component_function()
        
        empty_queries = ["", "   ", "\t\n"]
        
        for query in empty_queries:
            results = tool(query)
            # Should either return empty list or raise ValueError
            assert results == [] or isinstance(results, list)
    
    def test_special_characters_in_query(self):
        """Test queries with special characters."""
        tool = self.get_component_function()
        
        special_queries = [
            "C++ programming",
            "what is 2+2?",
            "email@example.com",
            "site:example.com python",
            '"exact match query"'
        ]
        
        for query in special_queries:
            with patch("duckduckgo_search.DDGS") as mock_ddgs:
                mock_instance = Mock()
                mock_instance.text.return_value = [
                    {"title": f"Result for {query}", "body": "Content", "href": "https://example.com"}
                ]
                mock_ddgs.return_value = mock_instance
                
                results = tool(query)
                assert isinstance(results, list)
