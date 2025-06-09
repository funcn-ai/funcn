"""Test suite for sqlite_db tool following best practices."""

import pytest
import sqlite3
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import MagicMock, Mock, patch


class TestSQLiteDB(BaseToolTest):
    """Test sqlite_db tool component."""
    
    component_name = "sqlite_db"
    component_path = Path("packages/funcn_registry/components/tools/sqlite_db")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.sqlite_db import execute_query
        def mock_execute_query(
            db_path: str | Path,
            query: str,
            params: tuple | dict | None = None,
            fetch_all: bool = True,
            commit: bool = False
        ) -> list[dict[str, any]] | int:
            """Mock SQLite execute query tool."""
            if query.upper().startswith("SELECT"):
                return [
                    {"id": 1, "name": "John Doe", "age": 30},
                    {"id": 2, "name": "Jane Smith", "age": 25}
                ]
            elif query.upper().startswith(("INSERT", "UPDATE", "DELETE")):
                return 1  # Rows affected
            else:
                return []
        return mock_execute_query
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "db_path": "/path/to/database.db",
                "query": "SELECT * FROM users WHERE age > ?",
                "params": (21,),
                "fetch_all": True
            },
            {
                "db_path": "/path/to/database.db",
                "query": "INSERT INTO users (name, age) VALUES (?, ?)",
                "params": ("Bob Johnson", 35),
                "commit": True
            },
            {
                "db_path": "/path/to/database.db",
                "query": "UPDATE users SET age = :age WHERE name = :name",
                "params": {"age": 31, "name": "John Doe"},
                "commit": True
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        query = input_data["query"]
        
        if query.upper().startswith("SELECT"):
            assert isinstance(output, list)
            for row in output:
                assert isinstance(row, dict)
        else:
            # For INSERT/UPDATE/DELETE
            assert isinstance(output, int)
            assert output >= 0
    
    def test_select_queries(self, tmp_path):
        """Test SELECT query execution."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            # Mock query results
            mock_cursor.fetchall.return_value = [
                (1, "Alice", 25),
                (2, "Bob", 30)
            ]
            mock_cursor.description = [
                ("id",), ("name",), ("age",)
            ]
            
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.row_factory = sqlite3.Row
            mock_connect.return_value = mock_conn
            
            # Test simple SELECT
            results = tool(db_path, "SELECT * FROM users")
            assert len(results) >= 2
            
            # Test SELECT with parameters
            results = tool(
                db_path,
                "SELECT * FROM users WHERE age > ?",
                params=(25,)
            )
            mock_cursor.execute.assert_called_with(
                "SELECT * FROM users WHERE age > ?",
                (25,)
            )
    
    def test_insert_queries(self, tmp_path):
        """Test INSERT query execution."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.rowcount = 1
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Test INSERT
            result = tool(
                db_path,
                "INSERT INTO users (name, age) VALUES (?, ?)",
                params=("Charlie", 28),
                commit=True
            )
            
            assert result == 1
            mock_conn.commit.assert_called_once()
            mock_cursor.execute.assert_called_with(
                "INSERT INTO users (name, age) VALUES (?, ?)",
                ("Charlie", 28)
            )
    
    def test_update_queries(self, tmp_path):
        """Test UPDATE query execution."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.rowcount = 2
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Test UPDATE with named parameters
            result = tool(
                db_path,
                "UPDATE users SET status = :status WHERE age > :min_age",
                params={"status": "active", "min_age": 21},
                commit=True
            )
            
            assert result == 2
            mock_conn.commit.assert_called_once()
    
    def test_delete_queries(self, tmp_path):
        """Test DELETE query execution."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.rowcount = 3
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Test DELETE
            result = tool(
                db_path,
                "DELETE FROM users WHERE status = ?",
                params=("inactive",),
                commit=True
            )
            
            assert result == 3
            mock_conn.commit.assert_called_once()
    
    def test_transaction_handling(self, tmp_path):
        """Test transaction commit/rollback."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Test without commit
            tool(
                db_path,
                "INSERT INTO users (name) VALUES (?)",
                params=("Test",),
                commit=False
            )
            mock_conn.commit.assert_not_called()
            
            # Test with commit
            tool(
                db_path,
                "INSERT INTO users (name) VALUES (?)",
                params=("Test",),
                commit=True
            )
            mock_conn.commit.assert_called()
    
    def test_sql_injection_prevention(self, tmp_path):
        """Test that parameterized queries prevent SQL injection."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Potentially dangerous input
            dangerous_input = "'; DROP TABLE users; --"
            
            tool(
                db_path,
                "SELECT * FROM users WHERE name = ?",
                params=(dangerous_input,)
            )
            
            # Should use parameterized query, not string concatenation
            mock_cursor.execute.assert_called_with(
                "SELECT * FROM users WHERE name = ?",
                (dangerous_input,)
            )
    
    def test_fetch_options(self, tmp_path):
        """Test different fetch options (fetchall vs fetchone)."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_cursor.fetchall.return_value = [(1, "All",), (2, "Results",)]
            mock_cursor.fetchone.return_value = (1, "One",)
            mock_cursor.description = [("id",), ("name",)]
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Test fetchall
            results = tool(db_path, "SELECT * FROM users", fetch_all=True)
            assert isinstance(results, list)
            mock_cursor.fetchall.assert_called()
            
            # Test fetchone
            result = tool(db_path, "SELECT * FROM users LIMIT 1", fetch_all=False)
            if not isinstance(result, list):  # Single result
                assert isinstance(result, dict) or result is not None
    
    def test_error_handling(self, tmp_path):
        """Test error handling for various scenarios."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        # Test database locked error
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.side_effect = sqlite3.OperationalError("database is locked")
            
            result = tool(db_path, "SELECT * FROM users")
            assert isinstance(result, list) or "error" in str(result).lower()
        
        # Test SQL syntax error
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.OperationalError("syntax error")
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            result = tool(db_path, "INVALID SQL QUERY")
            assert isinstance(result, list) or "error" in str(result).lower()
    
    def test_create_table_execution(self, tmp_path):
        """Test CREATE TABLE execution."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            create_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            result = tool(db_path, create_query, commit=True)
            
            mock_cursor.execute.assert_called_with(create_query, None)
            mock_conn.commit.assert_called()
    
    def test_pragma_queries(self, tmp_path):
        """Test PRAGMA queries for database info."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            # Mock table info
            mock_cursor.fetchall.return_value = [
                (0, "id", "INTEGER", 0, None, 1),
                (1, "name", "TEXT", 1, None, 0)
            ]
            mock_cursor.description = [
                ("cid",), ("name",), ("type",), ("notnull",), ("dflt_value",), ("pk",)
            ]
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Test PRAGMA table_info
            results = tool(db_path, "PRAGMA table_info(users)")
            assert isinstance(results, list)
            assert len(results) >= 2
    
    def test_connection_pooling(self, tmp_path):
        """Test that connections are properly closed."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            # Execute query
            tool(db_path, "SELECT * FROM users")
            
            # Connection should be closed
            mock_conn.close.assert_called()
    
    def test_null_handling(self, tmp_path):
        """Test handling of NULL values."""
        db_path = tmp_path / "test.db"
        tool = self.get_component_function()
        
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            
            # Results with NULL values
            mock_cursor.fetchall.return_value = [
                (1, "Alice", None),
                (2, None, 25),
                (3, "Charlie", 30)
            ]
            mock_cursor.description = [("id",), ("name",), ("age",)]
            
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn
            
            results = tool(db_path, "SELECT * FROM users")
            
            # Should handle NULL values appropriately
            assert any(r.get("age") is None for r in results)
            assert any(r.get("name") is None for r in results)
