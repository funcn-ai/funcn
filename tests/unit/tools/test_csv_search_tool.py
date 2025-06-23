"""Test suite for csv_search_tool following best practices."""

import asyncio
import io
import pandas as pd
import pytest

# Import the actual tool components
from packages.funcn_registry.components.tools.csv_search.tool import (
    CSVSearchArgs,
    CSVSearchResponse,
    CSVSearchResult,
    search_csv_content,
)
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, mock_open, patch


class TestCSVSearchTool(BaseToolTest):
    """Test csv_search_tool component."""

    component_name = "csv_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/csv_search")

    def get_component_function(self):
        """Import the tool function."""
        return search_csv_content

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            CSVSearchArgs(
                file_path="/path/to/data.csv",
                query="engineering",
                columns=["department"],
                case_sensitive=False
            ),
            CSVSearchArgs(
                file_path="/path/to/employees.csv",
                query="john",
                columns=["name", "email"],
                exact_match=False
            ),
            CSVSearchArgs(
                file_path="/path/to/products.csv",
                query="laptop",
                max_results=10
            )
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, CSVSearchResponse)
        
        if hasattr(input_data, 'max_results'):
            assert len(output.results) <= input_data.max_results

        for result in output.results:
            assert isinstance(result, CSVSearchResult)
            assert isinstance(result.row_index, int)
            assert isinstance(result.row_data, dict)
            assert isinstance(result.matched_columns, list)
            assert isinstance(result.match_scores, dict)

    @pytest.mark.asyncio
    async def test_search_specific_columns(self, tmp_path):
        """Test searching in specific columns only."""
        # Create test CSV
        csv_content = "name,email,department\nJohn Doe,john@example.com,Engineering\nJane Smith,jane@example.com,Marketing\nBob Johnson,bob@example.com,Engineering\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        tool = self.get_component_function()

        # Search only in department column
        args = CSVSearchArgs(
            file_path=str(csv_file),
            query="engineering",
            columns=["department"],
            case_sensitive=False
        )
        result = await tool(args)

        # Should find 2 engineering entries
        assert len(result.results) == 2
        for res in result.results:
            assert "Engineering" in res.row_data["department"]

    @pytest.mark.asyncio
    async def test_case_sensitive_search(self, tmp_path):
        """Test case-sensitive vs case-insensitive search."""
        csv_content = "product,price\nLaptop,1000\nLAPTOP,1200\nlaptop,900\nDesktop,800\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Case-insensitive search
        args_insensitive = CSVSearchArgs(
            file_path=str(csv_file),
            query="laptop",
            case_sensitive=False
        )
        results_insensitive = await tool(args_insensitive)

        # Case-sensitive search (should also use exact match for proper behavior)
        args_sensitive = CSVSearchArgs(
            file_path=str(csv_file),
            query="laptop",
            case_sensitive=True,
            exact_match=True
        )
        results_sensitive = await tool(args_sensitive)

        # Case-insensitive should find all 3 laptop entries
        assert len(results_insensitive.results) == 3
        # Case-sensitive should find only lowercase "laptop"
        assert len(results_sensitive.results) == 1

    @pytest.mark.asyncio
    async def test_exact_match_vs_fuzzy(self, tmp_path):
        """Test exact match vs fuzzy/partial matching."""
        csv_content = "name,id\nJohn Doe,1\nJohnny Smith,2\nDon Johnson,3\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Exact match
        args_exact = CSVSearchArgs(
            file_path=str(csv_file),
            query="John",
            exact_match=True
        )
        exact_results = await tool(args_exact)

        # Fuzzy match
        args_fuzzy = CSVSearchArgs(
            file_path=str(csv_file),
            query="John",
            exact_match=False
        )
        fuzzy_results = await tool(args_fuzzy)

        # Fuzzy should find more matches (John, Johnny, Johnson)
        assert len(fuzzy_results.results) >= len(exact_results.results)

    @pytest.mark.asyncio
    async def test_numeric_search(self, tmp_path):
        """Test searching for numeric values."""
        csv_content = "product,price,quantity\nA,100,5\nB,200,10\nC,100,5\nD,300,15\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Search for numeric value
        args = CSVSearchArgs(
            file_path=str(csv_file),
            query="100",
            columns=["price"]
        )
        results = await tool(args)

        # Should find products with price 100
        assert len(results.results) == 2

    @pytest.mark.asyncio
    async def test_limit_parameter(self, tmp_path):
        """Test that limit parameter restricts results."""
        # Create large dataset
        csv_content = "id,value\n"
        for i in range(100):
            csv_content += f"{i},test\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Search with limit
        args_limited = CSVSearchArgs(
            file_path=str(csv_file),
            query="test",
            max_results=5
        )
        results = await tool(args_limited)
        assert len(results.results) <= 5

        # Search without limit (default is 50)
        args_no_limit = CSVSearchArgs(
            file_path=str(csv_file),
            query="test",
            max_results=50
        )
        results_no_limit = await tool(args_no_limit)
        assert len(results_no_limit.results) >= len(results.results)

    @pytest.mark.asyncio
    async def test_empty_csv_handling(self, tmp_path):
        """Test handling of empty CSV files."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("column1,column2\n")  # Headers only

        tool = self.get_component_function()

        args = CSVSearchArgs(
            file_path=str(empty_csv),
            query="test"
        )
        results = await tool(args)
        assert results.results == []

    @pytest.mark.asyncio
    async def test_missing_column_handling(self, tmp_path):
        """Test handling when specified columns don't exist."""
        csv_content = "name,age\nJohn,30\nJane,25\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Try to search non-existent column
        args = CSVSearchArgs(
            file_path=str(csv_file),
            query="test",
            columns=["nonexistent_column"]
        )
        results = await tool(args)

        # Should handle gracefully - no results since column doesn't exist
        assert isinstance(results, CSVSearchResponse)
        assert results.results == []

    @pytest.mark.asyncio
    async def test_special_characters_in_search(self, tmp_path):
        """Test searching for special characters."""
        csv_content = "email,notes\nuser@example.com,$100 payment\nadmin+test@example.com,50% discount\ninfo@company.org,C++ developer\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Search for special characters
        special_queries = ["@example.com", "$100", "50%", "C++", "admin+"]

        for query in special_queries:
            args = CSVSearchArgs(
                file_path=str(csv_file),
                query=query
            )
            results = await tool(args)
            assert isinstance(results, CSVSearchResponse)
            # Each query should find at least one result
            assert len(results.results) >= 1

    @pytest.mark.asyncio
    async def test_large_csv_performance(self, tmp_path):
        """Test performance with large CSV files."""
        # Create large dataset
        csv_content = "id,text,category\n"
        for i in range(10000):
            category = ["A", "B", "C", "D"][i % 4]
            csv_content += f"{i},row {i} data,{category}\n"
        csv_file = tmp_path / "large.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        import time
        start_time = time.time()

        args = CSVSearchArgs(
            file_path=str(csv_file),
            query="row 5",
            max_results=10
        )
        results = await tool(args)

        elapsed = time.time() - start_time

        # Should complete quickly even for large files
        assert elapsed < 2.0
        assert len(results.results) <= 10

    @pytest.mark.asyncio
    async def test_encoding_handling(self, tmp_path):
        """Test handling of different file encodings."""
        # Test with UTF-8 encoding (default)
        csv_content = "text,id\ncafé,1\nrésumé,2\nnaïve,3\n"
        csv_file = tmp_path / "encoded.csv"
        csv_file.write_text(csv_content, encoding="utf-8")
        
        tool = self.get_component_function()

        args = CSVSearchArgs(
            file_path=str(csv_file),
            query="café"
        )
        results = await tool(args)
        assert isinstance(results, CSVSearchResponse)
        assert len(results.results) >= 1

    @pytest.mark.asyncio
    async def test_multiline_cell_search(self, tmp_path):
        """Test searching in cells with multiline content."""
        csv_content = '''description,id
"First line
Second line
Third line",1
"Single line",2
"Another
multiline
entry",3
'''
        csv_file = tmp_path / "multiline.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Search for text in multiline cells
        args1 = CSVSearchArgs(
            file_path=str(csv_file),
            query="Second line"
        )
        results = await tool(args1)
        assert len(results.results) >= 1

        args2 = CSVSearchArgs(
            file_path=str(csv_file),
            query="multiline"
        )
        results = await tool(args2)
        assert len(results.results) >= 1

    @pytest.mark.asyncio
    async def test_filters_functionality(self, tmp_path):
        """Test filtering functionality before search."""
        csv_content = "name,age,department,salary\nJohn,25,Engineering,50000\nJane,35,Marketing,60000\nBob,45,Engineering,80000\nAlice,30,HR,55000\n"
        csv_file = tmp_path / "employees.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Test greater than filter
        args_gt = CSVSearchArgs(
            file_path=str(csv_file),
            query="Engineering",
            filters={"age": ">30"}
        )
        results_gt = await tool(args_gt)
        assert len(results_gt.results) == 1  # Only Bob is >30 in Engineering
        assert results_gt.results[0].row_data["name"] == "Bob"

        # Test less than filter
        args_lt = CSVSearchArgs(
            file_path=str(csv_file),
            query="0",  # Search for 0 in any field
            columns=["salary"],
            filters={"age": "<35"}
        )
        results_lt = await tool(args_lt)
        # John (25) and Alice (30) have salaries containing "0"
        assert len(results_lt.results) == 2

        # Test exact match filter
        args_exact = CSVSearchArgs(
            file_path=str(csv_file),
            query="",  # Empty query to match all
            filters={"department": "Engineering"},
            exact_match=True
        )
        results_exact = await tool(args_exact)
        # Should find both Engineering employees when searching empty string
        assert len(results_exact.results) == 2

    @pytest.mark.asyncio
    async def test_error_handling(self, tmp_path):
        """Test error handling for various edge cases."""
        tool = self.get_component_function()

        # Test non-existent file
        args_missing = CSVSearchArgs(
            file_path=str(tmp_path / "nonexistent.csv"),
            query="test"
        )
        result = await tool(args_missing)
        assert result.error is not None
        assert "not found" in result.error

        # Test invalid CSV content
        invalid_csv = tmp_path / "invalid.csv"
        invalid_csv.write_text("This is not a valid CSV\n\n\n")
        
        args_invalid = CSVSearchArgs(
            file_path=str(invalid_csv),
            query="test"
        )
        result = await tool(args_invalid)
        # Should handle gracefully
        assert isinstance(result, CSVSearchResponse)
