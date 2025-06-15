"""Test suite for web_search_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestWebSearchAgent(BaseAgentTest):
    """Test cases for web search agent."""

    component_name = "web_search_agent"
    component_path = Path("packages/funcn_registry/components/agents/web_search")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "web_search_agent", "packages/funcn_registry/components/agents/web_search/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.web_search_agent

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "question": "What is Mirascope and how does it work?",
                "search_provider": "auto",
                "num_results": 5,
            },
            {
                "question": "Latest AI safety research papers",
                "search_provider": "exa",
                "num_results": 10,
            },
            {
                "question": "Python web frameworks comparison",
                "search_provider": "duckduckgo",
                "num_results": 8,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "web_search_agent", "packages/funcn_registry/components/agents/web_search/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions mentioned in component.json
        assert hasattr(module, 'web_search_agent')
        assert callable(module.web_search_agent)
        assert hasattr(module, 'web_search_private')
        assert callable(module.web_search_private)
        assert hasattr(module, 'web_search_comprehensive')
        assert callable(module.web_search_comprehensive)
        assert hasattr(module, 'web_search_ai')
        assert callable(module.web_search_ai)
        assert hasattr(module, 'web_search_structured')
        assert callable(module.web_search_structured)
        # Check for other functions that exist in this version
        assert hasattr(module, 'determine_search_strategy')
        assert hasattr(module, 'determine_exa_category')

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "web_search_agent", "packages/funcn_registry/components/agents/web_search/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'WebSearchResponse')
        assert hasattr(module, 'SearchProvider')

        # Test basic model instantiation
        WebSearchResponse = module.WebSearchResponse
        response = WebSearchResponse(
            answer="Test answer",
            sources=["http://example.com"],
            search_queries=["query 1"],
            search_providers=["duckduckgo"],
            privacy_note="No tracking",
        )
        assert response.answer == "Test answer"
        assert len(response.sources) == 1
        assert len(response.search_providers) == 1

        # Test SearchProvider is defined as a Literal type
        assert 'SearchProvider' in dir(module)

    @pytest.mark.unit
    def test_web_search_agent_structure(self):
        """Test basic structure of web_search_agent function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        # Note: web_search_agent is not async, it returns a BaseDynamicConfig

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'question' in params
        assert 'search_provider' in params
        assert 'max_results_per_search' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "web_search_agent", "packages/funcn_registry/components/agents/web_search/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Web search agent returns a BaseDynamicConfig, not WebSearchResponse directly
        # Check that output is a dict with the expected structure
        assert isinstance(output, dict)
        assert 'tools' in output
        assert 'call_params' in output
        assert 'computed_fields' in output
        assert 'metadata' in output

        # Check computed fields
        computed = output.get('computed_fields', {})
        assert 'question' in computed
        assert 'search_strategy' in computed
        assert 'current_date' in computed

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "web_search_agent", "packages/funcn_registry/components/agents/web_search/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test web_search_private
        func = module.web_search_private
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'question' in params

        # Test web_search_ai
        func = module.web_search_ai
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'question' in params

        # Test web_search_comprehensive
        func = module.web_search_comprehensive
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'question' in params

    @pytest.mark.unit
    def test_multi_provider_support(self):
        """Test that the agent supports multiple search providers."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "web_search_agent", "packages/funcn_registry/components/agents/web_search/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check that multiple providers are mentioned
        import inspect

        source = inspect.getsource(module)
        assert 'duckduckgo' in source.lower()
        assert 'qwant' in source.lower()
        assert 'exa' in source.lower()
        assert 'nimble' in source.lower()

        # Check for provider selection logic
        assert 'auto' in source or 'provider' in source

    @pytest.mark.unit
    def test_search_tools_integration(self):
        """Test that the agent integrates with search tools."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "web_search_agent", "packages/funcn_registry/components/agents/web_search/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for search tool imports
        import inspect

        source = inspect.getsource(module)
        assert 'duckduckgo_search' in source or 'search_tools' in source
        assert 'qwant' in source or 'exa' in source or 'nimble' in source
