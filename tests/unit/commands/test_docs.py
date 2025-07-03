"""Tests for the sygaldry docs command."""

from __future__ import annotations

import json
import os
import pytest
import typer
from pathlib import Path
from sygaldry_cli.commands.docs import (
    EDITOR_CONFIGS,
    _discover_all_components,
    _discover_components_by_type,
    _find_component_path,
    _generate_all_docs,
    _generate_component_docs,
    _generate_component_sygaldry_md,
    _generate_docs_by_type,
    _generate_global_editor_rules,
    _generate_sygaldry_md_template,
    generate,
    template,
    types,
)
from unittest.mock import MagicMock, call, mock_open, patch


class TestDocs:
    """Test the sygaldry docs command and its subcommands."""

    @pytest.fixture
    def mock_console(self, mocker):
        """Mock console output."""
        return mocker.patch("sygaldry_cli.commands.docs.console")

    @pytest.fixture
    def tmp_registry(self, tmp_path):
        """Create a temporary registry structure."""
        registry_path = tmp_path / "packages" / "sygaldry_registry" / "components"
        registry_path.mkdir(parents=True)

        # Create agent component
        agent_dir = registry_path / "agents" / "test_agent"
        agent_dir.mkdir(parents=True)
        agent_data = {
            "name": "test_agent",
            "version": "1.0.0",
            "type": "agent",
            "description": "Test agent",
            "authors": [{"name": "Test"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": [],
            "target_directory_key": "agents",
            "python_dependencies": [],
            "registry_dependencies": [],
            "environment_variables": [],
        }
        (agent_dir / "component.json").write_text(json.dumps(agent_data, indent=2))
        (agent_dir / "README.md").write_text("# Test Agent\n\nThis is a test agent.")

        # Create tool component
        tool_dir = registry_path / "tools" / "test_tool"
        tool_dir.mkdir(parents=True)
        tool_data = {
            "name": "test_tool",
            "version": "1.0.0",
            "type": "tool",
            "description": "Test tool",
            "authors": [{"name": "Test"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": [],
            "target_directory_key": "tools",
            "python_dependencies": [],
            "registry_dependencies": [],
            "environment_variables": [],
        }
        (tool_dir / "component.json").write_text(json.dumps(tool_data, indent=2))

        return tmp_path

    def test_generate_unknown_editor(self, mock_console):
        """Test generate with unknown editor."""
        with pytest.raises(typer.Exit) as exc_info:
            generate(editor="unknown", component=None, output_dir=None, component_type=None, force_regenerate=False)

        assert exc_info.value.exit_code == 1
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Unknown editor 'unknown'" in call for call in console_calls)

    def test_generate_specific_component(self, mock_console, tmp_registry, mocker):
        """Test generating docs for a specific component."""
        # Mock the internal functions
        mock_find = mocker.patch("sygaldry_cli.commands.docs._find_component_path")
        mock_find.return_value = tmp_registry / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent"

        mock_gen_sygaldry = mocker.patch("sygaldry_cli.commands.docs._generate_component_sygaldry_md")
        mock_gen_editor = mocker.patch("sygaldry_cli.commands.docs._generate_editor_rules_for_component")

        # Change working directory to tmp_registry
        with patch("sygaldry_cli.commands.docs.Path.cwd", return_value=tmp_registry):
            generate(
                editor="cursor", component="test_agent", output_dir=None, component_type=None, force_regenerate=False
            )

        # Verify calls
        mock_find.assert_called_once_with("test_agent")
        assert mock_gen_sygaldry.called
        assert mock_gen_editor.called

    def test_generate_by_type(self, mock_console, tmp_registry, mocker):
        """Test generating docs for all components of a type."""
        # Mock internal functions
        mock_gen_by_type = mocker.patch("sygaldry_cli.commands.docs._generate_docs_by_type")

        generate(editor="cursor", component=None, output_dir=None, component_type="agent", force_regenerate=False)

        mock_gen_by_type.assert_called_once_with("agent", "cursor", None, False)

    def test_generate_all_docs(self, mock_console, tmp_registry, mocker):
        """Test generating all documentation."""
        # Mock internal functions
        mock_gen_all = mocker.patch("sygaldry_cli.commands.docs._generate_all_docs")

        generate(editor="cursor", component=None, output_dir=None, component_type=None, force_regenerate=False)

        mock_gen_all.assert_called_once_with("cursor", None, False)

    def test_template_command(self, mock_console, mocker):
        """Test template generation command."""
        mock_gen_template = mocker.patch("sygaldry_cli.commands.docs._generate_sygaldry_md_template")

        template(component_name="my_component", output_file="output.md")

        mock_gen_template.assert_called_once_with("my_component", "output.md")

    def test_template_command_default_output(self, mock_console, mocker):
        """Test template generation with default output."""
        mock_gen_template = mocker.patch("sygaldry_cli.commands.docs._generate_sygaldry_md_template")

        template(component_name="my_component", output_file=None)

        mock_gen_template.assert_called_once_with("my_component", None)

    def test_types_command(self, mock_console, mocker):
        """Test types command."""
        # Mock the import
        mock_templates = {"agent": {}, "tool": {}, "prompt_template": {}}
        mocker.patch.dict("sygaldry_cli.templates.component_type_templates.COMPONENT_TYPE_TEMPLATES", mock_templates)

        types()

        # Verify console output
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Available component types" in call for call in console_calls)
        assert any("agent" in call for call in console_calls)
        assert any("tool" in call for call in console_calls)

    def test_find_component_path(self, tmp_registry, mocker):
        """Test finding component path."""
        # Change to the tmp directory so relative paths work
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_registry)

            # Test finding by directory name
            path = _find_component_path("test_agent")
            assert path is not None
            assert path.name == "test_agent"

            # Test not found
            path = _find_component_path("nonexistent")
            assert path is None
        finally:
            os.chdir(original_cwd)

    def test_discover_all_components(self, tmp_registry):
        """Test discovering all components."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_registry)
            components = _discover_all_components()

            assert len(components) == 2
            names = [comp[1]["name"] for comp in components]
            assert "test_agent" in names
            assert "test_tool" in names
        finally:
            os.chdir(original_cwd)

    def test_discover_components_by_type(self, tmp_registry):
        """Test discovering components by type."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_registry)
            # Find agents
            agents = _discover_components_by_type("agent")
            assert len(agents) == 1
            assert agents[0][1]["name"] == "test_agent"

            # Find tools
            tools = _discover_components_by_type("tool")
            assert len(tools) == 1
            assert tools[0][1]["name"] == "test_tool"

            # Find non-existent type
            others = _discover_components_by_type("nonexistent")
            assert len(others) == 0
        finally:
            os.chdir(original_cwd)

    def test_generate_component_sygaldry_md_new_file(self, mock_console, tmp_registry, mocker):
        """Test generating sygaldry.md for a component without existing file."""
        # Mock template functions
        mock_gen = mocker.patch("sygaldry_cli.templates.sygaldry_md_template.generate_sygaldry_md")
        mock_gen.return_value = "# Generated sygaldry.md content"

        component_path = tmp_registry / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent"
        component_data = {"name": "test_agent", "type": "agent"}

        _generate_component_sygaldry_md(component_data, component_path, force_regenerate=False)

        # Verify sygaldry.md was created
        sygaldry_md_path = component_path / "sygaldry.md"
        assert sygaldry_md_path.exists()
        assert sygaldry_md_path.read_text() == "# Generated sygaldry.md content"

    def test_generate_component_sygaldry_md_existing_file(self, mock_console, tmp_registry, mocker):
        """Test generating sygaldry.md with existing file and merge."""
        # Create existing sygaldry.md
        component_path = tmp_registry / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent"
        sygaldry_md_path = component_path / "sygaldry.md"
        sygaldry_md_path.write_text("# Existing content\n\nUser customizations here.")

        # Mock template functions
        mock_gen = mocker.patch("sygaldry_cli.templates.sygaldry_md_template.generate_sygaldry_md")
        mock_gen.return_value = "# New generated content"

        mock_merge = mocker.patch("sygaldry_cli.templates.sygaldry_md_template.merge_with_existing_sygaldry_md")
        mock_merge.return_value = "# Merged content"

        component_data = {"name": "test_agent", "type": "agent"}

        _generate_component_sygaldry_md(component_data, component_path, force_regenerate=False)

        # Verify merge was called
        assert mock_merge.called
        assert sygaldry_md_path.read_text() == "# Merged content"

    def test_generate_component_sygaldry_md_force_regenerate(self, mock_console, tmp_registry, mocker):
        """Test force regenerate overwrites existing content."""
        # Create existing sygaldry.md
        component_path = tmp_registry / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent"
        sygaldry_md_path = component_path / "sygaldry.md"
        sygaldry_md_path.write_text("# Existing content")

        # Mock template functions
        mock_gen = mocker.patch("sygaldry_cli.templates.sygaldry_md_template.generate_sygaldry_md")
        mock_gen.return_value = "# New generated content"

        component_data = {"name": "test_agent", "type": "agent"}

        _generate_component_sygaldry_md(component_data, component_path, force_regenerate=True)

        # Verify content was overwritten
        assert sygaldry_md_path.read_text() == "# New generated content"

    def test_generate_global_editor_rules(self, mock_console, tmp_registry, mocker):
        """Test generating global editor rules."""
        # Mock template function
        mock_gen_rules = mocker.patch("sygaldry_cli.templates.editor_rules.generate_editor_rules")
        mock_gen_rules.return_value = "# Editor rules content"

        components = [
            (Path("path1"), {"name": "comp1", "type": "agent"}),
            (Path("path2"), {"name": "comp2", "type": "tool"}),
        ]

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_registry)
            _generate_global_editor_rules(components, "cursor", None)

            # Verify file was created
            cursor_rules_path = tmp_registry / ".cursor" / "rules" / "sygaldry.mdc"
            assert cursor_rules_path.exists()
            assert cursor_rules_path.read_text() == "# Editor rules content"
        finally:
            os.chdir(original_cwd)

    def test_generate_docs_by_type_unknown_type(self, mock_console, mocker):
        """Test generating docs by unknown type."""
        mock_templates = {"agent": {}, "tool": {}}
        mocker.patch.dict("sygaldry_cli.templates.component_type_templates.COMPONENT_TYPE_TEMPLATES", mock_templates)

        with pytest.raises(typer.Exit) as exc_info:
            _generate_docs_by_type("unknown_type", "cursor", None, False)

        assert exc_info.value.exit_code == 1
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Unknown component type 'unknown_type'" in call for call in console_calls)

    def test_generate_docs_by_type_no_components(self, mock_console, tmp_registry, mocker):
        """Test generating docs when no components of type exist."""
        mock_templates = {"agent": {}, "tool": {}, "eval": {}}
        mocker.patch.dict("sygaldry_cli.templates.component_type_templates.COMPONENT_TYPE_TEMPLATES", mock_templates)

        with patch("sygaldry_cli.commands.docs.Path.cwd", return_value=tmp_registry):
            _generate_docs_by_type("eval", "cursor", None, False)

        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("No components of type 'eval' found" in call for call in console_calls)

    def test_generate_sygaldry_md_template_custom_output(self, mock_console, tmp_path, mocker):
        """Test generating sygaldry.md template with custom output."""
        mock_gen = mocker.patch("sygaldry_cli.templates.sygaldry_md_template.generate_template_sygaldry_md")
        mock_gen.return_value = "# Template content"

        output_file = tmp_path / "custom.md"

        _generate_sygaldry_md_template("my_component", str(output_file))

        assert output_file.exists()
        assert output_file.read_text() == "# Template content"

    def test_editor_configs_structure(self):
        """Test that EDITOR_CONFIGS has expected structure."""
        required_editors = ["cursor", "windsurf", "cline", "claude", "sourcegraph", "openai_codex", "amp_code"]

        for editor in required_editors:
            assert editor in EDITOR_CONFIGS
            config = EDITOR_CONFIGS[editor]
            assert "files" in config
            assert "format" in config
            assert isinstance(config["files"], list)
            assert len(config["files"]) > 0

    def test_generate_all_docs_integration(self, mock_console, tmp_registry, mocker):
        """Test full integration of generate all docs."""
        # Mock template functions
        mock_gen_sygaldry = mocker.patch("sygaldry_cli.templates.sygaldry_md_template.generate_sygaldry_md")
        mock_gen_sygaldry.return_value = "# Generated content"

        mock_gen_rules = mocker.patch("sygaldry_cli.templates.editor_rules.generate_editor_rules")
        mock_gen_rules.return_value = "# Rules content"

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_registry)
            _generate_all_docs("claude", None, False)

            # Verify sygaldry.md files were created
            agent_sygaldry = (
                tmp_registry / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent" / "sygaldry.md"
            )
            tool_sygaldry = tmp_registry / "packages" / "sygaldry_registry" / "components" / "tools" / "test_tool" / "sygaldry.md"
            assert agent_sygaldry.exists()
            assert tool_sygaldry.exists()

            # Verify CLAUDE.md was created
            claude_md = tmp_registry / "CLAUDE.md"
            assert claude_md.exists()
        finally:
            os.chdir(original_cwd)
