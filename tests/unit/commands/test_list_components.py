"""Tests for the funcn list command."""

from __future__ import annotations

import pytest
import typer
from funcn_cli.commands.list_components import list_components
from funcn_cli.core.models import RegistryComponentEntry, RegistryIndex
from unittest.mock import MagicMock, patch


class TestListComponents:
    """Test the funcn list command."""

    @pytest.fixture
    def mock_config_manager(self, mocker):
        """Mock ConfigManager."""
        return mocker.patch("funcn_cli.commands.list_components.ConfigManager")

    @pytest.fixture
    def mock_registry_handler(self, mocker):
        """Mock RegistryHandler."""
        return mocker.patch("funcn_cli.commands.list_components.RegistryHandler")

    @pytest.fixture
    def mock_console(self, mocker):
        """Mock console output."""
        return mocker.patch("funcn_cli.commands.list_components.console")

    @pytest.fixture
    def sample_components(self):
        """Sample components for testing."""
        return [
            RegistryComponentEntry(
                name="text_summarization_agent",
                version="1.0.0",
                type="agent",
                description="Advanced text summarization agent",
                manifest_path="src/agents/text_summarization_agent/component.json",
            ),
            RegistryComponentEntry(
                name="duckduckgo_search_tool",
                version="1.0.0",
                type="tool",
                description="DuckDuckGo web search tools",
                manifest_path="src/tools/duckduckgo_search_tool/component.json",
            ),
            RegistryComponentEntry(
                name="research_assistant_agent",
                version="2.0.0",
                type="agent",
                description="AI-powered research agent",
                manifest_path="src/agents/research_assistant_agent/component.json",
            ),
        ]

    def test_list_components_default_source(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test listing components from default source."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute
        list_components(ctx, source=None)

        # Verify
        mock_registry_handler.assert_called_once_with(mock_cfg)
        mock_rh.fetch_index.assert_called_once_with(source_alias=None)

        # Check table creation
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Components – default"
        assert len(printed_table.columns) == 4
        assert printed_table.columns[0].header == "Name"
        assert printed_table.columns[1].header == "Version"
        assert printed_table.columns[2].header == "Type"
        assert printed_table.columns[3].header == "Description"

    def test_list_components_specific_source(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test listing components from a specific source."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute
        list_components(ctx, source="custom")

        # Verify
        mock_rh.fetch_index.assert_called_once_with(source_alias="custom")

        # Check table title
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Components – custom"

    def test_list_components_empty_registry(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
    ):
        """Test listing components when registry is empty."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=[])
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute
        list_components(ctx, source=None)

        # Verify
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        # Table should be empty but still have proper structure
        assert len(printed_table.columns) == 4

    def test_list_components_verify_table_content(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test that table content matches components data."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Capture table rows
        captured_rows = []

        def capture_add_row(*args):
            captured_rows.append(args)

        # Execute with row capture
        with patch("funcn_cli.commands.list_components.Table") as mock_table_class:
            mock_table = MagicMock()
            mock_table.add_row = MagicMock(side_effect=capture_add_row)
            mock_table_class.return_value = mock_table

            list_components(ctx, source=None)

        # Verify rows match components
        assert len(captured_rows) == len(sample_components)
        for i, comp in enumerate(sample_components):
            row = captured_rows[i]
            assert row[0] == comp.name
            assert row[1] == comp.version
            assert row[2] == comp.type
            assert row[3] == comp.description

    def test_list_components_with_registry_error(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
    ):
        """Test listing components when registry handler raises an error."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_rh.fetch_index.side_effect = Exception("Failed to fetch index")
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Failed to fetch index"):
            list_components(ctx, source=None)

    def test_list_components_source_variations(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test listing components with various source names."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        test_sources = ["", "github", "local", "custom-registry", "my_source"]

        for source in test_sources:
            # Reset mocks
            mock_rh.fetch_index.reset_mock()
            mock_console.print.reset_mock()

            # Execute
            list_components(ctx, source=source)

            # Verify
            mock_rh.fetch_index.assert_called_once_with(source_alias=source)
            printed_table = mock_console.print.call_args[0][0]
            # Empty string should show "default" in title
            expected_title = f"Components – {source or 'default'}"
            assert printed_table.title == expected_title

    def test_list_components_column_properties(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test that table columns have correct properties."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Capture table creation
        with patch("funcn_cli.commands.list_components.Table") as mock_table_class:
            mock_table = MagicMock()
            captured_columns = []

            def capture_add_column(header, **kwargs):
                captured_columns.append((header, kwargs))

            mock_table.add_column = MagicMock(side_effect=capture_add_column)
            mock_table_class.return_value = mock_table

            list_components(ctx, source=None)

        # Verify column properties
        assert len(captured_columns) == 4

        # Name column
        assert captured_columns[0][0] == "Name"
        assert captured_columns[0][1]["style"] == "cyan"
        assert captured_columns[0][1]["no_wrap"] is True

        # Version column
        assert captured_columns[1][0] == "Version"
        assert captured_columns[1][1]["justify"] == "right"

        # Type column
        assert captured_columns[2][0] == "Type"
        assert captured_columns[2][1] == {}  # No special properties

        # Description column
        assert captured_columns[3][0] == "Description"
        assert captured_columns[3][1] == {}  # No special properties

    def test_list_components_long_descriptions(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
    ):
        """Test listing components with very long descriptions."""
        # Setup
        long_desc_components = [
            RegistryComponentEntry(
                name="long_desc_component",
                version="1.0.0",
                type="agent",
                description="This is a very long description that goes on and on and on. " * 10,
                manifest_path="src/agents/long_desc_component/component.json",
            )
        ]

        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=long_desc_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute
        list_components(ctx, source=None)

        # Verify - should still work with long descriptions
        assert mock_console.print.called

    def test_list_components_special_characters(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
    ):
        """Test listing components with special characters in fields."""
        # Setup
        special_char_components = [
            RegistryComponentEntry(
                name="component_with_special_chars",
                version="2.0.0-beta.1",
                type="agent",
                description="Component with 特殊文字 and émojis 🚀",
                manifest_path="src/agents/component_with_special_chars/component.json",
            )
        ]

        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=special_char_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute
        list_components(ctx, source=None)

        # Verify - should handle special characters gracefully
        assert mock_console.print.called
