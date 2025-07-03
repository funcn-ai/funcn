"""Tests for the registry handler with offline source handling."""

from __future__ import annotations

import httpx
import pytest
from sygaldry_cli.config_manager import ConfigManager, SygaldryConfig
from sygaldry_cli.core.models import RegistryComponentEntry, RegistryIndex
from sygaldry_cli.core.registry_handler import RegistryHandler
from unittest.mock import MagicMock, patch


class TestRegistryHandler:
    """Test the registry handler."""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration with multiple sources."""
        return SygaldryConfig(
            default_registry_url="https://default.com/index.json",
            registry_sources={
                "default": "https://default.com/index.json",
                "backup": "https://backup.com/index.json",
                "local": "https://local.com/index.json",
            },
            component_paths={"agents": "./src/agents", "tools": "./src/tools"},
        )

    @pytest.fixture
    def sample_index(self):
        """Sample registry index."""
        return RegistryIndex(
            registry_version="1.0.0",
            components=[
                RegistryComponentEntry(
                    name="test-agent",
                    version="1.0.0",
                    type="agent",
                    description="Test agent",
                    manifest_path="components/agents/test-agent/component.json",
                ),
                RegistryComponentEntry(
                    name="test-tool",
                    version="2.0.0",
                    type="tool",
                    description="Test tool",
                    manifest_path="components/tools/test-tool/component.json",
                ),
            ],
        )

    @pytest.fixture
    def mock_config_manager(self, sample_config):
        """Mock ConfigManager."""
        mock_cfg = MagicMock(spec=ConfigManager)
        mock_cfg.config = sample_config
        return mock_cfg

    def test_fetch_index_with_silent_errors_timeout(self, mock_config_manager):
        """Test fetch_index with timeout and silent errors."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # With silent_errors=True, should return None
            result = rh.fetch_index(source_alias="default", silent_errors=True)
            assert result is None

            # With silent_errors=False, should raise
            with pytest.raises(httpx.TimeoutException):
                rh.fetch_index(source_alias="default", silent_errors=False)

    def test_fetch_index_with_silent_errors_connection_error(self, mock_config_manager):
        """Test fetch_index with connection error and silent errors."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # With silent_errors=True, should return None
            result = rh.fetch_index(source_alias="backup", silent_errors=True)
            assert result is None

            # With silent_errors=False, should raise
            with pytest.raises(httpx.ConnectError):
                rh.fetch_index(source_alias="backup", silent_errors=False)

    def test_fetch_index_with_silent_errors_http_error(self, mock_config_manager):
        """Test fetch_index with HTTP error and silent errors."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_response
            )

            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # With silent_errors=True, should return None
            result = rh.fetch_index(source_alias="local", silent_errors=True)
            assert result is None

            # With silent_errors=False, should raise
            with pytest.raises(httpx.HTTPStatusError):
                rh.fetch_index(source_alias="local", silent_errors=False)

    def test_fetch_all_indexes_mixed_availability(self, mock_config_manager, sample_index):
        """Test fetch_all_indexes with some sources offline."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()

            def mock_get_side_effect(url):
                if "default.com" in url:
                    # Default source works
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = sample_index.model_dump()
                    return mock_response
                elif "backup.com" in url:
                    # Backup source is offline
                    raise httpx.ConnectError("Connection failed")
                elif "local.com" in url:
                    # Local source works
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = sample_index.model_dump()
                    return mock_response

            mock_client.get.side_effect = mock_get_side_effect
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # Should return only the working sources
            indexes = rh.fetch_all_indexes(silent_errors=True)
            assert len(indexes) == 2
            assert "default" in indexes
            assert "local" in indexes
            assert "backup" not in indexes

    def test_fetch_all_indexes_all_offline(self, mock_config_manager):
        """Test fetch_all_indexes when all sources are offline."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # Should return empty dict when all sources fail
            indexes = rh.fetch_all_indexes(silent_errors=True)
            assert indexes == {}

    def test_find_component_with_offline_sources(self, mock_config_manager, sample_index):
        """Test finding component when some sources are offline."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()

            def mock_get_side_effect(url):
                if "default.com" in url:
                    # Default source is offline
                    raise httpx.TimeoutException("Timeout")
                elif "backup.com" in url:
                    # Backup source works and has the component
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = sample_index.model_dump()
                    return mock_response
                elif "local.com" in url:
                    # Local source is offline
                    raise httpx.ConnectError("Connection failed")

            mock_client.get.side_effect = mock_get_side_effect
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # Should find component in backup source
            result = rh.find_component_manifest_url("test-agent")
            assert result is not None
            assert "backup.com" in result

    def test_search_single_source_offline(self, mock_config_manager):
        """Test _search_single_source when source is offline."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # Should return None gracefully
            result = rh._search_single_source("test-component", None, "offline-source")
            assert result is None

    def test_no_url_for_source_alias(self, mock_config_manager):
        """Test handling when no URL is configured for a source alias."""
        rh = RegistryHandler(mock_config_manager)

        # With silent_errors=True
        result = rh.fetch_index(source_alias="nonexistent", silent_errors=True)
        assert result is None

        # With silent_errors=False
        with pytest.raises(ValueError, match="No URL found for registry source"):
            rh.fetch_index(source_alias="nonexistent", silent_errors=False)

    def test_get_sources_by_priority(self, mock_config_manager):
        """Test getting sources ordered by priority."""
        # Mix of string and object formats
        mock_config_manager.config.registry_sources = {
            "high": {"url": "https://high.com/index.json", "priority": 10, "enabled": True},
            "disabled": {"url": "https://disabled.com/index.json", "priority": 5, "enabled": False},
            "medium": {"url": "https://medium.com/index.json", "priority": 50, "enabled": True},
            "low": "https://low.com/index.json",  # Default priority 100
            "lower": {"url": "https://lower.com/index.json", "priority": 200, "enabled": True},
            "default": "https://default.com/index.json",  # Override default to avoid adding it twice
        }

        rh = RegistryHandler(mock_config_manager)
        sources = rh.get_sources_by_priority()

        # Should be sorted by priority, excluding disabled
        assert len(sources) == 5
        assert sources[0] == ("high", "https://high.com/index.json", 10)
        assert sources[1] == ("medium", "https://medium.com/index.json", 50)

        # Both default and low have priority 100, order between them doesn't matter
        priority_100_sources = [s for s in sources if s[2] == 100]
        assert len(priority_100_sources) == 2
        assert ("default", "https://default.com/index.json", 100) in priority_100_sources
        assert ("low", "https://low.com/index.json", 100) in priority_100_sources

        assert sources[4] == ("lower", "https://lower.com/index.json", 200)

    def test_fetch_all_indexes_respects_priority(self, mock_config_manager, sample_index):
        """Test that fetch_all_indexes fetches sources in priority order."""
        # Set up sources with different priorities
        mock_config_manager.config.registry_sources = {
            "high": {"url": "https://high.com/index.json", "priority": 10, "enabled": True},
            "medium": {"url": "https://medium.com/index.json", "priority": 50, "enabled": True},
            "low": {"url": "https://low.com/index.json", "priority": 100, "enabled": True},
        }

        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            fetch_order = []

            def mock_get_side_effect(url):
                # Track the order of fetches
                if "high.com" in url:
                    fetch_order.append("high")
                elif "medium.com" in url:
                    fetch_order.append("medium")
                elif "low.com" in url:
                    fetch_order.append("low")

                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = sample_index.model_dump()
                return mock_response

            mock_client.get.side_effect = mock_get_side_effect
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # Fetch all indexes
            indexes = rh.fetch_all_indexes(silent_errors=True)

            # Check fetch order matches priority
            assert fetch_order == ["high", "medium", "low"]
            assert len(indexes) == 3

    def test_find_component_uses_priority_order(self, mock_config_manager, sample_index):
        """Test that component search respects source priority."""
        # Set up sources with different priorities
        mock_config_manager.config.registry_sources = {
            "low_priority": {"url": "https://low.com/index.json", "priority": 100, "enabled": True},
            "high_priority": {"url": "https://high.com/index.json", "priority": 10, "enabled": True},
        }

        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            search_order = []

            def mock_get_side_effect(url):
                if "high.com" in url:
                    search_order.append("high_priority")
                    # Return empty index (component not found)
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"registry_version": "1.0.0", "components": []}
                    return mock_response
                elif "low.com" in url:
                    search_order.append("low_priority")
                    # Return index with component
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = sample_index.model_dump()
                    return mock_response

            mock_client.get.side_effect = mock_get_side_effect
            mock_client_class.return_value = mock_client

            rh = RegistryHandler(mock_config_manager)
            rh._client = mock_client

            # Search for component
            result = rh.find_component_manifest_url("test-agent")

            # Should search high priority first, then low priority
            assert search_order == ["high_priority", "low_priority"]
            assert result is not None
            assert "low.com" in result
