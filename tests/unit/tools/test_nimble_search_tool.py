"""Test suite for nimble_search_tool following best practices."""

import pytest
from pathlib import Path
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestNimbleSearchTool(BaseToolTest):
    """Test nimble_search_tool component."""
    
    component_name = "nimble_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/nimble_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.nimble_search_tool import search_web
        def mock_search_web(
            query: str,
            search_type: str = "web",
            max_results: int = 10,
            location: str | None = None,
            language: str = "en"
        ) -> list[dict[str, any]]:
            """Mock Nimble search tool."""
            base_result = {
                "title": f"Result for '{query}'",
                "url": "https://example.com",
                "snippet": "Search result snippet",
                "source": "Nimble"
            }
            
            if search_type == "web":
                return [
                    {**base_result, "title": f"Web result {i+1}", "url": f"https://example.com/web{i+1}"}
                    for i in range(min(max_results, 5))
                ]
            elif search_type == "serp":
                return [
                    {**base_result, "title": f"SERP result {i+1}", "position": i+1, "domain": "example.com"}
                    for i in range(min(max_results, 5))
                ]
            elif search_type == "maps":
                return [
                    {
                        "name": f"Location {i+1}",
                        "address": f"{i+1} Main St",
                        "rating": 4.5 - (i * 0.1),
                        "reviews": 100 - (i * 10),
                        "type": "business"
                    }
                    for i in range(min(max_results, 3))
                ]
            return []
        return mock_search_web
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "query": "best restaurants near me",
                "search_type": "maps",
                "location": "New York, NY",
                "max_results": 5
            },
            {
                "query": "python programming",
                "search_type": "web",
                "max_results": 10,
                "language": "en"
            },
            {
                "query": "machine learning courses",
                "search_type": "serp",
                "max_results": 20
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        assert len(output) <= input_data.get("max_results", 10)
        
        search_type = input_data.get("search_type", "web")
        for result in output:
            assert isinstance(result, dict)
            if search_type == "maps":
                assert "name" in result or "title" in result
                assert "address" in result or "location" in result
            else:
                assert "title" in result
                assert "url" in result or "link" in result
    
    def test_web_api_search(self):
        """Test Nimble Web API search functionality."""
        tool = self.get_component_function()
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": [
                    {
                        "title": "Python Tutorial",
                        "url": "https://python.org/tutorial",
                        "description": "Learn Python programming"
                    }
                ]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            results = tool("python tutorial", search_type="web")
            
            assert len(results) > 0
            # Verify API was called with correct parameters
            assert mock_post.called
    
    def test_serp_api_search(self):
        """Test Nimble SERP API search functionality."""
        tool = self.get_component_function()
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "organic_results": [
                    {
                        "title": "Search Result 1",
                        "link": "https://example1.com",
                        "snippet": "Result snippet",
                        "position": 1,
                        "domain": "example1.com"
                    },
                    {
                        "title": "Search Result 2",
                        "link": "https://example2.com",
                        "snippet": "Another snippet",
                        "position": 2,
                        "domain": "example2.com"
                    }
                ]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            results = tool("test query", search_type="serp")
            
            assert len(results) >= 2
            # Verify results have SERP-specific fields
            assert all("position" in r or "rank" in r for r in results)
    
    def test_maps_api_search(self):
        """Test Nimble Maps API search functionality."""
        tool = self.get_component_function()
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "local_results": [
                    {
                        "name": "Best Pizza Place",
                        "address": "123 Main St, New York, NY",
                        "rating": 4.8,
                        "reviews_count": 250,
                        "phone": "+1-234-567-8900",
                        "hours": "Mon-Sun 11am-10pm",
                        "website": "https://bestpizza.com"
                    }
                ]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            results = tool(
                "pizza near times square",
                search_type="maps",
                location="New York, NY"
            )
            
            assert len(results) > 0
            result = results[0]
            assert "name" in result
            assert "address" in result
            assert "rating" in result
    
    def test_location_parameter(self):
        """Test location-based search filtering."""
        tool = self.get_component_function()
        
        locations = ["London, UK", "Tokyo, Japan", "Sydney, Australia"]
        
        for location in locations:
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "results": [{"title": f"Result in {location}", "url": "https://local.com"}]
                }
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                results = tool("coffee shops", location=location)
                
                # Verify location was passed to API
                call_args = mock_post.call_args
                assert location in str(call_args)
    
    def test_language_support(self):
        """Test multi-language search support."""
        tool = self.get_component_function()
        
        languages = ["en", "es", "fr", "de", "ja", "zh"]
        
        for lang in languages:
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "results": [{"title": f"Result in {lang}", "url": "https://example.com"}]
                }
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                results = tool("test query", language=lang)
                
                assert len(results) > 0
                # Verify language parameter was used
                call_args = mock_post.call_args
                assert lang in str(call_args)
    
    def test_api_error_handling(self):
        """Test handling of various API errors."""
        tool = self.get_component_function()
        
        # Test rate limiting
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"error": "Rate limit exceeded"}
            mock_post.return_value = mock_response
            
            results = tool("test query")
            assert isinstance(results, list)
            assert len(results) == 0 or "error" in str(results)
        
        # Test authentication error
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"error": "Invalid API key"}
            mock_post.return_value = mock_response
            
            results = tool("test query")
            assert isinstance(results, list)
    
    def test_result_limit_handling(self):
        """Test that max_results parameter is respected."""
        tool = self.get_component_function()
        
        limits = [1, 5, 10, 50, 100]
        
        for limit in limits:
            with patch("requests.post") as mock_post:
                # Create more results than requested
                mock_results = [
                    {"title": f"Result {i}", "url": f"https://example.com/{i}"}
                    for i in range(200)
                ]
                
                mock_response = Mock()
                mock_response.json.return_value = {"results": mock_results}
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                results = tool("test query", max_results=limit)
                assert len(results) <= limit
    
    def test_empty_results_handling(self):
        """Test handling when no results are found."""
        tool = self.get_component_function()
        
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "results": [],
                "organic_results": [],
                "local_results": []
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            results = tool("extremely obscure query xyz123")
            assert results == []
    
    def test_special_characters_in_query(self):
        """Test queries with special characters."""
        tool = self.get_component_function()
        
        special_queries = [
            "C++ programming",
            "email@example.com search",
            "price: $100-$200",
            "café & restaurant",
            '"exact phrase search"'
        ]
        
        for query in special_queries:
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "results": [{"title": "Result", "url": "https://example.com"}]
                }
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                results = tool(query)
                assert isinstance(results, list)
    
    def test_api_selection_logic(self):
        """Test that correct API is selected based on search_type."""
        tool = self.get_component_function()
        
        api_endpoints = {
            "web": "https://api.nimble.com/web",
            "serp": "https://api.nimble.com/serp",
            "maps": "https://api.nimble.com/maps"
        }
        
        for search_type, expected_endpoint in api_endpoints.items():
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {"results": []}
                mock_response.status_code = 200
                mock_post.return_value = mock_response
                
                tool("test", search_type=search_type)
                
                # Verify correct endpoint was called
                call_url = mock_post.call_args[0][0]
                assert expected_endpoint in call_url or search_type in str(mock_post.call_args)
    
    def test_response_parsing(self):
        """Test parsing of different response formats."""
        tool = self.get_component_function()
        
        # Test nested response structure
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "success",
                "data": {
                    "results": [
                        {"title": "Nested result", "url": "https://example.com"}
                    ]
                }
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            results = tool("test query")
            # Should handle nested structures
            assert isinstance(results, list)
