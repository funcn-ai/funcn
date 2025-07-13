from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console
from typing import Any

console = Console()

CONFIG_ENV_VAR = "SYGALDRY_CONFIG_FILE"
PROJECT_CONFIG_FILENAME = "sygaldry.json"
DEFAULT_REGISTRY_URL = "https://raw.githubusercontent.com/greyhaven-ai/sygaldry/main/packages/sygaldry_registry/index.json"


class ComponentPaths(BaseModel):
    agents: str = "src/ai_agents"
    tools: str = "src/ai_tools"


class RegistrySourceConfig(BaseModel):
    url: str
    priority: int = 100  # Lower number = higher priority
    enabled: bool = True


class CacheConfig(BaseModel):
    """Configuration for caching behavior."""
    enabled: bool = True
    ttl_seconds: int = 3600  # 1 hour default
    max_size_mb: int = 100
    directory: str | None = None  # None = use default platform directory


class SygaldryConfig(BaseModel):
    default_registry_url: str = DEFAULT_REGISTRY_URL
    registry_sources: Mapping[str, str | RegistrySourceConfig] = Field(default_factory=lambda: {"default": DEFAULT_REGISTRY_URL})
    component_paths: ComponentPaths = Field(default_factory=ComponentPaths)
    default_provider: str = Field(default="openai")
    default_model: str = Field(default="gpt-4o-mini")
    stream: bool = Field(default=False)
    default_mcp_host: str = Field(default="0.0.0.0")
    default_mcp_port: int = Field(default=8000)
    cache_config: CacheConfig = Field(default_factory=CacheConfig)

    model_config = ConfigDict(extra="ignore")


class ConfigManager:
    """Loads and persists sygaldry configuration."""

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._project_cfg = self._load_json(self._project_config_path)

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------

    @property
    def config(self) -> SygaldryConfig:
        # Convert from init format if needed
        cfg = self._normalize_config(self._project_cfg)
        return SygaldryConfig.model_validate(cfg)

    @property
    def project_root(self) -> Path:
        return self._project_root

    @property
    def _project_config_path(self) -> Path:
        custom_path = os.getenv(CONFIG_ENV_VAR)
        if custom_path:
            return Path(custom_path).expanduser()
        return self._project_root / PROJECT_CONFIG_FILENAME

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            console.print(f"[red]Error parsing configuration file {path}: {exc}")
            return {}

    @staticmethod
    def _save_json(data: Mapping[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=4))

    # ------------------------------------------------------------------
    # Mutating helpers
    # ------------------------------------------------------------------

    def add_registry_source(self, alias: str, url: str, priority: int = 100, enabled: bool = True) -> None:
        # Reload the config from disk first to preserve existing data
        self._project_cfg = self._load_json(self._project_config_path)
        sources = self._project_cfg.setdefault("registry_sources", {})

        # Support both string (backward compat) and object format
        if priority == 100 and enabled:
            # Use simple string format for default values (backward compat)
            sources[alias] = url
        else:
            # Use object format when non-default values are provided
            sources[alias] = {
                "url": url,
                "priority": priority,
                "enabled": enabled
            }

        self._save_json(self._project_cfg, self._project_config_path)

    def remove_registry_source(self, alias: str) -> None:
        # Reload the config from disk first to preserve existing data
        self._project_cfg = self._load_json(self._project_config_path)
        if "registry_sources" in self._project_cfg and alias in self._project_cfg["registry_sources"]:
            del self._project_cfg["registry_sources"][alias]
            self._save_json(self._project_cfg, self._project_config_path)

    def set_default_registry(self, url: str) -> None:
        self._project_cfg["default_registry_url"] = url
        self.add_registry_source("default", url)

    # ------------------------------------------------------------------
    # Format conversion helpers
    # ------------------------------------------------------------------

    def _normalize_config(self, cfg: dict[str, Any]) -> dict[str, Any]:
        """Convert sygaldry.json init format to SygaldryConfig format."""
        # Start with a copy of the original config to preserve all fields
        normalized = cfg.copy()

        # If it already has new format fields, just ensure consistency
        if "component_paths" in cfg:
            return normalized

        # Convert from init format to new format
        # Map directory paths to component_paths
        if "agentDirectory" in cfg or "toolDirectory" in cfg:
            component_paths = {}
            if "agentDirectory" in cfg:
                component_paths["agents"] = cfg["agentDirectory"]
                del normalized["agentDirectory"]
            if "toolDirectory" in cfg:
                component_paths["tools"] = cfg["toolDirectory"]
                del normalized["toolDirectory"]
            if "evalDirectory" in cfg:
                component_paths["evals"] = cfg["evalDirectory"]
                del normalized["evalDirectory"]
            if "promptTemplateDirectory" in cfg:
                component_paths["prompts"] = cfg["promptTemplateDirectory"]
                del normalized["promptTemplateDirectory"]
            if "responseModelDirectory" in cfg:
                component_paths["response_models"] = cfg["responseModelDirectory"]
                del normalized["responseModelDirectory"]
            normalized["component_paths"] = component_paths

        # Map other fields from old to new names
        if "defaultProvider" in cfg:
            normalized["default_provider"] = cfg["defaultProvider"]
            del normalized["defaultProvider"]
        if "defaultModel" in cfg:
            normalized["default_model"] = cfg["defaultModel"]
            del normalized["defaultModel"]
        if "defaultMcpHost" in cfg:
            normalized["default_mcp_host"] = cfg["defaultMcpHost"]
            del normalized["defaultMcpHost"]
        if "defaultMcpPort" in cfg:
            normalized["default_mcp_port"] = cfg["defaultMcpPort"]
            del normalized["defaultMcpPort"]

        # Remove fields that aren't part of SygaldryConfig
        normalized.pop("aliases", None)
        normalized.pop("$schema", None)

        return normalized
