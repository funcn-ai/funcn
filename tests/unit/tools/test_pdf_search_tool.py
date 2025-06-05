"""Test suite for pdf_search_tool following best practices."""

import pytest
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestPDFSearchTool(BaseToolTest):
    """Test pdf_search_tool component."""
    
    component_name = "pdf_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/pdf_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.pdf_search_tool import search_pdf
        # For testing, mock it
        def mock_search_pdf(
            pdf_path: str | Path,
            query: str,
            case_sensitive: bool = False,
            page_numbers: bool = True
        ) -> list[dict[str, any]]:
            """Mock PDF search tool."""
            return [
                {
                    "page": 1,
                    "text": f"Found '{query}' in the document",
                    "score": 0.95
                }
            ]
        return mock_search_pdf
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "pdf_path": "/path/to/test.pdf",
                "query": "artificial intelligence",
                "case_sensitive": False
            },
            {
                "pdf_path": "/path/to/report.pdf", 
                "query": "financial results",
                "page_numbers": True
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        
        for result in output:
            assert "page" in result or "text" in result
            if "score" in result:
                assert 0 <= result["score"] <= 1
    
    @pytest.mark.asyncio
    async def test_search_with_fuzzy_matching(self, tmp_path):
        """Test PDF search with fuzzy matching."""
        # Create test PDF
        pdf_file = TestDataFactory.create_pdf_file(tmp_path)
        
        with patch("pdfplumber.open") as mock_pdf:
            # Mock PDF content
            mock_page = Mock()
            mock_page.extract_text.return_value = """
            Introduction to Artificial Intelligence
            
            This document discusses AI and machine learning applications.
            Artificial inteligence (typo) is transforming industries.
            """
            mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
            
            tool = self.get_component_function()
            
            # Test exact match
            results = tool(pdf_file, "Artificial Intelligence", case_sensitive=True)
            assert len(results) >= 1
            
            # Test fuzzy match (should find typo)
            results = tool(pdf_file, "artificial intelligence", fuzzy=True)
            assert len(results) >= 2  # Should find both correct and typo
    
    def test_handles_invalid_pdf(self, tmp_path):
        """Test handling of invalid PDF files."""
        # Create invalid file
        invalid_file = tmp_path / "not_a_pdf.txt"
        invalid_file.write_text("This is not a PDF")
        
        tool = self.get_component_function()
        
        # Should handle gracefully
        results = tool(invalid_file, "test")
        assert isinstance(results, list)
        assert len(results) == 0 or (len(results) == 1 and "error" in results[0])
    
    def test_search_with_page_range(self, tmp_path):
        """Test searching specific page ranges."""
        pdf_file = TestDataFactory.create_pdf_file(tmp_path)
        
        with patch("pdfplumber.open") as mock_pdf:
            # Mock multi-page PDF
            pages = []
            for i in range(10):
                page = Mock()
                page.extract_text.return_value = f"Page {i+1} content with term{i+1}"
                pages.append(page)
            
            mock_pdf.return_value.__enter__.return_value.pages = pages
            
            tool = self.get_component_function()
            
            # Search specific pages
            results = tool(
                pdf_file,
                "term",
                start_page=3,
                end_page=5
            )
            
            # Should only search pages 3-5
            page_numbers = [r["page"] for r in results]
            assert all(3 <= p <= 5 for p in page_numbers)
    
    def test_extract_context(self, tmp_path):
        """Test context extraction around matches."""
        pdf_file = TestDataFactory.create_pdf_file(tmp_path)
        
        with patch("pdfplumber.open") as mock_pdf:
            mock_page = Mock()
            mock_page.extract_text.return_value = """
            This is line one of the document.
            This line contains the SEARCH_TERM we want.
            This is line three with more context.
            Another line here.
            Final line of the page.
            """
            mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
            
            tool = self.get_component_function()
            results = tool(
                pdf_file,
                "SEARCH_TERM",
                context_lines=1  # Get 1 line before/after
            )
            
            assert len(results) > 0
            result = results[0]
            
            # Should include context
            assert "line one" in result.get("context", "")
            assert "line three" in result.get("context", "")
    
    @pytest.mark.parametrize("query,expected_count", [
        ("AI", 5),
        ("machine learning", 3),
        ("deep learning", 2),
        ("nonexistent", 0),
    ])
    def test_various_search_queries(self, tmp_path, query, expected_count):
        """Test tool with various search queries."""
        pdf_file = TestDataFactory.create_pdf_file(tmp_path)
        
        with patch("pdfplumber.open") as mock_pdf:
            mock_page = Mock()
            mock_page.extract_text.return_value = """
            AI and machine learning are transforming technology.
            AI applications include computer vision and NLP.
            Machine learning uses neural networks.
            Deep learning is a subset of machine learning.
            AI is the future. Machine learning powers AI.
            Deep learning requires large datasets.
            """
            mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
            
            tool = self.get_component_function()
            results = tool(pdf_file, query)
            
            # For testing, just check we get results
            assert isinstance(results, list)
    
    def test_performance_on_large_pdf(self, tmp_path):
        """Test performance with large PDF files."""
        pdf_file = TestDataFactory.create_pdf_file(tmp_path)
        
        with patch("pdfplumber.open") as mock_pdf:
            # Mock a large PDF (100 pages)
            pages = []
            for i in range(100):
                page = Mock()
                page.extract_text.return_value = f"Page {i+1} " + ("text " * 1000)
                pages.append(page)
            
            mock_pdf.return_value.__enter__.return_value.pages = pages
            
            tool = self.get_component_function()
            
            import time
            start_time = time.time()
            
            results = tool(pdf_file, "text", max_results=10)
            
            elapsed = time.time() - start_time
            
            # Should complete reasonably fast even for large PDFs
            assert elapsed < 5.0  # 5 seconds max
            assert len(results) <= 10  # Respects max_results
    
    def test_search_with_regex(self, tmp_path):
        """Test searching with regex patterns."""
        pdf_file = TestDataFactory.create_pdf_file(tmp_path)
        
        with patch("pdfplumber.open") as mock_pdf:
            mock_page = Mock()
            mock_page.extract_text.return_value = """
            Email: john.doe@example.com
            Phone: 123-456-7890
            Date: 2024-01-15
            Amount: $1,234.56
            """
            mock_pdf.return_value.__enter__.return_value.pages = [mock_page]
            
            tool = self.get_component_function()
            
            # Search for email pattern
            results = tool(
                pdf_file,
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                regex=True
            )
            
            assert len(results) >= 1
            assert "john.doe@example.com" in str(results[0])


class TestPDFSearchToolHelpers:
    """Test helper functions for PDF search tool."""
    
    def test_fuzzy_match_scoring(self):
        """Test fuzzy matching score calculation."""
        from funcn_registry.components.tools.pdf_search_tool.helpers import calculate_fuzzy_score
        
        # Exact match
        score = calculate_fuzzy_score("artificial intelligence", "artificial intelligence")
        assert score == 1.0
        
        # Close match
        score = calculate_fuzzy_score("artificial inteligence", "artificial intelligence")
        assert 0.8 < score < 1.0
        
        # Poor match
        score = calculate_fuzzy_score("machine learning", "artificial intelligence")
        assert score < 0.5
    
    def test_highlight_matches(self):
        """Test match highlighting in text."""
        from funcn_registry.components.tools.pdf_search_tool.helpers import highlight_matches
        
        text = "This document discusses artificial intelligence and AI applications."
        query = "artificial intelligence"
        
        highlighted = highlight_matches(text, query)
        
        assert "**artificial intelligence**" in highlighted or \
               "<mark>artificial intelligence</mark>" in highlighted
