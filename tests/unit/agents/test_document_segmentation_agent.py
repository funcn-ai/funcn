"""Test suite for document_segmentation_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestDocumentSegmentationAgent(BaseAgentTest):
    """Test cases for document segmentation agent."""

    component_name = "document_segmentation_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/document_segmentation")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "document_segmentation_agent", "packages/sygaldry_registry/components/agents/document_segmentation/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.segment_document

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "document": "Chapter 1: Introduction\n\nThis is the introduction.\n\nChapter 2: Methods\n\nThese are the methods.",
                "strategy": "structural",
                "chunk_size": 500,
                "overlap": 50,
                "generate_summaries": True,
            },
            {
                "document": "The quick brown fox jumps over the lazy dog. This is a test document for semantic segmentation.",
                "strategy": "semantic",
                "chunk_size": 1000,
                "overlap": 100,
                "generate_summaries": False,
            },
            {
                "document": "Section 1: Background. Long text here. Section 2: Analysis. More text here.",
                "strategy": "hybrid",
                "chunk_size": 750,
                "overlap": 75,
                "generate_summaries": True,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "document_segmentation_agent", "packages/sygaldry_registry/components/agents/document_segmentation/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, 'segment_document')
        assert callable(module.segment_document)
        assert hasattr(module, 'segment_by_structure')
        assert callable(module.segment_by_structure)
        assert hasattr(module, 'analyze_document_structure')
        assert callable(module.analyze_document_structure)
        assert hasattr(module, 'segment_semantically')
        assert callable(module.segment_semantically)
        assert hasattr(module, 'summarize_segment')
        assert callable(module.summarize_segment)
        assert hasattr(module, 'quick_segment')
        assert callable(module.quick_segment)
        assert hasattr(module, 'extract_sections')
        assert callable(module.extract_sections)
        assert hasattr(module, 'chunk_for_embedding')
        assert callable(module.chunk_for_embedding)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "document_segmentation_agent", "packages/sygaldry_registry/components/agents/document_segmentation/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'DocumentSegment')
        assert hasattr(module, 'DocumentStructure')
        assert hasattr(module, 'SegmentationResult')

        # Test basic model instantiation
        DocumentSegment = module.DocumentSegment
        segment = DocumentSegment(
            id="seg_1", content="This is segment content", start_char=0, end_char=22, metadata={"type": "introduction"}
        )
        assert segment.id == "seg_1"
        assert segment.content == "This is segment content"
        assert segment.start_char == 0

        # Test optional summary field
        segment_with_summary = DocumentSegment(
            id="seg_2", content="Long content here", start_char=23, end_char=40, metadata={}, summary="Brief summary"
        )
        assert segment_with_summary.summary == "Brief summary"

    @pytest.mark.unit
    def test_segment_document_structure(self):
        """Test basic structure of segment_document function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'document' in params
        assert 'strategy' in params
        assert 'chunk_size' in params
        assert 'overlap' in params
        assert 'generate_summaries' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "document_segmentation_agent", "packages/sygaldry_registry/components/agents/document_segmentation/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SegmentationResult = module.SegmentationResult

        # Document segmentation should return a SegmentationResult
        assert isinstance(output, SegmentationResult)
        assert hasattr(output, "segments")
        assert hasattr(output, "strategy_used")
        assert hasattr(output, "total_segments")
        assert hasattr(output, "document_structure")
        assert hasattr(output, "metadata")
        assert isinstance(output.segments, list)
        assert output.total_segments >= 0

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "document_segmentation_agent", "packages/sygaldry_registry/components/agents/document_segmentation/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test analyze_document_structure
        func = module.analyze_document_structure
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'document' in params

        # Test segment_semantically
        func = module.segment_semantically
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test chunk_for_embedding
        func = module.chunk_for_embedding
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'text' in params
        assert 'chunk_size' in params

    @pytest.mark.unit
    def test_segmentation_strategies(self):
        """Test that multiple segmentation strategies are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "document_segmentation_agent", "packages/sygaldry_registry/components/agents/document_segmentation/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for different strategies
        import inspect

        source = inspect.getsource(module)
        assert 'structural' in source or 'structure' in source
        assert 'semantic' in source
        assert 'hybrid' in source or 'combined' in source
        assert 'fixed' in source or 'chunk' in source

    @pytest.mark.unit
    def test_embedding_optimization(self):
        """Test that the agent supports embedding optimization."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "document_segmentation_agent", "packages/sygaldry_registry/components/agents/document_segmentation/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for embedding-related features
        import inspect

        source = inspect.getsource(module)
        assert 'embedding' in source.lower() or 'vector' in source.lower()
        assert 'overlap' in source
        assert 'chunk' in source.lower()
