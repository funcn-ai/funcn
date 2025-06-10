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

    @pytest.mark.asyncio
    async def test_dnd_game_master_async_structure(self):
        """Test that dnd_game_master is properly async."""
        func = self.get_component_function()
        
        # Test that function is async
        import inspect
        assert inspect.iscoroutinefunction(func)
        
        # Test function signature includes all required parameters
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        expected_params = ['campaign_name', 'players', 'starting_location', 
                          'dm_provider', 'dm_model', 'session_length',
                          'enable_persistence', 'db_path', 'load_session_id']
        for param in expected_params:
            assert param in params

    @pytest.mark.asyncio 
    async def test_game_state_initialization(self):
        """Test that GameState model exists and has proper fields."""
        # Mock the tool imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test that GameState and related models exist
        assert hasattr(module, 'GameState')
        assert hasattr(module, 'GamePhase')
        
        # Check GameState has expected fields
        GameState = module.GameState
        expected_fields = [
            'session_id', 'campaign_name', 'current_phase', 'location',
            'scene_description', 'active_players', 'npcs_present',
            'combat_round', 'combat_order', 'recent_events',
            'quest_status', 'world_state', 'game_time', 'days_elapsed'
        ]
        
        # Check fields exist in the model
        for field in expected_fields:
            assert field in GameState.model_fields

    @pytest.mark.asyncio
    async def test_process_player_turn(self):
        """Test the process_player_turn function."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test that process_player_turn exists and is async
        assert hasattr(module, 'process_player_turn')
        import inspect
        assert inspect.iscoroutinefunction(module.process_player_turn)

    @pytest.mark.asyncio
    async def test_dice_rolling_functions(self):
        """Test dice rolling helper functions."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dice_roller_mock.roll_dice = MagicMock(return_value=MagicMock(
            dice_type="d20", num_dice=1, rolls=[15], modifier=2, total=17,
            purpose="ability check", critical=False
        ))
        dice_roller_mock.format_roll_result = MagicMock(return_value="Rolled 1d20+2: [15] + 2 = 17")
        
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test roll_ability_check with proper parameters
        result = await module.roll_ability_check(
            character_name="Test Character",
            ability="strength", 
            skill=None,
            modifier=2,
            advantage=False,
            disadvantage=False,
            proficiency_bonus=2,
            is_proficient=True,
            has_expertise=False
        )
        assert result is not None
        assert isinstance(result, str)
        assert "Rolled" in result or "Proficiency" in result
        dice_roller_mock.roll_dice.assert_called_once()
        
        # Test roll_saving_throw
        dice_roller_mock.roll_dice.reset_mock()
        result = await module.roll_saving_throw(
            character_name="Test Character",
            ability="dexterity",
            dc=15,
            modifier=1,
            proficiency_bonus=2,
            is_proficient=False,
            advantage=False,
            disadvantage=False
        )
        assert result is not None
        assert isinstance(result, str)
        dice_roller_mock.roll_dice.assert_called_once()

    @pytest.mark.asyncio
    async def test_combat_and_roleplay_functions(self):
        """Test combat and roleplay scene functions exist and are async."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test run_combat_round
        assert hasattr(module, 'run_combat_round')
        import inspect
        assert inspect.iscoroutinefunction(module.run_combat_round)
        
        # Test run_roleplay_scene  
        assert hasattr(module, 'run_roleplay_scene')
        assert inspect.iscoroutinefunction(module.run_roleplay_scene)

    @pytest.mark.asyncio
    async def test_persistence_functions(self):
        """Test game state persistence functions."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        sqlite_mock.create_agent_state_table = AsyncMock()
        sqlite_mock.store_agent_state = AsyncMock()
        sqlite_mock.get_agent_state = AsyncMock(return_value=None)
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test persistence functions exist
        assert hasattr(module, 'initialize_campaign_database')
        assert hasattr(module, 'save_game_state')
        assert hasattr(module, 'load_game_state')
        
        # Test they are async
        import inspect
        assert inspect.iscoroutinefunction(module.initialize_campaign_database)
        assert inspect.iscoroutinefunction(module.save_game_state)
        assert inspect.iscoroutinefunction(module.load_game_state)

    @pytest.mark.asyncio
    async def test_character_stat_calculations(self):
        """Test character stat and modifier calculations."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test CharacterStats
        CharacterStats = module.CharacterStats
        stats = CharacterStats(
            strength=15, dexterity=12, constitution=14,
            intelligence=10, wisdom=13, charisma=8
        )
        
        # Test ability modifiers
        assert stats.get_modifier("strength") == 2  # (15-10)//2 = 2
        assert stats.get_modifier("dexterity") == 1  # (12-10)//2 = 1
        assert stats.get_modifier("charisma") == -1  # (8-10)//2 = -1
        
        # Test saving throw modifiers
        assert stats.get_saving_throw_modifier("strength", 2, True) == 4  # 2 + 2
        assert stats.get_saving_throw_modifier("strength", 2, False) == 2  # 2 + 0

    @pytest.mark.asyncio 
    async def test_spell_slot_management(self):
        """Test spell slot tracking and usage."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test SpellSlots
        SpellSlots = module.SpellSlots
        slots = SpellSlots(level_1=3, level_2=2)
        
        # Test available slots
        assert slots.get_available_slots(1) == 3
        assert slots.get_available_slots(2) == 2
        assert slots.get_available_slots(3) == 0
        
        # Test using slots
        assert slots.use_slot(1) is True
        assert slots.get_available_slots(1) == 2
        assert slots.use_slot(3) is False  # No level 3 slots
        
        # Test reset
        slots.reset_slots()
        assert slots.get_available_slots(1) == 3

    @pytest.mark.asyncio
    async def test_position_calculations(self):
        """Test position and distance calculations."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test Position
        Position = module.Position
        pos1 = Position(x=0, y=0, z=0)
        pos2 = Position(x=3, y=4, z=0)
        
        # Test distance calculation (3-4-5 triangle)
        assert pos1.distance_to(pos2) == 25.0  # 5 * 5 feet per square
        
        # Test adjacency
        pos3 = Position(x=1, y=1, z=0)
        assert pos1.is_adjacent(pos3) is True
        assert pos1.is_adjacent(pos2) is False

    @pytest.mark.asyncio
    async def test_llm_decorated_functions(self):
        """Test that LLM-decorated functions are properly configured."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test that key LLM functions exist
        llm_functions = [
            'generate_dm_response',
            'generate_ai_player_action',
            'generate_character_dialogue'
        ]
        
        for func_name in llm_functions:
            assert hasattr(module, func_name), f"Missing LLM function: {func_name}"
            func = getattr(module, func_name)
            assert callable(func)

    @pytest.mark.unit
    def test_enums_and_constants(self):
        """Test that all required enums are properly defined."""
        # Mock imports
        dice_roller_mock = MagicMock()
        dnd_api_mock = MagicMock()
        sqlite_mock = MagicMock()
        
        sys.modules['packages.funcn_registry.components.tools.dice_roller.tool'] = dice_roller_mock
        sys.modules['packages.funcn_registry.components.tools.dnd_5e_api.tool'] = dnd_api_mock
        sys.modules['packages.funcn_registry.components.tools.sqlite_db.tool'] = sqlite_mock
        
        # Import module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "dnd_game_master", "packages/funcn_registry/components/agents/game_playing_dnd/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test PlayerType enum
        PlayerType = module.PlayerType
        assert PlayerType.HUMAN == "human"
        assert PlayerType.AI == "ai"
        assert PlayerType.DM == "dm"
        
        # Test GamePhase enum
        GamePhase = module.GamePhase
        assert hasattr(GamePhase, 'EXPLORATION')
        assert hasattr(GamePhase, 'COMBAT')
        assert hasattr(GamePhase, 'ROLEPLAY')
        assert hasattr(GamePhase, 'PUZZLE')
        assert hasattr(GamePhase, 'REST')
        
        # Test ActionType enum
        ActionType = module.ActionType
        assert hasattr(ActionType, 'MOVEMENT')
        assert hasattr(ActionType, 'ATTACK')
        assert hasattr(ActionType, 'SPELL')
        assert hasattr(ActionType, 'SKILL_CHECK')
        
        # Test DiceType enum
        DiceType = module.DiceType
        assert DiceType.D20 == "d20"
        assert DiceType.D6 == "d6"
        assert DiceType.D8 == "d8"
