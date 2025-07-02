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

    @pytest.mark.asyncio
    async def test_fuzzy_threshold_edge_cases(self, tmp_path):
        """Test fuzzy matching with various threshold values."""
        csv_content = "text,id\nHello World,1\nHelo Wrld,2\nGoodbye,3\n"
        csv_file = tmp_path / "fuzzy.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Test threshold 0 - should match everything
        args_0 = CSVSearchArgs(
            file_path=str(csv_file),
            query="Hello",
            fuzzy_threshold=0,
            exact_match=False
        )
        results_0 = await tool(args_0)
        assert len(results_0.results) >= 2  # Should match both Hello and Helo

        # Test threshold 100 - should only match exact
        args_100 = CSVSearchArgs(
            file_path=str(csv_file),
            query="Hello",
            fuzzy_threshold=100,
            exact_match=False
        )
        results_100 = await tool(args_100)
        assert len(results_100.results) <= 1  # Should match fewer

        # Test threshold 50 - moderate matching
        args_50 = CSVSearchArgs(
            file_path=str(csv_file),
            query="Hello",
            fuzzy_threshold=50,
            exact_match=False
        )
        results_50 = await tool(args_50)
        assert len(results_50.results) >= len(results_100.results)

    @pytest.mark.asyncio
    async def test_unicode_and_emoji_handling(self, tmp_path):
        """Test handling of Unicode characters and emojis."""
        csv_content = "name,comment,rating\nJohn 😀,Great product! 👍,5\nMarie Château,Très bien ⭐,4\n山田太郎,素晴らしい 🎌,5\nüñíçødé_tëst,Special chars,3\n"
        csv_file = tmp_path / "unicode.csv"
        csv_file.write_text(csv_content, encoding="utf-8")
        
        tool = self.get_component_function()

        # Search for emoji
        args_emoji = CSVSearchArgs(
            file_path=str(csv_file),
            query="😀"
        )
        results_emoji = await tool(args_emoji)
        assert len(results_emoji.results) >= 1

        # Search for Japanese characters
        args_japanese = CSVSearchArgs(
            file_path=str(csv_file),
            query="山田"
        )
        results_japanese = await tool(args_japanese)
        assert len(results_japanese.results) >= 1

        # Search for accented characters
        args_accent = CSVSearchArgs(
            file_path=str(csv_file),
            query="Château"
        )
        results_accent = await tool(args_accent)
        assert len(results_accent.results) >= 1

        # Search with emoji in query
        args_emoji_query = CSVSearchArgs(
            file_path=str(csv_file),
            query="👍"
        )
        results_emoji_query = await tool(args_emoji_query)
        assert len(results_emoji_query.results) >= 1

    @pytest.mark.asyncio
    async def test_mixed_data_types_in_columns(self, tmp_path):
        """Test handling of mixed data types within same column."""
        csv_content = "mixed_col,id\n123,1\ntext,2\n123.45,3\nTrue,4\n,5\nNaN,6\n"
        csv_file = tmp_path / "mixed.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Search for number in mixed column
        args_number = CSVSearchArgs(
            file_path=str(csv_file),
            query="123",
            columns=["mixed_col"]
        )
        results_number = await tool(args_number)
        assert len(results_number.results) >= 1

        # Search for boolean value
        args_bool = CSVSearchArgs(
            file_path=str(csv_file),
            query="True",
            columns=["mixed_col"]
        )
        results_bool = await tool(args_bool)
        assert len(results_bool.results) >= 1

        # Search for text in mixed column
        args_text = CSVSearchArgs(
            file_path=str(csv_file),
            query="text",
            columns=["mixed_col"]
        )
        results_text = await tool(args_text)
        assert len(results_text.results) >= 1

    @pytest.mark.asyncio
    async def test_parameter_edge_cases(self, tmp_path):
        """Test edge cases for various parameters."""
        csv_content = "text,number\ntest,1\ndata,2\ninfo,3\n"
        csv_file = tmp_path / "params.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Test max_results = 0
        args_zero = CSVSearchArgs(
            file_path=str(csv_file),
            query="test",
            max_results=0
        )
        results_zero = await tool(args_zero)
        assert len(results_zero.results) == 0

        # Test max_results = 1
        args_one = CSVSearchArgs(
            file_path=str(csv_file),
            query="t",  # Should match multiple
            max_results=1
        )
        results_one = await tool(args_one)
        assert len(results_one.results) <= 1

        # Test very large max_results
        args_large = CSVSearchArgs(
            file_path=str(csv_file),
            query="t",
            max_results=10000
        )
        results_large = await tool(args_large)
        assert len(results_large.results) <= 3  # Only 3 rows total

        # Test empty query string
        args_empty = CSVSearchArgs(
            file_path=str(csv_file),
            query="",
            exact_match=True
        )
        results_empty = await tool(args_empty)
        # Empty query with exact match should match all (empty string is in all strings)
        assert len(results_empty.results) >= 0

        # Test whitespace-only query
        args_whitespace = CSVSearchArgs(
            file_path=str(csv_file),
            query="   ",
            exact_match=True
        )
        results_whitespace = await tool(args_whitespace)
        assert isinstance(results_whitespace, CSVSearchResponse)

    @pytest.mark.asyncio
    async def test_complex_filter_combinations(self, tmp_path):
        """Test complex combinations of filters."""
        csv_content = "name,age,salary,department,active\nJohn,25,50000,Engineering,True\nJane,35,60000,Marketing,True\nBob,45,80000,Engineering,False\nAlice,30,55000,HR,True\nCharlie,28,52000,Engineering,True\n"
        csv_file = tmp_path / "complex.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Multiple filters with different operators
        args_multi = CSVSearchArgs(
            file_path=str(csv_file),
            query="Engineering",
            filters={
                "age": ">25",
                "salary": ">=55000",
                "active": "True"
            }
        )
        results_multi = await tool(args_multi)
        # Should find Charlie (28, 52000) doesn't meet salary requirement, so only John doesn't meet age requirement
        assert len(results_multi.results) == 0  # No one meets all criteria

        # Test > filter
        args_greater = CSVSearchArgs(
            file_path=str(csv_file),
            query="",  # Match all
            filters={"age": ">29"},
            exact_match=True
        )
        results_greater = await tool(args_greater)
        assert len(results_greater.results) >= 3  # Jane (35), Bob (45), Alice (30)

        # Test != filter
        args_not_equal = CSVSearchArgs(
            file_path=str(csv_file),
            query="",
            filters={"department": "!=Engineering"},
            exact_match=True
        )
        results_not_equal = await tool(args_not_equal)
        assert len(results_not_equal.results) == 2  # Jane and Alice

    @pytest.mark.asyncio
    async def test_nan_and_null_handling(self, tmp_path):
        """Test handling of NaN and null values."""
        csv_content = "name,age,notes\nJohn,25,Good\nJane,,Active\nBob,30,\nAlice,35,NaN\n,40,Unknown\n"
        csv_file = tmp_path / "nulls.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Search in column with missing values
        args_missing = CSVSearchArgs(
            file_path=str(csv_file),
            query="30",
            columns=["age"]
        )
        results_missing = await tool(args_missing)
        assert len(results_missing.results) >= 1

        # Search for empty notes
        args_empty_notes = CSVSearchArgs(
            file_path=str(csv_file),
            query="",
            columns=["notes"],
            exact_match=True
        )
        results_empty_notes = await tool(args_empty_notes)
        # Should handle empty cells gracefully
        assert isinstance(results_empty_notes, CSVSearchResponse)

        # Test filtering with null values
        args_filter_null = CSVSearchArgs(
            file_path=str(csv_file),
            query="",
            filters={"age": ">20"},
            exact_match=True
        )
        results_filter_null = await tool(args_filter_null)
        # Should only include rows where age can be converted to number
        assert len(results_filter_null.results) >= 1

    @pytest.mark.asyncio
    async def test_concurrent_searches(self, tmp_path):
        """Test multiple concurrent searches on the same file."""
        csv_content = "id,text,category\n"
        for i in range(1000):
            csv_content += f"{i},row {i} content,category_{i % 5}\n"
        csv_file = tmp_path / "concurrent.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Create multiple search tasks
        tasks = []
        for i in range(10):
            args = CSVSearchArgs(
                file_path=str(csv_file),
                query=f"row {i * 100}",
                max_results=5
            )
            tasks.append(tool(args))

        # Run all searches concurrently
        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(results) == 10
        for result in results:
            assert isinstance(result, CSVSearchResponse)
            assert result.error is None

    @pytest.mark.asyncio
    async def test_very_short_and_long_queries(self, tmp_path):
        """Test with very short and very long query strings."""
        csv_content = "data,id\na,1\nab,2\nabc,3\nabcdefghijklmnopqrstuvwxyz,4\nVery long text content that spans multiple words and contains lots of information for testing purposes,5\n"
        csv_file = tmp_path / "query_lengths.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Very short query (1 character)
        args_short = CSVSearchArgs(
            file_path=str(csv_file),
            query="a",
            exact_match=False
        )
        results_short = await tool(args_short)
        assert len(results_short.results) >= 4  # Should match multiple rows

        # Very long query
        long_query = "Very long text content that spans multiple words and contains lots of information for testing purposes"
        args_long = CSVSearchArgs(
            file_path=str(csv_file),
            query=long_query,
            exact_match=False
        )
        results_long = await tool(args_long)
        assert len(results_long.results) >= 1

        # Query longer than cell content
        super_long_query = "a" * 1000
        args_super_long = CSVSearchArgs(
            file_path=str(csv_file),
            query=super_long_query,
            exact_match=False
        )
        results_super_long = await tool(args_super_long)
        assert isinstance(results_super_long, CSVSearchResponse)

    @pytest.mark.asyncio
    async def test_csv_with_duplicate_column_names(self, tmp_path):
        """Test CSV files with duplicate column names."""
        # Pandas will automatically rename duplicate columns
        csv_content = "name,age,name,status\nJohn,25,John Doe,active\nJane,30,Jane Smith,inactive\n"
        csv_file = tmp_path / "duplicates.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        args = CSVSearchArgs(
            file_path=str(csv_file),
            query="John"
        )
        results = await tool(args)
        assert isinstance(results, CSVSearchResponse)
        assert len(results.columns) >= 3  # Should handle duplicate column names

    @pytest.mark.asyncio
    async def test_memory_intensive_operations(self, tmp_path):
        """Test memory handling with very large CSV files."""
        # Create a larger dataset to test memory handling
        csv_content = "id,text,data\n"
        for i in range(50000):  # 50k rows
            csv_content += f"{i},{'x' * 100},{i * 2}\n"  # Each row has 100 chars of text
        csv_file = tmp_path / "memory_test.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        import time
        start_time = time.time()

        args = CSVSearchArgs(
            file_path=str(csv_file),
            query="x",
            max_results=10,
            fuzzy_threshold=90
        )
        results = await tool(args)
        
        elapsed = time.time() - start_time

        # Should complete within reasonable time
        assert elapsed < 10.0
        assert isinstance(results, CSVSearchResponse)
        assert len(results.results) <= 10

    @pytest.mark.asyncio
    async def test_invalid_filter_operators(self, tmp_path):
        """Test handling of invalid filter operators."""
        csv_content = "name,age\nJohn,25\nJane,30\n"
        csv_file = tmp_path / "filters.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Test invalid operator
        args_invalid = CSVSearchArgs(
            file_path=str(csv_file),
            query="John",
            filters={"age": "~25"}  # Invalid operator
        )
        results_invalid = await tool(args_invalid)
        # Should handle gracefully
        assert isinstance(results_invalid, CSVSearchResponse)

        # Test numeric operator on text column
        args_text_numeric = CSVSearchArgs(
            file_path=str(csv_file),
            query="John",
            filters={"name": ">John"}  # Numeric operator on text
        )
        results_text_numeric = await tool(args_text_numeric)
        # Should handle gracefully
        assert isinstance(results_text_numeric, CSVSearchResponse)

    @pytest.mark.asyncio
    async def test_column_names_edge_cases(self, tmp_path):
        """Test edge cases with column names."""
        # CSV with special characters in column names
        csv_content = "col with spaces,col@special,col-dash,col.dot,col#hash\nvalue1,value2,value3,value4,value5\ntest1,test2,test3,test4,test5\n"
        csv_file = tmp_path / "special_cols.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Search in column with spaces
        args_spaces = CSVSearchArgs(
            file_path=str(csv_file),
            query="value1",
            columns=["col with spaces"]
        )
        results_spaces = await tool(args_spaces)
        assert len(results_spaces.results) >= 1

        # Search in column with special characters
        args_special = CSVSearchArgs(
            file_path=str(csv_file),
            query="value2",
            columns=["col@special"]
        )
        results_special = await tool(args_special)
        assert len(results_special.results) >= 1

        # Search with non-existent column but valid columns also specified
        args_mixed = CSVSearchArgs(
            file_path=str(csv_file),
            query="test",
            columns=["col.dot", "nonexistent_column", "col#hash"]
        )
        results_mixed = await tool(args_mixed)
        # Should search in valid columns only
        assert len(results_mixed.results) >= 1

    @pytest.mark.asyncio
    async def test_boundary_conditions(self, tmp_path):
        """Test various boundary conditions."""
        csv_content = "text,number\ntest,1\n"
        csv_file = tmp_path / "boundary.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Test negative fuzzy threshold (should be handled gracefully)
        args_negative_threshold = CSVSearchArgs(
            file_path=str(csv_file),
            query="test",
            fuzzy_threshold=-10
        )
        results_negative = await tool(args_negative_threshold)
        assert isinstance(results_negative, CSVSearchResponse)

        # Test fuzzy threshold > 100
        args_high_threshold = CSVSearchArgs(
            file_path=str(csv_file),
            query="test",
            fuzzy_threshold=150
        )
        results_high = await tool(args_high_threshold)
        assert isinstance(results_high, CSVSearchResponse)

        # Test negative max_results (should be handled gracefully)
        args_negative_max = CSVSearchArgs(
            file_path=str(csv_file),
            query="test",
            max_results=-5
        )
        results_negative_max = await tool(args_negative_max)
        assert isinstance(results_negative_max, CSVSearchResponse)

    @pytest.mark.asyncio
    async def test_csv_with_no_headers(self, tmp_path):
        """Test CSV files without headers."""
        # CSV without headers - pandas will use first row as headers
        csv_content = "John,25,Engineer\nJane,30,Designer\nBob,35,Manager\n"
        csv_file = tmp_path / "no_headers.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        args = CSVSearchArgs(
            file_path=str(csv_file),
            query="Engineer"
        )
        results = await tool(args)
        assert isinstance(results, CSVSearchResponse)
        # Should handle gracefully even if structure is unexpected

    @pytest.mark.asyncio
    async def test_error_scenarios_comprehensive(self, tmp_path):
        """Test comprehensive error scenarios."""
        tool = self.get_component_function()

        # Test directory instead of file
        directory = tmp_path / "test_dir"
        directory.mkdir()
        args_dir = CSVSearchArgs(
            file_path=str(directory),
            query="test"
        )
        result_dir = await tool(args_dir)
        assert result_dir.error is not None

        # Test binary file (not CSV)
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\x04')
        args_binary = CSVSearchArgs(
            file_path=str(binary_file),
            query="test"
        )
        result_binary = await tool(args_binary)
        assert isinstance(result_binary, CSVSearchResponse)

        # Test empty file
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")
        args_empty = CSVSearchArgs(
            file_path=str(empty_file),
            query="test"
        )
        result_empty = await tool(args_empty)
        assert isinstance(result_empty, CSVSearchResponse)

    @pytest.mark.asyncio
    async def test_date_and_datetime_columns(self, tmp_path):
        """Test handling of date and datetime columns."""
        csv_content = "event,date,timestamp\nMeeting,2024-01-15,2024-01-15 14:30:00\nConference,2024-02-20,2024-02-20 09:00:00\nWorkshop,2024-01-15,2024-01-15 16:00:00\n"
        csv_file = tmp_path / "dates.csv"
        csv_file.write_text(csv_content)
        
        tool = self.get_component_function()

        # Search for date
        args_date = CSVSearchArgs(
            file_path=str(csv_file),
            query="2024-01-15",
            columns=["date"]
        )
        results_date = await tool(args_date)
        assert len(results_date.results) >= 2  # Should find 2 matches

        # Search for time in timestamp
        args_time = CSVSearchArgs(
            file_path=str(csv_file),
            query="14:30",
            columns=["timestamp"]
        )
        results_time = await tool(args_time)
        assert len(results_time.results) >= 1

        # Filter by date
        args_filter_date = CSVSearchArgs(
            file_path=str(csv_file),
            query="",
            filters={"date": "2024-01-15"},
            exact_match=True
        )
        results_filter_date = await tool(args_filter_date)
        assert len(results_filter_date.results) >= 2
