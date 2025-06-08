"""Test suite for game_playing_dnd following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestGamePlayingDndAgent(BaseAgentTest):
    """Test cases for D&D game playing agent."""

    component_name = "game_playing_dnd"
    component_path = Path("packages/funcn_registry/components/agents/game_playing_dnd")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_dnd", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.dnd_game_master

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "campaign_name": "Lost Mines of Phandelver",
                "players": [
                    {"name": "Thorin", "race": "Dwarf", "class": "Fighter", "level": 1},
                    {"name": "Elara", "race": "Elf", "class": "Wizard", "level": 1},
                    {"name": "Raven", "race": "Human", "class": "Rogue", "level": 1},
                    {"name": "Brother Marcus", "race": "Human", "class": "Cleric", "level": 1},
                ],
                "session_number": 1,
                "db_path": None,
            },
            {
                "campaign_name": "Curse of Strahd",
                "players": [
                    {"name": "Sir Galahad", "race": "Human", "class": "Paladin", "level": 3},
                    {"name": "Luna", "race": "Halfling", "class": "Druid", "level": 3},
                ],
                "session_number": 5,
                "db_path": None,
            },
            {
                "campaign_name": "Homebrew Adventure",
                "players": [{"name": "Gruk", "race": "Half-Orc", "class": "Barbarian", "level": 5}],
                "session_number": 10,
                "db_path": None,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_dnd", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, 'dnd_game_master')
        assert callable(module.dnd_game_master)
        assert hasattr(module, 'dnd_game_master_stream')
        assert callable(module.dnd_game_master_stream)
        assert hasattr(module, 'process_player_turn')
        assert callable(module.process_player_turn)
        assert hasattr(module, 'run_combat_round')
        assert callable(module.run_combat_round)
        assert hasattr(module, 'run_roleplay_scene')
        assert callable(module.run_roleplay_scene)
        assert hasattr(module, 'initialize_campaign_database')
        assert callable(module.initialize_campaign_database)
        assert hasattr(module, 'save_game_state')
        assert callable(module.save_game_state)
        assert hasattr(module, 'load_game_state')
        assert callable(module.load_game_state)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_dnd", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'GameState')
        assert hasattr(module, 'CharacterSheet')
        assert hasattr(module, 'CombatState')
        assert hasattr(module, 'GameMode')
        assert hasattr(module, 'ActionType')
        assert hasattr(module, 'PlayerAction')
        assert hasattr(module, 'GameResponse')

        # Test basic enum instantiation
        GameMode = module.GameMode
        assert GameMode.ROLEPLAY == "roleplay"
        assert GameMode.COMBAT == "combat"

        # Test ActionType enum
        ActionType = module.ActionType
        assert ActionType.ATTACK == "attack"
        assert ActionType.CAST_SPELL == "cast_spell"

    @pytest.mark.unit
    def test_dnd_game_master_structure(self):
        """Test basic structure of dnd_game_master function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'campaign_name' in params
        assert 'players' in params
        assert 'session_number' in params or 'db_path' in params
        assert 'llm_provider' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_dnd", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        GameResponse = module.GameResponse

        # DND game master should return a GameResponse
        assert isinstance(output, GameResponse)
        assert hasattr(output, "narration")
        assert hasattr(output, "dice_rolls")
        assert hasattr(output, "state_changes")
        assert hasattr(output, "npc_dialogue")
        assert hasattr(output, "player_options")
        assert hasattr(output, "combat_log")
        assert hasattr(output, "session_summary")
        assert isinstance(output.dice_rolls, list)
        assert isinstance(output.player_options, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "game_playing_dnd", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test roll_dice
        func = module.roll_dice
        assert callable(func)
        # roll_dice might not be async
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert any(p in params for p in ['dice_string', 'dice_type', 'dice', 'roll'])

        # Test manage_combat
        func = module.manage_combat
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test narrate_scene
        func = module.narrate_scene
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

    @pytest.mark.unit
    def test_dnd_mechanics(self):
        """Test that D&D game mechanics are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_dnd", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for D&D-specific features
        import inspect

        source = inspect.getsource(module)
        assert 'd20' in source.lower() or 'dice' in source.lower()
        assert 'initiative' in source.lower() or 'combat' in source.lower()
        assert 'spell' in source.lower() or 'magic' in source.lower()
        assert 'skill' in source.lower() or 'ability' in source.lower()
        assert 'save' in source.lower() or 'saving throw' in source.lower()
        assert 'damage' in source.lower() or 'hp' in source.lower() or 'hit points' in source.lower()

    @pytest.mark.unit
    def test_game_modes(self):
        """Test that different game modes are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_dnd", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for game mode support
        import inspect

        source = inspect.getsource(module)
        assert 'combat' in source.lower()
        assert 'roleplay' in source.lower() or 'dialogue' in source.lower()
        assert 'exploration' in source.lower() or 'explore' in source.lower()
        assert 'puzzle' in source.lower() or 'riddle' in source.lower()
