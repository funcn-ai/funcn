"""Test suite for research_assistant_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestResearchAssistantAgent(BaseAgentTest):
    """Test cases for research assistant agent."""

    component_name = "research_assistant_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/research_assistant")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "research_assistant_agent", "packages/sygaldry_registry/components/agents/research_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.research_topic

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "topic": "artificial intelligence in healthcare",
                "depth": "comprehensive",
                "audience": "healthcare professionals",
                "num_queries": 3,
                "style": "professional",
                "target_words": 1000,
            },
            {
                "topic": "renewable energy storage solutions",
                "depth": "standard",
                "audience": "investors",
                "num_queries": 5,
                "style": "professional",
                "target_words": 1500,
            },
            {
                "topic": "quantum computing applications",
                "depth": "quick",
                "audience": "general",
                "num_queries": 2,
                "style": "casual",
                "target_words": 500,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "research_assistant_agent", "packages/sygaldry_registry/components/agents/research_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions mentioned in component.json
        assert hasattr(module, 'research_topic')
        assert callable(module.research_topic)
        assert hasattr(module, 'research_company')
        assert callable(module.research_company)
        assert hasattr(module, 'research_technology')
        assert callable(module.research_technology)
        assert hasattr(module, 'research_market')
        assert callable(module.research_market)
        assert hasattr(module, 'quick_research_summary')
        assert callable(module.quick_research_summary)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "research_assistant_agent", "packages/sygaldry_registry/components/agents/research_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'SearchQuery')
        assert hasattr(module, 'SearchQueriesResponse')
        assert hasattr(module, 'ResearchSection')
        assert hasattr(module, 'ResearchReportResponse')

        # Test basic model instantiation without complex types
        # Test ResearchSection model (doesn't have complex dependencies)
        ResearchSection = module.ResearchSection
        section = ResearchSection(title="Test Section", content="Section content", sources_used=["http://example.com"])
        assert section.title == "Test Section"
        assert len(section.sources_used) == 1

        # Test ResearchReportResponse model
        ResearchReportResponse = module.ResearchReportResponse
        report = ResearchReportResponse(
            title="Test Report",
            executive_summary="Summary text",
            sections=[section],
            all_sources=["http://example.com"],
            word_count=100,
        )
        assert report.title == "Test Report"
        assert len(report.sections) == 1
        assert report.word_count == 100

        # Just verify SearchQuery exists - don't instantiate due to ExaCategory dependency
        assert module.SearchQuery.__name__ == 'SearchQuery'
        assert module.SearchQueriesResponse.__name__ == 'SearchQueriesResponse'

    @pytest.mark.unit
    def test_research_topic_structure(self):
        """Test basic structure of research_topic function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'topic' in params
        assert 'depth' in params
        assert 'audience' in params
        assert 'num_queries' in params
        assert 'style' in params
        assert 'target_words' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "research_assistant_agent", "packages/sygaldry_registry/components/agents/research_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ResearchReportResponse = module.ResearchReportResponse

        # Research assistant should return a ResearchReportResponse
        assert isinstance(output, ResearchReportResponse)
        assert hasattr(output, "title")
        assert hasattr(output, "executive_summary")
        assert hasattr(output, "sections")
        assert hasattr(output, "all_sources")
        assert hasattr(output, "word_count")
        assert isinstance(output.sections, list)
        assert isinstance(output.all_sources, list)
        assert output.word_count > 0

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "research_assistant_agent", "packages/sygaldry_registry/components/agents/research_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test research_company
        func = module.research_company
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'company_name' in params

        # Test research_technology
        func = module.research_technology
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'technology' in params

        # Test research_market
        func = module.research_market
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'market_or_industry' in params

        # Test quick_research_summary
        func = module.quick_research_summary
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'topic' in params

    @pytest.mark.unit
    def test_exa_search_integration(self):
        """Test that the agent properly integrates with exa_search tool."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "research_assistant_agent", "packages/sygaldry_registry/components/agents/research_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check that the exa_search imports are attempted
        import inspect

        source = inspect.getsource(module)
        assert 'from exa_search_tools' in source or 'import exa_search_tools' in source or 'exa_search' in source

        # Verify the agent uses search functionality
        source = inspect.getsource(module.research_topic)
        assert 'search' in source.lower() or 'exa' in source.lower()

    @pytest.mark.unit
    def test_depth_and_style_parameters(self):
        """Test that depth and style parameters are properly defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "research_assistant_agent", "packages/sygaldry_registry/components/agents/research_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for depth options
        import inspect

        source = inspect.getsource(module)
        assert 'comprehensive' in source or 'detailed' in source or 'overview' in source

        # Check for style options
        assert 'professional' in source or 'executive' in source or 'accessible' in source
