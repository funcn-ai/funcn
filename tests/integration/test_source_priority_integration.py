"""Integration tests for source priority and fallback mechanisms."""

from __future__ import annotations

import httpx
import json
import pytest
from funcn_cli.config_manager import ConfigManager, FuncnConfig
from funcn_cli.core.registry_handler import RegistryHandler
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch


@pytest.mark.integration
class TestSourcePriorityIntegration:
    """Test source priority and fallback behavior."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory."""
        with TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            yield project_dir

    @pytest.fixture
    def config_with_multiple_sources(self, temp_project_dir):
        """Create a config with multiple sources with different priorities."""
        config = FuncnConfig(
            default_registry_url="https://default.com/index.json",
            registry_sources={
                "high_priority": {
                    "url": "https://high.com/index.json",
                    "priority": 10,
                    "enabled": True
                },
                "medium_priority": {
                    "url": "https://medium.com/index.json", 
                    "priority": 50,
                    "enabled": True
                },
                "low_priority": {
                    "url": "https://low.com/index.json",
                    "priority": 200,
                    "enabled": True
                },
                "default": "https://default.com/index.json",  # Priority 100
                "disabled": {
                    "url": "https://disabled.com/index.json",
                    "priority": 5,
                    "enabled": False
                }
            },
            component_paths={"agents": "src/agents", "tools": "src/tools"}
        )
        
        # Save config to file
        config_path = temp_project_dir / "funcn.json"
        config_path.write_text(json.dumps(config.model_dump(), indent=2))
        
        return config, temp_project_dir

    def test_sources_tried_in_priority_order(self, config_with_multiple_sources):
        """Test that sources are tried in priority order when fetching."""
        config, project_dir = config_with_multiple_sources
        
        # Track which URLs were called
        called_urls = []
        
        def mock_get(url, *args, **kwargs):
            called_urls.append(url)
            # Simulate all sources being unavailable except the last one
            if "low.com" in url:
                response = MagicMock()
                response.status_code = 200
                response.json.return_value = {
                    "registry_version": "1.0.0",
                    "components": [{
                        "name": "test",
                        "type": "tool",
                        "version": "1.0.0",
                        "description": "Test component",
                        "manifest_path": "test/component.json"
                    }]
                }
                response.raise_for_status = MagicMock()
                return response
            else:
                raise httpx.ConnectError("Simulated connection error")
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = mock_get
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Create handler and fetch index
            cfg_manager = ConfigManager(project_root=project_dir)
            handler = RegistryHandler(cfg_manager)
            
            # Fetch from all sources
            indexes = handler.fetch_all_indexes(silent_errors=True)
            
            # Verify sources were tried in priority order (excluding disabled)
            assert len(called_urls) >= 4
            assert "high.com" in called_urls[0]  # Priority 10
            assert "medium.com" in called_urls[1]  # Priority 50
            assert "default.com" in called_urls[2]  # Priority 100 (default)
            assert "low.com" in called_urls[3]  # Priority 200
            
            # Disabled source should not be called
            assert not any("disabled.com" in url for url in called_urls)
            
            # Should get index from low priority source (the only one that succeeded)
            assert len(indexes) == 1
            assert "low_priority" in indexes
            assert len(indexes["low_priority"].components) == 1
            assert indexes["low_priority"].components[0].name == "test"

    def test_fallback_on_source_failure(self, config_with_multiple_sources):
        """Test fallback behavior when high priority sources fail."""
        config, project_dir = config_with_multiple_sources
        
        def mock_get(url, *args, **kwargs):
            response = MagicMock()
            
            if "high.com" in url:
                # High priority source returns 500 error
                raise httpx.HTTPStatusError(
                    "Server error", 
                    request=MagicMock(), 
                    response=MagicMock(status_code=500)
                )
            elif "medium.com" in url:
                # Medium priority source times out
                raise httpx.TimeoutException("Request timed out")
            elif "default.com" in url:
                # Default source works
                response.status_code = 200
                response.json.return_value = {
                    "registry_version": "1.0.0",
                    "components": [{
                        "name": "default-component",
                        "type": "agent",
                        "version": "1.0.0",
                        "description": "Default component",
                        "manifest_path": "default/component.json"
                    }]
                }
                response.raise_for_status = MagicMock()
                return response
            else:
                # Other sources fail
                raise httpx.ConnectError("Connection failed")
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = mock_get
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            cfg_manager = ConfigManager(project_root=project_dir)
            handler = RegistryHandler(cfg_manager)
            
            # Should fallback to default source
            indexes = handler.fetch_all_indexes(silent_errors=True)
            
            assert len(indexes) == 1
            assert "default" in indexes
            assert len(indexes["default"].components) == 1
            assert indexes["default"].components[0].name == "default-component"

    def test_component_deduplication_across_sources(self, config_with_multiple_sources):
        """Test that duplicate components across sources are deduplicated."""
        config, project_dir = config_with_multiple_sources
        
        def mock_get(url, *args, **kwargs):
            response = MagicMock()
            response.status_code = 200
            response.raise_for_status = MagicMock()
            
            if "high.com" in url:
                response.json.return_value = {
                    "registry_version": "1.0.0",
                    "components": [
                        {
                            "name": "shared-tool",
                            "type": "tool",
                            "version": "2.0.0",
                            "description": "Shared tool",
                            "manifest_path": "shared/tool.json"
                        },
                        {
                            "name": "high-only",
                            "type": "agent",
                            "version": "1.0.0",
                            "description": "High priority only",
                            "manifest_path": "high/agent.json"
                        }
                    ]
                }
            elif "medium.com" in url:
                response.json.return_value = {
                    "registry_version": "1.0.0", 
                    "components": [
                        {
                            "name": "shared-tool",
                            "type": "tool",
                            "version": "1.5.0",
                            "description": "Shared tool",
                            "manifest_path": "shared/tool.json"
                        },
                        {
                            "name": "medium-only",
                            "type": "tool",
                            "version": "1.0.0",
                            "description": "Medium priority only",
                            "manifest_path": "medium/tool.json"
                        }
                    ]
                }
            else:
                response.json.return_value = {
                    "registry_version": "1.0.0",
                    "components": []
                }
            
            return response
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = mock_get
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            cfg_manager = ConfigManager(project_root=project_dir)
            handler = RegistryHandler(cfg_manager)
            
            indexes = handler.fetch_all_indexes(silent_errors=True)
            
            # Should have indexes from both sources  
            assert len(indexes) >= 2
            
            # Collect all components across sources
            all_components = []
            for index in indexes.values():
                all_components.extend(index.components)
            
            # Check that we have components from both sources
            component_names = [c.name for c in all_components]
            assert "shared-tool" in component_names
            assert "high-only" in component_names
            assert "medium-only" in component_names
            
            # Note: deduplication happens at the command level, not in RegistryHandler
            # So we should see shared-tool from both sources
            shared_tools = [c for c in all_components if c.name == "shared-tool"]
            assert len(shared_tools) >= 1

    def test_single_source_request(self, config_with_multiple_sources):
        """Test fetching from a specific source only."""
        config, project_dir = config_with_multiple_sources
        
        called_urls = []
        
        def mock_get(url, *args, **kwargs):
            called_urls.append(url)
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "registry_version": "1.0.0",
                "components": [{
                    "name": f"component-from-{url.split('/')[2]}",
                    "type": "tool",
                    "version": "1.0.0",
                    "description": "Test component",
                    "manifest_path": "test/component.json"
                }]
            }
            response.raise_for_status = MagicMock()
            return response
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = mock_get
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            cfg_manager = ConfigManager(project_root=project_dir)
            handler = RegistryHandler(cfg_manager)
            
            # Fetch from specific source
            index = handler.fetch_index(source_alias="medium_priority")
            
            # Should only call the specified source
            assert len(called_urls) == 1
            assert "medium.com" in called_urls[0]
            
            # Should get component from that source
            assert index is not None
            assert len(index.components) == 1
            assert "component-from-medium.com" in index.components[0].name

    def test_cache_with_priority_sources(self, config_with_multiple_sources):
        """Test that caching works correctly with multiple prioritized sources."""
        config, project_dir = config_with_multiple_sources
        
        # Enable caching
        config.cache_config.enabled = True
        config.cache_config.ttl_seconds = 3600
        
        # Save updated config
        config_path = project_dir / "funcn.json"
        config_path.write_text(json.dumps(config.model_dump(), indent=2))
        
        call_count = 0
        
        def mock_get(url, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = {
                "registry_version": "1.0.0",
                "components": [{
                    "name": f"cached-{call_count}",
                    "type": "tool",
                    "version": "1.0.0",
                    "description": "Cached component",
                    "manifest_path": "cached/component.json"
                }]
            }
            response.headers = {"ETag": f"etag-{call_count}"}
            response.raise_for_status = MagicMock()
            return response
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = mock_get
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            cfg_manager = ConfigManager(project_root=project_dir)
            handler = RegistryHandler(cfg_manager)
            
            # First fetch - should hit network
            indexes1 = handler.fetch_all_indexes(silent_errors=True)
            initial_call_count = call_count
            
            # Second fetch - should use cache
            indexes2 = handler.fetch_all_indexes(silent_errors=True)
            
            # Should not make additional network calls
            assert call_count == initial_call_count
            
            # Results should be the same
            assert len(indexes1) == len(indexes2)
            assert set(indexes1.keys()) == set(indexes2.keys())

    def test_negative_priority_sources(self, temp_project_dir):
        """Test that negative priorities work correctly (higher priority)."""
        config = FuncnConfig(
            default_registry_url="https://default.com/index.json",
            registry_sources={
                "urgent": {
                    "url": "https://urgent.com/index.json",
                    "priority": -10,
                    "enabled": True
                },
                "normal": {
                    "url": "https://normal.com/index.json",
                    "priority": 50,
                    "enabled": True
                },
                "default": "https://default.com/index.json"
            },
            component_paths={"agents": "src/agents", "tools": "src/tools"}
        )
        
        config_path = temp_project_dir / "funcn.json"
        config_path.write_text(json.dumps(config.model_dump(), indent=2))
        
        called_urls = []
        
        def mock_get(url, *args, **kwargs):
            called_urls.append(url)
            raise httpx.ConnectError("All sources fail")
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = mock_get
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            cfg_manager = ConfigManager(project_root=config_path.parent)
            handler = RegistryHandler(cfg_manager)
            
            # Try to fetch (will fail but we check order)
            handler.fetch_all_indexes(silent_errors=True)
            
            # Verify urgent source (negative priority) was tried first
            assert len(called_urls) >= 2
            assert "urgent.com" in called_urls[0]
            assert "normal.com" in called_urls[1]

    def test_source_metadata_caching(self, config_with_multiple_sources):
        """Test that source metadata (updated_at, etag) is cached correctly."""
        config, project_dir = config_with_multiple_sources
        
        # Enable caching with very short TTL
        config.cache_config.enabled = True
        config.cache_config.ttl_seconds = 0  # Expire immediately
        config_path = project_dir / "funcn.json"
        config_path.write_text(json.dumps(config.model_dump(), indent=2))
        
        # Track ETag headers sent
        sent_etags = {}
        
        def mock_get(url, headers=None, *args, **kwargs):
            if headers and "If-None-Match" in headers:
                sent_etags[url] = headers["If-None-Match"]
            
            response = MagicMock()
            
            # Return 304 if ETag matches
            if url in sent_etags and sent_etags[url] == f"etag-{url}":
                response.status_code = 304
                response.raise_for_status = MagicMock()
                return response
            
            # Otherwise return fresh data
            response.status_code = 200
            response.json.return_value = {
                "registry_version": "1.0.0",
                "updated_at": "2024-01-01T00:00:00Z",
                "components": [{
                    "name": "test",
                    "type": "tool",
                    "version": "1.0.0",
                    "description": "Test component",
                    "manifest_path": "test/component.json"
                }]
            }
            response.headers = {"ETag": f"etag-{url}"}
            response.raise_for_status = MagicMock()
            return response
        
        with patch("funcn_cli.core.registry_handler.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = mock_get
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            cfg_manager = ConfigManager(project_root=config_path.parent)
            handler = RegistryHandler(cfg_manager)
            
            # First fetch - gets fresh data
            handler.fetch_all_indexes(silent_errors=True)
            
            # Second fetch - should send ETag headers
            handler.fetch_all_indexes(silent_errors=True)
            
            # Verify ETags were sent on second request
            assert len(sent_etags) > 0
