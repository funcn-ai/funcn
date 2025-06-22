"""Unit tests for funcn add command."""

import json
import pytest
from pathlib import Path
from tests.unit.commands.base import BaseCommandTest
from unittest.mock import AsyncMock, Mock, call, patch


class TestAddCommand(BaseCommandTest):
    """Test cases for the funcn add command."""
    
    def test_add_component_by_name_success(self, tmp_path):
        """Test successfully adding a component by name."""
        mock_component_manager = Mock()
        mock_component_manager.add_component.return_value = None
        
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                # Mock the prompts since the logic checks "if not with_lilypad" which means ask if False
                with patch("rich.prompt.Confirm.ask") as mock_confirm:
                    # Mock both potential prompts
                    mock_confirm.side_effect = [
                        False,  # Enable lilypad tracing? (because with_lilypad=False triggers prompt)
                        False,  # Enable streaming responses? (because stream=None triggers prompt)
                    ]
                    
                    import typer
                    from funcn_cli.commands import add as add_module
                    ctx = Mock(spec=typer.Context)
                    ctx.invoked_subcommand = None
                    
                    # Call the add function directly
                    add_module.add(
                        ctx,
                        identifier="test-agent",
                        provider="openai",
                        model="gpt-4",
                        with_lilypad=False,
                        stream=None,
                        source=None
                    )
                    
                    mock_component_manager.add_component.assert_called_once_with(
                        "test-agent",
                        provider="openai",
                        model="gpt-4",
                        with_lilypad=False,
                        stream=False,  # Will be False from the prompt
                        source_alias=None
                    )
    
    def test_add_component_with_url(self, tmp_path):
        """Test adding a component using a direct manifest URL."""
        manifest_url = "https://registry.funcn.ai/components/test-agent/manifest.json"
        
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Confirm.ask") as mock_confirm:
                    # Only stream prompt needed since with_lilypad=True
                    mock_confirm.return_value = False  # Enable streaming responses?
                    
                    import typer
                    from funcn_cli.commands import add as add_module
                    ctx = Mock(spec=typer.Context)
                    ctx.invoked_subcommand = None
                    
                    add_module.add(
                        ctx,
                        identifier=manifest_url,
                        provider="openai",
                        model="gpt-4o-mini",
                        with_lilypad=True,
                        stream=None,
                        source=None
                    )
                    
                    mock_component_manager.add_component.assert_called_once_with(
                        manifest_url,
                        provider="openai",
                        model="gpt-4o-mini",
                        with_lilypad=True,
                        stream=False,
                        source_alias=None
                    )
    
    def test_add_interactive_mode(self, tmp_path):
        """Test interactive mode when no identifier provided."""
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Prompt.ask") as mock_prompt:
                    with patch("rich.prompt.Confirm.ask") as mock_confirm:
                        mock_prompt.side_effect = [
                            "test-tool",      # Component identifier
                            "anthropic",      # Provider
                            "claude-3-opus",  # Model
                        ]
                        mock_confirm.side_effect = [
                            True,   # Enable lilypad?
                            False,  # Enable streaming?
                        ]
                        
                        import typer
                        from funcn_cli.commands import add as add_module
                        ctx = Mock(spec=typer.Context)
                        ctx.invoked_subcommand = None
                        
                        add_module.add(
                            ctx,
                            identifier=None,
                            provider=None,
                            model=None,
                            with_lilypad=False,  # This triggers lilypad prompt
                            stream=None,  # This triggers stream prompt
                            source=None
                        )
                        
                        mock_component_manager.add_component.assert_called_once_with(
                            "test-tool",
                            provider="anthropic",
                            model="claude-3-opus",
                            with_lilypad=True,
                            stream=False,
                            source_alias=None
                        )
    
    def test_add_with_streaming_enabled(self, tmp_path):
        """Test adding component with streaming enabled."""
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Confirm.ask") as mock_confirm:
                    # Only lilypad prompt needed since stream=True
                    mock_confirm.return_value = False  # Enable lilypad tracing?
                    
                    import typer
                    from funcn_cli.commands import add as add_module
                    ctx = Mock(spec=typer.Context)
                    ctx.invoked_subcommand = None
                    
                    add_module.add(
                        ctx,
                        identifier="chat-agent",
                        provider="openai",
                        model="gpt-4o-mini",
                        with_lilypad=False,  # This triggers prompt
                        stream=True,  # This does NOT trigger prompt
                        source=None
                    )
                    
                    mock_component_manager.add_component.assert_called_once_with(
                        "chat-agent",
                        provider="openai",
                        model="gpt-4o-mini",
                        with_lilypad=False,
                        stream=True,
                        source_alias=None
                    )
    
    def test_add_component_already_exists_error(self, tmp_path):
        """Test error when component directory already exists."""
        mock_component_manager = Mock()
        mock_component_manager.add_component.side_effect = SystemExit(1)
        
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Confirm.ask") as mock_confirm:
                    mock_confirm.side_effect = [False, False]
                    
                    import typer
                    from funcn_cli.commands import add as add_module
                    ctx = Mock(spec=typer.Context)
                    ctx.invoked_subcommand = None
                    
                    with pytest.raises(SystemExit) as exc_info:
                        add_module.add(
                            ctx,
                            identifier="existing-agent",
                            provider="openai",
                            model="gpt-4o-mini",
                            with_lilypad=False,
                            stream=None,
                            source=None
                        )
                    
                    assert exc_info.value.code == 1
    
    def test_add_component_not_found(self, tmp_path):
        """Test error when component not found in registry."""
        mock_component_manager = Mock()
        mock_component_manager.add_component.side_effect = Exception("Component 'unknown-agent' not found in registry")
        
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("funcn_cli.commands.add.console") as mock_console:
                    with patch("rich.prompt.Confirm.ask") as mock_confirm:
                        mock_confirm.side_effect = [False, False]
                        
                        import typer
                        from funcn_cli.commands import add as add_module
                        ctx = Mock(spec=typer.Context)
                        ctx.invoked_subcommand = None
                        
                        # The add function doesn't catch exceptions - they bubble up
                        with pytest.raises(Exception) as exc_info:
                            add_module.add(
                                ctx,
                                identifier="unknown-agent",
                                provider="openai",
                                model="gpt-4o-mini",
                                with_lilypad=False,
                                stream=None,
                                source=None
                            )
                        
                        assert "Component 'unknown-agent' not found" in str(exc_info.value)
    
    def test_add_with_all_options(self, tmp_path):
        """Test adding component with all CLI options specified."""
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                # No prompts needed since all options are specified
                import typer
                from funcn_cli.commands import add as add_module
                ctx = Mock(spec=typer.Context)
                ctx.invoked_subcommand = None
                
                add_module.add(
                    ctx,
                    identifier="ml-agent",
                    provider="google",
                    model="gemini-pro",
                    with_lilypad=True,  # No prompt - explicitly True
                    stream=True,  # No prompt - explicitly True
                    source=None
                )
                
                mock_component_manager.add_component.assert_called_once_with(
                    "ml-agent",
                    provider="google",
                    model="gemini-pro",
                    with_lilypad=True,
                    stream=True,
                    source_alias=None
                )
    
    def test_add_empty_identifier_interactive(self, tmp_path):
        """Test that empty identifier in interactive mode handles correctly."""
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Prompt.ask") as mock_prompt:
                    with patch("rich.prompt.Confirm.ask") as mock_confirm:
                        mock_prompt.side_effect = [
                            "",  # Empty identifier
                            "openai",
                            "gpt-4",
                        ]
                        mock_confirm.side_effect = [False, False]
                        
                        import typer
                        from funcn_cli.commands import add as add_module
                        ctx = Mock(spec=typer.Context)
                        ctx.invoked_subcommand = None
                        
                        add_module.add(
                            ctx,
                            identifier=None,
                            provider=None,
                            model=None,
                            with_lilypad=False,
                            stream=None,
                            source=None
                        )
                        
                        # Should try to add with empty string
                        mock_component_manager.add_component.assert_called_once_with(
                            "",
                            provider="openai",
                            model="gpt-4",
                            with_lilypad=False,
                            stream=False,
                            source_alias=None
                        )
    
    def test_add_missing_config_file(self, tmp_path):
        """Test adding component when funcn.json is missing."""
        # ConfigManager should raise an error when config is missing
        with patch("funcn_cli.commands.add.ConfigManager") as mock_config_cls:
            mock_config_cls.side_effect = Exception("No funcn.json found")
            
            import typer
            from funcn_cli.commands import add as add_module
            ctx = Mock(spec=typer.Context)
            ctx.invoked_subcommand = None
            
            with pytest.raises(Exception) as exc_info:
                add_module.add(
                    ctx,
                    identifier="test-agent",
                    provider="openai",
                    model="gpt-4",
                    with_lilypad=True,
                    stream=True,
                    source=None
                )
            
            assert "No funcn.json found" in str(exc_info.value)
    
    def test_add_with_config_defaults(self, tmp_path):
        """Test that config defaults are used when options not specified."""
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        # These should be loaded from the actual config
        mock_config.config.defaultProvider = "anthropic"
        mock_config.config.defaultModel = "claude-3-haiku"
        mock_config.config.stream = True
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Prompt.ask") as mock_prompt:
                    with patch("rich.prompt.Confirm.ask") as mock_confirm:
                        # Mock prompts to use defaults
                        mock_prompt.side_effect = [
                            "test-agent",
                            "anthropic",  # Should use default
                            "claude-3-haiku",  # Should use default
                        ]
                        mock_confirm.side_effect = [
                            False,  # Lilypad
                            True,   # Stream - should use default
                        ]
                        
                        import typer
                        from funcn_cli.commands import add as add_module
                        ctx = Mock(spec=typer.Context)
                        ctx.invoked_subcommand = None
                        
                        add_module.add(
                            ctx,
                            identifier=None,
                            provider=None,
                            model=None,
                            with_lilypad=False,
                            stream=None,
                            source=None
                        )
                        
                        # Should use config defaults
                        mock_component_manager.add_component.assert_called_once_with(
                            "test-agent",
                            provider="anthropic",
                            model="claude-3-haiku",
                            with_lilypad=False,
                            stream=True,
                            source_alias=None
                        )
    
    @pytest.mark.parametrize("provider,model", [
        ("openai", "gpt-4o"),
        ("anthropic", "claude-3-opus"),
        ("google", "gemini-pro"),
        ("mistral", "mistral-large"),
    ])
    def test_add_different_providers(self, tmp_path, provider, model):
        """Test adding components with different provider/model combinations."""
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Confirm.ask") as mock_confirm:
                    mock_confirm.side_effect = [False, False]
                    
                    import typer
                    from funcn_cli.commands import add as add_module
                    ctx = Mock(spec=typer.Context)
                    ctx.invoked_subcommand = None
                    
                    add_module.add(
                        ctx,
                        identifier="test-agent",
                        provider=provider,
                        model=model,
                        with_lilypad=False,
                        stream=None,
                        source=None
                    )
                    
                    mock_component_manager.add_component.assert_called_once_with(
                        "test-agent",
                        provider=provider,
                        model=model,
                        with_lilypad=False,
                        stream=False,
                        source_alias=None
                    )
    
    def test_add_whitespace_handling(self, tmp_path):
        """Test that whitespace in identifier is handled properly."""
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Prompt.ask") as mock_prompt:
                    with patch("rich.prompt.Confirm.ask") as mock_confirm:
                        mock_prompt.side_effect = [
                            "  test-agent  ",  # With whitespace
                            "openai",
                            "gpt-4",
                        ]
                        mock_confirm.side_effect = [False, False]
                        
                        import typer
                        from funcn_cli.commands import add as add_module
                        ctx = Mock(spec=typer.Context)
                        ctx.invoked_subcommand = None
                        
                        add_module.add(
                            ctx,
                            identifier=None,
                            provider=None,
                            model=None,
                            with_lilypad=False,
                            stream=None,
                            source=None
                        )
                        
                        # Should strip whitespace
                        mock_component_manager.add_component.assert_called_once()
                        args = mock_component_manager.add_component.call_args[0]
                        assert args[0] == "test-agent"  # Whitespace stripped
    
    def test_add_help_command(self):
        """Test that add --help displays usage information."""
        result = self.run_command(["add", "--help"])
        
        self.assert_command_success(result)
        assert "Add a component" in result.output
        assert "--provider" in result.output
        assert "--model" in result.output
        assert "--with-lilypad" in result.output
        assert "--stream" in result.output
        assert "--source" in result.output
    
    def test_add_with_source_parameter(self, tmp_path):
        """Test adding component from a specific registry source."""
        mock_component_manager = Mock()
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.defaultProvider = "openai"
        mock_config.config.defaultModel = "gpt-4o-mini"
        mock_config.config.stream = False
        
        with patch("funcn_cli.commands.add.ConfigManager", return_value=mock_config):
            with patch("funcn_cli.commands.add.ComponentManager", return_value=mock_component_manager):
                with patch("rich.prompt.Confirm.ask") as mock_confirm:
                    mock_confirm.side_effect = [False, False]
                    
                    import typer
                    from funcn_cli.commands import add as add_module
                    ctx = Mock(spec=typer.Context)
                    ctx.invoked_subcommand = None
                    
                    # Add component from specific source
                    add_module.add(
                        ctx,
                        identifier="custom-agent",
                        provider="openai",
                        model="gpt-4",
                        with_lilypad=False,
                        stream=None,
                        source="custom_registry"
                    )
                    
                    # Verify source alias was passed to ComponentManager
                    mock_component_manager.add_component.assert_called_once_with(
                        "custom-agent",
                        provider="openai",
                        model="gpt-4",
                        with_lilypad=False,
                        stream=False,
                        source_alias="custom_registry"
                    )
