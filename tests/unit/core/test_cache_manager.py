"""Unit tests for the CacheManager."""

from __future__ import annotations

import json
import pytest
import time
from pathlib import Path
from sygaldry_cli.core.cache_manager import CacheManager, CacheMetadata
from sygaldry_cli.core.models import RegistryComponentEntry, RegistryIndex
from tempfile import TemporaryDirectory


class TestCacheMetadata:
    """Test the CacheMetadata class."""

    def test_metadata_creation(self):
        """Test creating cache metadata."""
        metadata = CacheMetadata(etag="test-etag", timestamp=1234567890.0)
        assert metadata.etag == "test-etag"
        assert metadata.timestamp == 1234567890.0
        assert metadata.last_accessed == 1234567890.0

    def test_metadata_default_timestamp(self):
        """Test metadata creation with default timestamp."""
        before = time.time()
        metadata = CacheMetadata(etag="test-etag")
        after = time.time()

        assert metadata.etag == "test-etag"
        assert before <= metadata.timestamp <= after
        assert metadata.timestamp == metadata.last_accessed

    def test_metadata_serialization(self):
        """Test metadata serialization to/from dict."""
        metadata = CacheMetadata(etag="test-etag", timestamp=1234567890.0)

        # To dict
        data = metadata.to_dict()
        assert data["etag"] == "test-etag"
        assert data["timestamp"] == 1234567890.0
        assert data["last_accessed"] == 1234567890.0

        # From dict
        restored = CacheMetadata.from_dict(data)
        assert restored.etag == metadata.etag
        assert restored.timestamp == metadata.timestamp
        assert restored.last_accessed == metadata.last_accessed

    def test_expiration_check(self):
        """Test cache expiration logic."""
        # Create metadata from 1 hour ago
        old_timestamp = time.time() - 3700  # 1 hour + 100 seconds
        metadata = CacheMetadata(etag="test", timestamp=old_timestamp)

        # Should be expired with 1 hour TTL
        assert metadata.is_expired(3600) is True

        # Should not be expired with 2 hour TTL
        assert metadata.is_expired(7200) is False

        # Should never expire with 0 or negative TTL
        assert metadata.is_expired(0) is False
        assert metadata.is_expired(-1) is False

    def test_update_access_time(self):
        """Test updating last accessed time."""
        metadata = CacheMetadata(etag="test", timestamp=1234567890.0)
        original_access = metadata.last_accessed

        time.sleep(0.01)  # Small delay
        metadata.update_access_time()

        assert metadata.timestamp == 1234567890.0  # Unchanged
        assert metadata.last_accessed > original_access


