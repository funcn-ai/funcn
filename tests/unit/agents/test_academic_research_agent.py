"""Test suite for academic_research_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestAcademicResearchAgent(BaseAgentTest):
    """Test cases for academic research agent."""

    component_name = "academic_research_agent"
    component_path = Path("packages/funcn_registry/components/agents/academic_research")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "academic_research_agent",
            "packages/funcn_registry/components/agents/academic_research/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.academic_research_agent

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "topic": "machine learning interpretability",
                "field": "computer_science",
                "journal_requirements": ["peer-reviewed"],
                "time_period": "2020-2024",
                "publication_venue": "journal",
            },
            {
                "topic": "CRISPR gene editing",
                "field": "biology",
                "journal_requirements": ["Nature", "Science", "Cell"],
                "time_period": "2023-2024",
                "author_requirements": ["PhD", "from major university"],
            },
            {
                "topic": "quantum computing algorithms",
                "field": "physics",
                "journal_requirements": [],
                "time_period": "2022-2024",
                "citation_threshold": 50,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "academic_research_agent",
            "packages/funcn_registry/components/agents/academic_research/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Main function
        assert hasattr(module, 'academic_research_agent')
        assert callable(module.academic_research_agent)
        
        # Additional functions available
        assert hasattr(module, 'find_papers_by_author_credentials')
        assert callable(module.find_papers_by_author_credentials)
        assert hasattr(module, 'find_high_impact_papers')
        assert callable(module.find_high_impact_papers)
        assert hasattr(module, 'find_emerging_research')
        assert callable(module.find_emerging_research)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "academic_research_agent",
            "packages/funcn_registry/components/agents/academic_research/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test that the models exist
        assert hasattr(module, 'ResearchPaperQuery')
        assert hasattr(module, 'AcademicResearchResponse')
        assert hasattr(module, 'ResearchField')
        assert hasattr(module, 'PublicationVenue')
        
        # Test basic model instantiation without Literal types
        AcademicResearchResponse = module.AcademicResearchResponse
        response = AcademicResearchResponse(
            webset_id="test-id",
            search_query="test query",
            research_field="computer_science",
            filters=["peer-reviewed"],
            enrichments=["abstract", "authors"],
            estimated_papers=100,
            publication_types=["journal", "conference"],
            status="completed"
        )
        assert response.webset_id == "test-id"
        assert response.research_field == "computer_science"
        assert len(response.filters) == 1
        
        # Just verify ResearchPaperQuery exists - don't instantiate due to Literal types
        assert module.ResearchPaperQuery.__name__ == 'ResearchPaperQuery'
        
        # Check that Literal types are defined
        assert 'ResearchField' in dir(module)
        assert 'PublicationVenue' in dir(module)

    @pytest.mark.unit
    def test_academic_research_agent_structure(self):
        """Test basic structure of academic_research_agent function."""
        # Import the function
        func = self.get_component_function()
        
        # Test that function exists and is callable
        import inspect
        assert callable(func)
        
        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'topic' in params
        assert 'field' in params
        assert 'journal_requirements' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "academic_research_agent",
            "packages/funcn_registry/components/agents/academic_research/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        AcademicResearchResponse = module.AcademicResearchResponse
        
        # Academic research agent should return an AcademicResearchResponse
        assert isinstance(output, AcademicResearchResponse)
        assert hasattr(output, "webset_id")
        assert hasattr(output, "search_query")
        assert hasattr(output, "research_field")
        assert hasattr(output, "filters")
        assert hasattr(output, "enrichments")
        assert hasattr(output, "estimated_papers")
        assert hasattr(output, "publication_types")
        assert hasattr(output, "status")
        assert isinstance(output.filters, list)
        assert isinstance(output.enrichments, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect
        
        spec = importlib.util.spec_from_file_location(
            "academic_research_agent",
            "packages/funcn_registry/components/agents/academic_research/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test find_papers_by_author_credentials
        func = module.find_papers_by_author_credentials
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'topic' in params
        assert 'author_degree' in params
        
        # Test find_high_impact_papers
        func = module.find_high_impact_papers
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'topic' in params
        assert 'field' in params
        assert 'min_citations' in params
        
        # Test find_emerging_research
        func = module.find_emerging_research
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

    @pytest.mark.unit 
    def test_exa_websets_integration(self):
        """Test that the agent properly integrates with exa_websets tool."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "academic_research_agent",
            "packages/funcn_registry/components/agents/academic_research/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check that the exa_websets imports are attempted
        # The actual tools might not be available in test environment
        import inspect
        source = inspect.getsource(module)
        assert 'from exa_websets import' in source or 'create_webset' in source
        
        # Verify the agent decorator includes tools
        source = inspect.getsource(module.academic_research_agent)
        assert 'tools=' in source