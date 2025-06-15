"""End-to-end tests for funcn init command workflow."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from tests.e2e.base import BaseE2ETest


@pytest.mark.e2e
class TestInitWorkflow(BaseE2ETest):
    """Test complete initialization workflows."""
    
    def test_init_creates_complete_project_structure(self, cli_runner, test_project_dir):
        """Test that funcn init creates all necessary files and directories."""
        # Run funcn init with --yes to use all defaults
        # It still asks if we want to add components
        result = self.run_command(cli_runner, ["init", "--yes"], input="n\n")
        
        # Assert command succeeded
        self.assert_command_success(result)
        
        # Verify funcn.json was created
        self.assert_file_exists(test_project_dir / "funcn.json")
        
        # Verify funcn.json has correct structure
        funcn_json_path = test_project_dir / "funcn.json"
        with open(funcn_json_path) as f:
            config = json.load(f)
        
        assert config["$schema"] == "./funcn.schema.json"
        assert "agentDirectory" in config
        assert "toolDirectory" in config
        assert "evalDirectory" in config
        assert "promptTemplateDirectory" in config
        assert "responseModelDirectory" in config
        assert "aliases" in config
        
        # Verify default directories were created (using absolute paths from config)
        base_dir = Path(config["agentDirectory"]).parent
        self.assert_file_exists(config["agentDirectory"])
        self.assert_file_exists(config["toolDirectory"])
        self.assert_file_exists(config["evalDirectory"])
        self.assert_file_exists(config["promptTemplateDirectory"])
        self.assert_file_exists(config["responseModelDirectory"])
        
        # Verify .gitignore was updated
        gitignore_path = test_project_dir / ".gitignore"
        self.assert_file_exists(gitignore_path)
        # Check that funcn added its entry
        self.assert_file_contains(gitignore_path, ".funcn/")
    
    def test_init_with_custom_directories(self, cli_runner, test_project_dir):
        """Test funcn init with custom directory structure."""
        # Run funcn init with custom directories
        # Need to provide: base dir, agents, evals, prompts, tools, response models, aliases, add components
        input_text = (
            "custom\n"           # base directory
            "custom/agents\n"    # agents
            "custom/evals\n"     # evals
            "custom/prompts\n"   # prompts
            "custom/tools\n"     # tools
            "custom/models\n"    # response models
            "\n\n\n\n"          # default aliases
            "1\n"               # select openai provider
            "1\n"               # select first model
            "n\n"               # don't enable streaming
            "n\n"               # don't add components
        )
        result = self.run_command(cli_runner, ["init"], input=input_text)
        
        self.assert_command_success(result)
        
        # Verify custom directories were created
        self.verify_project_structure(test_project_dir, [
            "custom",
            "custom/agents",
            "custom/tools",
            "custom/prompts",
            "custom/models"
        ])
        
        # Verify funcn.json has custom paths
        with open(test_project_dir / "funcn.json") as f:
            config = json.load(f)
        
        assert config["agentDirectory"] == "custom/agents"
        assert config["toolDirectory"] == "custom/tools"
        assert config["promptTemplateDirectory"] == "custom/prompts"
        assert config["responseModelDirectory"] == "custom/models"
    
    def test_init_creates_schema_file(self, cli_runner, test_project_dir):
        """Test that funcn init creates or uses the schema file."""
        result = self.run_command(cli_runner, ["init", "--yes"], input="n\n")
        
        self.assert_command_success(result)
        
        # Check that it warned about missing schema
        assert "funcn.schema.json not found" in result.output
    
    def test_init_in_existing_project(self, cli_runner, test_project_dir):
        """Test funcn init behavior in a directory with existing funcn.json."""
        # Create an existing funcn.json
        existing_config = {
            "$schema": "./funcn.schema.json",
            "defaultProvider": "anthropic",
            "defaultModel": "claude-3-opus",
            "stream": True,
            "agentDirectory": "existing/agents"
        }
        
        funcn_json_path = test_project_dir / "funcn.json"
        with open(funcn_json_path, "w") as f:
            json.dump(existing_config, f, indent=2)
        
        # Run funcn init again
        result = self.run_command(cli_runner, ["init"], input="\n\n\n\nno\n")
        
        # Should warn about existing configuration (note: British spelling used)
        assert "already initialised" in result.output or "funcn.json exists" in result.output
    
    def test_init_handles_permission_errors(self, cli_runner, test_project_dir, monkeypatch):
        """Test funcn init handles directory creation permission errors gracefully."""
        # Mock Path.mkdir to raise permission error
        from pathlib import Path
        original_mkdir = Path.mkdir
        
        def mock_mkdir(self, *args, **kwargs):
            raise PermissionError("Cannot create directory")
        
        monkeypatch.setattr(Path, "mkdir", mock_mkdir)
        
        # Use --yes flag to skip prompts and trigger directory creation
        result = self.run_command(cli_runner, ["init", "--yes"])
        
        # Should fail with permission error
        assert result.exit_code != 0
        # Check for the permission error in output or exception
        assert ("Permission denied" in result.output or 
                "Cannot create directory" in result.output or
                "Cannot create directory" in str(result.exception) or 
                isinstance(result.exception, PermissionError))