class TestCacheManager:
    """Test the CacheManager class."""

    @pytest.fixture
    def cache_dir(self):
        """Create a temporary cache directory."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

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

    def test_cache_manager_initialization(self, cache_dir):
        """Test CacheManager initialization."""
        manager = CacheManager(cache_dir=cache_dir)
        assert manager.cache_dir == cache_dir
        assert manager.registries_dir == cache_dir / "registries"
        assert manager.registries_dir.exists()

    def test_cache_manager_default_dir(self):
        """Test CacheManager with default directory."""
        manager = CacheManager()
        assert manager.cache_dir is not None
        assert manager.registries_dir.exists()

    def test_save_and_get_cached_index(self, cache_dir, sample_index):
        """Test saving and retrieving cached index."""
        manager = CacheManager(cache_dir=cache_dir)

        # Save index
        manager.save_index_to_cache("test-source", sample_index, etag="test-etag")

        # Retrieve index
        cached_index, etag = manager.get_cached_index("test-source", max_age=3600)

        assert cached_index is not None
        assert etag == "test-etag"
        assert cached_index.registry_version == sample_index.registry_version
        assert len(cached_index.components) == len(sample_index.components)
        assert cached_index.components[0].name == sample_index.components[0].name

    def test_cache_expiration(self, cache_dir, sample_index):
        """Test cache expiration."""
        manager = CacheManager(cache_dir=cache_dir)

        # Save index
        manager.save_index_to_cache("test-source", sample_index, etag="test-etag")

        # Should be valid with long TTL
        cached_index, etag = manager.get_cached_index("test-source", max_age=3600)
        assert cached_index is not None

        # Should be expired with 0 second TTL (unless TTL is 0)
        cached_index, etag = manager.get_cached_index("test-source", max_age=0)
        assert cached_index is not None  # TTL 0 means no expiration

        # Manually set old timestamp to test expiration
        metadata_path = manager._get_metadata_path("test-source")
        with open(metadata_path) as f:
            metadata_dict = json.load(f)
        metadata_dict["timestamp"] = time.time() - 7200  # 2 hours ago
        with open(metadata_path, "w") as f:
            json.dump(metadata_dict, f)

        # Should be expired with 1 hour TTL
        cached_index, returned_etag = manager.get_cached_index("test-source", max_age=3600)
        assert cached_index is None
        assert returned_etag == "test-etag"  # ETag still returned for conditional request

    def test_cache_miss(self, cache_dir):
        """Test cache miss for non-existent source."""
        manager = CacheManager(cache_dir=cache_dir)

        cached_index, etag = manager.get_cached_index("non-existent", max_age=3600)
        assert cached_index is None
        assert etag is None

    def test_invalidate_specific_cache(self, cache_dir, sample_index):
        """Test invalidating cache for specific source."""
        manager = CacheManager(cache_dir=cache_dir)

        # Save indexes for multiple sources
        manager.save_index_to_cache("source1", sample_index, etag="etag1")
        manager.save_index_to_cache("source2", sample_index, etag="etag2")

        # Verify both exist
        assert manager.get_cached_index("source1", max_age=3600)[0] is not None
        assert manager.get_cached_index("source2", max_age=3600)[0] is not None

        # Invalidate source1
        manager.invalidate_cache("source1")

        # source1 should be gone, source2 should remain
        assert manager.get_cached_index("source1", max_age=3600)[0] is None
        assert manager.get_cached_index("source2", max_age=3600)[0] is not None

    def test_invalidate_all_caches(self, cache_dir, sample_index):
        """Test invalidating all caches."""
        manager = CacheManager(cache_dir=cache_dir)

        # Save indexes for multiple sources
        manager.save_index_to_cache("source1", sample_index, etag="etag1")
        manager.save_index_to_cache("source2", sample_index, etag="etag2")

        # Verify both exist
        assert manager.get_cached_index("source1", max_age=3600)[0] is not None
        assert manager.get_cached_index("source2", max_age=3600)[0] is not None

        # Invalidate all
        manager.invalidate_cache()

        # Both should be gone
        assert manager.get_cached_index("source1", max_age=3600)[0] is None
        assert manager.get_cached_index("source2", max_age=3600)[0] is None

    def test_cache_stats(self, cache_dir, sample_index):
        """Test getting cache statistics."""
        manager = CacheManager(cache_dir=cache_dir)

        # Initially empty
        stats = manager.get_cache_stats()
        assert len(stats) == 0

        # Save some indexes
        manager.save_index_to_cache("source1", sample_index, etag="etag1")
        time.sleep(0.1)  # Small delay
        manager.save_index_to_cache("source2", sample_index, etag="etag2")

        # Get stats
        stats = manager.get_cache_stats()
        assert len(stats) == 2

        # Check source1 stats
        assert "source1" in stats
        assert stats["source1"]["etag"] == "etag1"
        assert stats["source1"]["size_bytes"] > 0
        assert "age" in stats["source1"]
        assert "cached_at" in stats["source1"]
        assert "last_accessed" in stats["source1"]

        # Check source2 stats
        assert "source2" in stats
        assert stats["source2"]["etag"] == "etag2"

    def test_format_duration(self):
        """Test duration formatting."""
        assert CacheManager._format_duration(30) == "30s"
        assert CacheManager._format_duration(90) == "1m"
        assert CacheManager._format_duration(3600) == "1h"
        assert CacheManager._format_duration(7200) == "2h"
        assert CacheManager._format_duration(86400) == "1d"
        assert CacheManager._format_duration(172800) == "2d"

    def test_clear_all_caches(self, cache_dir, sample_index):
        """Test clear_all_caches method."""
        manager = CacheManager(cache_dir=cache_dir)

        # Save some data
        manager.save_index_to_cache("source1", sample_index)
        assert manager.get_cached_index("source1", max_age=3600)[0] is not None

        # Clear all
        manager.clear_all_caches()

        # Should be gone
        assert manager.get_cached_index("source1", max_age=3600)[0] is None

    def test_corrupted_cache_handling(self, cache_dir, sample_index):
        """Test handling of corrupted cache files."""
        manager = CacheManager(cache_dir=cache_dir)

        # Save valid cache
        manager.save_index_to_cache("test-source", sample_index)

        # Corrupt the index file
        index_path = manager._get_index_path("test-source")
        index_path.write_text("invalid json {{{")

        # Should return None on error
        cached_index, etag = manager.get_cached_index("test-source", max_age=3600)
        assert cached_index is None
        assert etag is None

    def test_access_time_update(self, cache_dir, sample_index):
        """Test that accessing cache updates last accessed time."""
        manager = CacheManager(cache_dir=cache_dir)

        # Save index
        manager.save_index_to_cache("test-source", sample_index)

        # Get initial stats
        stats1 = manager.get_cache_stats()
        initial_access = stats1["test-source"]["last_accessed"]

        # Wait and access cache
        time.sleep(0.1)
        manager.get_cached_index("test-source", max_age=3600)

        # Check updated stats
        stats2 = manager.get_cache_stats()
        new_access = stats2["test-source"]["last_accessed"]

        assert new_access > initial_access
