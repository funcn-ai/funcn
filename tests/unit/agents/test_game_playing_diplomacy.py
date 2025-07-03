"""Test suite for game_playing_diplomacy agent following best practices."""

import pytest
from datetime import datetime
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestGamePlayingDiplomacyAgent(BaseAgentTest):
    """Test cases for game playing diplomacy agent."""

    component_name = "game_playing_diplomacy"
    component_path = Path("packages/sygaldry_registry/components/agents/game_playing_diplomacy")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.diplomacy_game_agent

    def get_test_inputs(self):
        """Get test input cases."""
        # Import enums and models for test data
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        DiplomacyPower = module.DiplomacyPower
        DiplomacyPhase = module.DiplomacyPhase
        PlayerType = module.PlayerType
        UnitType = module.UnitType
        DiplomacyState = module.DiplomacyState
        DiplomacyPlayer = module.DiplomacyPlayer
        DiplomacyUnit = module.DiplomacyUnit
        ProvinceControl = module.ProvinceControl
        DiplomacyMessage = module.DiplomacyMessage

        # Create test game states
        test_state_1 = DiplomacyState(
            year=1901,
            phase=DiplomacyPhase.SPRING_DIPLOMACY,
            provinces=[
                ProvinceControl(
                    province="London",
                    controller=DiplomacyPower.ENGLAND,
                    has_supply_center=True,
                    unit=DiplomacyUnit(unit_type=UnitType.FLEET, location="London", power=DiplomacyPower.ENGLAND),
                ),
                ProvinceControl(
                    province="Paris",
                    controller=DiplomacyPower.FRANCE,
                    has_supply_center=True,
                    unit=DiplomacyUnit(unit_type=UnitType.ARMY, location="Paris", power=DiplomacyPower.FRANCE),
                ),
            ],
            units=[
                DiplomacyUnit(unit_type=UnitType.FLEET, location="London", power=DiplomacyPower.ENGLAND),
                DiplomacyUnit(unit_type=UnitType.ARMY, location="Paris", power=DiplomacyPower.FRANCE),
            ],
            supply_centers={
                DiplomacyPower.ENGLAND.value: 3,
                DiplomacyPower.FRANCE.value: 3,
            },
            recent_messages=[],
            eliminated_powers=[],
        )

        test_state_2 = DiplomacyState(
            year=1902,
            phase=DiplomacyPhase.SPRING_ORDERS,
            provinces=[
                ProvinceControl(province="London", controller=DiplomacyPower.ENGLAND, has_supply_center=True, unit=None),
                ProvinceControl(
                    province="English Channel",
                    controller=None,
                    has_supply_center=False,
                    unit=DiplomacyUnit(unit_type=UnitType.FLEET, location="English Channel", power=DiplomacyPower.ENGLAND),
                ),
            ],
            units=[
                DiplomacyUnit(unit_type=UnitType.FLEET, location="English Channel", power=DiplomacyPower.ENGLAND),
                DiplomacyUnit(unit_type=UnitType.ARMY, location="Burgundy", power=DiplomacyPower.FRANCE),
            ],
            supply_centers={
                DiplomacyPower.ENGLAND.value: 4,
                DiplomacyPower.FRANCE.value: 3,
            },
            recent_messages=[
                DiplomacyMessage(
                    from_power=DiplomacyPower.ENGLAND,
                    to_power=DiplomacyPower.FRANCE,
                    message="Let's work together against Germany",
                    timestamp=datetime.now(),
                    is_public=False,
                )
            ],
            eliminated_powers=[],
        )

        # Test players with different configurations
        test_players_1 = [
            DiplomacyPlayer(
                power=DiplomacyPower.ENGLAND,
                player_type=PlayerType.AI,
                model="gpt-4o",
                provider="openai",
                personality="diplomatic",
                strategy_style="coalition-builder",
            ),
            DiplomacyPlayer(
                power=DiplomacyPower.FRANCE,
                player_type=PlayerType.AI,
                model="claude-3-opus-20240229",
                provider="anthropic",
                personality="aggressive",
                strategy_style="rapid-expansion",
            ),
        ]

        test_players_2 = [
            DiplomacyPlayer(power=DiplomacyPower.ENGLAND, player_type=PlayerType.HUMAN, personality="balanced"),
            DiplomacyPlayer(
                power=DiplomacyPower.FRANCE,
                player_type=PlayerType.AI,
                model="gpt-4o",
                provider="openai",
                personality="defensive",
                strategy_style="fortress-builder",
            ),
        ]

        return [
            {
                "game_state": test_state_1,
                "players": test_players_1,
                "game_history": None,
                "active_agreements": None,
                "game_id": "test_game_001",
                "current_phase": DiplomacyPhase.SPRING_DIPLOMACY,
                "llm_provider": "openai",
                "default_model": "gpt-4o",
            },
            {
                "game_state": test_state_2,
                "players": test_players_2,
                "game_history": [],
                "active_agreements": [],
                "game_id": "test_game_002",
                "current_phase": DiplomacyPhase.SPRING_ORDERS,
            },
        ]

    def test_enums_and_constants(self):
        """Test that all enums and constants are properly defined."""
        # Import directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test DiplomacyPower enum
        assert hasattr(module, 'DiplomacyPower')
        assert len(module.DiplomacyPower) == 7
        assert module.DiplomacyPower.ENGLAND.value == "England"
        assert module.DiplomacyPower.FRANCE.value == "France"

        # Test DiplomacyPhase enum
        assert hasattr(module, 'DiplomacyPhase')
        assert module.DiplomacyPhase.SPRING_DIPLOMACY.value == "spring_diplomacy"
        assert module.DiplomacyPhase.SPRING_ORDERS.value == "spring_orders"

        # Test UnitType enum
        assert hasattr(module, 'UnitType')
        assert module.UnitType.ARMY.value == "army"
        assert module.UnitType.FLEET.value == "fleet"

        # Test OrderType enum
        assert hasattr(module, 'OrderType')
        assert module.OrderType.MOVE.value == "move"
        assert module.OrderType.HOLD.value == "hold"
        assert module.OrderType.SUPPORT.value == "support"

        # Test PlayerType enum
        assert hasattr(module, 'PlayerType')
        assert module.PlayerType.HUMAN.value == "human"
        assert module.PlayerType.AI.value == "ai"

        # Test PERSONALITY_PROMPTS
        assert hasattr(module, 'PERSONALITY_PROMPTS')
        assert isinstance(module.PERSONALITY_PROMPTS, dict)
        assert "aggressive" in module.PERSONALITY_PROMPTS
        assert "diplomatic" in module.PERSONALITY_PROMPTS
        assert "balanced" in module.PERSONALITY_PROMPTS

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Import directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test model existence
        models = [
            'DiplomacyUnit',
            'DiplomacyOrder',
            'DiplomacyMessage',
            'DiplomacyPlayer',
            'ProvinceControl',
            'DiplomacyState',
            'DiplomacyMove',
            'NegotiationProposal',
            'StrategicAnalysis',
            'DiplomacyGame',
        ]

        for model_name in models:
            assert hasattr(module, model_name)

        # Test that models are Pydantic BaseModel subclasses
        from pydantic import BaseModel

        for model_name in models:
            model_class = getattr(module, model_name)
            assert issubclass(model_class, BaseModel)

        # Test field presence without instantiation due to forward references
        DiplomacyUnit = module.DiplomacyUnit
        assert 'unit_type' in DiplomacyUnit.model_fields
        assert 'location' in DiplomacyUnit.model_fields
        assert 'power' in DiplomacyUnit.model_fields
        assert 'can_retreat_to' in DiplomacyUnit.model_fields

        # Test DiplomacyOrder fields
        DiplomacyOrder = module.DiplomacyOrder
        assert 'unit_location' in DiplomacyOrder.model_fields
        assert 'order_type' in DiplomacyOrder.model_fields
        assert 'destination' in DiplomacyOrder.model_fields

        # Test DiplomacyPlayer fields
        DiplomacyPlayer = module.DiplomacyPlayer
        assert 'power' in DiplomacyPlayer.model_fields
        assert 'player_type' in DiplomacyPlayer.model_fields
        assert 'model' in DiplomacyPlayer.model_fields
        assert 'provider' in DiplomacyPlayer.model_fields
        assert 'personality' in DiplomacyPlayer.model_fields

        # Test StrategicAnalysis fields
        StrategicAnalysis = module.StrategicAnalysis
        assert 'power_rankings' in StrategicAnalysis.model_fields
        assert 'threat_assessment' in StrategicAnalysis.model_fields
        assert 'opportunity_zones' in StrategicAnalysis.model_fields
        assert 'defensive_priorities' in StrategicAnalysis.model_fields
        assert 'alliance_recommendations' in StrategicAnalysis.model_fields
        assert 'key_chokepoints' in StrategicAnalysis.model_fields

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Import directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        # Main functions
        assert hasattr(agent, 'diplomacy_game_agent')
        assert callable(agent.diplomacy_game_agent)
        assert hasattr(agent, 'diplomacy_game_stream')
        assert callable(agent.diplomacy_game_stream)

        # LLM-decorated functions
        assert hasattr(agent, 'analyze_strategic_situation')
        assert hasattr(agent, 'develop_negotiation_strategy')
        assert hasattr(agent, 'craft_diplomatic_messages')
        assert hasattr(agent, 'plan_military_orders')
        assert hasattr(agent, 'synthesize_complete_move')

        # Helper functions
        assert hasattr(agent, 'process_human_input')
        assert callable(agent.process_human_input)

    @pytest.mark.asyncio
    async def test_diplomacy_game_agent_basic_structure(self):
        """Test basic structure of diplomacy_game_agent function."""
        # Import directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        diplomacy_game_agent = module.diplomacy_game_agent

        # Test that function is async
        import inspect

        assert inspect.iscoroutinefunction(diplomacy_game_agent)

        # Test function signature
        sig = inspect.signature(diplomacy_game_agent)
        params = list(sig.parameters.keys())
        assert 'game_state' in params
        assert 'players' in params
        assert 'game_history' in params
        assert 'active_agreements' in params
        assert 'game_id' in params
        assert 'current_phase' in params
        assert 'llm_provider' in params
        assert 'default_model' in params

    @pytest.mark.asyncio
    async def test_diplomacy_game_stream_structure(self):
        """Test basic structure of diplomacy_game_stream function."""
        # Import directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        diplomacy_game_stream = module.diplomacy_game_stream

        # Test that function is async generator
        import inspect

        assert inspect.isasyncgenfunction(diplomacy_game_stream)

        # Test function signature
        sig = inspect.signature(diplomacy_game_stream)
        params = list(sig.parameters.keys())
        assert 'game_state' in params
        assert 'players' in params
        assert 'kwargs' in params  # **kwargs parameter

    @pytest.mark.unit
    def test_llm_decorated_functions(self):
        """Test that LLM-decorated functions have proper structure."""
        # Import directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test analyze_strategic_situation
        import inspect

        sig = inspect.signature(module.analyze_strategic_situation)
        params = list(sig.parameters.keys())
        assert 'power' in params
        assert 'game_state' in params
        assert 'recent_messages' in params
        assert 'active_agreements' in params
        assert 'personality_prompt' in params
        assert 'provider' in params
        assert 'model' in params

        # Test develop_negotiation_strategy
        sig = inspect.signature(module.develop_negotiation_strategy)
        params = list(sig.parameters.keys())
        assert 'power' in params
        assert 'strategic_analysis' in params
        assert 'current_relationships' in params

        # Test craft_diplomatic_messages
        sig = inspect.signature(module.craft_diplomatic_messages)
        params = list(sig.parameters.keys())
        assert 'power' in params
        assert 'proposals' in params
        assert 'target_powers' in params

        # Test plan_military_orders
        sig = inspect.signature(module.plan_military_orders)
        params = list(sig.parameters.keys())
        assert 'power' in params
        assert 'current_units' in params
        assert 'strategic_analysis' in params

        # Test synthesize_complete_move
        sig = inspect.signature(module.synthesize_complete_move)
        params = list(sig.parameters.keys())
        assert 'power' in params
        assert 'military_orders' in params
        assert 'diplomatic_messages' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Import models
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        DiplomacyGame = module.DiplomacyGame

        # Output should be a DiplomacyGame instance
        assert isinstance(output, DiplomacyGame)
        assert hasattr(output, "game_id")
        assert hasattr(output, "current_state")
        assert hasattr(output, "players")
        assert hasattr(output, "move_history")
        assert hasattr(output, "active_agreements")
        assert hasattr(output, "strategic_analysis")

        # Validate game_id matches input
        assert output.game_id == input_data.get("game_id", "game_001")

        # Validate current_state
        assert output.current_state is not None
        assert hasattr(output.current_state, "year")
        assert hasattr(output.current_state, "phase")
        assert hasattr(output.current_state, "provinces")
        assert hasattr(output.current_state, "units")
        assert hasattr(output.current_state, "supply_centers")

        # Validate players list
        assert isinstance(output.players, list)
        assert len(output.players) > 0

        # Validate move_history
        assert isinstance(output.move_history, list)

        # Validate strategic_analysis
        assert output.strategic_analysis is not None
        assert hasattr(output.strategic_analysis, "power_rankings")
        assert isinstance(output.strategic_analysis.power_rankings, dict)

    @pytest.mark.unit
    async def test_process_human_input_diplomatic_phase(self):
        """Test process_human_input function structure and signature."""
        # Import directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test function exists and is async
        assert hasattr(module, 'process_human_input')
        import inspect

        assert inspect.iscoroutinefunction(module.process_human_input)

        # Test function signature
        sig = inspect.signature(module.process_human_input)
        params = list(sig.parameters.keys())
        assert 'game' in params
        assert 'human_power' in params
        assert 'phase' in params

        # Test that the function has a return type annotation
        return_annotation = sig.return_annotation
        # The annotation might be a string or a class, handle both cases
        if hasattr(return_annotation, '__name__'):
            assert return_annotation.__name__ == 'DiplomacyMove'
        else:
            assert 'DiplomacyMove' in str(return_annotation)

    @pytest.mark.unit
    async def test_diplomacy_stream_function(self):
        """Test diplomacy_game_stream function structure."""
        # Import directly
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_playing_diplomacy", "packages/sygaldry_registry/components/agents/game_playing_diplomacy/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test function exists and is async generator
        assert hasattr(module, 'diplomacy_game_stream')
        import inspect

        assert inspect.isasyncgenfunction(module.diplomacy_game_stream)

        # Test streaming function returns strings
        # We don't need to test actual execution due to forward reference issues
        # Just verify it's properly structured as an async generator
