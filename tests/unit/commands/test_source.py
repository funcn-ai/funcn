"""Tests for the sygaldry source command."""

from __future__ import annotations

import httpx
import pytest
import typer
from sygaldry_cli.commands.source import _test_source_connectivity, add, cache_clear, cache_stats, list_sources, remove
from sygaldry_cli.config_manager import CacheConfig, SygaldryConfig
from unittest.mock import MagicMock, patch


class TestSource:
    """Test the sygaldry source command and its subcommands."""

    @pytest.fixture
    def mock_config_manager(self, mocker):
        """Mock ConfigManager."""
        mock_cfg_manager = MagicMock()
        mocker.patch("sygaldry_cli.commands.source.ConfigManager", return_value=mock_cfg_manager)
        return mock_cfg_manager

    @pytest.fixture
    def mock_console(self, mocker):
        """Mock console output."""
        return mocker.patch("sygaldry_cli.commands.source.console")

    @pytest.fixture
    def sample_config(self):
        """Sample configuration with registry sources."""
        return SygaldryConfig(
            default_registry_url="https://raw.githubusercontent.com/sygaldry-ai/sygaldry-registry/main/index.json",
            registry_sources={
                "default": "https://raw.githubusercontent.com/sygaldry-ai/sygaldry-registry/main/index.json",
                "custom": "https://example.com/custom/index.json",
                "local": "file:///path/to/local/index.json",
            },
            component_paths={"agents": "./src/agents", "tools": "./src/tools"},
            enable_lilypad=False,
        )

    def test_add_source_project_level(self, mock_config_manager, mock_console):
        """Test adding a registry source at project level."""
        # Execute with skip connectivity check to simplify test
        add(alias="test", url="https://test.com/index.json", priority=100, skip_connectivity_check=True)

        # Verify - default priority is 100
        mock_config_manager.add_registry_source.assert_called_once_with("test", "https://test.com/index.json", priority=100)
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source 'test' -> https://test.com/index.json" in printed_msg

    def test_add_source_global_level(self, mock_config_manager, mock_console):
        """Test adding a registry source at global level."""
        # Execute
        add(alias="global_test", url="https://global.com/index.json", priority=100, skip_connectivity_check=True)

        # Verify
        mock_config_manager.add_registry_source.assert_called_once_with("global_test", "https://global.com/index.json", priority=100)
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source 'global_test' -> https://global.com/index.json" in printed_msg

    def test_add_source_with_special_characters(self, mock_config_manager, mock_console):
        """Test adding a source with special characters in alias."""
        # Execute
        add(alias="test-source_123", url="https://test.com/index.json", priority=100, skip_connectivity_check=True)

        # Verify
        mock_config_manager.add_registry_source.assert_called_once_with("test-source_123", "https://test.com/index.json", priority=100)

    def test_add_source_with_file_url(self, mock_config_manager, mock_console):
        """Test adding a source with file:// URL."""
        # Execute
        add(alias="local", url="file:///home/user/registry/index.json", priority=100, skip_connectivity_check=True)

        # Verify
        mock_config_manager.add_registry_source.assert_called_once_with("local", "file:///home/user/registry/index.json", priority=100)

    def test_list_sources_with_multiple_sources(self, mock_config_manager, mock_console, sample_config):
        """Test listing multiple registry sources."""
        # Setup
        mock_config_manager.config = sample_config

        # Execute
        list_sources()

        # Verify table was printed
        assert mock_console.print.called
        # Get all print calls
        print_calls = mock_console.print.call_args_list
        # Find the table in the print calls
        printed_table = None
        for call in print_calls:
            if hasattr(call[0][0], 'title') and hasattr(call[0][0], 'columns'):
                printed_table = call[0][0]
                break
        assert printed_table is not None
        assert printed_table.title == "Registry Sources"
        assert len(printed_table.columns) == 5
        assert printed_table.columns[0].header == "Alias"
        assert printed_table.columns[1].header == "URL"
        assert printed_table.columns[2].header == "Priority"
        assert printed_table.columns[3].header == "Status"
        assert printed_table.columns[4].header == "Cache"

    def test_list_sources_empty(self, mock_config_manager, mock_console):
        """Test listing sources when none are configured."""
        # Setup
        empty_config = SygaldryConfig(
            default_registry_url="",
            registry_sources={},
            component_paths={},
            enable_lilypad=False,
        )
        mock_config_manager.config = empty_config

        # Execute
        list_sources()

        # Verify empty table was printed
        assert mock_console.print.called
        # Get all print calls
        print_calls = mock_console.print.call_args_list
        # Find the table in the print calls
        printed_table = None
        for call in print_calls:
            if hasattr(call[0][0], 'title') and hasattr(call[0][0], 'columns'):
                printed_table = call[0][0]
                break
        assert printed_table is not None
        assert printed_table.title == "Registry Sources"

    def test_list_sources_default_marked(self, mock_config_manager, mock_console, sample_config):
        """Test that default source is marked correctly."""
        # Setup
        mock_config_manager.config = sample_config

        # Capture table rows
        captured_rows = []

        def capture_add_row(*args):
            captured_rows.append(args)

        # Execute with row capture
        from unittest.mock import patch

        with patch("sygaldry_cli.commands.source.Table") as mock_table_class:
            mock_table = MagicMock()
            mock_table.add_row = MagicMock(side_effect=capture_add_row)
            mock_table_class.return_value = mock_table

            list_sources()

        # Verify default is marked
        default_found = False
        for row in captured_rows:
            if "[bold]default[/]" in row[0] or row[0] == "default":
                default_found = True
                # Verify it's pointing to the correct URL
                # Now table has 5 columns: Alias, URL, Priority, Status, Cache
                assert len(row) == 5
                assert sample_config.default_registry_url in row[1]

        assert default_found, "Default source should be marked"

    def test_list_sources_ordering(self, mock_config_manager, mock_console):
        """Test that sources are listed in a consistent order."""
        # Setup with sources that would have different ordering
        config = SygaldryConfig(
            default_registry_url="https://default.com/index.json",
            registry_sources={
                "zebra": "https://zebra.com/index.json",
                "alpha": "https://alpha.com/index.json",
                "beta": "https://beta.com/index.json",
                "default": "https://default.com/index.json",
            },
            component_paths={},
            enable_lilypad=False,
        )
        mock_config_manager.config = config

        # Capture table rows
        captured_rows = []

        def capture_add_row(*args):
            captured_rows.append(args)

        # Execute with row capture
        from unittest.mock import patch

        with patch("sygaldry_cli.commands.source.Table") as mock_table_class:
            mock_table = MagicMock()
            mock_table.add_row = MagicMock(side_effect=capture_add_row)
            mock_table_class.return_value = mock_table

            list_sources()

        # Verify all sources are present
        assert len(captured_rows) == 4
        aliases = [row[0].replace(" (default)", "").replace("[bold]", "").replace("[/]", "") for row in captured_rows]
        assert set(aliases) == {"zebra", "alpha", "beta", "default"}

    def test_add_source_url_variations(self, mock_config_manager, mock_console):
        """Test adding sources with various URL formats."""
        test_urls = [
            "https://example.com/index.json",
            "http://example.com/index.json",
            "file:///absolute/path/index.json",
            "file://relative/path/index.json",
            "https://example.com:8080/path/to/index.json",
            "https://user:pass@example.com/index.json",
        ]

        for i, url in enumerate(test_urls):
            # Reset mock
            mock_config_manager.add_registry_source.reset_mock()
            mock_console.print.reset_mock()

            # Execute
            add(alias=f"test{i}", url=url, priority=100, skip_connectivity_check=True)

            # Verify
            mock_config_manager.add_registry_source.assert_called_once_with(f"test{i}", url, priority=100)

    def test_add_source_error_handling(self, mock_config_manager, mock_console):
        """Test error handling when adding a source fails."""
        # Setup - simulate error
        mock_config_manager.add_registry_source.side_effect = Exception("Failed to add source")

        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Failed to add source"):
            add(alias="error_test", url="https://test.com/index.json", priority=100, skip_connectivity_check=True)

    def test_list_sources_with_long_urls(self, mock_config_manager, mock_console):
        """Test listing sources with very long URLs."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={
                "long": "https://very-long-domain-name.example.com/with/very/deep/path/structure/to/test/table/formatting/index.json",
                "short": "https://ex.co/i.json",
            },
            component_paths={},
            enable_lilypad=False,
        )
        mock_config_manager.config = config

        # Execute
        list_sources()

        # Verify table was printed without errors
        assert mock_console.print.called

    def test_remove_source_success(self, mock_config_manager, mock_console):
        """Test successfully removing a registry source."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={
                "default": "https://example.com/index.json",
                "custom": "https://custom.com/index.json",
                "local": "file:///path/to/local/index.json",
            },
            component_paths={},
        )
        mock_config_manager.config = config

        # Execute
        remove(alias="custom")

        # Verify
        mock_config_manager.remove_registry_source.assert_called_once_with("custom")
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Removed registry source 'custom'" in printed_msg

    def test_remove_source_not_found(self, mock_config_manager, mock_console):
        """Test removing a non-existent registry source."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={
                "default": "https://example.com/index.json",
            },
            component_paths={},
        )
        mock_config_manager.config = config

        # Execute and verify exception is raised
        with pytest.raises(typer.Exit) as exc_info:
            remove(alias="nonexistent")

        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Registry source 'nonexistent' not found" in printed_msg

    def test_remove_last_remaining_source(self, mock_config_manager, mock_console):
        """Test preventing removal of the only remaining registry source."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={
                "default": "https://example.com/index.json",
            },
            component_paths={},
        )
        mock_config_manager.config = config

        # Execute and verify exception is raised
        with pytest.raises(typer.Exit) as exc_info:
            remove(alias="default")

        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Cannot remove the only remaining registry source" in printed_msg

    def test_remove_source_with_multiple_sources(self, mock_config_manager, mock_console):
        """Test removing a source when multiple sources exist."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={
                "default": "https://example.com/index.json",
                "backup": "https://backup.com/index.json",
                "test": "https://test.com/index.json",
            },
            component_paths={},
        )
        mock_config_manager.config = config

        # Execute
        remove(alias="test")

        # Verify
        mock_config_manager.remove_registry_source.assert_called_once_with("test")
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Removed registry source 'test'" in printed_msg

    def test_remove_default_source_with_other_sources(self, mock_config_manager, mock_console):
        """Test that default source can be removed if other sources exist."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={
                "default": "https://example.com/index.json",
                "alternative": "https://alternative.com/index.json",
            },
            component_paths={},
        )
        mock_config_manager.config = config

        # Execute - should succeed since there's another source
        remove(alias="default")

        # Verify
        mock_config_manager.remove_registry_source.assert_called_once_with("default")
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Removed registry source 'default'" in printed_msg

    def test_add_source_invalid_scheme(self, mock_config_manager, mock_console):
        """Test adding source with invalid URL scheme."""
        # Execute and verify exception is raised
        with pytest.raises(typer.Exit) as exc_info:
            add(alias="invalid", url="ftp://example.com/index.json", priority=100, skip_connectivity_check=True)

        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Invalid URL scheme" in printed_msg
        assert "ftp" in printed_msg

    def test_add_source_missing_domain(self, mock_config_manager, mock_console):
        """Test adding source with missing domain."""
        # Execute and verify exception is raised
        with pytest.raises(typer.Exit) as exc_info:
            add(alias="nodomain", url="https://", priority=100, skip_connectivity_check=True)

        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "missing domain/host" in printed_msg

    def test_add_source_warns_non_index_url(self, mock_config_manager, mock_console):
        """Test warning when URL doesn't end with index.json."""
        # Execute - should succeed but warn
        add(alias="nonindex", url="https://example.com/registry", priority=100, skip_connectivity_check=True)

        # Should have two print calls - warning and success
        assert mock_console.print.call_count == 2
        warning_msg = str(mock_console.print.call_args_list[0][0][0])
        success_msg = str(mock_console.print.call_args_list[1][0][0])

        assert "should typically point to an index.json file" in warning_msg
        assert "Added registry source" in success_msg

        # Should still add the source
        mock_config_manager.add_registry_source.assert_called_once_with("nonindex", "https://example.com/registry", priority=100)

    def test_add_source_accepts_index_json(self, mock_config_manager, mock_console):
        """Test that URL ending with index.json doesn't warn."""
        # Execute
        add(alias="proper", url="https://example.com/index.json", priority=100, skip_connectivity_check=True)

        # Should only have one print call (success, no warning)
        assert mock_console.print.call_count == 1
        success_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source" in success_msg

        # Should add the source
        mock_config_manager.add_registry_source.assert_called_once_with("proper", "https://example.com/index.json", priority=100)

    def test_add_source_accepts_file_scheme(self, mock_config_manager, mock_console):
        """Test that file:// URLs are accepted."""
        # Execute
        add(alias="local", url="file:///path/to/index.json", priority=100, skip_connectivity_check=True)

        # Should succeed
        assert mock_console.print.call_count == 1
        success_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source" in success_msg

        # Should add the source
        mock_config_manager.add_registry_source.assert_called_once_with("local", "file:///path/to/index.json", priority=100)

    def test_add_source_with_connectivity_check_success(self, mock_config_manager, mock_console):
        """Test adding source with successful connectivity check."""
        # Mock the console and config manager correctly
        mock_console.print.reset_mock()

        # Need to mock _test_source_connectivity directly since it has its own console
        with patch("sygaldry_cli.commands.source._test_source_connectivity") as mock_test_connectivity:
            mock_test_connectivity.return_value = True

            # Execute with defaults
            add(alias="valid", url="https://example.com/index.json", priority=100, skip_connectivity_check=False)

            # Should call connectivity test
            mock_test_connectivity.assert_called_once_with("https://example.com/index.json")

            # Should have print calls
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("Testing connectivity" in msg for msg in messages)
            assert any("Successfully connected" in msg for msg in messages)
            assert any("Added registry source" in msg for msg in messages)

            # Should add the source
            mock_config_manager.add_registry_source.assert_called_once_with("valid", "https://example.com/index.json", priority=100)

    def test_add_source_with_connectivity_check_failure(self, mock_config_manager, mock_console):
        """Test adding source with failed connectivity check."""
        # Mock _test_source_connectivity to return False
        with patch("sygaldry_cli.commands.source._test_source_connectivity") as mock_test_connectivity:
            mock_test_connectivity.return_value = False

            # Execute and verify exception is raised
            with pytest.raises(typer.Exit) as exc_info:
                add(alias="unreachable", url="https://unreachable.com/index.json", priority=100, skip_connectivity_check=False)

            assert exc_info.value.exit_code == 1

            # Should call connectivity test
            mock_test_connectivity.assert_called_once_with("https://unreachable.com/index.json")

            # Should print error messages
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("Testing connectivity" in msg for msg in messages)
            assert any("Failed to connect" in msg for msg in messages)
            assert any("--skip-check" in msg for msg in messages)

            # Should NOT add the source
            mock_config_manager.add_registry_source.assert_not_called()

    def test_add_source_skip_connectivity_check(self, mock_config_manager, mock_console):
        """Test adding source with connectivity check skipped."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            # Execute with skip flag
            add(alias="skipped", url="https://example.com/index.json", priority=100, skip_connectivity_check=True)

            # httpx.Client should not be called
            mock_client_class.assert_not_called()

            # Should only have 1 print call (added message)
            assert mock_console.print.call_count == 1
            success_msg = str(mock_console.print.call_args[0][0])
            assert "Added registry source" in success_msg

            # Should add the source
            mock_config_manager.add_registry_source.assert_called_once_with("skipped", "https://example.com/index.json", priority=100)

    def test_connectivity_check_timeout(self, mock_console):
        """Test connectivity check with timeout."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.TimeoutException("Request timed out")
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://slow.com/index.json")

            assert result is False
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("timed out" in msg for msg in messages)

    def test_connectivity_check_invalid_json(self, mock_console):
        """Test connectivity check with invalid JSON response."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")

            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://invalid.com/index.json")

            assert result is False
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("Invalid registry response format" in msg for msg in messages)

    def test_connectivity_check_missing_fields(self, mock_console):
        """Test connectivity check with missing required fields."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            # Test missing registry_version
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"components": []}

            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://incomplete.com/index.json")

            assert result is False
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("missing 'registry_version'" in msg for msg in messages)

    def test_connectivity_check_http_error(self, mock_console):
        """Test connectivity check with HTTP error."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.reason_phrase = "Not Found"

            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.get.side_effect = httpx.HTTPStatusError(
                "Not Found", request=MagicMock(), response=mock_response
            )
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://notfound.com/index.json")

            assert result is False
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("HTTP error 404" in msg for msg in messages)

    def test_connectivity_check_connect_error(self, mock_console):
        """Test connectivity check with connection error."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = httpx.ConnectError("Failed to connect")
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://unreachable.com/index.json")

            assert result is False
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("Failed to connect" in msg for msg in messages)

    def test_connectivity_check_missing_components_field(self, mock_console):
        """Test connectivity check with missing components field."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"registry_version": "1.0.0"}  # Missing components

            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://incomplete.com/index.json")

            assert result is False
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("missing 'components' field" in msg for msg in messages)

    def test_connectivity_check_valid_registry(self, mock_console):
        """Test connectivity check with valid registry response."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "registry_version": "1.0.0",
                "components": [],
                "updated_at": "2024-01-01T00:00:00Z"
            }

            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://valid.com/index.json")

            assert result is True
            # Should not print any error messages
            assert mock_console.print.call_count == 0

    def test_connectivity_check_not_json(self, mock_console):
        """Test connectivity check with non-JSON response."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []  # Returns array instead of object

            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://array.com/index.json")

            assert result is False

    def test_connectivity_check_generic_exception(self, mock_console):
        """Test connectivity check with unexpected exception."""
        with patch("sygaldry_cli.commands.source.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.get.side_effect = Exception("Unexpected error")
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client_class.return_value = mock_client

            result = _test_source_connectivity("https://error.com/index.json")

            assert result is False
            messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
            assert any("Unexpected error" in msg for msg in messages)

    def test_add_source_with_custom_priority(self, mock_config_manager, mock_console):
        """Test adding a source with custom priority."""
        # Execute with custom priority
        add(alias="high", url="https://high.com/index.json", priority=10, skip_connectivity_check=True)

        # Verify priority is passed correctly
        mock_config_manager.add_registry_source.assert_called_once_with("high", "https://high.com/index.json", priority=10)
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source 'high'" in printed_msg
        assert "(priority: 10)" in printed_msg

    def test_add_source_with_default_priority(self, mock_config_manager, mock_console):
        """Test adding a source with default priority doesn't show priority in message."""
        # Execute with default priority
        add(alias="default_prio", url="https://default.com/index.json", priority=100, skip_connectivity_check=True)

        # Verify priority is passed but not shown in message
        mock_config_manager.add_registry_source.assert_called_once_with("default_prio", "https://default.com/index.json", priority=100)
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source 'default_prio'" in printed_msg
        assert "(priority:" not in printed_msg

    def test_list_sources_with_priorities(self, mock_config_manager, mock_console):
        """Test listing sources shows priorities and status."""
        # Setup config with mixed format sources
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={
                "old_format": "https://old.com/index.json",
                "new_format": {
                    "url": "https://new.com/index.json",
                    "priority": 50,
                    "enabled": True
                },
                "disabled": {
                    "url": "https://disabled.com/index.json",
                    "priority": 20,
                    "enabled": False
                }
            },
            component_paths={},
        )
        mock_config_manager.config = config

        # Execute
        list_sources()

        # Verify table was printed
        assert mock_console.print.called
        # Get all print calls
        print_calls = mock_console.print.call_args_list
        # Find the table in the print calls
        printed_table = None
        for call in print_calls:
            if hasattr(call[0][0], 'title') and hasattr(call[0][0], 'columns'):
                printed_table = call[0][0]
                break
        assert printed_table is not None

        # Should have Priority, Status, and Cache columns
        assert any(col.header == "Priority" for col in printed_table.columns)
        assert any(col.header == "Status" for col in printed_table.columns)
        assert any(col.header == "Cache" for col in printed_table.columns)


