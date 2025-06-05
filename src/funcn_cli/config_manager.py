from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console
from typing import Any

console = Console()

CONFIG_ENV_VAR = "FUNCN_CONFIG_FILE"
GLOBAL_CONFIG_DIR = Path.home() / ".config" / "funcn"
GLOBAL_CONFIG_PATH = GLOBAL_CONFIG_DIR / "config.json"
PROJECT_CONFIG_FILENAME = ".funcnrc.json"
DEFAULT_REGISTRY_URL = "https://raw.githubusercontent.com/greyhaven-ai/funcn_registry/main/index.json"


class ComponentPaths(BaseModel):
    agents: str = "src/ai_agents"
    tools: str = "src/ai_tools"


class FuncnConfig(BaseModel):
    default_registry_url: str = DEFAULT_REGISTRY_URL
    registry_sources: Mapping[str, str] = {"default": DEFAULT_REGISTRY_URL}
    component_paths: ComponentPaths = Field(default_factory=ComponentPaths)
    default_provider: str = Field(default="openai")
    default_model: str = Field(default="gpt-4o-mini")
    stream: bool = Field(default=False)
    default_mcp_host: str = Field(default="0.0.0.0")
    default_mcp_port: int = Field(default=8000)

    model_config = ConfigDict(extra="ignore")


class ConfigManager:
    """Loads and persists funcn configuration."""

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._global_cfg = self._load_json(GLOBAL_CONFIG_PATH)
        self._project_cfg = self._load_json(self._project_config_path)

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------

    @property
    def config(self) -> FuncnConfig:
        cfg = {**self._global_cfg, **self._project_cfg}
        return FuncnConfig.model_validate(cfg)

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

    def add_registry_source(self, alias: str, url: str, project_level: bool = True) -> None:
        target_cfg = self._project_cfg if project_level else self._global_cfg
        target_cfg.setdefault("registry_sources", {})[alias] = url
        if project_level:
            self._save_json(self._project_cfg, self._project_config_path)
        else:
            self._save_json(self._global_cfg, GLOBAL_CONFIG_PATH)

    def set_default_registry(self, url: str, project_level: bool = True) -> None:
        target_cfg = self._project_cfg if project_level else self._global_cfg
        target_cfg["default_registry_url"] = url
        self.add_registry_source("default", url, project_level=project_level)
