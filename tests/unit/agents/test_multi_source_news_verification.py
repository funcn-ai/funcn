"""Test suite for multi_source_news_verification following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestMultiSourceNewsVerificationAgent(BaseAgentTest):
    """Test cases for multi source news verification agent."""

    component_name = "multi_source_news_verification"
    component_path = Path("packages/funcn_registry/components/agents/multi_source_news_verification")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "multi_source_news_verification",
            "packages/funcn_registry/components/agents/multi_source_news_verification/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.multi_source_news_verification

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "article_content": "New AI breakthrough announced at major tech conference",
                "headline": "Revolutionary AI System Achieves Human-Level Performance",
                "sources": ["TechNews", "AI Journal"],
                "check_fact_checkers": True,
                "educational_mode": True,
            },
            {
                "article_content": "Local community raises funds for new library",
                "headline": "Community Comes Together for Education",
                "context": "Small town fundraising effort",
                "use_realtime_search": False,
            },
            {
                "article_content": "Breaking: Major policy change announced",
                "headline": "Government Announces New Policy",
                "topic_area": "Politics",
                "author_info": "Political Correspondent",
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "multi_source_news_verification",
            "packages/funcn_registry/components/agents/multi_source_news_verification/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Main functions found in the agent
        assert hasattr(module, 'multi_source_news_verification')
        assert callable(module.multi_source_news_verification)
        assert hasattr(module, 'multi_source_news_verification_stream')
        assert callable(module.multi_source_news_verification_stream)
        assert hasattr(module, 'assess_source_credibility')
        assert callable(module.assess_source_credibility)
        assert hasattr(module, 'analyze_news_content')
        assert callable(module.analyze_news_content)
        assert hasattr(module, 'fact_check_claims')
        assert callable(module.fact_check_claims)
        assert hasattr(module, 'create_media_literacy_report')
        assert callable(module.create_media_literacy_report)
        assert hasattr(module, 'synthesize_news_verification')
        assert callable(module.synthesize_news_verification)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "multi_source_news_verification",
            "packages/funcn_registry/components/agents/multi_source_news_verification/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test that the enums exist
        assert hasattr(module, 'CredibilityLevel')
        assert hasattr(module, 'VerificationStatus')
        assert hasattr(module, 'BiasDirection')
        assert hasattr(module, 'MisinformationType')
        assert hasattr(module, 'ClaimType')
        
        # Test enum values
        assert module.CredibilityLevel.HIGH == "high"
        assert module.VerificationStatus.VERIFIED == "verified"
        assert module.BiasDirection.CENTER == "center"
        
        # Test models exist  
        assert hasattr(module, 'SourceCredibilityAssessment')
        assert hasattr(module, 'ContentAnalysisReport')
        assert hasattr(module, 'ClaimVerificationResult')
        assert hasattr(module, 'MediaLiteracyEducation')
        assert hasattr(module, 'NewsVerificationResult')

    @pytest.mark.unit
    def test_verify_news_structure(self):
        """Test basic structure of multi_source_news_verification function."""
        # Import the function
        func = self.get_component_function()
        
        # Test that function exists and is callable
        import inspect
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        
        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'article_content' in params
        assert 'headline' in params
        assert 'sources' in params
        assert 'context' in params
        assert 'topic_area' in params
        assert 'author_info' in params
        assert 'check_fact_checkers' in params
        assert 'educational_mode' in params
        assert 'use_realtime_search' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "multi_source_news_verification",
            "packages/funcn_registry/components/agents/multi_source_news_verification/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        NewsVerificationResult = module.NewsVerificationResult
        
        # News verification should return a NewsVerificationResult
        assert isinstance(output, NewsVerificationResult)
        assert hasattr(output, "headline")
        assert hasattr(output, "verification_status")
        assert hasattr(output, "confidence_score")
        assert hasattr(output, "credibility_assessment")
        assert hasattr(output, "content_analysis")
        assert hasattr(output, "claim_verifications")
        assert hasattr(output, "overall_summary")

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect
        
        spec = importlib.util.spec_from_file_location(
            "multi_source_news_verification",
            "packages/funcn_registry/components/agents/multi_source_news_verification/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test assess_source_credibility - not async
        func = module.assess_source_credibility
        assert callable(func)
        assert not inspect.iscoroutinefunction(func)
        
        # Test analyze_news_content - not async
        func = module.analyze_news_content
        assert callable(func)
        assert not inspect.iscoroutinefunction(func)
        
        # Test fact_check_claims - not async
        func = module.fact_check_claims
        assert callable(func)
        assert not inspect.iscoroutinefunction(func)

    @pytest.mark.unit 
    def test_multi_tool_integration(self):
        """Test that the agent integrates multiple verification tools."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "multi_source_news_verification",
            "packages/funcn_registry/components/agents/multi_source_news_verification/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for tool classes
        assert hasattr(module, 'WebSearchTool')
        assert hasattr(module, 'ExaNewsVerificationTool')
        
        # Check for verification capabilities
        import inspect
        source = inspect.getsource(module)
        assert 'credibility' in source.lower()
        assert 'fact_check' in source or 'fact-check' in source

    @pytest.mark.unit
    def test_verification_enums(self):
        """Test that verification enums are properly defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "multi_source_news_verification",
            "packages/funcn_registry/components/agents/multi_source_news_verification/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check CredibilityLevel values
        credibility_values = [e.value for e in module.CredibilityLevel]
        assert "high" in credibility_values
        assert "low" in credibility_values
        
        # Check VerificationStatus values
        verification_values = [e.value for e in module.VerificationStatus]
        assert "verified" in verification_values
        assert "unverified" in verification_values
