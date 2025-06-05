"""Example test demonstrating Mirascope testing best practices."""

import pytest
from pydantic import BaseModel, Field
from tests.utils.mirascope_test_helpers import MirascopeMockFactory, MirascopeTestCase, MirascopeTestHelper
from typing import Any
from unittest.mock import Mock, patch


# Example agent code to test
class AnalysisResult(BaseModel):
    """Structured analysis output following Mirascope best practices."""

    summary: str = Field(..., description="Brief summary of findings")
    key_points: list[str] = Field(..., description="Main points identified")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    sources: list[str] = Field(default_factory=list, description="Source references")


# Mock the Mirascope decorators for testing
def mock_llm_call(**kwargs):
    """Mock @llm.call decorator."""
    def decorator(func):
        func._mirascope_call_kwargs = kwargs
        func.__wrapped__ = func  # Simulate wrapped function
        return func
    return decorator


def mock_prompt_template(template: str):
    """Mock @prompt_template decorator."""
    def decorator(func):
        func._mirascope_prompt_template = template
        func.__wrapped__ = func
        return func
    return decorator


# Example agent using Mirascope patterns
@mock_llm_call(
    provider="{{provider}}",
    model="{{model}}",
    response_model=AnalysisResult
)
@mock_prompt_template("""
Analyze the following document and provide structured findings.

Document: {document}

Please include:
1. A brief summary
2. 3-5 key points
3. Your confidence level (0-1)
4. Any sources referenced
""")
async def analyze_document(document: str) -> AnalysisResult:
    """Analyze document following Mirascope best practices."""
    # In real implementation, this would be handled by Mirascope
    pass


# Example tool following Mirascope patterns
def search_documents(
    query: str,
    limit: int = 10,
    file_type: str = "all"
) -> list[dict[str, str]]:
    """Search documents - simple tool function following best practices.

    Args:
        query: Search query string
        limit: Maximum results to return
        file_type: Filter by file type (all, pdf, txt, md)

    Returns:
        List of documents with title and content
    """
    # Mock implementation
    return [
        {"title": f"Doc {i}", "content": f"Content matching {query}"}
        for i in range(min(limit, 5))
    ]


class TestMirascopeAgent(MirascopeTestCase):
    """Test suite demonstrating Mirascope testing best practices."""

    def test_agent_follows_best_practices(self):
        """Test that agent follows Mirascope best practices."""
        # Check decorator usage
        MirascopeTestHelper.assert_uses_llm_decorator(analyze_document)
        MirascopeTestHelper.assert_uses_prompt_template(analyze_document)

        # Check response model
        MirascopeTestHelper.assert_has_response_model(analyze_document, AnalysisResult)

        # Check provider-agnostic design
        MirascopeTestHelper.assert_provider_agnostic(analyze_document)

    @pytest.mark.asyncio
    async def test_agent_with_structured_output(self):
        """Test agent with structured Pydantic output."""
        # Create mock response data
        mock_result = AnalysisResult(
            summary="This document discusses AI applications",
            key_points=[
                "AI is transforming healthcare",
                "Machine learning enables predictive analytics",
                "Ethical considerations are crucial"
            ],
            confidence=0.92,
            sources=["research_paper.pdf", "industry_report.html"]
        )

        # Mock the LLM call
        with MirascopeMockFactory.mock_llm_call(
            provider="openai",
            response_model=AnalysisResult,
            response_data=mock_result
        ):
            # In real test, the decorated function would return the parsed response
            result = mock_result  # Simulating the response

            # Verify structured output
            assert isinstance(result, AnalysisResult)
            assert result.confidence > 0.9
            assert len(result.key_points) == 3
            assert "research_paper.pdf" in result.sources

    @pytest.mark.asyncio
    async def test_agent_validation_errors(self):
        """Test handling of validation errors in response models."""
        # Invalid data that should fail validation
        invalid_data = {
            "summary": "Valid summary",
            "key_points": ["point1"],
            "confidence": 1.5,  # Invalid: > 1.0
            "sources": []
        }

        # Test that validation error is raised
        with pytest.raises(ValueError) as exc_info:
            AnalysisResult(**invalid_data)

        assert "less than or equal to 1" in str(exc_info.value)

    def test_tool_follows_best_practices(self):
        """Test that tools follow Mirascope patterns."""
        # Tools should be simple functions
        assert callable(search_documents)

        # Test with various inputs
        results = search_documents("AI research", limit=3)
        assert len(results) == 3
        assert all("content" in r and "title" in r for r in results)

        # Test with filters
        results = search_documents("machine learning", limit=10, file_type="pdf")
        assert len(results) <= 10

    @pytest.mark.asyncio
    async def test_agent_with_tool_calls(self):
        """Test agent that uses tools."""
        # Mock tool response
        mock_tool_results = [
            {"title": "AI Ethics", "content": "Discussion on AI ethics..."},
            {"title": "ML Best Practices", "content": "Machine learning guidelines..."}
        ]

        with patch("search_documents", return_value=mock_tool_results):
            # In real scenario, agent would call the tool
            tool_results = search_documents("ethics in AI")

            # Verify tool was called correctly
            assert len(tool_results) == 2
            assert any("ethics" in r["title"].lower() for r in tool_results)

    @pytest.mark.asyncio
    async def test_streaming_response(self):
        """Test streaming responses following Mirascope patterns."""
        content = "This is a streaming response for testing purposes"

        with MirascopeMockFactory.mock_llm_call(
            provider="openai",
            response_content=content,
            stream=True
        ):
            # In real implementation, this would stream
            # For testing, we simulate collecting chunks
            chunks = []
            words = content.split()

            for word in words:
                chunks.append(word + " ")

            result = "".join(chunks).strip()
            assert result == content

    def test_error_handling_in_tools(self):
        """Test proper error handling in tools."""
        def fetch_with_timeout(url: str, timeout: int = 10) -> dict[str, Any]:
            """Tool with proper error handling."""
            if "invalid" in url:
                return {"error": "Invalid URL", "url": url}
            if timeout < 1:
                return {"error": "Timeout too short", "timeout": timeout}
            return {"data": "Success", "url": url}

        # Test error cases
        result = fetch_with_timeout("http://invalid-url.com")
        assert "error" in result

        result = fetch_with_timeout("http://valid.com", timeout=0)
        assert result["error"] == "Timeout too short"

        # Test success case
        result = fetch_with_timeout("http://valid.com")
        assert result["data"] == "Success"


