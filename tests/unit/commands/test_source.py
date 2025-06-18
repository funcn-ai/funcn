"""Tests for the funcn source command."""

from __future__ import annotations

import pytest
import typer
from funcn_cli.commands.source import add, list_sources, remove
from funcn_cli.config_manager import FuncnConfig
from unittest.mock import MagicMock


class TestSource:
    """Test the funcn source command and its subcommands."""

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

    @pytest.fixture
    def sample_config(self):
        """Sample configuration with registry sources."""
        return FuncnConfig(
            default_registry_url="https://raw.githubusercontent.com/funcn-ai/funcn-registry/main/index.json",
            registry_sources={
                "default": "https://raw.githubusercontent.com/funcn-ai/funcn-registry/main/index.json",
                "custom": "https://example.com/custom/index.json",
                "local": "file:///path/to/local/index.json",
            },
            component_paths={"agents": "./src/agents", "tools": "./src/tools"},
            enable_lilypad=False,
        )

    def test_add_source_project_level(self, mock_config_manager, mock_console):
        """Test adding a registry source at project level."""
        # Execute
        add(alias="test", url="https://test.com/index.json")

        # Verify
        mock_config_manager.add_registry_source.assert_called_once_with("test", "https://test.com/index.json")
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source 'test' -> https://test.com/index.json" in printed_msg

    def test_add_source_global_level(self, mock_config_manager, mock_console):
        """Test adding a registry source at global level."""
        # Execute
        add(alias="global_test", url="https://global.com/index.json")

        # Verify
        mock_config_manager.add_registry_source.assert_called_once_with("global_test", "https://global.com/index.json")
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source 'global_test' -> https://global.com/index.json" in printed_msg

    def test_add_source_with_special_characters(self, mock_config_manager, mock_console):
        """Test adding a source with special characters in alias."""
        # Execute
        add(alias="test-source_123", url="https://test.com/index.json")

        # Verify
        mock_config_manager.add_registry_source.assert_called_once_with("test-source_123", "https://test.com/index.json")

    def test_add_source_with_file_url(self, mock_config_manager, mock_console):
        """Test adding a source with file:// URL."""
        # Execute
        add(alias="local", url="file:///home/user/registry/index.json")

        # Verify
        mock_config_manager.add_registry_source.assert_called_once_with("local", "file:///home/user/registry/index.json")

    def test_list_sources_with_multiple_sources(self, mock_config_manager, mock_console, sample_config):
        """Test listing multiple registry sources."""
        # Setup
        mock_config_manager.config = sample_config

        # Execute
        list_sources()

        # Verify table was printed
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Registry Sources"
        assert len(printed_table.columns) == 2
        assert printed_table.columns[0].header == "Alias"
        assert printed_table.columns[1].header == "URL"

    def test_list_sources_empty(self, mock_config_manager, mock_console):
        """Test listing sources when none are configured."""
        # Setup
        empty_config = FuncnConfig(
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
        printed_table = mock_console.print.call_args[0][0]
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

        with patch("funcn_cli.commands.source.Table") as mock_table_class:
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
                assert sample_config.default_registry_url in row[1]

        assert default_found, "Default source should be marked"

    def test_list_sources_ordering(self, mock_config_manager, mock_console):
        """Test that sources are listed in a consistent order."""
        # Setup with sources that would have different ordering
        config = FuncnConfig(
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

        with patch("funcn_cli.commands.source.Table") as mock_table_class:
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
            add(alias=f"test{i}", url=url)

            # Verify
            mock_config_manager.add_registry_source.assert_called_once_with(f"test{i}", url)

    def test_add_source_error_handling(self, mock_config_manager, mock_console):
        """Test error handling when adding a source fails."""
        # Setup - simulate error
        mock_config_manager.add_registry_source.side_effect = Exception("Failed to add source")

        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Failed to add source"):
            add(alias="error_test", url="https://test.com/index.json")

    def test_list_sources_with_long_urls(self, mock_config_manager, mock_console):
        """Test listing sources with very long URLs."""
        # Setup
        config = FuncnConfig(
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
        config = FuncnConfig(
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
        config = FuncnConfig(
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
        config = FuncnConfig(
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
        config = FuncnConfig(
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
        config = FuncnConfig(
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
            add(alias="invalid", url="ftp://example.com/index.json")

        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "Invalid URL scheme" in printed_msg
        assert "ftp" in printed_msg

    def test_add_source_missing_domain(self, mock_config_manager, mock_console):
        """Test adding source with missing domain."""
        # Execute and verify exception is raised
        with pytest.raises(typer.Exit) as exc_info:
            add(alias="nodomain", url="https://")

        assert exc_info.value.exit_code == 1
        mock_console.print.assert_called()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "missing domain/host" in printed_msg

    def test_add_source_warns_non_index_url(self, mock_config_manager, mock_console):
        """Test warning when URL doesn't end with index.json."""
        # Execute - should succeed but warn
        add(alias="nonindex", url="https://example.com/registry")

        # Should have two print calls - warning and success
        assert mock_console.print.call_count == 2
        warning_msg = str(mock_console.print.call_args_list[0][0][0])
        success_msg = str(mock_console.print.call_args_list[1][0][0])

        assert "should typically point to an index.json file" in warning_msg
        assert "Added registry source" in success_msg

        # Should still add the source
        mock_config_manager.add_registry_source.assert_called_once_with("nonindex", "https://example.com/registry")

    def test_add_source_accepts_index_json(self, mock_config_manager, mock_console):
        """Test that URL ending with index.json doesn't warn."""
        # Execute
        add(alias="proper", url="https://example.com/index.json")

        # Should only have one print call (success, no warning)
        assert mock_console.print.call_count == 1
        success_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source" in success_msg

        # Should add the source
        mock_config_manager.add_registry_source.assert_called_once_with("proper", "https://example.com/index.json")

    def test_add_source_accepts_file_scheme(self, mock_config_manager, mock_console):
        """Test that file:// URLs are accepted."""
        # Execute
        add(alias="local", url="file:///path/to/index.json")

        # Should succeed
        assert mock_console.print.call_count == 1
        success_msg = str(mock_console.print.call_args[0][0])
        assert "Added registry source" in success_msg

        # Should add the source
        mock_config_manager.add_registry_source.assert_called_once_with("local", "file:///path/to/index.json")
