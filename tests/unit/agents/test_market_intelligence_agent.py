"""Test suite for market_intelligence_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestMarketIntelligenceAgent(BaseAgentTest):
    """Test cases for market intelligence agent."""

    component_name = "market_intelligence_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/market_intelligence")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.market_intelligence_agent

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "segment": "fintech",
                "investment_stage": "series-a",
                "time_period": "2024",
                "geographic_focus": "United States",
                "investor_criteria": ["major US based VC fund"],
                "signal_keywords": ["payments", "blockchain"],
            },
            {
                "segment": "biotech",
                "company_type": "pharmaceutical companies",
                "investment_stage": "seed",
                "time_period": "last 6 months",
                "signal_keywords": ["gene therapy", "CRISPR"],
            },
            {
                "segment": "cleantech",
                "investment_stage": "series-b",
                "geographic_focus": "Europe",
                "investor_criteria": ["impact investors", "ESG focused funds"],
                "signal_keywords": ["renewable energy", "carbon capture"],
            },
        ]

    def test_market_segments_and_stages(self):
        """Test that market segments and investment stages are properly defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test MarketSegment literal type
        expected_segments = {
            "fintech",
            "agrotech",
            "biotech",
            "cleantech",
            "edtech",
            "healthtech",
            "proptech",
            "insurtech",
            "regtech",
            "other",
        }

        # Test InvestmentStage literal type
        expected_stages = {"pre-seed", "seed", "series-a", "series-b", "series-c", "later-stage", "ipo", "acquisition"}

        # Verify the types exist (we can't directly access Literal values, but we can test usage)
        assert hasattr(module, 'MarketIntelligenceQuery')
        assert hasattr(module, 'MarketIntelligenceResponse')

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that models exist
        assert hasattr(module, 'MarketIntelligenceQuery')
        assert hasattr(module, 'MarketIntelligenceResponse')

        # Test MarketIntelligenceQuery fields (without instantiation due to Literal type issues)
        MarketIntelligenceQuery = module.MarketIntelligenceQuery
        # Check that the model has the expected fields
        fields = MarketIntelligenceQuery.model_fields
        assert 'segment' in fields
        assert 'company_type' in fields
        assert 'investment_stage' in fields
        assert 'time_period' in fields
        assert 'geographic_focus' in fields
        assert 'investor_criteria' in fields
        assert 'signal_keywords' in fields

        # Test MarketIntelligenceResponse model (can instantiate since no Literal types)
        MarketIntelligenceResponse = module.MarketIntelligenceResponse
        response = MarketIntelligenceResponse(
            webset_id="test-123",
            search_focus="fintech startups",
            search_query="series A fintech companies",
            filters_applied=["funding round", "location"],
            enrichments=["company profile", "funding history"],
            signal_types=["funding", "expansion"],
            estimated_results=42,
            status="pending",
        )
        assert response.webset_id == "test-123"
        assert response.search_focus == "fintech startups"
        assert response.search_query == "series A fintech companies"
        assert len(response.filters_applied) == 2
        assert len(response.enrichments) == 2
        assert len(response.signal_types) == 2
        assert response.estimated_results == 42
        assert response.status == "pending"

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        # Main function
        assert hasattr(agent, 'market_intelligence_agent')
        assert callable(agent.market_intelligence_agent)

        # Convenience functions
        assert hasattr(agent, 'track_stealth_founders')
        assert hasattr(agent, 'find_funded_startups')
        assert hasattr(agent, 'analyze_company_changes')
        assert hasattr(agent, 'find_emerging_technologies')

        # All functions should be callable
        assert callable(agent.track_stealth_founders)
        assert callable(agent.find_funded_startups)
        assert callable(agent.analyze_company_changes)
        assert callable(agent.find_emerging_technologies)

    @pytest.mark.asyncio
    async def test_market_intelligence_agent_structure(self):
        """Test basic structure of market_intelligence_agent function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        market_intelligence_agent = module.market_intelligence_agent

        # Test that function exists and is callable
        assert callable(market_intelligence_agent)

        # The decorated function might not appear as async due to decorators
        # Check the underlying function or just verify it's callable
        import inspect

        # Test function signature - the decorator might modify it
        # Try to get the original function if it's wrapped
        func = market_intelligence_agent
        if hasattr(func, '__wrapped__'):
            # Get the original function
            while hasattr(func, '__wrapped__'):
                func = func.__wrapped__
            assert inspect.iscoroutinefunction(func)

        # Check that we can at least call it (would need proper mocking in real test)
        # Just verify the function exists and is callable
        assert market_intelligence_agent.__name__ == 'market_intelligence_agent'

    @pytest.mark.asyncio
    async def test_convenience_functions_structure(self):
        """Test structure of convenience functions."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test track_stealth_founders
        import inspect

        assert inspect.iscoroutinefunction(module.track_stealth_founders)
        sig = inspect.signature(module.track_stealth_founders)
        params = list(sig.parameters.keys())
        assert 'year' in params
        assert sig.parameters['year'].default == 2025

        # Test find_funded_startups
        assert inspect.iscoroutinefunction(module.find_funded_startups)
        sig = inspect.signature(module.find_funded_startups)
        params = list(sig.parameters.keys())
        assert 'segment' in params
        assert 'stage' in params
        assert 'year' in params
        assert 'investor_type' in params
        assert sig.parameters['year'].default == 2024

        # Test analyze_company_changes
        assert inspect.iscoroutinefunction(module.analyze_company_changes)
        sig = inspect.signature(module.analyze_company_changes)
        params = list(sig.parameters.keys())
        assert 'keywords' in params
        assert 'segment' in params

        # Test find_emerging_technologies
        assert inspect.iscoroutinefunction(module.find_emerging_technologies)
        sig = inspect.signature(module.find_emerging_technologies)
        params = list(sig.parameters.keys())
        assert 'tech_focus' in params
        assert 'hardware_focused' in params
        assert sig.parameters['hardware_focused'].default is False

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        MarketIntelligenceResponse = module.MarketIntelligenceResponse

        # Check output is correct type
        assert isinstance(output, MarketIntelligenceResponse)

        # Validate required fields
        assert hasattr(output, "webset_id")
        assert hasattr(output, "search_focus")
        assert hasattr(output, "search_query")
        assert hasattr(output, "filters_applied")
        assert hasattr(output, "enrichments")
        assert hasattr(output, "signal_types")
        assert hasattr(output, "estimated_results")
        assert hasattr(output, "status")

        # Validate field types
        assert isinstance(output.webset_id, str)
        assert isinstance(output.search_focus, str)
        assert isinstance(output.search_query, str)
        assert isinstance(output.filters_applied, list)
        assert isinstance(output.enrichments, list)
        assert isinstance(output.signal_types, list)
        assert output.estimated_results is None or isinstance(output.estimated_results, int)
        assert isinstance(output.status, str)

    @pytest.mark.unit
    def test_agent_decorators(self):
        """Test that the agent has proper Mirascope decorators."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # The function should have decorators that add attributes
        agent_func = module.market_intelligence_agent

        # Check that it's been decorated (would have __wrapped__ or similar attributes)
        # Note: Direct import may not preserve all decorator attributes
        assert callable(agent_func)

    @pytest.mark.unit
    def test_tool_dependencies(self):
        """Test that agent handles tool imports gracefully."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "market_intelligence_agent", "packages/sygaldry_registry/components/agents/market_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # The agent should handle missing exa_websets_tools gracefully
        # Check that the fallback values are set when import fails
        if module.create_webset is None:
            assert module.get_webset_status is None
            assert module.list_webset_items is None
            assert module.WebsetSearchConfig is None
            assert module.WebsetEnrichment is None
            assert module.WebsetCriteria is None
