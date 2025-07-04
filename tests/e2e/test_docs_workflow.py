"""End-to-end tests for sygaldry docs generation workflow."""

from __future__ import annotations

import json
import pytest
import shutil
from pathlib import Path
from tests.e2e.base import BaseE2ETest


@pytest.mark.e2e
class TestDocsWorkflow(BaseE2ETest):
    """Test documentation generation workflows."""

    @pytest.fixture
    def registry_with_components(self, tmp_path):
        """Create a registry structure with components."""
        # Create registry structure
        packages_dir = tmp_path / "packages" / "sygaldry_registry" / "components"
        packages_dir.mkdir(parents=True)

        # Create agent
        agents_dir = packages_dir / "agents"
        agents_dir.mkdir()

        test_agent_dir = agents_dir / "test_agent"
        test_agent_dir.mkdir()

        agent_manifest = {
            "name": "test_agent",
            "version": "1.0.0",
            "type": "agent",
            "description": "A test agent for documentation",
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": ["agent.py", "README.md"],
            "target_directory_key": "agents",
            "python_dependencies": ["requests>=2.28.0"],
            "registry_dependencies": [],
            "environment_variables": [
                {"name": "API_KEY", "description": "Your API key", "required": True},
                {"name": "API_SECRET", "description": "Your API secret", "required": True}
            ],
            "manifest_path": "components/agents/test_agent/component.json"
        }

        (test_agent_dir / "component.json").write_text(json.dumps(agent_manifest, indent=2))
        (test_agent_dir / "README.md").write_text("""# Test Agent

This is a test agent for documentation generation.

## Usage

```python
from test_agent import agent
result = agent("Hello")
```

## Configuration

Set the following environment variables:
- API_KEY: Your API key
- API_SECRET: Your API secret
""")

        # Create tool
        tools_dir = packages_dir / "tools"
        tools_dir.mkdir()

        test_tool_dir = tools_dir / "test_tool"
        test_tool_dir.mkdir()

        tool_manifest = {
            "name": "test_tool",
            "version": "1.0.0",
            "type": "tool",
            "description": "A test tool",
            "license": "Apache-2.0",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": ["tool.py"],
            "target_directory_key": "tools",
            "python_dependencies": [],
            "registry_dependencies": [],
            "environment_variables": [],
            "manifest_path": "components/tools/test_tool/component.json"
        }

        (test_tool_dir / "component.json").write_text(json.dumps(tool_manifest, indent=2))

        # Create sygaldry.json config
        config = {
            "base_dir": "packages/sygaldry_registry/components",
            "directories": {
                "agents": "agents",
                "tools": "tools",
                "response_models": "response_models",
                "prompt_templates": "prompt_templates",
                "evals": "evals"
            }
        }
        (tmp_path / "sygaldry.json").write_text(json.dumps(config, indent=2))

        return tmp_path

    def test_docs_generate_all(self, cli_runner, registry_with_components):
        """Test generating documentation for all components."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_with_components)

            # Generate docs for all components
            result = self.run_command(cli_runner, ["docs", "generate"])

            self.assert_command_success(result)

            # Verify sygaldry.md files were created
            agent_sygaldry_md = registry_with_components / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent" / "sygaldry.md"
            tool_sygaldry_md = registry_with_components / "packages" / "sygaldry_registry" / "components" / "tools" / "test_tool" / "sygaldry.md"

            self.assert_file_exists(agent_sygaldry_md)
            self.assert_file_exists(tool_sygaldry_md)

            # Verify .cursor/rules/sygaldry.mdc was created (default editor is cursor)
            cursor_rules = registry_with_components / ".cursor" / "rules" / "sygaldry.mdc"
            self.assert_file_exists(cursor_rules)

        finally:
            os.chdir(original_cwd)

    def test_docs_generate_specific_component(self, cli_runner, registry_with_components):
        """Test generating docs for a specific component."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_with_components)

            # Generate docs for specific component
            result = self.run_command(
                cli_runner,
                ["docs", "generate", "--component", "test_agent"]
            )

            self.assert_command_success(result)

            # Verify only test_agent sygaldry.md was created
            agent_sygaldry_md = registry_with_components / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent" / "sygaldry.md"
            self.assert_file_exists(agent_sygaldry_md)

            # Tool sygaldry.md should not exist
            tool_sygaldry_md = registry_with_components / "packages" / "sygaldry_registry" / "components" / "tools" / "test_tool" / "sygaldry.md"
            assert not tool_sygaldry_md.exists()

        finally:
            os.chdir(original_cwd)

    def test_docs_generate_by_type(self, cli_runner, registry_with_components):
        """Test generating docs for all components of a specific type."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_with_components)

            # Generate docs for all agents
            result = self.run_command(
                cli_runner,
                ["docs", "generate", "--type", "agent"]
            )

            self.assert_command_success(result)

            # Verify agent sygaldry.md was created
            agent_sygaldry_md = registry_with_components / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent" / "sygaldry.md"
            self.assert_file_exists(agent_sygaldry_md)

            # Tool sygaldry.md should not exist
            tool_sygaldry_md = registry_with_components / "packages" / "sygaldry_registry" / "components" / "tools" / "test_tool" / "sygaldry.md"
            assert not tool_sygaldry_md.exists()

        finally:
            os.chdir(original_cwd)

    def test_docs_different_editors(self, cli_runner, registry_with_components):
        """Test generating docs for different editors."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_with_components)

            # Test different editors
            editors = ["cursor", "windsurf", "claude"]

            for editor in editors:
                # Clear any existing editor files
                if editor == "cursor":
                    cursor_dir = registry_with_components / ".cursor" / "rules"
                    if cursor_dir.exists():
                        shutil.rmtree(cursor_dir)
                elif editor == "windsurf":
                    windsurf_file = registry_with_components / ".windsurfrules"
                    if windsurf_file.exists():
                        windsurf_file.unlink()
                elif editor == "claude":
                    claude_file = registry_with_components / "CLAUDE.md"
                    if claude_file.exists():
                        claude_file.unlink()

                # Generate docs for editor
                result = self.run_command(
                    cli_runner,
                    ["docs", "generate", "--editor", editor]
                )

                self.assert_command_success(result)

                # Verify editor-specific files
                if editor == "cursor":
                    cursor_rules = registry_with_components / ".cursor" / "rules" / "sygaldry.mdc"
                    self.assert_file_exists(cursor_rules)
                elif editor == "windsurf":
                    windsurf_rules = registry_with_components / ".windsurfrules"
                    self.assert_file_exists(windsurf_rules)
                elif editor == "claude":
                    claude_md = registry_with_components / "CLAUDE.md"
                    self.assert_file_exists(claude_md)

        finally:
            os.chdir(original_cwd)

    def test_docs_template_generation(self, cli_runner, tmp_path):
        """Test generating a sygaldry.md template."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Generate template
            result = self.run_command(
                cli_runner,
                ["docs", "template", "my_component"]
            )

            self.assert_command_success(result)

            # Verify template file was created
            template_file = tmp_path / "my_component_sygaldry.md"
            self.assert_file_exists(template_file)

            # Verify template content
            content = template_file.read_text()
            assert "my_component" in content
            assert "## Overview" in content
            assert "## Configuration" in content

        finally:
            os.chdir(original_cwd)

    def test_docs_template_custom_output(self, cli_runner, tmp_path):
        """Test generating template with custom output path."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)

            # Create output directory
            output_dir = tmp_path / "templates"
            output_dir.mkdir()

            # Generate template with custom output
            result = self.run_command(
                cli_runner,
                ["docs", "template", "custom_component", "--output", str(output_dir / "custom.md")]
            )

            self.assert_command_success(result)

            # Verify custom output
            custom_file = output_dir / "custom.md"
            self.assert_file_exists(custom_file)

            content = custom_file.read_text()
            assert "custom_component" in content

        finally:
            os.chdir(original_cwd)

    def test_docs_list_types(self, cli_runner):
        """Test listing available component types."""
        result = self.run_command(cli_runner, ["docs", "types"])

        self.assert_command_success(result)

        # Verify types are listed
        assert "agent" in result.output
        assert "tool" in result.output
        assert "prompt_template" in result.output

        # Should show usage examples
        assert "sygaldry docs generate --type" in result.output

    def test_docs_force_regenerate(self, cli_runner, registry_with_components):
        """Test force regenerating documentation."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_with_components)

            # First generate docs
            result = self.run_command(cli_runner, ["docs", "generate"])
            self.assert_command_success(result)

            # Modify existing sygaldry.md
            agent_sygaldry_md = registry_with_components / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent" / "sygaldry.md"
            original_content = agent_sygaldry_md.read_text()
            agent_sygaldry_md.write_text(original_content + "\n\n## Custom Section\n\nUser added content")

            # Regenerate without force (should preserve custom content)
            result = self.run_command(cli_runner, ["docs", "generate"])
            self.assert_command_success(result)

            content = agent_sygaldry_md.read_text()
            assert "Custom Section" in content
            assert "User added content" in content

            # Force regenerate (should overwrite)
            result = self.run_command(
                cli_runner,
                ["docs", "generate", "--force-regenerate"]
            )
            self.assert_command_success(result)

            # Custom content should be gone
            content = agent_sygaldry_md.read_text()
            assert "Custom Section" not in content
            assert "User added content" not in content

        finally:
            os.chdir(original_cwd)

    def test_docs_sygaldry_md_content(self, cli_runner, registry_with_components):
        """Test that sygaldry.md contains expected content."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_with_components)

            # Generate docs
            result = self.run_command(cli_runner, ["docs", "generate"])
            self.assert_command_success(result)

            # Check agent sygaldry.md content
            agent_sygaldry_md = registry_with_components / "packages" / "sygaldry_registry" / "components" / "agents" / "test_agent" / "sygaldry.md"
            content = agent_sygaldry_md.read_text()

            # Should contain component metadata
            assert "test_agent" in content
            assert "1.0.0" in content
            assert "A test agent for documentation" in content

            # Should contain environment variables
            assert "API_KEY" in content
            assert "API_SECRET" in content

            # Should contain dependencies
            assert "requests>=2.28.0" in content

            # Should incorporate README content
            assert "Usage" in content
            assert "Configuration" in content

        finally:
            os.chdir(original_cwd)

    def test_docs_editor_rules_content(self, cli_runner, registry_with_components):
        """Test that editor rules contain component information."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_with_components)

            # Generate docs
            result = self.run_command(cli_runner, ["docs", "generate", "--editor", "claude"])
            self.assert_command_success(result)

            # Check CLAUDE.md content
            claude_md = registry_with_components / "CLAUDE.md"
            content = claude_md.read_text()

            # Should list available components
            assert "test_agent" in content
            assert "test_tool" in content

            # Should include component descriptions
            assert "A test agent for documentation" in content
            assert "A test tool" in content

        finally:
            os.chdir(original_cwd)
