"""End-to-end tests for funcn build command workflow."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from tests.e2e.base import BaseE2ETest


@pytest.mark.e2e
class TestBuildWorkflow(BaseE2ETest):
    """Test registry building workflows."""
    
    @pytest.fixture
    def registry_structure(self, tmp_path):
        """Create a mock registry structure for building."""
        # Create packages directory structure
        packages_dir = tmp_path / "packages" / "funcn_registry" / "components"
        packages_dir.mkdir(parents=True)
        
        # Create agents directory
        agents_dir = packages_dir / "agents"
        agents_dir.mkdir()
        
        # Create test_agent
        test_agent_dir = agents_dir / "test_agent"
        test_agent_dir.mkdir()
        
        agent_manifest = {
            "name": "test_agent",
            "version": "1.0.0",
            "type": "agent",
            "description": "A test agent for e2e testing",
            "authors": [{"name": "Test Author", "email": "test@example.com"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": ["agent.py", "README.md"],
            "target_directory_key": "agents",
            "python_dependencies": ["requests>=2.28.0"],
            "registry_dependencies": [],
            "environment_variables": ["TEST_API_KEY"],
            "tags": ["test", "demo", "agent"]
        }
        
        (test_agent_dir / "component.json").write_text(json.dumps(agent_manifest, indent=2))
        (test_agent_dir / "agent.py").write_text("# Test agent implementation")
        (test_agent_dir / "README.md").write_text("# Test Agent\n\nA test agent.")
        
        # Create another agent
        another_agent_dir = agents_dir / "another_agent"
        another_agent_dir.mkdir()
        
        another_manifest = {
            "name": "another_agent",
            "version": "2.0.0",
            "type": "agent",
            "description": "Another test agent",
            "authors": [{"name": "Test Author", "email": "test@example.com"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": ["agent.py"],
            "target_directory_key": "agents",
            "python_dependencies": [],
            "registry_dependencies": ["test_agent"],
            "environment_variables": []
        }
        
        (another_agent_dir / "component.json").write_text(json.dumps(another_manifest, indent=2))
        (another_agent_dir / "agent.py").write_text("# Another agent")
        
        # Create tools directory
        tools_dir = packages_dir / "tools"
        tools_dir.mkdir()
        
        # Create test_tool
        test_tool_dir = tools_dir / "test_tool"
        test_tool_dir.mkdir()
        
        tool_manifest = {
            "name": "test_tool",
            "version": "1.1.0",
            "type": "tool",
            "description": "A test tool",
            "authors": [{"name": "Tool Author", "email": "tool@example.com"}],
            "license": "Apache-2.0",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": ["tool.py"],
            "target_directory_key": "tools",
            "python_dependencies": [],
            "registry_dependencies": [],
            "environment_variables": [],
            "tags": ["utility", "test"]
        }
        
        (test_tool_dir / "component.json").write_text(json.dumps(tool_manifest, indent=2))
        (test_tool_dir / "tool.py").write_text("# Test tool implementation")
        
        return tmp_path
    
    def test_build_creates_index_json(self, cli_runner, registry_structure):
        """Test that build command creates index.json file."""
        # Change to registry directory
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_structure)
            
            # Run build command
            result = self.run_command(cli_runner, ["build"])
            
            self.assert_command_success(result)
            
            # Verify index.json was created
            index_path = registry_structure / "index.json"
            self.assert_file_exists(index_path)
            
            # Verify index.json structure
            with open(index_path) as f:
                index_data = json.load(f)
            
            assert "registry_version" in index_data
            assert "components" in index_data
            assert isinstance(index_data["components"], list)
            
            # Verify components are included
            component_names = [c["name"] for c in index_data["components"]]
            assert "test_agent" in component_names
            assert "another_agent" in component_names
            assert "test_tool" in component_names
            
        finally:
            os.chdir(original_cwd)
    
    def test_build_with_output_path(self, cli_runner, registry_structure):
        """Test build command with custom output path."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_structure)
            
            # Create custom output directory
            output_dir = registry_structure / "dist"
            output_dir.mkdir()
            
            # Run build with output path
            result = self.run_command(
                cli_runner,
                ["build", "--output", str(output_dir / "custom_index.json")]
            )
            
            self.assert_command_success(result)
            
            # Verify custom output file
            custom_index_path = output_dir / "custom_index.json"
            self.assert_file_exists(custom_index_path)
            
            # Verify content
            with open(custom_index_path) as f:
                index_data = json.load(f)
            
            assert len(index_data["components"]) == 3
            
        finally:
            os.chdir(original_cwd)
    
    def test_build_validates_manifests(self, cli_runner, registry_structure):
        """Test that build validates component manifests."""
        # Create invalid component
        invalid_dir = registry_structure / "packages" / "funcn_registry" / "components" / "agents" / "invalid"
        invalid_dir.mkdir()
        
        # Invalid manifest (missing required fields)
        invalid_manifest = {
            "name": "invalid_component",
            # Missing required fields like version, type, etc.
        }
        
        (invalid_dir / "component.json").write_text(json.dumps(invalid_manifest))
        
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_structure)
            
            # Run build
            result = self.run_command(cli_runner, ["build"])
            
            # Should either skip invalid component or fail
            if result.exit_code == 0:
                # If successful, invalid component should be skipped
                index_path = registry_structure / "index.json"
                with open(index_path) as f:
                    index_data = json.load(f)
                
                component_names = [c["name"] for c in index_data["components"]]
                assert "invalid_component" not in component_names
            else:
                # If failed, should mention validation
                assert "invalid" in result.output.lower() or "validation" in result.output.lower()
            
        finally:
            os.chdir(original_cwd)
    
    def test_build_includes_metadata(self, cli_runner, registry_structure):
        """Test that build includes all component metadata."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_structure)
            
            result = self.run_command(cli_runner, ["build"])
            self.assert_command_success(result)
            
            # Check generated index
            with open(registry_structure / "index.json") as f:
                index_data = json.load(f)
            
            # Find test_agent in components
            test_agent = next(c for c in index_data["components"] if c["name"] == "test_agent")
            
            # Verify all metadata is included
            assert test_agent["version"] == "1.0.0"
            assert test_agent["type"] == "agent"
            assert test_agent["description"] == "A test agent for e2e testing"
            assert test_agent["license"] == "MIT"
            assert test_agent["authors"][0]["name"] == "Test Author"
            assert "requests>=2.28.0" in test_agent["python_dependencies"]
            assert "TEST_API_KEY" in test_agent["environment_variables"]
            assert "test" in test_agent["tags"]
            assert "demo" in test_agent["tags"]
            
            # Verify URLs are generated
            assert "manifest_url" in test_agent
            assert "download_url" in test_agent
            
        finally:
            os.chdir(original_cwd)
    
    def test_build_handles_dependencies(self, cli_runner, registry_structure):
        """Test that build correctly handles registry dependencies."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_structure)
            
            result = self.run_command(cli_runner, ["build"])
            self.assert_command_success(result)
            
            with open(registry_structure / "index.json") as f:
                index_data = json.load(f)
            
            # Find another_agent which depends on test_agent
            another_agent = next(c for c in index_data["components"] if c["name"] == "another_agent")
            
            # Verify dependency is preserved
            assert "test_agent" in another_agent["registry_dependencies"]
            
        finally:
            os.chdir(original_cwd)
    
    def test_build_empty_registry(self, cli_runner, tmp_path):
        """Test build with no components."""
        # Create empty registry structure
        packages_dir = tmp_path / "packages" / "funcn_registry" / "components"
        packages_dir.mkdir(parents=True)
        
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            
            result = self.run_command(cli_runner, ["build"])
            
            # Should succeed but with empty components
            self.assert_command_success(result)
            
            with open(tmp_path / "index.json") as f:
                index_data = json.load(f)
            
            assert index_data["components"] == []
            
        finally:
            os.chdir(original_cwd)
    
    def test_build_updates_existing_index(self, cli_runner, registry_structure):
        """Test that build updates existing index.json."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_structure)
            
            # Create existing index.json
            existing_index = {
                "registry_version": "0.9.0",
                "components": [
                    {"name": "old_component", "version": "0.1.0", "type": "tool"}
                ]
            }
            
            index_path = registry_structure / "index.json"
            with open(index_path, "w") as f:
                json.dump(existing_index, f)
            
            # Run build
            result = self.run_command(cli_runner, ["build"])
            self.assert_command_success(result)
            
            # Verify index was updated
            with open(index_path) as f:
                new_index = json.load(f)
            
            # Should have new components, not old ones
            component_names = [c["name"] for c in new_index["components"]]
            assert "test_agent" in component_names
            assert "old_component" not in component_names
            
            # Version should be updated
            assert new_index["registry_version"] == "1.0.0"
            
        finally:
            os.chdir(original_cwd)
    
    def test_build_generates_urls(self, cli_runner, registry_structure):
        """Test that build generates correct URLs for components."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_structure)
            
            # Run build with base URL
            result = self.run_command(
                cli_runner,
                ["build", "--base-url", "https://registry.funcn.ai"]
            )
            
            self.assert_command_success(result)
            
            with open(registry_structure / "index.json") as f:
                index_data = json.load(f)
            
            test_agent = next(c for c in index_data["components"] if c["name"] == "test_agent")
            
            # Verify URLs are generated correctly
            assert test_agent["manifest_url"].startswith("https://registry.funcn.ai")
            assert "test_agent" in test_agent["manifest_url"]
            assert "component.json" in test_agent["manifest_url"]
            
            assert test_agent["download_url"].startswith("https://registry.funcn.ai")
            assert "test_agent" in test_agent["download_url"]
            assert ".tar.gz" in test_agent["download_url"]
            
        finally:
            os.chdir(original_cwd)
    
    def test_build_verbose_output(self, cli_runner, registry_structure):
        """Test build with verbose output."""
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(registry_structure)
            
            # Run build with verbose flag
            result = self.run_command(cli_runner, ["build", "--verbose"])
            
            self.assert_command_success(result)
            
            # Should show detailed progress
            assert "test_agent" in result.output
            assert "another_agent" in result.output
            assert "test_tool" in result.output
            
            # Should show summary
            assert "3" in result.output or "three" in result.output.lower()
            
        finally:
            os.chdir(original_cwd)
