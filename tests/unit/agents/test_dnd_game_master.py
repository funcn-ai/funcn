"""Test suite for dnd_game_master following best practices."""

import pytest
import sys
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, MagicMock, patch


class TestDndGameMasterAgent(BaseAgentTest):
    """Test cases for D&D game master agent."""

    component_name = "dnd_game_master"
    component_path = Path("packages/funcn_registry/components/agents/game_playing_dnd")

    def get_component_function(self):
        """Get the main agent function."""
        # Mock the tool imports before loading the module
        dice_roller_mock = MagicMock()
        dice_roller_mock.DiceRoll = MagicMock
        dice_roller_mock.DiceType = MagicMock
        dice_roller_mock.format_roll_result = MagicMock()
        dice_roller_mock.roll_dice = MagicMock()
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.dnd_game_master

    def get_test_inputs(self):
        """Get test input cases."""
        # Import PlayerCharacter model for test data
        import importlib.util
        
        # Mock the tool imports
        dice_roller_mock = MagicMock()
        dice_roller_mock.DiceRoll = MagicMock
        dice_roller_mock.DiceType = MagicMock
        dice_roller_mock.format_roll_result = MagicMock()
        dice_roller_mock.roll_dice = MagicMock()
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        PlayerCharacter = module.PlayerCharacter
        CharacterSheet = module.CharacterSheet
        CharacterStats = module.CharacterStats
        PlayerType = module.PlayerType
        
        # Create test players
        stats = CharacterStats(
            strength=15, dexterity=12, constitution=14,
            intelligence=10, wisdom=13, charisma=8
        )
        
        sheet = CharacterSheet(
            name="Thorin",
            race="Dwarf",
            character_class="Fighter",
            level=1,
            stats=stats,
            hp=10,
            max_hp=10,
            armor_class=16,
            proficiency_bonus=2,
            skills=["Athletics", "Intimidation"],
            equipment=[],
            spell_slots={},
            conditions=[],
            death_saves_success=0,
            death_saves_failure=0,
            exhaustion_level=0
        )
        
        player1 = PlayerCharacter(
            character=sheet,
            player_type=PlayerType.HUMAN,
            ai_model=None,
            ai_provider=None,
            personality=None
        )
        
        return [
            {
                "campaign_name": "Lost Mines of Phandelver",
                "players": [player1],
                "starting_location": "Neverwinter",
                "dm_provider": "openai",
                "dm_model": "gpt-4o-mini",
                "session_length": 60,
                "enable_persistence": False,
            },
            {
                "campaign_name": "Curse of Strahd",
                "players": None,  # Will use default
                "starting_location": "Barovia",
                "dm_provider": "anthropic",
                "dm_model": "claude-3-haiku-20240307",
                "session_length": 120,
                "enable_persistence": False,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Mock the tool imports
        dice_roller_mock = MagicMock()
        dice_roller_mock.DiceRoll = MagicMock
        dice_roller_mock.DiceType = MagicMock
        dice_roller_mock.format_roll_result = MagicMock()
        dice_roller_mock.roll_dice = MagicMock()
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
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
        # Mock the tool imports
        dice_roller_mock = MagicMock()
        dice_roller_mock.DiceRoll = MagicMock
        dice_roller_mock.DiceType = MagicMock
        dice_roller_mock.format_roll_result = MagicMock()
        dice_roller_mock.roll_dice = MagicMock()
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'GameState')
        assert hasattr(module, 'CharacterSheet')
        assert hasattr(module, 'BattleMap')
        assert hasattr(module, 'GamePhase')
        assert hasattr(module, 'ActionType')
        assert hasattr(module, 'PlayerAction')
        assert hasattr(module, 'DMResponse')

        # Test basic enum instantiation
        GamePhase = module.GamePhase
        assert hasattr(GamePhase, 'ROLEPLAY')
        assert hasattr(GamePhase, 'COMBAT')

        # Test ActionType enum
        ActionType = module.ActionType
        assert ActionType.ATTACK == "attack"
        assert ActionType.SPELL == "spell"

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
        assert any(p in params for p in ['dm_provider', 'dm_model'])

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Mock the tool imports
        dice_roller_mock = MagicMock()
        dice_roller_mock.DiceRoll = MagicMock
        dice_roller_mock.DiceType = MagicMock
        dice_roller_mock.format_roll_result = MagicMock()
        dice_roller_mock.roll_dice = MagicMock()
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        GameState = module.GameState

        # DND game master should return a GameState
        assert isinstance(output, GameState)
        assert hasattr(output, "session_id")
        assert hasattr(output, "campaign_name")
        assert hasattr(output, "current_phase")
        assert hasattr(output, "party")
        assert hasattr(output, "current_location")
        assert hasattr(output, "recent_events")
        assert hasattr(output, "player_inventory")
        assert isinstance(output.party, list)
        assert isinstance(output.recent_events, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Mock the tool imports
        dice_roller_mock = MagicMock()
        dice_roller_mock.DiceRoll = MagicMock
        dice_roller_mock.DiceType = MagicMock
        dice_roller_mock.format_roll_result = MagicMock()
        dice_roller_mock.roll_dice = MagicMock()
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test roll_ability_check
        func = module.roll_ability_check
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        
        # Test roll_saving_throw
        func = module.roll_saving_throw
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test run_combat_round
        func = module.run_combat_round
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test run_roleplay_scene
        func = module.run_roleplay_scene
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

    @pytest.mark.unit
    def test_dnd_mechanics(self):
        """Test that D&D game mechanics are supported."""
        # Mock the tool imports
        dice_roller_mock = MagicMock()
        dice_roller_mock.DiceRoll = MagicMock
        dice_roller_mock.DiceType = MagicMock
        dice_roller_mock.format_roll_result = MagicMock()
        dice_roller_mock.roll_dice = MagicMock()
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
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
        # Mock the tool imports
        dice_roller_mock = MagicMock()
        dice_roller_mock.DiceRoll = MagicMock
        dice_roller_mock.DiceType = MagicMock
        dice_roller_mock.format_roll_result = MagicMock()
        dice_roller_mock.roll_dice = MagicMock()
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
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
