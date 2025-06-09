"""SQLite Database Tool for persistent agent state storage."""

import asyncio
import json
import sqlite3
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import Any, Optional, Union


class SQLiteQueryResult(BaseModel):
    """Result of a SQLite query operation."""

    success: bool = Field(..., description="Whether the query was successful")
    query: str = Field(..., description="The SQL query executed")
    rows_affected: int = Field(0, description="Number of rows affected by the query")
    results: list[dict[str, Any]] = Field(default_factory=list, description="Query results as list of dictionaries")
    columns: list[str] = Field(default_factory=list, description="Column names from the query")
    error: str | None = Field(None, description="Error message if query failed")
    execution_time: float = Field(..., description="Query execution time in seconds")


class SQLiteTableInfo(BaseModel):
    """Information about a SQLite table."""

    name: str = Field(..., description="Table name")
    columns: list[dict[str, Any]] = Field(..., description="Column information")
    row_count: int = Field(..., description="Number of rows in the table")
    indexes: list[str] = Field(default_factory=list, description="List of indexes on the table")


class SQLiteDatabaseInfo(BaseModel):
    """Information about a SQLite database."""

    path: str = Field(..., description="Database file path")
    size_bytes: int = Field(..., description="Database file size in bytes")
    tables: list[SQLiteTableInfo] = Field(..., description="Information about all tables")
    version: str = Field(..., description="SQLite version")


@contextmanager
def get_sqlite_connection(db_path: str) -> Iterator[sqlite3.Connection]:
    """Get a SQLite connection with proper error handling."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


async def execute_sqlite_query(
    db_path: str, query: str, parameters: tuple | dict | None = None, fetch_results: bool = True, commit: bool = True
) -> SQLiteQueryResult:
    """Execute a SQLite query with proper error handling and async support.

    Args:
        db_path: Path to the SQLite database file
        query: SQL query to execute
        parameters: Query parameters (for parameterized queries)
        fetch_results: Whether to fetch and return results
        commit: Whether to commit the transaction

    Returns:
        SQLiteQueryResult with query results or error information
    """
    start_time = asyncio.get_event_loop().time()

    try:
        # Ensure database directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        # Run query in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _execute_query_sync, str(db_file), query, parameters, fetch_results, commit)

        execution_time = asyncio.get_event_loop().time() - start_time
        result.execution_time = execution_time
        return result

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return SQLiteQueryResult(success=False, query=query, rows_affected=0, error=str(e), execution_time=execution_time)


def _execute_query_sync(
    db_path: str, query: str, parameters: tuple | dict | None, fetch_results: bool, commit: bool
) -> SQLiteQueryResult:
    """Synchronous query execution for thread pool."""
    with get_sqlite_connection(db_path) as conn:
        cursor = conn.cursor()

        try:
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            rows_affected = cursor.rowcount
            results = []
            columns = []

            if fetch_results and cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                results = [dict(zip(columns, row, strict=False)) for row in rows]

            if commit:
                conn.commit()

            return SQLiteQueryResult(
                success=True,
                query=query,
                rows_affected=rows_affected,
                results=results,
                columns=columns,
                error=None,
                execution_time=0,  # Will be set by async wrapper
            )

        except Exception as e:
            conn.rollback()
            raise e


async def create_agent_state_table(db_path: str, table_name: str = "agent_state") -> SQLiteQueryResult:
    """Create a table for storing agent state.

    Args:
        db_path: Path to the SQLite database file
        table_name: Name of the state table

    Returns:
        SQLiteQueryResult indicating success or failure
    """
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT NOT NULL,
        conversation_id TEXT,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        data_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT,
        UNIQUE(agent_id, conversation_id, key)
    )
    """

    # Create indexes for better performance
    create_index_queries = [
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_agent_id ON {table_name}(agent_id)",
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_conversation_id ON {table_name}(conversation_id)",
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_key ON {table_name}(key)",
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_updated_at ON {table_name}(updated_at)",
    ]

    # Execute table creation
    result = await execute_sqlite_query(db_path, create_table_query, commit=True)

    if result.success:
        # Create indexes
        for index_query in create_index_queries:
            await execute_sqlite_query(db_path, index_query, commit=True)

    return result


async def store_agent_state(
    db_path: str,
    agent_id: str,
    key: str,
    value: Any,
    conversation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    table_name: str = "agent_state",
) -> SQLiteQueryResult:
    """Store or update agent state in the database.

    Args:
        db_path: Path to the SQLite database file
        agent_id: Unique identifier for the agent
        key: State key
        value: State value (will be JSON serialized)
        conversation_id: Optional conversation identifier
        metadata: Optional metadata dictionary
        table_name: Name of the state table

    Returns:
        SQLiteQueryResult indicating success or failure
    """
    # Serialize value and metadata
    value_json = json.dumps(value) if not isinstance(value, str) else value
    metadata_json = json.dumps(metadata) if metadata else None
    data_type = type(value).__name__

    # Use UPSERT to insert or update
    query = f"""
    INSERT INTO {table_name} (agent_id, conversation_id, key, value, data_type, metadata, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(agent_id, conversation_id, key)
    DO UPDATE SET
        value = excluded.value,
        data_type = excluded.data_type,
        metadata = excluded.metadata,
        updated_at = CURRENT_TIMESTAMP
    """

    parameters = (agent_id, conversation_id, key, value_json, data_type, metadata_json)

    return await execute_sqlite_query(db_path, query, parameters, commit=True)


