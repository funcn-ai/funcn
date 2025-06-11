"""Test suite for url_content_parser_tool following best practices."""

import asyncio
import pytest

# Import the tool
from packages.funcn_registry.components.tools.url_content_parser_tool.tool import parse_url_content
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, Mock, patch


class TestUrlContentParserTool(BaseToolTest):
    """Test cases for URL content parsing tool."""

    component_name = "url_content_parser_tool"
    component_path = Path("packages/funcn_registry/components/tools/url_content_parser_tool")

    def get_component_function(self):
        """Get the main tool function."""
        return parse_url_content

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {"url": "https://example.com", "include_links": True, "max_length": 5000},
            {"url": "https://news.example.com/article", "include_links": False, "max_length": 10000},
            {"url": "https://blog.example.com/post", "include_links": True, "max_length": None},
        ]

    @pytest.mark.asyncio
    async def test_successful_content_parsing(self):
        """Test successful URL content parsing."""
        mock_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Example Page</title>
            <meta name="description" content="An example page for testing">
        </head>
        <body>
            <h1>Welcome to Example</h1>
            <p>This is a test paragraph with some content.</p>
            <a href="/about">About Us</a>
            <script>console.log('This should be removed');</script>
            <style>body { color: black; }</style>
        </body>
        </html>
        """

        expected_content = {
            "title": "Example Page",
            "content": "Welcome to Example\n\nThis is a test paragraph with some content.",
            "links": ["https://example.com/about"],
            "meta": {"description": "An example page for testing"},
        }

        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.headers = {"content-type": "text/html"}

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://example.com", include_links=True)

            assert result["title"] == "Example Page"
            assert "Welcome to Example" in result["content"]
            assert "This is a test paragraph" in result["content"]
            assert "console.log" not in result["content"]  # Scripts removed
            assert "body { color:" not in result["content"]  # Styles removed
            assert len(result["links"]) > 0

    @pytest.mark.asyncio
    async def test_content_without_links(self):
        """Test parsing content without extracting links."""
        mock_html = """
        <html>
        <body>
            <h1>Article Title</h1>
            <p>Article content here.</p>
            <a href="/link1">Link 1</a>
            <a href="/link2">Link 2</a>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.headers = {"content-type": "text/html"}

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://example.com", include_links=False)

            assert "Article Title" in result["content"]
            assert "links" not in result or len(result["links"]) == 0

    @pytest.mark.asyncio
    async def test_max_length_truncation(self):
        """Test content truncation with max_length."""
        # Create long content
        long_content = "A" * 10000
        mock_html = f"<html><body><p>{long_content}</p></body></html>"

        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.headers = {"content-type": "text/html"}

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://example.com", max_length=100)

            assert len(result["content"]) <= 100
            assert result["truncated"] is True

    @pytest.mark.asyncio
    async def test_metadata_extraction(self):
        """Test extraction of various metadata tags."""
        mock_html = """
        <html>
        <head>
            <title>Test Page</title>
            <meta name="author" content="Test Author">
            <meta name="keywords" content="test, parsing, content">
            <meta property="og:title" content="Open Graph Title">
            <meta property="og:description" content="OG Description">
            <meta name="twitter:card" content="summary">
        </head>
        <body>
            <h1>Content</h1>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.headers = {"content-type": "text/html"}

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://example.com")

            assert result["title"] == "Test Page"
            assert result["meta"]["author"] == "Test Author"
            assert result["meta"]["keywords"] == "test, parsing, content"
            assert result["meta"]["og:title"] == "Open Graph Title"

    @pytest.mark.asyncio
    async def test_relative_to_absolute_links(self):
        """Test conversion of relative links to absolute."""
        mock_html = """
        <html>
        <body>
            <a href="/page1">Relative Link 1</a>
            <a href="page2">Relative Link 2</a>
            <a href="../page3">Relative Link 3</a>
            <a href="https://external.com">External Link</a>
            <a href="//cdn.example.com/resource">Protocol-relative</a>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.headers = {"content-type": "text/html"}

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://example.com/articles/", include_links=True)

            links = result["links"]
            assert "https://example.com/page1" in links
            assert "https://example.com/articles/page2" in links
            assert "https://external.com" in links
            assert "https://cdn.example.com/resource" in links

    @pytest.mark.asyncio
    async def test_404_error_handling(self):
        """Test handling of 404 errors."""
        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.text = AsyncMock(return_value="Page not found")

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await parse_url_content("https://example.com/notfound")

            assert "404" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling of connection errors."""
        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Connection refused"))

            with pytest.raises(Exception) as exc_info:
                await parse_url_content("https://unreachable.com")

            assert "Connection refused" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_non_html_content(self):
        """Test handling of non-HTML content types."""
        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value='{"key": "value"}')
            mock_response.headers = {"content-type": "application/json"}

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://api.example.com/data.json")

            # Should still attempt to extract text content
            assert '{"key": "value"}' in result["content"]

    @pytest.mark.asyncio
    async def test_empty_page_handling(self):
        """Test handling of empty HTML pages."""
        mock_html = "<html><head><title></title></head><body></body></html>"

        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.headers = {"content-type": "text/html"}

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://example.com/empty")

            assert result["content"] == ""
            assert result["title"] == ""

    @pytest.mark.asyncio
    async def test_special_characters_handling(self):
        """Test handling of special characters and entities."""
        mock_html = """
        <html>
        <body>
            <p>Test &amp; verify &lt;special&gt; characters</p>
            <p>Unicode: Café • Résumé • 你好</p>
            <p>Emojis: 🎉 🚀 💻</p>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.headers = {"content-type": "text/html; charset=utf-8"}

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://example.com/special")

            assert "&" in result["content"]  # HTML entities decoded
            assert "<special>" in result["content"]
            assert "Café" in result["content"]
            assert "你好" in result["content"]
            assert "🎉" in result["content"]

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of request timeouts."""
        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.get = AsyncMock(side_effect=TimeoutError("Request timeout"))

            with pytest.raises(asyncio.TimeoutError) as exc_info:
                await parse_url_content("https://slow-site.com")

            assert "Request timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_redirect_handling(self):
        """Test handling of HTTP redirects."""
        mock_html = "<html><body><h1>Redirected Page</h1></body></html>"

        with patch("packages.funcn_registry.components.tools.url_content_parser_tool.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_html)
            mock_response.headers = {"content-type": "text/html"}
            mock_response.url = "https://example.com/new-location"

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await parse_url_content("https://example.com/old-location")

            assert "Redirected Page" in result["content"]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        assert isinstance(output, dict), "Output should be a dictionary"
        assert "content" in output, "Output must contain 'content' field"
        assert isinstance(output["content"], str), "Content should be a string"

        if input_data.get("include_links"):
            assert "links" in output, "Output should contain 'links' when requested"
            assert isinstance(output["links"], list), "Links should be a list"

        if "title" in output:
            assert isinstance(output["title"], str), "Title should be a string"

        if "meta" in output:
            assert isinstance(output["meta"], dict), "Meta should be a dictionary"

    @pytest.mark.unit
    def test_tool_docstring(self):
        """Test that the tool has a proper docstring."""
        assert parse_url_content.__doc__ is not None
        assert len(parse_url_content.__doc__) > 50
        assert "parse" in parse_url_content.__doc__.lower() or "content" in parse_url_content.__doc__.lower()
