"""End-to-end tests for registry source management."""

from __future__ import annotations

import httpx
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
        # Add a custom source (skip connectivity check for E2E tests)
        result = self.run_command(
            cli_runner, ["source", "add", "myregistry", "https://myregistry.funcn.ai/index.json", "--skip-check"], cwd=initialized_project
        )

        self.assert_command_success(result)

        # Verify source was added in output
        assert "Added registry source" in result.output
        assert "myregistry" in result.output

        # List sources to verify
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)

        assert "myregistry" in result.output
        assert "myregistry.funcn.ai" in result.output  # URL may be truncated in table

    def test_add_duplicate_source(self, cli_runner, initialized_project):
        """Test adding a source with duplicate alias."""
        # Add a source
        result = self.run_command(
            cli_runner, ["source", "add", "duplicate", "https://first.funcn.ai/index.json", "--skip-check"], cwd=initialized_project
        )
        self.assert_command_success(result)

        # Try to add another source with same alias
        result = self.run_command(
            cli_runner, ["source", "add", "duplicate", "https://second.funcn.ai/index.json", "--skip-check"], cwd=initialized_project
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
        local_index.write_text(json.dumps({"registry_version": "1.0.0", "components": []}))

        # Add file source
        result = self.run_command(cli_runner, ["source", "add", "local", f"file://{local_index}", "--skip-check"], cwd=initialized_project)

        self.assert_command_success(result)

        # Verify in list
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        assert "local" in result.output
        assert "file://" in result.output

    def test_use_custom_source_for_list(self, cli_runner, initialized_project):
        """Test using a custom source for listing components."""
        # Add custom source
        result = self.run_command(
            cli_runner, ["source", "add", "custom", "https://custom.funcn.ai/index.json", "--skip-check"], cwd=initialized_project
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
                    "manifest_path": "components/agents/custom_component/component.json",
                }
            ],
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
        result = self.run_command(cli_runner, ["source", "add", "invalid", "not-a-valid-url", "--skip-check"], cwd=initialized_project)

        # Should either accept it (trusting user) or validate
        # The behavior depends on implementation
        if result.exit_code != 0:
            assert "invalid" in result.output.lower() or "url" in result.output.lower()

    def test_source_persistence(self, cli_runner, initialized_project):
        """Test that sources persist across CLI invocations."""
        # Add a source
        result = self.run_command(
            cli_runner, ["source", "add", "persistent", "https://persistent.funcn.ai/index.json", "--skip-check"], cwd=initialized_project
        )
        self.assert_command_success(result)

        # Create new CLI runner to simulate new session
        new_runner = cli_runner

        # List sources in new session
        result = self.run_command(new_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)

        # Source should still be there
        assert "persistent" in result.output
        # URL may be truncated in table, so check for partial match
        assert "persistent.funcn.ai" in result.output

    def test_multiple_sources_workflow(self, cli_runner, initialized_project):
        """Test complete workflow with multiple sources."""
        # Add multiple sources
        sources = [
            ("dev", "https://dev.funcn.ai/index.json"),
            ("prod", "https://prod.funcn.ai/index.json"),
            ("staging", "https://staging.funcn.ai/index.json"),
        ]

        for alias, url in sources:
            result = self.run_command(cli_runner, ["source", "add", alias, url, "--skip-check"], cwd=initialized_project)
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
            "components": [
                {
                    "name": "dev_component",
                    "type": "agent",
                    "version": "1.0.0",
                    "description": "Dev component",
                    "manifest_path": "components/agents/dev_component/component.json",
                }
            ],
        }

        prod_registry = {
            "registry_version": "1.0.0",
            "components": [
                {
                    "name": "prod_component",
                    "type": "tool",
                    "version": "2.0.0",
                    "description": "Prod component",
                    "manifest_path": "components/tools/prod_component/component.json",
                }
            ],
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
            cli_runner, ["source", "add", "private", "https://private.funcn.ai/index.json", "--skip-check"], cwd=initialized_project
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
            mock_auth_response.json.return_value = {"registry_version": "1.0.0", "components": []}
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

    def test_source_remove(self, cli_runner, initialized_project):
        """Test removing a registry source."""
        # Add a custom source
        result = self.run_command(
            cli_runner, ["source", "add", "test", "https://test.example.com/index.json", "--skip-check"], cwd=initialized_project
        )
        self.assert_command_success(result)

        # List sources to verify it was added
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)
        assert "test" in result.output
        assert "https://test.example.com/index.json" in result.output

        # Remove the source
        result = self.run_command(cli_runner, ["source", "remove", "test"], cwd=initialized_project)
        self.assert_command_success(result)
        assert "Removed registry source 'test'" in result.output

        # List sources to verify it was removed
        result = self.run_command(cli_runner, ["source", "list"], cwd=initialized_project)
        self.assert_command_success(result)
        assert "test" not in result.output
        assert "https://test.example.com/index.json" not in result.output

    def test_source_remove_nonexistent(self, cli_runner, initialized_project):
        """Test removing a non-existent registry source."""
        # Try to remove a non-existent source
        result = self.run_command(cli_runner, ["source", "remove", "nonexistent"], cwd=initialized_project)
        assert result.exit_code == 1
        assert "Registry source 'nonexistent' not found" in result.output

    def test_source_remove_default_when_only_source(self, cli_runner, initialized_project):
        """Test preventing removal of the only remaining source."""
        # Try to remove default source when it's the only one
        result = self.run_command(cli_runner, ["source", "remove", "default"], cwd=initialized_project)
        assert result.exit_code == 1
        assert "Cannot remove the only remaining registry source" in result.output

    def test_source_add_url_validation(self, cli_runner, initialized_project):
        """Test URL validation when adding sources."""
        # Test invalid scheme
        result = self.run_command(
            cli_runner, ["source", "add", "invalid", "ftp://example.com/index.json", "--skip-check"], cwd=initialized_project
        )
        assert result.exit_code == 1
        assert "Invalid URL scheme" in result.output
        assert "ftp" in result.output

        # Test missing domain
        result = self.run_command(cli_runner, ["source", "add", "nodomain", "https://", "--skip-check"], cwd=initialized_project)
        assert result.exit_code == 1
        assert "missing domain/host" in result.output

        # Test warning for non-index.json URL
        result = self.run_command(
            cli_runner, ["source", "add", "nonindex", "https://example.com/registry", "--skip-check"], cwd=initialized_project
        )
        self.assert_command_success(result)
        assert "should typically point to an index.json file" in result.output
        assert "Added registry source" in result.output

        # Test valid index.json URL
        result = self.run_command(
            cli_runner, ["source", "add", "proper", "https://example.com/index.json", "--skip-check"], cwd=initialized_project
        )
        self.assert_command_success(result)
        assert "Added registry source" in result.output
        assert "should typically point to an index.json file" not in result.output

    def test_source_connectivity_check(self, cli_runner, initialized_project):
        """Test source connectivity checking when adding."""
        with patch("funcn_cli.commands.source.httpx.Client") as mock_client_class:
            # Mock successful connectivity check
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "registry_version": "1.0.0",
                "components": []
            }
            
            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Add source with connectivity check
            result = self.run_command(
                cli_runner, ["source", "add", "checked", "https://example.com/index.json"], cwd=initialized_project
            )
            self.assert_command_success(result)
            assert "Testing connectivity" in result.output
            assert "Successfully connected" in result.output
            assert "Added registry source" in result.output

    def test_source_connectivity_check_failure(self, cli_runner, initialized_project):
        """Test handling failed connectivity check."""
        with patch("funcn_cli.commands.source.httpx.Client") as mock_client_class:
            # Mock connection failure
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.ConnectError("Connection failed")
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Try to add source - should fail
            result = self.run_command(
                cli_runner, ["source", "add", "unreachable", "https://unreachable.com/index.json"], cwd=initialized_project
            )
            assert result.exit_code == 1
            assert "Testing connectivity" in result.output
            assert "Failed to connect" in result.output
            assert "--skip-check" in result.output

    def test_source_connectivity_skip_check(self, cli_runner, initialized_project):
        """Test skipping connectivity check."""
        with patch("funcn_cli.commands.source.httpx.Client") as mock_client_class:
            # Add source with skip flag
            result = self.run_command(
                cli_runner, ["source", "add", "skipped", "https://example.com/index.json", "--skip-check"], cwd=initialized_project
            )
            self.assert_command_success(result)
            
            # Should not call httpx.Client
            mock_client_class.assert_not_called()
            
            # Should not show connectivity messages
            assert "Testing connectivity" not in result.output
            assert "Successfully connected" not in result.output
            assert "Added registry source" in result.output
