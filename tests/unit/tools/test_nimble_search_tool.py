"""Test suite for nimble_search_tool following best practices."""

import asyncio
import json
import os
import pytest
import requests

# Import the actual tool functions and models
from packages.sygaldry_registry.components.tools.nimble_search.tool import (
    NimbleMapsSearchArgs,
    NimbleSearchArgs,
    NimbleSERPSearchArgs,
    get_content,
    nimble_maps_search,
    nimble_search,
    nimble_serp_search,
)
from pathlib import Path
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import MagicMock, Mock, patch


class TestNimbleSearchTool(BaseToolTest):
    """Test nimble_search_tool component."""

    component_name = "nimble_search_tool"
    component_path = Path("packages/sygaldry_registry/components/tools/nimble_search")

    def get_component_function(self):
        """Import the tool function."""
        return nimble_serp_search  # Using SERP as the primary function

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            NimbleSERPSearchArgs(
                query="python programming",
                search_engine="google_search",
                country="US",
                locale="en"
            ),
            NimbleSERPSearchArgs(
                query="machine learning courses",
                search_engine="bing_search",
                page=2
            ),
            NimbleSERPSearchArgs(
                query="artificial intelligence research",
                search_engine="duckduckgo_search",
                parse=True
            )
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, dict)
        assert "query" in output
        assert output["query"] == input_data.query

        if "error" not in output:
            assert "results" in output
            assert isinstance(output["results"], list)
            assert "sources" in output
            assert isinstance(output["sources"], list)

    def test_component_json_valid(self):
        """Test that component.json is valid."""
        component_json = self.component_path / "component.json"
        with open(component_json) as f:
            data = json.load(f)

        # Check required fields - accept both author and authors
        assert "name" in data
        assert "description" in data
        assert "author" in data or "authors" in data  # Accept either field
        assert "version" in data
        assert "type" in data

    def test_tool_basic_functionality(self):
        """Test that the tool function works with basic inputs."""
        tool = self.get_component_function()

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {
                        "entities": {
                            "OrganicResult": [
                                {
                                    "title": "Test Result",
                                    "url": "https://example.com",
                                    "snippet": "Test snippet"
                                }
                            ]
                        }
                    }
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.get_content") as mock_get_content:
                    mock_get_content.return_value = "Mocked content"

                    # Test with each input
                    for input_data in self.get_test_inputs():
                        output = tool(input_data)
                        self.validate_tool_output(output, input_data)

    def test_web_api_search(self):
        """Test Nimble Web API search functionality."""
        # Patch the module-level NIMBLE_TOKEN variable
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {
                        "entities": {},
                        "metadata": {}
                    },
                    "html_content": "<html>Test content</html>"
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSearchArgs(query="python tutorial", parse=True)
                result = nimble_search(args)

                assert isinstance(result, dict)
                assert result["query"] == "python tutorial"
                assert "parsed_data" in result
                assert mock_post.called

                # Verify API call parameters
                call_args = mock_post.call_args
                assert call_args[1]["headers"]["Authorization"] == "Basic test_key"
                assert "google.com/search" in call_args[1]["json"]["url"]

    def test_serp_api_search(self):
        """Test Nimble SERP API search functionality."""
        tool = self.get_component_function()

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {
                        "entities": {
                            "OrganicResult": [
                                {
                                    "title": "Search Result 1",
                                    "url": "https://example1.com",
                                    "snippet": "Result snippet"
                                },
                                {
                                    "title": "Search Result 2",
                                    "url": "https://example2.com",
                                    "snippet": "Another snippet"
                                }
                            ]
                        }
                    }
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                # Mock get_content to avoid actual HTTP requests
                with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.get_content") as mock_get_content:
                    mock_get_content.return_value = "Mocked content"

                    args = NimbleSERPSearchArgs(query="test query", search_engine="google_search")
                    result = tool(args)

                    assert result["query"] == "test query"
                    assert result["search_engine"] == "google_search"
                    assert len(result["results"]) == 2
                    assert len(result["sources"]) == 2
                    assert result["results"][0]["content"] == "Mocked content"

    def test_maps_api_search(self):
        """Test Nimble Maps API search functionality."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {
                        "entities": {
                            "PlaceResult": [
                                {
                                    "name": "Best Pizza Place",
                                    "address": "123 Main St, New York, NY",
                                    "rating": 4.8,
                                    "review_count": 250,
                                    "phone": "+1-234-567-8900",
                                    "website": "https://bestpizza.com",
                                    "coordinates": {"lat": 40.7128, "lng": -74.0060},
                                    "place_id": "ChIJrTLr-GyuEmsRBfy61i59si0"
                                }
                            ]
                        }
                    }
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleMapsSearchArgs(
                    query="pizza near times square",
                    latitude=40.7580,
                    longitude=-73.9855,
                    radius=1000
                )
                result = nimble_maps_search(args)

                assert result["query"] == "pizza near times square"
                assert len(result["places"]) == 1
                place = result["places"][0]
                assert place["name"] == "Best Pizza Place"
                assert place["rating"] == 4.8
                assert place["coordinates"]["lat"] == 40.7128

    def test_missing_api_key(self):
        """Test handling when API key is missing."""
        # Clear API key
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", ""):
            args = NimbleSERPSearchArgs(query="test query")
            result = nimble_serp_search(args)

            assert "error" in result
            assert "NIMBLE_API_KEY environment variable not set" in result["error"]

    def test_location_parameters(self):
        """Test location-based search filtering."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            countries = ["US", "UK", "JP", "AU"]
            locales = ["en", "en-GB", "ja", "en-AU"]

            for country, locale in zip(countries, locales, strict=False):
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"OrganicResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleSERPSearchArgs(
                        query="coffee shops",
                        country=country,
                        locale=locale
                    )
                    nimble_serp_search(args)

                    # Verify parameters were passed
                    call_json = mock_post.call_args[1]["json"]
                    assert call_json["country"] == country
                    assert call_json["locale"] == locale

    def test_search_engines(self):
        """Test different search engine support."""
        search_engines = [
            "google_search",
            "bing_search",
            "duckduckgo_search",
            "yahoo_search",
            "baidu_search"
        ]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            for engine in search_engines:
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"OrganicResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleSERPSearchArgs(
                        query="test query",
                        search_engine=engine
                    )
                    result = nimble_serp_search(args)

                    assert result["search_engine"] == engine
                    call_json = mock_post.call_args[1]["json"]
                    assert call_json["search_engine"] == engine

    def test_api_error_handling(self):
        """Test handling of various API errors."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            # Test rate limiting
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 429
                mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
                mock_post.return_value = mock_response

                args = NimbleSERPSearchArgs(query="test query")
                result = nimble_serp_search(args)
                assert "error" in result
                assert "Rate limit exceeded" in result["error"]

            # Test authentication error
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 401
                mock_response.raise_for_status.side_effect = Exception("Invalid API key")
                mock_post.return_value = mock_response

                args = NimbleSERPSearchArgs(query="test query")
                result = nimble_serp_search(args)
                assert "error" in result
                assert "Invalid API key" in result["error"]

    def test_pagination(self):
        """Test pagination support in SERP API."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            pages = [1, 2, 5, 10]

            for page in pages:
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"OrganicResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleSERPSearchArgs(query="test query", page=page)
                    nimble_serp_search(args)

                    call_json = mock_post.call_args[1]["json"]
                    assert call_json["page"] == page

    def test_empty_results_handling(self):
        """Test handling when no results are found."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {"entities": {"OrganicResult": []}}
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSERPSearchArgs(query="extremely obscure query xyz123")
                result = nimble_serp_search(args)

                assert result["results"] == []
                assert result["sources"] == []

    def test_special_characters_in_query(self):
        """Test queries with special characters."""
        special_queries = [
            "C++ programming",
            "email@example.com search",
            "price: $100-$200",
            "café & restaurant",
            '"exact phrase search"',
            "unicode test: 你好世界",
            "emoji test: 🚀 🎉"
        ]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            for query in special_queries:
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"OrganicResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleSERPSearchArgs(query=query)
                    result = nimble_serp_search(args)

                    assert result["query"] == query

    def test_get_content_function(self):
        """Test the get_content helper function."""
        # Test successful content extraction
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = b"""
            <html>
                <body>
                    <script>console.log('test');</script>
                    <style>body { color: red; }</style>
                    <p>First paragraph</p>
                    <p>Second paragraph</p>
                    <div>Other content</div>
                </body>
            </html>
            """
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            content = get_content("https://example.com")

            # Scripts and styles should be removed
            assert "console.log" not in content
            assert "color: red" not in content
            # Paragraphs should be included
            assert "First paragraph" in content
            assert "Second paragraph" in content

        # Test error handling
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection error")

            content = get_content("https://example.com")
            assert "Error fetching content" in content
            assert "Connection error" in content

    def test_result_limit_enforcement(self):
        """Test that result limits are enforced."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                # Create many results
                mock_results = [
                    {"title": f"Result {i}", "url": f"https://example.com/{i}", "snippet": f"Snippet {i}"}
                    for i in range(50)
                ]

                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {"entities": {"OrganicResult": mock_results}}
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSERPSearchArgs(query="test query")
                result = nimble_serp_search(args)

                # Should be limited to 10 results
                assert len(result["results"]) == 10
                assert len(result["sources"]) == 10

    def test_render_and_parse_options(self):
        """Test render and parse options."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            # Test with parse=False
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {"html_content": "<html>Raw HTML</html>"}
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSearchArgs(query="test", parse=False, render=False)
                result = nimble_search(args)

                assert "html_content" in result
                call_json = mock_post.call_args[1]["json"]
                assert call_json["parse"] is False
                assert call_json["render"] is False

    def test_coordinates_in_maps_search(self):
        """Test coordinate-based maps search."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {"entities": {"PlaceResult": []}}
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleMapsSearchArgs(
                    query="restaurants",
                    latitude=40.7128,
                    longitude=-74.0060,
                    radius=5000
                )
                nimble_maps_search(args)

                call_json = mock_post.call_args[1]["json"]
                assert "coordinates" in call_json
                assert call_json["coordinates"]["latitude"] == 40.7128
                assert call_json["coordinates"]["longitude"] == -74.0060
                assert call_json["radius"] == 5000

    def test_timeout_handling(self):
        """Test handling of request timeouts."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_post.side_effect = Exception("Request timeout")

                args = NimbleSERPSearchArgs(query="test query")
                result = nimble_serp_search(args)

                assert "error" in result
                assert "Request timeout" in result["error"]

    def test_content_fetching_limit(self):
        """Test that content is only fetched for top 3 results."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                # Create 10 results
                mock_results = [
                    {"title": f"Result {i}", "url": f"https://example.com/{i}", "snippet": f"Snippet {i}"}
                    for i in range(10)
                ]

                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {"entities": {"OrganicResult": mock_results}}
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.get_content") as mock_get_content:
                    mock_get_content.return_value = "Fetched content"

                    args = NimbleSERPSearchArgs(query="test query")
                    result = nimble_serp_search(args)

                    # get_content should only be called 3 times
                    assert mock_get_content.call_count == 3
                    # Only first 3 results should have content
                    for i in range(3):
                        assert result["results"][i]["content"] == "Fetched content"
                    for i in range(3, 10):
                        assert "content" not in result["results"][i]

    def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            malformed_responses = [
                {},  # Empty response
                {"parsing": {}},  # Missing entities
                {"parsing": {"entities": {}}},  # Missing OrganicResult
                {"wrong_key": "wrong_value"},  # Completely wrong structure
            ]

            for response_data in malformed_responses:
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = response_data
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleSERPSearchArgs(query="test query")
                    result = nimble_serp_search(args)

                    # Should handle gracefully
                    assert "error" not in result
                    assert result["results"] == []
                    assert result["sources"] == []

    def test_web_api_url_encoding(self):
        """Test URL encoding in Web API."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {"parsing": {}}
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSearchArgs(query="test query with spaces & special chars")
                nimble_search(args)

                call_json = mock_post.call_args[1]["json"]
                # URL should be properly encoded
                assert "test%20query%20with%20spaces" in call_json["url"]
                assert "%26%20special%20chars" in call_json["url"]

    def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            queries = ["query1", "query2", "query3", "query4", "query5"]

            with patch("requests.post") as mock_post:
                def side_effect(*args, **kwargs):
                    response = Mock()
                    query = kwargs["json"]["query"]
                    response.json.return_value = {
                        "parsing": {
                            "entities": {
                                "OrganicResult": [
                                    {"title": f"Result for {query}", "url": f"https://example.com/{query}", "snippet": "Test"}
                                ]
                            }
                        }
                    }
                    response.status_code = 200
                    response.raise_for_status.return_value = None
                    return response

                mock_post.side_effect = side_effect

                # Execute multiple searches
                results = []
                for query in queries:
                    args = NimbleSERPSearchArgs(query=query)
                    result = nimble_serp_search(args)
                    results.append(result)

                # Verify all succeeded with correct data
                assert len(results) == 5
                for i, result in enumerate(results):
                    assert result["query"] == queries[i]
                    assert f"Result for {queries[i]}" in result["results"][0]["title"]

    def test_get_content_edge_cases(self):
        """Test get_content function with various edge cases."""
        # Test timeout
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Request timed out")
            content = get_content("https://example.com")
            assert "Error fetching content" in content
            assert "Request timed out" in content

        # Test empty HTML
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = b"<html></html>"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            content = get_content("https://example.com")
            assert content == ""

        # Test HTML with only scripts and styles
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = b"""
            <html>
                <head>
                    <script>var x = 1;</script>
                    <style>body { margin: 0; }</style>
                </head>
                <body>
                    <script>console.log('test');</script>
                    <style>.hidden { display: none; }</style>
                </body>
            </html>
            """
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            content = get_content("https://example.com")
            assert "var x" not in content
            assert "console.log" not in content
            assert "margin: 0" not in content

        # Test content length limiting
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            long_text = "x" * 10000
            mock_response.content = f"<html><body><p>{long_text}</p></body></html>".encode()
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            content = get_content("https://example.com")
            assert len(content) <= 5000
            assert content == "x" * 5000

    def test_malformed_html_handling(self):
        """Test handling of malformed HTML in get_content."""
        malformed_html_cases = [
            b"<html><body><p>Unclosed paragraph",  # Missing closing tags
            b"<html><body><p>Text with & unescaped < characters > </p></body></html>",
            b"<html><body><<p>>Double brackets<</p>></body></html>",
            b"\xff\xfe<html><body><p>Invalid encoding start</p></body></html>",  # Invalid bytes
        ]

        for html_content in malformed_html_cases:
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.content = html_content
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                # Should not crash
                content = get_content("https://example.com")
                assert isinstance(content, str)

    def test_unicode_and_emoji_handling(self):
        """Test Unicode and emoji handling in all APIs."""
        unicode_tests = [
            "café résumé naïve 北京 🍕🎉",
            "🚀 rocket science 🧪 research",
            "математика физика наука",
            "🐍 Python programming 💻 tutorials",
            "日本語 テスト データ",
            "العربية اختبار البيانات",
        ]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            for test_query in unicode_tests:
                # Test SERP API
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"OrganicResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleSERPSearchArgs(query=test_query)
                    result = nimble_serp_search(args)
                    assert result["query"] == test_query

                # Test Maps API
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"PlaceResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleMapsSearchArgs(query=test_query)
                    result = nimble_maps_search(args)
                    assert result["query"] == test_query

    def test_very_long_queries(self):
        """Test handling of very long search queries."""
        # Create a very long query
        long_query = "test " * 500  # 2500 characters

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {"entities": {"OrganicResult": []}}
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSERPSearchArgs(query=long_query)
                result = nimble_serp_search(args)

                assert result["query"] == long_query
                # Check that the query was sent
                call_json = mock_post.call_args[1]["json"]
                assert call_json["query"] == long_query

    def test_various_http_status_codes(self):
        """Test handling of various HTTP status codes."""
        status_scenarios = [
            (400, "Bad Request"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
        ]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            for status_code, status_text in status_scenarios:
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.status_code = status_code
                    mock_response.raise_for_status.side_effect = requests.HTTPError(f"{status_code} {status_text}")
                    mock_post.return_value = mock_response

                    args = NimbleSERPSearchArgs(query="test")
                    result = nimble_serp_search(args)

                    assert "error" in result
                    assert status_text in result["error"] or str(status_code) in result["error"]

    def test_network_errors(self):
        """Test handling of various network errors."""
        network_errors = [
            requests.ConnectionError("Connection refused"),
            requests.Timeout("Request timed out"),
            requests.TooManyRedirects("Too many redirects"),
            requests.RequestException("Generic request error"),
        ]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            for error in network_errors:
                with patch("requests.post") as mock_post:
                    mock_post.side_effect = error

                    args = NimbleSERPSearchArgs(query="test")
                    result = nimble_serp_search(args)

                    assert "error" in result
                    assert "request failed" in result["error"].lower()

    def test_json_decode_errors(self):
        """Test handling of invalid JSON responses."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.side_effect = ValueError("Invalid JSON")
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSERPSearchArgs(query="test")
                result = nimble_serp_search(args)

                assert "error" in result
                assert "Invalid JSON" in result["error"] or "Unexpected error" in result["error"]

    def test_coordinate_edge_cases(self):
        """Test edge cases for coordinate-based searches."""
        coordinate_tests = [
            # Valid edge coordinates
            (90.0, 180.0, "North Pole at International Date Line"),
            (-90.0, -180.0, "South Pole at International Date Line"),
            (0.0, 0.0, "Null Island (0,0)"),
            # Very precise coordinates
            (40.7127281, -74.0059945, "Very precise NYC coordinates"),
            # Near boundary coordinates
            (89.999999, 179.999999, "Almost North Pole"),
        ]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            for lat, lon, description in coordinate_tests:
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"PlaceResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleMapsSearchArgs(
                        query=f"test {description}",
                        latitude=lat,
                        longitude=lon,
                        radius=1000
                    )
                    result = nimble_maps_search(args)

                    # Should handle without error
                    assert "error" not in result

                    # Verify coordinates were sent correctly
                    call_json = mock_post.call_args[1]["json"]
                    assert call_json["coordinates"]["latitude"] == lat
                    assert call_json["coordinates"]["longitude"] == lon

    def test_radius_edge_cases(self):
        """Test edge cases for radius parameter."""
        radius_tests = [
            1,  # Minimum reasonable radius
            50000,  # 50km radius
            100000,  # 100km radius
            1000000,  # 1000km radius (very large)
        ]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            for radius in radius_tests:
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"PlaceResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleMapsSearchArgs(
                        query="restaurants",
                        latitude=40.7128,
                        longitude=-74.0060,
                        radius=radius
                    )
                    result = nimble_maps_search(args)

                    assert "error" not in result
                    call_json = mock_post.call_args[1]["json"]
                    assert call_json["radius"] == radius

    def test_concurrent_api_calls_with_failures(self):
        """Test concurrent API calls with some failures."""
        queries = ["query1", "query2", "query3", "query4", "query5"]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                def side_effect(*args, **kwargs):
                    query = kwargs["json"]["query"]
                    # Make query2 and query4 fail
                    if query in ["query2", "query4"]:
                        raise requests.ConnectionError("Connection failed")

                    response = Mock()
                    response.json.return_value = {
                        "parsing": {
                            "entities": {
                                "OrganicResult": [
                                    {"title": f"Success for {query}", "url": f"https://example.com/{query}", "snippet": "Test"}
                                ]
                            }
                        }
                    }
                    response.status_code = 200
                    response.raise_for_status.return_value = None
                    return response

                mock_post.side_effect = side_effect

                results = []
                for query in queries:
                    args = NimbleSERPSearchArgs(query=query)
                    result = nimble_serp_search(args)
                    results.append(result)

                # Check results
                assert "error" not in results[0]  # query1 should succeed
                assert "error" in results[1]  # query2 should fail
                assert "error" not in results[2]  # query3 should succeed
                assert "error" in results[3]  # query4 should fail
                assert "error" not in results[4]  # query5 should succeed

    def test_html_entities_in_content(self):
        """Test handling of HTML entities in content extraction."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.content = b"""
            <html>
                <body>
                    <p>Price: &pound;100 &amp; &euro;120</p>
                    <p>Copyright &copy; 2024 &mdash; All rights reserved</p>
                    <p>Temperature: 25&deg;C &rarr; 77&deg;F</p>
                    <p>&quot;Quote&quot; &lt;tag&gt;</p>
                </body>
            </html>
            """
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            content = get_content("https://example.com")

            # BeautifulSoup should decode entities
            assert "£" in content or "&pound;" in content
            assert "€" in content or "&euro;" in content
            assert "©" in content or "&copy;" in content
            assert "°" in content or "&deg;" in content

    def test_different_locale_country_combinations(self):
        """Test various locale and country combinations."""
        locale_country_pairs = [
            ("en-US", "US"),
            ("en-GB", "UK"),
            ("fr-FR", "FR"),
            ("de-DE", "DE"),
            ("ja-JP", "JP"),
            ("zh-CN", "CN"),
            ("es-ES", "ES"),
            ("pt-BR", "BR"),
            ("ru-RU", "RU"),
            ("ar-SA", "SA"),
        ]

        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            for locale, country in locale_country_pairs:
                with patch("requests.post") as mock_post:
                    mock_response = Mock()
                    mock_response.json.return_value = {
                        "parsing": {"entities": {"OrganicResult": []}}
                    }
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                    mock_post.return_value = mock_response

                    args = NimbleSERPSearchArgs(
                        query="test",
                        locale=locale,
                        country=country
                    )
                    result = nimble_serp_search(args)

                    assert "error" not in result
                    call_json = mock_post.call_args[1]["json"]
                    assert call_json["locale"] == locale
                    assert call_json["country"] == country

    def test_place_result_missing_fields(self):
        """Test handling of place results with missing fields."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {
                        "entities": {
                            "PlaceResult": [
                                {
                                    "name": "Place 1",
                                    # Missing most fields
                                },
                                {
                                    "name": "Place 2",
                                    "rating": 4.5,
                                    # Missing other fields
                                },
                                {
                                    # All fields present
                                    "name": "Place 3",
                                    "address": "123 Main St",
                                    "rating": 4.8,
                                    "review_count": 100,
                                    "phone": "555-1234",
                                    "website": "https://example.com",
                                    "coordinates": {"lat": 40.7, "lng": -74.0},
                                    "place_id": "ABC123"
                                }
                            ]
                        }
                    }
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleMapsSearchArgs(query="test places")
                result = nimble_maps_search(args)

                assert len(result["places"]) == 3

                # Check first place with minimal data
                place1 = result["places"][0]
                assert place1["name"] == "Place 1"
                assert place1["address"] == ""
                assert place1["rating"] is None
                assert place1["review_count"] is None

                # Check second place with partial data
                place2 = result["places"][1]
                assert place2["name"] == "Place 2"
                assert place2["rating"] == 4.5

                # Check third place with all data
                place3 = result["places"][2]
                assert place3["name"] == "Place 3"
                assert place3["rating"] == 4.8
                assert place3["coordinates"]["lat"] == 40.7

    def test_parse_false_option(self):
        """Test behavior when parse=False."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            # Test SERP API with parse=False
            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "html_content": "<html>Raw HTML content</html>"
                    # No parsing data when parse=False
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSERPSearchArgs(query="test", parse=False)
                result = nimble_serp_search(args)

                # Should handle missing parsing data gracefully
                assert result["results"] == []
                assert result["sources"] == []

    def test_web_api_html_truncation(self):
        """Test that Web API truncates HTML content properly."""
        with patch("packages.sygaldry_registry.components.tools.nimble_search.tool.NIMBLE_TOKEN", "test_key"):
            with patch("requests.post") as mock_post:
                # Create very long HTML content
                long_html = "<html>" + "x" * 5000 + "</html>"

                mock_response = Mock()
                mock_response.json.return_value = {
                    "parsing": {},
                    "html_content": long_html
                }
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                args = NimbleSearchArgs(query="test", parse=False)
                result = nimble_search(args)

                # HTML content should be truncated to 1000 chars
                assert len(result["html_content"]) == 1000
                assert result["html_content"] == long_html[:1000]

    def test_exception_in_get_content(self):
        """Test various exceptions in get_content function."""
        exceptions = [
            AttributeError("NoneType has no attribute"),
            UnicodeDecodeError('utf-8', b'\xff', 0, 1, 'invalid start byte'),
            MemoryError("Out of memory"),
            KeyboardInterrupt("User interrupted"),
        ]

        for exc in exceptions[:-1]:  # Skip KeyboardInterrupt for safety
            with patch("requests.get") as mock_get:
                mock_get.side_effect = exc

                content = get_content("https://example.com")
                assert "Error fetching content" in content
                assert str(exc) in content or type(exc).__name__ in content