async def get_agent_state(
    db_path: str, agent_id: str, key: str | None = None, conversation_id: str | None = None, table_name: str = "agent_state"
) -> SQLiteQueryResult:
    """Retrieve agent state from the database.

    Args:
        db_path: Path to the SQLite database file
        agent_id: Unique identifier for the agent
        key: Optional specific key to retrieve
        conversation_id: Optional conversation identifier
        table_name: Name of the state table

    Returns:
        SQLiteQueryResult with the state data
    """
    conditions = ["agent_id = ?"]
    parameters: list[Any] = [agent_id]

    if conversation_id is not None:
        conditions.append("conversation_id = ?")
        parameters.append(conversation_id)
    else:
        conditions.append("conversation_id IS NULL")

    if key is not None:
        conditions.append("key = ?")
        parameters.append(key)

    query = f"""
    SELECT id, agent_id, conversation_id, key, value, data_type,
           created_at, updated_at, metadata
    FROM {table_name}
    WHERE {' AND '.join(conditions)}
    ORDER BY updated_at DESC
    """

    result = await execute_sqlite_query(db_path, query, tuple(parameters))

    # Deserialize JSON values
    if result.success and result.results:
        for row in result.results:
            try:
                # Try to deserialize value based on data_type
                if row['data_type'] != 'str':
                    row['value'] = json.loads(row['value'])
                if row['metadata']:
                    row['metadata'] = json.loads(row['metadata'])
            except json.JSONDecodeError:
                pass  # Keep as string if deserialization fails

    return result


async def delete_agent_state(
    db_path: str, agent_id: str, key: str | None = None, conversation_id: str | None = None, table_name: str = "agent_state"
) -> SQLiteQueryResult:
    """Delete agent state from the database.

    Args:
        db_path: Path to the SQLite database file
        agent_id: Unique identifier for the agent
        key: Optional specific key to delete
        conversation_id: Optional conversation identifier
        table_name: Name of the state table

    Returns:
        SQLiteQueryResult indicating success or failure
    """
    conditions = ["agent_id = ?"]
    parameters: list[Any] = [agent_id]

    if conversation_id is not None:
        conditions.append("conversation_id = ?")
        parameters.append(conversation_id)

    if key is not None:
        conditions.append("key = ?")
        parameters.append(key)

    query = f"DELETE FROM {table_name} WHERE {' AND '.join(conditions)}"

    return await execute_sqlite_query(db_path, query, tuple(parameters), commit=True)


async def get_database_info(db_path: str) -> SQLiteDatabaseInfo:
    """Get comprehensive information about the SQLite database.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        SQLiteDatabaseInfo with database details
    """
    db_file = Path(db_path)

    if not db_file.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    # Get file size
    size_bytes = db_file.stat().st_size

    # Get SQLite version
    version_result = await execute_sqlite_query(db_path, "SELECT sqlite_version()")
    sqlite_version = version_result.results[0]['sqlite_version()'] if version_result.success else "Unknown"

    # Get table information
    tables_result = await execute_sqlite_query(
        db_path, "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )

    tables = []
    if tables_result.success:
        for table_row in tables_result.results:
            table_name = table_row['name']

            # Get column info
            pragma_result = await execute_sqlite_query(db_path, f"PRAGMA table_info({table_name})")

            columns = []
            if pragma_result.success:
                for col in pragma_result.results:
                    columns.append(
                        {
                            'name': col['name'],
                            'type': col['type'],
                            'nullable': not col['notnull'],
                            'default': col['dflt_value'],
                            'primary_key': bool(col['pk']),
                        }
                    )

            # Get row count
            count_result = await execute_sqlite_query(db_path, f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = count_result.results[0]['count'] if count_result.success else 0

            # Get indexes
            index_result = await execute_sqlite_query(
                db_path, f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'"
            )
            indexes = [idx['name'] for idx in index_result.results] if index_result.success else []

            tables.append(SQLiteTableInfo(name=table_name, columns=columns, row_count=row_count, indexes=indexes))

    return SQLiteDatabaseInfo(path=str(db_file), size_bytes=size_bytes, tables=tables, version=sqlite_version)


# Convenience functions for common operations
async def query_agent_history(
    db_path: str,
    agent_id: str,
    conversation_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
    table_name: str = "agent_state",
) -> SQLiteQueryResult:
    """Query agent state history with pagination.

    Args:
        db_path: Path to the SQLite database file
        agent_id: Unique identifier for the agent
        conversation_id: Optional conversation identifier
        limit: Maximum number of records to return
        offset: Number of records to skip
        table_name: Name of the state table

    Returns:
        SQLiteQueryResult with historical state data
    """
    conditions = ["agent_id = ?"]
    parameters: list[Any] = [agent_id]

    if conversation_id is not None:
        conditions.append("conversation_id = ?")
        parameters.append(conversation_id)

    query = f"""
    SELECT * FROM {table_name}
    WHERE {' AND '.join(conditions)}
    ORDER BY updated_at DESC
    LIMIT ? OFFSET ?
    """

    parameters.extend([limit, offset])

    return await execute_sqlite_query(db_path, query, tuple(parameters))


async def cleanup_old_state(db_path: str, days_to_keep: int = 30, table_name: str = "agent_state") -> SQLiteQueryResult:
    """Clean up old agent state records.

    Args:
        db_path: Path to the SQLite database file
        days_to_keep: Number of days of history to keep
        table_name: Name of the state table

    Returns:
        SQLiteQueryResult indicating success or failure
    """
    query = f"""
    DELETE FROM {table_name}
    WHERE updated_at < datetime('now', '-{days_to_keep} days')
    """

    return await execute_sqlite_query(db_path, query, commit=True)
