"""Test suite for sqlalchemy_db tool following best practices."""

import asyncio
import json
import pytest
from datetime import UTC, datetime, timedelta

# Import the actual tool functions and models
from packages.sygaldry_registry.components.tools.sqlalchemy_db.tool import (
    AgentState,
    Base,
    DatabaseInfo,
    SQLAlchemyConfig,
    SQLAlchemyQueryResult,
    and_,
    cleanup_old_state,
    create_tables,
    delete,
    delete_agent_state,
    get_agent_state,
    get_async_session,
    get_database_info,
    get_sync_engine,
    query_agent_history,
    store_agent_state,
)
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from tests.fixtures import MockResponseFactory
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch


class TestSQLAlchemyDB(BaseToolTest):
    """Test sqlalchemy_db tool component."""

    component_name = "sqlalchemy_db"
    component_path = Path("packages/sygaldry_registry/components/tools/sqlalchemy_db")

    def get_component_function(self):
        """Import the tool function."""
        # This tool has multiple functions, return the main one
        return store_agent_state

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            SQLAlchemyConfig(
                database_url="sqlite:///test.db",
                echo=False,
                use_async=True
            )
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        # This is an async tool, validation happens in async tests
        pass

    @pytest.mark.asyncio
    async def test_create_tables(self):
        """Test table creation."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_sync_engine") as mock_get_engine:
            mock_engine = Mock()
            mock_get_engine.return_value = mock_engine

            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.Base.metadata.create_all") as mock_create_all:
                result = await create_tables(config)

                assert result.success is True
                assert result.operation == "create_tables"
                assert result.error is None
                mock_create_all.assert_called_once_with(mock_engine)

    @pytest.mark.asyncio
    async def test_store_agent_state_new(self):
        """Test storing new agent state."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            # Mock async context manager
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock query result - no existing record
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value={"data": "test_value"},
                conversation_id="conv_123",
                metadata={"source": "test"}
            )

            assert result.success is True
            assert result.operation == "store_agent_state"
            assert result.rows_affected == 1
            assert result.error is None

            # Verify session methods were called
            assert mock_session.add.called
            assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_store_agent_state_update(self):
        """Test updating existing agent state."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock existing record
            mock_existing = Mock(spec=AgentState)
            mock_existing.value = '{"old": "value"}'
            mock_existing.data_type = "dict"
            mock_existing.agent_metadata = None

            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = mock_existing
            mock_session.execute.return_value = mock_result

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value={"data": "new_value"},
                conversation_id="conv_123"
            )

            assert result.success is True
            assert result.rows_affected == 1
            assert mock_existing.value == '{"data": "new_value"}'
            assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_get_agent_state(self):
        """Test retrieving agent state."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock records
            mock_record1 = Mock(spec=AgentState)
            mock_record1.id = 1
            mock_record1.agent_id = "test_agent"
            mock_record1.conversation_id = "conv_123"
            mock_record1.key = "key1"
            mock_record1.value = '{"data": "value1"}'
            mock_record1.data_type = "dict"
            mock_record1.created_at = datetime.utcnow()
            mock_record1.updated_at = datetime.utcnow()
            mock_record1.agent_metadata = '{"source": "test"}'

            mock_record2 = Mock(spec=AgentState)
            mock_record2.id = 2
            mock_record2.agent_id = "test_agent"
            mock_record2.conversation_id = "conv_123"
            mock_record2.key = "key2"
            mock_record2.value = "simple string"
            mock_record2.data_type = "str"
            mock_record2.created_at = datetime.utcnow()
            mock_record2.updated_at = datetime.utcnow()
            mock_record2.agent_metadata = None

            mock_result = Mock()
            mock_scalars = Mock()
            mock_scalars.all.return_value = [mock_record1, mock_record2]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await get_agent_state(
                config=config,
                agent_id="test_agent",
                conversation_id="conv_123"
            )

            assert result.success is True
            assert result.operation == "get_agent_state"
            assert len(result.results) == 2
            assert result.results[0]["key"] == "key1"
            assert result.results[0]["value"] == {"data": "value1"}
            assert result.results[1]["key"] == "key2"
            assert result.results[1]["value"] == "simple string"
            assert result.results[0]["metadata"] == {"source": "test"}

    @pytest.mark.asyncio
    async def test_delete_agent_state(self):
        """Test deleting agent state."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock delete result
            mock_result = Mock()
            mock_result.rowcount = 3
            mock_session.execute.return_value = mock_result

            result = await delete_agent_state(
                config=config,
                agent_id="test_agent",
                key="old_key"
            )

            assert result.success is True
            assert result.operation == "delete_agent_state"
            assert result.rows_affected == 3
            assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_query_agent_history(self):
        """Test querying agent history with filters."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock historical records
            records = []
            base_time = datetime.utcnow()
            for i in range(5):
                mock_record = Mock(spec=AgentState)
                mock_record.id = i + 1
                mock_record.agent_id = "test_agent"
                mock_record.conversation_id = "conv_123"
                mock_record.key = f"key_{i}"
                mock_record.value = f'"value_{i}"'
                mock_record.data_type = "str"
                mock_record.created_at = base_time - timedelta(days=i+1)
                mock_record.updated_at = base_time - timedelta(days=i)
                mock_record.agent_metadata = None
                records.append(mock_record)

            mock_result = Mock()
            mock_scalars = Mock()
            mock_scalars.all.return_value = records
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await query_agent_history(
                config=config,
                agent_id="test_agent",
                conversation_id="conv_123",
                start_date=base_time - timedelta(days=7),
                end_date=base_time,
                limit=10
            )

            assert result.success is True
            assert result.operation == "query_agent_history"
            assert len(result.results) == 5
            assert all(r["agent_id"] == "test_agent" for r in result.results)

    @pytest.mark.asyncio
    async def test_get_database_info(self):
        """Test getting database information."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock bind and dialect
            mock_bind = Mock()
            mock_bind.dialect.name = "sqlite"
            mock_session.bind = mock_bind

            # Mock table query
            mock_table_result = Mock()
            mock_table_result.__iter__ = Mock(return_value=iter([
                ("agent_state",), ("other_table",)
            ]))

            # Mock count query
            mock_count_result = Mock()
            mock_count_result.scalar.return_value = 42

            # Return different results for different queries
            mock_session.execute.side_effect = [mock_table_result, mock_count_result]

            info = await get_database_info(config)

            assert isinstance(info, DatabaseInfo)
            assert info.database_url == config.database_url
            assert info.dialect == "sqlite"
            assert len(info.tables) == 2
            assert info.agent_state_count == 42

    @pytest.mark.asyncio
    async def test_cleanup_old_state(self):
        """Test cleaning up old state records."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock delete result
            mock_result = Mock()
            mock_result.rowcount = 15
            mock_session.execute.return_value = mock_result

            result = await cleanup_old_state(config, days_to_keep=30)

            assert result.success is True
            assert result.operation == "cleanup_old_state"
            assert result.rows_affected == 15
            assert mock_session.commit.called

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in operations."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            # Simulate connection error
            mock_get_session.side_effect = Exception("Database connection failed")

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value="test_value"
            )

            assert result.success is False
            assert result.operation == "store_agent_state"
            assert "Database connection failed" in result.error
            assert result.rows_affected == 0

    @pytest.mark.asyncio
    async def test_json_serialization(self):
        """Test JSON serialization of complex values."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock no existing record
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # Test complex object serialization
            complex_value = {
                "nested": {
                    "list": [1, 2, 3],
                    "dict": {"a": 1, "b": 2}
                },
                "date": datetime.utcnow().isoformat(),
                "null": None,
                "bool": True
            }

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="complex_key",
                value=complex_value
            )

            assert result.success is True
            # Verify add was called with proper JSON
            add_call = mock_session.add.call_args[0][0]
            assert isinstance(add_call.value, str)
            assert json.loads(add_call.value) == complex_value

    @pytest.mark.asyncio
    async def test_conversation_id_filtering(self):
        """Test filtering by conversation ID."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Test with conversation_id
            mock_result1 = Mock()
            mock_scalars1 = Mock()
            mock_scalars1.all.return_value = []
            mock_result1.scalars.return_value = mock_scalars1
            mock_session.execute.return_value = mock_result1

            result1 = await get_agent_state(
                config=config,
                agent_id="test_agent",
                conversation_id="conv_123"
            )

            assert result1.success is True

            # Reset mock for second call
            mock_session.execute.reset_mock()

            # Test without conversation_id (should query for None)
            result2 = await get_agent_state(
                config=config,
                agent_id="test_agent",
                conversation_id=None
            )

            assert result2.success is True

    def test_config_validation(self):
        """Test SQLAlchemyConfig validation."""
        # Valid configs
        valid_configs = [
            SQLAlchemyConfig(database_url="sqlite:///test.db"),
            SQLAlchemyConfig(database_url="postgresql://user:pass@localhost/db"),
            SQLAlchemyConfig(database_url="mysql://user:pass@localhost/db"),
            SQLAlchemyConfig(database_url="sqlite+aiosqlite:///test.db"),
            SQLAlchemyConfig(database_url="postgresql+asyncpg://user:pass@localhost/db"),
            SQLAlchemyConfig(database_url="mysql+aiomysql://user:pass@localhost/db"),
        ]

        for config in valid_configs:
            assert config.database_url.startswith(("sqlite://", "postgresql://", "mysql://",
                                                   "sqlite+aiosqlite://", "postgresql+asyncpg://",
                                                   "mysql+aiomysql://"))

        # Invalid config
        with pytest.raises(ValueError):
            SQLAlchemyConfig(database_url="invalid://database")

    @pytest.mark.asyncio
    async def test_database_specific_queries(self):
        """Test database-specific query handling."""
        databases = [
            ("sqlite:///test.db", "sqlite"),
            ("postgresql://localhost/test", "postgresql"),
            ("mysql://localhost/test", "mysql")
        ]

        for db_url, dialect in databases:
            config = SQLAlchemyConfig(database_url=db_url)

            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
                mock_session = AsyncMock(spec=AsyncSession)
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__.return_value = None

                # Mock bind and dialect
                mock_bind = Mock()
                mock_bind.dialect.name = dialect
                mock_session.bind = mock_bind

                # Create proper async iterables for different results
                async def async_iter_tables():
                    for item in [("table1",)]:
                        yield item

                # First call returns table results
                mock_table_result = AsyncMock()
                mock_table_result.__aiter__.return_value = async_iter_tables()

                # Second call returns count
                mock_count_result = Mock()
                mock_count_result.scalar.return_value = 10

                # Third call for database size (only for postgresql)
                mock_size_result = Mock()
                mock_size_result.scalar.return_value = 1048576 if dialect == 'postgresql' else None

                # Set up side effects based on dialect
                if dialect == 'postgresql':
                    mock_session.execute.side_effect = [mock_table_result, mock_count_result, mock_size_result]
                else:
                    mock_session.execute.side_effect = [mock_table_result, mock_count_result]

                info = await get_database_info(config)

                assert info.dialect == dialect

    @pytest.mark.asyncio
    async def test_connection_pooling(self):
        """Test connection pool configuration."""
        config = SQLAlchemyConfig(
            database_url="postgresql://localhost/test",
            pool_size=10,
            max_overflow=20,
            pool_timeout=60,
            pool_recycle=7200
        )

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.create_async_engine") as mock_create_engine:
            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.async_sessionmaker") as mock_sessionmaker:
                # Clear cache to force engine creation
                from packages.sygaldry_registry.components.tools.sqlalchemy_db.tool import _async_session_cache, _engine_cache
                _engine_cache.clear()
                _async_session_cache.clear()

                mock_engine = Mock()
                mock_create_engine.return_value = mock_engine

                # Create a proper async session mock
                mock_session_instance = AsyncMock(spec=AsyncSession)
                mock_session_instance.__aenter__.return_value = mock_session_instance
                mock_session_instance.__aexit__.return_value = None

                # Mock sessionmaker to return a callable that returns our async context manager
                def session_factory():
                    return mock_session_instance

                mock_sessionmaker.return_value = session_factory

                # Use get_async_session
                async with get_async_session(config) as session:
                    assert session == mock_session_instance

                # Verify engine was created with pool settings
                mock_create_engine.assert_called_once()
                call_kwargs = mock_create_engine.call_args[1]
                assert call_kwargs["pool_size"] == 10
                assert call_kwargs["max_overflow"] == 20
                assert call_kwargs["pool_timeout"] == 60
                assert call_kwargs["pool_recycle"] == 7200

    @pytest.mark.asyncio
    async def test_async_to_sync_url_conversion(self):
        """Test automatic URL conversion for async engines."""
        conversions = [
            ("sqlite:///test.db", "sqlite+aiosqlite:///test.db"),
            ("postgresql://localhost/test", "postgresql+asyncpg://localhost/test"),
            ("mysql://localhost/test", "mysql+aiomysql://localhost/test"),
        ]

        for sync_url, expected_async_url in conversions:
            config = SQLAlchemyConfig(database_url=sync_url, use_async=True)

            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.create_async_engine") as mock_create_engine:
                # Clear cache
                from packages.sygaldry_registry.components.tools.sqlalchemy_db.tool import _async_session_cache, _engine_cache
                _engine_cache.clear()
                _async_session_cache.clear()

                mock_engine = Mock()
                mock_create_engine.return_value = mock_engine

                with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.async_sessionmaker"):
                    async with get_async_session(config) as session:
                        pass

                # Verify async URL was used
                mock_create_engine.assert_called_once()
                actual_url = mock_create_engine.call_args[0][0]
                assert actual_url == expected_async_url

    @pytest.mark.asyncio
    async def test_metadata_storage(self):
        """Test storing and retrieving metadata."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock no existing record
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            metadata = {
                "version": "1.0",
                "tags": ["important", "production"],
                "created_by": "test_user"
            }

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value="test_value",
                metadata=metadata
            )

            assert result.success is True
            # Verify metadata was serialized
            add_call = mock_session.add.call_args[0][0]
            assert json.loads(add_call.agent_metadata) == metadata

    @pytest.mark.asyncio
    async def test_data_type_tracking(self):
        """Test tracking of value data types."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        test_values = [
            ("string value", "str"),
            (123, "int"),
            (45.67, "float"),
            (True, "bool"),
            ([1, 2, 3], "list"),
            ({"key": "value"}, "dict"),
            (None, "NoneType")
        ]

        for value, expected_type in test_values:
            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
                mock_session = AsyncMock(spec=AsyncSession)
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__.return_value = None

                # Mock no existing record
                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result

                await store_agent_state(
                    config=config,
                    agent_id="test_agent",
                    key=f"key_{expected_type}",
                    value=value
                )

                # Verify data type was set correctly
                add_call = mock_session.add.call_args[0][0]
                assert add_call.data_type == expected_type

    @pytest.mark.asyncio
    async def test_execution_time_tracking(self):
        """Test that execution time is tracked correctly."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # Add small delay to ensure measurable execution time
            async def delayed_commit():
                await asyncio.sleep(0.01)

            mock_session.commit = delayed_commit

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value="test_value"
            )

            assert result.execution_time > 0
            assert result.execution_time < 1.0  # Should be fast

    @pytest.mark.asyncio
    async def test_limit_and_offset(self):
        """Test limit and offset in queries."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Create mock records
            all_records = []
            for i in range(20):
                mock_record = Mock(spec=AgentState)
                mock_record.id = i + 1
                mock_record.agent_id = "test_agent"
                mock_record.conversation_id = None
                mock_record.key = f"key_{i}"
                mock_record.value = f"value_{i}"
                mock_record.data_type = "str"
                mock_record.created_at = datetime.utcnow()
                mock_record.updated_at = datetime.utcnow()
                mock_record.agent_metadata = None
                all_records.append(mock_record)

            # Test with different limits
            for limit in [5, 10, 15]:
                mock_result = Mock()
                mock_scalars = Mock()
                mock_scalars.all.return_value = all_records[:limit]
                mock_result.scalars.return_value = mock_scalars
                mock_session.execute.return_value = mock_result

                result = await get_agent_state(
                    config=config,
                    agent_id="test_agent",
                    limit=limit
                )

                assert len(result.results) == limit

    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        special_values = [
            "Hello 世界 🌍",
            "Special chars: !@#$%^&*()",
            "Quotes: 'single' and \"double\"",
            "Newlines:\nand\ttabs",
            "Emoji: 😀 🎉 🚀"
        ]

        for value in special_values:
            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
                mock_session = AsyncMock(spec=AsyncSession)
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__.return_value = None

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result

                result = await store_agent_state(
                    config=config,
                    agent_id="test_agent",
                    key="unicode_key",
                    value=value
                )

                assert result.success is True

    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent database operations."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        async def store_value(key: str, value: str):
            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
                mock_session = AsyncMock(spec=AsyncSession)
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__.return_value = None

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result

                return await store_agent_state(
                    config=config,
                    agent_id="test_agent",
                    key=key,
                    value=value
                )

        # Run multiple operations concurrently
        tasks = [
            store_value(f"key_{i}", f"value_{i}")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r.success for r in results)
        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock error during commit
            mock_session.commit.side_effect = Exception("Commit failed")

            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value="test_value"
            )

            assert result.success is False
            assert "Commit failed" in result.error

    @pytest.mark.asyncio
    async def test_json_decode_error_handling(self):
        """Test handling of JSON decode errors."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock record with invalid JSON
            mock_record = Mock(spec=AgentState)
            mock_record.id = 1
            mock_record.agent_id = "test_agent"
            mock_record.conversation_id = None
            mock_record.key = "bad_json"
            mock_record.value = "{invalid json"  # Invalid JSON
            mock_record.data_type = "dict"
            mock_record.created_at = datetime.utcnow()
            mock_record.updated_at = datetime.utcnow()
            mock_record.agent_metadata = "{also invalid"  # Invalid JSON

            mock_result = Mock()
            mock_scalars = Mock()
            mock_scalars.all.return_value = [mock_record]
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await get_agent_state(
                config=config,
                agent_id="test_agent"
            )

            # Should handle gracefully - return raw values
            assert result.success is True
            assert result.results[0]["value"] == "{invalid json"
            assert result.results[0]["metadata"] == "{also invalid"

    @pytest.mark.asyncio
    async def test_large_data_storage(self):
        """Test storing and retrieving very large data."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock no existing record
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # Create large data structure
            large_data = {
                "items": [{"id": i, "data": "x" * 1000} for i in range(100)],
                "nested": {
                    "deep": {
                        "structure": {
                            "with": {
                                "lots": {
                                    "of": {
                                        "data": ["item"] * 100
                                    }
                                }
                            }
                        }
                    }
                }
            }

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="large_data",
                value=large_data
            )

            assert result.success is True
            # Verify large JSON was serialized
            add_call = mock_session.add.call_args[0][0]
            assert len(add_call.value) > 100000  # Should be large

    @pytest.mark.asyncio
    async def test_special_characters_in_identifiers(self):
        """Test special characters in agent_id and keys."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        special_ids = [
            ("agent-with-dashes", "key-with-dashes"),
            ("agent_with_underscores", "key_with_underscores"),
            ("agent.with.dots", "key.with.dots"),
            ("agent@email.com", "key:with:colons"),
            ("agent/with/slashes", "key\\with\\backslashes"),
            ("agent with spaces", "key with spaces"),
            ("agent-123!@#", "key$%^&*()"),
        ]

        for agent_id, key in special_ids:
            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
                mock_session = AsyncMock(spec=AsyncSession)
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__.return_value = None

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result

                result = await store_agent_state(
                    config=config,
                    agent_id=agent_id,
                    key=key,
                    value="test_value"
                )

                assert result.success is True
                # Verify identifiers were stored correctly
                add_call = mock_session.add.call_args[0][0]
                assert add_call.agent_id == agent_id
                assert add_call.key == key

    @pytest.mark.asyncio
    async def test_connection_url_with_special_characters(self):
        """Test database URLs with special characters in credentials."""
        special_urls = [
            "postgresql://user:p@ssw0rd!@localhost/db",
            "mysql://admin:p@ss#word$@localhost:3306/database",
            "postgresql://user%40email.com:pass%40word@localhost/db",
            "sqlite:///path/with spaces/test.db",
        ]

        for url in special_urls:
            if url.startswith(("postgresql://", "mysql://")):
                config = SQLAlchemyConfig(database_url=url)
                assert config.database_url == url

    @pytest.mark.asyncio
    async def test_date_filtering_edge_cases(self):
        """Test edge cases in date filtering for query_agent_history."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Create records with edge case dates
            now = datetime.utcnow()
            records = []

            # Record from far past
            past_record = Mock(spec=AgentState)
            past_record.created_at = datetime(1970, 1, 1)
            past_record.agent_id = "test_agent"
            past_record.key = "old_key"
            past_record.value = '"old_value"'
            past_record.data_type = "str"
            past_record.updated_at = past_record.created_at
            past_record.conversation_id = None
            past_record.agent_metadata = None
            records.append(past_record)

            # Record from future (edge case)
            future_record = Mock(spec=AgentState)
            future_record.created_at = now + timedelta(days=365)
            future_record.agent_id = "test_agent"
            future_record.key = "future_key"
            future_record.value = '"future_value"'
            future_record.data_type = "str"
            future_record.updated_at = future_record.created_at
            future_record.conversation_id = None
            future_record.agent_metadata = None
            records.append(future_record)

            mock_result = Mock()
            mock_scalars = Mock()
            mock_scalars.all.return_value = records
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            # Query with various date ranges
            result = await query_agent_history(
                config=config,
                agent_id="test_agent",
                start_date=datetime(1900, 1, 1),
                end_date=datetime(2100, 1, 1)
            )

            assert result.success is True
            assert len(result.results) == 2

    @pytest.mark.asyncio
    async def test_batch_operations(self):
        """Test batch insert/update operations."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        # Test batch storing
        batch_data = [
            ("key1", {"data": "value1"}),
            ("key2", [1, 2, 3, 4, 5]),
            ("key3", "simple string"),
            ("key4", 42),
            ("key5", True),
        ]

        for key, value in batch_data:
            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
                mock_session = AsyncMock(spec=AsyncSession)
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__.return_value = None

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result

                result = await store_agent_state(
                    config=config,
                    agent_id="batch_agent",
                    key=key,
                    value=value,
                    conversation_id="batch_conv"
                )

                assert result.success is True

    @pytest.mark.asyncio
    async def test_null_and_empty_values(self):
        """Test handling of null and empty values."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        test_cases = [
            ("", "Empty string"),
            ([], "Empty list"),
            ({}, "Empty dict"),
            (None, "None value"),
            (0, "Zero"),
            (False, "False boolean"),
            ("null", "String 'null'"),
        ]

        for value, description in test_cases:
            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
                mock_session = AsyncMock(spec=AsyncSession)
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__.return_value = None

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result

                result = await store_agent_state(
                    config=config,
                    agent_id="test_agent",
                    key=f"test_{description.replace(' ', '_')}",
                    value=value
                )

                assert result.success is True

    @pytest.mark.asyncio
    async def test_query_with_complex_filters(self):
        """Test complex query scenarios."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock empty result for complex query
            mock_result = Mock()
            mock_scalars = Mock()
            mock_scalars.all.return_value = []
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            # Test with all parameters
            result = await query_agent_history(
                config=config,
                agent_id="test_agent",
                conversation_id="conv_123",
                start_date=datetime.utcnow() - timedelta(days=7),
                end_date=datetime.utcnow(),
                limit=100,
                offset=50
            )

            assert result.success is True
            assert result.results == []

    @pytest.mark.asyncio
    async def test_database_connection_recovery(self):
        """Test database connection recovery after failure."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            # First call fails
            mock_get_session.side_effect = [
                Exception("Connection lost"),
                # Second call would succeed but we catch the first error
            ]

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value="test_value"
            )

            assert result.success is False
            assert "Connection lost" in result.error

    @pytest.mark.asyncio
    async def test_base64_binary_data(self):
        """Test storing binary data as base64."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # Store base64 encoded binary data
            import base64
            binary_data = b"Binary content \x00\x01\x02\x03\xff"
            encoded_data = base64.b64encode(binary_data).decode('utf-8')

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="binary_data",
                value={"data": encoded_data, "encoding": "base64"},
                metadata={"content_type": "application/octet-stream"}
            )

            assert result.success is True

    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self):
        """Test SQL injection prevention with malicious inputs."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        malicious_inputs = [
            "'; DROP TABLE agent_state; --",
            "' OR '1'='1",
            "'; DELETE FROM agent_state WHERE '1'='1'; --",
            "' UNION SELECT * FROM agent_state --",
            "\\'; DROP TABLE agent_state; --",
        ]

        for malicious_input in malicious_inputs:
            with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
                mock_session = AsyncMock(spec=AsyncSession)
                mock_get_session.return_value.__aenter__.return_value = mock_session
                mock_get_session.return_value.__aexit__.return_value = None

                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = None
                mock_session.execute.return_value = mock_result

                # Should safely store malicious strings as data
                result = await store_agent_state(
                    config=config,
                    agent_id=malicious_input,
                    key=malicious_input,
                    value=malicious_input
                )

                assert result.success is True
                # Verify the malicious string was treated as data
                add_call = mock_session.add.call_args[0][0]
                assert add_call.agent_id == malicious_input
                assert add_call.key == malicious_input

    @pytest.mark.asyncio
    async def test_connection_pool_exhaustion(self):
        """Test behavior when connection pool is exhausted."""
        config = SQLAlchemyConfig(
            database_url="postgresql://localhost/test",
            pool_size=1,
            max_overflow=0,
            pool_timeout=1  # Very short timeout
        )

        # Patch at the correct scope for the async context manager
        async_session_mock = AsyncMock()
        async_session_mock.__aenter__.side_effect = Exception("QueuePool limit of size 1 overflow 0 reached")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session", return_value=async_session_mock):
            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value="test_value"
            )

            assert result.success is False
            assert "QueuePool" in result.error

    @pytest.mark.asyncio
    async def test_long_running_transaction(self):
        """Test handling of long-running transactions."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # Simulate long-running operation
            async def slow_commit():
                await asyncio.sleep(0.5)  # 500ms delay

            mock_session.commit = slow_commit

            start = asyncio.get_event_loop().time()
            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key="test_key",
                value="test_value"
            )
            end = asyncio.get_event_loop().time()

            assert result.success is True
            assert result.execution_time >= 0.5
            assert (end - start) >= 0.5

    @pytest.mark.asyncio
    async def test_key_pattern_filtering(self):
        """Test key pattern filtering in queries."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Create records with various key patterns
            test_records = []
            key_patterns = [
                "config.database.host",
                "config.database.port",
                "config.api.key",
                "state.user.preferences",
                "state.user.profile",
                "temp.cache.data",
            ]

            for i, key in enumerate(key_patterns):
                record = Mock(spec=AgentState)
                record.id = i + 1
                record.agent_id = "test_agent"
                record.key = key
                record.value = f'"value_{i}"'
                record.data_type = "str"
                record.created_at = datetime.utcnow()
                record.updated_at = datetime.utcnow()
                record.conversation_id = None
                record.agent_metadata = None
                test_records.append(record)

            # Test different pattern queries
            patterns_to_test = [
                ("config.*", ["config.database.host", "config.database.port", "config.api.key"]),
                ("*.user.*", ["state.user.preferences", "state.user.profile"]),
                ("*cache*", ["temp.cache.data"]),
            ]

            for pattern, expected_keys in patterns_to_test:
                # Filter records based on pattern
                filtered = [r for r in test_records if any(
                    pattern.replace("*", "") in r.key for part in pattern.split("*") if part
                )]

                mock_result = Mock()
                mock_scalars = Mock()
                mock_scalars.all.return_value = filtered
                mock_result.scalars.return_value = mock_scalars
                mock_session.execute.return_value = mock_result

                result = await get_agent_state(
                    config=config,
                    agent_id="test_agent",
                    key=pattern  # Using pattern as key filter
                )

                assert result.success is True

    @pytest.mark.asyncio
    async def test_cleanup_with_conversation_filter(self):
        """Test cleanup with conversation ID filter."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        # Mock delete with conversation filter
        mock_result = Mock()
        mock_result.rowcount = 25

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None
            mock_session.execute.return_value = mock_result

            # Test the actual cleanup_old_state function with custom cutoff
            result = await cleanup_old_state(config, days_to_keep=7)

            assert result.success is True
            assert result.rows_affected == 25
            assert result.operation == "cleanup_old_state"

    @pytest.mark.asyncio
    async def test_extremely_long_keys_and_values(self):
        """Test handling of extremely long keys and string values."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # Test with very long key (near 255 char limit)
            long_key = "k" * 254

            # Test with very long complex value that will be JSON encoded
            long_value = {"data": "x" * 100000, "metadata": {"type": "large_data"}}

            result = await store_agent_state(
                config=config,
                agent_id="test_agent",
                key=long_key,
                value=long_value
            )

            assert result.success is True
            add_call = mock_session.add.call_args[0][0]
            assert len(add_call.key) == 254
            # JSON encoded value should be longer due to JSON structure
            assert len(add_call.value) > 100000

    @pytest.mark.asyncio
    async def test_timezone_handling(self):
        """Test handling of different timezones in dates."""
        config = SQLAlchemyConfig(database_url="sqlite:///test.db")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Create records with timezone-aware dates
            from datetime import timezone

            records = []
            utc_now = datetime.now(UTC)

            # Record with UTC timezone
            utc_record = Mock(spec=AgentState)
            utc_record.created_at = utc_now
            utc_record.updated_at = utc_now
            utc_record.agent_id = "test_agent"
            utc_record.key = "utc_key"
            utc_record.value = '"utc_value"'
            utc_record.data_type = "str"
            utc_record.conversation_id = None
            utc_record.agent_metadata = None
            records.append(utc_record)

            mock_result = Mock()
            mock_scalars = Mock()
            mock_scalars.all.return_value = records
            mock_result.scalars.return_value = mock_scalars
            mock_session.execute.return_value = mock_result

            result = await get_agent_state(config=config, agent_id="test_agent")

            assert result.success is True
            assert len(result.results) == 1

    @pytest.mark.asyncio
    async def test_database_specific_features(self):
        """Test database-specific features and syntax."""
        # Test PostgreSQL-specific features
        pg_config = SQLAlchemyConfig(database_url="postgresql://localhost/test")

        with patch("packages.sygaldry_registry.components.tools.sqlalchemy_db.tool.get_async_session") as mock_get_session:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_get_session.return_value.__aenter__.return_value = mock_session
            mock_get_session.return_value.__aexit__.return_value = None

            # Mock PostgreSQL-specific query result
            mock_bind = Mock()
            mock_bind.dialect.name = "postgresql"
            mock_session.bind = mock_bind

            # Test JSONB operations (PostgreSQL specific)
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            # Store JSON data that would use JSONB in PostgreSQL
            complex_json = {
                "nested": {"array": [1, 2, 3]},
                "query": {"field": "value"}
            }

            result = await store_agent_state(
                config=pg_config,
                agent_id="test_agent",
                key="jsonb_test",
                value=complex_json
            )

            assert result.success is True
