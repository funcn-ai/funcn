"""Test suite for duckduckgo_search_tool following best practices."""

import asyncio
import pytest

# Import the actual tool functions and models
from packages.funcn_registry.components.tools.duckduckgo_search.tool import (
    SearchArgs,
    SearchResponse,
    SearchResult,
    duckduckgo_search,
)
from pathlib import Path
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import MagicMock, Mock, patch


class TestDuckDuckGoSearchTool(BaseToolTest):
    """Test duckduckgo_search_tool component."""
    
    component_name = "duckduckgo_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/duckduckgo_search")
    
    def get_component_function(self):
        """Import the tool function."""
        return duckduckgo_search
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            SearchArgs(
                query="artificial intelligence",
                max_results=5
            ),
            SearchArgs(
                query="python programming",
                max_results=10
            ),
            SearchArgs(
                query="machine learning tutorial",
                max_results=3
            )
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, SearchResponse)
        assert isinstance(output.results, list)
        assert len(output.results) <= input_data.max_results
        assert output.query == input_data.query
        assert output.provider == "duckduckgo"
        
        for result in output.results:
            assert isinstance(result, SearchResult)
            assert result.title
            assert result.url
            assert result.snippet is not None
    
    @pytest.mark.asyncio
    async def test_basic_search(self):
        """Test basic search functionality."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = [
                {
                    "title": "Test Result 1",
                    "body": "This is a test snippet",
                    "href": "https://example.com/1"
                },
                {
                    "title": "Test Result 2",
                    "body": "Another test snippet",
                    "href": "https://example.com/2"
                }
            ]
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 2
            assert response.query == "test query"
            assert response.provider == "duckduckgo"
            
            # Verify first result
            assert response.results[0].title == "Test Result 1"
            assert response.results[0].snippet == "This is a test snippet"
            assert response.results[0].url == "https://example.com/1"
    
    @pytest.mark.asyncio
    async def test_handles_no_results(self):
        """Test handling when no results are found."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = []
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="very obscure query that returns nothing", max_results=5)
            response = await tool(args)
            
            assert isinstance(response, SearchResponse)
            assert response.results == []
            assert response.query == "very obscure query that returns nothing"
            assert response.provider == "duckduckgo"
    
    @pytest.mark.asyncio
    async def test_handles_api_errors(self):
        """Test handling of API errors."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.side_effect = Exception("API Error")
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            # Should handle error gracefully
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Search Error for: test query" in response.results[0].title
            assert "Error performing search: API Error" in response.results[0].snippet
    
    @pytest.mark.asyncio
    async def test_handles_import_error(self):
        """Test handling when duckduckgo_search is not installed."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_ddgs.side_effect = ImportError("No module named 'duckduckgo_search'")
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            # Should return fallback response
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Search for: test query" in response.results[0].title
            assert "DuckDuckGo search library not available" in response.results[0].snippet
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("max_results", [1, 5, 10, 20, 50])
    async def test_respects_max_results(self, max_results):
        """Test that max_results parameter is respected."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            # Create more results than requested
            mock_results = [
                {"title": f"Result {i}", "body": "Content", "href": f"https://example.com/{i}"}
                for i in range(100)
            ]
            
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = mock_results[:max_results]
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=max_results)
            response = await tool(args)
            
            assert len(response.results) == max_results
            mock_instance.text.assert_called_once_with("test query", max_results=max_results)
    
    @pytest.mark.asyncio
    async def test_result_structure_transformation(self):
        """Test that DuckDuckGo results are properly transformed."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            # Mock raw DuckDuckGo response format
            raw_results = [
                {
                    "title": "Test Title",
                    "body": "This is the body/snippet of the result",
                    "href": "https://example.com/page",
                    "domain": "example.com"
                },
                {
                    "title": "",  # Test empty title
                    "body": "",   # Test empty body
                    "href": "https://example.com/empty"
                }
            ]
            
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = raw_results
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            # Verify transformation
            assert len(response.results) == 2
            
            # Check first result
            assert response.results[0].title == "Test Title"
            assert response.results[0].snippet == "This is the body/snippet of the result"
            assert response.results[0].url == "https://example.com/page"
            
            # Check handling of empty fields
            assert response.results[1].title == ""
            assert response.results[1].snippet == ""
            assert response.results[1].url == "https://example.com/empty"
    
    @pytest.mark.asyncio
    async def test_empty_query_handling(self):
        """Test handling of empty or whitespace queries."""
        tool = self.get_component_function()
        
        empty_queries = ["", "   ", "\t\n"]
        
        for query in empty_queries:
            with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
                mock_instance = MagicMock()
                mock_instance.__enter__.return_value = mock_instance
                mock_instance.__exit__.return_value = None
                mock_instance.text.return_value = []
                mock_ddgs.return_value = mock_instance
                
                args = SearchArgs(query=query, max_results=5)
                response = await tool(args)
                
                # Should handle empty queries gracefully
                assert isinstance(response, SearchResponse)
                assert response.query == query
    
    @pytest.mark.asyncio
    async def test_special_characters_in_query(self):
        """Test queries with special characters."""
        tool = self.get_component_function()
        
        special_queries = [
            "C++ programming",
            "what is 2+2?",
            "email@example.com",
            "site:example.com python",
            '"exact match query"',
            "python AND (tutorial OR guide)",
            "test/path\\query"
        ]
        
        for query in special_queries:
            with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
                mock_instance = MagicMock()
                mock_instance.__enter__.return_value = mock_instance
                mock_instance.__exit__.return_value = None
                mock_instance.text.return_value = [
                    {"title": f"Result for {query}", "body": "Content", "href": "https://example.com"}
                ]
                mock_ddgs.return_value = mock_instance
                
                args = SearchArgs(query=query, max_results=5)
                response = await tool(args)
                
                assert isinstance(response, SearchResponse)
                assert response.query == query
                assert len(response.results) == 1
    
    @pytest.mark.asyncio
    async def test_async_thread_execution(self):
        """Test that search runs in a thread to avoid blocking."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            
            # Simulate slow search
            def slow_search(*args, **kwargs):
                import time
                time.sleep(0.1)  # Small delay
                return [{"title": "Result", "body": "Content", "href": "https://example.com"}]
            
            mock_instance.text = slow_search
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=5)
            
            # Should still complete quickly due to thread execution
            import time
            start = time.time()
            response = await tool(args)
            duration = time.time() - start
            
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            # Test that it's not blocking the event loop too much
            assert duration < 1.0
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self):
        """Test multiple concurrent searches."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            call_count = 0
            
            def create_instance():
                nonlocal call_count
                call_count += 1
                instance = MagicMock()
                instance.__enter__.return_value = instance
                instance.__exit__.return_value = None
                instance.text.return_value = [
                    {"title": f"Result {call_count}", "body": f"Content {call_count}", "href": f"https://example.com/{call_count}"}
                ]
                return instance
            
            mock_ddgs.side_effect = create_instance
            
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
    async def test_missing_fields_in_results(self):
        """Test handling of missing fields in search results."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            # Results with various missing fields
            raw_results = [
                {"title": "Has all fields", "body": "Complete", "href": "https://complete.com"},
                {"body": "Missing title", "href": "https://notitle.com"},  # Missing title
                {"title": "Missing body", "href": "https://nobody.com"},  # Missing body
                {"title": "Missing URL", "body": "No link"},  # Missing href
                {},  # Empty result
            ]
            
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = raw_results
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=10)
            response = await tool(args)
            
            # Should handle all cases gracefully
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 5
            
            # Check handling of missing fields
            assert response.results[0].title == "Has all fields"
            assert response.results[1].title == ""  # Missing title gets empty string
            assert response.results[2].snippet == ""  # Missing body gets empty string
            assert response.results[3].url == ""  # Missing href gets empty string
            assert response.results[4].title == ""  # Empty result gets all empty strings
    
    @pytest.mark.asyncio
    async def test_unicode_and_encoding(self):
        """Test handling of Unicode characters and different encodings."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            # Results with various Unicode characters
            raw_results = [
                {
                    "title": "Résumé with café ☕",
                    "body": "Unicode test: 你好世界 🌍 Здравствуй мир",
                    "href": "https://unicode.com/café"
                },
                {
                    "title": "Math symbols: ∑ ∏ ∫ ≠ ≤ ≥",
                    "body": "Emojis: 😀 🎉 🚀 💻",
                    "href": "https://symbols.com"
                }
            ]
            
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = raw_results
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="unicode test 测试", max_results=5)
            response = await tool(args)
            
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 2
            
            # Verify Unicode is preserved
            assert "café" in response.results[0].title
            assert "☕" in response.results[0].title
            assert "你好世界" in response.results[0].snippet
            assert "🌍" in response.results[0].snippet
            assert "∑" in response.results[1].title
            assert "😀" in response.results[1].snippet
    
    @pytest.mark.asyncio
    async def test_very_long_query(self):
        """Test handling of very long search queries."""
        tool = self.get_component_function()
        
        # Create a very long query
        long_query = "python " * 100 + "programming tutorial for beginners"
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = [
                {"title": "Result for long query", "body": "Content", "href": "https://example.com"}
            ]
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query=long_query, max_results=5)
            response = await tool(args)
            
            assert isinstance(response, SearchResponse)
            assert response.query == long_query
            assert len(response.results) == 1
    
    @pytest.mark.asyncio
    async def test_html_entities_in_results(self):
        """Test handling of HTML entities in search results."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            raw_results = [
                {
                    "title": "HTML &amp; Entities &lt;test&gt;",
                    "body": "Content with &quot;quotes&quot; and &apos;apostrophes&apos;",
                    "href": "https://example.com?param=value&amp;other=test"
                }
            ]
            
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = raw_results
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="html test", max_results=5)
            response = await tool(args)
            
            # HTML entities should be preserved as-is (not decoded)
            assert isinstance(response, SearchResponse)
            assert "&amp;" in response.results[0].title
            assert "&quot;" in response.results[0].snippet
    
    @pytest.mark.asyncio
    async def test_network_timeout_simulation(self):
        """Test handling of network timeouts."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.side_effect = TimeoutError("Network timeout")
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            # Should handle timeout gracefully
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Search Error" in response.results[0].title
            assert "Network timeout" in response.results[0].snippet
    
    @pytest.mark.asyncio
    async def test_rate_limiting_response(self):
        """Test handling of rate limiting responses."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.side_effect = Exception("Rate limit exceeded")
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            # Should handle rate limiting gracefully
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Rate limit exceeded" in response.results[0].snippet
    
    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self):
        """Test that DDGS context manager is properly cleaned up."""
        tool = self.get_component_function()
        
        mock_instance = MagicMock()
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.__exit__.return_value = None
        mock_instance.text.return_value = [
            {"title": "Test", "body": "Content", "href": "https://example.com"}
        ]
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            # Verify context manager was used properly
            mock_instance.__enter__.assert_called_once()
            mock_instance.__exit__.assert_called_once()
            
            assert isinstance(response, SearchResponse)
    
    @pytest.mark.asyncio
    async def test_performance_with_many_results(self):
        """Test performance with a large number of results."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            # Create exactly max_results mock results
            large_results = [
                {"title": f"Result {i}", "body": f"Content {i}", "href": f"https://example.com/{i}"}
                for i in range(100)  # Matches max_results
            ]
            
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = large_results
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=100)
            
            import time
            start = time.time()
            response = await tool(args)
            duration = time.time() - start
            
            # Should handle large results efficiently
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 100  # Limited by max_results
            assert duration < 2.0  # Should process quickly
    
    @pytest.mark.asyncio
    async def test_malformed_url_handling(self):
        """Test handling of malformed URLs in results."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.duckduckgo_search.tool.DDGS") as mock_ddgs:
            raw_results = [
                {"title": "Valid URL", "body": "Content", "href": "https://valid.com"},
                {"title": "Invalid URL", "body": "Content", "href": "not-a-valid-url"},
                {"title": "Relative URL", "body": "Content", "href": "/relative/path"},
                {"title": "Missing protocol", "body": "Content", "href": "www.example.com"},
            ]
            
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.text.return_value = raw_results
            mock_ddgs.return_value = mock_instance
            
            args = SearchArgs(query="test query", max_results=10)
            response = await tool(args)
            
            # Should accept all URLs as-is
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 4
            assert response.results[0].url == "https://valid.com"
            assert response.results[1].url == "not-a-valid-url"
            assert response.results[2].url == "/relative/path"
            assert response.results[3].url == "www.example.com"
