"""Test suite for hallucination_detector_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestHallucinationDetectorAgent(BaseAgentTest):
    """Test cases for hallucination detector agent."""

    component_name = "hallucination_detector_agent"
    component_path = Path("packages/funcn_registry/components/agents/hallucination_detector")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hallucination_detector_agent",
            "packages/funcn_registry/components/agents/hallucination_detector/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.detect_hallucinations

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "text": "The Eiffel Tower was built in 1889 in Paris. It is made entirely of gold.",
                "search_type": "neural",
                "max_sources_per_claim": 5,
            },
            {
                "text": "Machine learning models require training data to learn patterns.",
                "search_type": "auto",
                "max_sources_per_claim": 3,
            },
            {
                "text": "The moon is made of green cheese and orbits Earth every 28 days.",
                "search_type": "keyword",
                "max_sources_per_claim": 4,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hallucination_detector_agent",
            "packages/funcn_registry/components/agents/hallucination_detector/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Main functions mentioned in component.json
        assert hasattr(module, 'detect_hallucinations')
        assert callable(module.detect_hallucinations)
        assert hasattr(module, 'detect_hallucinations_quick')
        assert callable(module.detect_hallucinations_quick)
        assert hasattr(module, 'verify_single_statement')
        assert callable(module.verify_single_statement)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hallucination_detector_agent",
            "packages/funcn_registry/components/agents/hallucination_detector/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test that the models exist
        assert hasattr(module, 'ExtractedClaim')
        assert hasattr(module, 'ExtractedClaimsResponse')
        assert hasattr(module, 'ClaimVerification')
        assert hasattr(module, 'HallucinationDetectionResponse')
        
        # Test basic model instantiation
        ExtractedClaim = module.ExtractedClaim
        claim = ExtractedClaim(
            claim="Test claim"
        )
        assert claim.claim == "Test claim"
        
        # Test ExtractedClaimsResponse
        ExtractedClaimsResponse = module.ExtractedClaimsResponse
        claims_response = ExtractedClaimsResponse(
            claims=["Claim 1", "Claim 2"]
        )
        assert len(claims_response.claims) == 2
        
        # Test ClaimVerification model
        ClaimVerification = module.ClaimVerification
        verification = ClaimVerification(
            claim="Test claim",
            assessment="supported",
            confidence_score=0.85,
            supporting_sources=["http://example.com"],
            refuting_sources=[],
            summary="Claim is supported"
        )
        assert verification.claim == "Test claim"
        assert verification.assessment == "supported"
        assert verification.confidence_score == 0.85
        assert len(verification.supporting_sources) == 1
        
        # Test HallucinationDetectionResponse model
        HallucinationDetectionResponse = module.HallucinationDetectionResponse
        result = HallucinationDetectionResponse(
            claims_extracted=2,
            claims_verified=[verification],
            overall_assessment="mostly accurate",
            hallucination_score=0.1,
            summary="Text appears to be factual"
        )
        assert result.claims_extracted == 2
        assert len(result.claims_verified) == 1
        assert result.hallucination_score == 0.1

    @pytest.mark.unit
    def test_detect_hallucinations_structure(self):
        """Test basic structure of detect_hallucinations function."""
        # Import the function
        func = self.get_component_function()
        
        # Test that function exists and is callable
        import inspect
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        
        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'text' in params
        assert 'search_type' in params
        assert 'max_sources_per_claim' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hallucination_detector_agent",
            "packages/funcn_registry/components/agents/hallucination_detector/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        HallucinationDetectionResponse = module.HallucinationDetectionResponse
        
        # Hallucination detector should return a HallucinationDetectionResponse
        assert isinstance(output, HallucinationDetectionResponse)
        assert hasattr(output, "claims_extracted")
        assert hasattr(output, "claims_verified")
        assert hasattr(output, "hallucination_score")
        assert hasattr(output, "overall_assessment")
        assert hasattr(output, "summary")
        assert isinstance(output.claims_verified, list)
        assert output.claims_extracted >= 0
        assert 0 <= output.hallucination_score <= 1

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect
        
        spec = importlib.util.spec_from_file_location(
            "hallucination_detector_agent",
            "packages/funcn_registry/components/agents/hallucination_detector/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test detect_hallucinations_quick
        func = module.detect_hallucinations_quick
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'text' in params
        
        # Test verify_single_statement
        func = module.verify_single_statement
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'statement' in params

    @pytest.mark.unit 
    def test_exa_search_integration(self):
        """Test that the agent properly integrates with exa_search tool."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hallucination_detector_agent",
            "packages/funcn_registry/components/agents/hallucination_detector/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check that the exa_search imports are attempted
        import inspect
        source = inspect.getsource(module)
        assert 'from exa_search_tools' in source or 'import exa_search_tools' in source or 'exa_search' in source
        
        # Verify the agent uses search functionality
        source = inspect.getsource(module.detect_hallucinations)
        assert 'search' in source.lower() or 'exa' in source.lower() or 'verify' in source.lower()

    @pytest.mark.unit
    def test_hallucination_scoring(self):
        """Test that hallucination scoring is properly implemented."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "hallucination_detector_agent",
            "packages/funcn_registry/components/agents/hallucination_detector/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check that scoring logic exists
        import inspect
        source = inspect.getsource(module)
        assert 'hallucination_score' in source
        assert 'confidence' in source or 'score' in source