class TestMirascopeRetryLogic:
    """Test retry patterns with Tenacity."""

    @pytest.mark.asyncio
    async def test_retry_on_validation_error(self):
        """Test retry behavior on validation errors."""
        attempt_count = 0

        class RetryableResult(BaseModel):
            value: str
            attempt: int

        async def flaky_agent(query: str) -> RetryableResult:
            """Agent that fails first 2 attempts."""
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:
                # Simulate validation error
                raise ValueError("Invalid response format")

            return RetryableResult(value="Success", attempt=attempt_count)

        # In real code, this would use @retry decorator
        # For testing, we simulate the retry behavior
        for i in range(3):
            try:
                result = await flaky_agent("test")
                break
            except ValueError:
                if i == 2:
                    raise
                continue

        assert attempt_count == 3
        assert result.value == "Success"
        assert result.attempt == 3


class TestProviderAgnostic:
    """Test provider-agnostic patterns."""

    def test_template_variable_substitution(self):
        """Test that template variables work correctly."""
        # Simulate template substitution
        template = "provider='{{provider}}', model='{{model}}'"

        # Test substitution
        openai_config = template.replace("{{provider}}", "openai").replace("{{model}}", "gpt-4")
        assert "provider='openai'" in openai_config
        assert "model='gpt-4'" in openai_config

        anthropic_config = template.replace("{{provider}}", "anthropic").replace("{{model}}", "claude-3")
        assert "provider='anthropic'" in anthropic_config
        assert "model='claude-3'" in anthropic_config


# Example of testing with multiple providers
@pytest.mark.parametrize("provider,model", [
    ("openai", "gpt-4"),
    ("anthropic", "claude-3-opus-20240229"),
    ("google", "gemini-pro"),
])
@pytest.mark.asyncio
async def test_multi_provider_compatibility(provider: str, model: str):
    """Test that components work with multiple providers."""
    with MirascopeMockFactory.mock_llm_call(
        provider=provider,
        model=model,
        response_content=f"Response from {provider}"
    ):
        # Each provider would be tested here
        mock_response = Mock()
        mock_response.content = f"Response from {provider}"
        mock_response.provider = provider
        mock_response.model = model

        assert provider in mock_response.content
        assert mock_response.model == model
