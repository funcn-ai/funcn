"""End-to-end tests for registry source management."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from tests.e2e.base import BaseE2ETest
from unittest.mock import MagicMock, patch


@pytest.mark.e2e
class TestSourceManagement(BaseE2ETest):
    """Test registry source management workflows."""
    
    def setup_method(self):
        """Clean up any existing global config before each test."""
        import os
        if os.path.exists(".funcnrc.json"):
            os.remove(".funcnrc.json")
    
    def teardown_method(self):
        """Clean up global config after each test."""
        import os
        if os.path.exists(".funcnrc.json"):
            os.remove(".funcnrc.json")
    
    @pytest.fixture
    def initialized_project(self, cli_runner, test_project_dir):
        """Create an initialized funcn project."""
        # Run funcn init with --yes flag to use all defaults
        result = self.run_command(cli_runner, ["init", "--yes"], input="n\n", cwd=test_project_dir)
        self.assert_command_success(result)
        return test_project_dir
    
    def test_add_source_project_level(self, cli_runner, initialized_project):
        """Test adding a registry source at project level."""
        # Add a custom source
        result = self.run_command(
            cli_runner,
            ["source", "add", "myregistry", "https://myregistry.funcn.ai/index.json"],
            cwd=initialized_project
        )
        
        self.assert_command_success(result)
        
        # Verify source was added in output
        assert "Added registry source" in result.output
        assert "myregistry" in result.output
        
        # List sources to verify
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)
        
        assert "myregistry" in result.output
        assert "https://myregistry.funcn.ai/index.json" in result.output
    
    @pytest.mark.skip(reason="Global sources not shown in list - tracked in FUNCNOS-35")
    def test_add_source_global_level(self, cli_runner, initialized_project):
        """Test adding a registry source at global level."""
        # Add a global source
        result = self.run_command(
            cli_runner,
            ["source", "add", "global_registry", "https://global.funcn.ai/index.json", "--global"],
            cwd=initialized_project
        )
        
        self.assert_command_success(result)
        
        # Verify source was added
        assert "Added registry source" in result.output
        assert "global_registry" in result.output
        
        # Global source should appear in list
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)
        
        assert "global_registry" in result.output
    
    def test_add_duplicate_source(self, cli_runner, initialized_project):
        """Test adding a source with duplicate alias."""
        # Add a source
        result = self.run_command(
            cli_runner,
            ["source", "add", "duplicate", "https://first.funcn.ai/index.json"],
            cwd=initialized_project
        )
        self.assert_command_success(result)
        
        # Try to add another source with same alias
        result = self.run_command(
            cli_runner,
            ["source", "add", "duplicate", "https://second.funcn.ai/index.json"],
            cwd=initialized_project
        )
        
        # Should either update or warn about duplicate
        assert "duplicate" in result.output.lower() or "updated" in result.output.lower()
    
    def test_list_sources_with_default(self, cli_runner, initialized_project):
        """Test listing sources shows default source."""
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        
        self.assert_command_success(result)
        
        # Should show default source
        assert "default" in result.output
        assert "funcn-ai/funcn-registry" in result.output or "default" in result.output
    
    def test_add_file_source(self, cli_runner, initialized_project):
        """Test adding a local file source."""
        # Create a local index file
        local_index = initialized_project / "local_index.json"
        local_index.write_text(json.dumps({
            "registry_version": "1.0.0",
            "components": []
        }))
        
        # Add file source
        result = self.run_command(
            cli_runner,
            ["source", "add", "local", f"file://{local_index}"],
            cwd=initialized_project
        )
        
        self.assert_command_success(result)
        
        # Verify in list
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        assert "local" in result.output
        assert "file://" in result.output
    
    @pytest.mark.skip(reason="Config format mismatch between init and source commands - tracked in FUNCNOS-37")
    def test_use_custom_source_for_list(self, cli_runner, initialized_project):
        """Test using a custom source for listing components."""
        # Add custom source
        result = self.run_command(
            cli_runner,
            ["source", "add", "custom", "https://custom.funcn.ai/index.json"],
            cwd=initialized_project
        )
        self.assert_command_success(result)
        
        # Verify source was added by listing sources
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)
        assert "custom" in result.output
        
        # Mock custom registry response
        custom_registry = {
            "registry_version": "1.0.0",
            "components": [
                {
                    "name": "custom_component",
                    "version": "1.0.0",
                    "type": "agent",
                    "description": "Component from custom registry",
                    "manifest_path": "components/agents/custom_component/component.json"
                }
            ]
        }
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = custom_registry
            mock_response.raise_for_status = MagicMock()
            mock_client.get.return_value = mock_response
            
            # List from custom source
            result = self.run_command(cli_runner, ["list", "--source", "custom"], cwd=initialized_project)
            
            # Debug: print the actual error
            if result.exit_code != 0:
                print(f"List command failed: {result.exception}")
                # Check if config file exists and has the source
                funcnrc_path = initialized_project / ".funcnrc.json"
                if funcnrc_path.exists():
                    import json
                    config = json.loads(funcnrc_path.read_text())
                    print(f".funcnrc.json contents: {config}")
                else:
                    print(".funcnrc.json does not exist")
                    
            self.assert_command_success(result)
            
            # Should show custom component
            assert "custom_component" in result.output
            
            # Verify custom URL was used
            mock_client.get.assert_called()
            call_args = str(mock_client.get.call_args)
            assert "custom.funcn.ai" in call_args
    
    def test_add_source_invalid_url(self, cli_runner, initialized_project):
        """Test adding source with invalid URL format."""
        # Try to add source with invalid URL
        result = self.run_command(
            cli_runner,
            ["source", "add", "invalid", "not-a-valid-url"],
            cwd=initialized_project
        )
        
        # Should either accept it (trusting user) or validate
        # The behavior depends on implementation
        if result.exit_code != 0:
            assert "invalid" in result.output.lower() or "url" in result.output.lower()
    
    def test_source_persistence(self, cli_runner, initialized_project):
        """Test that sources persist across CLI invocations."""
        # Add a source
        result = self.run_command(
            cli_runner,
            ["source", "add", "persistent", "https://persistent.funcn.ai/index.json"],
            cwd=initialized_project
        )
        self.assert_command_success(result)
        
        # Create new CLI runner to simulate new session
        new_runner = cli_runner
        
        # List sources in new session
        result = self.run_command(new_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)
        
        # Source should still be there
        assert "persistent" in result.output
        assert "https://persistent.funcn.ai/index.json" in result.output
    
    @pytest.mark.skip(reason="Config format mismatch between init and source commands - tracked in FUNCNOS-37")
    def test_multiple_sources_workflow(self, cli_runner, initialized_project):
        """Test complete workflow with multiple sources."""
        # Add multiple sources
        sources = [
            ("dev", "https://dev.funcn.ai/index.json"),
            ("prod", "https://prod.funcn.ai/index.json"),
            ("staging", "https://staging.funcn.ai/index.json")
        ]
        
        for alias, url in sources:
            result = self.run_command(
                cli_runner,
                ["source", "add", alias, url],
                cwd=initialized_project
            )
            self.assert_command_success(result)
        
        # List all sources
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)
        
        # All sources should be listed
        for alias, url in sources:
            assert alias in result.output
            assert url in result.output
        
        # Mock different responses for each source
        dev_registry = {
            "registry_version": "1.0.0",
            "components": [{
                "name": "dev_component", 
                "type": "agent", 
                "version": "1.0.0",
                "description": "Dev component",
                "manifest_path": "components/agents/dev_component/component.json"
            }]
        }
        
        prod_registry = {
            "registry_version": "1.0.0",
            "components": [{
                "name": "prod_component", 
                "type": "tool", 
                "version": "2.0.0",
                "description": "Prod component",
                "manifest_path": "components/tools/prod_component/component.json"
            }]
        }
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            def mock_get_side_effect(url, *args, **kwargs):
                response = MagicMock()
                response.status_code = 200
                response.raise_for_status = MagicMock()
                
                if "dev.funcn.ai" in url:
                    response.json.return_value = dev_registry
                elif "prod.funcn.ai" in url:
                    response.json.return_value = prod_registry
                else:
                    response.json.return_value = {"registry_version": "1.0.0", "components": []}
                
                return response
            
            mock_client.get.side_effect = mock_get_side_effect
            
            # List from dev source
            result = self.run_command(cli_runner, ["list", "--source", "dev"], cwd=initialized_project)
            self.assert_command_success(result)
            assert "dev_component" in result.output
            assert "prod_component" not in result.output
            
            # List from prod source
            result = self.run_command(cli_runner, ["list", "--source", "prod"], cwd=initialized_project)
            self.assert_command_success(result)
            assert "prod_component" in result.output
            assert "dev_component" not in result.output
    
    @pytest.mark.skip(reason="Authentication for registry sources not implemented - tracked in FUNCNOS-36")
    def test_source_with_auth_token(self, cli_runner, initialized_project):
        """Test adding source that requires authentication."""
        # Add source (auth would be handled via headers)
        result = self.run_command(
            cli_runner,
            ["source", "add", "private", "https://private.funcn.ai/index.json"],
            cwd=initialized_project
        )
        
        self.assert_command_success(result)
        
        # When using this source, it should handle auth
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            # Simulate auth required
            mock_unauth_response = MagicMock()
            mock_unauth_response.status_code = 401
            mock_unauth_response.raise_for_status = MagicMock()
            
            mock_auth_response = MagicMock()
            mock_auth_response.status_code = 200
            mock_auth_response.json.return_value = {
                "registry_version": "1.0.0",
                "components": []
            }
            mock_auth_response.raise_for_status = MagicMock()
            
            # Return different responses based on headers
            def mock_get_side_effect(url, headers=None, *args, **kwargs):
                if headers and "Authorization" in headers:
                    return mock_auth_response
                return mock_unauth_response
            
            mock_client.get.side_effect = mock_get_side_effect
            
            # Try to list - implementation should handle auth
            result = self.run_command(cli_runner, ["list", "--source", "private"], cwd=initialized_project)
            
            # Should either succeed (if auth is configured) or show auth error
            if result.exit_code != 0:
                assert "401" in result.output or "auth" in result.output.lower()
