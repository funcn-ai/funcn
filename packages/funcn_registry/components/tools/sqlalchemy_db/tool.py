"""SQLAlchemy Database Tool for advanced ORM-based agent state storage."""

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    and_,
    create_engine,
    delete,
    func,
    or_,
    select,
    text,
    update,
)
from sqlalchemy.dialects import mysql, postgresql, sqlite
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from typing import Any, Optional, Union

# Base model for SQLAlchemy
Base: DeclarativeMeta = declarative_base()


class AgentState(Base):
    """SQLAlchemy model for agent state storage."""

    __tablename__ = 'agent_state'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(255), nullable=False, index=True)
    conversation_id = Column(String(255), index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=False)
    data_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    metadata = Column(Text)

    __table_args__ = (
        UniqueConstraint('agent_id', 'conversation_id', 'key', name='uq_agent_conv_key'),
        Index('idx_agent_updated', 'agent_id', 'updated_at'),
    )


class SQLAlchemyConfig(BaseModel):
    """Configuration for SQLAlchemy connection."""

    database_url: str = Field(..., description="Database connection URL")
    echo: bool = Field(False, description="Echo SQL statements")
    pool_size: int = Field(5, description="Connection pool size")
    max_overflow: int = Field(10, description="Maximum overflow connections")
    pool_timeout: int = Field(30, description="Pool timeout in seconds")
    pool_recycle: int = Field(3600, description="Recycle connections after N seconds")
    use_async: bool = Field(True, description="Use async engine")

    @validator('database_url')
    def validate_url(cls, v):
        if not any(
            v.startswith(prefix)
            for prefix in [
                'sqlite://',
                'postgresql://',
                'mysql://',
                'sqlite+aiosqlite://',
                'postgresql+asyncpg://',
                'mysql+aiomysql://',
            ]
        ):
            raise ValueError("Unsupported database URL format")
        return v


class SQLAlchemyQueryResult(BaseModel):
    """Result of a SQLAlchemy operation."""

    success: bool = Field(..., description="Whether the operation was successful")
    operation: str = Field(..., description="Operation performed")
    rows_affected: int = Field(0, description="Number of rows affected")
    results: list[dict[str, Any]] = Field(default_factory=list, description="Query results")
    error: str | None = Field(None, description="Error message if operation failed")
    execution_time: float = Field(..., description="Operation execution time in seconds")


class DatabaseInfo(BaseModel):
    """Information about the database."""

    database_url: str = Field(..., description="Database connection URL")
    dialect: str = Field(..., description="Database dialect")
    tables: list[str] = Field(..., description="List of tables")
    agent_state_count: int = Field(..., description="Number of agent state records")
    database_size: str | None = Field(None, description="Database size (if available)")


# Global engine cache
_engine_cache: dict[str, Engine | Any] = {}
_async_session_cache: dict[str, async_sessionmaker] = {}


@asynccontextmanager
async def get_async_session(config: SQLAlchemyConfig) -> AsyncIterator[AsyncSession]:
    """Get an async database session."""
    if config.database_url not in _engine_cache:
        # Convert sync URL to async URL if needed
        async_url = config.database_url
        if async_url.startswith('sqlite://'):
            async_url = async_url.replace('sqlite://', 'sqlite+aiosqlite://')
        elif async_url.startswith('postgresql://'):
            async_url = async_url.replace('postgresql://', 'postgresql+asyncpg://')
        elif async_url.startswith('mysql://'):
            async_url = async_url.replace('mysql://', 'mysql+aiomysql://')

        engine = create_async_engine(
            async_url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle,
            poolclass=NullPool if 'sqlite' in async_url else QueuePool,
        )
        _engine_cache[config.database_url] = engine
        _async_session_cache[config.database_url] = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with _async_session_cache[config.database_url]() as session:
        yield session


def get_sync_engine(config: SQLAlchemyConfig) -> Engine:
    """Get a synchronous database engine."""
    if f"{config.database_url}_sync" not in _engine_cache:
        engine = create_engine(
            config.database_url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_timeout=config.pool_timeout,
            pool_recycle=config.pool_recycle,
            poolclass=NullPool if 'sqlite' in config.database_url else QueuePool,
        )
        _engine_cache[f"{config.database_url}_sync"] = engine

    return _engine_cache[f"{config.database_url}_sync"]


async def create_tables(config: SQLAlchemyConfig) -> SQLAlchemyQueryResult:
    """Create all tables defined in the models.

    Args:
        config: SQLAlchemy configuration

    Returns:
        SQLAlchemyQueryResult indicating success or failure
    """
    start_time = asyncio.get_event_loop().time()

    try:
        if config.use_async:
            # For async, we need to run create_all in sync mode
            engine = get_sync_engine(config)
            await asyncio.get_event_loop().run_in_executor(None, Base.metadata.create_all, engine)
        else:
            engine = get_sync_engine(config)
            Base.metadata.create_all(engine)

        execution_time = asyncio.get_event_loop().time() - start_time

        return SQLAlchemyQueryResult(
            success=True, operation="create_tables", rows_affected=0, error=None, execution_time=execution_time
        )

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return SQLAlchemyQueryResult(
            success=False, operation="create_tables", rows_affected=0, error=str(e), execution_time=execution_time
        )


