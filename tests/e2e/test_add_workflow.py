"""End-to-end tests for sygaldry add command workflow."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from tests.e2e.base import BaseE2ETest
from unittest.mock import MagicMock, patch


@pytest.mark.e2e
class TestAddWorkflow(BaseE2ETest):
    """Test complete component addition workflows."""

    @pytest.fixture
    def initialized_project(self, cli_runner, test_project_dir):
        """Create an initialized sygaldry project."""
        # Run sygaldry init with --yes flag
        result = self.run_command(cli_runner, ["init", "--yes"], input="n\n")
        self.assert_command_success(result)
        return test_project_dir


    def test_add_component_by_name(self, cli_runner, initialized_project, mock_registry_response, mock_component_manifest):
        """Test adding a component by name from the registry."""
        with patch("httpx.Client") as mock_client_class:
            # Create mock client instance with context manager support
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Mock registry index request
            mock_index_response = MagicMock()
            mock_index_response.status_code = 200
            mock_index_response.json.return_value = mock_registry_response
            mock_index_response.raise_for_status = MagicMock()

            # Mock component manifest request
            mock_manifest_response = MagicMock()
            mock_manifest_response.status_code = 200
            mock_manifest_response.json.return_value = mock_component_manifest
            mock_manifest_response.raise_for_status = MagicMock()

            # Mock component file downloads
            def get_file_content(url):
                if "agent.py" in url:
                    return b"""# Test agent
from mirascope.core import BaseModel, prompt_template
from mirascope.integrations.openai import OpenAICall

class TestResponse(BaseModel):
    answer: str

@OpenAICall("gpt-4o-mini", response_model=TestResponse)
@prompt_template("Test prompt: {question}")
def test_agent(question: str): ...
"""
                elif "requirements.txt" in url:
                    return b"requests>=2.28.0\n"
                else:
                    return b"# Default content"

            # Set up mock responses
            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    return mock_index_response
                elif "component.json" in url:
                    return mock_manifest_response
                elif ".py" in url or ".txt" in url:
                    mock_file_response = MagicMock()
                    mock_file_response.status_code = 200
                    mock_file_response.content = get_file_content(url)
                    mock_file_response.raise_for_status = MagicMock()
                    return mock_file_response
                return MagicMock(status_code=404)

            mock_client.get.side_effect = mock_get_side_effect

            # Run sygaldry add with all options to avoid prompts
            result = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent"],
                input="n\n"  # Answer 'n' to lilypad tracing
            )

            self.assert_command_success(result)

            # Read the sygaldry.json to get the actual agent directory
            with open(initialized_project / "sygaldry.json") as f:
                config = json.load(f)

            # Get the agent directory from config
            agent_directory = config.get("agentDirectory", "packages/sygaldry_registry/components/agents")
            agent_dir = initialized_project / agent_directory / "test-agent"
            self.assert_file_exists(agent_dir / "agent.py")
            self.assert_file_exists(agent_dir / "requirements.txt")

            # Verify agent.py content
            self.assert_file_contains(
                agent_dir / "agent.py",
                "TestResponse",
                "Agent file should contain the response model"
            )

    def test_add_component_with_dependencies(self, cli_runner, initialized_project, mock_registry_response, mock_component_manifest):
        """Test adding a component with Python dependencies - verify dependency message is shown."""
        with patch("httpx.Client") as mock_client_class:
            # Create mock client instance with context manager support
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Mock registry index request
            mock_index_response = MagicMock()
            mock_index_response.status_code = 200
            mock_index_response.json.return_value = mock_registry_response
            mock_index_response.raise_for_status = MagicMock()

            # Mock component manifest request
            mock_manifest_response = MagicMock()
            mock_manifest_response.status_code = 200
            mock_manifest_response.json.return_value = mock_component_manifest
            mock_manifest_response.raise_for_status = MagicMock()

            # Mock component file downloads
            def get_file_content(url):
                if "agent.py" in url:
                    return b"# Test agent with dependencies"
                elif "requirements.txt" in url:
                    return b"requests>=2.28.0\n"
                else:
                    return b"# Default content"

            # Set up mock responses
            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    return mock_index_response
                elif "component.json" in url:
                    return mock_manifest_response
                elif ".py" in url or ".txt" in url:
                    mock_file_response = MagicMock()
                    mock_file_response.status_code = 200
                    mock_file_response.content = get_file_content(url)
                    mock_file_response.raise_for_status = MagicMock()
                    return mock_file_response
                return MagicMock(status_code=404)

            mock_client.get.side_effect = mock_get_side_effect

            # Run sygaldry add (without --install flag to avoid subprocess issues)
            result = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent"],
                input="n\n"  # Answer 'n' to lilypad tracing
            )

            self.assert_command_success(result)

            # Verify dependency message is shown
            assert "requests>=2.28.0" in result.output or "uv pip install" in result.output

    def test_add_multiple_components(self, cli_runner, initialized_project, mock_registry_response, mock_component_manifest):
        """Test adding multiple components in sequence."""
        with patch("httpx.Client") as mock_client_class:
            # Create mock client instance with context manager support
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Create a second component manifest for tools
            tool_manifest = {
                "name": "test-tool",
                "version": "1.0.0",
                "type": "tool",
                "description": "A test tool for demos",
                "authors": [{"name": "Test Author", "email": "test@example.com"}],
                "license": "MIT",
                "mirascope_version_min": "0.1.0",
                "files_to_copy": [
                    {"source": "tool.py", "destination": "tool.py"}
                ],
                "target_directory_key": "tools",
                "python_dependencies": [],
                "registry_dependencies": [],
                "environment_variables": [],
                "tags": ["test", "demo"]
            }

            # Mock component file downloads
            def get_file_content(url):
                if "test-agent" in url and "agent.py" in url:
                    return b"""# Test agent
