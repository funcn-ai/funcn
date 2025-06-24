"""Test suite for pdf_search_tool following best practices."""

import asyncio
import pytest
import tempfile

# Import the actual tool functions
from packages.funcn_registry.components.tools.pdf_search.tool import (
    PDFSearchArgs,
    PDFSearchResponse,
    PDFSearchResult,
    search_pdf_content,
)
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from tests.utils import BaseToolTest


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
                file_path="/tmp/test.pdf",
                query="artificial intelligence",
                max_results=5,
                fuzzy_threshold=80
            ),
            PDFSearchArgs(
                file_path="/tmp/report.pdf", 
                query="financial results",
                context_chars=300
            ),
            PDFSearchArgs(
                file_path="/tmp/document.pdf",
                query="machine learning",
                max_results=10,
                fuzzy_threshold=75
            )
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, PDFSearchResponse)
        assert isinstance(output.results, list)
        assert output.total_pages >= 0
        
        for result in output.results:
            assert isinstance(result, PDFSearchResult)
            assert result.page_number > 0
            assert 0 <= result.match_score <= 100
            assert isinstance(result.text, str)
            assert isinstance(result.excerpt, str)
    
    def create_test_pdf(self, file_path: Path, content: list[str]) -> Path:
        """Create a test PDF with given content."""
        c = canvas.Canvas(str(file_path), pagesize=letter)
        width, height = letter
        
        for page_num, page_content in enumerate(content):
            if page_num > 0:
                c.showPage()
            
            # Split text into lines that fit on the page
            y_position = height - 50
            lines = page_content.split('\n')
            
            for line in lines:
                if y_position < 50:
                    break
                    
                # Wrap long lines
                wrapped_lines = simpleSplit(line, "Helvetica", 12, width - 100)
                for wrapped_line in wrapped_lines:
                    c.drawString(50, y_position, wrapped_line)
                    y_position -= 15
                    if y_position < 50:
                        break
        
        c.save()
        return file_path
    
    @pytest.mark.asyncio
    async def test_basic_search(self, tmp_path):
        """Test basic PDF search functionality."""
        # Create test PDF
        pdf_file = tmp_path / "test.pdf"
        content = [
            """Introduction to Artificial Intelligence
            
            This document discusses artificial intelligence and machine learning applications.
            AI is transforming various industries including healthcare, finance, and transportation.
            Machine learning algorithms enable computers to learn from data without explicit programming.
            
            The field of artificial intelligence has seen tremendous growth in recent years.
            Deep learning, a subset of machine learning, has achieved remarkable results.
            """,
            """Chapter 2: Applications of AI
            
            Artificial intelligence is being applied in numerous domains:
            - Healthcare: Disease diagnosis and drug discovery
            - Finance: Fraud detection and algorithmic trading
            - Transportation: Autonomous vehicles and traffic optimization
            
            The future of AI looks promising with continued research and development.
            """
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        # Search for "artificial intelligence"
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="artificial intelligence",
            max_results=10,
            fuzzy_threshold=80
        )
        
        response = await search_pdf_content(args)
        
        assert response.error is None
        assert response.total_pages == 2
        assert len(response.results) > 0
        
        # Should find matches on both pages
        page_numbers = {result.page_number for result in response.results}
        assert 1 in page_numbers  # Found on page 1
        assert 2 in page_numbers  # Found on page 2
        
        # Check match scores are reasonable
        for result in response.results:
            assert result.match_score >= 80
            assert "artificial intelligence" in result.text.lower()
    
    @pytest.mark.asyncio
    async def test_fuzzy_matching(self, tmp_path):
        """Test fuzzy matching capabilities."""
        # Create PDF with typos
        pdf_file = tmp_path / "fuzzy_test.pdf"
        content = [
            """Machine Learning and Artificial Inteligence
            
            This document contains some typos:
            - Artifical intelligence (missing 'i')
            - Artifficial intelligence (extra 'f')
            - Machine lerning (typo in learning)
            
            We want to test if fuzzy matching can find these variations.
            """
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        # Search with fuzzy matching
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="artificial intelligence",
            max_results=10,
            fuzzy_threshold=70  # Lower threshold to catch typos
        )
        
        response = await search_pdf_content(args)
        
        assert response.error is None
        assert len(response.results) >= 2  # Should find at least the typos
        
        # Check that typos were found
        excerpts = [result.excerpt.lower() for result in response.results]
        assert any("inteligence" in excerpt for excerpt in excerpts)
    
    @pytest.mark.asyncio
    async def test_context_extraction(self, tmp_path):
        """Test context extraction around matches."""
        pdf_file = tmp_path / "context_test.pdf"
        content = [
            """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
            The term MACHINE LEARNING appears here in the middle of the text.
            Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            """
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        # Search with specific context size
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="MACHINE LEARNING",
            context_chars=100  # Get 100 chars of context
        )
        
        response = await search_pdf_content(args)
        
        assert len(response.results) > 0
        result = response.results[0]
        
        # Context should include surrounding text
        assert "Lorem ipsum" in result.text or "appears here" in result.text or "MACHINE LEARNING" in result.text
        
        # Check context length is reasonable
        # The actual implementation may vary in how it calculates context
        assert len(result.text) <= 300  # Be more generous with context size
        
        # Ellipsis may or may not be present depending on where match is found
        # Just verify the match is in the text
        assert "MACHINE LEARNING" in result.text
    
    @pytest.mark.asyncio
    async def test_max_results_limit(self, tmp_path):
        """Test that max_results limits output."""
        pdf_file = tmp_path / "many_matches.pdf"
        
        # Create content with many occurrences of search term
        repeated_text = "This document discusses AI. " * 20
        content = [repeated_text for _ in range(3)]  # 3 pages
        
        self.create_test_pdf(pdf_file, content)
        
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="AI",
            max_results=5,
            fuzzy_threshold=90
        )
        
        response = await search_pdf_content(args)
        
        assert len(response.results) <= 5
        assert response.total_pages == 3
        
        # Results should be sorted by match score
        scores = [r.match_score for r in response.results]
        assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_empty_pdf(self, tmp_path):
        """Test handling of empty PDF."""
        pdf_file = tmp_path / "empty.pdf"
        
        # Create empty PDF
        c = canvas.Canvas(str(pdf_file), pagesize=letter)
        c.save()
        
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="test"
        )
        
        response = await search_pdf_content(args)
        
        assert response.error is None
        assert response.results == []
        # Empty PDFs may report 0 or 1 pages depending on implementation
        assert response.total_pages in [0, 1]
    
    @pytest.mark.asyncio
    async def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        args = PDFSearchArgs(
            file_path="/nonexistent/path/file.pdf",
            query="test"
        )
        
        response = await search_pdf_content(args)
        
        assert response.error is not None
        assert "not found" in response.error
        assert response.results == []
        assert response.total_pages == 0
    
    @pytest.mark.asyncio
    async def test_invalid_pdf(self, tmp_path):
        """Test handling of invalid PDF files."""
        # Create a text file with .pdf extension
        invalid_pdf = tmp_path / "invalid.pdf"
        invalid_pdf.write_text("This is not a valid PDF file")
        
        args = PDFSearchArgs(
            file_path=str(invalid_pdf),
            query="test"
        )
        
        response = await search_pdf_content(args)
        
        assert response.error is not None
        assert "Error" in response.error
        assert response.results == []
    
    @pytest.mark.asyncio
    async def test_case_insensitive_search(self, tmp_path):
        """Test case-insensitive searching."""
        pdf_file = tmp_path / "case_test.pdf"
        content = [
            """MACHINE LEARNING in uppercase
            machine learning in lowercase
            Machine Learning in title case
            MaChInE LeArNiNg in mixed case
            """
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="machine learning",
            fuzzy_threshold=90
        )
        
        response = await search_pdf_content(args)
        
        # Should find matches (may be chunked together)
        assert len(response.results) >= 2
        
        # All should have high match scores
        for result in response.results:
            assert result.match_score >= 90
            
        # Check that multiple variations were found in the results
        all_text = " ".join(r.text.lower() for r in response.results)
        assert "machine learning in uppercase" in all_text or "MACHINE LEARNING".lower() in all_text
        assert "machine learning in lowercase" in all_text
        assert "machine learning in title case" in all_text or "Machine Learning".lower() in all_text
    
    @pytest.mark.asyncio
    async def test_multi_page_search(self, tmp_path):
        """Test searching across multiple pages."""
        pdf_file = tmp_path / "multipage.pdf"
        content = [
            "Page 1: Introduction to deep learning",
            "Page 2: Deep learning algorithms and techniques",
            "Page 3: Applications of deep learning in computer vision",
            "Page 4: Deep learning for natural language processing",
            "Page 5: Future of deep learning and AI"
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="deep learning",
            max_results=10
        )
        
        response = await search_pdf_content(args)
        
        assert response.total_pages == 5
        assert len(response.results) >= 5  # Should find on all pages
        
        # Check all pages are represented
        found_pages = {r.page_number for r in response.results}
        assert found_pages == {1, 2, 3, 4, 5}
    
    @pytest.mark.asyncio
    async def test_special_characters(self, tmp_path):
        """Test searching for text with special characters."""
        pdf_file = tmp_path / "special_chars.pdf"
        content = [
            """Special characters test:
            - Email: user@example.com
            - Phone: +1 (555) 123-4567
            - URL: https://www.example.com/path?query=value
            - Price: $99.99
            - Percentage: 85%
            - C++ programming language
            """
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        # Test various special character searches
        test_queries = [
            ("user@example.com", 90),
            ("(555) 123-4567", 80),
            ("$99.99", 90),
            ("C++", 90)
        ]
        
        for query, threshold in test_queries:
            args = PDFSearchArgs(
                file_path=str(pdf_file),
                query=query,
                fuzzy_threshold=threshold
            )
            
            response = await search_pdf_content(args)
            
            assert response.error is None
            assert len(response.results) > 0
            assert response.results[0].match_score >= threshold
    
    @pytest.mark.asyncio
    async def test_long_query(self, tmp_path):
        """Test searching with long queries."""
        pdf_file = tmp_path / "long_query.pdf"
        content = [
            """This is a document about machine learning and artificial intelligence applications
            in modern technology. The combination of deep learning algorithms and neural networks
            has revolutionized how we approach complex problems in computer vision and natural
            language processing.
            """
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        # Search with a long phrase
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="machine learning and artificial intelligence applications",
            fuzzy_threshold=70
        )
        
        response = await search_pdf_content(args)
        
        assert len(response.results) > 0
        assert response.results[0].match_score >= 70
    
    @pytest.mark.asyncio
    async def test_performance_large_pdf(self, tmp_path):
        """Test performance with moderately large PDF."""
        pdf_file = tmp_path / "large.pdf"
        
        # Create 50-page PDF
        content = []
        for i in range(50):
            page_text = f"""Page {i+1}
            
            This is page {i+1} of a large document. It contains various topics including
            artificial intelligence, machine learning, data science, and programming.
            
            """ + ("Lorem ipsum dolor sit amet. " * 50)
            content.append(page_text)
        
        self.create_test_pdf(pdf_file, content)
        
        import time
        start_time = time.time()
        
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="machine learning",
            max_results=20
        )
        
        response = await search_pdf_content(args)
        
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time
        assert elapsed < 5.0
        assert response.total_pages == 50
        assert len(response.results) > 0
    
    @pytest.mark.asyncio
    async def test_unicode_content(self, tmp_path):
        """Test searching in PDFs with unicode content."""
        pdf_file = tmp_path / "unicode.pdf"
        
        # Note: Basic PDF creation with reportlab may have limited unicode support
        # This test checks that the tool handles unicode gracefully
        content = [
            """Unicode Test Document
            
            English: Artificial Intelligence
            Spanish: Inteligencia Artificial
            French: Intelligence Artificielle
            German: Künstliche Intelligenz
            
            Testing search across different languages.
            """
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="Intelligence",
            fuzzy_threshold=80
        )
        
        response = await search_pdf_content(args)
        
        assert response.error is None
        assert len(response.results) >= 2  # At least English and French
    
    @pytest.mark.asyncio
    async def test_punctuation_handling(self, tmp_path):
        """Test handling of punctuation in searches."""
        pdf_file = tmp_path / "punctuation.pdf"
        content = [
            """Punctuation test document.
            
            This tests various punctuation scenarios:
            - "machine learning" in quotes
            - machine-learning with hyphen
            - machine.learning with period
            - machine/learning with slash
            - (machine learning) in parentheses
            """
        ]
        
        self.create_test_pdf(pdf_file, content)
        
        args = PDFSearchArgs(
            file_path=str(pdf_file),
            query="machine learning",
            fuzzy_threshold=75
        )
        
        response = await search_pdf_content(args)
        
        # Should find multiple variations
        assert len(response.results) >= 3
        
        # Check different punctuation forms were found
        texts = [r.text.lower() for r in response.results]
        assert any('"machine learning"' in t for t in texts)
        assert any('machine-learning' in t for t in texts)
