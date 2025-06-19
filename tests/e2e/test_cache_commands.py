"""E2E tests for cache commands."""

from __future__ import annotations

import json
import os
import pytest
from funcn_cli.main import app
from pathlib import Path
from tempfile import TemporaryDirectory
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch


class TestCacheCommands:
    """E2E tests for cache-related commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with funcn.json."""
        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            
            # Create initial funcn.json with cache enabled
            funcn_config = {
                "default_registry_url": "https://raw.githubusercontent.com/funcn-ai/funcn-registry/main/index.json",
                "registry_sources": {
                    "default": "https://raw.githubusercontent.com/funcn-ai/funcn-registry/main/index.json"
                },
                "component_paths": {
                    "agents": "src/agents",
                    "tools": "src/tools"
                },
                "cache_config": {
                    "enabled": True,
                    "ttl_seconds": 3600,
                    "directory": str(project_dir / ".funcn" / "cache")
                }
            }
            
            (project_dir / "funcn.json").write_text(json.dumps(funcn_config, indent=2))
            yield project_dir
    
    def run_command(self, runner: CliRunner, command: list[str], cwd: Path | None = None):
        """Run a CLI command and return the result."""
        if cwd:
            original_cwd = Path.cwd()
            try:
                os.chdir(cwd)
                result = runner.invoke(app, command)
                return result
            finally:
                os.chdir(original_cwd)
        else:
            result = runner.invoke(app, command)
            return result
    
    def test_source_list_shows_cache_column(self, runner, temp_project):
        """Test that source list shows cache column."""
        result = self.run_command(runner, ["source", "list"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Cache" in result.output
        assert "Cache TTL:" in result.output
        assert "3600s" in result.output
    
    def test_source_list_refresh_flag(self, runner, temp_project):
        """Test source list with --refresh flag."""
        result = self.run_command(runner, ["source", "list", "--refresh"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Refreshing cache..." in result.output
    
    def test_cache_clear_all(self, runner, temp_project):
        """Test clearing all caches."""
        result = self.run_command(runner, ["source", "cache", "clear"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Cleared all registry caches" in result.output
    
    def test_cache_clear_specific_source(self, runner, temp_project):
        """Test clearing cache for specific source."""
        result = self.run_command(runner, ["source", "cache", "clear", "default"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Cleared cache for 'default'" in result.output
    
    def test_cache_stats_empty(self, runner, temp_project):
        """Test cache stats when no cache exists."""
        result = self.run_command(runner, ["source", "cache", "stats"], cwd=temp_project)
        assert result.exit_code == 0
        assert "No cached data found" in result.output
    
    @patch("funcn_cli.core.registry_handler.httpx.Client")
    def test_cache_stats_with_data(self, mock_client_class, runner, temp_project):
        """Test cache stats after fetching data."""
        # Setup mock to return valid index data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "registry_version": "1.0.0",
            "updated_at": "2024-01-01T00:00:00Z",
            "components": []
        }
        mock_response.headers = {"ETag": "test-etag"}
        
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # First, list components to populate cache
        self.run_command(runner, ["list"], cwd=temp_project)
        
        # Now check stats
        result = self.run_command(runner, ["source", "cache", "stats"], cwd=temp_project)
        assert result.exit_code == 0
        assert "Registry Cache Statistics" in result.output
        assert "default" in result.output
        assert "KB" in result.output
        assert "Total cache size:" in result.output
    
    def test_cache_disabled_message(self, runner):
        """Test cache commands when caching is disabled."""
        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            
            # Create funcn.json with cache disabled
            funcn_config = {
                "default_registry_url": "https://example.com/index.json",
                "cache_config": {
                    "enabled": False
                }
            }
            
            (project_dir / "funcn.json").write_text(json.dumps(funcn_config, indent=2))
            
            # Try cache stats
            result = self.run_command(runner, ["source", "cache", "stats"], cwd=project_dir)
            assert result.exit_code == 0
            assert "Cache is disabled in configuration" in result.output
            
            # Try cache clear
            result = self.run_command(runner, ["source", "cache", "clear"], cwd=project_dir)
            assert result.exit_code == 0
            assert "Cache is disabled in configuration" in result.output
    
    @patch("funcn_cli.core.registry_handler.httpx.Client")
    def test_list_components_with_refresh(self, mock_client_class, runner, temp_project):
        """Test list components with --refresh flag."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "registry_version": "1.0.0",
            "updated_at": "2024-01-01T00:00:00Z",
            "components": [
                {
                    "name": "test-component",
                    "version": "1.0.0",
                    "type": "tool",
                    "description": "Test",
                    "manifest_path": "test.json"
                }
            ]
        }
        
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # First fetch
        result1 = self.run_command(runner, ["list"], cwd=temp_project)
        assert result1.exit_code == 0
        assert "test-component" in result1.output
        
        # Second fetch with refresh
        result2 = self.run_command(runner, ["list", "--refresh"], cwd=temp_project)
        assert result2.exit_code == 0
        assert "test-component" in result2.output
        
        # Should have made 2 network calls
        assert mock_client.get.call_count == 2
    
    @patch("funcn_cli.core.registry_handler.httpx.Client")
    def test_list_components_with_cache_ttl_override(self, mock_client_class, runner, temp_project):
        """Test list components with --cache-ttl override."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "registry_version": "1.0.0",
            "updated_at": "2024-01-01T00:00:00Z",
            "components": []
        }
        
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # List with custom TTL
        result = self.run_command(runner, ["list", "--cache-ttl", "7200"], cwd=temp_project)
        assert result.exit_code == 0
    
    @patch("funcn_cli.core.registry_handler.httpx.Client")
    def test_cache_survives_between_commands(self, mock_client_class, runner, temp_project):
        """Test that cache persists between command invocations."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "registry_version": "1.0.0",
            "updated_at": "2024-01-01T00:00:00Z",
            "components": []
        }
        mock_response.headers = {"ETag": "test-etag"}
        
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # First command - populates cache
        result1 = self.run_command(runner, ["list"], cwd=temp_project)
        assert result1.exit_code == 0
        initial_call_count = mock_client.get.call_count
        
        # Second command - should use cache
        result2 = self.run_command(runner, ["list"], cwd=temp_project)
        assert result2.exit_code == 0
        assert mock_client.get.call_count == initial_call_count  # No additional calls
        
        # Check cache stats to confirm cache exists
        result3 = self.run_command(runner, ["source", "cache", "stats"], cwd=temp_project)
        assert result3.exit_code == 0
        assert "default" in result3.output
