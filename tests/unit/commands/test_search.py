"""Tests for the funcn search command."""

from __future__ import annotations

import pytest
import typer
from funcn_cli.commands.search import search
from funcn_cli.core.models import RegistryComponentEntry, RegistryIndex
from unittest.mock import MagicMock


class TestSearch:
    """Test the funcn search command."""

    @pytest.fixture
    def mock_config_manager(self, mocker):
        """Mock ConfigManager."""
        return mocker.patch("funcn_cli.commands.search.ConfigManager")

    @pytest.fixture
    def mock_registry_handler(self, mocker):
        """Mock RegistryHandler."""
        return mocker.patch("funcn_cli.commands.search.RegistryHandler")

    @pytest.fixture
    def mock_console(self, mocker):
        """Mock console output."""
        return mocker.patch("funcn_cli.commands.search.console")

    @pytest.fixture
    def sample_components(self):
        """Sample components for testing."""
        return [
            RegistryComponentEntry(
                name="text_summarization_agent",
                version="1.0.0",
                type="agent",
                description="Advanced text summarization agent using chain-of-thought reasoning",
                manifest_path="src/agents/text_summarization_agent/component.json",
            ),
            RegistryComponentEntry(
                name="duckduckgo_search_tool",
                version="1.0.0",
                type="tool",
                description="DuckDuckGo web search tools with clean, structured results",
                manifest_path="src/tools/duckduckgo_search_tool/component.json",
            ),
            RegistryComponentEntry(
                name="research_assistant_agent",
                version="2.0.0",
                type="agent",
                description="AI-powered research agent that conducts comprehensive research",
                manifest_path="src/agents/research_assistant_agent/component.json",
            ),
            RegistryComponentEntry(
                name="web_search_agent",
                version="1.0.0",
                type="agent",
                description="Unified web search agent supporting multiple providers",
                manifest_path="src/agents/web_search_agent/component.json",
            ),
        ]

    def test_search_by_name(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test searching components by name."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute
        search(ctx, keyword="search", source=None)

        # Verify
        mock_registry_handler.assert_called_once_with(mock_cfg)
        mock_rh.fetch_index.assert_called_once_with(source_alias=None)

        # Check table output
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Search results for 'search'"
        assert len(printed_table.columns) == 2
        assert printed_table.columns[0].header == "Name"
        assert printed_table.columns[1].header == "Description"

    def test_search_by_description(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test searching components by description."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute
        search(ctx, keyword="comprehensive", source=None)

        # Verify search found components with "comprehensive" in description
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Search results for 'comprehensive'"

    def test_search_no_results(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test searching with no matching results."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute and verify
        with pytest.raises(typer.Exit):
            search(ctx, keyword="nonexistent", source=None)

        # Verify console message
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "No components matching 'nonexistent' found." in printed_msg

    def test_search_case_insensitive(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test that search is case insensitive."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Test various case variations
        test_keywords = ["SEARCH", "Search", "SeArCh", "search"]
        
        for keyword in test_keywords:
            # Reset mocks
            mock_console.print.reset_mock()
            
            # Execute
            search(ctx, keyword=keyword, source=None)
            
            # Verify results were found
            assert mock_console.print.called
            printed_table = mock_console.print.call_args[0][0]
            assert f"Search results for '{keyword}'" == printed_table.title

    def test_search_with_source(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test searching from a specific registry source."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute
        search(ctx, keyword="agent", source="custom")

        # Verify
        mock_rh.fetch_index.assert_called_once_with(source_alias="custom")

    def test_search_partial_match(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test searching with partial keyword match."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute - should find components with "summ" in name or description
        search(ctx, keyword="summ", source=None)

        # Verify
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Search results for 'summ'"

    def test_search_empty_keyword(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test searching with empty keyword matches all."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute - empty string should match all components
        search(ctx, keyword="", source=None)

        # Verify - should show all components
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Search results for ''"

    def test_search_special_characters(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
    ):
        """Test searching with special characters in keyword."""
        # Setup
        special_components = [
            RegistryComponentEntry(
                name="component_with_special-chars",
                version="1.0.0",
                type="agent",
                description="Component with special characters: @#$%",
                manifest_path="src/agents/special/component.json",
            ),
        ]

        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=special_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute - search for special character
        search(ctx, keyword="@#$%", source=None)

        # Verify
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Search results for '@#$%'"

    def test_search_unicode_characters(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
    ):
        """Test searching with unicode characters."""
        # Setup
        unicode_components = [
            RegistryComponentEntry(
                name="unicode_component",
                version="1.0.0",
                type="tool",
                description="Component with unicode: 你好世界 émojis 🚀",
                manifest_path="src/tools/unicode/component.json",
            ),
        ]

        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=unicode_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute - search for unicode
        search(ctx, keyword="你好", source=None)

        # Verify
        assert mock_console.print.called
        printed_table = mock_console.print.call_args[0][0]
        assert printed_table.title == "Search results for '你好'"

    def test_search_multiple_matches(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test searching returns multiple matching components."""
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
        from unittest.mock import patch
        with patch("funcn_cli.commands.search.Table") as mock_table_class:
            mock_table = MagicMock()
            mock_table.add_row = MagicMock(side_effect=capture_add_row)
            mock_table_class.return_value = mock_table

            search(ctx, keyword="agent", source=None)

        # Verify multiple matches (should find all components with "agent" in name)
        assert len(captured_rows) == 3  # text_summarization_agent, research_assistant_agent, web_search_agent

    def test_search_whitespace_handling(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
        sample_components,
    ):
        """Test searching with whitespace in keyword."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_index = RegistryIndex(registry_version="1.0.0", components=sample_components)
        mock_rh.fetch_index.return_value = mock_index
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute - search with spaces
        # The current implementation doesn't strip whitespace, so this won't match
        with pytest.raises(typer.Exit):
            search(ctx, keyword="  search  ", source=None)

        # Verify the no results message was shown
        mock_console.print.assert_called_once()
        printed_msg = str(mock_console.print.call_args[0][0])
        assert "No components matching '  search  ' found." in printed_msg

    def test_search_with_registry_error(
        self,
        mock_config_manager,
        mock_registry_handler,
        mock_console,
    ):
        """Test search when registry handler raises an error."""
        # Setup
        mock_cfg = MagicMock()
        mock_config_manager.return_value = mock_cfg

        mock_rh = MagicMock()
        mock_rh.fetch_index.side_effect = Exception("Failed to fetch index")
        mock_registry_handler.return_value.__enter__.return_value = mock_rh

        ctx = typer.Context(command=MagicMock())

        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Failed to fetch index"):
            search(ctx, keyword="test", source=None)
