"""Test suite for pg_search_tool following best practices."""

import asyncio
import json
import os
import pytest
from datetime import datetime

# Import the tool functions
from packages.funcn_registry.components.tools.pg_search.tool import (
    PGSearchResult,
    QueryResult,
    execute_postgres_query,
    full_text_search,
    get_table_data,
    query_postgres,
    search_table,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class TestPgSearchTool(BaseToolTest):
    """Test cases for PostgreSQL database search and query tool."""

    component_name = "pg_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/pg_search")
    
    def create_mock_pool_and_conn(self, mock_asyncpg, fetch_results=None, side_effect=None):
        """Create properly mocked pool and connection for testing."""
        mock_pool = AsyncMock()
        mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
        
        mock_conn = AsyncMock()
        # Create a proper async context manager for pool.acquire()
        mock_acquire_cm = AsyncMock()
        mock_acquire_cm.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_acquire_cm.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire = Mock(return_value=mock_acquire_cm)
        
        if side_effect:
            mock_conn.fetch = AsyncMock(side_effect=side_effect)
        elif fetch_results is not None:
            mock_conn.fetch = AsyncMock(return_value=fetch_results)
        
        mock_pool.close = AsyncMock()
        
        return mock_pool, mock_conn
    
    def create_mock_record(self, data_dict):
        """Create a mock asyncpg Record object."""
        class MockRecord:
            def __init__(self, data):
                self._data = data
                
            def keys(self):
                return list(self._data.keys())
                
            def values(self):
                return list(self._data.values())
                
            def items(self):
                return list(self._data.items())
                
            def __iter__(self):
                return iter(self._data.items())
                
            def __getitem__(self, key):
                return self._data[key]
                
        return MockRecord(data_dict)

    def get_component_function(self):
        """Get the main tool function."""
        # This tool has multiple functions, return the main one
        return execute_postgres_query

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {"connection_string": "postgresql://user:pass@localhost/db", "query": "SELECT * FROM users LIMIT 10"},
            {"connection_string": "postgresql://user:pass@localhost/db", "table_name": "products", "search_text": "laptop", "search_columns": ["name", "description"]},
            {"connection_string": "postgresql://user:pass@localhost/db", "table_name": "orders", "where_conditions": {"status": "pending"}, "limit": 50},
        ]

    @pytest.mark.asyncio
    async def test_execute_query_basic(self):
        """Test basic query execution."""
        # Create mock records that behave like asyncpg Record objects
        mock_record1 = self.create_mock_record({"id": 1, "name": "John Doe", "email": "john@example.com"})
        mock_record2 = self.create_mock_record({"id": 2, "name": "Jane Smith", "email": "jane@example.com"})
        
        mock_results = [mock_record1, mock_record2]

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, fetch_results=mock_results)

            result = await query_postgres("postgresql://localhost/test", "SELECT * FROM users LIMIT 2")

            assert result.success is True
            assert result.total_rows == 2
            assert len(result.results) == 2
            assert result.results[0].row_data["name"] == "John Doe"
            mock_conn.fetch.assert_called_once_with("SELECT * FROM users LIMIT 2")

    @pytest.mark.asyncio
    async def test_search_table_functionality(self):
        """Test table search functionality."""
        mock_record = self.create_mock_record({"id": 1, "name": "Gaming Laptop", "description": "High-performance laptop for gaming"})
        
        mock_results = [mock_record]

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, fetch_results=mock_results)

            result = await search_table(
                "postgresql://localhost/test",
                table_name="products",
                search_text="laptop",
                search_columns=["name", "description"],
                limit=10
            )

            assert result.success is True
            assert result.total_rows == 1
            assert "laptop" in result.results[0].row_data["description"].lower()

    @pytest.mark.asyncio
    async def test_full_text_search(self):
        """Test full-text search functionality."""
        mock_record1 = self.create_mock_record({"id": 1, "title": "Python Programming", "content": "Learn Python basics"})
        
        mock_results = [mock_record1]

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, fetch_results=mock_results)

            result = await full_text_search(
                "postgresql://localhost/test",
                table_name="articles",
                search_text="Python",
                search_columns=["title", "content"],
                limit=10
            )

            assert result.success is True
            assert result.total_rows == 1
            assert result.results[0].row_data["title"] == "Python Programming"

    @pytest.mark.asyncio
    async def test_get_table_data_with_conditions(self):
        """Test retrieving table data with WHERE conditions."""
        mock_record = self.create_mock_record({"id": 1, "status": "pending", "total": 150.00})
        
        mock_results = [mock_record]

        # Mock schema result
        mock_schema_record = self.create_mock_record({
            "column_name": "id",
            "data_type": "integer",
            "is_nullable": "NO",
            "column_default": None,
            "character_maximum_length": None
        })
        
        mock_schema_results = [mock_schema_record]

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, side_effect=[mock_results, mock_schema_results])

            result = await get_table_data(
                "postgresql://localhost/test",
                table_name="orders",
                where_conditions={"status": "pending"},
                limit=10
            )

            assert result.success is True
            assert result.total_rows == 1
            assert result.results[0].row_data["status"] == "pending"
            assert "schema" in result.metadata

    @pytest.mark.asyncio
    async def test_connection_error_handling(self):
        """Test database connection error handling."""
        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_asyncpg.create_pool = AsyncMock(side_effect=Exception("Connection refused"))

            result = await execute_postgres_query("postgresql://localhost/test", query="SELECT 1")

            assert result.success is False
            assert "Connection refused" in result.error

    @pytest.mark.asyncio
    async def test_query_timeout(self):
        """Test query timeout handling."""
        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, side_effect=TimeoutError("Query timeout"))

            result = await execute_postgres_query("postgresql://localhost/test", query="SELECT pg_sleep(30)")

            assert result.success is False
            assert "Query timeout" in result.error

    @pytest.mark.asyncio
    async def test_empty_result_handling(self):
        """Test handling of empty result sets."""
        mock_results = []

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, fetch_results=mock_results)

            result = await execute_postgres_query("postgresql://localhost/test", query="SELECT * FROM users WHERE id = -1")

            assert result.success is True
            assert result.total_rows == 0
            assert len(result.results) == 0

    @pytest.mark.asyncio
    async def test_invalid_connection_string(self):
        """Test behavior with invalid connection string."""
        result = await execute_postgres_query("invalid://connection", query="SELECT 1")
        
        assert result.success is False
        assert "Connection string must start with postgresql:// or postgres://" in result.error

    @pytest.mark.asyncio
    async def test_null_value_handling(self):
        """Test handling of NULL values in results."""
        mock_record = self.create_mock_record({"id": 1, "name": "Test User", "email": None})
        
        mock_results = [mock_record]

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, fetch_results=mock_results)

            result = await execute_postgres_query("postgresql://localhost/test", query="SELECT * FROM users WHERE email IS NULL")

            assert result.success is True
            assert result.results[0].row_data["email"] is None

    @pytest.mark.asyncio
    async def test_complex_where_conditions(self):
        """Test complex WHERE conditions including IN and NULL."""
        mock_record = self.create_mock_record({"id": 1, "status": "active", "category": "electronics"})
        
        mock_results = [mock_record]

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, fetch_results=mock_results)

            result = await execute_postgres_query(
                "postgresql://localhost/test",
                table_name="products",
                where_conditions={
                    "status": "active",
                    "category": ["electronics", "computers"],
                    "deleted_at": None
                }
            )

            assert result.success is True
            assert result.total_rows == 1

    @pytest.mark.asyncio
    async def test_order_by_and_pagination(self):
        """Test ORDER BY and pagination with LIMIT/OFFSET."""
        mock_records = []
        for i in range(5):
            mock_record = self.create_mock_record({"id": i + 1, "created_at": f"2023-01-{i+1:02d}"})
            mock_records.append(mock_record)

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            mock_pool, mock_conn = self.create_mock_pool_and_conn(mock_asyncpg, fetch_results=mock_records)

            result = await execute_postgres_query(
                "postgresql://localhost/test",
                table_name="events",
                order_by="created_at DESC",
                limit=5,
                offset=10
            )

            assert result.success is True
            assert result.total_rows == 5

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        # Output should be a PGSearchResult
        assert isinstance(output, dict) or isinstance(output, PGSearchResult)
        
        if isinstance(output, dict):
            assert "success" in output
            assert "query" in output
            assert "total_rows" in output
            assert "results" in output
            assert "execution_time" in output

    @pytest.mark.unit
    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        functions = [execute_postgres_query, query_postgres, search_table, full_text_search, get_table_data]

        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 20
            
    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """Test handling of concurrent queries."""
        mock_results1 = [self.create_mock_record({"count": 100})]
        mock_results2 = [self.create_mock_record({"sum": 5000})]

        with patch("packages.funcn_registry.components.tools.pg_search.tool.asyncpg") as mock_asyncpg:
            # Create separate pools for each query
            mock_pool1 = AsyncMock()
            mock_pool2 = AsyncMock()
            
            mock_asyncpg.create_pool = AsyncMock(side_effect=[mock_pool1, mock_pool2])

            # Create two mock connections with proper async context managers
            mock_conn1 = AsyncMock()
            mock_conn2 = AsyncMock()
            
            # Create async context managers for pool.acquire()
            mock_acquire_cm1 = AsyncMock()
            mock_acquire_cm1.__aenter__ = AsyncMock(return_value=mock_conn1)
            mock_acquire_cm1.__aexit__ = AsyncMock(return_value=None)
            mock_pool1.acquire = Mock(return_value=mock_acquire_cm1)
            
            mock_acquire_cm2 = AsyncMock()
            mock_acquire_cm2.__aenter__ = AsyncMock(return_value=mock_conn2)
            mock_acquire_cm2.__aexit__ = AsyncMock(return_value=None)
            mock_pool2.acquire = Mock(return_value=mock_acquire_cm2)
            
            mock_conn1.fetch = AsyncMock(return_value=mock_results1)
            mock_conn2.fetch = AsyncMock(return_value=mock_results2)
            
            mock_pool1.close = AsyncMock()
            mock_pool2.close = AsyncMock()

            # Execute queries concurrently
            results = await asyncio.gather(
                query_postgres("postgresql://localhost/test", "SELECT COUNT(*) FROM users"),
                query_postgres("postgresql://localhost/test", "SELECT SUM(amount) FROM transactions")
            )

            assert results[0].success is True
            assert results[0].results[0].row_data["count"] == 100
            assert results[1].success is True
            assert results[1].results[0].row_data["sum"] == 5000
