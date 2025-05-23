"""PostgreSQL Search Tool for database queries and data retrieval."""

import asyncio
import asyncpg
import json
from asyncpg.pool import Pool
from datetime import datetime
from pydantic import BaseModel, Field, SecretStr
from typing import Any, Literal, Optional, Union


class QueryResult(BaseModel):
    """Represents a single query result row."""

    columns: list[str] = Field(..., description="Column names")
    values: list[Any] = Field(..., description="Row values")
    row_data: dict[str, Any] = Field(..., description="Row data as dictionary")

    @classmethod
    def from_record(cls, record: asyncpg.Record) -> "QueryResult":
        """Create QueryResult from asyncpg Record."""
        columns = list(record.keys())
        values = list(record.values())
        row_data = dict(record)
        return cls(columns=columns, values=values, row_data=row_data)


class PGSearchResult(BaseModel):
    """Result of PostgreSQL search operation."""

    success: bool = Field(..., description="Whether the query was successful")
    query: str = Field(..., description="The SQL query executed")
    total_rows: int = Field(..., description="Total number of rows returned")
    results: list[QueryResult] = Field(default_factory=list, description="Query results")
    execution_time: float = Field(..., description="Query execution time in seconds")
    error: str | None = Field(None, description="Error message if query failed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional query metadata")


def validate_connection_string(connection_string: str) -> str:
    """Validate the connection string format."""
    if not connection_string.startswith(('postgresql://', 'postgres://')):
        raise ValueError("Connection string must start with postgresql:// or postgres://")
    return connection_string


async def create_pool(connection_string: str, pool_size: int = 10, query_timeout: int = 30) -> Pool:
    """Create a connection pool."""
    return await asyncpg.create_pool(
        connection_string,
        min_size=1,
        max_size=pool_size,
        command_timeout=query_timeout
    )


def build_search_query(
    table_name: str | None,
    columns: list[str] | None,
    search_text: str | None,
    search_columns: list[str] | None,
    where_conditions: dict[str, Any] | None,
    use_full_text_search: bool,
    order_by: str | None,
    limit: int,
    offset: int
) -> tuple[str, list[Any]]:
    """Build SQL query based on search parameters."""
    if not table_name:
        raise ValueError("table_name must be provided")

    # Build SELECT clause
    select_clause = "*"
    if columns:
        select_clause = ", ".join(f'"{col}"' for col in columns)

    query_parts = [f'SELECT {select_clause} FROM "{table_name}"']
    params: list[Any] = []

    # Build WHERE clause
    where_clauses = []

    # Add text search conditions
    if search_text:
        if use_full_text_search and search_columns:
            # PostgreSQL full-text search
            search_vector = " || ' ' || ".join(f'COALESCE("{col}"::text, \'\')' for col in search_columns)
            where_clauses.append(f"to_tsvector('english', {search_vector}) @@ plainto_tsquery('english', ${len(params) + 1})")
            params.append(search_text)
        elif search_columns:
            # Simple ILIKE search
            search_conditions = []
            for col in search_columns:
                search_conditions.append(f'"{col}"::text ILIKE ${len(params) + 1}')
            where_clauses.append(f"({' OR '.join(search_conditions)})")
            params.append(f"%{search_text}%")

    # Add custom WHERE conditions
    if where_conditions:
        for col, value in where_conditions.items():
            if value is None:
                where_clauses.append(f'"{col}" IS NULL')
            elif isinstance(value, list):
                placeholders = [f'${len(params) + i + 1}' for i in range(len(value))]
                where_clauses.append(f'"{col}" IN ({", ".join(placeholders)})')
                params.extend(value)
            else:
                where_clauses.append(f'"{col}" = ${len(params) + 1}')
                params.append(value)

    if where_clauses:
        query_parts.append(f"WHERE {' AND '.join(where_clauses)}")

    # Add ORDER BY
    if order_by:
        query_parts.append(f"ORDER BY {order_by}")

    # Add LIMIT and OFFSET
    query_parts.append(f"LIMIT {limit}")
    if offset > 0:
        query_parts.append(f"OFFSET {offset}")

    return " ".join(query_parts), params


async def get_table_schema(conn: asyncpg.Connection, table_name: str) -> dict[str, Any]:
    """Get schema information for a table."""
    schema_query = """
    SELECT
        column_name,
        data_type,
        is_nullable,
        column_default,
        character_maximum_length
    FROM information_schema.columns
    WHERE table_name = $1
    ORDER BY ordinal_position
    """

    columns = await conn.fetch(schema_query, table_name)

    return {
        "columns": [
            {
                "name": col["column_name"],
                "type": col["data_type"],
                "nullable": col["is_nullable"] == "YES",
                "default": col["column_default"],
                "max_length": col["character_maximum_length"]
            }
            for col in columns
        ]
    }


