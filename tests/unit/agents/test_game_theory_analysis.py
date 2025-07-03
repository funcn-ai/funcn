"""Test suite for game_theory_analysis following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestGameTheoryAnalysisAgent(BaseAgentTest):
    """Test cases for game theory analysis agent."""

    component_name = "game_theory_analysis"
    component_path = Path("packages/sygaldry_registry/components/agents/game_theory_analysis")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_theory_analysis", "packages/sygaldry_registry/components/agents/game_theory_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.analyze_strategic_situation

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "situation": "Two companies competing for market share with pricing strategies",
                "players": ["Company A", "Company B"],
                "analysis_depth": "comprehensive",
                "focus_areas": ["nash_equilibrium", "dominant_strategies", "payoff_analysis"],
            },
            {
                "situation": "Negotiation between employer and employee union",
                "players": ["Employer", "Union"],
                "analysis_depth": "standard",
                "focus_areas": ["bargaining", "cooperative_game"],
            },
            {
                "situation": "Environmental regulation compliance decision",
                "players": ["Government", "Industry", "Public"],
                "analysis_depth": "quick",
                "focus_areas": ["social_welfare", "enforcement"],
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_theory_analysis", "packages/sygaldry_registry/components/agents/game_theory_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions mentioned in component.json
        assert hasattr(module, 'analyze_strategic_situation')
        assert callable(module.analyze_strategic_situation)
        assert hasattr(module, 'identify_players_and_strategies')
        assert callable(module.identify_players_and_strategies)
        assert hasattr(module, 'construct_payoff_matrix')
        assert callable(module.construct_payoff_matrix)
        assert hasattr(module, 'find_equilibria')
        assert callable(module.find_equilibria)
        assert hasattr(module, 'analyze_dynamics')
        assert callable(module.analyze_dynamics)
        assert hasattr(module, 'generate_recommendations')
        assert callable(module.generate_recommendations)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_theory_analysis", "packages/sygaldry_registry/components/agents/game_theory_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'Player')
        assert hasattr(module, 'Strategy')
        assert hasattr(module, 'PayoffEntry')
        assert hasattr(module, 'Equilibrium')
        assert hasattr(module, 'GameTheoryAnalysis')

        # Test basic model instantiation
        Player = module.Player
        player = Player(
            name="Company A",
            objectives=["Maximize profit", "Maintain market share"],
            constraints=["Budget limit", "Regulatory compliance"],
            available_strategies=["High price", "Low price"],
        )
        assert player.name == "Company A"
        assert len(player.objectives) == 2
        assert len(player.available_strategies) == 2

        # Test Strategy model
        Strategy = module.Strategy
        strategy = Strategy(
            player="Company A",
            action="Set high price",
            description="Premium pricing strategy",
            conditions=["Market leader position"],
        )
        assert strategy.player == "Company A"
        assert strategy.action == "Set high price"

        # Test PayoffEntry model
        PayoffEntry = module.PayoffEntry
        payoff = PayoffEntry(
            strategies={"Company A": "High price", "Company B": "Low price"},
            payoffs={"Company A": 50.0, "Company B": 70.0},
            outcome_description="B captures market share",
        )
        assert payoff.payoffs["Company A"] == 50.0
        assert payoff.payoffs["Company B"] == 70.0

    @pytest.mark.unit
    def test_analyze_strategic_situation_structure(self):
        """Test basic structure of analyze_strategic_situation function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'situation' in params
        assert 'players' in params
        assert 'analysis_depth' in params
        assert 'focus_areas' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_theory_analysis", "packages/sygaldry_registry/components/agents/game_theory_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        GameTheoryAnalysis = module.GameTheoryAnalysis

        # Game theory analysis should return a GameTheoryAnalysis
        assert isinstance(output, GameTheoryAnalysis)
        assert hasattr(output, "situation_summary")
        assert hasattr(output, "game_type")
        assert hasattr(output, "players")
        assert hasattr(output, "strategies")
        assert hasattr(output, "payoff_matrix")
        assert hasattr(output, "equilibria")
        assert hasattr(output, "dominant_strategies")
        assert hasattr(output, "analysis_insights")
        assert hasattr(output, "recommendations")
        assert hasattr(output, "confidence_score")
        assert isinstance(output.players, list)
        assert isinstance(output.strategies, list)
        assert isinstance(output.equilibria, list)
        assert 0 <= output.confidence_score <= 1

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "game_theory_analysis", "packages/sygaldry_registry/components/agents/game_theory_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test identify_players_and_strategies
        func = module.identify_players_and_strategies
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'situation' in params
        assert 'players' in params

        # Test construct_payoff_matrix
        func = module.construct_payoff_matrix
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'players' in params
        assert 'strategies' in params

        # Test find_equilibria
        func = module.find_equilibria
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'payoff_matrix' in params

    @pytest.mark.unit
    def test_game_theory_concepts(self):
        """Test that key game theory concepts are implemented."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_theory_analysis", "packages/sygaldry_registry/components/agents/game_theory_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for game theory concepts
        import inspect

        source = inspect.getsource(module)
        assert 'nash' in source.lower() or 'equilibrium' in source.lower()
        assert 'payoff' in source.lower()
        assert 'strategy' in source.lower() or 'strategies' in source.lower()
        assert 'dominant' in source or 'dominated' in source

        # Verify analysis capabilities
        assert 'cooperative' in source or 'non-cooperative' in source or 'zero-sum' in source

    @pytest.mark.unit
    def test_analysis_depth_levels(self):
        """Test that analysis depth levels are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "game_theory_analysis", "packages/sygaldry_registry/components/agents/game_theory_analysis/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for depth level support
        import inspect

        source = inspect.getsource(module)
        assert 'comprehensive' in source or 'detailed' in source
        assert 'standard' in source or 'basic' in source
        assert 'quick' in source or 'summary' in source
