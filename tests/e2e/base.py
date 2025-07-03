"""Base class for end-to-end tests."""

from __future__ import annotations

import json
import os
import pytest
from pathlib import Path
from sygaldry_cli.config_manager import ConfigManager
from sygaldry_cli.main import app
from typer.testing import CliRunner
from typing import Any, Optional
from unittest.mock import MagicMock, patch


class BaseE2ETest:
    """Base class for end-to-end CLI tests.

    Provides utilities for testing complete user workflows with the sygaldry CLI.
    """

    @pytest.fixture
    def cli_runner(self):
        """Get a CLI runner for testing commands."""
        return CliRunner()

    @pytest.fixture
    def test_project_dir(self, tmp_path):
        """Create a temporary project directory for testing."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Change to the project directory for the test
        original_cwd = os.getcwd()
        os.chdir(project_dir)

        yield project_dir

        # Restore original directory
        os.chdir(original_cwd)

    @pytest.fixture
    def mock_registry_response(self):
        """Mock response from the sygaldry registry."""
        return {
            "registry_version": "1.0.0",
            "components": [
                {
                    "name": "test-agent",
                    "version": "1.0.0",
                    "type": "agent",
                    "description": "A test agent for demos",
                    "manifest_path": "components/agents/test-agent/component.json"
                },
                {
                    "name": "test-tool",
                    "version": "1.0.0",
                    "type": "tool",
                    "description": "A test tool for demos",
                    "manifest_path": "components/tools/test-tool/component.json"
                }
            ]
        }

    @pytest.fixture
    def mock_component_manifest(self):
        """Mock component manifest data."""
        return {
            "name": "test-agent",
            "version": "1.0.0",
            "type": "agent",
            "description": "A test agent for demos",
            "authors": [{"name": "Test Author", "email": "test@example.com"}],
            "license": "MIT",
            "mirascope_version_min": "0.1.0",
            "files_to_copy": [
                {"source": "agent.py", "destination": "agent.py"},
                {"source": "requirements.txt", "destination": "requirements.txt"}
            ],
            "target_directory_key": "agents",
            "python_dependencies": ["requests>=2.28.0"],
            "registry_dependencies": [],
            "environment_variables": ["TEST_API_KEY"],
            "tags": ["test", "demo"]
        }

    @pytest.fixture
    def initialized_project(self, cli_runner, test_project_dir):
        """Create an initialized sygaldry project."""
        # Run sygaldry init with defaults
        result = self.run_command(cli_runner, ["init", "--yes"], input="n\n")
        assert result.exit_code == 0

        # Return the project directory
        return test_project_dir

    @pytest.fixture
    def mock_component_files(self, tmp_path):
        """Create mock component files for testing."""
        components_dir = tmp_path / "mock_components"
        components_dir.mkdir()

        # Create test agent files
        agent_dir = components_dir / "test-agent"
        agent_dir.mkdir()
        (agent_dir / "agent.py").write_text("""
# Test agent
from mirascope.core import BaseModel, prompt_template
from mirascope.integrations.openai import OpenAICall

class TestResponse(BaseModel):
    answer: str

@OpenAICall("gpt-4o-mini", response_model=TestResponse)
@prompt_template("Test prompt: {question}")
def test_agent(question: str): ...
""")
        (agent_dir / "requirements.txt").write_text("requests>=2.28.0\n")
        (agent_dir / "component.json").write_text(json.dumps({
            "name": "test-agent",
            "version": "1.0.0",
            "type": "agent",
            "description": "A test agent for demos",
            "files_to_copy": ["agent.py", "requirements.txt"]
        }))

        # Create test tool files
        tool_dir = components_dir / "test-tool"
        tool_dir.mkdir()
        (tool_dir / "tool.py").write_text("""
# Test tool
from mirascope.core import tool

@tool
def test_tool(input: str) -> str:
    '''A test tool that echoes input.'''
    return f"Echo: {input}"
""")
        (tool_dir / "component.json").write_text(json.dumps({
            "name": "test-tool",
            "version": "1.0.0",
            "type": "tool",
            "description": "A test tool for demos",
            "files_to_copy": ["tool.py"]
        }))

        return components_dir

    def run_command(self, cli_runner: CliRunner, command: list[str], input: str = None, cwd: Path = None) -> Any:
        """Run a CLI command and return the result."""
        if cwd:
            import os
            original_cwd = Path.cwd()
            try:
                os.chdir(cwd)
                result = cli_runner.invoke(app, command, input=input)
                return result
            finally:
                os.chdir(original_cwd)
        else:
            result = cli_runner.invoke(app, command, input=input)
            return result

    def assert_command_success(self, result: Any):
        """Assert that a command executed successfully."""
        if result.exit_code != 0:
            print(f"Command failed with output:\n{result.output}")
            if result.exception:
                print(f"Exception: {result.exception}")
        assert result.exit_code == 0

    def assert_file_exists(self, path: Path | str, message: str = None):
        """Assert that a file exists."""
        path = Path(path)
        if not path.exists():
            msg = message or f"File does not exist: {path}"
            pytest.fail(msg)

    def assert_file_contains(self, path: Path | str, content: str, message: str = None):
        """Assert that a file contains specific content."""
        path = Path(path)
        self.assert_file_exists(path)

        file_content = path.read_text()
        if content not in file_content:
            msg = message or f"File {path} does not contain expected content: {content}"
            pytest.fail(msg)

    def assert_json_file_has_key(self, path: Path | str, key: str, expected_value: Any = None):
        """Assert that a JSON file has a specific key and optionally check its value."""
        path = Path(path)
        self.assert_file_exists(path)

        with open(path) as f:
            data = json.load(f)

        if key not in data:
            pytest.fail(f"JSON file {path} does not have key: {key}")

        if expected_value is not None and data[key] != expected_value:
            pytest.fail(f"JSON file {path} key '{key}' has value {data[key]}, expected {expected_value}")

    def create_mock_registry_server(self, mock_response: dict):
        """Create a mock HTTP server for registry requests."""
        def mock_get(url, *args, **kwargs):
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = mock_response
            return response

        return mock_get

    def verify_project_structure(self, project_dir: Path, expected_dirs: list[str]):
        """Verify that the project has the expected directory structure."""
        for dir_name in expected_dirs:
            dir_path = project_dir / dir_name
            self.assert_file_exists(dir_path, f"Expected directory '{dir_name}' not found")
            assert dir_path.is_dir(), f"'{dir_name}' is not a directory"
