"""Test suite for game_playing_catan following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestGamePlayingCatanAgent(BaseAgentTest):
    """Test cases for game playing catan agent."""

    component_name = "game_playing_catan"
    component_path = Path("packages/sygaldry_registry/components/agents/game_playing_catan")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_catan", "packages/sygaldry_registry/components/agents/game_playing_catan/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.catan_game_agent

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "game_state": None,  # Will be created by the agent
                "players": [
                    {"name": "Player 1", "type": "strategic", "model": "gpt-4o"},
                    {"name": "Player 2", "type": "aggressive", "model": "gpt-4o"},
                    {"name": "Player 3", "type": "balanced", "model": "gpt-4o"},
                    {"name": "Player 4", "type": "human", "model": None},
                ],
                "action_history": [],
                "game_id": "test_game_001",
            },
            {
                "game_state": None,
                "players": [
                    {"name": "AI", "type": "aggressive", "model": "gpt-4o"},
                    {"name": "Human", "type": "human", "model": None},
                ],
                "action_history": [],
                "game_id": "test_game_002",
            },
            {
                "game_state": None,
                "players": [
                    {"name": "Player 1", "type": "balanced", "model": "gpt-4o"},
                    {"name": "Player 2", "type": "strategic", "model": "claude-3-5-sonnet-20241022"},
                    {"name": "Player 3", "type": "aggressive", "model": "gpt-4o"},
                ],
                "action_history": [],
                "game_id": "test_game_003",
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_catan", "packages/sygaldry_registry/components/agents/game_playing_catan/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, 'catan_game_agent')
        assert callable(module.catan_game_agent)
        assert hasattr(module, 'catan_game_stream')
        assert callable(module.catan_game_stream)
        assert hasattr(module, 'process_human_catan_input')
        assert callable(module.process_human_catan_input)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_catan", "packages/sygaldry_registry/components/agents/game_playing_catan/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'CatanState')
        assert hasattr(module, 'CatanPlayer')
        assert hasattr(module, 'CatanAction')
        assert hasattr(module, 'CatanGame')
        assert hasattr(module, 'Resource')
        assert hasattr(module, 'BuildingType')
        assert hasattr(module, 'DevelopmentCard')
        assert hasattr(module, 'CatanPhase')

        # Test basic enum instantiation
        Resource = module.Resource
        assert Resource.WOOD == "wood"
        assert Resource.BRICK == "brick"

        # Test CatanPhase enum
        CatanPhase = module.CatanPhase
        assert CatanPhase.ROLL_DICE == "roll_dice"
        assert CatanPhase.MAIN_TURN == "main_turn"

    @pytest.mark.unit
    def test_catan_game_agent_structure(self):
        """Test basic structure of catan_game_agent function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'game_state' in params
        assert 'players' in params
        assert 'action_history' in params
        assert 'game_id' in params
        assert 'llm_provider' in params
        assert 'default_model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_catan", "packages/sygaldry_registry/components/agents/game_playing_catan/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        CatanGame = module.CatanGame

        # Game playing agent should return a CatanGame
        assert isinstance(output, CatanGame)
        assert hasattr(output, "game_id")
        assert hasattr(output, "state")
        assert hasattr(output, "players")
        assert hasattr(output, "action_history")
        assert hasattr(output, "winner")
        assert hasattr(output, "summary")
        assert isinstance(output.players, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "game_playing_catan", "packages/sygaldry_registry/components/agents/game_playing_catan/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test process_human_catan_input
        func = module.process_human_catan_input
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'game' in params
        assert 'human_player' in params

        # Test catan_game_stream
        func = module.catan_game_stream
        assert callable(func)
        # It's an async generator, not a coroutine function
        assert inspect.isasyncgenfunction(func)

    @pytest.mark.unit
    def test_game_mechanics(self):
        """Test that Catan game mechanics are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_catan", "packages/sygaldry_registry/components/agents/game_playing_catan/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for Catan-specific features
        import inspect

        source = inspect.getsource(module)
        assert 'settlement' in source.lower()
        assert 'road' in source.lower()
        assert 'city' in source.lower() or 'cities' in source.lower()
        assert 'robber' in source.lower()
        assert 'trade' in source.lower()
        assert 'dice' in source.lower() or 'roll' in source.lower()
        assert 'resources' in source.lower() or 'resource' in source.lower()

    @pytest.mark.unit
    def test_player_types(self):
        """Test that different player types are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_catan", "packages/sygaldry_registry/components/agents/game_playing_catan/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for player type support
        import inspect

        source = inspect.getsource(module)
        assert 'strategic' in source.lower() or 'strategy' in source.lower()
        assert 'aggressive' in source.lower() or 'offensive' in source.lower()
        assert 'balanced' in source.lower() or 'defensive' in source.lower()
