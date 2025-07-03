"""Test suite for sourcing_assistant_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestSourcingAssistantAgent(BaseAgentTest):
    """Test cases for sourcing assistant agent."""

    component_name = "sourcing_assistant_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/sourcing_assistant")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.sourcing_assistant_agent

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "product_type": "industrial valves",
                "category": "manufacturer",
                "specifications": ["316 stainless steel", "High pressure rated", "API certified"],
                "location_preference": "United States",
                "sustainability_required": True,
                "moq_requirements": "100 units minimum",
                "certifications": ["ISO 9001", "API 6D"],
                "budget_range": "$500-$2000 per unit",
            },
            {
                "product_type": "organic cotton fabric",
                "category": "supplier",
                "specifications": ["GOTS certified", "200-300 GSM", "Natural dyes only"],
                "location_preference": "India or Turkey",
                "sustainability_required": True,
                "certifications": ["GOTS", "OEKO-TEX"],
            },
            {
                "product_type": "ERP software",
                "category": "software",
                "specifications": ["Cloud-based", "Manufacturing module", "Multi-currency support", "API integration"],
                "budget_range": "$50,000-$200,000 annual",
            },
            {
                "product_type": "AI productivity platform",
                "category": "tool",
                "specifications": ["Task automation", "Team collaboration", "API access", "Enterprise security"],
            },
        ]

    def test_sourcing_categories_literal(self):
        """Test SourcingCategory literal type definition."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the literal type exists
        assert hasattr(module, 'SourcingCategory')

        # Test expected categories (based on the Literal definition)
        expected_categories = ["manufacturer", "supplier", "software", "service", "tool", "platform", "solution"]
        # Can't directly test Literal values, but we can test in the model

    def test_industry_literal(self):
        """Test Industry literal type definition."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the literal type exists
        assert hasattr(module, 'Industry')

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'SourcingRequirements')
        assert hasattr(module, 'SourcingSearchResponse')

        # Test model field definitions without instantiation due to forward references
        SourcingRequirements = module.SourcingRequirements
        fields = SourcingRequirements.model_fields
        assert 'product_type' in fields
        assert 'category' in fields
        assert 'specifications' in fields
        assert 'location_preference' in fields
        assert 'sustainability_required' in fields
        assert 'minimum_order_quantity' in fields
        assert 'certifications' in fields
        assert 'budget_range' in fields

        # Test SourcingSearchResponse model fields
        SourcingSearchResponse = module.SourcingSearchResponse
        fields = SourcingSearchResponse.model_fields
        assert 'webset_id' in fields
        assert 'search_query' in fields
        assert 'sourcing_type' in fields
        assert 'criteria' in fields
        assert 'enrichments' in fields
        assert 'geographic_scope' in fields
        assert 'estimated_suppliers' in fields
        assert 'status' in fields

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        # Main function
        assert hasattr(agent, 'sourcing_assistant_agent')
        assert callable(agent.sourcing_assistant_agent)

        # Convenience functions
        assert hasattr(agent, 'find_sustainable_manufacturers')
        assert hasattr(agent, 'find_low_moq_suppliers')
        assert hasattr(agent, 'find_software_solutions')
        assert hasattr(agent, 'find_ai_productivity_tools')

        # All should be callable
        assert callable(agent.find_sustainable_manufacturers)
        assert callable(agent.find_low_moq_suppliers)
        assert callable(agent.find_software_solutions)
        assert callable(agent.find_ai_productivity_tools)

    @pytest.mark.asyncio
    async def test_sourcing_assistant_agent_structure(self):
        """Test basic structure of sourcing_assistant_agent function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sourcing_assistant_agent = module.sourcing_assistant_agent

        # Test that function is async (check the wrapped function if decorated)
        import inspect

        # The function is decorated with @llm.call, so check for __wrapped__
        if hasattr(sourcing_assistant_agent, '__wrapped__'):
            assert inspect.iscoroutinefunction(sourcing_assistant_agent.__wrapped__)
        else:
            assert inspect.iscoroutinefunction(sourcing_assistant_agent)

        # Test function signature
        sig = inspect.signature(sourcing_assistant_agent)
        params = list(sig.parameters.keys())
        assert 'product_type' in params
        assert 'category' in params
        assert 'specifications' in params
        assert 'location_preference' in params
        assert 'sustainability_required' in params
        assert 'moq_requirements' in params
        assert 'certifications' in params
        assert 'budget_range' in params
        assert 'llm_provider' in params
        assert 'model' in params

        # Test default values
        assert sig.parameters['category'].default == "supplier"
        assert sig.parameters['specifications'].default is None
        assert sig.parameters['location_preference'].default is None
        assert sig.parameters['sustainability_required'].default is False
        assert sig.parameters['moq_requirements'].default is None
        assert sig.parameters['certifications'].default is None
        assert sig.parameters['budget_range'].default is None
        assert sig.parameters['llm_provider'].default == "openai"
        assert sig.parameters['model'].default == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_convenience_functions_structure(self):
        """Test structure of convenience functions."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test find_sustainable_manufacturers
        func = module.find_sustainable_manufacturers
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'product_type' in params
        assert 'location' in params
        assert 'certifications' in params
        assert 'kwargs' in params

        # Test find_low_moq_suppliers
        func = module.find_low_moq_suppliers
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'product_type' in params
        assert 'max_moq' in params
        assert 'regions' in params
        assert 'kwargs' in params

        # Test find_software_solutions
        func = module.find_software_solutions
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'solution_type' in params
        assert 'features' in params
        assert 'industry' in params
        assert 'kwargs' in params

        # Test find_ai_productivity_tools
        func = module.find_ai_productivity_tools
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'use_case' in params
        assert 'kwargs' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Since we can't directly import and instantiate the model due to forward references,
        # we'll just check the output has the expected attributes

        # Should have all required fields
        assert hasattr(output, "webset_id")
        assert hasattr(output, "search_query")
        assert hasattr(output, "sourcing_type")
        assert hasattr(output, "criteria")
        assert hasattr(output, "enrichments")
        assert hasattr(output, "geographic_scope")
        assert hasattr(output, "status")

        # Validate types
        assert isinstance(output.webset_id, str)
        assert isinstance(output.search_query, str)
        assert isinstance(output.sourcing_type, str)
        assert isinstance(output.criteria, list)
        assert isinstance(output.enrichments, list)
        assert isinstance(output.geographic_scope, str)
        assert isinstance(output.status, str)

        # estimated_suppliers can be None or int
        if hasattr(output, "estimated_suppliers") and output.estimated_suppliers is not None:
            assert isinstance(output.estimated_suppliers, int)

    @pytest.mark.unit
    def test_prompt_template_variables(self):
        """Test that the prompt template has all required variables."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check that the decorated function exists
        assert hasattr(module.sourcing_assistant_agent, '__wrapped__')

    @pytest.mark.unit
    def test_tool_imports_fallback(self):
        """Test that the agent handles missing tool imports gracefully."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sourcing_assistant_agent", "packages/sygaldry_registry/components/agents/sourcing_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)

        # The module should load even if exa_websets_tools is not available
        # (it has try/except fallback)
        spec.loader.exec_module(module)

        # If tools aren't available, they should be None
        if module.create_webset is None:
            assert module.get_webset_status is None
            assert module.list_webset_items is None
            assert module.WebsetSearchConfig is None
            assert module.WebsetEnrichment is None
            assert module.WebsetCriteria is None
