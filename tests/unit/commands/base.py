"""Base test class for funcn CLI commands."""

import json
import pytest
from pathlib import Path
from typer.testing import CliRunner
from typing import Any
from unittest.mock import AsyncMock, Mock, patch


class BaseCommandTest:
    """Base test class for CLI command testing."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.runner = CliRunner()
        self.mock_registry_url = "https://registry.funcn.ai"
        
    def create_test_project(self, tmp_path: Path, with_funcn_json: bool = True) -> Path:
        """Create a test project directory with basic structure."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Create basic project structure
        (project_dir / "src").mkdir()
        (project_dir / "src" / "agents").mkdir()
        (project_dir / "src" / "tools").mkdir()
        (project_dir / "src" / "prompts").mkdir()
        (project_dir / "src" / "models").mkdir()
        (project_dir / "src" / "evals").mkdir()

        if with_funcn_json:
            # Create a basic funcn.json
            funcn_config = {
                "directories": {
                    "agents": "src/agents",
                    "tools": "src/tools",
                    "prompt_templates": "src/prompts",
                    "response_models": "src/models",
                    "evals": "src/evals",
                },
                "provider": "openai",
                "model": "gpt-4o-mini",
            }

            with open(project_dir / "funcn.json", "w") as f:
                json.dump(funcn_config, f, indent=2)

        return project_dir

    def mock_registry_response(self, components: list) -> dict:
        """Create a mock registry API response."""
        return {
            "components": components,
            "total": len(components),
            "page": 1,
            "per_page": 50,
        }

    def mock_component_data(
        self,
        name: str = "test_component",
        type: str = "agent",
        version: str = "0.1.0",
        description: str = "A test component",
    ) -> dict:
        """Create mock component data."""
        return {
            "name": name,
            "type": type,
            "version": version,
            "description": description,
            "authors": [{"name": "Test Author", "email": "test@example.com"}],
            "license": "MIT",
            "mirascope_version_min": "1.24.0",
            "python_dependencies": [{"name": "mirascope", "version": ">=1.24.0"}],
            "registry_dependencies": [],
            "supports_lilypad": True,
            "tags": ["test", type],
            "example_usage": f"```python\\nfrom {type}s.{name} import {name}\\n```",
        }

    def assert_command_success(self, result):
        """Assert that a command executed successfully."""
        assert result.exit_code == 0, f"Command failed with output: {result.output}"

    def assert_command_failure(self, result, expected_error: str = None):
        """Assert that a command failed."""
        assert result.exit_code != 0, f"Command should have failed but succeeded with: {result.output}"
        if expected_error:
            assert expected_error in result.output

    def assert_file_exists(self, file_path: Path):
        """Assert that a file exists."""
        assert file_path.exists(), f"File {file_path} does not exist"

    def assert_file_contains(self, file_path: Path, content: str):
        """Assert that a file contains specific content."""
        assert file_path.exists(), f"File {file_path} does not exist"
        file_content = file_path.read_text()
        assert content in file_content, f"Content '{content}' not found in {file_path}"

    def assert_json_file_contains(self, file_path: Path, key: str, value: Any):
        """Assert that a JSON file contains a specific key-value pair."""
        assert file_path.exists(), f"File {file_path} does not exist"
        with open(file_path) as f:
            data = json.load(f)
        assert key in data, f"Key '{key}' not found in {file_path}"
        assert data[key] == value, f"Expected {key}={value}, got {key}={data[key]}"

    @pytest.fixture
    def mock_httpx_client(self):
        """Create a mock httpx client for registry requests."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_config_manager(self, tmp_path):
        """Create a mock ConfigManager."""
        project_dir = self.create_test_project(tmp_path)
        with patch("funcn_cli.config_manager.Path.cwd", return_value=project_dir):
            from funcn_cli.config_manager import ConfigManager
            yield ConfigManager()

    @pytest.fixture
    def mock_console(self):
        """Mock the rich console for testing output."""
        with patch("funcn_cli.commands.init_cmd.Console") as mock_console_cls:
            mock_console = Mock()
            mock_console_cls.return_value = mock_console
            yield mock_console

    def run_command(self, command_args: list, cwd: Path = None):
        """Run a funcn CLI command."""
        from funcn_cli.main import app
        
        # Set working directory if provided
        if cwd:
            with patch("os.getcwd", return_value=str(cwd)):
                with patch("pathlib.Path.cwd", return_value=cwd):
                    return self.runner.invoke(app, command_args)
        else:
            return self.runner.invoke(app, command_args)
