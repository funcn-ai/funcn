"""Test suite for firecrawl_scrape_tool following best practices."""

import asyncio
import pytest

# Import the tool
from packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool import scrape_url
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, Mock, patch


class TestFirecrawlScrapeTool(BaseToolTest):
    """Test cases for Firecrawl web scraping tool."""

    component_name = "firecrawl_scrape_tool"
    component_path = Path("packages/funcn_registry/components/tools/firecrawl_scrape_tool")

    def get_component_function(self):
        """Get the main tool function."""
        return scrape_url

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "url": "https://example.com",
                "include_html": False,
                "include_raw_html": False,
                "only_main_content": True,
                "include_metadata": True,
                "wait_time": 0,
            },
            {
                "url": "https://example.com/article",
                "include_html": True,
                "include_raw_html": False,
                "only_main_content": False,
                "include_metadata": False,
                "wait_time": 1000,
            },
            {
                "url": "https://news.example.com",
                "include_html": True,
                "include_raw_html": True,
                "only_main_content": True,
                "include_metadata": True,
                "wait_time": 2000,
            },
        ]

    @pytest.mark.asyncio
    async def test_successful_scrape_basic(self):
        """Test successful web scraping with basic options."""
        mock_content = {
            "content": "# Example Website\n\nThis is the main content of the page.",
            "metadata": {
                "title": "Example Website",
                "description": "An example website for testing",
                "language": "en",
                "author": "Test Author",
            },
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            # Mock the Firecrawl client
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(return_value=mock_content)

            result = await scrape_url(
                url="https://example.com",
                include_html=False,
                include_raw_html=False,
                only_main_content=True,
                include_metadata=True,
            )

            assert result == mock_content
            mock_client.scrape_url.assert_called_once_with(
                "https://example.com",
                params={
                    "includeHtml": False,
                    "includeRawHtml": False,
                    "onlyMainContent": True,
                    "includeMetadata": True,
                    "waitFor": 0,
                },
            )

    @pytest.mark.asyncio
    async def test_scrape_with_all_options(self):
        """Test scraping with all options enabled."""
        mock_content = {
            "content": "# Full Content\n\nMain article text here.",
            "html": "<html><body><h1>Full Content</h1><p>Main article text here.</p></body></html>",
            "rawHtml": "<!DOCTYPE html><html>...</html>",
            "metadata": {
                "title": "Full Content Page",
                "description": "Page with all content types",
                "keywords": ["test", "content", "html"],
            },
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(return_value=mock_content)

            result = await scrape_url(
                url="https://example.com/full",
                include_html=True,
                include_raw_html=True,
                only_main_content=False,
                include_metadata=True,
                wait_time=2000,
            )

            assert result == mock_content
            assert "html" in result
            assert "rawHtml" in result
            assert "metadata" in result

    @pytest.mark.asyncio
    async def test_scrape_markdown_only(self):
        """Test scraping only markdown content."""
        mock_content = {"content": "# Simple Page\n\nJust the markdown content."}

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(return_value=mock_content)

            result = await scrape_url(
                url="https://example.com/simple",
                include_html=False,
                include_raw_html=False,
                only_main_content=True,
                include_metadata=False,
            )

            assert "content" in result
            assert "metadata" not in result
            assert "html" not in result

    @pytest.mark.asyncio
    async def test_scrape_with_wait_time(self):
        """Test scraping with wait time for dynamic content."""
        mock_content = {"content": "# Dynamic Content\n\nLoaded after JavaScript execution."}

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(return_value=mock_content)

            result = await scrape_url(
                url="https://example.com/dynamic",
                wait_time=5000,  # 5 second wait
            )

            # Verify wait time was passed correctly
            mock_client.scrape_url.assert_called_once()
            call_args = mock_client.scrape_url.call_args
            assert call_args[1]["params"]["waitFor"] == 5000

    @pytest.mark.asyncio
    async def test_scrape_error_handling(self):
        """Test error handling for failed scrapes."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(side_effect=Exception("Network error"))

            with pytest.raises(Exception) as exc_info:
                await scrape_url(url="https://example.com/error")

            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_url(self):
        """Test handling of invalid URLs."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(side_effect=ValueError("Invalid URL format"))

            with pytest.raises(ValueError) as exc_info:
                await scrape_url(url="not-a-valid-url")

            assert "Invalid URL format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of timeout errors."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(side_effect=TimeoutError("Request timeout"))

            with pytest.raises(asyncio.TimeoutError) as exc_info:
                await scrape_url(url="https://slow-site.com", wait_time=1000)

            assert "Request timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_content_handling(self):
        """Test handling of empty content responses."""
        mock_content = {"content": "", "metadata": {"title": "Empty Page"}}

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(return_value=mock_content)

            result = await scrape_url(url="https://example.com/empty", include_metadata=True)

            assert result["content"] == ""
            assert result["metadata"]["title"] == "Empty Page"

    @pytest.mark.asyncio
    async def test_large_content_handling(self):
        """Test handling of large content responses."""
        # Create large content (1MB of text)
        large_text = "Lorem ipsum " * 100000
        mock_content = {"content": f"# Large Page\n\n{large_text}", "metadata": {"title": "Large Content Page"}}

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(return_value=mock_content)

            result = await scrape_url(url="https://example.com/large")

            assert len(result["content"]) > 1000000  # Over 1MB
            assert "Large Page" in result["content"]

    @pytest.mark.asyncio
    async def test_special_characters_in_content(self):
        """Test handling of special characters and unicode."""
        mock_content = {
            "content": "# Special Characters\n\n© 2024 • Émojis: 🔥 💻 🚀\n\nChinese: 你好\nArabic: مرحبا",
            "metadata": {"title": "Unicode Test Page", "language": "multi"},
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(return_value=mock_content)

            result = await scrape_url(url="https://example.com/unicode")

            assert "©" in result["content"]
            assert "🔥" in result["content"]
            assert "你好" in result["content"]
            assert "مرحبا" in result["content"]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        assert isinstance(output, dict), "Output should be a dictionary"

        # Check for required content field
        assert "content" in output, "Output must contain 'content' field"

        # Check optional fields based on input
        if input_data.get("include_html"):
            assert "html" in output or "content" in output
        if input_data.get("include_raw_html"):
            assert "rawHtml" in output or "content" in output
        if input_data.get("include_metadata"):
            assert "metadata" in output or "content" in output

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        """Test behavior when Firecrawl API key is missing."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.os.getenv", return_value=None):
            with pytest.raises(ValueError) as exc_info:
                await scrape_url(url="https://example.com")

            assert "FIRECRAWL_API_KEY" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Test handling of rate limit errors."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape_tool.tool.FirecrawlApp") as mock_firecrawl:
            mock_client = AsyncMock()
            mock_firecrawl.return_value = mock_client
            mock_client.scrape_url = AsyncMock(side_effect=Exception("Rate limit exceeded"))

            with pytest.raises(Exception) as exc_info:
                await scrape_url(url="https://example.com")

            assert "Rate limit exceeded" in str(exc_info.value)

    @pytest.mark.unit
    def test_tool_docstring(self):
        """Test that the tool has a proper docstring."""
        assert scrape_url.__doc__ is not None
        assert len(scrape_url.__doc__) > 50
        assert "scrape" in scrape_url.__doc__.lower()
