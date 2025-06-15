"""End-to-end tests for funcn list and search commands."""

from __future__ import annotations

import pytest
from tests.e2e.base import BaseE2ETest
from unittest.mock import MagicMock, patch


@pytest.mark.e2e
class TestListSearchWorkflow(BaseE2ETest):
    """Test component listing and searching workflows."""
    
    def _mock_registry_response(self, mock_data):
        """Helper to create a mock httpx client with registry response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status = MagicMock()
        return mock_response
    
    @pytest.fixture
    def mock_registry_with_many_components(self):
        """Create a mock registry with many components for testing."""
        return {
            "registry_version": "1.0.0",
            "components": [
                {
                    "name": "text_summarization_agent",
                    "version": "1.2.0",
                    "type": "agent",
                    "description": "Advanced text summarization agent using chain-of-thought reasoning",
                    "manifest_path": "components/agents/text_summarization_agent/component.json"
                },
                {
                    "name": "web_search_agent",
                    "version": "2.0.0",
                    "type": "agent",
                    "description": "Unified web search agent supporting multiple providers",
                    "manifest_path": "components/agents/web_search_agent/component.json"
                },
                {
                    "name": "pdf_search_tool",
                    "version": "1.0.0",
                    "type": "tool",
                    "description": "PDF search tool for searching text within PDF documents",
                    "manifest_path": "components/tools/pdf_search_tool/component.json"
                },
                {
                    "name": "csv_search_tool",
                    "version": "1.1.0",
                    "type": "tool",
                    "description": "CSV search and filtering tool for structured data",
                    "manifest_path": "components/tools/csv_search_tool/component.json"
                },
                {
                    "name": "dice_roller",
                    "version": "0.9.0",
                    "type": "tool",
                    "description": "A fair dice rolling tool for tabletop RPGs",
                    "manifest_path": "components/tools/dice_roller/component.json"
                },
                {
                    "name": "chat_template",
                    "version": "1.0.0",
                    "type": "prompt_template",
                    "description": "Basic chat conversation template",
                    "manifest_path": "components/templates/chat_template/component.json"
                }
            ]
        }
    
    def test_list_all_components(self, cli_runner, mock_registry_with_many_components):
        """Test listing all components from registry."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            # Run funcn list
            result = self.run_command(cli_runner, ["list"])
            
            self.assert_command_success(result)
            
            # Verify all components are shown
            assert "text_summarization_agent" in result.output
            assert "web_search_agent" in result.output
            assert "pdf_search_tool" in result.output
            assert "csv_search_tool" in result.output
            assert "dice_roller" in result.output
            assert "chat_template" in result.output
            
            # Verify component types are shown
            assert "agent" in result.output
            assert "tool" in result.output
            assert "prompt_template" in result.output
    
    @pytest.mark.skip(reason="Requires complex funcn config setup - tracked in FUNCNOS-33")
    def test_list_with_custom_source(self, cli_runner, test_project_dir, mock_registry_with_many_components):
        """Test listing components from a custom registry source."""
        # First initialize 
        result = self.run_command(cli_runner, ["init", "--yes"], input="n\n")
        self.assert_command_success(result)
        
        result = self.run_command(
            cli_runner,
            ["source", "add", "custom", "https://custom.funcn.ai/index.json"]
        )
        self.assert_command_success(result)
        
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            # List from custom source
            result = self.run_command(cli_runner, ["list", "--source", "custom"])
            
            self.assert_command_success(result)
            
            # Verify components are listed
            assert "text_summarization_agent" in result.output
            
            # Verify the custom URL was used
            mock_client.get.assert_called()
            call_args = str(mock_client.get.call_args)
            assert "custom.funcn.ai" in call_args
    
    def test_search_by_name(self, cli_runner, mock_registry_with_many_components):
        """Test searching components by name."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            # Search for "search"
            result = self.run_command(cli_runner, ["search", "search"])
            
            self.assert_command_success(result)
            
            # Should find components with "search" in name
            assert "web_search_agent" in result.output
            assert "pdf_search_tool" in result.output
            assert "csv_search_tool" in result.output
            
            # Should not show unrelated components
            assert "dice_roller" not in result.output
            assert "chat_template" not in result.output
    
    def test_search_by_description(self, cli_runner, mock_registry_with_many_components):
        """Test searching components by description."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            # Search for "summarization"
            result = self.run_command(cli_runner, ["search", "summarization"])
            
            self.assert_command_success(result)
            
            # Should find text summarization agent
            assert "text_summarization_agent" in result.output
            
            # Should not show unrelated components
            assert "dice_roller" not in result.output
    
    def test_search_case_insensitive(self, cli_runner, mock_registry_with_many_components):
        """Test that search is case insensitive."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            # Search with different cases
            for query in ["PDF", "pdf", "PdF"]:
                result = self.run_command(cli_runner, ["search", query])
                self.assert_command_success(result)
                assert "pdf_search_tool" in result.output
    
    def test_search_no_results(self, cli_runner, mock_registry_with_many_components):
        """Test search with no matching results."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            # Search for non-existent term
            result = self.run_command(cli_runner, ["search", "nonexistent"])
            
            self.assert_command_success(result)
            
            # Should indicate no results
            assert "No components matching" in result.output
    
    def test_list_empty_registry(self, cli_runner):
        """Test listing when registry has no components."""
        empty_registry = {
            "registry_version": "1.0.0",
            "components": []
        }
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(empty_registry)
            
            result = self.run_command(cli_runner, ["list"])
            
            self.assert_command_success(result)
            
            # Should show empty table (no rows in table body)
            assert "└──────┴─────────┴──────┴─────────────┘" in result.output  # Empty table footer
    
    def test_list_network_error(self, cli_runner):
        """Test handling network errors when listing."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.side_effect = Exception("Network error")
            
            result = self.run_command(cli_runner, ["list"])
            
            # Should fail gracefully
            assert result.exit_code != 0
    
    def test_search_special_characters(self, cli_runner, mock_registry_with_many_components):
        """Test searching with special characters."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            # Search with special characters
            result = self.run_command(cli_runner, ["search", "chain-of-thought"])
            
            self.assert_command_success(result)
            
            # Should find text summarization agent (has chain-of-thought in description)
            assert "text_summarization_agent" in result.output
    
    def test_list_shows_versions(self, cli_runner, mock_registry_with_many_components):
        """Test that list command shows component versions."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            result = self.run_command(cli_runner, ["list"])
            
            self.assert_command_success(result)
            
            # Should show versions
            assert "1.2.0" in result.output  # text_summarization_agent version
            assert "2.0.0" in result.output  # web_search_agent version
            assert "0.9.0" in result.output  # dice_roller version
    
    def test_search_by_tag(self, cli_runner, mock_registry_with_many_components):
        """Test searching components by tag."""
        with patch("httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.get.return_value = self._mock_registry_response(mock_registry_with_many_components)
            
            # Search for RPG-related term (dice_roller is for tabletop RPGs)
            result = self.run_command(cli_runner, ["search", "RPG"])
            
            self.assert_command_success(result)
            
            # Should find dice_roller (has RPG in description)
            assert "dice_roller" in result.output
            
            # Should not show unrelated components
            assert "pdf_search_tool" not in result.output
