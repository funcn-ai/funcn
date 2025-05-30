"""Test suite for pg_search_tool following best practices."""

import asyncio
import json
import pytest
from datetime import datetime

# Import the tool functions
from packages.funcn_registry.components.tools.pg_search_tool.tool import (
    execute_query,
    full_text_search,
    get_schema_info,
    search_by_column,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, Mock, patch


class TestPgSearchTool(BaseToolTest):
    """Test cases for PostgreSQL database search and query tool."""

    component_name = "pg_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/pg_search_tool")

    def get_component_function(self):
        """Get the main tool function."""
        # This tool has multiple functions, return the main one
        return execute_query

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {"query": "SELECT * FROM users LIMIT 10", "params": None},
            {"query": "SELECT * FROM products WHERE price > $1", "params": [100]},
            {"query": "INSERT INTO logs (message, created_at) VALUES ($1, $2)", "params": ["Test log", datetime.now()]},
        ]

    @pytest.mark.asyncio
    async def test_execute_query_basic(self):
        """Test basic query execution."""
        mock_results = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        ]

        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            # Mock connection pool
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            # Mock connection and fetch
            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.fetch = AsyncMock(return_value=mock_results)

            result = await execute_query("SELECT * FROM users LIMIT 2")

            assert result == mock_results
            mock_conn.fetch.assert_called_once_with("SELECT * FROM users LIMIT 2")

    @pytest.mark.asyncio
    async def test_execute_query_with_params(self):
        """Test query execution with parameters."""
        mock_results = [
            {"id": 3, "name": "Premium Widget", "price": 150.00},
            {"id": 4, "name": "Deluxe Gadget", "price": 299.99},
        ]

        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.fetch = AsyncMock(return_value=mock_results)

            result = await execute_query("SELECT * FROM products WHERE price > $1", params=[100])

            assert result == mock_results
            mock_conn.fetch.assert_called_once_with("SELECT * FROM products WHERE price > $1", 100)

    @pytest.mark.asyncio
    async def test_full_text_search(self):
        """Test full-text search functionality."""
        mock_results = [
            {"id": 1, "title": "Python Programming", "content": "Learn Python basics", "rank": 0.9},
            {"id": 2, "title": "Advanced Python", "content": "Python advanced topics", "rank": 0.8},
        ]

        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.fetch = AsyncMock(return_value=mock_results)

            result = await full_text_search(
                table="articles", search_columns=["title", "content"], search_query="Python", limit=10
            )

            assert len(result) == 2
            assert result[0]["title"] == "Python Programming"
            mock_conn.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_by_column(self):
        """Test column-specific search."""
        mock_results = [
            {"id": 1, "name": "Alice Johnson", "department": "Engineering"},
            {"id": 2, "name": "Bob Anderson", "department": "Sales"},
        ]

        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.fetch = AsyncMock(return_value=mock_results)

            result = await search_by_column(table="employees", column="name", search_value="%son%", limit=10)

            assert len(result) == 2
            mock_conn.fetch.assert_called_once()
            # Verify ILIKE was used for case-insensitive search
            call_args = mock_conn.fetch.call_args[0][0]
            assert "ILIKE" in call_args

    @pytest.mark.asyncio
    async def test_get_schema_info(self):
        """Test schema information retrieval."""
        mock_tables = [
            {"table_name": "users", "table_type": "BASE TABLE"},
            {"table_name": "products", "table_type": "BASE TABLE"},
            {"table_name": "user_view", "table_type": "VIEW"},
        ]

        mock_columns = [
            {"table_name": "users", "column_name": "id", "data_type": "integer", "is_nullable": "NO"},
            {"table_name": "users", "column_name": "name", "data_type": "character varying", "is_nullable": "NO"},
            {"table_name": "users", "column_name": "email", "data_type": "character varying", "is_nullable": "NO"},
        ]

        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)

            # Mock different responses for different queries
            mock_conn.fetch = AsyncMock(side_effect=[mock_tables, mock_columns])

            result = await get_schema_info(table_name="users")

            assert "tables" in result
            assert "columns" in result
            assert len(result["tables"]) == 3
            assert len(result["columns"]) == 3

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test database connection error handling."""
        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_asyncpg.create_pool = AsyncMock(side_effect=Exception("Connection refused"))

            with pytest.raises(Exception) as exc_info:
                await execute_query("SELECT 1")

            assert "Connection refused" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_query_timeout(self):
        """Test query timeout handling."""
        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.fetch = AsyncMock(side_effect=TimeoutError("Query timeout"))

            with pytest.raises(asyncio.TimeoutError) as exc_info:
                await execute_query("SELECT pg_sleep(30)")

            assert "Query timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self):
        """Test that parameterized queries prevent SQL injection."""
        mock_results = []

        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.fetch = AsyncMock(return_value=mock_results)

            # Attempt SQL injection via parameter
            malicious_input = "'; DROP TABLE users; --"
            await search_by_column(table="users", column="name", search_value=malicious_input)

            # Verify the query was parameterized (not concatenated)
            call_args = mock_conn.fetch.call_args
            query = call_args[0][0]
            params = call_args[0][1]

            assert "$1" in query  # Parameter placeholder
            assert params == malicious_input  # Value passed as parameter, not in query

    @pytest.mark.asyncio
    async def test_large_result_set_handling(self):
        """Test handling of large result sets."""
        # Create mock results with 1000 rows
        mock_results = [{"id": i, "data": f"Row {i}"} for i in range(1000)]

        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.fetch = AsyncMock(return_value=mock_results)

            result = await execute_query("SELECT * FROM large_table")

            assert len(result) == 1000
            assert result[0]["id"] == 0
            assert result[999]["id"] == 999

    @pytest.mark.asyncio
    async def test_transaction_handling(self):
        """Test transaction commit and rollback."""
        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.execute = AsyncMock(return_value="INSERT 1")

            # Test INSERT operation
            await execute_query("INSERT INTO users (name, email) VALUES ($1, $2)", params=["Test User", "test@example.com"])

            mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_empty_result_handling(self):
        """Test handling of empty result sets."""
        mock_results = []

        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.asyncpg") as mock_asyncpg:
            mock_pool = AsyncMock()
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

            mock_conn = AsyncMock()
            mock_pool.acquire = AsyncMock(return_value=mock_conn)
            mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_conn.__aexit__ = AsyncMock(return_value=None)
            mock_conn.fetch = AsyncMock(return_value=mock_results)

            result = await execute_query("SELECT * FROM users WHERE id = -1")

            assert result == []
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_missing_database_url(self):
        """Test behavior when DATABASE_URL is missing."""
        with patch("packages.funcn_registry.components.tools.pg_search_tool.tool.os.getenv", return_value=None):
            with pytest.raises(ValueError) as exc_info:
                await execute_query("SELECT 1")

            assert "DATABASE_URL" in str(exc_info.value)

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        # For query results, output should be a list
        if isinstance(output, list):
            # Each item should be a dict (row)
            for item in output:
                assert isinstance(item, dict), "Each result row should be a dictionary"
        # For schema info, output should be a dict
        elif isinstance(output, dict):
            if "tables" in output:
                assert isinstance(output["tables"], list)
            if "columns" in output:
                assert isinstance(output["columns"], list)

    @pytest.mark.unit
    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        functions = [execute_query, full_text_search, get_schema_info, search_by_column]

        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 20
            assert func.__name__ in func.__doc__.lower() or "search" in func.__doc__.lower() or "query" in func.__doc__.lower()
