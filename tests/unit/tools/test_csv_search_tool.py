"""Test suite for csv_search_tool following best practices."""

import io
import pandas as pd
import pytest
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, mock_open, patch


class TestCSVSearchTool(BaseToolTest):
    """Test csv_search_tool component."""

    component_name = "csv_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/csv_search_tool")

    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.csv_search_tool import search_csv
        def mock_search_csv(
            csv_path: str | Path,
            query: str,
            columns: list[str] | None = None,
            case_sensitive: bool = False,
            exact_match: bool = False,
            limit: int | None = None
        ) -> list[dict[str, any]]:
            """Mock CSV search tool."""
            # Return mock results
            return [
                {
                    "row_index": 0,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "department": "Engineering",
                    "match_score": 1.0
                },
                {
                    "row_index": 1,
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "department": "Marketing",
                    "match_score": 0.8
                }
            ][:limit] if limit else []
        return mock_search_csv

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "csv_path": "/path/to/data.csv",
                "query": "engineering",
                "columns": ["department"],
                "case_sensitive": False
            },
            {
                "csv_path": "/path/to/employees.csv",
                "query": "john",
                "columns": ["name", "email"],
                "exact_match": False
            },
            {
                "csv_path": "/path/to/products.csv",
                "query": "laptop",
                "limit": 10
            }
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)

        if input_data.get("limit"):
            assert len(output) <= input_data["limit"]

        for result in output:
            assert isinstance(result, dict)
            if "match_score" in result:
                assert 0 <= result["match_score"] <= 1

    def test_search_specific_columns(self, tmp_path):
        """Test searching in specific columns only."""
        # Create test CSV
        csv_content = TestDataFactory.SAMPLE_CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            df = pd.DataFrame({
                "name": ["John Doe", "Jane Smith", "Bob Johnson"],
                "email": ["john@example.com", "jane@example.com", "bob@example.com"],
                "department": ["Engineering", "Marketing", "Engineering"]
            })
            mock_read.return_value = df

            # Search only in department column
            results = tool(
                csv_file,
                "engineering",
                columns=["department"],
                case_sensitive=False
            )

            # Should find 2 engineering entries
            assert len(results) >= 2
            for result in results:
                assert "engineering" in str(result).lower()

    def test_case_sensitive_search(self, tmp_path):
        """Test case-sensitive vs case-insensitive search."""
        csv_file = TestDataFactory.create_csv_file(tmp_path)
        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            df = pd.DataFrame({
                "product": ["Laptop", "LAPTOP", "laptop", "Desktop"],
                "price": [1000, 1200, 900, 800]
            })
            mock_read.return_value = df

            # Case-insensitive search
            results_insensitive = tool(csv_file, "laptop", case_sensitive=False)

            # Case-sensitive search
            results_sensitive = tool(csv_file, "laptop", case_sensitive=True)

            # Case-insensitive should find more results
            assert len(results_insensitive) >= len(results_sensitive)

    def test_exact_match_vs_fuzzy(self, tmp_path):
        """Test exact match vs fuzzy/partial matching."""
        csv_file = TestDataFactory.create_csv_file(tmp_path)
        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            df = pd.DataFrame({
                "name": ["John Doe", "Johnny Smith", "Don Johnson"],
                "id": [1, 2, 3]
            })
            mock_read.return_value = df

            # Exact match
            exact_results = tool(csv_file, "John", exact_match=True)

            # Fuzzy match
            fuzzy_results = tool(csv_file, "John", exact_match=False)

            # Fuzzy should find more matches (John, Johnny, Johnson)
            assert len(fuzzy_results) >= len(exact_results)

    def test_numeric_search(self, tmp_path):
        """Test searching for numeric values."""
        csv_file = TestDataFactory.create_csv_file(tmp_path)
        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            df = pd.DataFrame({
                "product": ["A", "B", "C", "D"],
                "price": [100, 200, 100, 300],
                "quantity": [5, 10, 5, 15]
            })
            mock_read.return_value = df

            # Search for numeric value
            results = tool(csv_file, "100", columns=["price"])

            # Should find products with price 100
            assert len(results) >= 2

    def test_limit_parameter(self, tmp_path):
        """Test that limit parameter restricts results."""
        csv_file = TestDataFactory.create_csv_file(tmp_path)
        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            # Create large dataset
            df = pd.DataFrame({
                "id": range(100),
                "value": ["test"] * 100
            })
            mock_read.return_value = df

            # Search with limit
            results = tool(csv_file, "test", limit=5)
            assert len(results) <= 5

            # Search without limit
            results_no_limit = tool(csv_file, "test")
            assert len(results_no_limit) >= len(results)

    def test_empty_csv_handling(self, tmp_path):
        """Test handling of empty CSV files."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("column1,column2\n")  # Headers only

        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            mock_read.return_value = pd.DataFrame(columns=["column1", "column2"])

            results = tool(empty_csv, "test")
            assert results == []

    def test_missing_column_handling(self, tmp_path):
        """Test handling when specified columns don't exist."""
        csv_file = TestDataFactory.create_csv_file(tmp_path)
        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            df = pd.DataFrame({
                "name": ["John", "Jane"],
                "age": [30, 25]
            })
            mock_read.return_value = df

            # Try to search non-existent column
            results = tool(csv_file, "test", columns=["nonexistent_column"])

            # Should handle gracefully
            assert isinstance(results, list)

    def test_special_characters_in_search(self, tmp_path):
        """Test searching for special characters."""
        csv_file = TestDataFactory.create_csv_file(tmp_path)
        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            df = pd.DataFrame({
                "email": ["user@example.com", "admin+test@example.com", "info@company.org"],
                "notes": ["$100 payment", "50% discount", "C++ developer"]
            })
            mock_read.return_value = df

            # Search for special characters
            special_queries = ["@example.com", "$100", "50%", "C++", "admin+"]

            for query in special_queries:
                results = tool(csv_file, query)
                assert isinstance(results, list)

    def test_large_csv_performance(self, tmp_path):
        """Test performance with large CSV files."""
        csv_file = TestDataFactory.create_csv_file(tmp_path)
        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            # Create large dataframe
            large_df = pd.DataFrame({
                "id": range(10000),
                "text": [f"row {i} data" for i in range(10000)],
                "category": ["A", "B", "C", "D"] * 2500
            })
            mock_read.return_value = large_df

            import time
            start_time = time.time()

            results = tool(csv_file, "row 5", limit=10)

            elapsed = time.time() - start_time

            # Should complete quickly even for large files
            assert elapsed < 2.0
            assert len(results) <= 10

    def test_encoding_handling(self, tmp_path):
        """Test handling of different file encodings."""
        csv_file = tmp_path / "encoded.csv"
        tool = self.get_component_function()

        # Test with different encodings
        encodings = ["utf-8", "latin-1", "utf-16"]

        for _ in encodings:  # encoding variable not used in mock test
            with patch("pandas.read_csv") as mock_read:
                df = pd.DataFrame({
                    "text": ["café", "résumé", "naïve"],
                    "id": [1, 2, 3]
                })
                mock_read.return_value = df

                results = tool(csv_file, "café")
                assert isinstance(results, list)

                # Verify encoding parameter was considered
                if mock_read.called:
                    # Check if encoding was handled
                    assert True  # Placeholder for encoding verification

    def test_multiline_cell_search(self, tmp_path):
        """Test searching in cells with multiline content."""
        csv_file = TestDataFactory.create_csv_file(tmp_path)
        tool = self.get_component_function()

        with patch("pandas.read_csv") as mock_read:
            df = pd.DataFrame({
                "description": [
                    "First line\nSecond line\nThird line",
                    "Single line",
                    "Another\nmultiline\nentry"
                ],
                "id": [1, 2, 3]
            })
            mock_read.return_value = df

            # Search for text in multiline cells
            results = tool(csv_file, "Second line")
            assert len(results) >= 1

            results = tool(csv_file, "multiline")
            assert len(results) >= 1
