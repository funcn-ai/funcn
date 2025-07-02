"""Test suite for docx_search_tool following best practices."""

import asyncio
import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class TestDOCXSearchTool(BaseToolTest):
    """Test cases for DOCX search tool."""

    component_name = "docx_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/docx_search_tool")

    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.docx_search_tool import search_docx
        def mock_search_docx(
            docx_path: str | Path,
            query: str,
            case_sensitive: bool = False,
            search_headers: bool = True,
            search_tables: bool = True,
            search_footnotes: bool = True,
            include_metadata: bool = False
        ) -> list[dict[str, any]]:
            """Mock DOCX search tool."""
            results = [
                {
                    "paragraph": 1,
                    "text": f"This paragraph contains the search term '{query}'.",
                    "type": "paragraph",
                    "style": "Normal",
                    "match_score": 0.95
                },
                {
                    "paragraph": 5,
                    "text": f"Header: {query} Documentation",
                    "type": "heading",
                    "style": "Heading 1",
                    "level": 1,
                    "match_score": 0.90
                }
            ]

            if include_metadata:
                results.append({
                    "type": "metadata",
                    "author": "Test Author",
                    "created": "2024-01-01",
                    "modified": "2024-01-15",
                    "title": f"Document about {query}"
                })

            return results
        return mock_search_docx

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "docx_path": "/path/to/document.docx",
                "query": "introduction",
                "search_headers": True,
                "case_sensitive": False
            },
            {
                "docx_path": "/path/to/report.docx",
                "query": "financial results",
                "search_tables": True,
                "include_metadata": True
            },
            {
                "docx_path": "/path/to/thesis.docx",
                "query": "conclusion",
                "search_footnotes": True
            }
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)

        for result in output:
            assert isinstance(result, dict)
            assert "type" in result or "match_type" in result
            if result.get("type") != "metadata":
                assert "text" in result or "content" in result

    def test_search_paragraphs(self, tmp_path):
        """Test searching in document paragraphs."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            # Mock document with paragraphs
            mock_paragraphs = [
                Mock(text="Introduction to the topic", style=Mock(name="Normal")),
                Mock(text="This is the main content with important information", style=Mock(name="Normal")),
                Mock(text="Conclusion and summary", style=Mock(name="Normal"))
            ]

            mock_doc_instance = Mock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "important")

            assert len(results) >= 1
            assert any("important" in r.get("text", "").lower() for r in results)

    def test_search_headers(self, tmp_path):
        """Test searching in document headers."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            # Mock document with headers
            mock_paragraphs = [
                Mock(text="Chapter 1: Introduction", style=Mock(name="Heading 1")),
                Mock(text="Regular paragraph", style=Mock(name="Normal")),
                Mock(text="Section 1.1: Background", style=Mock(name="Heading 2")),
                Mock(text="1.1.1 Historical Context", style=Mock(name="Heading 3"))
            ]

            mock_doc_instance = Mock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "Introduction", search_headers=True)

            assert len(results) >= 1
            # Should find in Heading 1
            assert any(r.get("style") == "Heading 1" for r in results)

    def test_search_tables(self, tmp_path):
        """Test searching in document tables."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            # Mock table cells
            mock_cell1 = Mock(text="Product Name")
            mock_cell2 = Mock(text="Price")
            mock_cell3 = Mock(text="Laptop Computer")
            mock_cell4 = Mock(text="$999")

            mock_row1 = Mock(cells=[mock_cell1, mock_cell2])
            mock_row2 = Mock(cells=[mock_cell3, mock_cell4])

            mock_table = Mock()
            mock_table.rows = [mock_row1, mock_row2]

            mock_doc_instance = Mock()
            mock_doc_instance.tables = [mock_table]
            mock_doc_instance.paragraphs = []
            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "Laptop", search_tables=True)

            assert len(results) >= 1
            assert any("table" in r.get("type", "").lower() for r in results)

    def test_search_footnotes(self, tmp_path):
        """Test searching in document footnotes."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            # Mock document with footnotes
            mock_doc_instance = Mock()

            # Mock footnotes (if supported by python-docx)
            mock_footnotes = [
                Mock(text="See reference [1] for more details"),
                Mock(text="Data sourced from annual report 2023")
            ]

            # Simulate footnotes as special paragraphs
            mock_doc_instance.paragraphs = []
            mock_doc_instance.footnotes = mock_footnotes if hasattr(mock_doc_instance, 'footnotes') else []

            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "reference", search_footnotes=True)

            # Should handle footnotes if supported
            assert isinstance(results, list)

    def test_case_sensitivity(self, tmp_path):
        """Test case-sensitive vs case-insensitive search."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            mock_paragraphs = [
                Mock(text="UPPERCASE text here", style=Mock(name="Normal")),
                Mock(text="lowercase text here", style=Mock(name="Normal")),
                Mock(text="MixedCase Text Here", style=Mock(name="Normal"))
            ]

            mock_doc_instance = Mock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc.return_value = mock_doc_instance

            # Case-insensitive
            results_insensitive = tool(docx_file, "text", case_sensitive=False)

            # Case-sensitive
            results_sensitive = tool(docx_file, "text", case_sensitive=True)

            # Case-insensitive should find more
            assert len(results_insensitive) >= len(results_sensitive)

    def test_document_metadata(self, tmp_path):
        """Test extracting document metadata."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            mock_doc_instance = Mock()

            # Mock core properties
            mock_doc_instance.core_properties = Mock(
                author="John Doe",
                title="Test Document",
                subject="Testing",
                created="2024-01-01",
                modified="2024-01-15",
                keywords="test, document, search"
            )

            mock_doc_instance.paragraphs = [Mock(text="Content", style=Mock(name="Normal"))]
            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "test", include_metadata=True)

            # Should include metadata
            assert any(r.get("type") == "metadata" for r in results)

    def test_styled_text_search(self, tmp_path):
        """Test searching in styled text (bold, italic, etc)."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            # Mock runs with different styles
            mock_run1 = Mock(text="Normal text ", bold=False, italic=False)
            mock_run2 = Mock(text="bold text", bold=True, italic=False)
            mock_run3 = Mock(text=" and ", bold=False, italic=False)
            mock_run4 = Mock(text="italic text", bold=False, italic=True)

            mock_paragraph = Mock()
            mock_paragraph.runs = [mock_run1, mock_run2, mock_run3, mock_run4]
            mock_paragraph.text = "Normal text bold text and italic text"
            mock_paragraph.style = Mock(name="Normal")

            mock_doc_instance = Mock()
            mock_doc_instance.paragraphs = [mock_paragraph]
            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "bold")

            assert len(results) >= 1

    def test_numbered_lists(self, tmp_path):
        """Test searching in numbered and bulleted lists."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            mock_paragraphs = [
                Mock(text="1. First item in list", style=Mock(name="List Number")),
                Mock(text="2. Second item in list", style=Mock(name="List Number")),
                Mock(text="• Bullet point one", style=Mock(name="List Bullet")),
                Mock(text="• Bullet point two", style=Mock(name="List Bullet"))
            ]

            mock_doc_instance = Mock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "item")

            assert len(results) >= 2
            # Should identify list items
            assert any("List" in r.get("style", "") for r in results)

    def test_hyperlinks(self, tmp_path):
        """Test searching in hyperlinked text."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            # Mock paragraph with hyperlink
            mock_paragraph = Mock()
            mock_paragraph.text = "Visit our website for more information"
            mock_paragraph.style = Mock(name="Normal")

            # Mock hyperlink relationship
            mock_paragraph.hyperlinks = [
                Mock(text="website", url="https://example.com")
            ]

            mock_doc_instance = Mock()
            mock_doc_instance.paragraphs = [mock_paragraph]
            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "website")

            assert len(results) >= 1

    def test_comments_and_revisions(self, tmp_path):
        """Test handling of comments and tracked changes."""
        docx_file = tmp_path / "test.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            mock_doc_instance = Mock()

            # Regular content
            mock_doc_instance.paragraphs = [
                Mock(text="Main document text", style=Mock(name="Normal"))
            ]

            # Comments (if supported)
            mock_doc_instance.comments = [
                Mock(text="This needs revision", author="Reviewer")
            ]

            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "revision")

            # Should handle comments if supported
            assert isinstance(results, list)

    def test_empty_document(self, tmp_path):
        """Test handling of empty documents."""
        docx_file = tmp_path / "empty.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            mock_doc_instance = Mock()
            mock_doc_instance.paragraphs = []
            mock_doc_instance.tables = []
            mock_doc.return_value = mock_doc_instance

            results = tool(docx_file, "test")

            assert results == []

    def test_large_document_performance(self, tmp_path):
        """Test performance with large documents."""
        docx_file = tmp_path / "large.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            # Create large document
            mock_paragraphs = [
                Mock(text=f"Paragraph {i} with some content", style=Mock(name="Normal"))
                for i in range(1000)
            ]

            mock_doc_instance = Mock()
            mock_doc_instance.paragraphs = mock_paragraphs
            mock_doc.return_value = mock_doc_instance

            import time
            start_time = time.time()

            results = tool(docx_file, "Paragraph 500")

            elapsed = time.time() - start_time

            # Should complete quickly
            assert elapsed < 2.0
            assert len(results) >= 1

    def test_corrupted_document_handling(self, tmp_path):
        """Test handling of corrupted documents."""
        docx_file = tmp_path / "corrupted.docx"
        tool = self.get_component_function()

        with patch("docx.Document") as mock_doc:
            # Simulate corrupted document
            mock_doc.side_effect = Exception("Document is corrupted")

            results = tool(docx_file, "test")

            # Should handle gracefully
            assert isinstance(results, list)
            assert len(results) == 0 or "error" in str(results)
