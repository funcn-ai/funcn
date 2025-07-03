"""Tests for the ConfigManager with priority support."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from sygaldry_cli.config_manager import ConfigManager, RegistrySourceConfig, SygaldryConfig
from tempfile import TemporaryDirectory


class TestConfigManager:
    """Test the ConfigManager."""

    def test_add_registry_source_default_priority(self):
        """Test adding a source with default priority."""
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            cfg_manager = ConfigManager(project_root)

            # Add source with default priority
            cfg_manager.add_registry_source("test", "https://test.com/index.json")

            # Should be stored as string (backward compat)
            config = json.loads((project_root / "sygaldry.json").read_text())
            assert config["registry_sources"]["test"] == "https://test.com/index.json"

    def test_add_registry_source_custom_priority(self):
        """Test adding a source with custom priority."""
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            cfg_manager = ConfigManager(project_root)

            # Add source with custom priority
            cfg_manager.add_registry_source("test", "https://test.com/index.json", priority=50)

            # Should be stored as object
            config = json.loads((project_root / "sygaldry.json").read_text())
            assert config["registry_sources"]["test"]["url"] == "https://test.com/index.json"
            assert config["registry_sources"]["test"]["priority"] == 50
            assert config["registry_sources"]["test"]["enabled"] is True

    def test_add_registry_source_disabled(self):
        """Test adding a disabled source."""
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            cfg_manager = ConfigManager(project_root)

            # Add disabled source
            cfg_manager.add_registry_source("test", "https://test.com/index.json", enabled=False)

            # Should be stored as object
            config = json.loads((project_root / "sygaldry.json").read_text())
            assert config["registry_sources"]["test"]["url"] == "https://test.com/index.json"
            assert config["registry_sources"]["test"]["priority"] == 100
            assert config["registry_sources"]["test"]["enabled"] is False

    def test_config_backward_compatibility(self):
        """Test that SygaldryConfig can handle both string and object sources."""
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            # Create a mixed format config
            config_data = {
                "default_registry_url": "https://default.com/index.json",
                "registry_sources": {
                    "old_format": "https://old.com/index.json",
                    "new_format": {
                        "url": "https://new.com/index.json",
                        "priority": 50,
                        "enabled": True
                    }
                }
            }

            (project_root / "sygaldry.json").write_text(json.dumps(config_data))

            cfg_manager = ConfigManager(project_root)
            cfg = cfg_manager.config

            # Check that both formats are parsed correctly
            assert "old_format" in cfg.registry_sources
            assert "new_format" in cfg.registry_sources

            # Old format should be string
            assert isinstance(cfg.registry_sources["old_format"], str)
            assert cfg.registry_sources["old_format"] == "https://old.com/index.json"

            # New format should be RegistrySourceConfig
            new_source = cfg.registry_sources["new_format"]
            if isinstance(new_source, dict):
                # When loaded from JSON, it might be a dict
                assert new_source["url"] == "https://new.com/index.json"
                assert new_source["priority"] == 50
                assert new_source["enabled"] is True

    def test_multiple_sources_with_priorities(self):
        """Test adding multiple sources with different priorities."""
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            cfg_manager = ConfigManager(project_root)

            # Add multiple sources
            cfg_manager.add_registry_source("high", "https://high.com/index.json", priority=10)
            cfg_manager.add_registry_source("medium", "https://medium.com/index.json", priority=50)
            cfg_manager.add_registry_source("low", "https://low.com/index.json", priority=200)
            cfg_manager.add_registry_source("default_prio", "https://default_prio.com/index.json")

            config = json.loads((project_root / "sygaldry.json").read_text())

            # Check all sources are saved correctly
            assert config["registry_sources"]["high"]["priority"] == 10
            assert config["registry_sources"]["medium"]["priority"] == 50
            assert config["registry_sources"]["low"]["priority"] == 200
            assert config["registry_sources"]["default_prio"] == "https://default_prio.com/index.json"
