"""Tests for the sygaldry mcp command."""

from __future__ import annotations

import asyncio
import json
import pytest
import sys
import typer
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Mock the mcp module before importing
sys.modules['mcp'] = MagicMock()
sys.modules['mcp.client'] = MagicMock()
sys.modules['mcp.client.stdio'] = MagicMock()
sys.modules['mirascope.mcp'] = MagicMock()

from sygaldry_cli.commands.mcp_cmd import run_mcp_agent


class TestMcp:
    """Test the sygaldry mcp command."""

    @pytest.fixture
    def mock_console(self, mocker):
        """Mock console output."""
        return mocker.patch("sygaldry_cli.commands.mcp_cmd.console")

    @pytest.fixture
    def mock_config_manager(self, mocker):
        """Mock ConfigManager."""
        return mocker.patch("sygaldry_cli.commands.mcp_cmd.ConfigManager")

    @pytest.fixture
    def mock_get_sygaldry_config(self, mocker):
        """Mock get_sygaldry_config function."""
        return mocker.patch("sygaldry_cli.commands.mcp_cmd.get_sygaldry_config")

    @pytest.fixture
    def tmp_project(self, tmp_path):
        """Create a temporary project structure."""
        # Create sygaldry.json
        sygaldry_config = {
            "$schema": "./sygaldry.schema.json",
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
            "defaultModel": "gpt-4o-mini",
            "stream": False,
            "default_mcp_host": "localhost",
            "default_mcp_port": 8080,
        }
        (tmp_path / "sygaldry.json").write_text(json.dumps(sygaldry_config, indent=2))

        # Create agent directory structure
        agent_dir = tmp_path / "src" / "agents" / "test_agent"
        agent_dir.mkdir(parents=True)

        # Create mcp_server.py
        mcp_server_content = """
# Test MCP server
import sys
print(f"MCP Server started with args: {sys.argv}")
"""
        (agent_dir / "mcp_server.py").write_text(mcp_server_content)

        return tmp_path

    def test_run_mcp_agent_no_sygaldry_json(self, mock_console, mock_config_manager, mock_get_sygaldry_config):
        """Test running MCP agent without sygaldry.json."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = Path("/test/project")
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = None

        # Execute
        with pytest.raises(typer.Exit) as exc_info:
            run_mcp_agent(agent_name="test_agent", mode="stdio", host=None, port=None)

        assert exc_info.value.exit_code == 1

        # Verify error message
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("sygaldry.json not found" in call for call in console_calls)

    def test_run_mcp_agent_no_agent_directory(self, mock_console, mock_config_manager, mock_get_sygaldry_config):
        """Test running MCP agent without agent directory configured."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = Path("/test/project")
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            # Missing agentDirectory
            "defaultProvider": "openai",
        }

        # Execute
        with pytest.raises(typer.Exit) as exc_info:
            run_mcp_agent(agent_name="test_agent", mode="stdio", host=None, port=None)

        assert exc_info.value.exit_code == 1

        # Verify error message
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Agent directory not configured" in call for call in console_calls)

    def test_run_mcp_agent_missing_mcp_server(
        self, mock_console, mock_config_manager, mock_get_sygaldry_config, tmp_path
    ):
        """Test running MCP agent when mcp_server.py doesn't exist."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = tmp_path
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
        }

        # Create agent dir without mcp_server.py
        agent_dir = tmp_path / "src" / "agents" / "missing_server"
        agent_dir.mkdir(parents=True)

        # Execute
        with pytest.raises(typer.Exit) as exc_info:
            run_mcp_agent(agent_name="missing_server", mode="stdio", host=None, port=None)

        assert exc_info.value.exit_code == 1

        # Verify error message
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("MCP server entrypoint 'mcp_server.py' not found" in call for call in console_calls)

    def test_run_mcp_agent_stdio_success(
        self, mock_console, mock_config_manager, mock_get_sygaldry_config, tmp_project, mocker
    ):
        """Test successful MCP agent run in stdio mode."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = tmp_project
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
        }

        # Mock stdio_client
        mock_client = AsyncMock()
        mock_client.list_prompts.return_value = [
            MagicMock(
                name="test_prompt",
                description="A test prompt",
                arguments=[MagicMock(name="arg1", required=True, description="Test argument")],
            )
        ]

        mock_stdio_client = mocker.patch("sygaldry_cli.commands.mcp_cmd.stdio_client")
        mock_stdio_client.return_value.__aenter__.return_value = mock_client

        # Mock asyncio.run to capture the async function
        captured_coro = None

        def capture_coro(coro):
            nonlocal captured_coro
            captured_coro = coro
            # Run the coroutine synchronously for testing
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(coro)

        mocker.patch("asyncio.run", side_effect=capture_coro)

        # Execute
        run_mcp_agent(agent_name="test_agent", mode="stdio", host=None, port=None)

        # Verify
        assert mock_client.list_prompts.called
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Successfully connected to MCP server" in call for call in console_calls)
        assert any("test_prompt" in call for call in console_calls)

    def test_run_mcp_agent_different_modes(
        self, mock_console, mock_config_manager, mock_get_sygaldry_config, tmp_project, mocker
    ):
        """Test MCP agent with different modes."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = tmp_project
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
            "default_mcp_host": "0.0.0.0",
            "default_mcp_port": 8000,
        }

        # Mock clients
        mock_stdio_client = mocker.patch("sygaldry_cli.commands.mcp_cmd.stdio_client")
        mock_sse_client = mocker.patch("sygaldry_cli.commands.mcp_cmd.sse_client")

        # Mock asyncio.run to execute the coroutine
        def run_async(coro):
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(coro)

        mocker.patch("asyncio.run", side_effect=run_async)

        # Test stdio mode
        run_mcp_agent(agent_name="test_agent", mode="stdio", host=None, port=None)
        assert mock_stdio_client.called

        # Test http mode
        mock_stdio_client.reset_mock()
        run_mcp_agent(agent_name="test_agent", mode="http", host="localhost", port=3000)
        # Note: The command still uses stdio_client for server params, but would connect with sse_client

    def test_run_mcp_agent_custom_host_port(
        self, mock_console, mock_config_manager, mock_get_sygaldry_config, tmp_project, mocker
    ):
        """Test MCP agent with custom host and port."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = tmp_project
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
        }

        # Mock StdioServerParameters to capture its creation
        captured_args = None

        original_stdio_params = sys.modules['mcp.client.stdio'].StdioServerParameters

        def mock_stdio_params(command, args, env):
            nonlocal captured_args
            captured_args = args
            return original_stdio_params(command, args, env)

        mocker.patch("sygaldry_cli.commands.mcp_cmd.StdioServerParameters", side_effect=mock_stdio_params)
        mocker.patch("sygaldry_cli.commands.mcp_cmd.stdio_client", return_value=MagicMock(__aenter__=AsyncMock(return_value=AsyncMock())))

        # Mock asyncio.run to execute the coroutine
        def run_async(coro):
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(coro)

        mocker.patch("asyncio.run", side_effect=run_async)

        # Execute
        run_mcp_agent(agent_name="test_agent", mode="stdio", host="192.168.1.1", port=9999)

        # Verify custom host and port were used
        assert captured_args is not None
        assert "--host" in captured_args
        assert "192.168.1.1" in captured_args
        assert "--port" in captured_args
        assert "9999" in captured_args

    def test_run_mcp_agent_connection_refused(
        self, mock_console, mock_config_manager, mock_get_sygaldry_config, tmp_project, mocker
    ):
        """Test MCP agent when connection is refused."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = tmp_project
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
        }

        # Mock stdio_client to raise ConnectionRefusedError
        async def raise_connection_refused():
            raise ConnectionRefusedError("Connection refused")

        mock_stdio_client = mocker.patch("sygaldry_cli.commands.mcp_cmd.stdio_client")
        mock_stdio_client.return_value.__aenter__.side_effect = raise_connection_refused

        # Mock asyncio.run
        def run_async(coro):
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(coro)

        mocker.patch("asyncio.run", side_effect=run_async)

        # Execute
        run_mcp_agent(agent_name="test_agent", mode="stdio", host=None, port=None)

        # Verify error handling
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Connection refused by MCP server" in call for call in console_calls)

    def test_run_mcp_agent_keyboard_interrupt(
        self, mock_console, mock_config_manager, mock_get_sygaldry_config, tmp_project, mocker
    ):
        """Test MCP agent handling keyboard interrupt."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = tmp_project
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
        }

        # Mock asyncio.run to raise KeyboardInterrupt
        mocker.patch("asyncio.run", side_effect=KeyboardInterrupt())

        # Execute
        run_mcp_agent(agent_name="test_agent", mode="stdio", host=None, port=None)

        # Verify graceful handling
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Agent run interrupted by user" in call for call in console_calls)
        assert any("Finished running agent" in call for call in console_calls)

    def test_run_mcp_agent_no_prompts(
        self, mock_console, mock_config_manager, mock_get_sygaldry_config, tmp_project, mocker
    ):
        """Test MCP agent when no prompts are exposed."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = tmp_project
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
        }

        # Mock client with empty prompts
        mock_client = AsyncMock()
        mock_client.list_prompts.return_value = []

        mock_stdio_client = mocker.patch("sygaldry_cli.commands.mcp_cmd.stdio_client")
        mock_stdio_client.return_value.__aenter__.return_value = mock_client

        # Mock asyncio.run
        def run_async(coro):
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(coro)

        mocker.patch("asyncio.run", side_effect=run_async)

        # Execute
        run_mcp_agent(agent_name="test_agent", mode="stdio", host=None, port=None)

        # Verify
        console_calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("No prompts exposed by agent" in call for call in console_calls)

    def test_run_mcp_agent_case_insensitive_mode(
        self, mock_console, mock_config_manager, mock_get_sygaldry_config, tmp_project, mocker
    ):
        """Test that mode parameter is case insensitive."""
        # Setup
        mock_cfg = MagicMock()
        mock_cfg.project_root = tmp_project
        mock_config_manager.return_value = mock_cfg

        mock_get_sygaldry_config.return_value = {
            "agentDirectory": "src/agents",
            "defaultProvider": "openai",
        }

        mocker.patch("sygaldry_cli.commands.mcp_cmd.stdio_client")
        mocker.patch("asyncio.run")

        # Test different case variations
        for mode in ["STDIO", "Stdio", "StDiO"]:
            run_mcp_agent(agent_name="test_agent", mode=mode, host=None, port=None)

            # Should not raise errors
