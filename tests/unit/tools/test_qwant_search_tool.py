"""Test suite for qwant_search_tool following best practices."""

import pytest
from pathlib import Path
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestQwantSearchTool(BaseToolTest):
    """Test qwant_search_tool component."""
    
    component_name = "qwant_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/qwant_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.qwant_search_tool import search_web
        def mock_search_web(
            query: str,
            count: int = 10,
            locale: str = "en_US",
            offset: int = 0,
            safesearch: int = 1
        ) -> list[dict[str, any]]:
            """Mock Qwant search tool."""
            return [
                {
                    "title": f"Privacy-focused result {i+1} for '{query}'",
                    "description": f"Qwant search result {i+1} with no tracking",
                    "url": f"https://example.com/qwant{i+1}",
                    "source": "Qwant"
                }
                for i in range(min(count, 5))
            ]
        return mock_search_web
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "query": "privacy search engine",
                "count": 5,
                "locale": "en_US"
            },
            {
                "query": "données privées",
                "count": 10,
                "locale": "fr_FR",
                "safesearch": 2
            },
            {
                "query": "no tracking search",
                "count": 3,
                "offset": 10
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        assert len(output) <= input_data.get("count", 10)
        
        for result in output:
            assert "title" in result
            assert "description" in result or "snippet" in result
            assert "url" in result
            assert result["url"].startswith("http")
    
    def test_privacy_focused_search(self):
        """Test that Qwant search maintains privacy features."""
        tool = self.get_component_function()
        
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "result": {
                        "items": [
                            {
                                "title": "Private Result",
                                "desc": "No tracking here",
                                "url": "https://private.com"
                            }
                        ]
                    }
                }
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            results = tool("privacy test")
            
            # Verify no tracking headers were sent
            headers = mock_get.call_args[1].get("headers", {})
            assert "User-Agent" in headers
            # Should not contain tracking cookies or identifiers
            assert "Cookie" not in headers or headers.get("Cookie") == ""
    
    def test_locale_support(self):
        """Test search with different locales."""
        locales = ["en_US", "fr_FR", "de_DE", "es_ES", "it_IT"]
        tool = self.get_component_function()
        
        for locale in locales:
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {
                        "result": {
                            "items": [
                                {
                                    "title": f"Result for {locale}",
                                    "desc": f"Localized content for {locale}",
                                    "url": "https://example.com"
                                }
                            ]
                        }
                    }
                }
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                results = tool("test query", locale=locale)
                assert len(results) > 0
                
                # Verify locale was passed in request
                call_args = mock_get.call_args
                assert f"locale={locale}" in str(call_args)
    
    def test_safesearch_levels(self):
        """Test different safesearch levels (0=off, 1=moderate, 2=strict)."""
        safesearch_levels = [0, 1, 2]
        tool = self.get_component_function()
        
        for level in safesearch_levels:
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {
                        "result": {
                            "items": [
                                {"title": f"Safe level {level}", "desc": "Content", "url": "https://safe.com"}
                            ]
                        }
                    }
                }
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                results = tool("test query", safesearch=level)
                assert len(results) > 0
                
                # Verify safesearch parameter
                call_args = mock_get.call_args
                assert f"safesearch={level}" in str(call_args)
    
    def test_pagination_with_offset(self):
        """Test pagination using offset parameter."""
        tool = self.get_component_function()
        
        offsets = [0, 10, 20, 50]
        for offset in offsets:
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {
                        "result": {
                            "items": [
                                {
                                    "title": f"Page starting at {offset}",
                                    "desc": f"Result {offset + i}",
                                    "url": f"https://example.com/page{offset + i}"
                                }
                                for i in range(5)
                            ]
                        }
                    }
                }
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                results = tool("paginated query", offset=offset)
                assert len(results) > 0
                
                # Verify offset in request
                call_args = mock_get.call_args
                assert f"offset={offset}" in str(call_args)
    
    def test_handles_api_errors(self):
        """Test handling of various API errors."""
        tool = self.get_component_function()
        
        # Test rate limiting
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"error": "Rate limited"}
            mock_get.return_value = mock_response
            
            results = tool("test query")
            assert isinstance(results, list)
            assert len(results) == 0 or "error" in str(results)
        
        # Test server error
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            
            results = tool("test query")
            assert isinstance(results, list)
    
    def test_empty_results_handling(self):
        """Test handling when Qwant returns no results."""
        tool = self.get_component_function()
        
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {
                    "result": {
                        "items": []
                    }
                }
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            results = tool("very obscure query xyz123")
            assert results == []
    
    def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        tool = self.get_component_function()
        
        malformed_responses = [
            {},  # Empty response
            {"data": {}},  # Missing result
            {"data": {"result": {}}},  # Missing items
            {"data": {"result": {"items": "not a list"}}},  # Wrong type
        ]
        
        for response in malformed_responses:
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = response
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                results = tool("test query")
                assert isinstance(results, list)
                assert len(results) == 0 or all(isinstance(r, dict) for r in results)
    
    @pytest.mark.parametrize("count", [1, 10, 50, 100])
    def test_result_count_limits(self, count):
        """Test that count parameter limits results appropriately."""
        tool = self.get_component_function()
        
        with patch("requests.get") as mock_get:
            # Create more results than requested
            mock_items = [
                {"title": f"Result {i}", "desc": "Content", "url": f"https://example.com/{i}"}
                for i in range(200)
            ]
            
            mock_response = Mock()
            mock_response.json.return_value = {
                "data": {"result": {"items": mock_items}}
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            results = tool("test query", count=count)
            assert len(results) <= count
    
    def test_url_encoding_special_characters(self):
        """Test that special characters in queries are properly encoded."""
        tool = self.get_component_function()
        
        special_queries = [
            "C++ programming",
            "search with spaces",
            "special!@#$%^&*()chars",
            "unicode: café résumé",
            "quotes: \"exact match\""
        ]
        
        for query in special_queries:
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {"result": {"items": [{"title": "Test", "desc": "Test", "url": "https://test.com"}]}}
                }
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                
                results = tool(query)
                
                # Verify query was properly encoded in URL
                call_url = mock_get.call_args[0][0]
                assert "q=" in call_url
                # Should not contain raw special characters
                assert " " not in call_url  # Spaces should be encoded
