"""Utility functions for funcn CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_funcn_config(project_root: Path) -> dict[str, Any]:
    """Load funcn.json configuration from project root."""
    funcn_config_path = project_root / "funcn.json"

    if not funcn_config_path.exists():
        return {}

    try:
        with open(funcn_config_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}