from mirascope.core import BaseModel, prompt_template
from mirascope.integrations.openai import OpenAICall

class TestResponse(BaseModel):
    answer: str

@OpenAICall("gpt-4o-mini", response_model=TestResponse)
@prompt_template("Test prompt: {question}")
def test_agent(question: str): ...
"""
                elif "test-agent" in url and "requirements.txt" in url:
                    return b"requests>=2.28.0\n"
                elif "test-tool" in url and "tool.py" in url:
                    return b"""# Test tool
from mirascope.core import tool

@tool
def test_tool(input: str) -> str:
    '''A test tool that echoes input.'''
    return f"Echo: {input}"
"""
                else:
                    return b"# Default content"

            # Set up mock responses
            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = mock_registry_response
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                elif "test-agent" in url and "component.json" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = mock_component_manifest
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                elif "test-tool" in url and "component.json" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = tool_manifest
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                elif ".py" in url or ".txt" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.content = get_file_content(url)
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                return MagicMock(status_code=404)

            mock_client.get.side_effect = mock_get_side_effect

            # Add first component (agent)
            result1 = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent"],
                input="n\n"
            )
            self.assert_command_success(result1)

            # Add second component (tool)
            result2 = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-tool"],
                input="n\n"
            )
            self.assert_command_success(result2)

            # Read the sygaldry.json to get the actual directories
            with open(initialized_project / "sygaldry.json") as f:
                config = json.load(f)

            # Verify both components were added
            agent_directory = config.get("agentDirectory", "packages/sygaldry_registry/components/agents")
            agent_dir = initialized_project / agent_directory / "test-agent"
            self.assert_file_exists(agent_dir / "agent.py")

            tool_directory = config.get("toolDirectory", "packages/sygaldry_registry/components/tools")
            tool_dir = initialized_project / tool_directory / "test-tool"
            self.assert_file_exists(tool_dir / "tool.py")

    def test_add_component_already_exists(self, cli_runner, initialized_project, mock_registry_response, mock_component_manifest):
        """Test adding a component that already exists."""
        with patch("httpx.Client") as mock_client_class:
            # Create mock client instance with context manager support
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Mock component file downloads
            def get_file_content(url):
                if "agent.py" in url:
                    return b"# Test agent content"
                elif "requirements.txt" in url:
                    return b"requests>=2.28.0\n"
                else:
                    return b"# Default content"

            # Set up mock responses
            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = mock_registry_response
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                elif "component.json" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = mock_component_manifest
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                elif ".py" in url or ".txt" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.content = get_file_content(url)
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                return MagicMock(status_code=404)

            mock_client.get.side_effect = mock_get_side_effect

            # Add component first time
            result1 = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent"],
                input="n\n"
            )
            self.assert_command_success(result1)

            # Try to add it again
            result2 = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent"],
                input="n\n"
            )

            # Should complete successfully but mention it already exists
            assert result2.exit_code == 0
            assert "already exists" in result2.output

    def test_add_component_with_version(self, cli_runner, initialized_project, mock_registry_response):
        """Test adding a specific version of a component."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = mock_registry_response
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                elif "component.json" in url:
                    # Return the component manifest
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_component_manifest = {
                        "name": "test-agent",
                        "version": "1.0.0",
                        "description": "Test agent component version 1.0.0",
                        "type": "agent",
                        "authors": [{"name": "Test Author", "email": "test@example.com"}],
                        "license": "MIT",
                        "mirascope_version_min": "1.0.0",
                        "files_to_copy": [
                            {"source": "test_agent.py", "destination": "test_agent.py"}
                        ],
                        "target_directory_key": "agents",
                        "python_dependencies": ["mirascope", "httpx"],
                        "template_variables": {
                            "provider": "openai",
                            "model": "gpt-4o",
                            "stream": "false"
                        }
                    }
                    mock_response.json.return_value = mock_component_manifest
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                elif ".py" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.content = b"# Test agent code"
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                return MagicMock(status_code=404)

            mock_client.get.side_effect = mock_get_side_effect

            # Run sygaldry add with version
            result = self.run_command(cli_runner, ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent@1.0.0"], input="n\nn\n")

            # Version handling should be mentioned
            if result.exit_code != 0:
                print(f"Test failed with output: {result.output}")
            assert result.exit_code == 0
            assert "test-agent" in result.output
            assert "added successfully" in result.output

    def test_add_component_with_invalid_version_format(self, cli_runner, initialized_project):
        """Test adding a component with invalid version format."""
        # Run sygaldry add with invalid version format
        result = self.run_command(cli_runner, ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent@invalid-version"], input="n\nn\n")

        # Should fail with error message about invalid version
        assert result.exit_code == 1
        assert "Invalid version format" in result.output
        assert "Expected format like '1.0.0'" in result.output

    def test_add_component_with_nonexistent_version(self, cli_runner, initialized_project, mock_registry_response):
        """Test adding a specific version that doesn't exist."""
        with patch("sygaldry_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    # Registry has test-agent but only version 1.0.0
                    mock_response.json.return_value = mock_registry_response
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                return MagicMock(status_code=404)

            mock_client.get.side_effect = mock_get_side_effect

            # Run sygaldry add with non-existent version
            result = self.run_command(cli_runner, ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent@9.9.9"], input="n\nn\n")

            # Should fail with appropriate error message
            assert result.exit_code == 1
            assert "Could not find component 'test-agent' version '9.9.9'" in result.output

    def test_add_nonexistent_component(self, cli_runner, initialized_project, mock_registry_response):
        """Test adding a component that doesn't exist."""
        with patch("httpx.Client") as mock_client_class:
            # Create mock client instance with context manager support
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Set up mock responses
            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = mock_registry_response
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                return MagicMock(status_code=404)

            mock_client.get.side_effect = mock_get_side_effect

            # Try to add non-existent component with required options
            result = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "nonexistent-component"],
                input="n\n"
            )

            # Should fail with appropriate message
            assert result.exit_code != 0
            assert "Could not find component" in result.output

    def test_add_component_network_error(self, cli_runner, initialized_project):
        """Test handling network errors when adding components."""
        with patch("httpx.Client") as mock_client_class:
            # Create mock client instance with context manager support
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Simulate network error
            mock_client.get.side_effect = Exception("Network error")

            result = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent"],
                input="n\n"
            )

            # Should handle error gracefully
            if result.exit_code == 0:
                print(f"Result output: {result.output}")
                print(f"Exception: {result.exception}")
            assert result.exit_code != 0
            # The error message should be in the output
            # The component manager catches the exception and prints an error message
            assert "Could not find component" in result.output or "Error" in result.output

    def test_add_component_from_url(self, cli_runner, initialized_project):
        """Test adding a component directly from URL."""
        with patch("httpx.Client") as mock_client_class:
            # Create mock client instance with context manager support
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=None)
            mock_client_class.return_value = mock_client

            # Mock component manifest
            manifest_data = {
                "name": "custom-agent",
                "version": "1.0.0",
                "type": "agent",
                "description": "Custom agent from URL",
                "authors": [{"name": "Test Author", "email": "test@example.com"}],
                "license": "MIT",
                "mirascope_version_min": "0.1.0",
                "files_to_copy": [
                    {"source": "agent.py", "destination": "agent.py"}
                ],
                "target_directory_key": "agents",
                "python_dependencies": [],
                "registry_dependencies": [],
                "environment_variables": [],
                "tags": ["custom"]
            }

            # Mock component files
            def get_file_content(url):
                if "agent.py" in url:
                    return b"# Custom agent\nprint('Hello from custom agent')"
                else:
                    return b"# Default content"

            # Set up mock responses
            def mock_get_side_effect(url, *args, **kwargs):
                # For manifest URL
                if url == "https://example.com/components/custom-agent":
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = manifest_data
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                # For file downloads
                elif ".py" in url:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.content = get_file_content(url)
                    mock_response.raise_for_status = MagicMock()
                    return mock_response
                # Default case
                return MagicMock(status_code=404)

            mock_client.get.side_effect = mock_get_side_effect

            # Add from URL with required options
            result = self.run_command(
                cli_runner,
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "https://example.com/components/custom-agent"],
                input="n\n"
            )

            # Should succeed
            self.assert_command_success(result)

            # Read the sygaldry.json to get the actual agent directory
            with open(initialized_project / "sygaldry.json") as f:
                config = json.load(f)

            # Verify component was added
            agent_directory = config.get("agentDirectory", "packages/sygaldry_registry/components/agents")
            self.assert_file_exists(initialized_project / agent_directory / "custom-agent")
