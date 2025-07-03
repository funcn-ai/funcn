"""Cache manager for registry indexes and metadata."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime, timezone
from pathlib import Path
from rich.console import Console
from sygaldry_cli.core.models import RegistryIndex
from typing import Any

console = Console()


class CacheMetadata:
    """Metadata for cached items."""

    def __init__(self, etag: str | None = None, timestamp: float | None = None):
        self.etag = etag
        self.timestamp = timestamp or time.time()
        self.last_accessed = self.timestamp

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "etag": self.etag,
            "timestamp": self.timestamp,
            "last_accessed": self.last_accessed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CacheMetadata:
        """Create from dictionary."""
        metadata = cls(etag=data.get("etag"), timestamp=data.get("timestamp"))
        metadata.last_accessed = data.get("last_accessed", metadata.timestamp)
        return metadata

    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if cache entry is expired based on TTL."""
        if ttl_seconds <= 0:  # TTL of 0 or negative means no expiration
            return False
        return (time.time() - self.timestamp) > ttl_seconds

    def update_access_time(self) -> None:
        """Update last accessed time."""
        self.last_accessed = time.time()


class CacheManager:
    """Manages caching of registry indexes and metadata."""

    def __init__(self, cache_dir: Path | None = None):
        """Initialize cache manager.

        Args:
            cache_dir: Optional cache directory. If None, uses default platform-specific location.
        """
        if cache_dir is None:
            # Use platformdirs for cross-platform cache directory
            try:
                from platformdirs import user_cache_dir
                cache_dir = Path(user_cache_dir("sygaldry", "sygaldry-ai"))
            except ImportError:
                # Fallback to home directory if platformdirs not available
                cache_dir = Path.home() / ".sygaldry" / "cache"

        self.cache_dir = cache_dir
        self.registries_dir = self.cache_dir / "registries"
        self.registries_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, source_alias: str) -> Path:
        """Get cache directory path for a source."""
        return self.registries_dir / source_alias

    def _get_index_path(self, source_alias: str) -> Path:
        """Get index file path for a source."""
        return self._get_cache_path(source_alias) / "index.json"

    def _get_metadata_path(self, source_alias: str) -> Path:
        """Get metadata file path for a source."""
        return self._get_cache_path(source_alias) / "metadata.json"

    def get_cached_index(self, source_alias: str, max_age: int = 3600) -> tuple[RegistryIndex | None, str | None]:
        """Get cached index if valid.

        Args:
            source_alias: The source alias to get cache for
            max_age: Maximum age in seconds for cache validity (0 = no expiration)

        Returns:
            Tuple of (RegistryIndex or None, ETag or None)
        """
        try:
            index_path = self._get_index_path(source_alias)
            metadata_path = self._get_metadata_path(source_alias)

            if not index_path.exists() or not metadata_path.exists():
                return None, None

            # Load metadata
            with open(metadata_path) as f:
                metadata_dict = json.load(f)
            metadata = CacheMetadata.from_dict(metadata_dict)

            # Check if expired
            if metadata.is_expired(max_age):
                console.log(f"Cache for '{source_alias}' is expired")
                return None, metadata.etag  # Return ETag for conditional request

            # Load index
            with open(index_path) as f:
                index_data = json.load(f)
            index = RegistryIndex.model_validate(index_data)

            # Update access time
            metadata.update_access_time()
            with open(metadata_path, "w") as f:
                json.dump(metadata.to_dict(), f, indent=2)

            console.log(f"Using cached index for '{source_alias}'")
            return index, metadata.etag

        except Exception as e:
            console.log(f"Failed to load cache for '{source_alias}': {e}")
            return None, None

    def save_index_to_cache(self, source_alias: str, index: RegistryIndex, etag: str | None = None) -> None:
        """Save index to cache with metadata.

        Args:
            source_alias: The source alias to cache
            index: The registry index to cache
            etag: Optional ETag from HTTP response
        """
        try:
            cache_path = self._get_cache_path(source_alias)
            cache_path.mkdir(parents=True, exist_ok=True)

            # Save index
            index_path = self._get_index_path(source_alias)
            with open(index_path, "w") as f:
                json.dump(index.model_dump(), f, indent=2)

            # Save metadata
            metadata = CacheMetadata(etag=etag)
            metadata_path = self._get_metadata_path(source_alias)
            with open(metadata_path, "w") as f:
                json.dump(metadata.to_dict(), f, indent=2)

            console.log(f"Cached index for '{source_alias}'")

        except Exception as e:
            console.log(f"Failed to cache index for '{source_alias}': {e}")

    def invalidate_cache(self, source_alias: str | None = None) -> None:
        """Invalidate cache for source or all sources.

        Args:
            source_alias: Optional source to invalidate. If None, invalidates all.
        """
        try:
            if source_alias:
                # Invalidate specific source
                cache_path = self._get_cache_path(source_alias)
                if cache_path.exists():
                    import shutil
                    shutil.rmtree(cache_path)
                    console.log(f"Invalidated cache for '{source_alias}'")
            else:
                # Invalidate all caches
                if self.registries_dir.exists():
                    import shutil
                    shutil.rmtree(self.registries_dir)
                    self.registries_dir.mkdir(parents=True, exist_ok=True)
                    console.log("Invalidated all registry caches")

        except Exception as e:
            console.log(f"Failed to invalidate cache: {e}")

    def get_cache_stats(self) -> dict[str, dict[str, Any]]:
        """Get cache statistics for all sources.

        Returns:
            Dictionary mapping source alias to cache info
        """
        stats = {}

        try:
            for source_dir in self.registries_dir.iterdir():
                if source_dir.is_dir():
                    source_alias = source_dir.name
                    metadata_path = self._get_metadata_path(source_alias)

                    if metadata_path.exists():
                        with open(metadata_path) as f:
                            metadata_dict = json.load(f)
                        metadata = CacheMetadata.from_dict(metadata_dict)

                        # Calculate cache age
                        age_seconds = time.time() - metadata.timestamp
                        age_readable = self._format_duration(age_seconds)

                        # Get cache size
                        index_path = self._get_index_path(source_alias)
                        size_bytes = index_path.stat().st_size if index_path.exists() else 0

                        stats[source_alias] = {
                            "age": age_readable,
                            "age_seconds": age_seconds,
                            "size_bytes": size_bytes,
                            "etag": metadata.etag,
                            "cached_at": datetime.fromtimestamp(metadata.timestamp, tz=UTC).isoformat(),
                            "last_accessed": datetime.fromtimestamp(metadata.last_accessed, tz=UTC).isoformat(),
                        }

        except Exception as e:
            console.log(f"Failed to get cache stats: {e}")

        return stats

    def clear_all_caches(self) -> None:
        """Clear all cached data."""
        self.invalidate_cache()

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m"
        elif seconds < 86400:
            return f"{int(seconds / 3600)}h"
        else:
            return f"{int(seconds / 86400)}d"
