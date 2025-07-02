"""Test suite for firecrawl_scrape_tool following best practices."""

import asyncio
import os
import pytest
from packages.funcn_registry.components.tools.firecrawl_scrape.tool import (
    FirecrawlScrapeArgs,
    FirecrawlScrapeResponse,
    PageMetadata,
    scrape_website,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class TestFirecrawlScrapeTool(BaseToolTest):
    """Test cases for Firecrawl web scraping tool."""

    component_name = "firecrawl_scrape_tool"
    component_path = Path("packages/funcn_registry/components/tools/firecrawl_scrape")

    def get_component_function(self):
        """Get the main tool function."""
        return scrape_website

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            FirecrawlScrapeArgs(
                url="https://example.com",
                formats=["markdown"],
                only_main_content=True,
                screenshot=False,
            ),
            FirecrawlScrapeArgs(
                url="https://example.com/article",
                formats=["markdown", "html"],
                only_main_content=False,
                wait_for=1000,
            ),
            FirecrawlScrapeArgs(
                url="https://news.example.com",
                formats=["markdown", "html", "rawHtml", "links"],
                only_main_content=True,
                screenshot=True,
                include_tags=["article", ".content"],
                exclude_tags=[".ads", "#sidebar"],
            ),
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        assert isinstance(output, FirecrawlScrapeResponse), "Output should be a FirecrawlScrapeResponse"
        assert hasattr(output, 'success')
        assert hasattr(output, 'url')
        assert output.url == input_data.url

        if output.success:
            # Check that requested formats are present if successful
            if "markdown" in input_data.formats:
                assert output.markdown is not None or output.error is not None
            if "html" in input_data.formats:
                assert output.html is not None or output.error is not None

    @pytest.mark.asyncio
    async def test_successful_scrape_markdown_only(self):
        """Test successful web scraping with markdown format only."""
        mock_response = {
            "success": True,
            "markdown": "# Example Website\n\nThis is the main content of the page.",
            "metadata": {
                "title": "Example Website",
                "description": "An example website for testing",
                "language": "en",
            },
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(
                    url="https://example.com",
                    formats=["markdown"],
                    only_main_content=True,
                )
                result = await scrape_website(args)

            assert result.success is True
            assert result.url == "https://example.com"
            assert result.markdown == "# Example Website\n\nThis is the main content of the page."
            assert result.html is None  # Not requested
            assert result.error is None
            assert result.metadata is not None
            assert result.metadata.title == "Example Website"

    @pytest.mark.asyncio
    async def test_scrape_with_multiple_formats(self):
        """Test scraping with multiple output formats."""
        mock_response = {
            "success": True,
            "markdown": "# Full Content\n\nMain article text here.",
            "html": "<h1>Full Content</h1><p>Main article text here.</p>",
            "rawHtml": "<!DOCTYPE html><html>...</html>",
            "links": ["https://example.com/link1", "https://example.com/link2"],
            "content": "Full Content Main article text here.",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(
                    url="https://example.com/full",
                    formats=["markdown", "html", "rawHtml", "links", "content"],
                    only_main_content=False,
                )
                result = await scrape_website(args)

            assert result.success is True
            assert result.markdown == "# Full Content\n\nMain article text here."
            assert result.html == "<h1>Full Content</h1><p>Main article text here.</p>"
            assert result.raw_html == "<!DOCTYPE html><html>...</html>"
            assert result.links == ["https://example.com/link1", "https://example.com/link2"]
            assert result.content == "Full Content Main article text here."

    @pytest.mark.asyncio
    async def test_scrape_with_screenshot(self):
        """Test scraping with screenshot capture."""
        mock_response = {
            "success": True,
            "markdown": "# Page with Screenshot",
            "screenshot": "base64encodedscreenshot==",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(
                    url="https://example.com/screenshot",
                    formats=["markdown", "screenshot"],
                    screenshot=True,
                )
                result = await scrape_website(args)

            assert result.success is True
            assert result.screenshot == "base64encodedscreenshot=="
            
            # Verify screenshot parameter was passed
            mock_app.scrape_url.assert_called_once()
            call_args = mock_app.scrape_url.call_args
            assert call_args[1]["params"]["screenshot"] is True

    @pytest.mark.asyncio
    async def test_scrape_with_css_selectors(self):
        """Test scraping with include and exclude CSS selectors."""
        mock_response = {
            "success": True,
            "markdown": "# Filtered Content",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(
                    url="https://example.com/filtered",
                    formats=["markdown"],
                    include_tags=["article", ".content", "#main"],
                    exclude_tags=[".ads", "#sidebar", "nav"],
                )
                result = await scrape_website(args)

            # Verify CSS selectors were passed correctly
            mock_app.scrape_url.assert_called_once()
            call_args = mock_app.scrape_url.call_args
            assert call_args[1]["params"]["includeTags"] == ["article", ".content", "#main"]
            assert call_args[1]["params"]["excludeTags"] == [".ads", "#sidebar", "nav"]

    @pytest.mark.asyncio
    async def test_scrape_with_wait_time(self):
        """Test scraping with wait time for dynamic content."""
        mock_response = {
            "success": True,
            "markdown": "# Dynamic Content\n\nLoaded after JavaScript execution.",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(
                    url="https://example.com/dynamic",
                    wait_for=5000,  # 5 second wait
                )
                result = await scrape_website(args)

            # Verify wait time was passed correctly
            mock_app.scrape_url.assert_called_once()
            call_args = mock_app.scrape_url.call_args
            assert call_args[1]["params"]["waitFor"] == 5000

    @pytest.mark.asyncio
    async def test_missing_api_key(self):
        """Test behavior when Firecrawl API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            args = FirecrawlScrapeArgs(url="https://example.com")
            result = await scrape_website(args)

            assert result.success is False
            assert result.error == "FIRECRAWL_API_KEY environment variable not set"
            assert result.markdown is None
            assert result.html is None

    @pytest.mark.asyncio
    async def test_scrape_failure_from_api(self):
        """Test handling of failed scrape response from API."""
        mock_response = {
            "success": False,
            "error": "Failed to load page: 404 Not Found",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url="https://example.com/notfound")
                result = await scrape_website(args)

            assert result.success is False
            assert result.error == "Failed to load page: 404 Not Found"
            assert result.markdown is None

    @pytest.mark.asyncio
    async def test_scrape_with_no_response(self):
        """Test handling when API returns None."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=None)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url="https://example.com/null")
                result = await scrape_website(args)

            assert result.success is False
            assert result.error == "No response from Firecrawl"

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test handling of exceptions during scraping."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(side_effect=Exception("Network error"))

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url="https://example.com/error")
                result = await scrape_website(args)

            assert result.success is False
            assert "Error scraping website: Network error" in result.error

    @pytest.mark.asyncio
    async def test_comprehensive_metadata_extraction(self):
        """Test extraction of comprehensive metadata."""
        mock_response = {
            "success": True,
            "markdown": "# Test Page",
            "metadata": {
                "title": "Test Page Title",
                "description": "Test page description",
                "language": "en-US",
                "keywords": "test, scraping, firecrawl",
                "robots": "index, follow",
                "ogTitle": "Open Graph Title",
                "ogDescription": "Open Graph Description",
                "ogUrl": "https://example.com/test",
                "ogImage": "https://example.com/image.jpg",
                "ogLocale": "en_US",
                "ogSiteName": "Example Site",
                "twitterCard": "summary_large_image",
                "twitterTitle": "Twitter Title",
                "twitterDescription": "Twitter Description",
                "twitterImage": "https://example.com/twitter-image.jpg",
            },
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url="https://example.com/metadata")
                result = await scrape_website(args)

            assert result.success is True
            assert result.metadata is not None
            assert result.metadata.title == "Test Page Title"
            assert result.metadata.description == "Test page description"
            assert result.metadata.language == "en-US"
            assert result.metadata.keywords == "test, scraping, firecrawl"
            assert result.metadata.robots == "index, follow"
            assert result.metadata.og_title == "Open Graph Title"
            assert result.metadata.og_description == "Open Graph Description"
            assert result.metadata.og_url == "https://example.com/test"
            assert result.metadata.og_image == "https://example.com/image.jpg"
            assert result.metadata.og_locale == "en_US"
            assert result.metadata.og_site_name == "Example Site"
            assert result.metadata.twitter_card == "summary_large_image"
            assert result.metadata.twitter_title == "Twitter Title"
            assert result.metadata.twitter_description == "Twitter Description"
            assert result.metadata.twitter_image == "https://example.com/twitter-image.jpg"

    @pytest.mark.asyncio
    async def test_partial_metadata_extraction(self):
        """Test extraction of partial metadata."""
        mock_response = {
            "success": True,
            "markdown": "# Partial Metadata Page",
            "metadata": {
                "title": "Only Title",
                "language": "en",
                # Other fields missing
            },
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url="https://example.com/partial")
                result = await scrape_website(args)

            assert result.success is True
            assert result.metadata is not None
            assert result.metadata.title == "Only Title"
            assert result.metadata.language == "en"
            assert result.metadata.description is None
            assert result.metadata.keywords is None

    @pytest.mark.asyncio
    async def test_remove_scripts_parameter(self):
        """Test the remove_scripts parameter."""
        mock_response = {
            "success": True,
            "markdown": "# Page without scripts",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                # Test with remove_scripts=False
                args = FirecrawlScrapeArgs(
                    url="https://example.com/scripts",
                    remove_scripts=False,
                )
                result = await scrape_website(args)

            mock_app.scrape_url.assert_called_once()
            call_args = mock_app.scrape_url.call_args
            assert call_args[1]["params"]["removeScripts"] is False

    @pytest.mark.asyncio
    async def test_format_validation(self):
        """Test validation of format parameter."""
        # Test invalid format
        with pytest.raises(ValueError) as exc_info:
            FirecrawlScrapeArgs(
                url="https://example.com",
                formats=["markdown", "invalid_format"],
            )
        assert "Invalid format: invalid_format" in str(exc_info.value)

        # Test valid formats
        valid_args = FirecrawlScrapeArgs(
            url="https://example.com",
            formats=["markdown", "html", "rawHtml", "content", "links", "screenshot"],
        )
        assert len(valid_args.formats) == 6

    @pytest.mark.asyncio
    async def test_empty_content_handling(self):
        """Test handling of empty content responses."""
        mock_response = {
            "success": True,
            "markdown": "",
            "metadata": {"title": "Empty Page"},
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url="https://example.com/empty")
                result = await scrape_website(args)

            assert result.success is True
            assert result.markdown == ""
            assert result.metadata.title == "Empty Page"

    @pytest.mark.asyncio
    async def test_special_characters_in_content(self):
        """Test handling of special characters and unicode."""
        mock_response = {
            "success": True,
            "markdown": "# Special Characters\n\n© 2024 • Émojis: 🔥 💻 🚀\n\nChinese: 你好\nArabic: مرحبا",
            "html": "<h1>Special Characters</h1><p>© 2024 • Émojis: 🔥 💻 🚀</p>",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(
                    url="https://example.com/unicode",
                    formats=["markdown", "html"],
                )
                result = await scrape_website(args)

            assert result.success is True
            assert "©" in result.markdown
            assert "🔥" in result.markdown
            assert "你好" in result.markdown
            assert "مرحبا" in result.markdown
            assert "🔥" in result.html

    @pytest.mark.asyncio
    async def test_rate_limit_exception(self):
        """Test handling of rate limit errors."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(side_effect=Exception("Rate limit exceeded"))

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url="https://example.com/ratelimit")
                result = await scrape_website(args)

            assert result.success is False
            assert "Rate limit exceeded" in result.error

    @pytest.mark.asyncio
    async def test_timeout_exception(self):
        """Test handling of timeout errors."""
        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(side_effect=TimeoutError("Request timeout"))

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url="https://example.com/timeout")
                result = await scrape_website(args)

            assert result.success is False
            assert "Request timeout" in result.error

    @pytest.mark.asyncio
    async def test_only_main_content_parameter(self):
        """Test the only_main_content parameter behavior."""
        mock_response = {
            "success": True,
            "markdown": "# Main Content Only",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                # Test with only_main_content=False
                args = FirecrawlScrapeArgs(
                    url="https://example.com/fullpage",
                    only_main_content=False,
                )
                result = await scrape_website(args)

            mock_app.scrape_url.assert_called_once()
            call_args = mock_app.scrape_url.call_args
            assert call_args[1]["params"]["onlyMainContent"] is False

    @pytest.mark.asyncio
    async def test_default_parameters(self):
        """Test default parameter values."""
        args = FirecrawlScrapeArgs(url="https://example.com")
        
        assert args.formats == ["markdown", "html"]
        assert args.only_main_content is True
        assert args.remove_scripts is True
        assert args.screenshot is False
        assert args.include_tags is None
        assert args.exclude_tags is None
        assert args.wait_for is None

    @pytest.mark.asyncio
    async def test_concurrent_scrapes(self):
        """Test concurrent scraping operations."""
        mock_responses = [
            {"success": True, "markdown": f"# Page {i}"} 
            for i in range(3)
        ]

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(side_effect=mock_responses)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                # Create multiple scrape tasks
                tasks = [
                    scrape_website(FirecrawlScrapeArgs(url=f"https://example.com/page{i}"))
                    for i in range(3)
                ]
                
                results = await asyncio.gather(*tasks)

            assert len(results) == 3
            for i, result in enumerate(results):
                assert result.success is True
                assert result.markdown == f"# Page {i}"

    @pytest.mark.asyncio
    async def test_model_validation(self):
        """Test Pydantic model validation."""
        # Test PageMetadata
        metadata = PageMetadata(
            title="Test",
            description=None,
            language="en",
        )
        assert metadata.title == "Test"
        assert metadata.description is None
        assert metadata.language == "en"

        # Test FirecrawlScrapeResponse
        response = FirecrawlScrapeResponse(
            success=True,
            url="https://example.com",
            markdown="# Test",
            error=None,
        )
        assert response.success is True
        assert response.url == "https://example.com"
        assert response.markdown == "# Test"
        assert response.html is None

    @pytest.mark.asyncio
    async def test_edge_case_empty_formats(self):
        """Test behavior with empty formats list."""
        mock_response = {
            "success": True,
            # No content since no formats requested
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(
                    url="https://example.com/empty-formats",
                    formats=[],
                )
                result = await scrape_website(args)

            assert result.success is True
            assert result.markdown is None
            assert result.html is None
            assert result.content is None

    @pytest.mark.asyncio
    async def test_complex_url_handling(self):
        """Test handling of complex URLs with query parameters."""
        test_url = "https://example.com/search?q=test&page=2&filter=true#section"
        mock_response = {
            "success": True,
            "markdown": "# Search Results",
        }

        with patch("packages.funcn_registry.components.tools.firecrawl_scrape.tool.FirecrawlApp") as mock_firecrawl:
            mock_app = Mock()
            mock_firecrawl.return_value = mock_app
            mock_app.scrape_url = Mock(return_value=mock_response)

            with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"}):
                args = FirecrawlScrapeArgs(url=test_url)
                result = await scrape_website(args)

            assert result.success is True
            assert result.url == test_url
            mock_app.scrape_url.assert_called_once_with(test_url, params=mock_app.scrape_url.call_args[1]["params"])

    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        assert scrape_website.__doc__ is not None
        assert len(scrape_website.__doc__) > 20
        assert "scrape" in scrape_website.__doc__.lower()
