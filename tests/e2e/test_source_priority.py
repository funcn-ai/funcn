"""E2E tests for source priority functionality."""

from __future__ import annotations

import json
import os
import pytest
from pathlib import Path
from sygaldry_cli.main import app
from tempfile import TemporaryDirectory
from typer.testing import CliRunner
from typing import Any


class TestSourcePriority:
    """E2E tests for source priority and fallback functionality."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with sygaldry.json."""
        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)

            # Create initial sygaldry.json
            sygaldry_config = {
                "default_registry_url": "https://raw.githubusercontent.com/sygaldry-ai/sygaldry-registry/main/index.json",
                "registry_sources": {
                    "default": "https://raw.githubusercontent.com/sygaldry-ai/sygaldry-registry/main/index.json"
                },
                "component_paths": {
                    "agents": "src/agents",
                    "tools": "src/tools"
                }
            }

            (project_dir / "sygaldry.json").write_text(json.dumps(sygaldry_config, indent=2))
            yield project_dir

    def run_command(self, runner: CliRunner, command: list[str], cwd: Path = None) -> Any:
        """Run a CLI command and return the result."""
        if cwd:
            original_cwd = Path.cwd()
            try:
                os.chdir(cwd)
                result = runner.invoke(app, command)
                return result
            finally:
                os.chdir(original_cwd)
        else:
            result = runner.invoke(app, command)
            return result

    def test_add_source_with_priority(self, runner, temp_project):
        """Test adding sources with different priorities."""
        # Change to project directory
        result = self.run_command(runner, ["source", "add", "high-priority", "https://high.com/index.json", "--priority", "10", "--skip-check"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Added registry source 'high-priority'" in result.output
        assert "(priority: 10)" in result.output

        # Add another source with default priority
        result = self.run_command(runner, ["source", "add", "normal", "https://normal.com/index.json", "--skip-check"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Added registry source 'normal'" in result.output
        assert "(priority:" not in result.output  # Default priority not shown

        # Verify config file
        config = json.loads((temp_project / "sygaldry.json").read_text())
        assert config["registry_sources"]["high-priority"]["url"] == "https://high.com/index.json"
        assert config["registry_sources"]["high-priority"]["priority"] == 10
        assert config["registry_sources"]["normal"] == "https://normal.com/index.json"  # String format for default

    def test_list_sources_shows_priority_order(self, runner, temp_project):
        """Test that list command shows sources in priority order."""
        # Add sources with different priorities
        self.run_command(runner, ["source", "add", "low-prio", "https://low.com/index.json", "--priority", "200", "--skip-check"], cwd=temp_project)
        self.run_command(runner, ["source", "add", "high-prio", "https://high.com/index.json", "--priority", "10", "--skip-check"], cwd=temp_project)
        self.run_command(runner, ["source", "add", "medium-prio", "https://medium.com/index.json", "--priority", "50", "--skip-check"], cwd=temp_project)

        # List sources
        result = self.run_command(runner, ["source", "list"], cwd=temp_project)
        assert result.exit_code == 0

        # Verify order in output (sources should be sorted by priority)
        lines = result.output.split('\n')
        indices = {}
        for i, line in enumerate(lines):
            if "high-prio" in line:
                indices["high"] = i
            elif "medium-prio" in line:
                indices["medium"] = i
            elif "default" in line:
                indices["default"] = i
            elif "low-prio" in line:
                indices["low"] = i

        # High priority should appear before medium, medium before default, default before low
        assert indices["high"] < indices["medium"]
        assert indices["medium"] < indices["default"]
        assert indices["default"] < indices["low"]

    def test_mixed_format_compatibility(self, runner, temp_project):
        """Test that old string format and new object format work together."""
        # Manually create a mixed format config
        config = {
            "default_registry_url": "https://raw.githubusercontent.com/sygaldry-ai/sygaldry-registry/main/index.json",
            "registry_sources": {
                "default": "https://raw.githubusercontent.com/sygaldry-ai/sygaldry-registry/main/index.json",
                "old_format": "https://old.com/index.json",
                "new_format": {
                    "url": "https://new.com/index.json",
                    "priority": 50,
                    "enabled": True
                },
                "disabled": {
                    "url": "https://disabled.com/index.json",
                    "priority": 20,
                    "enabled": False
                }
            },
            "component_paths": {
                "agents": "src/agents",
                "tools": "src/tools"
            }
        }

        (temp_project / "sygaldry.json").write_text(json.dumps(config, indent=2))

        # List sources
        result = self.run_command(runner, ["source", "list"], cwd=temp_project)
        assert result.exit_code == 0

        # Old format should show with default priority
        assert "old_format" in result.output
        assert "100" in result.output  # Default priority

        # New format should show custom priority
        assert "new_format" in result.output
        assert "50" in result.output

        # Disabled source should show as disabled
        assert "disabled" in result.output
        assert "disabled" in result.output.lower()

    def test_priority_zero_allowed(self, runner, temp_project):
        """Test that priority 0 is allowed (highest priority)."""
        result = self.run_command(runner, ["source", "add", "top", "https://top.com/index.json", "--priority", "0", "--skip-check"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Added registry source 'top'" in result.output
        assert "(priority: 0)" in result.output

        # Verify in config
        config = json.loads((temp_project / "sygaldry.json").read_text())
        assert config["registry_sources"]["top"]["priority"] == 0

    def test_negative_priority_allowed(self, runner, temp_project):
        """Test that negative priorities are allowed."""
        result = self.run_command(runner, ["source", "add", "urgent", "https://urgent.com/index.json", "--priority", "-10", "--skip-check"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Added registry source 'urgent'" in result.output
        # Check for priority in output (might have newline in between)
        assert "priority:" in result.output
        assert "-10" in result.output

        # Verify in config
        config = json.loads((temp_project / "sygaldry.json").read_text())
        assert config["registry_sources"]["urgent"]["priority"] == -10
