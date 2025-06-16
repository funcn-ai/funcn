from __future__ import annotations

import httpx
from funcn_cli.config_manager import ConfigManager
from funcn_cli.core.models import ComponentManifest, RegistryIndex
from pathlib import Path
from rich.console import Console

console = Console()


class RegistryHandler:
    """Fetches registry indexes and component manifests."""

    def __init__(self, cfg: ConfigManager | None = None) -> None:
        self._cfg = cfg or ConfigManager()
        self._client = httpx.Client(timeout=30.0)

    # ------------------------------------------------------------------
    # Index helpers
    # ------------------------------------------------------------------

    def fetch_index(self, source_alias: str | None = None) -> RegistryIndex:
        url = self._cfg.config.registry_sources.get(source_alias, None) if source_alias else self._cfg.config.default_registry_url
        if not url:
            raise ValueError(f"No URL found for registry source: {source_alias}")
        console.log(f"Fetching registry index from {url}")
        resp = self._client.get(url)
        resp.raise_for_status()
        data = resp.json()
        return RegistryIndex.model_validate(data)

    def find_component_manifest_url(self, component_name: str, source_alias: str | None = None) -> str | None:
        """Find component manifest URL in the specified source or all sources."""
        if source_alias:
            # Search in specific source
            return self._search_single_source(component_name, source_alias)
        else:
            # Search in all sources, starting with default
            # Try default source first
            result = self._search_single_source(component_name, None)
            if result:
                return result
            
            # Try all other configured sources
            for alias in self._cfg.config.registry_sources:
                result = self._search_single_source(component_name, alias)
                if result:
                    console.print(f"[cyan]Found component '{component_name}' in source '{alias}'[/]")
                    return result
            return None
    
    def _search_single_source(self, component_name: str, source_alias: str | None) -> str | None:
        """Search for component in a single source."""
        try:
            index = self.fetch_index(source_alias=source_alias)
            url = self._cfg.config.registry_sources.get(source_alias) if source_alias else self._cfg.config.default_registry_url
            
            for comp in index.components:
                if comp.name == component_name:
                    root_url = str(Path(url).parent)
                    manifest_url = f"{root_url}/{comp.manifest_path}"
                    return manifest_url
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to search source '{source_alias or 'default'}': {e}[/]")
        return None

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
