"""Test suite for knowledge_graph_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestKnowledgeGraphAgent(BaseAgentTest):
    """Test cases for knowledge graph agent."""

    component_name = "knowledge_graph_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/knowledge_graph")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "knowledge_graph_agent", "packages/sygaldry_registry/components/agents/knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.extract_knowledge_graph

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "text": "Marie Curie discovered radium and polonium. She won the Nobel Prize in Physics in 1903.",
                "include_properties": True,
                "enrich_entities": True,
                "output_format": "graph",
            },
            {
                "text": "Amazon Web Services provides cloud computing services to many companies including Netflix.",
                "include_properties": False,
                "enrich_entities": False,
                "output_format": "triples",
            },
            {
                "text": "The Python programming language was created by Guido van Rossum in 1991.",
                "include_properties": True,
                "enrich_entities": False,
                "output_format": "json",
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "knowledge_graph_agent", "packages/sygaldry_registry/components/agents/knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, 'extract_knowledge_graph')
        assert callable(module.extract_knowledge_graph)
        assert hasattr(module, 'extract_entities')
        assert callable(module.extract_entities)
        assert hasattr(module, 'extract_relationships')
        assert callable(module.extract_relationships)
        assert hasattr(module, 'enrich_knowledge_graph')
        assert callable(module.enrich_knowledge_graph)
        assert hasattr(module, 'extract_entities_only')
        assert callable(module.extract_entities_only)
        assert hasattr(module, 'extract_triples')
        assert callable(module.extract_triples)
        assert hasattr(module, 'build_domain_graph')
        assert callable(module.build_domain_graph)
        assert hasattr(module, 'visualize_graph_data')
        assert callable(module.visualize_graph_data)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "knowledge_graph_agent", "packages/sygaldry_registry/components/agents/knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'Entity')
        assert hasattr(module, 'Relationship')
        assert hasattr(module, 'KnowledgeGraph')
        assert hasattr(module, 'EntityResponse')
        assert hasattr(module, 'RelationshipResponse')
        assert hasattr(module, 'EnrichmentResponse')

        # Test basic model instantiation
        Entity = module.Entity
        entity = Entity(name="Marie Curie", type="Person", properties={"profession": "Scientist", "nationality": "Polish-French"})
        assert entity.name == "Marie Curie"
        assert entity.type == "Person"

        # Test Relationship model
        Relationship = module.Relationship
        rel = Relationship(source="Marie Curie", relationship="discovered", target="Radium", properties={"year": "1898"})
        assert rel.source == "Marie Curie"
        assert rel.relationship == "discovered"
        assert rel.target == "Radium"

    @pytest.mark.unit
    def test_extract_knowledge_graph_structure(self):
        """Test basic structure of extract_knowledge_graph function."""
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
        assert 'include_properties' in params
        assert 'enrich_entities' in params
        assert 'output_format' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "knowledge_graph_agent", "packages/sygaldry_registry/components/agents/knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        KnowledgeGraph = module.KnowledgeGraph

        # Knowledge graph agent should return a KnowledgeGraph
        assert isinstance(output, KnowledgeGraph)
        assert hasattr(output, "entities")
        assert hasattr(output, "relationships")
        assert hasattr(output, "metadata")
        assert isinstance(output.entities, list)
        assert isinstance(output.relationships, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "knowledge_graph_agent", "packages/sygaldry_registry/components/agents/knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test extract_entities
        func = module.extract_entities
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'text' in params

        # Test extract_relationships
        func = module.extract_relationships
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test extract_triples
        func = module.extract_triples
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'text' in params

    @pytest.mark.unit
    def test_output_format_support(self):
        """Test that multiple output formats are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "knowledge_graph_agent", "packages/sygaldry_registry/components/agents/knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for output format support
        import inspect

        source = inspect.getsource(module)
        assert 'graph' in source.lower()
        assert 'triples' in source or 'triple' in source
        assert 'json' in source.lower()
        assert 'format' in source

    @pytest.mark.unit
    def test_enrichment_capabilities(self):
        """Test that the agent supports entity enrichment."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "knowledge_graph_agent", "packages/sygaldry_registry/components/agents/knowledge_graph/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for enrichment features
        import inspect

        source = inspect.getsource(module)
        assert 'enrich' in source.lower()
        assert 'properties' in source or 'attributes' in source
        assert 'metadata' in source
