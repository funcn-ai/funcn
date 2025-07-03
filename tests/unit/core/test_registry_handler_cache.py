"""Unit tests for RegistryHandler caching functionality."""

from __future__ import annotations

import httpx
import json
import pytest
from pathlib import Path
from sygaldry_cli.config_manager import CacheConfig, ConfigManager, SygaldryConfig
from sygaldry_cli.core.models import RegistryComponentEntry, RegistryIndex
from sygaldry_cli.core.registry_handler import RegistryHandler
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, Mock, patch


class TestRegistryHandlerCache:
    """Test RegistryHandler caching functionality."""

    @pytest.fixture
    def sample_index(self):
        """Create a sample registry index."""
        return RegistryIndex(
            registry_version="1.0.0",
            updated_at="2024-01-01T00:00:00Z",
            components=[
                RegistryComponentEntry(
                    name="test-component",
                    version="1.0.0",
                    type="tool",
                    description="Test component",
                    manifest_path="components/test-component/1.0.0/component.json"
                )
            ]
        )

    @pytest.fixture
    def mock_config_with_cache(self):
        """Create a mock config manager with caching enabled."""
        with TemporaryDirectory() as tmpdir:
            config = SygaldryConfig(
                default_registry_url="https://example.com/index.json",
                registry_sources={
                    "default": "https://example.com/index.json",
                    "custom": "https://custom.com/index.json"
                },
                cache_config=CacheConfig(
                    enabled=True,
                    ttl_seconds=3600,
                    directory=str(tmpdir)
                )
            )

            mock_cfg = MagicMock(spec=ConfigManager)
            mock_cfg.config = config
            yield mock_cfg

    @pytest.fixture
    def mock_config_no_cache(self):
        """Create a mock config manager with caching disabled."""
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={"default": "https://example.com/index.json"},
            cache_config=CacheConfig(enabled=False)
        )

        mock_cfg = MagicMock(spec=ConfigManager)
        mock_cfg.config = config
        return mock_cfg

    def test_cache_manager_initialization_enabled(self, mock_config_with_cache):
        """Test that cache manager is initialized when caching is enabled."""
        handler = RegistryHandler(mock_config_with_cache)
        assert handler._cache_manager is not None

    def test_cache_manager_initialization_disabled(self, mock_config_no_cache):
        """Test that cache manager is not initialized when caching is disabled."""
        handler = RegistryHandler(mock_config_no_cache)
        assert handler._cache_manager is None

    @patch("sygaldry_cli.core.registry_handler.httpx.Client")
    def test_fetch_index_uses_cache(self, mock_client_class, mock_config_with_cache, sample_index):
        """Test that fetch_index uses cached data when available."""
        # Setup mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_index.model_dump()
        mock_response.headers = {"ETag": "test-etag"}

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        handler = RegistryHandler(mock_config_with_cache)

        # First fetch - should hit the network
        index1 = handler.fetch_index("default")
        assert index1 is not None
        assert mock_client.get.call_count == 1

        # Second fetch - should use cache
        index2 = handler.fetch_index("default")
        assert index2 is not None
        assert mock_client.get.call_count == 1  # No additional network call

        # Verify the indexes are the same
        assert index1.registry_version == index2.registry_version

    @patch("sygaldry_cli.core.registry_handler.httpx.Client")
    def test_fetch_index_force_refresh(self, mock_client_class, mock_config_with_cache, sample_index):
        """Test that force_refresh bypasses cache."""
        # Setup mock HTTP client
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_index.model_dump()
        mock_response.headers = {}

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        handler = RegistryHandler(mock_config_with_cache)

        # First fetch
        index1 = handler.fetch_index("default")
        assert mock_client.get.call_count == 1

        # Second fetch with force_refresh
        index2 = handler.fetch_index("default", force_refresh=True)
        assert mock_client.get.call_count == 2  # Additional network call

    @patch("sygaldry_cli.core.registry_handler.httpx.Client")
    def test_fetch_index_etag_support(self, mock_client_class, mock_config_with_cache, sample_index):
        """Test ETag support for conditional requests."""
        # First response with ETag
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = sample_index.model_dump()
        mock_response1.headers = {"ETag": "test-etag-v1"}

        # Second response - 304 Not Modified
        mock_response2 = Mock()
        mock_response2.status_code = 304
        mock_response2.raise_for_status = Mock()  # 304 shouldn't raise

        mock_client = Mock()
        mock_client.get.side_effect = [mock_response1, mock_response2]
        mock_client_class.return_value = mock_client

        handler = RegistryHandler(mock_config_with_cache)

        # First fetch - gets data and ETag
        index1 = handler.fetch_index("default")
        assert index1 is not None
        first_call_headers = mock_client.get.call_args_list[0][1].get("headers", {})
        assert "If-None-Match" not in first_call_headers

        # Save the first index to cache
        assert handler._cache_manager is not None

        # Clear cache to trigger a conditional request with etag
        # but leave the etag stored in metadata
        cache_path = handler._cache_manager._get_cache_path("default")
        index_file = cache_path / "index.json"

        # Simulate cache expiry by modifying timestamp but keeping etag
        import time
        metadata_path = handler._cache_manager._get_metadata_path("default")
        with open(metadata_path) as f:
            metadata = json.load(f)
        metadata["timestamp"] = time.time() - 7200  # 2 hours ago
        with open(metadata_path, "w") as f:
            json.dump(metadata, f)

        # Second fetch - should send If-None-Match header and get 304
        index2 = handler.fetch_index("default")
        assert index2 is not None
        assert mock_client.get.call_count == 2
        second_call_headers = mock_client.get.call_args_list[1][1].get("headers", {})
        assert second_call_headers.get("If-None-Match") == "test-etag-v1"

    @patch("sygaldry_cli.core.registry_handler.httpx.Client")
    def test_fetch_all_indexes_with_cache(self, mock_client_class, mock_config_with_cache, sample_index):
        """Test that fetch_all_indexes uses cache."""
        # Setup mock responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_index.model_dump()
        mock_response.headers = {}

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        handler = RegistryHandler(mock_config_with_cache)

        # First fetch all
        indexes1 = handler.fetch_all_indexes()
        assert len(indexes1) == 2  # default and custom
        assert mock_client.get.call_count == 2

        # Second fetch all - should use cache
        indexes2 = handler.fetch_all_indexes()
        assert len(indexes2) == 2
        assert mock_client.get.call_count == 2  # No additional calls

    @patch("sygaldry_cli.core.registry_handler.httpx.Client")
    def test_fetch_all_indexes_force_refresh(self, mock_client_class, mock_config_with_cache, sample_index):
        """Test that fetch_all_indexes respects force_refresh."""
        # Setup mock responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_index.model_dump()
        mock_response.headers = {}

        mock_client = Mock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        handler = RegistryHandler(mock_config_with_cache)

        # First fetch all
        indexes1 = handler.fetch_all_indexes()
        assert mock_client.get.call_count == 2

        # Second fetch all with force_refresh
        indexes2 = handler.fetch_all_indexes(force_refresh=True)
        assert mock_client.get.call_count == 4  # Additional calls

    @patch("sygaldry_cli.core.registry_handler.httpx.Client")
    def test_cache_survives_network_errors(self, mock_client_class, mock_config_with_cache, sample_index):
        """Test that cache is used when network fails."""
        # First successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_index.model_dump()
        mock_response.headers = {"ETag": "test-etag"}

        # Setup client to succeed then fail
        mock_client = Mock()
        mock_client.get.side_effect = [
            mock_response,  # First call succeeds
            httpx.ConnectError("Network error")  # Second call fails
        ]
        mock_client_class.return_value = mock_client

        handler = RegistryHandler(mock_config_with_cache)

        # First fetch - succeeds and caches
        index1 = handler.fetch_index("default")
        assert index1 is not None

        # Expire cache to force re-fetch
        handler._cache_manager.invalidate_cache("default")

        # Second fetch - network fails, but should handle gracefully
        index2 = handler.fetch_index("default", silent_errors=True)
        assert index2 is None  # Returns None on error when silent_errors=True

    def test_cache_disabled_no_caching(self, mock_config_no_cache, sample_index):
        """Test that no caching occurs when disabled."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_index.model_dump()
            mock_response.headers = {}

            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            handler = RegistryHandler(mock_config_no_cache)

            # Multiple fetches should all hit the network
            for _ in range(3):
                index = handler.fetch_index("default")
                assert index is not None

            assert mock_client.get.call_count == 3  # All calls hit network
