from __future__ import annotations

import httpx
from pathlib import Path
from rich.console import Console
from sygaldry_cli.config_manager import ConfigManager, RegistrySourceConfig
from sygaldry_cli.core.cache_manager import CacheManager
from sygaldry_cli.core.models import ComponentManifest, RegistryIndex

console = Console()


class RegistryHandler:
    """Fetches registry indexes and component manifests."""

    def __init__(self, cfg: ConfigManager | None = None) -> None:
        self._cfg = cfg or ConfigManager()
        self._client = httpx.Client(timeout=30.0)

        # Initialize cache manager if caching is enabled
        cache_config = self._cfg.config.cache_config
        self._cache_manager: CacheManager | None = None
        if cache_config.enabled:
            cache_dir = Path(cache_config.directory) if cache_config.directory else None
            self._cache_manager = CacheManager(cache_dir=cache_dir)

    # ------------------------------------------------------------------
    # Index helpers
    # ------------------------------------------------------------------

    def get_sources_by_priority(self) -> list[tuple[str, str, int]]:
        """Get sources ordered by priority.

        Returns:
            List of tuples (alias, url, priority) sorted by priority
        """
        sources = []

        # Add default source if not in registry_sources
        if self._cfg.config.default_registry_url:
            if "default" not in self._cfg.config.registry_sources:
                sources.append(("default", self._cfg.config.default_registry_url, 100))

        # Add all configured sources
        for alias, source in self._cfg.config.registry_sources.items():
            if isinstance(source, str):
                # Backward compatibility: string format
                sources.append((alias, source, 100))
            elif isinstance(source, RegistrySourceConfig):
                # New format with priority
                if source.enabled:
                    sources.append((alias, source.url, source.priority))
            else:
                # Handle dict format (from JSON)
                if isinstance(source, dict):
                    enabled = source.get("enabled", True)
                    if enabled:
                        sources.append((alias, source["url"], source.get("priority", 100)))

        # Sort by priority (lower number = higher priority)
        return sorted(sources, key=lambda x: x[2])

    def fetch_all_indexes(self, silent_errors: bool = True, force_refresh: bool = False) -> dict[str, RegistryIndex]:
        """Fetch indexes from all configured sources.

        Args:
            silent_errors: If True, skip failed sources instead of raising
            force_refresh: If True, bypass cache and force fresh fetches

        Returns:
            Dictionary mapping source alias to RegistryIndex for successful fetches
        """
        indexes = {}

        # Fetch sources in priority order
        for alias, url, priority in self.get_sources_by_priority():
            index = self.fetch_index(source_alias=alias, silent_errors=silent_errors, force_refresh=force_refresh)
            if index:
                indexes[alias] = index

        return indexes

    def fetch_index(self, source_alias: str | None = None, silent_errors: bool = False, force_refresh: bool = False) -> RegistryIndex | None:
        """Fetch registry index from a source.

        Args:
            source_alias: The alias of the source to fetch from
            silent_errors: If True, returns None on error instead of raising
            force_refresh: If True, bypass cache and force a fresh fetch

        Returns:
            RegistryIndex if successful, None if silent_errors=True and an error occurs

        Raises:
            ValueError: If no URL found for the source alias
            httpx.HTTPError: If the request fails and silent_errors=False
        """
        # Determine the actual source alias to use
        actual_alias = source_alias or "default"

        # Check cache first if not forcing refresh
        etag = None
        if self._cache_manager and not force_refresh:
            cache_config = self._cfg.config.cache_config
            cached_index, etag = self._cache_manager.get_cached_index(actual_alias, max_age=cache_config.ttl_seconds)
            if cached_index:
                return cached_index

        # Get URL handling both string and object formats
        if source_alias:
            source = self._cfg.config.registry_sources.get(source_alias)
            if source is None:
                url = None
            elif isinstance(source, str):
                url = source
            elif isinstance(source, RegistrySourceConfig):
                url = source.url if source.enabled else None
            elif isinstance(source, dict):
                url = source.get("url") if source.get("enabled", True) else None
            else:
                url = None
        else:
            url = self._cfg.config.default_registry_url

        if not url:
            if silent_errors:
                return None
            raise ValueError(f"No URL found for registry source: {source_alias}")

        try:
            console.log(f"Fetching registry index from {url}")

            # Prepare headers with ETag if available
            headers = {}
            if etag:
                headers["If-None-Match"] = etag

            resp = self._client.get(url, headers=headers)

            # Handle 304 Not Modified
            if resp.status_code == 304:
                console.log(f"Registry index for '{actual_alias}' has not changed (304)")
                # The cached version is still valid, return it
                if self._cache_manager:
                    cached_index, _ = self._cache_manager.get_cached_index(actual_alias, max_age=0)  # No expiry check
                    if cached_index:
                        return cached_index

            resp.raise_for_status()
            data = resp.json()
            index = RegistryIndex.model_validate(data)

            # Cache the fetched index
            if self._cache_manager:
                new_etag = resp.headers.get("ETag")
                self._cache_manager.save_index_to_cache(actual_alias, index, etag=new_etag)

            return index
        except httpx.TimeoutException:
            if silent_errors:
                console.print(f"[yellow]Warning: Source '{source_alias or 'default'}' timed out[/]")
                return None
            raise
        except httpx.ConnectError:
            if silent_errors:
                console.print(f"[yellow]Warning: Source '{source_alias or 'default'}' is unreachable[/]")
                return None
            raise
        except httpx.HTTPStatusError as e:
            if silent_errors:
                console.print(f"[yellow]Warning: Source '{source_alias or 'default'}' returned error {e.response.status_code}[/]")
                return None
            raise
        except Exception as e:
            if silent_errors:
                console.print(f"[yellow]Warning: Failed to fetch from source '{source_alias or 'default'}': {e}[/]")
                return None
            raise

    def find_component_manifest_url(self, component_name: str, version: str | None = None, source_alias: str | None = None) -> str | None:
        """Find component manifest URL in the specified source or all sources.

        Args:
            component_name: Name of the component to find
            version: Optional version to match (if None, returns latest version)
            source_alias: Optional specific source to search in
        """
        if source_alias:
            # Search in specific source
            return self._search_single_source(component_name, version, source_alias)
        else:
            # Search in all sources by priority order
            for alias, url, priority in self.get_sources_by_priority():
                result = self._search_single_source(component_name, version, alias)
                if result:
                    if alias != "default":  # Don't show message for default source
                        console.print(f"[cyan]Found component '{component_name}' in source '{alias}'[/]")
                    return result
            return None

    def _search_single_source(self, component_name: str, version: str | None, source_alias: str | None) -> str | None:
        """Search for component in a single source."""
        # Use silent_errors=True to gracefully handle offline sources
        index = self.fetch_index(source_alias=source_alias, silent_errors=True)
        if not index:
            return None

        # Get URL handling both string and object formats
        url: str | None = None
        if source_alias:
            source = self._cfg.config.registry_sources.get(source_alias)
            if isinstance(source, str):
                url = source
            elif isinstance(source, RegistrySourceConfig):
                url = source.url
            elif isinstance(source, dict):
                url = source.get("url")
            else:
                url = None
        else:
            url = self._cfg.config.default_registry_url

        if not url:
            return None

        # Find all matching components by name
        matching_components = [comp for comp in index.components if comp.name == component_name]

        if not matching_components:
            return None

        # If version is specified, find exact match
        if version:
            for comp in matching_components:
                if comp.version == version:
                    root_url = str(Path(url).parent)
                    manifest_url = f"{root_url}/{comp.manifest_path}"
                    return manifest_url
            return None  # Version not found

        # If no version specified, find the latest version
        # Sort by version (assumes semantic versioning)
        from packaging import version as pkg_version
        try:
            sorted_components = sorted(
                matching_components,
                key=lambda c: pkg_version.parse(c.version),
                reverse=True
            )
            latest_comp = sorted_components[0]
        except Exception:
            # If version parsing fails, just use the first component
            latest_comp = matching_components[0]

        root_url = str(Path(url).parent)
        manifest_url = f"{root_url}/{latest_comp.manifest_path}"
        return manifest_url

    # ------------------------------------------------------------------
    # Manifest helpers
    # ------------------------------------------------------------------

    def fetch_manifest(self, manifest_url: str) -> ComponentManifest:
        console.log(f"Fetching component manifest from {manifest_url}")
        resp = self._client.get(manifest_url)
        resp.raise_for_status()
        data = resp.json()
        return ComponentManifest.model_validate(data)

    # ------------------------------------------------------------------
    # Files
    # ------------------------------------------------------------------

    def download_file(self, url: str, dest_path: Path) -> None:
        console.log(f"Downloading {url} -> {dest_path}")
        resp = self._client.get(url)
        resp.raise_for_status()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(resp.content)

    def close(self) -> None:
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
