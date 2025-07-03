"""Test suite for recruiting_assistant_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestRecruitingAssistantAgent(BaseAgentTest):
    """Test cases for recruiting assistant agent."""

    component_name = "recruiting_assistant_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/recruiting_assistant")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "recruiting_assistant_agent", "packages/sygaldry_registry/components/agents/recruiting_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.find_candidates

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "role": "Senior Python Developer",
                "company": "Tech Startup",
                "requirements": ["Python", "Django", "PostgreSQL", "5+ years experience"],
                "location": "Remote",
                "search_mode": "technical",
                "num_candidates": 10,
            },
            {
                "role": "VP of Sales",
                "company": "SaaS Company",
                "requirements": ["Enterprise sales", "Team leadership", "10+ years experience"],
                "location": "San Francisco",
                "search_mode": "executive",
                "num_candidates": 5,
            },
            {
                "role": "Marketing Manager",
                "company": "E-commerce Platform",
                "requirements": ["Digital marketing", "SEO/SEM", "Team management"],
                "location": "New York",
                "search_mode": "professional",
                "num_candidates": 8,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "recruiting_assistant_agent", "packages/sygaldry_registry/components/agents/recruiting_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions mentioned in component.json
        assert hasattr(module, 'find_candidates')
        assert callable(module.find_candidates)
        assert hasattr(module, 'find_technical_talent')
        assert callable(module.find_technical_talent)
        assert hasattr(module, 'find_sales_professionals')
        assert callable(module.find_sales_professionals)
        assert hasattr(module, 'find_executives')
        assert callable(module.find_executives)
        assert hasattr(module, 'screen_candidate_profile')
        assert callable(module.screen_candidate_profile)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "recruiting_assistant_agent", "packages/sygaldry_registry/components/agents/recruiting_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'CandidateProfile')
        assert hasattr(module, 'CandidateMatchScore')
        assert hasattr(module, 'RecruitingWebsetResponse')
        assert hasattr(module, 'CandidateSearchResponse')

        # Test basic model instantiation
        CandidateProfile = module.CandidateProfile
        profile = CandidateProfile(
            name="John Doe",
            current_title="Senior Software Engineer",
            company="Tech Corp",
            location="San Francisco",
            profile_url="http://linkedin.com/in/johndoe",
            summary="Experienced engineer",
            skills=["Python", "Django"],
            experience_years=7,
            match_reasons=["Strong Python skills"],
        )
        assert profile.name == "John Doe"
        assert profile.experience_years == 7
        assert len(profile.skills) == 2

        # Test CandidateMatchScore model
        CandidateMatchScore = module.CandidateMatchScore
        match = CandidateMatchScore(
            overall_score=0.85,
            skills_match=0.9,
            experience_match=0.8,
            location_match=1.0,
            strengths=["Technical skills"],
            gaps=["Industry experience"],
        )
        assert match.overall_score == 0.85
        assert match.skills_match == 0.9

        # Test CandidateSearchResponse model
        CandidateSearchResponse = module.CandidateSearchResponse
        response = CandidateSearchResponse(
            role="Senior Python Developer",
            company="Tech Startup",
            webset_id="test-webset-123",
            search_criteria="Python Django Remote",
            candidates_found=10,
            top_candidates=[profile],
            search_insights="Strong candidate pool available",
            hiring_recommendations=["Focus on remote candidates"],
        )
        assert response.candidates_found == 10
        assert len(response.top_candidates) == 1

    @pytest.mark.unit
    def test_find_candidates_structure(self):
        """Test basic structure of find_candidates function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'role' in params
        assert 'company' in params
        assert 'requirements' in params
        assert 'location' in params
        assert 'search_mode' in params
        assert 'num_candidates' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "recruiting_assistant_agent", "packages/sygaldry_registry/components/agents/recruiting_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        CandidateSearchResponse = module.CandidateSearchResponse

        # Recruiting assistant should return a CandidateSearchResponse
        assert isinstance(output, CandidateSearchResponse)
        assert hasattr(output, "role")
        assert hasattr(output, "company")
        assert hasattr(output, "webset_id")
        assert hasattr(output, "search_criteria")
        assert hasattr(output, "candidates_found")
        assert hasattr(output, "top_candidates")
        assert hasattr(output, "search_insights")
        assert hasattr(output, "hiring_recommendations")
        assert isinstance(output.top_candidates, list)
        assert output.candidates_found >= 0

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "recruiting_assistant_agent", "packages/sygaldry_registry/components/agents/recruiting_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test find_technical_talent
        func = module.find_technical_talent
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'role' in params
        assert 'technologies' in params

        # Test find_sales_professionals
        func = module.find_sales_professionals
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'role' in params
        assert 'industry' in params

        # Test find_executives
        func = module.find_executives
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'role' in params
        assert 'company_stage' in params

    @pytest.mark.unit
    def test_exa_websets_integration(self):
        """Test that the agent integrates with Exa websets."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "recruiting_assistant_agent", "packages/sygaldry_registry/components/agents/recruiting_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for Exa websets integration
        import inspect

        source = inspect.getsource(module)
        assert 'exa' in source.lower() or 'webset' in source.lower()
        assert 'create_webset' in source or 'get_webset' in source

        # Verify candidate search functionality
        assert 'candidate' in source and 'search' in source

    @pytest.mark.unit
    def test_search_modes(self):
        """Test that different search modes are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "recruiting_assistant_agent", "packages/sygaldry_registry/components/agents/recruiting_assistant/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for search mode support
        import inspect

        source = inspect.getsource(module)
        assert 'technical' in source or 'executive' in source or 'sales' in source
        assert 'mode' in source.lower() or 'search_mode' in source
