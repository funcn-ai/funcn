"""Pre-configured mock responses for common testing scenarios."""

from .llm_mocks import LLMMockFactory, MockToolCall
from pydantic import BaseModel
from typing import Any


# Sample response models for testing
class AnalysisResult(BaseModel):
    """Sample analysis result model."""

    summary: str
    confidence: float
    key_points: list[str]
    recommendations: list[str]


class EntityExtraction(BaseModel):
    """Sample entity extraction model."""

    entities: list[dict[str, str]]
    relationships: list[dict[str, Any]]


class SearchResult(BaseModel):
    """Sample search result model."""

    query: str
    results: list[dict[str, str]]
    total_count: int


# Pre-configured mock responses
MOCK_RESPONSES = {
    "text_analysis": {
        "content": "Based on my analysis, the text discusses three main themes: technology advancement, environmental impact, and social implications. The author presents a balanced view with strong supporting evidence.",
        "structured": AnalysisResult(
            summary="Analysis of technology's impact on society",
            confidence=0.92,
            key_points=["Technology is advancing rapidly", "Environmental concerns are growing", "Social dynamics are changing"],
            recommendations=[
                "Monitor technological developments",
                "Implement sustainable practices",
                "Foster community engagement",
            ],
        ),
    },
    "entity_extraction": {
        "content": "I found the following entities: Person: John Smith (CEO), Organization: TechCorp (technology company), Location: San Francisco (headquarters)",
        "structured": EntityExtraction(
            entities=[
                {"type": "Person", "name": "John Smith", "role": "CEO"},
                {"type": "Organization", "name": "TechCorp", "industry": "technology"},
                {"type": "Location", "name": "San Francisco", "context": "headquarters"},
            ],
            relationships=[
                {"source": "John Smith", "relation": "works_at", "target": "TechCorp"},
                {"source": "TechCorp", "relation": "located_in", "target": "San Francisco"},
            ],
        ),
    },
    "search": {
        "content": "I found 3 relevant results for your query about Python testing best practices.",
        "structured": SearchResult(
            query="Python testing best practices",
            results=[
                {
                    "title": "Python Testing 101",
                    "url": "https://example.com/python-testing",
                    "snippet": "Learn the fundamentals of testing in Python...",
                },
                {
                    "title": "Advanced pytest Patterns",
                    "url": "https://example.com/pytest-advanced",
                    "snippet": "Discover advanced pytest features and patterns...",
                },
                {
                    "title": "Test-Driven Development in Python",
                    "url": "https://example.com/tdd-python",
                    "snippet": "Master TDD principles with Python examples...",
                },
            ],
            total_count=42,
        ),
    },
    "code_generation": {
        "content": """```python
def calculate_fibonacci(n: int) -> int:
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)
```""",
        "tool_calls": [
            MockToolCall(
                "code_interpreter", {"code": "result = calculate_fibonacci(10)\nprint(f'The 10th Fibonacci number is: {result}')"}
            )
        ],
    },
    "multi_tool_coordination": {
        "content": "I'll search for the information and then analyze it.",
        "tool_calls": [
            MockToolCall("web_search", {"query": "latest AI developments 2024"}),
            MockToolCall("pdf_analyzer", {"url": "https://example.com/ai-report.pdf"}),
            MockToolCall("summarizer", {"text": "Combined findings from search and PDF"}),
        ],
    },
    "error_scenarios": {
        "rate_limit": {"error": "Rate limit exceeded. Please try again in 60 seconds."},
        "invalid_input": {"error": "Invalid input format. Expected JSON but received plain text."},
        "timeout": {"error": "Request timeout after 30 seconds."},
        "api_error": {"error": "Internal server error. Please try again later."},
    },
}


class MockResponseFactory:
    """Factory for creating pre-configured mock responses."""

    @staticmethod
    def get_text_analysis_response(provider: str = "openai"):
        """Get a mock text analysis response."""
        data = MOCK_RESPONSES["text_analysis"]
        return LLMMockFactory.create_mock_for_provider(
            provider,
            content=data["content"] if isinstance(data, dict) else str(data),
            response_model=AnalysisResult,
            parsed_data=data["structured"] if isinstance(data, dict) else None
        )

    @staticmethod
    def get_entity_extraction_response(provider: str = "openai"):
        """Get a mock entity extraction response."""
        data = MOCK_RESPONSES["entity_extraction"]
        return LLMMockFactory.create_mock_for_provider(
            provider,
            content=data["content"] if isinstance(data, dict) else str(data),
            response_model=EntityExtraction,
            parsed_data=data["structured"] if isinstance(data, dict) else None
        )

    @staticmethod
    def get_search_response(provider: str = "openai"):
        """Get a mock search response."""
        data = MOCK_RESPONSES["search"]
        return LLMMockFactory.create_mock_for_provider(
            provider,
            content=data["content"] if isinstance(data, dict) else str(data),
            response_model=SearchResult,
            parsed_data=data["structured"] if isinstance(data, dict) else None
        )

    @staticmethod
    def get_code_generation_response(provider: str = "openai"):
        """Get a mock code generation response with tool calls."""
        data = MOCK_RESPONSES["code_generation"]
        return LLMMockFactory.create_mock_for_provider(
            provider,
            content=data["content"] if isinstance(data, dict) else str(data),
            tool_calls=data.get("tool_calls", []) if isinstance(data, dict) else []
        )

    @staticmethod
    def get_multi_tool_response(provider: str = "openai"):
        """Get a mock response with multiple tool calls."""
        data = MOCK_RESPONSES["multi_tool_coordination"]
        return LLMMockFactory.create_mock_for_provider(
            provider,
            content=data["content"] if isinstance(data, dict) else str(data),
            tool_calls=data.get("tool_calls", []) if isinstance(data, dict) else []
        )

    @staticmethod
    def get_streaming_chunks(text: str, chunk_size: int = 10) -> list[str]:
        """Split text into chunks for streaming simulation."""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk_words = words[i : i + chunk_size]
            chunks.append(" ".join(chunk_words) + " ")

        return chunks

    @staticmethod
    def get_error_response(error_type: str = "api_error") -> dict[str, str]:
        """Get a mock error response."""
        error_data = MOCK_RESPONSES.get("error_scenarios", {})
        if isinstance(error_data, dict):
            return error_data.get(error_type, {"error": "Unknown error occurred"})
        return {"error": "Unknown error occurred"}
