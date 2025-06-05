# Funcn Testing Guide

This guide provides comprehensive documentation for testing funcn components, following Mirascope best practices and the project's testing standards.

## Table of Contents

1. [Overview](#overview)
2. [Testing Philosophy](#testing-philosophy)
3. [Test Structure](#test-structure)
4. [Testing Agents](#testing-agents)
5. [Testing Tools](#testing-tools)
6. [Testing with Mirascope](#testing-with-mirascope)
7. [Async Testing](#async-testing)
8. [Test Fixtures and Data](#test-fixtures-and-data)
9. [Running Tests](#running-tests)
10. [Best Practices](#best-practices)

## Overview

The funcn testing framework provides:

- **Base test classes** for agents and tools
- **Mock factories** for all LLM providers
- **Test fixtures** for common data formats
- **Async utilities** for testing async components
- **Mirascope-specific helpers** for testing LLM interactions

## Testing Philosophy

Following the 80/20 rule from `.claude/standards/testing-standards.md`:

1. **Focus on critical paths** - Test the most important functionality first
2. **Happy path first** - Ensure basic functionality works
3. **Common error cases** - Handle typical failures gracefully
4. **Skip trivial code** - Don't test getters, framework code, or generated code

## Test Structure

```
tests/
├── conftest.py                 # Global fixtures and configuration
├── unit/                       # Fast, isolated unit tests
├── integration/                # Tests with external dependencies
├── e2e/                        # End-to-end workflow tests
├── fixtures/                   # Test data and mock responses
├── utils/                      # Test utilities and base classes
└── examples/                   # Example tests demonstrating patterns
```

## Testing Agents

### Basic Agent Test

```python
from tests.utils import BaseAgentTest
from pathlib import Path

class TestMyAgent(BaseAgentTest):
    """Test suite for my_agent component."""
    
    # Configure the test
    component_name = "my_agent"
    component_path = Path("packages/funcn_registry/components/agents/my_agent")
    mock_llm_provider = "openai"
    mock_model = "gpt-4"
    
    def get_component_function(self):
        """Import and return the agent function."""
        from agents.my_agent import my_agent
        return my_agent
    
    def get_test_inputs(self):
        """Provide test cases."""
        return [
            {"query": "Test query", "context": {"key": "value"}},
            {"query": "Another test", "context": {}},
        ]
    
    def get_mock_structured_response(self, model_class):
        """Provide custom mock data for response models."""
        if model_class.__name__ == "AnalysisResult":
            return model_class(
                summary="Mock analysis",
                confidence=0.95,
                key_points=["Point 1", "Point 2"]
            )
        return super().get_mock_structured_response(model_class)
```

### Testing with Structured Outputs

```python
from pydantic import BaseModel
from tests.utils import MirascopeTestHelper

class AgentOutput(BaseModel):
    result: str
    confidence: float

@pytest.mark.asyncio
async def test_agent_structured_output():
    """Test agent with Pydantic response model."""
    from agents.my_agent import analyze_text
    
    # Verify it uses proper Mirascope patterns
    MirascopeTestHelper.assert_uses_llm_decorator(analyze_text)
    MirascopeTestHelper.assert_has_response_model(analyze_text, AgentOutput)
    
    # Mock and test
    mock_output = AgentOutput(result="Analysis complete", confidence=0.92)
    
    with MirascopeMockFactory.mock_llm_call(
        response_model=AgentOutput,
        response_data=mock_output
    ):
        result = await analyze_text("Test input")
        assert result.confidence > 0.9
```

## Testing Tools

### Basic Tool Test

```python
from tests.utils import BaseToolTest
from pathlib import Path

class TestMyTool(BaseToolTest):
    """Test suite for my_tool component."""
    
    component_name = "my_tool"
    component_path = Path("packages/funcn_registry/components/tools/my_tool")
    
    def get_component_function(self):
        from tools.my_tool import search_data
        return search_data
    
    def get_test_inputs(self):
        return [
            {"query": "test search", "limit": 10},
            {"query": "another search", "limit": 5, "filters": {"type": "pdf"}},
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate tool output format."""
        assert isinstance(output, list)
        assert len(output) <= input_data.get("limit", 10)
        
        for item in output:
            assert "id" in item
            assert "content" in item
```

### Testing Tool Error Handling

```python
@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test tool handles errors gracefully."""
    from tools.my_tool import fetch_data
    
    # Test timeout error
    result = await fetch_data("http://timeout.com", timeout=0.001)
    assert "error" in result
    assert "timeout" in result["error"].lower()
    
    # Test invalid URL
    result = await fetch_data("not-a-url")
    assert "error" in result
```

## Testing with Mirascope

### Mocking LLM Calls

```python
from tests.fixtures import LLMMockFactory

@pytest.mark.asyncio
async def test_with_specific_provider():
    """Test with provider-specific mock."""
    mock_response = LLMMockFactory.create_openai_mock(
        content="Generated content",
        model="gpt-4",
        tool_calls=[
            MockToolCall("search", {"query": "test"})
        ]
    )
    
    with patch("mirascope.llm.call", return_value=mock_response):
        result = await my_agent("process this")
        assert "Generated content" in result
```

### Testing Streaming Responses

```python
@pytest.mark.asyncio
async def test_streaming_agent():
    """Test agent with streaming responses."""
    chunks = ["Hello", " from", " streaming", " response"]
    
    stream_mock = LLMMockFactory.create_streaming_mock(
        provider="openai",
        chunks=chunks
    )
    
    with patch("mirascope.llm.call", return_value=stream_mock):
        result = []
        async for chunk in stream_agent("test"):
            result.append(chunk.content)
        
        assert "".join(result) == "Hello from streaming response"
```

### Testing Retry Logic

```python
from tenacity import RetryError

@pytest.mark.asyncio
async def test_retry_on_failure():
    """Test agent retries on failure."""
    attempt_count = 0
    
    async def flaky_llm_call(*args, **kwargs):
        nonlocal attempt_count
        attempt_count += 1
        
        if attempt_count < 3:
            raise ValidationError("Invalid response")
        
        return Mock(content="Success", parsed=ValidOutput())
    
    with patch("mirascope.llm.call", side_effect=flaky_llm_call):
        result = await agent_with_retry("test")
        assert attempt_count == 3
        assert result.content == "Success"
```

## Async Testing

### Using Async Test Helpers

```python
from tests.utils import AsyncTestHelper, async_test

@async_test(timeout=5.0)
async def test_concurrent_operations():
    """Test multiple async operations."""
    tasks = [
        process_item("item1"),
        process_item("item2"),
        process_item("item3")
    ]
    
    # Run with timeout
    results = await AsyncTestHelper.run_with_timeout(
        asyncio.gather(*tasks),
        timeout=3.0
    )
    
    assert len(results) == 3
```

### Testing with Concurrency Limits

```python
@pytest.mark.asyncio
async def test_limited_concurrency():
    """Test processing with concurrency limit."""
    items = list(range(100))
    
    async def process(item):
        await asyncio.sleep(0.1)
        return item * 2
    
    # Process with max 5 concurrent operations
    results = await AsyncTestHelper.async_map(
        process,
        items,
        concurrency=5
    )
    
    assert len(results) == 100
    assert results[0] == 0
    assert results[50] == 100
```

## Test Fixtures and Data

### Using Test Data Factory

```python
from tests.fixtures import TestDataFactory

def test_with_sample_files(tmp_path):
    """Test with various file types."""
    # Create sample files
    csv_file = TestDataFactory.create_csv_file(tmp_path)
    json_file = TestDataFactory.create_json_file(tmp_path)
    pdf_file = TestDataFactory.create_pdf_file(tmp_path)
    
    # Test file processing
    from tools.file_processor import process_file
    
    result = process_file(csv_file)
    assert result["type"] == "csv"
    assert len(result["rows"]) > 0
```

### Using Component Fixtures

```python
from tests.fixtures import ComponentFixtureFactory

def test_component_installation(tmp_path):
    """Test component installation process."""
    # Create sample components
    components = ComponentFixtureFactory.create_all_sample_components(tmp_path)
    
    # Test component loading
    from funcn_cli.core.component_manager import ComponentManager
    
    manager = ComponentManager()
    for name, path in components.items():
        component = manager.load_component(path)
        assert component.name == name
```

## Running Tests

### Basic Commands

```bash
# Run all tests
task test

# Run specific test file
pytest tests/unit/test_my_agent.py

# Run tests by marker
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests
pytest -m "not slow"        # Skip slow tests

# Run with coverage
pytest --cov=funcn_cli --cov-report=html

# Run tests in parallel
pytest -n auto
```

### Running Tests for Specific Components

```bash
# Test a specific agent
pytest tests/unit/agents/test_text_summarization_agent.py -v

# Test all tools
pytest tests/unit/tools/ -v

# Test with specific provider
pytest -k "openai" tests/unit/agents/
```

## Best Practices

### 1. Follow Mirascope Patterns

- Always mock `mirascope.llm.call` for LLM interactions
- Test with multiple providers using parametrize
- Verify structured outputs with Pydantic models
- Test streaming responses when applicable

### 2. Use Appropriate Test Levels

```python
# Unit test - mock all external dependencies
@pytest.mark.unit
async def test_agent_logic():
    with patch("mirascope.llm.call"):
        # Test pure logic
        pass

# Integration test - may use real services
@pytest.mark.integration
async def test_with_real_api():
    # Test with actual API calls
    pass

# E2E test - full workflow
@pytest.mark.e2e
async def test_complete_workflow():
    # Test entire user journey
    pass
```

### 3. Test Error Scenarios

```python
# Always test common error cases
async def test_error_handling():
    # API errors
    with pytest.raises(APIError):
        await agent_with_invalid_key("test")
    
    # Validation errors
    with pytest.raises(ValidationError):
        await agent_with_bad_input({"invalid": "data"})
    
    # Timeout errors
    with pytest.raises(TimeoutError):
        await agent_with_short_timeout("test", timeout=0.001)
```

### 4. Use Fixtures Effectively

```python
@pytest.fixture
def sample_document():
    """Reusable test document."""
    return {
        "title": "Test Document",
        "content": "Long test content...",
        "metadata": {"author": "Test Author"}
    }

async def test_with_fixture(sample_document):
    result = await analyze_document(sample_document)
    assert result.title == sample_document["title"]
```

### 5. Test Provider Compatibility

```python
@pytest.mark.parametrize("provider,model", [
    ("openai", "gpt-4"),
    ("anthropic", "claude-3-opus-20240229"),
    ("google", "gemini-pro"),
])
async def test_multi_provider(provider, model):
    """Ensure component works with all providers."""
    with patch("mirascope.llm.call") as mock:
        result = await agent_func(
            "test input",
            provider=provider,
            model=model
        )
        assert result is not None
```

### 6. Document Test Purpose

```python
def test_handles_empty_input():
    """
    Test that agent gracefully handles empty input.
    
    This is important because users might accidentally
    submit empty forms or queries.
    """
    result = process_empty_query("")
    assert result == "Please provide a valid query"
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure test files properly import components
2. **Async Warnings**: Use `@pytest.mark.asyncio` for async tests
3. **Mock Not Working**: Check you're mocking the right import path
4. **Timeout Errors**: Increase timeout for slow operations

### Debugging Tips

```python
# Enable verbose output
pytest -vv tests/unit/test_my_agent.py

# Show print statements
pytest -s tests/unit/test_my_agent.py

# Debug specific test
pytest tests/unit/test_my_agent.py::test_specific_case -vv

# Check test coverage gaps
pytest --cov=funcn_cli --cov-report=term-missing
```

## Contributing Tests

When adding new components:

1. Create corresponding test file in appropriate directory
2. Extend appropriate base test class
3. Provide comprehensive test inputs
4. Test happy path and error cases
5. Ensure 80%+ coverage for critical code
6. Run pre-commit hooks before committing

Remember: Good tests enable confident refactoring and prevent regressions!