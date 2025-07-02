"""Test suite for url_content_parser_tool following best practices."""

import asyncio
import httpx
import pytest

# Import the tool and models
from packages.funcn_registry.components.tools.url_content_parser.tool import URLParseArgs, parse_url_content
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, Mock, patch


class TestUrlContentParserTool(BaseToolTest):
    """Test cases for URL content parsing tool."""

    component_name = "url_content_parser_tool"
    component_path = Path("packages/funcn_registry/components/tools/url_content_parser")

    def get_component_function(self):
        """Get the main tool function."""
        return parse_url_content

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            URLParseArgs(url="https://example.com", max_chars=5000),
            URLParseArgs(url="https://news.example.com/article", max_chars=10000),
            URLParseArgs(url="https://blog.example.com/post", max_chars=8000),
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        assert isinstance(output, str), "Output should be a string"
        if not output.startswith("Error"):
            assert len(output) > 0, "Content should not be empty for successful parsing"
            if hasattr(input_data, 'max_chars'):
                assert len(output) <= input_data.max_chars + 3, "Content should respect max_chars limit"

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
            <p>Here is another paragraph with more text.</p>
            <a href="/about">About Us</a>
            <script>console.log('This should be removed');</script>
            <style>body { color: black; }</style>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            assert isinstance(result, str)
            assert "Welcome to Example" in result
            assert "This is a test paragraph" in result
            assert "console.log" not in result  # Scripts removed
            assert "body { color:" not in result  # Styles removed

    @pytest.mark.asyncio
    async def test_max_chars_truncation(self):
        """Test content truncation with max_chars."""
        # Create long content
        long_paragraph = "This is a very long paragraph. " * 100
        mock_html = f"""
        <html>
        <body>
            <p>{long_paragraph}</p>
            <p>{long_paragraph}</p>
            <p>{long_paragraph}</p>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com", max_chars=100)
            result = await parse_url_content(args)

            assert len(result) <= 103  # 100 + "..."
            assert result.endswith("...")

    @pytest.mark.asyncio
    async def test_whitespace_cleanup(self):
        """Test whitespace cleanup in extracted content."""
        mock_html = """
        <html>
        <body>
            <div>
                <p>  Text   with    extra     spaces  </p>
                <p>
                    Multiple
                    lines
                    of
                    text
                </p>
            </div>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            # Check that extra spaces are cleaned up
            assert "   " not in result  # No triple spaces
            assert result.count("  ") == 0  # No double spaces
            assert "Text with extra spaces" in result
            assert "Multiple lines of text" in result

    @pytest.mark.asyncio
    async def test_script_and_style_removal(self):
        """Test complete removal of script and style tags."""
        mock_html = """
        <html>
        <head>
            <style>
                .class1 { color: red; }
                #id1 { background: blue; }
            </style>
            <style type="text/css">
                body { margin: 0; }
            </style>
        </head>
        <body>
            <h1>Title</h1>
            <script>
                function test() {
                    console.log("test");
                }
            </script>
            <p>Content paragraph</p>
            <script src="external.js"></script>
            <script type="text/javascript">
                var x = 1;
            </script>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            # Check content is present
            assert "Title" in result
            assert "Content paragraph" in result
            
            # Check scripts and styles are removed
            assert "console.log" not in result
            assert "function test" not in result
            assert "var x" not in result
            assert "color: red" not in result
            assert "background: blue" not in result
            assert "margin: 0" not in result

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test handling of HTTP errors."""
        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            # Create a proper HTTPStatusError with mocked request and response
            mock_request = Mock()
            mock_error_response = Mock()
            mock_error_response.status_code = 404
            mock_response.raise_for_status = Mock(
                side_effect=httpx.HTTPStatusError("Client error '404 Not Found'", request=mock_request, response=mock_error_response)
            )
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com/notfound")
            result = await parse_url_content(args)

            assert result.startswith("Error parsing URL")
            assert "404" in result

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test handling of connection errors."""
        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=httpx.ConnectError("Connection refused")
            )
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://unreachable.com")
            result = await parse_url_content(args)

            assert result.startswith("Error parsing URL")
            assert "Connection refused" in result

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of request timeouts."""
        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=httpx.TimeoutException("Request timeout")
            )
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://slow-site.com")
            result = await parse_url_content(args)

            assert result.startswith("Error parsing URL")
            assert "timeout" in result.lower()

    @pytest.mark.asyncio
    async def test_empty_page_handling(self):
        """Test handling of empty HTML pages."""
        mock_html = "<html><head><title></title></head><body></body></html>"

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com/empty")
            result = await parse_url_content(args)

            assert isinstance(result, str)
            assert len(result.strip()) == 0 or result == ""

    @pytest.mark.asyncio
    async def test_special_characters_and_unicode(self):
        """Test handling of special characters and unicode."""
        mock_html = """
        <html>
        <body>
            <p>Test &amp; verify &lt;special&gt; characters</p>
            <p>Unicode: Café • Résumé • 你好 • مرحبا</p>
            <p>Emojis: 🎉 🚀 💻 🌍</p>
            <p>Math symbols: ∑ ∏ ∫ √ ∞</p>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode('utf-8')
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com/special")
            result = await parse_url_content(args)

            # HTML entities should be decoded
            assert "&" in result
            assert "<special>" in result
            
            # Unicode should be preserved
            assert "Café" in result
            assert "你好" in result
            assert "مرحبا" in result
            
            # Emojis should be preserved
            assert "🎉" in result
            
            # Math symbols
            assert "∑" in result

    @pytest.mark.asyncio
    async def test_nested_tags_handling(self):
        """Test handling of deeply nested HTML tags."""
        mock_html = """
        <html>
        <body>
            <div>
                <section>
                    <article>
                        <header>
                            <h1>Main Title</h1>
                        </header>
                        <div class="content">
                            <p>First <strong>paragraph</strong> with <em>emphasis</em>.</p>
                            <blockquote>
                                <p>A quote within the article.</p>
                            </blockquote>
                        </div>
                    </article>
                </section>
            </div>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            assert "Main Title" in result
            assert "First paragraph with emphasis" in result
            assert "A quote within the article" in result

    @pytest.mark.asyncio
    async def test_malformed_html_handling(self):
        """Test handling of malformed HTML."""
        mock_html = """
        <html>
        <body>
            <p>Unclosed paragraph
            <div>Unclosed div
            <p>Another paragraph</p>
            <span>Text with <b>unclosed bold
            </span>
        """  # Missing closing tags

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            # BeautifulSoup should handle malformed HTML gracefully
            assert "Unclosed paragraph" in result
            assert "Unclosed div" in result
            assert "Another paragraph" in result
            assert "unclosed bold" in result

    @pytest.mark.asyncio
    async def test_non_html_content(self):
        """Test handling of non-HTML content types."""
        mock_content = '{"key": "value", "number": 123, "array": [1, 2, 3]}'

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_content.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://api.example.com/data.json")
            result = await parse_url_content(args)

            # Should still attempt to extract text content
            assert '{"key": "value"' in result

    @pytest.mark.asyncio
    async def test_table_content_extraction(self):
        """Test extraction of content from HTML tables."""
        mock_html = """
        <html>
        <body>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                        <th>City</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>John Doe</td>
                        <td>30</td>
                        <td>New York</td>
                    </tr>
                    <tr>
                        <td>Jane Smith</td>
                        <td>25</td>
                        <td>London</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            # All table content should be extracted
            assert "Name" in result
            assert "Age" in result
            assert "City" in result
            assert "John Doe" in result
            assert "Jane Smith" in result
            assert "30" in result
            assert "25" in result
            assert "New York" in result
            assert "London" in result

    @pytest.mark.asyncio
    async def test_form_content_extraction(self):
        """Test extraction of content from forms."""
        mock_html = """
        <html>
        <body>
            <form>
                <label for="name">Full Name:</label>
                <input type="text" id="name" placeholder="Enter your name">
                
                <label for="email">Email:</label>
                <input type="email" id="email" placeholder="your@email.com">
                
                <label for="message">Message:</label>
                <textarea id="message" placeholder="Type your message here">Default text</textarea>
                
                <button type="submit">Submit Form</button>
            </form>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            # Form labels and text should be extracted
            assert "Full Name:" in result
            assert "Email:" in result
            assert "Message:" in result
            assert "Submit Form" in result
            assert "Default text" in result

    @pytest.mark.asyncio
    async def test_comment_removal(self):
        """Test that HTML comments are not included in output."""
        mock_html = """
        <html>
        <body>
            <!-- This is a comment that should not appear -->
            <p>Visible content</p>
            <!-- Another comment
                 spanning multiple lines
                 should also be removed -->
            <div>More visible content</div>
            <!--[if IE]>
                <p>IE specific content</p>
            <![endif]-->
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            assert "Visible content" in result
            assert "More visible content" in result
            assert "This is a comment" not in result
            assert "Another comment" not in result
            assert "IE specific content" not in result

    @pytest.mark.asyncio
    async def test_meta_tag_content(self):
        """Test that meta tag content is not included in extracted text."""
        mock_html = """
        <html>
        <head>
            <meta name="description" content="This is meta description">
            <meta name="keywords" content="test, keywords, meta">
            <meta property="og:title" content="Open Graph Title">
            <title>Page Title</title>
        </head>
        <body>
            <h1>Body Content</h1>
            <p>This is the actual page content.</p>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            # Body content should be present
            assert "Body Content" in result
            assert "This is the actual page content" in result
            
            # Meta content should not be extracted as text
            assert "This is meta description" not in result
            assert "test, keywords, meta" not in result
            assert "Open Graph Title" not in result

    @pytest.mark.asyncio
    async def test_list_content_extraction(self):
        """Test extraction of content from lists."""
        mock_html = """
        <html>
        <body>
            <h2>Ordered List</h2>
            <ol>
                <li>First item</li>
                <li>Second item</li>
                <li>Third item</li>
            </ol>
            
            <h2>Unordered List</h2>
            <ul>
                <li>Bullet point one</li>
                <li>Bullet point two
                    <ul>
                        <li>Nested item 1</li>
                        <li>Nested item 2</li>
                    </ul>
                </li>
                <li>Bullet point three</li>
            </ul>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            # All list items should be extracted
            assert "First item" in result
            assert "Second item" in result
            assert "Third item" in result
            assert "Bullet point one" in result
            assert "Bullet point two" in result
            assert "Bullet point three" in result
            assert "Nested item 1" in result
            assert "Nested item 2" in result

    @pytest.mark.asyncio
    async def test_invalid_url_handling(self):
        """Test handling of invalid URLs."""
        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(
                side_effect=httpx.InvalidURL("Invalid URL format")
            )
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="not-a-valid-url")
            result = await parse_url_content(args)

            assert result.startswith("Error parsing URL")
            assert "Invalid URL" in result

    @pytest.mark.asyncio
    async def test_redirect_handling(self):
        """Test that redirects are handled by httpx."""
        mock_html = "<html><body><h1>Redirected Page</h1></body></html>"

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com/old-location")
            result = await parse_url_content(args)

            assert "Redirected Page" in result

    @pytest.mark.asyncio
    async def test_large_content_handling(self):
        """Test handling of very large pages."""
        # Create content that's larger than default max_chars
        large_content = "Large content block. " * 500  # ~10,000 chars
        mock_html = f"""
        <html>
        <body>
            <div>{large_content}</div>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.content = mock_html.encode()
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Test with default max_chars (8000)
            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            assert len(result) <= 8003  # 8000 + "..."
            assert result.endswith("...")

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test concurrent URL parsing."""
        mock_html1 = "<html><body><h1>Page 1</h1></body></html>"
        mock_html2 = "<html><body><h1>Page 2</h1></body></html>"
        mock_html3 = "<html><body><h1>Page 3</h1></body></html>"

        async def mock_get(url, *args, **kwargs):
            mock_response = AsyncMock()
            if "page1" in url:
                mock_response.content = mock_html1.encode()
            elif "page2" in url:
                mock_response.content = mock_html2.encode()
            else:
                mock_response.content = mock_html3.encode()
            mock_response.raise_for_status = Mock()
            return mock_response

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = mock_get
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Run multiple requests concurrently
            tasks = [
                parse_url_content(URLParseArgs(url="https://example.com/page1")),
                parse_url_content(URLParseArgs(url="https://example.com/page2")),
                parse_url_content(URLParseArgs(url="https://example.com/page3"))
            ]
            
            results = await asyncio.gather(*tasks)

            assert "Page 1" in results[0]
            assert "Page 2" in results[1]
            assert "Page 3" in results[2]

    @pytest.mark.asyncio
    async def test_encoding_issues(self):
        """Test handling of various encodings."""
        # Test with different encoding declaration
        mock_html = """
        <?xml version="1.0" encoding="ISO-8859-1"?>
        <html>
        <body>
            <p>Special chars: café, naïve</p>
        </body>
        </html>
        """

        with patch("packages.funcn_registry.components.tools.url_content_parser.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            # BeautifulSoup should handle encoding detection
            mock_response.content = mock_html.encode('iso-8859-1')
            mock_response.raise_for_status = Mock()
            
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            args = URLParseArgs(url="https://example.com")
            result = await parse_url_content(args)

            # BeautifulSoup should handle encoding properly
            assert "Special chars" in result

    @pytest.mark.asyncio
    async def test_url_validation(self):
        """Test URLParseArgs validation."""
        # Valid URL
        args = URLParseArgs(url="https://example.com")
        assert args.url == "https://example.com"
        assert args.max_chars == 8000  # default

        # Custom max_chars
        args = URLParseArgs(url="https://example.com", max_chars=5000)
        assert args.max_chars == 5000

    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        assert parse_url_content.__doc__ is not None
        assert len(parse_url_content.__doc__) > 20
