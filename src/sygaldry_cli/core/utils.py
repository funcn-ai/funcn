"""Utility functions for sygaldry CLI."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_sygaldry_config(project_root: Path) -> dict[str, Any]:
    """Load sygaldry.json configuration from project root."""
    sygaldry_config_path = project_root / "sygaldry.json"

    if not sygaldry_config_path.exists():
        return {}

    try:
        with open(sygaldry_config_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}