async def store_agent_state(
    config: SQLAlchemyConfig,
    agent_id: str,
    key: str,
    value: Any,
    conversation_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> SQLAlchemyQueryResult:
    """Store or update agent state using SQLAlchemy.

    Args:
        config: SQLAlchemy configuration
        agent_id: Unique identifier for the agent
        key: State key
        value: State value (will be JSON serialized)
        conversation_id: Optional conversation identifier
        metadata: Optional metadata dictionary

    Returns:
        SQLAlchemyQueryResult indicating success or failure
    """
    start_time = asyncio.get_event_loop().time()

    try:
        # Serialize value and metadata
        value_json = json.dumps(value) if not isinstance(value, str) else value
        metadata_json = json.dumps(metadata) if metadata else None
        data_type = type(value).__name__

        async with get_async_session(config) as session:
            # Check if record exists
            stmt = select(AgentState).where(
                and_(AgentState.agent_id == agent_id, AgentState.conversation_id == conversation_id, AgentState.key == key)
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                existing.value = value_json
                existing.data_type = data_type
                existing.metadata = metadata_json
                existing.updated_at = datetime.utcnow()
                rows_affected = 1
            else:
                # Create new record
                new_state = AgentState(
                    agent_id=agent_id,
                    conversation_id=conversation_id,
                    key=key,
                    value=value_json,
                    data_type=data_type,
                    metadata=metadata_json,
                )
                session.add(new_state)
                rows_affected = 1

            await session.commit()

            execution_time = asyncio.get_event_loop().time() - start_time

            return SQLAlchemyQueryResult(
                success=True,
                operation="store_agent_state",
                rows_affected=rows_affected,
                error=None,
                execution_time=execution_time,
            )

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return SQLAlchemyQueryResult(
            success=False, operation="store_agent_state", rows_affected=0, error=str(e), execution_time=execution_time
        )


async def get_agent_state(
    config: SQLAlchemyConfig, agent_id: str, key: str | None = None, conversation_id: str | None = None, limit: int = 100
) -> SQLAlchemyQueryResult:
    """Retrieve agent state using SQLAlchemy.

    Args:
        config: SQLAlchemy configuration
        agent_id: Unique identifier for the agent
        key: Optional specific key to retrieve
        conversation_id: Optional conversation identifier
        limit: Maximum number of records to return

    Returns:
        SQLAlchemyQueryResult with the state data
    """
    start_time = asyncio.get_event_loop().time()

    try:
        async with get_async_session(config) as session:
            # Build query
            stmt = select(AgentState).where(AgentState.agent_id == agent_id)

            if conversation_id is not None:
                stmt = stmt.where(AgentState.conversation_id == conversation_id)
            else:
                stmt = stmt.where(AgentState.conversation_id.is_(None))

            if key is not None:
                stmt = stmt.where(AgentState.key == key)

            stmt = stmt.order_by(AgentState.updated_at.desc()).limit(limit)

            result = await session.execute(stmt)
            records = result.scalars().all()

            # Convert to dictionaries and deserialize
            results = []
            for record in records:
                data = {
                    'id': record.id,
                    'agent_id': record.agent_id,
                    'conversation_id': record.conversation_id,
                    'key': record.key,
                    'value': record.value,
                    'data_type': record.data_type,
                    'created_at': record.created_at.isoformat(),
                    'updated_at': record.updated_at.isoformat(),
                    'metadata': record.metadata,
                }

                # Deserialize JSON values
                try:
                    if record.data_type != 'str':
                        data['value'] = json.loads(record.value)
                    if record.metadata:
                        data['metadata'] = json.loads(record.metadata)
                except json.JSONDecodeError:
                    pass

                results.append(data)

            execution_time = asyncio.get_event_loop().time() - start_time

            return SQLAlchemyQueryResult(
                success=True,
                operation="get_agent_state",
                results=results,
                rows_affected=len(results),
                error=None,
                execution_time=execution_time,
            )

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return SQLAlchemyQueryResult(
            success=False, operation="get_agent_state", rows_affected=0, error=str(e), execution_time=execution_time
        )


async def delete_agent_state(
    config: SQLAlchemyConfig, agent_id: str, key: str | None = None, conversation_id: str | None = None
) -> SQLAlchemyQueryResult:
    """Delete agent state using SQLAlchemy.

    Args:
        config: SQLAlchemy configuration
        agent_id: Unique identifier for the agent
        key: Optional specific key to delete
        conversation_id: Optional conversation identifier

    Returns:
        SQLAlchemyQueryResult indicating success or failure
    """
    start_time = asyncio.get_event_loop().time()

    try:
        async with get_async_session(config) as session:
            # Build delete statement
            stmt = delete(AgentState).where(AgentState.agent_id == agent_id)

            if conversation_id is not None:
                stmt = stmt.where(AgentState.conversation_id == conversation_id)

            if key is not None:
                stmt = stmt.where(AgentState.key == key)

            result = await session.execute(stmt)
            await session.commit()

            execution_time = asyncio.get_event_loop().time() - start_time

            return SQLAlchemyQueryResult(
                success=True,
                operation="delete_agent_state",
                rows_affected=result.rowcount,
                error=None,
                execution_time=execution_time,
            )

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return SQLAlchemyQueryResult(
            success=False, operation="delete_agent_state", rows_affected=0, error=str(e), execution_time=execution_time
        )


async def query_agent_history(
    config: SQLAlchemyConfig,
    agent_id: str,
    conversation_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> SQLAlchemyQueryResult:
    """Query agent state history with advanced filtering.

    Args:
        config: SQLAlchemy configuration
        agent_id: Unique identifier for the agent
        conversation_id: Optional conversation identifier
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        SQLAlchemyQueryResult with historical state data
    """
    start_time = asyncio.get_event_loop().time()

    try:
        async with get_async_session(config) as session:
            # Build query
            stmt = select(AgentState).where(AgentState.agent_id == agent_id)

            if conversation_id is not None:
                stmt = stmt.where(AgentState.conversation_id == conversation_id)

            if start_date:
                stmt = stmt.where(AgentState.updated_at >= start_date)

            if end_date:
                stmt = stmt.where(AgentState.updated_at <= end_date)

            stmt = stmt.order_by(AgentState.updated_at.desc()).limit(limit).offset(offset)

            result = await session.execute(stmt)
            records = result.scalars().all()

            # Convert to dictionaries
            results = []
            for record in records:
                data = {
                    'id': record.id,
                    'agent_id': record.agent_id,
                    'conversation_id': record.conversation_id,
                    'key': record.key,
                    'value': record.value,
                    'data_type': record.data_type,
                    'created_at': record.created_at.isoformat(),
                    'updated_at': record.updated_at.isoformat(),
                    'metadata': record.metadata,
                }

                # Deserialize JSON values
                try:
                    if record.data_type != 'str':
                        data['value'] = json.loads(record.value)
                    if record.metadata:
                        data['metadata'] = json.loads(record.metadata)
                except json.JSONDecodeError:
                    pass

                results.append(data)

            execution_time = asyncio.get_event_loop().time() - start_time

            return SQLAlchemyQueryResult(
                success=True,
                operation="query_agent_history",
                results=results,
                rows_affected=len(results),
                error=None,
                execution_time=execution_time,
            )

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return SQLAlchemyQueryResult(
            success=False, operation="query_agent_history", rows_affected=0, error=str(e), execution_time=execution_time
        )


async def get_database_info(config: SQLAlchemyConfig) -> DatabaseInfo:
    """Get information about the database.

    Args:
        config: SQLAlchemy configuration

    Returns:
        DatabaseInfo with database details
    """
    try:
        async with get_async_session(config) as session:
            # Get dialect
            dialect = session.bind.dialect.name

            # Get tables
            if dialect == 'sqlite':
                result = await session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                )
            elif dialect == 'postgresql':
                result = await session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            elif dialect == 'mysql':
                result = await session.execute(text("SHOW TABLES"))
            else:
                result = None

            tables = [row[0] for row in result] if result else []

            # Get agent state count
            count_result = await session.execute(select(func.count()).select_from(AgentState))
            agent_state_count = count_result.scalar() or 0

            # Get database size (dialect-specific)
            database_size = None
            if dialect == 'postgresql':
                size_result = await session.execute(text("SELECT pg_database_size(current_database())"))
                size_bytes = size_result.scalar()
                if size_bytes:
                    database_size = f"{size_bytes / 1024 / 1024:.2f} MB"

            return DatabaseInfo(
                database_url=config.database_url,
                dialect=dialect,
                tables=tables,
                agent_state_count=agent_state_count,
                database_size=database_size,
            )

    except Exception as e:
        raise RuntimeError(f"Failed to get database info: {str(e)}") from e


async def cleanup_old_state(config: SQLAlchemyConfig, days_to_keep: int = 30) -> SQLAlchemyQueryResult:
    """Clean up old agent state records.

    Args:
        config: SQLAlchemy configuration
        days_to_keep: Number of days of history to keep

    Returns:
        SQLAlchemyQueryResult indicating success or failure
    """
    start_time = asyncio.get_event_loop().time()

    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        async with get_async_session(config) as session:
            stmt = delete(AgentState).where(AgentState.updated_at < cutoff_date)
            result = await session.execute(stmt)
            await session.commit()

            execution_time = asyncio.get_event_loop().time() - start_time

            return SQLAlchemyQueryResult(
                success=True,
                operation="cleanup_old_state",
                rows_affected=result.rowcount,
                error=None,
                execution_time=execution_time,
            )

    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return SQLAlchemyQueryResult(
            success=False, operation="cleanup_old_state", rows_affected=0, error=str(e), execution_time=execution_time
        )


# Import timedelta for cleanup function
from datetime import timedelta
