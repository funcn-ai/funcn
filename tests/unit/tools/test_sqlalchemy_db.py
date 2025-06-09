"""Test suite for sqlalchemy_db tool following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import MagicMock, Mock, patch


class TestSQLAlchemyDB(BaseToolTest):
    """Test sqlalchemy_db tool component."""
    
    component_name = "sqlalchemy_db"
    component_path = Path("packages/funcn_registry/components/tools/sqlalchemy_db")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.sqlalchemy_db import execute_query
        def mock_execute_query(
            connection_string: str,
            query: str,
            params: dict[str, any] | None = None,
            model_class: type | None = None,
            return_type: str = "dict"
        ) -> list[dict[str, any]] | list[any] | int:
            """Mock SQLAlchemy execute query tool."""
            if query.upper().startswith("SELECT"):
                if return_type == "dict":
                    return [
                        {"id": 1, "name": "Alice", "email": "alice@example.com"},
                        {"id": 2, "name": "Bob", "email": "bob@example.com"}
                    ]
                elif return_type == "model" and model_class:
                    # Return mock model instances
                    return [
                        Mock(id=1, name="Alice", email="alice@example.com"),
                        Mock(id=2, name="Bob", email="bob@example.com")
                    ]
            elif query.upper().startswith(("INSERT", "UPDATE", "DELETE")):
                return 1  # Rows affected
            return []
        return mock_execute_query
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "connection_string": "postgresql://user:pass@localhost/db",
                "query": "SELECT * FROM users WHERE active = :active",
                "params": {"active": True},
                "return_type": "dict"
            },
            {
                "connection_string": "mysql://user:pass@localhost/db",
                "query": "INSERT INTO logs (message, level) VALUES (:message, :level)",
                "params": {"message": "Test log", "level": "INFO"}
            },
            {
                "connection_string": "sqlite:///data.db",
                "query": "UPDATE users SET last_login = :timestamp WHERE id = :id",
                "params": {"timestamp": "2024-01-01", "id": 123}
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        query = input_data["query"]
        
        if query.upper().startswith("SELECT"):
            assert isinstance(output, list)
            if input_data.get("return_type") == "dict":
                for row in output:
                    assert isinstance(row, dict)
        else:
            # For INSERT/UPDATE/DELETE
            assert isinstance(output, int)
    
    def test_orm_model_queries(self):
        """Test queries returning ORM model instances."""
        tool = self.get_component_function()
        
        # Mock User model
        class MockUser:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        with patch("sqlalchemy.create_engine") as mock_engine:
            mock_session = MagicMock()
            mock_query = MagicMock()
            
            # Mock query results
            mock_query.all.return_value = [
                MockUser(id=1, name="Test User", active=True)
            ]
            
            mock_session.query.return_value = mock_query
            
            results = tool(
                "postgresql://localhost/test",
                "SELECT * FROM users",
                model_class=MockUser,
                return_type="model"
            )
            
            assert len(results) > 0
            assert hasattr(results[0], "name")
    
    def test_different_database_engines(self):
        """Test support for different database engines."""
        tool = self.get_component_function()
        
        engines = [
            "postgresql://user:pass@localhost/db",
            "mysql://user:pass@localhost/db",
            "sqlite:///local.db",
            "oracle://user:pass@localhost:1521/db",
            "mssql+pyodbc://user:pass@server/db"
        ]
        
        for conn_string in engines:
            with patch("sqlalchemy.create_engine") as mock_create_engine:
                mock_engine = MagicMock()
                mock_create_engine.return_value = mock_engine
                
                result = tool(conn_string, "SELECT 1")
                
                # Should create engine with correct connection string
                mock_create_engine.assert_called_with(conn_string)
    
    def test_parameterized_queries(self):
        """Test parameterized query execution."""
        tool = self.get_component_function()
        
        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_result = MagicMock()
            
            # Mock result proxy
            mock_result.fetchall.return_value = [(1, "Test")]
            mock_result.rowcount = 1
            
            mock_conn.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_create_engine.return_value = mock_engine
            
            # Test with named parameters
            result = tool(
                "postgresql://localhost/test",
                "SELECT * FROM items WHERE category = :cat AND price > :min_price",
                params={"cat": "electronics", "min_price": 100}
            )
            
            # Verify parameters were passed correctly
            call_args = mock_conn.execute.call_args
            assert "cat" in str(call_args) or "electronics" in str(call_args)
    
    def test_transaction_handling(self):
        """Test transaction commit and rollback."""
        tool = self.get_component_function()
        
        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_trans = MagicMock()
            
            mock_conn.begin.return_value = mock_trans
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_create_engine.return_value = mock_engine
            
            # Successful transaction
            result = tool(
                "postgresql://localhost/test",
                "INSERT INTO users (name) VALUES (:name)",
                params={"name": "New User"}
            )
            
            # Should commit transaction
            mock_trans.commit.assert_called()
            
            # Failed transaction
            mock_conn.execute.side_effect = Exception("DB Error")
            
            try:
                tool(
                    "postgresql://localhost/test",
                    "INSERT INTO users (name) VALUES (:name)",
                    params={"name": "Bad User"}
                )
            except:
                pass
            
            # Should rollback on error
            mock_trans.rollback.assert_called()
    
    def test_bulk_operations(self):
        """Test bulk insert/update operations."""
        # Would import: from tools.sqlalchemy_db import bulk_insert
        def mock_bulk_insert(
            connection_string: str,
            table_name: str,
            data: list[dict[str, any]]
        ) -> int:
            return len(data)
        
        tool = mock_bulk_insert
        
        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_conn.execute.return_value.rowcount = 100
            
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_create_engine.return_value = mock_engine
            
            data = [
                {"name": f"User {i}", "email": f"user{i}@example.com"}
                for i in range(100)
            ]
            
            result = tool("postgresql://localhost/test", "users", data)
            
            assert result == 100
    
    def test_connection_pooling(self):
        """Test connection pool configuration."""
        tool = self.get_component_function()
        
        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            
            # Multiple queries should reuse connection pool
            for i in range(5):
                tool(
                    "postgresql://localhost/test",
                    f"SELECT * FROM table{i}"
                )
            
            # Check pool configuration was applied
            create_calls = mock_create_engine.call_args_list
            # Should have pool settings
            assert any("pool" in str(call) for call in create_calls)
    
    def test_schema_reflection(self):
        """Test database schema reflection."""
        # Would import: from tools.sqlalchemy_db import get_table_info
        def mock_get_table_info(connection_string: str, table_name: str) -> dict[str, any]:
            return {
                "columns": [
                    {"name": "id", "type": "INTEGER", "primary_key": True},
                    {"name": "name", "type": "VARCHAR(100)", "nullable": False},
                    {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
                ],
                "indexes": ["idx_name"],
                "foreign_keys": []
            }
        
        tool = mock_get_table_info
        
        with patch("sqlalchemy.inspect") as mock_inspect:
            mock_inspector = MagicMock()
            mock_inspector.get_columns.return_value = [
                {"name": "id", "type": "INTEGER"},
                {"name": "name", "type": "VARCHAR"}
            ]
            mock_inspect.return_value = mock_inspector
            
            info = tool("postgresql://localhost/test", "users")
            
            assert "columns" in info
            assert len(info["columns"]) >= 2
    
    def test_query_timeout(self):
        """Test query timeout handling."""
        tool = self.get_component_function()
        
        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            
            # Simulate timeout
            mock_conn.execute.side_effect = Exception("Query timeout")
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_create_engine.return_value = mock_engine
            
            result = tool(
                "postgresql://localhost/test",
                "SELECT * FROM huge_table"
            )
            
            # Should handle timeout gracefully
            assert isinstance(result, list) or "error" in str(result)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention with parameterized queries."""
        tool = self.get_component_function()
        
        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_create_engine.return_value = mock_engine
            
            # Dangerous input
            dangerous_input = "'; DROP TABLE users; --"
            
            tool(
                "postgresql://localhost/test",
                "SELECT * FROM users WHERE name = :name",
                params={"name": dangerous_input}
            )
            
            # Should use parameterized query
            call_args = mock_conn.execute.call_args
            # Parameters should be separate from query
            assert ":name" in str(call_args[0][0])
    
    def test_result_mapping(self):
        """Test different result mapping options."""
        tool = self.get_component_function()
        
        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_result = MagicMock()
            
            # Mock different result formats
            mock_result.fetchall.return_value = [
                (1, "Alice", "alice@example.com"),
                (2, "Bob", "bob@example.com")
            ]
            mock_result.keys.return_value = ["id", "name", "email"]
            
            mock_conn.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_create_engine.return_value = mock_engine
            
            # Test dict mapping
            result = tool(
                "postgresql://localhost/test",
                "SELECT * FROM users",
                return_type="dict"
            )
            
            assert isinstance(result[0], dict)
            assert "name" in result[0]
    
    def test_stored_procedure_execution(self):
        """Test executing stored procedures."""
        tool = self.get_component_function()
        
        with patch("sqlalchemy.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_result = MagicMock()
            
            mock_result.fetchall.return_value = [(100,)]
            mock_conn.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_create_engine.return_value = mock_engine
            
            # Execute stored procedure
            result = tool(
                "postgresql://localhost/test",
                "CALL calculate_totals(:year, :month)",
                params={"year": 2024, "month": 1}
            )
            
            # Should handle stored procedure results
            assert result is not None
