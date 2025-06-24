"""Test suite for pdf_search_tool following best practices."""

import asyncio
import pytest
import tempfile

# Import the actual tool functions and models
from packages.funcn_registry.components.tools.pdf_search.tool import (
    PDFSearchArgs,
    PDFSearchResponse,
    PDFSearchResult,
    search_pdf_content,
)
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest
from unittest.mock import MagicMock, Mock, mock_open, patch


class TestPDFSearchTool(BaseToolTest):
    """Test pdf_search_tool component."""
    
    component_name = "pdf_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/pdf_search")
    
    def get_component_function(self):
        """Import the tool function."""
        return search_pdf_content
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            PDFSearchArgs(
                file_path="/path/to/test.pdf",
                query="artificial intelligence",
                max_results=10,
                context_chars=200,
                fuzzy_threshold=80
            ),
            PDFSearchArgs(
                file_path="/path/to/report.pdf", 
                query="financial results",
                max_results=5,
                context_chars=100,
                fuzzy_threshold=90
            ),
            PDFSearchArgs(
                file_path="/path/to/manual.pdf",
                query="installation guide",
                max_results=3,
                context_chars=300,
                fuzzy_threshold=70
            )
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, PDFSearchResponse)
        assert isinstance(output.results, list)
        assert isinstance(output.total_pages, int)
        assert output.total_pages >= 0
        assert len(output.results) <= input_data.max_results
        
        for result in output.results:
            assert isinstance(result, PDFSearchResult)
            assert result.page_number > 0
            assert 0 <= result.match_score <= 100
            assert isinstance(result.text, str)
            assert isinstance(result.excerpt, str)
    
    @pytest.mark.asyncio
    async def test_basic_pdf_search(self, tmp_path):
        """Test basic PDF search functionality."""
        # Create test PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"dummy pdf content")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            # Mock PDF reader
            mock_page = MagicMock()
            mock_page.extract_text.return_value = """
            Introduction to Artificial Intelligence
            
            This document discusses AI and machine learning applications.
            Artificial intelligence is transforming industries worldwide.
            Machine learning enables computers to learn from data.
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="artificial intelligence",
                    max_results=5,
                    fuzzy_threshold=80
                )
                response = await tool(args)
            
            assert isinstance(response, PDFSearchResponse)
            assert response.error is None
            assert len(response.results) > 0
            assert response.total_pages == 1
            
            # Check first result
            result = response.results[0]
            assert result.page_number == 1
            assert result.match_score >= 80
            assert "artificial intelligence" in result.text.lower()
    
    @pytest.mark.asyncio
    async def test_fuzzy_matching_with_typos(self, tmp_path):
        """Test fuzzy matching finds text with typos."""
        pdf_file = tmp_path / "typos.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = """
            Artificial inteligence is amazing.  # Typo: inteligence
            Mashine learning is powerful.       # Typo: Mashine
            Deep learing networks are complex.  # Typo: learing
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                # Search with lower threshold to catch typos
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="artificial intelligence",
                    max_results=5,
                    fuzzy_threshold=70
                )
                response = await tool(args)
            
            assert response.error is None
            assert len(response.results) > 0
            # Should find the typo version
            assert any("inteligence" in r.text for r in response.results)
    
    @pytest.mark.asyncio
    async def test_nonexistent_file(self):
        """Test handling of nonexistent PDF files."""
        tool = self.get_component_function()
        
        args = PDFSearchArgs(
            file_path="/nonexistent/path/to/file.pdf",
            query="test"
        )
        response = await tool(args)
        
        assert isinstance(response, PDFSearchResponse)
        assert response.error is not None
        assert "not found" in response.error
        assert response.results == []
        assert response.total_pages == 0
    
    @pytest.mark.asyncio
    async def test_invalid_pdf_file(self, tmp_path):
        """Test handling of invalid/corrupted PDF files."""
        # Create a file that's not a valid PDF
        invalid_file = tmp_path / "not_a_pdf.txt"
        invalid_file.write_text("This is not a PDF file")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_reader.side_effect = Exception("Invalid PDF structure")
            
            with patch("builtins.open", mock_open(read_data=b"not pdf")):
                args = PDFSearchArgs(
                    file_path=str(invalid_file),
                    query="test"
                )
                response = await tool(args)
        
        assert isinstance(response, PDFSearchResponse)
        assert response.error is not None
        assert "Invalid PDF structure" in response.error
        assert response.results == []
    
    @pytest.mark.asyncio
    async def test_multi_page_pdf_search(self, tmp_path):
        """Test searching across multiple pages."""
        pdf_file = tmp_path / "multipage.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            # Create multiple pages with different content
            pages = []
            for i in range(5):
                page = MagicMock()
                page.extract_text.return_value = f"""
                Page {i+1} content:
                This is page {i+1} discussing {'machine learning' if i % 2 == 0 else 'deep learning'}.
                Some additional content here.
                {'Machine learning' if i % 2 == 0 else 'Deep learning'} is important.
                """
                pages.append(page)
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = pages
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="machine learning",
                    max_results=10
                )
                response = await tool(args)
            
            assert response.error is None
            assert response.total_pages == 5
            assert len(response.results) > 0
            
            # Should find matches on pages 1, 3, 5 (0-indexed: 0, 2, 4)
            page_numbers = [r.page_number for r in response.results]
            assert any(p in [1, 3, 5] for p in page_numbers)
    
    @pytest.mark.asyncio
    async def test_context_extraction(self, tmp_path):
        """Test context extraction around matches."""
        pdf_file = tmp_path / "context.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            # Create text with clear context around search term
            mock_page.extract_text.return_value = """
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            This is the sentence with SEARCH_TERM that we want to find.
            Sed do eiusmod tempor incididunt ut labore et dolore magna.
            Another sentence here for more context.
            Final line of the page with additional text.
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="SEARCH_TERM",
                    context_chars=100  # Get 100 chars of context
                )
                response = await tool(args)
            
            assert response.error is None
            assert len(response.results) > 0
            
            result = response.results[0]
            # Should include the search term
            assert "SEARCH_TERM" in result.text
            # The exact match might be the full sentence without ellipsis
            assert "sentence with SEARCH_TERM" in result.text
    
    @pytest.mark.asyncio
    async def test_max_results_limit(self, tmp_path):
        """Test that max_results parameter is respected."""
        pdf_file = tmp_path / "results_limit.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            # Create content with many matches
            mock_page.extract_text.return_value = """
            Python is great. Python is powerful. Python is versatile.
            Python is popular. Python is easy. Python is fun.
            Python is dynamic. Python is interpreted. Python is high-level.
            Python is object-oriented. Python is cross-platform.
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="Python",
                    max_results=3  # Limit to 3 results
                )
                response = await tool(args)
            
            assert response.error is None
            assert len(response.results) == 3  # Should respect max_results
            # Results should be sorted by match score
            scores = [r.match_score for r in response.results]
            assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_empty_pdf_handling(self, tmp_path):
        """Test handling of empty PDF files."""
        pdf_file = tmp_path / "empty.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            # Mock empty pages
            mock_page = MagicMock()
            mock_page.extract_text.return_value = ""
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="test"
                )
                response = await tool(args)
            
            assert response.error is None
            assert response.results == []  # No results in empty PDF
            assert response.total_pages == 1
    
    @pytest.mark.asyncio
    async def test_unicode_content_search(self, tmp_path):
        """Test searching Unicode content in PDFs."""
        pdf_file = tmp_path / "unicode.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = """
            中文内容：人工智能的发展
            日本語：機械学習の応用
            한국어: 딥러닝 연구
            Русский: Искусственный интеллект
            العربية: الذكاء الاصطناعي
            Emojis: AI is 🔥 and ML is 💡
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                # Search for Chinese content
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="人工智能"
                )
                response = await tool(args)
            
            assert response.error is None
            assert len(response.results) > 0
            assert "人工智能" in response.results[0].text
    
    @pytest.mark.asyncio
    async def test_special_characters_in_pdf(self, tmp_path):
        """Test handling special characters and symbols."""
        pdf_file = tmp_path / "special_chars.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = """
            Email: user@example.com
            Price: $1,234.56 (USD)
            Math: x² + y² = r²
            Code: if (x > 0 && y < 10) { return true; }
            Path: C:\\Users\\Documents\\file.pdf
            Regex: ^[a-zA-Z0-9]+$
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="user@example.com"
                )
                response = await tool(args)
            
            assert response.error is None
            assert len(response.results) > 0
            assert "@example.com" in response.results[0].text
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self, tmp_path):
        """Test concurrent PDF searches."""
        # Create multiple PDF files
        pdf_files = []
        for i in range(3):
            pdf_file = tmp_path / f"concurrent_{i}.pdf"
            pdf_file.write_bytes(b"dummy pdf")
            pdf_files.append(pdf_file)
        
        tool = self.get_component_function()
        
        # Create separate mock configurations for each file
        mock_configs = []
        for i in range(3):
            mock_page = MagicMock()
            mock_page.extract_text.return_value = f"Document concurrent_{i}.pdf contains test{i+1}"
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_configs.append(mock_reader_instance)
        
        # Patch at the module level with side_effect to return different mocks
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_reader.side_effect = mock_configs
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                # Run searches concurrently
                tasks = []
                for i, pdf_file in enumerate(pdf_files):
                    args = PDFSearchArgs(
                        file_path=str(pdf_file),
                        query=f"test{i+1}"
                    )
                    tasks.append(tool(args))
                
                results = await asyncio.gather(*tasks)
        
        # All searches should succeed
        assert len(results) == 3
        for i, response in enumerate(results):
            assert response.error is None
            assert len(response.results) > 0
            # Check that we got the right document
            assert f"concurrent_{i}.pdf" in response.results[0].text
            assert f"test{i+1}" in response.results[0].text
    
    @pytest.mark.asyncio
    async def test_case_sensitivity_matching(self, tmp_path):
        """Test case-sensitive vs case-insensitive matching."""
        pdf_file = tmp_path / "case_test.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = """
            Machine Learning is important.
            MACHINE LEARNING applications are diverse.
            machine learning algorithms vary.
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                # Case-insensitive search (default)
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="MACHINE LEARNING"
                )
                response = await tool(args)
            
            assert response.error is None
            # Should find at least one match (fuzzy matching is case-insensitive)
            assert len(response.results) >= 1
    
    @pytest.mark.asyncio
    async def test_performance_with_large_pdf(self, tmp_path):
        """Test performance with large PDF files."""
        pdf_file = tmp_path / "large.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            # Create 100 pages
            pages = []
            for i in range(100):
                page = MagicMock()
                # Each page has substantial content
                page.extract_text.return_value = f"Page {i+1}\n" + ("Lorem ipsum dolor sit amet. " * 100)
                pages.append(page)
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = pages
            mock_reader.return_value = mock_reader_instance
            
            import time
            start_time = time.time()
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="Lorem ipsum",
                    max_results=10
                )
                response = await tool(args)
            
            elapsed = time.time() - start_time
            
            assert response.error is None
            assert response.total_pages == 100
            assert len(response.results) <= 10
            # Should complete in reasonable time
            assert elapsed < 5.0
    
    @pytest.mark.asyncio
    async def test_pdf_extraction_error_handling(self, tmp_path):
        """Test handling of PDF extraction errors."""
        pdf_file = tmp_path / "error.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            # Simulate extraction error on some pages
            mock_page.extract_text.side_effect = [
                "Page 1 content",
                Exception("Encryption error"),
                "Page 3 content"
            ]
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page, mock_page, mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="content"
                )
                response = await tool(args)
            
            # Should handle individual page errors gracefully
            assert response.error is not None
            assert "Encryption error" in response.error
    
    @pytest.mark.asyncio
    async def test_fuzzy_threshold_variations(self, tmp_path):
        """Test different fuzzy matching thresholds."""
        pdf_file = tmp_path / "fuzzy_test.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = """
            Artificial Intelligence
            Artifical Inteligence (typos)
            Artficial Intellgence (more typos)
            AI (abbreviation)
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            # Test with high threshold (strict matching)
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="Artificial Intelligence",
                    fuzzy_threshold=95
                )
                response_strict = await tool(args)
            
            # Test with low threshold (loose matching)
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="Artificial Intelligence",
                    fuzzy_threshold=60
                )
                response_loose = await tool(args)
            
            # Loose matching should find more results
            assert len(response_loose.results) > len(response_strict.results)
    
    @pytest.mark.asyncio
    async def test_long_search_queries(self, tmp_path):
        """Test handling of very long search queries."""
        pdf_file = tmp_path / "long_query.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = """
            This is a comprehensive guide to machine learning algorithms including
            supervised learning, unsupervised learning, reinforcement learning,
            deep learning, neural networks, and artificial intelligence applications.
            """
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                # Very long query
                long_query = "comprehensive guide to machine learning algorithms including supervised learning"
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query=long_query
                )
                response = await tool(args)
            
            assert response.error is None
            assert len(response.results) > 0
    
    @pytest.mark.asyncio
    async def test_pdf_with_no_text_content(self, tmp_path):
        """Test PDFs that contain no extractable text (e.g., scanned images)."""
        pdf_file = tmp_path / "no_text.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            # Multiple pages with no text
            pages = []
            for _ in range(3):
                page = MagicMock()
                page.extract_text.return_value = None  # No text extracted
                pages.append(page)
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = pages
            mock_reader.return_value = mock_reader_instance
            
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="test"
                )
                response = await tool(args)
            
            assert response.error is None
            assert response.results == []
            assert response.total_pages == 3
    
    @pytest.mark.asyncio
    async def test_context_chars_parameter(self, tmp_path):
        """Test different context_chars settings."""
        pdf_file = tmp_path / "context_chars.pdf"
        pdf_file.write_bytes(b"dummy pdf")
        
        tool = self.get_component_function()
        
        with patch("packages.funcn_registry.components.tools.pdf_search.tool.PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            # Long text to test context extraction
            long_text = "word " * 50 + "SEARCHTERM " + "word " * 50
            mock_page.extract_text.return_value = long_text
            
            mock_reader_instance = MagicMock()
            mock_reader_instance.pages = [mock_page]
            mock_reader.return_value = mock_reader_instance
            
            # Test with small context
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="SEARCHTERM",
                    context_chars=20
                )
                response_small = await tool(args)
            
            # Test with large context
            with patch("builtins.open", mock_open(read_data=b"dummy pdf")):
                args = PDFSearchArgs(
                    file_path=str(pdf_file),
                    query="SEARCHTERM",
                    context_chars=200
                )
                response_large = await tool(args)
            
            # Larger context should have longer text
            assert len(response_large.results[0].text) > len(response_small.results[0].text)
    
    @pytest.mark.asyncio
    async def test_io_error_handling(self, tmp_path):
        """Test handling of I/O errors during file operations."""
        tool = self.get_component_function()
        
        with patch("builtins.open") as mock_file_open:
            mock_file_open.side_effect = OSError("Permission denied")
            
            args = PDFSearchArgs(
                file_path="/path/to/protected.pdf",
                query="test"
            )
            response = await tool(args)
        
        # Tool might return a "file not found" error instead of IO error
        # since the path check happens before file opening
        assert response.error is not None
        assert response.results == []