async def execute_postgres_query(
    connection_string: str | SecretStr,
    query: str | None = None,
    search_text: str | None = None,
    table_name: str | None = None,
    columns: list[str] | None = None,
    where_conditions: dict[str, Any] | None = None,
    order_by: str | None = None,
    limit: int = 100,
    offset: int = 0,
    use_full_text_search: bool = False,
    search_columns: list[str] | None = None,
    query_timeout: int = 30,
    return_schema: bool = False,
    pool_size: int = 10
) -> PGSearchResult:
    """Execute a PostgreSQL query or search operation.

    Args:
        connection_string: PostgreSQL connection string
        query: SQL query to execute (if provided, other search params are ignored)
        search_text: Text to search for (full-text search)
        table_name: Table to search in
        columns: Columns to return (default: all)
        where_conditions: WHERE clause conditions
        order_by: ORDER BY clause
        limit: Maximum number of rows to return
        offset: Number of rows to skip
        use_full_text_search: Use PostgreSQL full-text search
        search_columns: Columns to search in (for text search)
        query_timeout: Query timeout in seconds
        return_schema: Return table schema information
        pool_size: Connection pool size

    Returns:
        PGSearchResult with query results
    """
    start_time = asyncio.get_event_loop().time()

    # Extract connection string value if SecretStr
    conn_str = connection_string.get_secret_value() if isinstance(connection_string, SecretStr) else connection_string

    try:
        # Validate connection string
        conn_str = validate_connection_string(conn_str)

        # Create connection pool
        pool = await create_pool(conn_str, pool_size, query_timeout)

        try:
            async with pool.acquire() as conn:
                # Prepare query and parameters
                if query:
                    sql_query = query
                    params: list[Any] = []
                else:
                    sql_query, params = build_search_query(
                        table_name, columns, search_text, search_columns,
                        where_conditions, use_full_text_search, order_by, limit, offset
                    )

                # Execute query
                if params:
                    rows = await conn.fetch(sql_query, *params)
                else:
                    rows = await conn.fetch(sql_query)

                # Convert results
                results = [QueryResult.from_record(row) for row in rows]

                # Get schema information if requested
                metadata = {}
                if return_schema and table_name:
                    metadata["schema"] = await get_table_schema(conn, table_name)

                execution_time = asyncio.get_event_loop().time() - start_time

                return PGSearchResult(
                    success=True,
                    query=sql_query,
                    total_rows=len(results),
                    results=results,
                    execution_time=execution_time,
                    metadata=metadata,
                    error=None
                )

        finally:
            await pool.close()

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return PGSearchResult(
            success=False,
            query=query or "",
            total_rows=0,
            execution_time=execution_time,
            error=str(e)
        )


# Convenience functions
async def query_postgres(
    connection_string: str,
    query: str,
    limit: int = 100
) -> PGSearchResult:
    """Execute a PostgreSQL query.

    Args:
        connection_string: PostgreSQL connection string
        query: SQL query to execute
        limit: Maximum rows to return

    Returns:
        PGSearchResult with query results
    """
    return await execute_postgres_query(
        connection_string=connection_string,
        query=query,
        limit=limit
    )


async def search_table(
    connection_string: str,
    table_name: str,
    search_text: str,
    search_columns: list[str],
    limit: int = 50
) -> PGSearchResult:
    """Search for text in specific table columns.

    Args:
        connection_string: PostgreSQL connection string
        table_name: Table to search in
        search_text: Text to search for
        search_columns: Columns to search in
        limit: Maximum rows to return

    Returns:
        PGSearchResult with matching rows
    """
    return await execute_postgres_query(
        connection_string=connection_string,
        table_name=table_name,
        search_text=search_text,
        search_columns=search_columns,
        limit=limit
    )


async def full_text_search(
    connection_string: str,
    table_name: str,
    search_text: str,
    search_columns: list[str],
    limit: int = 50
) -> PGSearchResult:
    """Perform PostgreSQL full-text search.

    Args:
        connection_string: PostgreSQL connection string
        table_name: Table to search in
        search_text: Text to search for
        search_columns: Columns to search in
        limit: Maximum rows to return

    Returns:
        PGSearchResult with matching rows
    """
    return await execute_postgres_query(
        connection_string=connection_string,
        table_name=table_name,
        search_text=search_text,
        search_columns=search_columns,
        use_full_text_search=True,
        limit=limit
    )


async def get_table_data(
    connection_string: str,
    table_name: str,
    where_conditions: dict[str, Any] | None = None,
    columns: list[str] | None = None,
    order_by: str | None = None,
    limit: int = 100
) -> PGSearchResult:
    """Get data from a PostgreSQL table with filtering.

    Args:
        connection_string: PostgreSQL connection string
        table_name: Table to query
        where_conditions: WHERE clause conditions
        columns: Columns to return
        order_by: ORDER BY clause
        limit: Maximum rows to return

    Returns:
        PGSearchResult with table data
    """
    return await execute_postgres_query(
        connection_string=connection_string,
        table_name=table_name,
        where_conditions=where_conditions,
        columns=columns,
        order_by=order_by,
        limit=limit,
        return_schema=True
    )