class TestSourceCacheCommands:
    """Test the cache subcommands of sygaldry source."""

    @pytest.fixture
    def mock_config_manager(self, mocker):
        """Mock ConfigManager."""
        mock_cfg_manager = MagicMock()
        mocker.patch("sygaldry_cli.commands.source.ConfigManager", return_value=mock_cfg_manager)
        return mock_cfg_manager

    @pytest.fixture
    def mock_registry_handler(self, mocker):
        """Mock RegistryHandler."""
        mock_handler = MagicMock()
        mocker.patch("sygaldry_cli.commands.source.RegistryHandler", return_value=mock_handler)
        return mock_handler

    @pytest.fixture
    def mock_console(self, mocker):
        """Mock console output."""
        return mocker.patch("sygaldry_cli.commands.source.console")

    def test_cache_clear_all(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test clearing all caches."""
        # Setup
        mock_cache_manager = MagicMock()
        mock_registry_handler._cache_manager = mock_cache_manager

        # Execute
        cache_clear(source=None)

        # Verify
        mock_cache_manager.clear_all_caches.assert_called_once()
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Cleared all registry caches" in printed_msg

    def test_cache_clear_specific_source(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test clearing cache for specific source."""
        # Setup
        mock_cache_manager = MagicMock()
        mock_registry_handler._cache_manager = mock_cache_manager

        # Execute
        cache_clear(source="custom")

        # Verify
        mock_cache_manager.invalidate_cache.assert_called_once_with("custom")
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Cleared cache for 'custom'" in printed_msg

    def test_cache_clear_disabled(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test cache clear when cache is disabled."""
        # Setup
        mock_registry_handler._cache_manager = None

        # Execute and verify
        with pytest.raises(typer.Exit) as exc_info:
            cache_clear(source=None)

        assert exc_info.value.exit_code == 0
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Cache is disabled in configuration" in printed_msg

    def test_cache_stats_with_data(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test cache stats with cached data."""
        # Setup
        mock_cache_manager = MagicMock()
        mock_cache_manager.get_cache_stats.return_value = {
            "default": {
                "age": "5 minutes",
                "size_bytes": 2048,
                "cached_at": "2024-01-01T12:00:00",
                "last_accessed": "2024-01-01T12:05:00"
            },
            "custom": {
                "age": "2 hours",
                "size_bytes": 4096,
                "cached_at": "2024-01-01T10:00:00",
                "last_accessed": "2024-01-01T11:00:00"
            }
        }
        mock_registry_handler._cache_manager = mock_cache_manager

        # Capture table
        from unittest.mock import patch
        with patch("sygaldry_cli.commands.source.Table") as mock_table_class:
            mock_table = MagicMock()
            mock_table_class.return_value = mock_table

            # Execute
            cache_stats()

        # Verify
        mock_cache_manager.get_cache_stats.assert_called_once()

        # Verify table creation
        mock_table_class.assert_called_once_with(title="Registry Cache Statistics")

        # Verify columns added
        assert mock_table.add_column.call_count == 5
        column_calls = [call[0][0] for call in mock_table.add_column.call_args_list]
        assert "Source" in column_calls
        assert "Age" in column_calls
        assert "Size" in column_calls
        assert "Cached At" in column_calls
        assert "Last Accessed" in column_calls

        # Verify rows added
        assert mock_table.add_row.call_count == 2

        # Verify summary printed
        assert mock_console.print.call_count >= 3  # Table + total size + location

    def test_cache_stats_empty(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test cache stats with no cached data."""
        # Setup
        mock_cache_manager = MagicMock()
        mock_cache_manager.get_cache_stats.return_value = {}
        mock_registry_handler._cache_manager = mock_cache_manager

        # Execute and verify
        with pytest.raises(typer.Exit) as exc_info:
            cache_stats()

        assert exc_info.value.exit_code == 0
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "No cached data found" in printed_msg

    def test_cache_stats_disabled(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test cache stats when cache is disabled."""
        # Setup
        mock_registry_handler._cache_manager = None

        # Execute and verify
        with pytest.raises(typer.Exit) as exc_info:
            cache_stats()

        assert exc_info.value.exit_code == 0
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Cache is disabled in configuration" in printed_msg

    def test_list_sources_with_cache_enabled(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test list sources shows cache info when cache is enabled."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={
                "default": "https://example.com/index.json",
                "custom": "https://custom.com/index.json"
            },
            component_paths={},
            cache_config=CacheConfig(enabled=True, ttl_seconds=3600)
        )
        mock_config_manager.config = config

        mock_cache_manager = MagicMock()
        mock_cache_manager.get_cache_stats.return_value = {
            "default": {"age": "10 minutes"},
            "custom": {"age": "1 hour"}
        }
        mock_registry_handler._cache_manager = mock_cache_manager

        # Execute
        list_sources(refresh=False)

        # Verify cache info displayed
        print_calls = mock_console.print.call_args_list
        output = " ".join(str(call[0][0]) for call in print_calls)
        assert "Cache TTL: 3600s" in output
        assert "Cache location:" in output

    def test_list_sources_with_refresh(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test list sources with --refresh flag."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={"default": "https://example.com/index.json"},
            component_paths={},
            cache_config=CacheConfig(enabled=True)
        )
        mock_config_manager.config = config

        mock_cache_manager = MagicMock()
        mock_cache_manager.get_cache_stats.return_value = {}
        mock_registry_handler._cache_manager = mock_cache_manager

        # Execute
        list_sources(refresh=True)

        # Verify
        mock_cache_manager.invalidate_cache.assert_called_once()
        messages = [str(call[0][0]) for call in mock_console.print.call_args_list]
        assert any("Refreshing cache" in msg for msg in messages)

    def test_list_sources_cache_disabled(self, mock_config_manager, mock_registry_handler, mock_console):
        """Test list sources when cache is disabled."""
        # Setup
        config = SygaldryConfig(
            default_registry_url="https://example.com/index.json",
            registry_sources={"default": "https://example.com/index.json"},
            component_paths={},
            cache_config=CacheConfig(enabled=False)
        )
        mock_config_manager.config = config
        mock_registry_handler._cache_manager = None

        # Execute
        list_sources(refresh=False)

        # Verify no cache info shown
        print_calls = mock_console.print.call_args_list
        output = " ".join(str(call[0][0]) for call in print_calls)
        assert "Cache TTL:" not in output
