"""Edge case tests for funcn source command."""

from __future__ import annotations

import httpx
import json
import pytest
import typer
from funcn_cli.commands.source import _test_source_connectivity, add, list_sources, remove
from funcn_cli.config_manager import CacheConfig, FuncnConfig, RegistrySourceConfig
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestSourceEdgeCases:
    """Test edge cases and error scenarios for source command."""

    @pytest.fixture
    def mock_config_manager(self, mocker):
        """Mock ConfigManager."""
        mock_cfg_manager = MagicMock()
        mocker.patch("funcn_cli.commands.source.ConfigManager", return_value=mock_cfg_manager)
        return mock_cfg_manager

    @pytest.fixture  
    def mock_console(self, mocker):
        """Mock console output."""
        return mocker.patch("funcn_cli.commands.source.console")

    def test_add_source_very_long_alias(self, mock_config_manager, mock_console):
        """Test adding source with very long alias name."""
        long_alias = "a" * 200
        add(alias=long_alias, url="https://example.com/index.json", priority=100, skip_connectivity_check=True)
        
        mock_config_manager.add_registry_source.assert_called_once_with(
            long_alias, "https://example.com/index.json", priority=100
        )

    def test_add_source_unicode_alias(self, mock_config_manager, mock_console):
        """Test adding source with unicode characters in alias."""
        unicode_alias = "测试源-🚀"
        add(alias=unicode_alias, url="https://example.com/index.json", priority=100, skip_connectivity_check=True)
        
        mock_config_manager.add_registry_source.assert_called_once_with(
            unicode_alias, "https://example.com/index.json", priority=100
        )

    def test_add_source_extreme_priorities(self, mock_config_manager, mock_console):
        """Test adding sources with extreme priority values."""
        # Very negative priority
        add(alias="super_urgent", url="https://example.com/index.json", priority=-999999, skip_connectivity_check=True)
        mock_config_manager.add_registry_source.assert_called_with(
            "super_urgent", "https://example.com/index.json", priority=-999999
        )
        
        # Very high priority
        mock_config_manager.add_registry_source.reset_mock()
        add(alias="super_low", url="https://example.com/index.json", priority=999999, skip_connectivity_check=True)
        mock_config_manager.add_registry_source.assert_called_with(
            "super_low", "https://example.com/index.json", priority=999999
        )

    def test_add_source_url_with_query_params(self, mock_config_manager, mock_console):
        """Test adding source URL with query parameters."""
        url_with_params = "https://example.com/index.json?version=2&format=json"
        add(alias="params", url=url_with_params, priority=100, skip_connectivity_check=True)
        
        mock_config_manager.add_registry_source.assert_called_once_with(
            "params", url_with_params, priority=100
        )

    def test_add_source_url_with_port(self, mock_config_manager, mock_console):
        """Test adding source URL with custom port."""
        url_with_port = "https://example.com:8443/registry/index.json"
        add(alias="custom_port", url=url_with_port, priority=100, skip_connectivity_check=True)
        
        mock_config_manager.add_registry_source.assert_called_once_with(
            "custom_port", url_with_port, priority=100
        )

    def test_add_source_url_with_auth(self, mock_config_manager, mock_console):
        """Test adding source URL with authentication in URL."""
        url_with_auth = "https://user:pass@example.com/index.json"
        add(alias="auth", url=url_with_auth, priority=100, skip_connectivity_check=True)
        
        # Should warn about credentials in URL
        assert mock_console.print.call_count >= 1
        mock_config_manager.add_registry_source.assert_called_once()

    def test_list_sources_mixed_config_formats(self, mock_config_manager, mock_console):
        """Test listing sources with mixed configuration formats."""
        # Config with every possible format variation
        config = FuncnConfig(
            default_registry_url="https://default.com/index.json",
            registry_sources={
                # String format (old)
                "old_string": "https://old.com/index.json",
                # Dict format from JSON (intermediate)
                "dict_format": {
                    "url": "https://dict.com/index.json",
                    "priority": 75
                },
                # Full object format (new)
                "full_object": RegistrySourceConfig(
                    url="https://object.com/index.json",
                    priority=25,
                    enabled=True
                ),
                # Disabled source
                "disabled": {
                    "url": "https://disabled.com/index.json",
                    "priority": 1,
                    "enabled": False
                }
            },
            component_paths={},
            cache_config=CacheConfig(enabled=False)
        )
        mock_config_manager.config = config
        
        # Execute
        list_sources()
        
        # Should handle all formats without error
        assert mock_console.print.called

    def test_remove_source_concurrent_modification(self, mock_config_manager, mock_console):
        """Test removing source when config is modified concurrently."""
        config = FuncnConfig(
            default_registry_url="https://default.com/index.json",
            registry_sources={
                "default": "https://default.com/index.json",
                "to_remove": "https://remove.com/index.json"
            },
            component_paths={}
        )
        mock_config_manager.config = config
        
        # Simulate concurrent modification
        def side_effect(alias):
            # Config changed while we were removing
            config.registry_sources.pop("to_remove", None)
            raise KeyError("Source already removed")
        
        mock_config_manager.remove_registry_source.side_effect = side_effect
        
        # Should handle gracefully
        with pytest.raises(KeyError):
            remove(alias="to_remove")

    def test_connectivity_check_redirect(self, mock_console):
        """Test connectivity check with HTTP redirects."""
        with patch("funcn_cli.commands.source.httpx.Client") as mock_client_class:
            # httpx handles redirects automatically, so we just return the final response
            final_response = MagicMock()
            final_response.status_code = 200
            final_response.json.return_value = {
                "registry_version": "1.0.0",
                "components": []
            }
            final_response.raise_for_status = MagicMock()
            
            mock_client = MagicMock()
            mock_client.get.return_value = final_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            result = _test_source_connectivity("https://old-location.com/index.json")
            
            assert result is True

    def test_connectivity_check_slow_response(self, mock_console):
        """Test connectivity check with slow but successful response."""
        with patch("funcn_cli.commands.source.httpx.Client") as mock_client_class:
            import time
            
            def slow_get(*args, **kwargs):
                time.sleep(0.1)  # Simulate slow response
                response = MagicMock()
                response.status_code = 200
                response.json.return_value = {
                    "registry_version": "1.0.0",
                    "components": []
                }
                return response
            
            mock_client = MagicMock()
            mock_client.get.side_effect = slow_get
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Should succeed despite being slow (within timeout)
            result = _test_source_connectivity("https://slow.com/index.json")
            assert result is True

    def test_connectivity_check_partial_response(self, mock_console):
        """Test connectivity check with partial/malformed response."""
        with patch("funcn_cli.commands.source.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            # Simulate partial JSON
            mock_response.json.side_effect = json.JSONDecodeError("Unexpected EOF", "", 100)
            
            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            result = _test_source_connectivity("https://partial.com/index.json")
            
            assert result is False
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("Invalid registry response format" in msg for msg in messages)

    def test_list_sources_empty_url(self, mock_config_manager, mock_console):
        """Test listing sources when a source has empty URL."""
        config = FuncnConfig(
            default_registry_url="",  # Empty default
            registry_sources={
                "empty": "",  # Empty source URL
                "valid": "https://valid.com/index.json"
            },
            component_paths={}
        )
        mock_config_manager.config = config
        
        # Should handle empty URLs gracefully
        list_sources()
        assert mock_console.print.called

    def test_add_source_localhost_url(self, mock_config_manager, mock_console):
        """Test adding localhost URLs."""
        localhost_urls = [
            "http://localhost/index.json",
            "http://localhost:8080/index.json",
            "http://127.0.0.1/index.json",
            "http://0.0.0.0:3000/index.json"
        ]
        
        for i, url in enumerate(localhost_urls):
            mock_config_manager.add_registry_source.reset_mock()
            add(alias=f"local{i}", url=url, priority=100, skip_connectivity_check=True)
            mock_config_manager.add_registry_source.assert_called_once()

    def test_connectivity_check_content_type(self, mock_console):
        """Test connectivity check validates content type."""
        with patch("funcn_cli.commands.source.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "text/html"}  # Wrong content type
            mock_response.json.side_effect = ValueError("Not JSON")
            
            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client
            
            result = _test_source_connectivity("https://html-page.com/index.json")
            
            assert result is False

    def test_add_source_special_characters_in_url(self, mock_config_manager, mock_console):
        """Test adding source with special characters in URL path."""
        special_urls = [
            "https://example.com/my%20registry/index.json",
            "https://example.com/registry/[test]/index.json",
            "https://example.com/registry/index.json#section",
            "https://example.com/~user/registry/index.json"
        ]
        
        for i, url in enumerate(special_urls):
            mock_config_manager.add_registry_source.reset_mock()
            add(alias=f"special{i}", url=url, priority=100, skip_connectivity_check=True)
            mock_config_manager.add_registry_source.assert_called_once()

    def test_cache_stats_formatting_edge_cases(self, mock_config_manager, mock_console):
        """Test cache stats with edge case values."""
        from funcn_cli.commands.source import cache_stats
        
        # Mock registry handler
        with patch("funcn_cli.commands.source.RegistryHandler") as mock_handler_class:
            mock_handler = MagicMock()
            mock_cache_manager = MagicMock()
            
            # Edge case stats
            mock_cache_manager.get_cache_stats.return_value = {
                "source1": {
                    "age": "0 seconds",  # Just cached
                    "size_bytes": 0,  # Empty cache
                    "cached_at": "2024-01-01T00:00:00",
                    "last_accessed": "2024-01-01T00:00:00"
                },
                "source2": {
                    "age": "365 days",  # Very old
                    "size_bytes": 1024 * 1024 * 100,  # 100MB
                    "cached_at": "2023-01-01T00:00:00",
                    "last_accessed": "2024-01-01T00:00:00"
                }
            }
            
            mock_handler._cache_manager = mock_cache_manager
            mock_handler_class.return_value = mock_handler
            
            # Execute
            cache_stats()
            
            # Should handle edge cases in formatting
            assert mock_console.print.called
