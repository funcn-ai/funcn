"""Tests for the funcn build command."""

from __future__ import annotations

import json
import pytest
import typer
from funcn_cli.commands.build_cmd import build
from pathlib import Path
from unittest.mock import MagicMock, call


class TestBuild:
    """Test the funcn build command."""

    @pytest.fixture
    def mock_console(self, mocker):
        """Mock console output."""
        return mocker.patch("funcn_cli.commands.build_cmd.console")

    @pytest.fixture
    def tmp_project(self, tmp_path):
        """Create a temporary project structure."""
        # Create default registry structure
        registry_dir = tmp_path / "packages" / "funcn_registry"
        registry_dir.mkdir(parents=True)
        
        # Create component manifests
        agents_dir = registry_dir / "src" / "agents"
        agents_dir.mkdir(parents=True)
        
        tools_dir = registry_dir / "src" / "tools"
        tools_dir.mkdir(parents=True)
        
        # Create sample component manifests
        text_agent_manifest = {
            "name": "text_summarization_agent",
            "version": "1.0.0",
            "type": "agent",
            "description": "Advanced text summarization agent",
            "authors": [{"name": "Test Author"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": [],
            "target_directory_key": "agents",
            "python_dependencies": [],
            "registry_dependencies": [],
            "environment_variables": []
        }
        
        search_tool_manifest = {
            "name": "duckduckgo_search_tool",
            "version": "1.0.0",
            "type": "tool",
            "description": "DuckDuckGo web search tools",
            "authors": [{"name": "Test Author"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": [],
            "target_directory_key": "tools",
            "python_dependencies": ["duckduckgo-search"],
            "registry_dependencies": [],
            "environment_variables": []
        }
        
        # Write manifest files
        text_agent_dir = agents_dir / "text_summarization_agent"
        text_agent_dir.mkdir()
        (text_agent_dir / "component.json").write_text(json.dumps(text_agent_manifest, indent=2))
        
        search_tool_dir = tools_dir / "duckduckgo_search_tool"
        search_tool_dir.mkdir()
        (search_tool_dir / "component.json").write_text(json.dumps(search_tool_manifest, indent=2))
        
        # Create registry index
        registry_index = {
            "registry_version": "1.0.0",
            "components": [
                {
                    "name": "text_summarization_agent",
                    "version": "1.0.0",
                    "type": "agent",
                    "description": "Advanced text summarization agent",
                    "manifest_path": "src/agents/text_summarization_agent/component.json"
                },
                {
                    "name": "duckduckgo_search_tool",
                    "version": "1.0.0",
                    "type": "tool",
                    "description": "DuckDuckGo web search tools",
                    "manifest_path": "src/tools/duckduckgo_search_tool/component.json"
                }
            ]
        }
        
        (registry_dir / "index.json").write_text(json.dumps(registry_index, indent=2))
        
        return tmp_path

    def test_build_default_paths(self, mock_console, tmp_project):
        """Test build with default registry and output paths."""
        ctx = typer.Context(command=MagicMock())
        
        # Execute build
        build(ctx, registry=None, output="./public/r", cwd=tmp_project)
        
        # Verify output directory was created
        output_dir = tmp_project / "public" / "r"
        assert output_dir.exists()
        
        # Verify component files were created
        assert (output_dir / "text_summarization_agent.json").exists()
        assert (output_dir / "duckduckgo_search_tool.json").exists()
        assert (output_dir / "index.json").exists()
        
        # Verify content
        text_agent_data = json.loads((output_dir / "text_summarization_agent.json").read_text())
        assert text_agent_data["name"] == "text_summarization_agent"
        assert text_agent_data["version"] == "1.0.0"
        
        # Verify console output
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("text_summarization_agent.json" in call for call in console_calls)
        assert any("duckduckgo_search_tool.json" in call for call in console_calls)
        assert any("Build complete!" in call for call in console_calls)
        assert any("Generated 2 manifest(s)" in call for call in console_calls)

    def test_build_custom_registry_path(self, mock_console, tmp_project):
        """Test build with custom registry path."""
        ctx = typer.Context(command=MagicMock())
        
        # Create custom registry location
        custom_registry = tmp_project / "custom" / "registry.json"
        custom_registry.parent.mkdir(parents=True)
        
        registry_data = {
            "registry_version": "1.0.0",
            "components": [
                {
                    "name": "custom_component",
                    "version": "1.0.0",
                    "type": "agent",
                    "description": "Custom component",
                    "manifest_path": "component.json"
                }
            ]
        }
        custom_registry.write_text(json.dumps(registry_data, indent=2))
        
        # Create manifest
        manifest_data = {
            "name": "custom_component",
            "version": "1.0.0",
            "type": "agent",
            "description": "Custom component",
            "authors": [{"name": "Test"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": [],
            "target_directory_key": "agents",
            "python_dependencies": [],
            "registry_dependencies": [],
            "environment_variables": []
        }
        (custom_registry.parent / "component.json").write_text(json.dumps(manifest_data, indent=2))
        
        # Execute build
        build(ctx, registry=str(custom_registry), output="./output", cwd=tmp_project)
        
        # Verify output
        output_dir = tmp_project / "output"
        assert (output_dir / "custom_component.json").exists()

    def test_build_absolute_paths(self, mock_console, tmp_project):
        """Test build with absolute paths."""
        ctx = typer.Context(command=MagicMock())
        
        # Use absolute paths
        registry_path = tmp_project / "packages" / "funcn_registry" / "index.json"
        output_path = tmp_project / "custom_output"
        
        # Execute build
        build(ctx, registry=str(registry_path), output=str(output_path), cwd=None)
        
        # Verify output
        assert output_path.exists()
        assert (output_path / "text_summarization_agent.json").exists()

    def test_build_missing_registry_file(self, mock_console, tmp_project):
        """Test build with missing registry file."""
        ctx = typer.Context(command=MagicMock())
        
        # Use non-existent registry
        with pytest.raises(typer.Exit) as exc_info:
            build(ctx, registry="nonexistent.json", output="./output", cwd=tmp_project)
        
        assert exc_info.value.exit_code == 1
        
        # Verify error message
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Registry file not found:" in call for call in console_calls)

    def test_build_invalid_json(self, mock_console, tmp_project):
        """Test build with invalid JSON in registry file."""
        ctx = typer.Context(command=MagicMock())
        
        # Create invalid JSON file
        invalid_registry = tmp_project / "invalid.json"
        invalid_registry.write_text("{ invalid json }")
        
        # Execute build
        with pytest.raises(typer.Exit) as exc_info:
            build(ctx, registry=str(invalid_registry), output="./output", cwd=tmp_project)
        
        assert exc_info.value.exit_code == 1
        
        # Verify error message
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Invalid JSON in registry file:" in call for call in console_calls)

    def test_build_empty_components(self, mock_console, tmp_project):
        """Test build with empty components list."""
        ctx = typer.Context(command=MagicMock())
        
        # Create registry with empty components
        empty_registry = tmp_project / "empty.json"
        empty_registry.write_text(json.dumps({"registry_version": "1.0.0", "components": []}, indent=2))
        
        # Execute build
        with pytest.raises(typer.Exit):
            build(ctx, registry=str(empty_registry), output="./output", cwd=tmp_project)
        
        # Verify warning message
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("No components found in registry file." in call for call in console_calls)

    def test_build_invalid_component_entry(self, mock_console, tmp_project):
        """Test build with invalid component entries."""
        ctx = typer.Context(command=MagicMock())
        
        # Create registry with invalid entries
        registry_data = {
            "registry_version": "1.0.0",
            "components": [
                {"name": "missing_manifest_path"},  # Missing manifest_path
                {"manifest_path": "some/path.json"},  # Missing name
                {
                    "name": "valid_component",
                    "manifest_path": "component.json"
                }
            ]
        }
        
        invalid_registry = tmp_project / "invalid_components.json"
        invalid_registry.write_text(json.dumps(registry_data, indent=2))
        
        # Create valid manifest
        manifest_data = {
            "name": "valid_component",
            "version": "1.0.0",
            "type": "agent",
            "description": "Valid component",
            "authors": [{"name": "Test"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": [],
            "target_directory_key": "agents",
            "python_dependencies": [],
            "registry_dependencies": [],
            "environment_variables": []
        }
        (invalid_registry.parent / "component.json").write_text(json.dumps(manifest_data, indent=2))
        
        # Execute build
        build(ctx, registry=str(invalid_registry), output="./output", cwd=tmp_project)
        
        # Verify warnings
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Skipping invalid component entry:" in call for call in console_calls)
        
        # Verify valid component was processed
        output_dir = tmp_project / "output"
        assert (output_dir / "valid_component.json").exists()

    def test_build_missing_manifest_file(self, mock_console, tmp_project):
        """Test build when manifest file doesn't exist."""
        ctx = typer.Context(command=MagicMock())
        
        # Create registry pointing to non-existent manifest
        registry_data = {
            "registry_version": "1.0.0",
            "components": [
                {
                    "name": "missing_component",
                    "manifest_path": "does/not/exist.json"
                }
            ]
        }
        
        registry_path = tmp_project / "registry.json"
        registry_path.write_text(json.dumps(registry_data, indent=2))
        
        # Execute build
        build(ctx, registry=str(registry_path), output="./output", cwd=tmp_project)
        
        # Verify warning
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Manifest not found for component 'missing_component':" in call for call in console_calls)

    def test_build_invalid_manifest_json(self, mock_console, tmp_project):
        """Test build with invalid JSON in manifest file."""
        ctx = typer.Context(command=MagicMock())
        
        # Create registry
        registry_data = {
            "registry_version": "1.0.0",
            "components": [
                {
                    "name": "invalid_manifest",
                    "manifest_path": "invalid.json"
                }
            ]
        }
        
        registry_path = tmp_project / "registry.json"
        registry_path.write_text(json.dumps(registry_data, indent=2))
        
        # Create invalid manifest
        (tmp_project / "invalid.json").write_text("{ invalid json }")
        
        # Execute build
        build(ctx, registry=str(registry_path), output="./output", cwd=tmp_project)
        
        # Verify warning
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Invalid manifest JSON for 'invalid_manifest':" in call for call in console_calls)

    def test_build_output_directory_creation(self, mock_console, tmp_project):
        """Test that output directory is created if it doesn't exist."""
        ctx = typer.Context(command=MagicMock())
        
        # Use nested output path that doesn't exist
        output_path = "./deeply/nested/output/dir"
        
        # Execute build
        build(ctx, registry=None, output=output_path, cwd=tmp_project)
        
        # Verify directory was created
        full_output_path = tmp_project / "deeply" / "nested" / "output" / "dir"
        assert full_output_path.exists()
        assert full_output_path.is_dir()

    def test_build_expanduser_paths(self, mock_console, tmp_project, mocker):
        """Test that ~ is expanded in paths."""
        ctx = typer.Context(command=MagicMock())
        
        # Mock expanduser to return tmp_project paths
        def mock_expanduser(self):
            if str(self).startswith("~"):
                return tmp_project / str(self)[2:]
            return self
        
        mocker.patch.object(Path, "expanduser", mock_expanduser)
        
        # Create registry at "home" location
        home_registry = tmp_project / "registry.json"
        home_registry.write_text(json.dumps({
            "registry_version": "1.0.0",
            "components": []
        }, indent=2))
        
        # Execute build with ~ paths
        with pytest.raises(typer.Exit):  # Will exit due to empty components
            build(ctx, registry="~/registry.json", output="~/output", cwd=tmp_project)
        
        # Verify expanduser was used
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("No components found" in call for call in console_calls)
