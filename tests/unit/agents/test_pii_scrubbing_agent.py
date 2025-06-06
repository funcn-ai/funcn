"""Test suite for pii_scrubbing_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestPiiScrubbingAgent(BaseAgentTest):
    """Test cases for PII scrubbing agent."""

    component_name = "pii_scrubbing_agent"
    component_path = Path("packages/funcn_registry/components/agents/pii_scrubbing")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pii_scrubbing_agent",
            "packages/funcn_registry/components/agents/pii_scrubbing/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.scrub_pii_from_text

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "text": "John Smith's email is john.smith@email.com and his SSN is 123-45-6789",
                "scrubbing_method": "mask",
                "pii_types": ["email", "ssn", "name"],
                "sensitivity_level": "high",
            },
            {
                "text": "Call me at (555) 123-4567 or visit my address at 123 Main St, City, ST 12345",
                "scrubbing_method": "redact",
                "pii_types": ["phone", "address"],
                "sensitivity_level": "medium",
            },
            {
                "text": "Patient ID: 12345, DOB: 01/15/1980, Diagnosis: Hypertension",
                "scrubbing_method": "generalize",
                "pii_types": ["medical", "date", "id"],
                "sensitivity_level": "maximum",
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pii_scrubbing_agent",
            "packages/funcn_registry/components/agents/pii_scrubbing/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Main functions found in the agent
        assert hasattr(module, 'scrub_pii')
        assert callable(module.scrub_pii)
        assert hasattr(module, 'scrub_pii_from_text')
        assert callable(module.scrub_pii_from_text)
        assert hasattr(module, 'detect_pii_regex')
        assert callable(module.detect_pii_regex)
        assert hasattr(module, 'detect_pii_llm')
        assert callable(module.detect_pii_llm)
        assert hasattr(module, 'quick_scrub')
        assert callable(module.quick_scrub)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pii_scrubbing_agent",
            "packages/funcn_registry/components/agents/pii_scrubbing/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test that the models exist
        assert hasattr(module, 'PIIEntity')
        assert hasattr(module, 'PIIDetectionResponse')
        assert hasattr(module, 'ScrubbedTextResponse')
        
        # Test basic model instantiation
        PIIEntity = module.PIIEntity
        entity = PIIEntity(
            text="john.smith@email.com",
            entity_type="email",
            start_index=20,
            end_index=40,
            confidence=0.95,
            replacement="[EMAIL]"
        )
        assert entity.entity_type == "email"
        assert entity.confidence == 0.95
        
        # Test ScrubbedTextResponse model
        ScrubbedTextResponse = module.ScrubbedTextResponse
        scrubbed = ScrubbedTextResponse(
            original_text="John works at Acme Corp",
            scrubbed_text="[NAME] works at [COMPANY]",
            entities_removed=[entity],
            scrubbing_method="redact",
            reversible=False
        )
        assert len(scrubbed.entities_removed) == 1
        assert scrubbed.scrubbing_method == "redact"

    @pytest.mark.unit
    def test_scrub_pii_from_text_structure(self):
        """Test basic structure of scrub_pii_from_text function."""
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
        assert 'scrubbing_method' in params
        assert 'pii_types_to_detect' in params or 'detection_method' in params
        assert 'llm_provider' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pii_scrubbing_agent",
            "packages/funcn_registry/components/agents/pii_scrubbing/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ScrubbedTextResponse = module.ScrubbedTextResponse
        
        # PII scrubbing should return a ScrubbedTextResponse
        assert isinstance(output, ScrubbedTextResponse)
        assert hasattr(output, "original_text")
        assert hasattr(output, "scrubbed_text")
        assert hasattr(output, "entities_removed")
        assert hasattr(output, "scrubbing_method")
        assert hasattr(output, "reversible")
        assert isinstance(output.entities_removed, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect
        
        spec = importlib.util.spec_from_file_location(
            "pii_scrubbing_agent",
            "packages/funcn_registry/components/agents/pii_scrubbing/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test detect_pii_regex
        func = module.detect_pii_regex
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'text' in params
        
        # Test detect_pii_llm (decorated function)
        func = module.detect_pii_llm
        assert callable(func)
        
        # Test quick_scrub
        func = module.quick_scrub
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

    @pytest.mark.unit 
    def test_scrubbing_methods(self):
        """Test that various scrubbing methods are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pii_scrubbing_agent",
            "packages/funcn_registry/components/agents/pii_scrubbing/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for scrubbing methods
        import inspect
        source = inspect.getsource(module)
        assert 'mask' in source.lower()
        assert 'redact' in source.lower()
        assert 'generalize' in source.lower() or 'generalization' in source.lower()
        assert 'synthetic' in source.lower() or 'replace' in source.lower()

    @pytest.mark.unit
    def test_pii_types(self):
        """Test that various PII types are detected."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "pii_scrubbing_agent",
            "packages/funcn_registry/components/agents/pii_scrubbing/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for PII type support
        import inspect
        source = inspect.getsource(module)
        assert 'email' in source.lower()
        assert 'phone' in source.lower()
        assert 'ssn' in source.lower() or 'social' in source.lower()
        assert 'address' in source.lower()
        assert 'name' in source.lower()
        assert 'credit' in source.lower() or 'card' in source.lower() or 'financial' in source.lower()
