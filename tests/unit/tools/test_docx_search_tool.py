"""Test suite for docx_search_tool following best practices."""

import asyncio
import pytest
from datetime import datetime
from packages.funcn_registry.components.tools.docx_search.tool import (
    DocumentSection,
    DOCXSearchResult,
    extract_docx_headings,
    extract_metadata,
    extract_table_text,
    get_heading_level,
    process_docx_document,
    search_docx,
    search_docx_with_regex,
    search_in_text,
    should_include_section,
    validate_file_path,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class TestDOCXSearchTool(BaseToolTest):
    """Test cases for DOCX search tool."""
    
    component_name = "docx_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/docx_search")
    
    def get_component_function(self):
        """Get the main tool function."""
        return search_docx
    
    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "file_path": "/path/to/document.docx",
                "search_text": "introduction",
                "case_sensitive": False,
                "include_tables": True
            },
            {
                "file_path": "/path/to/report.docx",
                "search_text": "financial results",
                "case_sensitive": True,
                "include_tables": True
            },
            {
                "file_path": "/path/to/thesis.docx",
                "search_text": "conclusion",
                "case_sensitive": False,
                "include_tables": False
            },
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        assert isinstance(output, DOCXSearchResult), "Output should be a DOCXSearchResult"
        assert hasattr(output, 'success')
        assert hasattr(output, 'file_path')
        assert hasattr(output, 'total_matches')
        assert isinstance(output.matching_sections, list)
        assert output.file_path == str(Path(input_data['file_path']).absolute())
    
    @pytest.mark.asyncio
    async def test_search_simple_text(self):
        """Test basic text search in paragraphs."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Mock paragraphs
            mock_p1 = Mock()
            mock_p1.text = "This is an introduction to the topic."
            mock_p1.style = Mock()
            mock_p1.style.name = "Normal"
            
            mock_p2 = Mock()
            mock_p2.text = "The main content goes here."
            mock_p2.style = Mock()
            mock_p2.style.name = "Normal"
            
            mock_p3 = Mock()
            mock_p3.text = "Finally, the introduction is complete."
            mock_p3.style = Mock()
            mock_p3.style.name = "Normal"
            
            mock_doc.paragraphs = [mock_p1, mock_p2, mock_p3]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title="Test Document",
                author="Test Author",
                subject=None,
                keywords=None,
                created=datetime(2024, 1, 1),
                modified=datetime(2024, 1, 15),
                last_modified_by="Test User",
                revision=1,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                with patch("asyncio.get_event_loop") as mock_loop:
                    mock_loop.return_value.time.return_value = 0.0
                    result = await search_docx("/test/doc.docx", "introduction")
            
            assert result.success is True
            assert result.total_matches == 2
            assert len(result.matching_sections) == 2
            assert result.matching_sections[0].paragraph_index == 0
            assert result.matching_sections[1].paragraph_index == 2
            assert "introduction" in result.matching_sections[0].text.lower()
            assert "introduction" in result.matching_sections[1].text.lower()
    
    @pytest.mark.asyncio
    async def test_case_sensitive_search(self):
        """Test case sensitive vs insensitive search."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            mock_p1 = Mock()
            mock_p1.text = "UPPERCASE text here"
            mock_p1.style = Mock()
            mock_p1.style.name = "Normal"
            
            mock_p2 = Mock()
            mock_p2.text = "lowercase text here"
            mock_p2.style = Mock()
            mock_p2.style.name = "Normal"
            
            mock_p3 = Mock()
            mock_p3.text = "MixedCase Text Here"
            mock_p3.style = Mock()
            mock_p3.style.name = "Normal"
            
            mock_doc.paragraphs = [mock_p1, mock_p2, mock_p3]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                # Case insensitive - should find all
                result_insensitive = await search_docx("/test/doc.docx", "text", case_sensitive=False)
                # Case sensitive - should find only lowercase
                result_sensitive = await search_docx("/test/doc.docx", "text", case_sensitive=True)
            
            assert result_insensitive.total_matches == 3
            # With case sensitive, it should find "text" in "UPPERCASE text" and "lowercase text"
            # but not "Text" in "MixedCase Text"
            assert result_sensitive.total_matches == 2
            texts = [s.text for s in result_sensitive.matching_sections]
            assert "lowercase text here" in texts
            assert "UPPERCASE text here" in texts  # Contains "text" in lowercase
    
    @pytest.mark.asyncio
    async def test_table_search(self):
        """Test searching within tables."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Mock table structure
            mock_cell1 = Mock()
            mock_cell1.paragraphs = [Mock(text="Product Name")]
            mock_cell2 = Mock()
            mock_cell2.paragraphs = [Mock(text="Price")]
            mock_cell3 = Mock()
            mock_cell3.paragraphs = [Mock(text="Laptop Computer")]
            mock_cell4 = Mock()
            mock_cell4.paragraphs = [Mock(text="$999")]
            
            mock_row1 = Mock()
            mock_row1.cells = [mock_cell1, mock_cell2]
            mock_row2 = Mock()
            mock_row2.cells = [mock_cell3, mock_cell4]
            
            mock_table = Mock()
            mock_table.rows = [mock_row1, mock_row2]
            
            mock_doc.paragraphs = []
            mock_doc.tables = [mock_table]
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await search_docx("/test/doc.docx", "Laptop", include_tables=True)
            
            assert result.success is True
            assert result.total_matches == 1
            assert result.matching_sections[0].section_type == "table"
            assert result.matching_sections[0].table_info is not None
            assert result.matching_sections[0].table_info["row"] == 1
            assert result.matching_sections[0].table_info["col"] == 0
    
    @pytest.mark.asyncio
    async def test_extract_headings(self):
        """Test extracting all headings from document."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Mock paragraphs with headings
            mock_h1 = Mock()
            mock_h1.text = "Chapter 1: Introduction"
            mock_h1.style = Mock()

            mock_h1.style.name = "Heading 1"
            
            mock_p1 = Mock()
            mock_p1.text = "Regular paragraph text"
            mock_p1.style = Mock()
            mock_p1.style.name = "Normal"
            
            mock_h2 = Mock()
            mock_h2.text = "Section 1.1: Background"
            mock_h2.style = Mock()

            mock_h2.style.name = "Heading 2"
            
            mock_h3 = Mock()
            mock_h3.text = "1.1.1 Historical Context"
            mock_h3.style = Mock()

            mock_h3.style.name = "Heading 3"
            
            mock_doc.paragraphs = [mock_h1, mock_p1, mock_h2, mock_h3]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await extract_docx_headings("/test/doc.docx")
            
            assert result.success is True
            assert len(result.matching_sections) == 3
            assert all(s.section_type == "heading" for s in result.matching_sections)
            assert result.matching_sections[0].heading_level == 1
            assert result.matching_sections[1].heading_level == 2
            assert result.matching_sections[2].heading_level == 3
    
    @pytest.mark.asyncio
    async def test_extract_specific_heading_level(self):
        """Test extracting specific heading level."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Mix of heading levels
            headings = []
            for i in range(1, 4):
                for j in range(2):
                    mock_h = Mock()
                    mock_h.text = f"Heading Level {i} - {j}"
                    mock_h.style = Mock()
                    mock_h.style.name = f"Heading {i}"
                    headings.append(mock_h)
            
            mock_doc.paragraphs = headings
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await extract_docx_headings("/test/doc.docx", heading_level=2)
            
            assert result.success is True
            assert len(result.matching_sections) == 2
            assert all(s.heading_level == 2 for s in result.matching_sections)
    
    @pytest.mark.asyncio
    async def test_regex_search(self):
        """Test searching with regular expressions."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            mock_p1 = Mock()
            mock_p1.text = "Email: john.doe@example.com"
            mock_p1.style = Mock()
            mock_p1.style.name = "Normal"
            
            mock_p2 = Mock()
            mock_p2.text = "Contact: jane.smith@company.org"
            mock_p2.style = Mock()
            mock_p2.style.name = "Normal"
            
            mock_p3 = Mock()
            mock_p3.text = "No email in this paragraph"
            mock_p3.style = Mock()
            mock_p3.style.name = "Normal"
            
            mock_doc.paragraphs = [mock_p1, mock_p2, mock_p3]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                # Email regex pattern
                pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                result = await search_docx_with_regex("/test/doc.docx", pattern)
            
            assert result.success is True
            assert result.total_matches == 2
            assert len(result.matching_sections) == 2
            assert "@example.com" in result.matching_sections[0].text
            assert "@company.org" in result.matching_sections[1].text
    
    @pytest.mark.asyncio
    async def test_metadata_extraction(self):
        """Test document metadata extraction."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Mock comprehensive metadata
            mock_doc.core_properties = Mock(
                title="Test Document Title",
                author="John Doe",
                subject="Test Subject",
                keywords="test, document, search",
                created=datetime(2024, 1, 1, 10, 30),
                modified=datetime(2024, 1, 15, 14, 45),
                last_modified_by="Jane Smith",
                revision=5,
                category="Technical",
                comments="This is a test document"
            )
            
            mock_p = Mock()
            mock_p.text = "Content"
            mock_p.style = Mock()
            mock_p.style.name = "Normal"
            mock_doc.paragraphs = [mock_p]
            mock_doc.tables = []
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await process_docx_document("/test/doc.docx", search_text="test", extract_metadata_flag=True)
            
            assert result.success is True
            assert result.document_metadata["title"] == "Test Document Title"
            assert result.document_metadata["author"] == "John Doe"
            assert result.document_metadata["keywords"] == "test, document, search"
            assert result.document_metadata["revision"] == 5
            assert "created" in result.document_metadata
            assert "modified" in result.document_metadata
    
    @pytest.mark.asyncio
    async def test_style_filter(self):
        """Test filtering by paragraph style."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Mix of styles
            mock_p1 = Mock()
            mock_p1.text = "Normal text with keyword"
            mock_p1.style = Mock()
            mock_p1.style.name = "Normal"
            
            mock_p2 = Mock()
            mock_p2.text = "Quote text with keyword"
            mock_p2.style = Mock()

            mock_p2.style.name = "Quote"
            
            mock_p3 = Mock()
            mock_p3.text = "Code text with keyword"
            mock_p3.style = Mock()

            mock_p3.style.name = "Code"
            
            mock_doc.paragraphs = [mock_p1, mock_p2, mock_p3]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await process_docx_document(
                    "/test/doc.docx",
                    search_text="keyword",
                    style_filter="Quote"
                )
            
            assert result.success is True
            assert result.total_matches == 1
            assert result.matching_sections[0].style == "Quote"
    
    @pytest.mark.asyncio
    async def test_multiple_matches_in_paragraph(self):
        """Test finding multiple matches within a single paragraph."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            mock_p1 = Mock()
            mock_p1.text = "Python is great. Python is powerful. Python is versatile."
            mock_p1.style = Mock()
            mock_p1.style.name = "Normal"
            
            mock_doc.paragraphs = [mock_p1]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await search_docx("/test/doc.docx", "Python")
            
            assert result.success is True
            assert result.total_matches == 3
            assert len(result.matching_sections) == 1
            assert len(result.matching_sections[0].match_positions) == 3
    
    @pytest.mark.asyncio
    async def test_empty_document(self):
        """Test handling empty documents."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            mock_doc.paragraphs = []
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await search_docx("/test/empty.docx", "test")
            
            assert result.success is True
            assert result.total_matches == 0
            assert len(result.matching_sections) == 0
            assert result.total_paragraphs == 0
            assert result.total_tables == 0
    
    @pytest.mark.asyncio
    async def test_file_validation(self):
        """Test file path validation."""
        # Test non-existent file
        with pytest.raises(ValueError, match="File does not exist"):
            validate_file_path("/non/existent/file.docx")
        
        # Test wrong file extension
        with patch("pathlib.Path.exists", return_value=True):
            with pytest.raises(ValueError, match="must be a Word document"):
                validate_file_path("/test/file.txt")
        
        # Test valid DOCX file
        with patch("pathlib.Path.exists", return_value=True):
            result = validate_file_path("/test/file.docx")
            assert result == str(Path("/test/file.docx").absolute())
        
        # Test valid DOCM file
        with patch("pathlib.Path.exists", return_value=True):
            result = validate_file_path("/test/file.docm")
            assert result == str(Path("/test/file.docm").absolute())
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling during document processing."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            # Simulate document loading error
            mock_doc_class.side_effect = Exception("Failed to load document")
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await search_docx("/test/corrupted.docx", "test")
            
            assert result.success is False
            assert result.error == "Failed to load document"
            assert result.total_matches == 0
            assert len(result.matching_sections) == 0
    
    def test_search_in_text_function(self):
        """Test the search_in_text utility function."""
        # Test simple text search
        text = "Hello world, this is a test."
        matches = search_in_text(text, "world", None, False)
        assert len(matches) == 1
        assert matches[0] == (6, 11)
        
        # Test case sensitive
        matches = search_in_text(text, "WORLD", None, True)
        assert len(matches) == 0
        
        # Test regex search
        matches = search_in_text(text, None, r'\b\w{4}\b', False)
        assert len(matches) >= 2  # "this" and "test"
        
        # Test empty text
        matches = search_in_text("", "test", None, False)
        assert len(matches) == 0
    
    def test_get_heading_level_function(self):
        """Test the get_heading_level utility function."""
        # Test valid heading
        mock_p = Mock()
        mock_p.style = Mock()

        mock_p.style.name = "Heading 1"
        assert get_heading_level(mock_p) == 1
        
        mock_p.style.name = "Heading 3"
        assert get_heading_level(mock_p) == 3
        
        # Test non-heading
        mock_p.style.name = "Normal"
        assert get_heading_level(mock_p) is None
        
        # Test invalid heading format
        mock_p.style.name = "Heading"
        assert get_heading_level(mock_p) is None
    
    def test_extract_table_text_function(self):
        """Test the extract_table_text utility function."""
        # Mock table structure
        mock_cell1 = Mock()
        mock_cell1.paragraphs = [Mock(text="Cell 1"), Mock(text="Line 2")]
        
        mock_cell2 = Mock()
        mock_cell2.paragraphs = [Mock(text="Cell 2")]
        
        mock_row = Mock()
        mock_row.cells = [mock_cell1, mock_cell2]
        
        mock_table = Mock()
        mock_table.rows = [mock_row]
        
        result = extract_table_text(mock_table)
        
        assert len(result) == 1
        assert len(result[0]) == 2
        assert result[0][0]["text"] == "Cell 1 Line 2"
        assert result[0][0]["row"] == 0
        assert result[0][0]["col"] == 0
        assert result[0][1]["text"] == "Cell 2"
        assert result[0][1]["row"] == 0
        assert result[0][1]["col"] == 1
    
    def test_should_include_section_function(self):
        """Test the should_include_section utility function."""
        mock_p = Mock()
        mock_p.style = Mock()

        mock_p.style.name = "Normal"
        
        # Test no filters - should include
        assert should_include_section(mock_p, None, False, None) is True
        
        # Test style filter match
        assert should_include_section(mock_p, "Normal", False, None) is True
        
        # Test style filter no match
        assert should_include_section(mock_p, "Quote", False, None) is False
        
        # Test heading extraction
        mock_p.style.name = "Heading 2"
        assert should_include_section(mock_p, None, True, None) is True
        assert should_include_section(mock_p, None, True, 2) is True
        assert should_include_section(mock_p, None, True, 1) is False
    
    @pytest.mark.asyncio
    async def test_word_count(self):
        """Test word counting functionality."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            mock_p1 = Mock()
            mock_p1.text = "This is a test."  # 4 words
            mock_p1.style = Mock()
            mock_p1.style.name = "Normal"
            
            mock_p2 = Mock()
            mock_p2.text = "Another paragraph with more words here."  # 6 words
            mock_p2.style = Mock()
            mock_p2.style.name = "Normal"
            
            mock_doc.paragraphs = [mock_p1, mock_p2]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await search_docx("/test/doc.docx", "test")
            
            assert result.success is True
            assert result.total_words == 10
    
    @pytest.mark.asyncio
    async def test_complex_table_search(self):
        """Test searching in complex table structures."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Create a 3x3 table
            cells = []
            for i in range(3):
                row_cells = []
                for j in range(3):
                    cell = Mock()
                    cell.paragraphs = [Mock(text=f"Row {i} Col {j} Data")]
                    row_cells.append(cell)
                cells.append(row_cells)
            
            rows = []
            for row_cells in cells:
                row = Mock()
                row.cells = row_cells
                rows.append(row)
            
            mock_table = Mock()
            mock_table.rows = rows
            
            mock_doc.paragraphs = []
            mock_doc.tables = [mock_table]
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await search_docx("/test/doc.docx", "Row 1", include_tables=True)
            
            assert result.success is True
            assert result.total_matches == 3  # Found in all 3 columns of row 1
            assert all(s.table_info["row"] == 1 for s in result.matching_sections)
    
    @pytest.mark.asyncio
    async def test_special_characters_search(self):
        """Test searching for special characters and Unicode."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            mock_p1 = Mock()
            mock_p1.text = "Price: $99.99 (€89.99)"
            mock_p1.style = Mock()
            mock_p1.style.name = "Normal"
            
            mock_p2 = Mock()
            mock_p2.text = "Special chars: © ® ™ • « »"
            mock_p2.style = Mock()
            mock_p2.style.name = "Normal"
            
            mock_p3 = Mock()
            mock_p3.text = "Unicode: 你好 مرحبا こんにちは"
            mock_p3.style = Mock()
            mock_p3.style.name = "Normal"
            
            mock_doc.paragraphs = [mock_p1, mock_p2, mock_p3]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                # Search for Euro symbol
                result = await search_docx("/test/doc.docx", "€")
                assert result.total_matches == 1
                
                # Search for copyright symbol
                result = await search_docx("/test/doc.docx", "©")
                assert result.total_matches == 1
                
                # Search for Chinese text
                result = await search_docx("/test/doc.docx", "你好")
                assert result.total_matches == 1
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test that performance metrics are recorded."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            mock_p = Mock()
            mock_p.text = "Test"
            mock_p.style = Mock()
            mock_p.style.name = "Normal"
            mock_doc.paragraphs = [mock_p]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await search_docx("/test/doc.docx", "test")
            
            assert result.success is True
            assert result.search_time > 0
            assert isinstance(result.search_time, float)
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self):
        """Test concurrent search operations."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            mock_p = Mock()
            mock_p.text = "Test content"
            mock_p.style = Mock()
            mock_p.style.name = "Normal"
            mock_doc.paragraphs = [mock_p]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                # Run multiple searches concurrently
                tasks = [
                    search_docx("/test/doc1.docx", "test"),
                    search_docx("/test/doc2.docx", "content"),
                    search_docx("/test/doc3.docx", "Test"),
                ]
                
                results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all(r.success for r in results)
    
    @pytest.mark.asyncio
    async def test_max_context_chars(self):
        """Test context extraction with max_context_chars parameter."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Long paragraph
            long_text = "a" * 100 + " keyword " + "b" * 100
            mock_p = Mock()
            mock_p.text = long_text
            mock_p.style = Mock()

            mock_p.style.name = "Normal"
            
            mock_doc.paragraphs = [mock_p]
            mock_doc.tables = []
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await process_docx_document(
                    "/test/doc.docx",
                    search_text="keyword",
                    max_context_chars=50
                )
            
            assert result.success is True
            assert result.total_matches == 1
            # The full text is still returned, max_context_chars might be used for display
            assert len(result.matching_sections[0].text) > 50
    
    @pytest.mark.asyncio
    async def test_document_statistics(self):
        """Test document statistics collection."""
        with patch("packages.funcn_registry.components.tools.docx_search.tool.docx.Document") as mock_doc_class:
            mock_doc = Mock()
            mock_doc_class.return_value = mock_doc
            
            # Create document with various content
            paragraphs = []
            for i in range(10):
                p = Mock()
                p.text = f"Paragraph {i} with some content."
                p.style = Mock()

                p.style.name = "Normal"
                paragraphs.append(p)
            
            # Add some headings
            for i in range(3):
                h = Mock()
                h.text = f"Heading {i}"
                h.style = Mock()
                h.style.name = f"Heading {i+1}"
                paragraphs.append(h)
            
            mock_doc.paragraphs = paragraphs
            
            # Add tables
            tables = []
            for i in range(2):
                table = Mock()
                table.rows = [Mock(cells=[Mock(paragraphs=[Mock(text="Cell")])])]
                tables.append(table)
            
            mock_doc.tables = tables
            mock_doc.core_properties = Mock(
                title=None,
                author=None,
                subject=None,
                keywords=None,
                created=None,
                modified=None,
                last_modified_by=None,
                revision=None,
                category=None,
                comments=None
            )
            
            with patch("pathlib.Path.exists", return_value=True):
                result = await process_docx_document("/test/doc.docx", search_text="content")
            
            assert result.success is True
            assert result.total_paragraphs == 13
            assert result.total_tables == 2
            assert result.total_words > 0
    
    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        functions = [
            process_docx_document,
            search_docx,
            extract_docx_headings,
            search_docx_with_regex,
            validate_file_path,
            extract_metadata,
            search_in_text,
            get_heading_level,
            extract_table_text,
            should_include_section,
        ]
        
        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 10
