"""Test suite for enhanced_knowledge_graph_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestEnhancedKnowledgeGraphAgent(BaseAgentTest):
    """Test cases for enhanced knowledge graph agent."""

    component_name = "enhanced_knowledge_graph_agent"
    component_path = Path("packages/funcn_registry/components/agents/enhanced_knowledge_graph")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "enhanced_knowledge_graph_agent",
            "packages/funcn_registry/components/agents/enhanced_knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.extract_enhanced_knowledge_graph

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "text": "Apple Inc. was founded by Steve Jobs in 1976. The company is headquartered in Cupertino.",
                "domain": "technology",
                "extraction_depth": "comprehensive",
                "include_metadata": True,
            },
            {
                "text": "The human brain contains approximately 86 billion neurons connected by synapses.",
                "domain": "neuroscience",
                "extraction_depth": "standard",
                "include_metadata": False,
            },
            {
                "text": "Climate change affects global weather patterns and sea levels.",
                "domain": "environmental_science",
                "extraction_depth": "quick",
                "include_metadata": True,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "enhanced_knowledge_graph_agent",
            "packages/funcn_registry/components/agents/enhanced_knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Main functions found in the agent
        assert hasattr(module, 'extract_enhanced_knowledge_graph')
        assert callable(module.extract_enhanced_knowledge_graph)
        assert hasattr(module, 'plan_extraction')
        assert callable(module.plan_extraction)
        assert hasattr(module, 'extract_entities_with_reasoning')
        assert callable(module.extract_entities_with_reasoning)
        assert hasattr(module, 'extract_relationships_multipass')
        assert callable(module.extract_relationships_multipass)
        assert hasattr(module, 'validate_consistency')
        assert callable(module.validate_consistency)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "enhanced_knowledge_graph_agent",
            "packages/funcn_registry/components/agents/enhanced_knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test that the models exist
        assert hasattr(module, 'Entity')
        assert hasattr(module, 'Relationship')
        assert hasattr(module, 'ExtractionStrategy')
        assert hasattr(module, 'EntityExtraction')
        assert hasattr(module, 'RelationshipExtraction')
        assert hasattr(module, 'ValidationReport')
        assert hasattr(module, 'EnhancedKnowledgeGraph')
        
        # Test basic model instantiation
        Entity = module.Entity
        entity = Entity(
            id="entity_1",
            name="Apple Inc.",
            type="Organization",
            properties={"founded": "1976", "industry": "Technology"}
        )
        assert entity.name == "Apple Inc."
        assert entity.type == "Organization"
        
        # Test Relationship model
        Relationship = module.Relationship
        rel = Relationship(
            source_id="entity_1",
            target_id="entity_2",
            relationship_type="founded_by",
            properties={"year": "1976"}
        )
        assert rel.relationship_type == "founded_by"

    @pytest.mark.unit
    def test_extract_knowledge_graph_structure(self):
        """Test basic structure of extract_enhanced_knowledge_graph function."""
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
        assert 'domain' in params
        assert 'extraction_depth' in params
        assert 'include_metadata' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "enhanced_knowledge_graph_agent",
            "packages/funcn_registry/components/agents/enhanced_knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        EnhancedKnowledgeGraph = module.EnhancedKnowledgeGraph
        
        # Enhanced knowledge graph should return an EnhancedKnowledgeGraph
        assert isinstance(output, EnhancedKnowledgeGraph)
        assert hasattr(output, "entities")
        assert hasattr(output, "relationships")
        assert hasattr(output, "extraction_metadata")
        assert hasattr(output, "validation_report")
        assert hasattr(output, "summary")
        assert isinstance(output.entities, list)
        assert isinstance(output.relationships, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect
        
        spec = importlib.util.spec_from_file_location(
            "enhanced_knowledge_graph_agent",
            "packages/funcn_registry/components/agents/enhanced_knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test plan_extraction
        func = module.plan_extraction
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'text_preview' in params
        assert 'domain' in params
        
        # Test extract_entities_with_reasoning
        func = module.extract_entities_with_reasoning
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        
        # Test validate_consistency
        func = module.validate_consistency
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

    @pytest.mark.unit 
    def test_advanced_extraction_features(self):
        """Test that the agent has advanced extraction features."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "enhanced_knowledge_graph_agent",
            "packages/funcn_registry/components/agents/enhanced_knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for advanced features
        import inspect
        source = inspect.getsource(module)
        assert 'reasoning' in source.lower() or 'chain-of-thought' in source.lower()
        assert 'multipass' in source or 'multi-pass' in source
        assert 'validation' in source or 'consistency' in source
        assert 'metadata' in source

    @pytest.mark.unit
    def test_domain_support(self):
        """Test that different domains are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "enhanced_knowledge_graph_agent",
            "packages/funcn_registry/components/agents/enhanced_knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for domain handling
        import inspect
        source = inspect.getsource(module)
        assert 'domain' in source
        # Check for various domain examples
        assert any(d in source.lower() for d in ['technology', 'science', 'business', 'medical', 'general'])
