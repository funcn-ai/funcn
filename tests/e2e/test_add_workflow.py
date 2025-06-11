"""End-to-end tests for funcn add command workflow."""

from __future__ import annotations

import json
import pytest
import tarfile
from io import BytesIO
from pathlib import Path
from tests.e2e.base import BaseE2ETest
from unittest.mock import MagicMock, patch


@pytest.mark.e2e
class TestAddWorkflow(BaseE2ETest):
    """Test complete component addition workflows."""
    
    @pytest.fixture
    def initialized_project(self, cli_runner, test_project_dir):
        """Create an initialized funcn project."""
        # Run funcn init with --yes flag
        result = self.run_command(cli_runner, ["init", "--yes"], input="n\n")
        self.assert_command_success(result)
        return test_project_dir
    
    @pytest.fixture
    def mock_component_download(self, mock_component_files):
        """Mock component download from registry."""
        def create_tarball(component_name: str) -> bytes:
            """Create a tar.gz file for a component."""
            component_dir = mock_component_files / component_name
            
            # Create tarball in memory
            tar_buffer = BytesIO()
            with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
                for file in component_dir.iterdir():
                    tar.add(file, arcname=file.name)
            
            return tar_buffer.getvalue()
        
        return create_tarball
    
    def test_add_component_by_name(self, cli_runner, initialized_project, mock_registry_response, mock_component_manifest, mock_component_download):
        """Test adding a component by name from the registry."""
        with patch("httpx.Client") as mock_client_class:
            # Create mock client instance
            mock_client = MagicMock()
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
            
            # Run funcn add with all options to avoid prompts
            result = self.run_command(
                cli_runner, 
                ["add", "--provider", "openai", "--model", "gpt-4o-mini", "--stream", "test-agent"],
                input="n\n"  # Answer 'n' to lilypad tracing
            )
            
            self.assert_command_success(result)
            
            # Verify component was added - it shows in output as going to src/ai_agents
            agent_dir = initialized_project / "src" / "ai_agents" / "test-agent"
            self.assert_file_exists(agent_dir / "agent.py")
            self.assert_file_exists(agent_dir / "requirements.txt")
            
            # Verify agent.py content
            self.assert_file_contains(
                agent_dir / "agent.py",
                "TestResponse",
                "Agent file should contain the response model"
            )
    
    def test_add_component_with_dependencies(self, cli_runner, initialized_project, mock_registry_response, mock_component_manifest):
        """Test adding a component with Python dependencies."""
        with patch("httpx.Client") as mock_client_class:
            # Mock responses
            mock_index_response = MagicMock()
            mock_index_response.status_code = 200
            mock_index_response.json.return_value = mock_registry_response
            
            mock_manifest_response = MagicMock()
            mock_manifest_response.status_code = 200
            mock_manifest_response.json.return_value = mock_registry_response["components"][0]
            
            mock_download_response = MagicMock()
            mock_download_response.status_code = 200
            mock_download_response.content = mock_component_download("test_agent")
            
            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    return mock_index_response
                elif "component.json" in url:
                    return mock_manifest_response
                elif ".tar.gz" in url:
                    return mock_download_response
                return MagicMock(status_code=404)
            
            mock_get.side_effect = mock_get_side_effect
            
            # Mock subprocess for pip install
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                
                # Run funcn add with install flag
                result = self.run_command(cli_runner, ["add", "test_agent", "--install"])
                
                self.assert_command_success(result)
                
                # Verify pip install was called
                mock_run.assert_called()
                call_args = str(mock_run.call_args)
                assert "pip" in call_args
                assert "requests" in call_args
    
    def test_add_multiple_components(self, cli_runner, initialized_project, mock_registry_response, mock_component_download):
        """Test adding multiple components in sequence."""
        with patch("requests.get") as mock_get:
            # Set up mock responses for both components
            mock_index_response = MagicMock()
            mock_index_response.status_code = 200
            mock_index_response.json.return_value = mock_registry_response
            
            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    return mock_index_response
                elif "test_agent" in url and "component.json" in url:
                    response = MagicMock()
                    response.status_code = 200
                    response.json.return_value = mock_registry_response["components"][0]
                    return response
                elif "test_tool" in url and "component.json" in url:
                    response = MagicMock()
                    response.status_code = 200
                    response.json.return_value = mock_registry_response["components"][1]
                    return response
                elif "test_agent" in url and ".tar.gz" in url:
                    response = MagicMock()
                    response.status_code = 200
                    response.content = mock_component_download("test_agent")
                    return response
                elif "test_tool" in url and ".tar.gz" in url:
                    response = MagicMock()
                    response.status_code = 200
                    response.content = mock_component_download("test_tool")
                    return response
                return MagicMock(status_code=404)
            
            mock_get.side_effect = mock_get_side_effect
            
            # Add agent
            result = self.run_command(cli_runner, ["add", "test_agent"])
            self.assert_command_success(result)
            
            # Add tool
            result = self.run_command(cli_runner, ["add", "test_tool"])
            self.assert_command_success(result)
            
            # Verify both components exist
            self.assert_file_exists(initialized_project / "src" / "agents" / "test_agent" / "agent.py")
            self.assert_file_exists(initialized_project / "src" / "tools" / "test_tool" / "tool.py")
    
    def test_add_component_already_exists(self, cli_runner, initialized_project, mock_registry_response, mock_component_download):
        """Test adding a component that already exists."""
        # First, add the component
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_response
            
            mock_manifest = MagicMock()
            mock_manifest.status_code = 200
            mock_manifest.json.return_value = mock_registry_response["components"][0]
            
            mock_download = MagicMock()
            mock_download.status_code = 200
            mock_download.content = mock_component_download("test_agent")
            
            def mock_get_side_effect(url, *args, **kwargs):
                if "index.json" in url:
                    return mock_response
                elif "component.json" in url:
                    return mock_manifest
                elif ".tar.gz" in url:
                    return mock_download
                return MagicMock(status_code=404)
            
            mock_get.side_effect = mock_get_side_effect
            
            # Add component first time
            result = self.run_command(cli_runner, ["add", "test_agent"])
            self.assert_command_success(result)
            
            # Try to add it again
            result = self.run_command(cli_runner, ["add", "test_agent"])
            
            # Should warn about existing component
            assert "already exists" in result.output or "already installed" in result.output
    
    def test_add_component_with_version(self, cli_runner, initialized_project, mock_registry_response):
        """Test adding a specific version of a component."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_response
            mock_get.return_value = mock_response
            
            # Run funcn add with version
            result = self.run_command(cli_runner, ["add", "test_agent@1.0.0"])
            
            # Version handling should be mentioned
            assert "1.0.0" in result.output or "version" in result.output.lower()
    
    def test_add_nonexistent_component(self, cli_runner, initialized_project, mock_registry_response):
        """Test adding a component that doesn't exist."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_response
            mock_get.return_value = mock_response
            
            # Try to add non-existent component
            result = self.run_command(cli_runner, ["add", "nonexistent_component"])
            
            # Should fail with appropriate message
            assert result.exit_code != 0
            assert "not found" in result.output or "doesn't exist" in result.output
    
    def test_add_component_network_error(self, cli_runner, initialized_project):
        """Test handling network errors when adding components."""
        with patch("requests.get") as mock_get:
            # Simulate network error
            mock_get.side_effect = Exception("Network error")
            
            result = self.run_command(cli_runner, ["add", "test_agent"])
            
            # Should handle error gracefully
            assert result.exit_code != 0
            assert "error" in result.output.lower() or "failed" in result.output.lower()
    
    def test_add_component_from_url(self, cli_runner, initialized_project, mock_component_download):
        """Test adding a component directly from URL."""
        with patch("requests.get") as mock_get:
            # Mock component manifest
            mock_manifest = MagicMock()
            mock_manifest.status_code = 200
            mock_manifest.json.return_value = {
                "name": "custom_agent",
                "version": "1.0.0",
                "type": "agent",
                "description": "Custom agent from URL",
                "files_to_copy": ["agent.py"],
                "target_directory_key": "agents",
                "python_dependencies": [],
                "registry_dependencies": [],
                "environment_variables": []
            }
            
            # Mock download
            mock_download = MagicMock()
            mock_download.status_code = 200
            mock_download.content = mock_component_download("test_agent")
            
            def mock_get_side_effect(url, *args, **kwargs):
                if "component.json" in url:
                    return mock_manifest
                elif ".tar.gz" in url:
                    return mock_download
                return MagicMock(status_code=404)
            
            mock_get.side_effect = mock_get_side_effect
            
            # Add from URL
            result = self.run_command(
                cli_runner,
                ["add", "--url", "https://example.com/components/custom_agent"]
            )
            
            # Should succeed
            self.assert_command_success(result)
            
            # Verify component was added
            self.assert_file_exists(initialized_project / "src" / "agents" / "custom_agent")
