"""Test suite for text_summarization_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestTextSummarizationAgent(BaseAgentTest):
    """Test cases for text summarization agent."""

    component_name = "text_summarization_agent"
    component_path = Path("packages/sygaldry_registry/components/agents/text_summarization")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "text_summarization_agent", "packages/sygaldry_registry/components/agents/text_summarization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.summarize_text

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "text": "Climate change is accelerating. Global temperatures have risen by 1.1°C since pre-industrial times. The impacts include more frequent extreme weather events, rising sea levels, and ecosystem disruption. Urgent action is needed to reduce greenhouse gas emissions and adapt to climate impacts.",
                "style": "executive",
                "target_length": 50,
                "progressive": False,
                "validate": False,
            },
            {
                "text": "The transformer architecture revolutionized natural language processing through self-attention mechanisms. It enables parallel processing of sequences and captures long-range dependencies effectively. BERT, GPT, and other transformer-based models have achieved state-of-the-art results across NLP tasks.",
                "style": "technical",
                "progressive": True,
                "validate": False,
            },
            {
                "text": "A new study shows that regular exercise improves mental health. Researchers found that 30 minutes of moderate activity daily reduces anxiety and depression symptoms. The benefits were consistent across age groups and demographics.",
                "style": "simple",
                "validate": False,
            },
        ]

    def test_get_style_config(self):
        """Test style configuration retrieval."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "text_summarization_agent", "packages/sygaldry_registry/components/agents/text_summarization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        get_style_config = module.get_style_config

        # Test all available styles
        styles = ["technical", "executive", "simple", "academic", "journalistic"]

        for style in styles:
            examples, guidelines = get_style_config(style)
            assert isinstance(examples, str)
            assert isinstance(guidelines, str)
            assert len(examples) > 0
            assert len(guidelines) > 0

        # Test unknown style
        examples, guidelines = get_style_config("unknown")
        assert examples == ""
        assert "clear, concise" in guidelines

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "text_summarization_agent", "packages/sygaldry_registry/components/agents/text_summarization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist and have the expected fields
        assert hasattr(module, 'KeyPoint')
        assert hasattr(module, 'Summary')
        assert hasattr(module, 'ProgressiveSummary')
        assert hasattr(module, 'SummaryAnalysis')
        assert hasattr(module, 'SummaryValidation')

        # Test basic model instantiation without complex types
        KeyPoint = module.KeyPoint
        key_point = KeyPoint(point="Test point", importance=0.5, evidence="Test evidence")
        assert key_point.point == "Test point"
        assert key_point.importance == 0.5
        assert key_point.evidence == "Test evidence"

        # Test Summary model
        Summary = module.Summary
        summary = Summary(
            summary="Test summary", style="executive", word_count=2, preserved_key_points=["test"], confidence_score=0.8
        )
        assert summary.summary == "Test summary"
        assert summary.style == "executive"
        assert summary.word_count == 2
        assert len(summary.preserved_key_points) == 1
        assert summary.confidence_score == 0.8

        # Test ProgressiveSummary model
        ProgressiveSummary = module.ProgressiveSummary
        progressive = ProgressiveSummary(
            one_sentence="One sentence",
            paragraph="Paragraph",
            detailed="Detailed",
            executive="Executive",
            key_takeaways=["Takeaway 1", "Takeaway 2"],
        )
        assert progressive.one_sentence == "One sentence"
        assert progressive.paragraph == "Paragraph"
        assert progressive.detailed == "Detailed"
        assert progressive.executive == "Executive"
        assert len(progressive.key_takeaways) == 2

        # Just verify the complex models exist - don't instantiate them
        # due to forward reference issues with direct import
        assert module.SummaryAnalysis.__name__ == 'SummaryAnalysis'
        assert module.SummaryValidation.__name__ == 'SummaryValidation'

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "text_summarization_agent", "packages/sygaldry_registry/components/agents/text_summarization/agent.py"
        )
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        # Main function
        assert hasattr(agent, 'summarize_text')
        assert callable(agent.summarize_text)

        # LLM-decorated functions
        assert hasattr(agent, 'analyze_for_summary')
        assert hasattr(agent, 'generate_summary')
        assert hasattr(agent, 'generate_progressive_summary')
        assert hasattr(agent, 'validate_summary')

        # Convenience functions
        assert hasattr(agent, 'quick_summary')
        assert hasattr(agent, 'executive_brief')
        assert hasattr(agent, 'multi_style_summary')

        # Helper functions
        assert hasattr(agent, 'get_style_config')

    @pytest.mark.asyncio
    async def test_summarize_text_basic_structure(self):
        """Test basic structure of summarize_text function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "text_summarization_agent", "packages/sygaldry_registry/components/agents/text_summarization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        summarize_text = module.summarize_text
        Summary = module.Summary
        ProgressiveSummary = module.ProgressiveSummary

        # Test that function is async
        import inspect

        assert inspect.iscoroutinefunction(summarize_text)

        # Test function signature
        sig = inspect.signature(summarize_text)
        params = list(sig.parameters.keys())
        assert 'text' in params
        assert 'style' in params
        assert 'target_length' in params
        assert 'progressive' in params
        assert 'validate' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "text_summarization_agent", "packages/sygaldry_registry/components/agents/text_summarization/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        Summary = module.Summary
        ProgressiveSummary = module.ProgressiveSummary

        if input_data.get("progressive", False):
            # Progressive summary
            assert isinstance(output, ProgressiveSummary)
            assert hasattr(output, "one_sentence")
            assert hasattr(output, "paragraph")
            assert hasattr(output, "detailed")
            assert hasattr(output, "executive")
            assert hasattr(output, "key_takeaways")
            assert isinstance(output.key_takeaways, list)
        else:
            # Regular summary
            assert isinstance(output, Summary)
            assert hasattr(output, "summary")
            assert hasattr(output, "style")
            assert hasattr(output, "word_count")
            assert hasattr(output, "preserved_key_points")
            assert hasattr(output, "confidence_score")
            assert isinstance(output.preserved_key_points, list)
            assert 0 <= output.confidence_score <= 1
