"""Test suite for qwant_search_tool following best practices."""

import asyncio
import pytest

# Import the actual tool functions and models
from packages.funcn_registry.components.tools.qwant_search.tool import (
    SearchArgs,
    SearchResponse,
    SearchResult,
    qwant_search,
)
from pathlib import Path
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class TestQwantSearchTool(BaseToolTest):
    """Test qwant_search_tool component."""
    
    component_name = "qwant_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/qwant_search")
    
    def get_component_function(self):
        """Import the tool function."""
        return qwant_search
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            SearchArgs(
                query="privacy search engine",
                max_results=5,
                locale="en_US"
            ),
            SearchArgs(
                query="données privées",
                max_results=10,
                locale="fr_FR"
            ),
            SearchArgs(
                query="no tracking search",
                max_results=3,
                locale="en_US"
            )
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, SearchResponse)
        assert isinstance(output.results, list)
        assert len(output.results) <= input_data.max_results
        assert output.query == input_data.query
        assert output.provider == "qwant"
        
        for result in output.results:
            assert isinstance(result, SearchResult)
            assert result.title is not None
            assert result.url is not None
            assert result.snippet is not None
    
    @pytest.mark.asyncio
    async def test_basic_qwant_search(self):
        """Test basic Qwant search functionality."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            # Mock async context manager
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            # Mock response
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "result": {
                        "items": [
                            {
                                "type": "web",
                                "title": "Privacy Search Result",
                                "url": "https://example.com/privacy",
                                "desc": "Private search engine with no tracking"
                            },
                            {
                                "type": "web", 
                                "title": "Second Result",
                                "url": "https://example.com/second",
                                "desc": "Another private result"
                            }
                        ]
                    }
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="privacy search", max_results=5, locale="en_US")
            response = await tool(args)
            
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 2
            assert response.query == "privacy search"
            assert response.provider == "qwant"
            
            # Check first result
            assert response.results[0].title == "Privacy Search Result"
            assert response.results[0].url == "https://example.com/privacy"
            assert response.results[0].snippet == "Private search engine with no tracking"
    
    @pytest.mark.asyncio
    async def test_handles_no_results(self):
        """Test handling when no results are found."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "result": {
                        "items": []
                    }
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="very obscure query that returns nothing", max_results=5)
            response = await tool(args)
            
            assert isinstance(response, SearchResponse)
            assert response.results == []
            assert response.query == "very obscure query that returns nothing"
            assert response.provider == "qwant"
    
    @pytest.mark.asyncio
    async def test_handles_api_errors(self):
        """Test handling of API errors."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            # Simulate HTTP error
            mock_instance.get.side_effect = Exception("API Error")
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            # Should handle error gracefully
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Search Error for: test query" in response.results[0].title
            assert "Error performing Qwant search: API Error" in response.results[0].snippet
    
    @pytest.mark.asyncio
    async def test_handles_http_status_errors(self):
        """Test handling when HTTP request fails with status error."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 429 Rate Limited")
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query", max_results=5)
            response = await tool(args)
            
            # Should return fallback response
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Search Error for: test query" in response.results[0].title
            assert "HTTP 429 Rate Limited" in response.results[0].snippet
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("max_results", [1, 5, 10])
    async def test_respects_max_results(self, max_results):
        """Test that max_results parameter is respected."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            # Create more results than requested
            mock_results = [
                {
                    "type": "web",
                    "title": f"Result {i}",
                    "url": f"https://example.com/{i}",
                    "desc": f"Content {i}"
                }
                for i in range(15)
            ]
            
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {"result": {"items": mock_results}}
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query", max_results=max_results)
            response = await tool(args)
            
            assert len(response.results) <= max_results
            # Verify API was called with correct count parameter
            call_args = mock_instance.get.call_args
            params = call_args[1]["params"]
            assert params["count"] == min(max_results, 10)  # Qwant limits to 10
    
    @pytest.mark.asyncio
    async def test_locale_parameter(self):
        """Test search with different locales."""
        tool = self.get_component_function()
        
        locales = ["en_US", "fr_FR", "de_DE", "es_ES", "it_IT"]
        
        for locale in locales:
            with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_client.return_value.__aexit__.return_value = None
                
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {
                        "result": {
                            "items": [
                                {
                                    "type": "web",
                                    "title": f"Result for {locale}",
                                    "url": "https://example.com",
                                    "desc": f"Localized content for {locale}"
                                }
                            ]
                        }
                    }
                }
                mock_response.raise_for_status.return_value = None
                mock_instance.get.return_value = mock_response
                
                args = SearchArgs(query="test query", locale=locale)
                response = await tool(args)
                
                assert response.provider == "qwant"
                assert len(response.results) > 0
                
                # Verify locale was passed in request
                call_args = mock_instance.get.call_args
                params = call_args[1]["params"]
                assert params["locale"] == locale
    
    @pytest.mark.asyncio
    async def test_filters_non_web_results(self):
        """Test that only web results are included."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            # Mix of web and non-web results
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "result": {
                        "items": [
                            {
                                "type": "web",
                                "title": "Web Result",
                                "url": "https://example.com/web",
                                "desc": "This is a web result"
                            },
                            {
                                "type": "image",
                                "title": "Image Result",
                                "url": "https://example.com/image.jpg",
                                "desc": "This is an image result"
                            },
                            {
                                "type": "web",
                                "title": "Another Web Result",
                                "url": "https://example.com/web2",
                                "desc": "This is another web result"
                            }
                        ]
                    }
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query")
            response = await tool(args)
            
            # Should only include web results
            assert len(response.results) == 2
            assert all("web" in r.title.lower() for r in response.results)
    
    @pytest.mark.asyncio
    async def test_handles_missing_fields(self):
        """Test handling of missing fields in search results."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            # Results with various missing fields
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "result": {
                        "items": [
                            {
                                "type": "web",
                                "title": "Complete Result",
                                "url": "https://complete.com",
                                "desc": "Has all fields"
                            },
                            {
                                "type": "web",
                                "url": "https://notitle.com",
                                "desc": "Missing title"
                            },
                            {
                                "type": "web",
                                "title": "Missing URL",
                                "desc": "No URL field"
                            },
                            {
                                "type": "web",
                                "title": "Missing desc",
                                "url": "https://nodesc.com"
                            }
                        ]
                    }
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query")
            response = await tool(args)
            
            # Should handle all cases gracefully
            assert len(response.results) == 4
            assert response.results[0].title == "Complete Result"
            assert response.results[1].title == ""  # Missing title gets empty string
            assert response.results[2].url == ""    # Missing URL gets empty string
            assert response.results[3].snippet == ""  # Missing desc gets empty string
    
    @pytest.mark.asyncio
    async def test_empty_query_handling(self):
        """Test handling of empty or whitespace queries."""
        tool = self.get_component_function()
        
        empty_queries = ["", "   ", "\t\n"]
        
        for query in empty_queries:
            with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_client.return_value.__aexit__.return_value = None
                
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {"result": {"items": []}}
                }
                mock_response.raise_for_status.return_value = None
                mock_instance.get.return_value = mock_response
                
                args = SearchArgs(query=query, max_results=5)
                response = await tool(args)
                
                # Should handle empty queries gracefully
                assert isinstance(response, SearchResponse)
                assert response.query == query
                assert response.provider == "qwant"
    
    @pytest.mark.asyncio
    async def test_special_characters_in_query(self):
        """Test queries with special characters."""
        tool = self.get_component_function()
        
        special_queries = [
            "C++ programming",
            "what is 2+2?",
            "email@example.com",
            "search with spaces",
            '\"exact match query\"',
            "café résumé unicode",
            "special!@#$%^&*()chars"
        ]
        
        for query in special_queries:
            with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_client.return_value.__aexit__.return_value = None
                
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {
                        "result": {
                            "items": [
                                {
                                    "type": "web",
                                    "title": f"Result for {query}",
                                    "url": "https://example.com",
                                    "desc": "Content"
                                }
                            ]
                        }
                    }
                }
                mock_response.raise_for_status.return_value = None
                mock_instance.get.return_value = mock_response
                
                args = SearchArgs(query=query, max_results=5)
                response = await tool(args)
                
                assert isinstance(response, SearchResponse)
                assert response.query == query
                assert len(response.results) == 1
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        tool = self.get_component_function()
        
        malformed_responses = [
            {},  # Empty response
            {"data": {}},  # Missing result
            {"data": {"result": {}}},  # Missing items
            {"wrong": "structure"},  # Completely wrong
        ]
        
        for response_data in malformed_responses:
            with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_client.return_value.__aexit__.return_value = None
                
                mock_response = Mock()
                mock_response.json.return_value = response_data
                mock_response.raise_for_status.return_value = None
                mock_instance.get.return_value = mock_response
                
                args = SearchArgs(query="test query")
                response = await tool(args)
                
                # Should handle gracefully, returning empty results for well-formed but incomplete responses
                assert isinstance(response, SearchResponse)
                assert response.results == []
                assert response.provider == "qwant"
        
        # Test case that causes actual processing error
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.json.return_value = {"data": {"result": {"items": "not a list"}}}  # This will cause error
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query")
            response = await tool(args)
            
            # Should handle processing errors gracefully with fallback error response
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Search Error for: test query" in response.results[0].title
            assert response.provider == "qwant"
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of request timeouts."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            # Simulate timeout
            mock_instance.get.side_effect = Exception("Request timeout")
            
            args = SearchArgs(query="test query")
            response = await tool(args)
            
            # Should handle timeout gracefully
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Search Error" in response.results[0].title
            assert "Request timeout" in response.results[0].snippet
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self):
        """Test multiple concurrent searches."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            call_count = 0
            
            def create_instance():
                nonlocal call_count
                call_count += 1
                instance = AsyncMock()
                
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {
                        "result": {
                            "items": [
                                {
                                    "type": "web",
                                    "title": f"Concurrent Result {call_count}",
                                    "url": f"https://example.com/{call_count}",
                                    "desc": f"Content {call_count}"
                                }
                            ]
                        }
                    }
                }
                mock_response.raise_for_status.return_value = None
                instance.get.return_value = mock_response
                return instance
            
            mock_client.return_value.__aenter__.side_effect = create_instance
            mock_client.return_value.__aexit__.return_value = None
            
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
    async def test_unicode_content_search(self):
        """Test searching and handling Unicode content."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            # Unicode content in results
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "result": {
                        "items": [
                            {
                                "type": "web",
                                "title": "Résumé with café ☕",
                                "url": "https://unicode.com/café",
                                "desc": "Unicode test: 你好世界 🌍 Здравствуй мир"
                            },
                            {
                                "type": "web",
                                "title": "Math symbols: ∑ ∏ ∫ ≠ ≤ ≥",
                                "url": "https://symbols.com",
                                "desc": "Emojis: 😀 🎉 🚀 💻"
                            }
                        ]
                    }
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
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
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "result": {
                        "items": [
                            {
                                "type": "web",
                                "title": "Result for long query",
                                "url": "https://example.com",
                                "desc": "Content"
                            }
                        ]
                    }
                }
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query=long_query, max_results=5)
            response = await tool(args)
            
            assert isinstance(response, SearchResponse)
            assert response.query == long_query
            assert len(response.results) == 1
    
    @pytest.mark.asyncio
    async def test_user_agent_header(self):
        """Test that proper User-Agent header is sent."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {"result": {"items": []}}
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query")
            await tool(args)
            
            # Verify User-Agent header was sent
            call_args = mock_instance.get.call_args
            headers = call_args[1]["headers"]
            assert "User-Agent" in headers
            assert "Mozilla" in headers["User-Agent"]
    
    @pytest.mark.asyncio
    async def test_performance_with_many_results(self):
        """Test performance with a large number of results."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            # Create many mock results
            large_results = [
                {
                    "type": "web",
                    "title": f"Result {i}",
                    "url": f"https://example.com/{i}",
                    "desc": f"Content {i}"
                }
                for i in range(100)
            ]
            
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {"result": {"items": large_results}}
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query", max_results=10)
            
            import time
            start = time.time()
            response = await tool(args)
            duration = time.time() - start
            
            # Should handle large results efficiently
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 10  # Limited by max_results
            assert duration < 2.0  # Should process quickly
    
    @pytest.mark.asyncio
    async def test_json_parsing_error(self):
        """Test handling of JSON parsing errors."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.json.side_effect = Exception("Invalid JSON")
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query")
            response = await tool(args)
            
            # Should handle JSON parsing error gracefully
            assert isinstance(response, SearchResponse)
            assert len(response.results) == 1
            assert "Search Error" in response.results[0].title
            assert "Invalid JSON" in response.results[0].snippet
    
    @pytest.mark.asyncio
    async def test_search_parameters_validation(self):
        """Test that search parameters are properly set."""
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.qwant_search.tool.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_client.return_value.__aexit__.return_value = None
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {"result": {"items": []}}
            }
            mock_response.raise_for_status.return_value = None
            mock_instance.get.return_value = mock_response
            
            args = SearchArgs(query="test query", max_results=7, locale="fr_FR")
            await tool(args)
            
            # Verify all parameters were set correctly
            call_args = mock_instance.get.call_args
            params = call_args[1]["params"]
            
            assert params["q"] == "test query"
            assert params["count"] == 7
            assert params["locale"] == "fr_FR"
            assert params["safesearch"] == 1
            assert params["freshness"] == "all"
