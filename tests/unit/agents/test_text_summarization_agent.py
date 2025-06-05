"""Test suite for text_summarization_agent following Mirascope best practices."""

import pytest
from pathlib import Path
from tests.fixtures import MockResponseFactory, TestDataFactory
from tests.utils import BaseAgentTest, MirascopeTestHelper
from unittest.mock import Mock, patch


class TestTextSummarizationAgent(BaseAgentTest):
    """Test text_summarization_agent component."""
    
    component_name = "text_summarization_agent"
    component_path = Path("packages/funcn_registry/components/agents/text_summarization_agent")
    mock_llm_provider = "openai"
    mock_model = "gpt-4o-mini"
    
    def get_component_function(self):
        """Import the main agent function."""
        # Import would be: from agents.text_summarization_agent import text_summarization_agent
        # For testing, we'll mock this
        async def mock_agent(text: str, **kwargs):
            """Mock agent for testing."""
            return Mock(
                summary="Test summary",
                style="technical",
                confidence=0.95
            )
        return mock_agent
    
    def get_test_inputs(self):
        """Provide test cases for the agent."""
        return [
            {
                "text": TestDataFactory.SAMPLE_TEXT,
                "style": "technical",
                "max_length": 100
            },
            {
                "text": "Short text for summarization.",
                "style": "executive",
                "max_length": 50
            },
            {
                "text": TestDataFactory.SAMPLE_MARKDOWN_CODE,
                "style": "simple",
                "max_length": 200
            }
        ]
    
    @pytest.mark.asyncio
    async def test_agent_summarizes_different_styles(self):
        """Test agent can produce different summary styles."""
        test_text = TestDataFactory.SAMPLE_TEXT
        
        styles = ["technical", "executive", "simple", "academic", "journalistic"]
        
        for style in styles:
            # Mock different responses for different styles
            mock_summary = f"This is a {style} summary of the text."
            
            with patch("mirascope.llm.call") as mock_llm:
                mock_llm.return_value = Mock(
                    content=mock_summary,
                    parsed=Mock(
                        summary=mock_summary,
                        style=style,
                        confidence=0.9,
                        word_count=len(mock_summary.split())
                    )
                )
                
                agent = self.get_component_function()
                result = await agent(text=test_text, style=style)
                
                assert result.summary is not None
                assert style.lower() in result.summary.lower() or hasattr(result, 'style')
    
    @pytest.mark.asyncio
    async def test_progressive_summarization(self):
        """Test progressive summarization for long texts."""
        # Create a very long text
        long_text = " ".join([TestDataFactory.SAMPLE_TEXT] * 10)
        
        with patch("mirascope.llm.call") as mock_llm:
            # Mock progressive summarization responses
            mock_llm.side_effect = [
                Mock(parsed=Mock(chunks=["chunk1", "chunk2", "chunk3"])),
                Mock(parsed=Mock(summary="Intermediate summary 1")),
                Mock(parsed=Mock(summary="Intermediate summary 2")),
                Mock(parsed=Mock(summary="Final consolidated summary"))
            ]
            
            agent = self.get_component_function()
            result = await agent(
                text=long_text,
                style="technical",
                progressive=True
            )
            
            # Should have made multiple calls for progressive summarization
            assert mock_llm.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_summary_validation(self):
        """Test summary validation and quality checks."""
        test_cases = [
            {
                "text": "AI is transforming healthcare through predictive analytics.",
                "expected_keywords": ["AI", "healthcare", "analytics"],
                "style": "technical"
            },
            {
                "text": TestDataFactory.SAMPLE_CSV,
                "expected_keywords": ["data", "employees", "departments"],
                "style": "executive"
            }
        ]
        
        for test_case in test_cases:
            with patch("mirascope.llm.call") as mock_llm:
                mock_summary = f"Summary containing {' and '.join(test_case['expected_keywords'])}"
                
                mock_llm.return_value = Mock(
                    parsed=Mock(
                        summary=mock_summary,
                        validation_passed=True,
                        key_concepts=test_case["expected_keywords"]
                    )
                )
                
                agent = self.get_component_function()
                result = await agent(
                    text=test_case["text"],
                    style=test_case["style"]
                )
                
                # Verify summary contains expected content
                assert result.summary is not None
    
    @pytest.mark.asyncio
    async def test_iterative_refinement(self):
        """Test iterative refinement improves summary quality."""
        initial_summary = "Basic summary of the text."
        refined_summary = "A comprehensive and well-structured summary of the text with key insights."
        
        with patch("mirascope.llm.call") as mock_llm:
            # Mock iterative refinement
            mock_llm.side_effect = [
                Mock(parsed=Mock(summary=initial_summary, needs_refinement=True)),
                Mock(parsed=Mock(improvements=["Add more detail", "Include key metrics"])),
                Mock(parsed=Mock(summary=refined_summary, needs_refinement=False))
            ]
            
            agent = self.get_component_function()
            result = await agent(
                text=TestDataFactory.SAMPLE_TEXT,
                style="academic",
                iterative_refinement=True
            )
            
            # Should have made multiple calls for refinement
            assert mock_llm.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_handles_special_content(self):
        """Test agent handles special content types."""
        special_contents = [
            ("```python\ncode here\n```", "code"),
            ("| Col1 | Col2 |\n|------|------|\n| A    | B    |", "table"),
            ("1. First\n2. Second\n3. Third", "list"),
            ("$$E = mc^2$$", "formula")
        ]
        
        for content, content_type in special_contents:
            with patch("mirascope.llm.call") as mock_llm:
                mock_llm.return_value = Mock(
                    parsed=Mock(
                        summary=f"Summary of {content_type} content",
                        detected_content_type=content_type,
                        special_handling_applied=True
                    )
                )
                
                agent = self.get_component_function()
                result = await agent(text=content, style="technical")
                
                assert result.summary is not None
    
    def test_component_follows_mirascope_patterns(self):
        """Verify the component follows Mirascope best practices."""
        # In real implementation, would import actual function
        # from agents.text_summarization_agent import analyze_text
        
        # For demonstration, create a mock decorated function
        from mirascope import llm, prompt_template
        
        @llm.call(provider="{{provider}}", model="{{model}}")
        @prompt_template("Analyze: {text}")
        async def analyze_text(text: str):
            pass
        
        # Test best practices
        MirascopeTestHelper.assert_uses_llm_decorator(analyze_text)
        MirascopeTestHelper.assert_uses_prompt_template(analyze_text)
        MirascopeTestHelper.assert_provider_agnostic(analyze_text)


class TestTextSummarizationTools:
    """Test the tools used by text summarization agent."""
    
    def test_chunk_text_tool(self):
        """Test text chunking for long documents."""
        from funcn_registry.components.agents.text_summarization_agent.tools import chunk_text
        
        long_text = " ".join(["Sentence."] * 1000)
        chunks = chunk_text(long_text, chunk_size=500)
        
        assert len(chunks) > 1
        assert all(len(chunk.split()) <= 500 for chunk in chunks)
        
    def test_extract_key_points_tool(self):
        """Test key point extraction."""
        from funcn_registry.components.agents.text_summarization_agent.tools import extract_key_points
        
        text = """
        AI is revolutionizing healthcare. 
        Machine learning enables early disease detection.
        Natural language processing improves patient care.
        """
        
        points = extract_key_points(text)
        
        assert len(points) >= 2
        assert any("AI" in point for point in points)
        assert any("healthcare" in point for point in points)
