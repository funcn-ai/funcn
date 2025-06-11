"""End-to-end tests for funcn list and search commands."""

from __future__ import annotations

import pytest
from tests.e2e.base import BaseE2ETest
from unittest.mock import MagicMock, patch


@pytest.mark.e2e
class TestListSearchWorkflow(BaseE2ETest):
    """Test component listing and searching workflows."""
    
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
                    "authors": [{"name": "Funcn Team", "email": "team@funcn.ai"}],
                    "tags": ["nlp", "summarization", "text-processing"]
                },
                {
                    "name": "web_search_agent",
                    "version": "2.0.0",
                    "type": "agent",
                    "description": "Unified web search agent supporting multiple providers",
                    "authors": [{"name": "Funcn Team", "email": "team@funcn.ai"}],
                    "tags": ["search", "web", "research"]
                },
                {
                    "name": "pdf_search_tool",
                    "version": "1.0.0",
                    "type": "tool",
                    "description": "PDF search tool for searching text within PDF documents",
                    "authors": [{"name": "Funcn Team", "email": "team@funcn.ai"}],
                    "tags": ["pdf", "search", "document"]
                },
                {
                    "name": "csv_search_tool",
                    "version": "1.1.0",
                    "type": "tool",
                    "description": "CSV search and filtering tool for structured data",
                    "authors": [{"name": "Funcn Team", "email": "team@funcn.ai"}],
                    "tags": ["csv", "data", "search"]
                },
                {
                    "name": "dice_roller",
                    "version": "0.9.0",
                    "type": "tool",
                    "description": "A fair dice rolling tool for tabletop RPGs",
                    "authors": [{"name": "Gaming Team", "email": "gaming@funcn.ai"}],
                    "tags": ["gaming", "rpg", "utility"]
                },
                {
                    "name": "chat_template",
                    "version": "1.0.0",
                    "type": "prompt_template",
                    "description": "Basic chat conversation template",
                    "authors": [{"name": "Funcn Team", "email": "team@funcn.ai"}],
                    "tags": ["chat", "conversation"]
                }
            ]
        }
    
    def test_list_all_components(self, cli_runner, mock_registry_with_many_components):
        """Test listing all components from registry."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
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
    
    def test_list_with_custom_source(self, cli_runner, test_project_dir, mock_registry_with_many_components):
        """Test listing components from a custom registry source."""
        # First initialize and add a custom source
        result = self.run_command(cli_runner, ["init"], input="\n\n\n\nno\n")
        self.assert_command_success(result)
        
        result = self.run_command(
            cli_runner,
            ["source", "add", "custom", "https://custom.funcn.ai/index.json"]
        )
        self.assert_command_success(result)
        
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
            # List from custom source
            result = self.run_command(cli_runner, ["list", "--source", "custom"])
            
            self.assert_command_success(result)
            
            # Verify components are listed
            assert "text_summarization_agent" in result.output
            
            # Verify the custom URL was used
            mock_get.assert_called()
            call_args = str(mock_get.call_args)
            assert "custom.funcn.ai" in call_args
    
    def test_search_by_name(self, cli_runner, mock_registry_with_many_components):
        """Test searching components by name."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
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
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
            # Search for "summarization"
            result = self.run_command(cli_runner, ["search", "summarization"])
            
            self.assert_command_success(result)
            
            # Should find text summarization agent
            assert "text_summarization_agent" in result.output
            
            # Should not show unrelated components
            assert "dice_roller" not in result.output
    
    def test_search_case_insensitive(self, cli_runner, mock_registry_with_many_components):
        """Test that search is case insensitive."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
            # Search with different cases
            for query in ["PDF", "pdf", "PdF"]:
                result = self.run_command(cli_runner, ["search", query])
                self.assert_command_success(result)
                assert "pdf_search_tool" in result.output
    
    def test_search_no_results(self, cli_runner, mock_registry_with_many_components):
        """Test search with no matching results."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
            # Search for non-existent term
            result = self.run_command(cli_runner, ["search", "nonexistent"])
            
            self.assert_command_success(result)
            
            # Should indicate no results
            assert "No components found" in result.output or "0" in result.output
    
    def test_list_empty_registry(self, cli_runner):
        """Test listing when registry has no components."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "registry_version": "1.0.0",
                "components": []
            }
            mock_get.return_value = mock_response
            
            result = self.run_command(cli_runner, ["list"])
            
            self.assert_command_success(result)
            
            # Should indicate empty registry
            assert "No components" in result.output or "empty" in result.output.lower()
    
    def test_list_network_error(self, cli_runner):
        """Test handling network errors when listing."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = self.run_command(cli_runner, ["list"])
            
            # Should fail gracefully
            assert result.exit_code != 0
            assert "error" in result.output.lower()
    
    def test_search_special_characters(self, cli_runner, mock_registry_with_many_components):
        """Test searching with special characters."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
            # Search with special characters
            result = self.run_command(cli_runner, ["search", "chain-of-thought"])
            
            self.assert_command_success(result)
            
            # Should find text summarization agent (has chain-of-thought in description)
            assert "text_summarization_agent" in result.output
    
    def test_list_shows_versions(self, cli_runner, mock_registry_with_many_components):
        """Test that list command shows component versions."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
            result = self.run_command(cli_runner, ["list"])
            
            self.assert_command_success(result)
            
            # Should show versions
            assert "1.2.0" in result.output  # text_summarization_agent version
            assert "2.0.0" in result.output  # web_search_agent version
            assert "0.9.0" in result.output  # dice_roller version
    
    def test_search_by_tag(self, cli_runner, mock_registry_with_many_components):
        """Test searching components by tag."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_registry_with_many_components
            mock_get.return_value = mock_response
            
            # Search for gaming tag
            result = self.run_command(cli_runner, ["search", "gaming"])
            
            self.assert_command_success(result)
            
            # Should find dice_roller (has gaming tag)
            assert "dice_roller" in result.output
            
            # Should not show unrelated components
            assert "pdf_search_tool" not in result.output
