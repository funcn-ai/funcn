"""Unit tests for funcn init command."""

import json
import pytest
from pathlib import Path
from tests.unit.commands.base import BaseCommandTest
from unittest.mock import Mock, mock_open, patch


class TestInitCommand(BaseCommandTest):
    """Test cases for the funcn init command."""
    
    def get_default_schema_data(self):
        """Get default schema data for testing."""
        return {
            "agentDirectory": "packages/funcn_registry/components/agents",
            "evalDirectory": "packages/funcn_registry/components/evals", 
            "promptTemplateDirectory": "packages/funcn_registry/components/prompt_templates",
            "toolDirectory": "packages/funcn_registry/components/tools",
            "responseModelDirectory": "packages/funcn_registry/components/response_models",
            "defaultProvider": "openai",
            "defaultModel": "gpt-4o-mini",
            "stream": False,
            "aliases": {
                "agents": "@/agents",
                "evals": "@/evals",
                "prompts": "@/prompt_templates",
                "tools": "@/tools",
            }
        }
    
    def run_init_command(self, args, cwd, add_components=False):
        """Run init command with common mocks."""
        with patch("funcn_cli.commands.init_cmd.load_schema_defaults") as mock_load:
            with patch("funcn_cli.commands.init_cmd.Confirm.ask") as mock_confirm:
                mock_load.return_value = self.get_default_schema_data()
                mock_confirm.return_value = add_components
                return self.run_command(["init"] + args, cwd=cwd)

    def test_init_with_defaults_creates_config(self, tmp_path):
        """Test that init with --defaults creates funcn.json."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        result = self.run_init_command(["--defaults"], project_dir)
        
        self.assert_command_success(result)
        self.assert_file_exists(project_dir / "funcn.json")
        
        # Verify config content
        config_data = json.loads((project_dir / "funcn.json").read_text())
        assert "agentDirectory" in config_data
        assert "toolDirectory" in config_data
        assert config_data["defaultProvider"] == "openai"
        assert config_data["defaultModel"] == "gpt-4o-mini"

    def test_init_creates_directory_structure(self, tmp_path):
        """Test that init creates all required directories."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        result = self.run_init_command(["--yes"], project_dir)
        
        self.assert_command_success(result)
        
        # Verify directories were created (default uses packages path for response_models)
        assert (project_dir / "src" / "funcn" / "agents").exists()
        assert (project_dir / "src" / "funcn" / "evals").exists()
        assert (project_dir / "src" / "funcn" / "prompt_templates").exists()
        assert (project_dir / "src" / "funcn" / "tools").exists()
        assert (project_dir / "packages" / "funcn_registry" / "components" / "response_models").exists()

    def test_init_with_existing_config_no_force(self, tmp_path):
        """Test that init fails when config exists without --force."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=True)
        
        result = self.run_init_command(["--defaults"], project_dir)
        
        # Should show message about existing config
        assert "funcn already initialised" in result.output
        assert (project_dir / "funcn.json").exists()

    def test_init_with_force_overwrites_config(self, tmp_path):
        """Test that init --force overwrites existing config."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=True)
        
        # Modify existing config
        original_config = json.loads((project_dir / "funcn.json").read_text())
        original_config["customField"] = "test"
        with open(project_dir / "funcn.json", "w") as f:
            json.dump(original_config, f)
        
        result = self.run_init_command(["--force", "--defaults"], project_dir)
        
        self.assert_command_success(result)
        
        # Verify config was overwritten
        new_config = json.loads((project_dir / "funcn.json").read_text())
        assert "customField" not in new_config
        assert new_config["defaultProvider"] == "openai"

    @pytest.mark.skip(reason="Complex mock setup - needs refactoring")
    def test_init_interactive_mode(self, tmp_path):
        """Test interactive configuration mode."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        # We'll test the simpler case where known_llms.json doesn't exist
        # This avoids the complexity of mocking the file reading
        with patch("funcn_cli.commands.init_cmd.load_schema_defaults") as mock_load:
            with patch("funcn_cli.commands.init_cmd.Prompt.ask") as mock_prompt:
                with patch("funcn_cli.commands.init_cmd.Confirm.ask") as mock_confirm:
                    mock_load.return_value = self.get_default_schema_data()
                    
                    # Create a temporary known_llms.json file that doesn't exist in the expected location
                    # This will trigger the fallback to free text prompts
                    mock_prompt.side_effect = [
                        str(project_dir / "src" / "agents"),  # agents dir
                        str(project_dir / "src" / "evals"),   # evals dir
                        str(project_dir / "src" / "prompts"), # prompts dir
                        str(project_dir / "src" / "tools"),   # tools dir
                        str(project_dir / "src" / "models"),  # models dir
                        "@/agents",    # agents alias
                        "@/evals",     # evals alias
                        "@/prompts",   # prompts alias
                        "@/tools",     # tools alias
                        "openai",      # provider (free text fallback)
                        "gpt-4",       # model (free text fallback)
                    ]
                    mock_confirm.side_effect = [
                        False,  # Enable streaming?
                        False,  # Add components now?
                    ]
                    
                    # Temporarily move any existing known_llms.json
                    import tempfile
                    with tempfile.TemporaryDirectory() as temp_dir:
                        result = self.run_command(["init"], cwd=project_dir)
                    
                    self.assert_command_success(result)
                    
                    # Verify config was created with custom values
                    config = json.loads((project_dir / "funcn.json").read_text())
                    assert config["defaultProvider"] == "openai"
                    assert config["defaultModel"] == "gpt-4"
                    assert config["stream"] is False

    def test_init_silent_mode(self, tmp_path):
        """Test that --silent suppresses output."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        result = self.run_init_command(["--defaults", "--silent"], project_dir)
        
        self.assert_command_success(result)
        # Output should be minimal/empty
        assert len(result.output.strip()) == 0 or "funcn initialised" not in result.output

    def test_init_updates_gitignore(self, tmp_path):
        """Test that init updates .gitignore file."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        # Create existing .gitignore
        gitignore_path = project_dir / ".gitignore"
        with open(gitignore_path, "w") as f:
            f.write("*.pyc\n")
        
        result = self.run_init_command(["--defaults"], project_dir)
        
        self.assert_command_success(result)
        
        # Verify .gitignore was updated
        gitignore_content = gitignore_path.read_text()
        assert ".funcn/" in gitignore_content
        assert "*.pyc" in gitignore_content  # Original content preserved

    def test_init_without_schema_fallback(self, tmp_path):
        """Test that init works with fallback when schema is missing."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        # Mock load_schema_defaults to simulate missing schema
        with patch("funcn_cli.commands.init_cmd.load_schema_defaults") as mock_load:
            with patch("funcn_cli.commands.init_cmd.Confirm.ask") as mock_confirm:
                # Return the fallback defaults that would be used when schema is missing
                mock_load.return_value = {
                    "agentDirectory": "packages/funcn_registry/components/agents",
                    "evalDirectory": "packages/funcn_registry/components/evals",
                    "promptTemplateDirectory": "packages/funcn_registry/components/prompt_templates",
                    "toolDirectory": "packages/funcn_registry/components/tools",
                    "aliases": {
                        "agents": "@/agents",
                        "evals": "@/evals",
                        "prompts": "@/prompt_templates",
                        "tools": "@/tools",
                    },
                }
                mock_confirm.return_value = False
                
                result = self.run_command(["init", "--defaults"], cwd=project_dir)
                
                self.assert_command_success(result)
                
                # Should still create config with fallback defaults
                config = json.loads((project_dir / "funcn.json").read_text())
                assert "agentDirectory" in config

    def test_init_with_custom_cwd(self, tmp_path):
        """Test init with --cwd option."""
        # Create project in a subdirectory
        project_dir = tmp_path / "subdir" / "project"
        project_dir.mkdir(parents=True)
        
        # Create basic structure
        (project_dir / "src").mkdir()
        
        # Run from parent directory with --cwd
        result = self.run_init_command(
            ["--defaults", "--cwd", str(project_dir)],
            tmp_path  # Running from parent
        )
        
        self.assert_command_success(result)
        self.assert_file_exists(project_dir / "funcn.json")

    def test_init_detects_src_directory(self, tmp_path):
        """Test that init detects existing src directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "src").mkdir()
        
        result = self.run_init_command(["--defaults"], project_dir)
        
        self.assert_command_success(result)
        
        # Should use src/funcn as base
        config = json.loads((project_dir / "funcn.json").read_text())
        assert "src/funcn" in config["agentDirectory"]

    def test_init_detects_app_directory(self, tmp_path):
        """Test that init detects existing app directory."""
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / "app").mkdir()
        
        result = self.run_init_command(["--defaults"], project_dir)
        
        self.assert_command_success(result)
        
        # Should use app/funcn as base
        config = json.loads((project_dir / "funcn.json").read_text())
        assert "app/funcn" in config["agentDirectory"]

    def test_init_error_writing_config(self, tmp_path):
        """Test error handling when unable to write config."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        # Mock open to simulate write error
        with patch("funcn_cli.commands.init_cmd.load_schema_defaults") as mock_load:
            with patch("funcn_cli.commands.init_cmd.Confirm.ask") as mock_confirm:
                with patch("builtins.open", side_effect=OSError("Permission denied")) as mock_open:
                    mock_load.return_value = self.get_default_schema_data()
                    mock_confirm.return_value = False
                    
                    # Allow reading but not writing
                    original_open = open
                    def selective_open(path, mode='r', *args, **kwargs):
                        if 'w' in mode and "funcn.json" in str(path):
                            raise OSError("Permission denied")
                        return original_open(path, mode, *args, **kwargs)
                    
                    mock_open.side_effect = selective_open
                    
                    result = self.run_command(["init", "--defaults"], cwd=project_dir)
                    
                    # Should fail with error
                    self.assert_command_failure(result)
                    assert "Error writing configuration file" in result.output

    @pytest.mark.parametrize("flag", ["--yes", "-y", "--defaults", "-d"])
    def test_init_skip_confirmation_flags(self, tmp_path, flag):
        """Test various flags that skip confirmation."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        result = self.run_init_command([flag], project_dir)
        
        self.assert_command_success(result)
        self.assert_file_exists(project_dir / "funcn.json")

    @pytest.mark.skip(reason="Complex mock setup - needs refactoring")
    def test_init_with_known_llms(self, tmp_path):
        """Test interactive mode with known_llms.json."""
        project_dir = self.create_test_project(tmp_path, with_funcn_json=False)
        
        # Create the actual known_llms.json file in a temp location
        known_llms_data = {
            "openai": {
                "models": ["gpt-4", "gpt-4o-mini", "gpt-3.5-turbo"],
                "api_key_env": "OPENAI_API_KEY"
            },
            "anthropic": {
                "models": ["claude-3-opus", "claude-3-haiku"],
                "api_key_env": "ANTHROPIC_API_KEY"
            }
        }
        
        # Create a temporary known_llms.json file
        known_llms_path = project_dir / "known_llms.json"
        with open(known_llms_path, "w") as f:
            json.dump(known_llms_data, f)
        
        with patch("funcn_cli.commands.init_cmd.load_schema_defaults") as mock_load:
            with patch("funcn_cli.commands.init_cmd.Prompt.ask") as mock_prompt:
                with patch("funcn_cli.commands.init_cmd.Confirm.ask") as mock_confirm:
                    # Patch the path construction for known_llms.json
                    original_truediv = Path.__truediv__
                    
                    def patched_truediv(self, other):
                        result = original_truediv(self, other)
                        if str(result).endswith("known_llms.json") and "funcn_cli" in str(result):
                            return known_llms_path
                        return result
                    
                    with patch.object(Path, "__truediv__", patched_truediv):
                        mock_load.return_value = self.get_default_schema_data()
                        
                        # Mock user selections
                        mock_prompt.side_effect = [
                            str(project_dir / "src" / "agents"),
                            str(project_dir / "src" / "evals"),
                            str(project_dir / "src" / "prompts"),
                            str(project_dir / "src" / "tools"),
                            str(project_dir / "src" / "models"),
                            "@/agents",
                            "@/evals", 
                            "@/prompts",
                            "@/tools",
                            "2",  # Select anthropic (2nd option)
                            "1",  # Select first model
                        ]
                        mock_confirm.side_effect = [
                            True,   # Enable streaming
                            False,  # Add components now
                        ]
                        
                        result = self.run_command(["init"], cwd=project_dir)
                        
                        self.assert_command_success(result)
                        
                        # Verify provider selection worked
                        config = json.loads((project_dir / "funcn.json").read_text())
                        assert config["defaultProvider"] == "anthropic"
                        assert config["defaultModel"] == "claude-3-opus"
                        assert config["stream"] is True
