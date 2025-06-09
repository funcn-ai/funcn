"""Test helpers specifically for Mirascope-based components following best practices."""

import asyncio
import pytest
from collections.abc import Callable
from mirascope.core import BaseMessageParam, BaseToolKit
from pydantic import BaseModel, ValidationError
from tenacity import RetryError
from typing import Any, TypeVar
from unittest.mock import AsyncMock, Mock, patch

T = TypeVar("T", bound=BaseModel)


class MirascopeTestHelper:
    """Helper utilities for testing Mirascope components."""

    @staticmethod
    def assert_uses_llm_decorator(func: Callable) -> None:
        """Assert that a function uses the @llm.call decorator.
        
        Args:
            func: Function to check
            
        Raises:
            AssertionError: If function doesn't use @llm.call
        """
        # Check for Mirascope decorator attributes
        assert hasattr(func, "__wrapped__"), "Function should use @llm.call decorator"
        
        # Look for Mirascope-specific attributes
        wrapped = func
        found_llm_call = False
        
        while hasattr(wrapped, "__wrapped__"):
            if hasattr(wrapped, "_mirascope_call_kwargs"):
                found_llm_call = True
                break
            wrapped = wrapped.__wrapped__
        
        assert found_llm_call, "Function must use @llm.call decorator"

    @staticmethod
    def assert_uses_prompt_template(func: Callable) -> None:
        """Assert that a function uses the @prompt_template decorator.
        
        Args:
            func: Function to check
            
        Raises:
            AssertionError: If function doesn't use @prompt_template
        """
        assert hasattr(func, "__wrapped__"), "Function should use @prompt_template decorator"
        
        # Check for prompt template specific markers
        wrapped = func
        found_prompt_template = False
        
        while hasattr(wrapped, "__wrapped__"):
            if hasattr(wrapped, "_mirascope_prompt_template"):
                found_prompt_template = True
                break
            wrapped = wrapped.__wrapped__
        
        assert found_prompt_template, "Function must use @prompt_template decorator"

    @staticmethod
    def assert_has_response_model(func: Callable, model_class: type[BaseModel]) -> None:
        """Assert that a function uses a specific response model.
        
        Args:
            func: Function to check
            model_class: Expected response model class
            
        Raises:
            AssertionError: If function doesn't use the expected response model
        """
        wrapped = func
        while hasattr(wrapped, "__wrapped__"):
            if hasattr(wrapped, "_mirascope_call_kwargs"):
                response_model = wrapped._mirascope_call_kwargs.get("response_model")
                assert response_model is model_class, \
                    f"Expected response_model {model_class.__name__}, got {response_model}"
                return
            wrapped = wrapped.__wrapped__
        
        raise AssertionError("Function doesn't have a response_model configured")

    @staticmethod
    def assert_provider_agnostic(func: Callable) -> None:
        """Assert that a function is provider-agnostic (uses template variables).
        
        Args:
            func: Function to check
            
        Raises:
            AssertionError: If function hardcodes a provider
        """
        wrapped = func
        while hasattr(wrapped, "__wrapped__"):
            if hasattr(wrapped, "_mirascope_call_kwargs"):
                provider = wrapped._mirascope_call_kwargs.get("provider", "")
                model = wrapped._mirascope_call_kwargs.get("model", "")
                
                # Check for template variables
                assert "{{provider}}" in str(provider) or not provider, \
                    "Provider should use {{provider}} template variable"
                assert "{{model}}" in str(model) or not model, \
                    "Model should use {{model}} template variable"
                return
            wrapped = wrapped.__wrapped__
        
        raise AssertionError("Function doesn't have provider configuration")

    @staticmethod
    def get_mirascope_config(func: Callable) -> dict[str, Any]:
        """Extract Mirascope configuration from a decorated function.
        
        Args:
            func: Decorated function
            
        Returns:
            Dictionary of Mirascope configuration
        """
        config = {}
        wrapped = func
        
        while hasattr(wrapped, "__wrapped__"):
            if hasattr(wrapped, "_mirascope_call_kwargs"):
                config.update(wrapped._mirascope_call_kwargs)
                break
            wrapped = wrapped.__wrapped__
        
        return config

    @staticmethod
    def create_mock_message(content: str, role: str = "assistant") -> BaseMessageParam:
        """Create a mock message for testing.
        
        Args:
            content: Message content
            role: Message role (user, assistant, system)
            
        Returns:
            Mock message object
        """
        mock = Mock(spec=BaseMessageParam)
        mock.content = content
        mock.role = role
        return mock

    @staticmethod
    def create_mock_tool_response(
        tool_name: str,
        result: Any,
        success: bool = True
    ) -> Mock:
        """Create a mock tool response.
        
        Args:
            tool_name: Name of the tool
            result: Tool result
            success: Whether the tool call succeeded
            
        Returns:
            Mock tool response
        """
        response = Mock()
        response.tool_name = tool_name
        response.result = result
        response.success = success
        response.error = None if success else "Tool execution failed"
        return response


class MirascopeMockFactory:
    """Factory for creating Mirascope-specific mocks."""

    @staticmethod
    def mock_llm_call(
        provider: str = "openai",
        model: str = "gpt-4",
        response_content: str = "Mock response",
        response_model: type[BaseModel] | None = None,
        response_data: BaseModel | None = None,
        stream: bool = False
    ):
        """Create a context manager that mocks @llm.call decorated functions.
        
        Args:
            provider: Provider to mock
            model: Model to mock
            response_content: Text content of response
            response_model: Expected response model class
            response_data: Structured response data
            stream: Whether to mock streaming
            
        Returns:
            Context manager for mocking
        """
        def mock_decorator(func):
            if stream:
                # Create streaming mock
                async def async_gen():
                    words = response_content.split()
                    for word in words:
                        yield Mock(content=word + " ")
                
                return AsyncMock(return_value=async_gen())
            
            # Create regular mock
            mock_response = Mock()
            mock_response.content = response_content
            mock_response.model = model
            
            if response_model and response_data:
                mock_response.parsed = response_data
            elif response_model:
                # Auto-generate mock data
                mock_response.parsed = MirascopeMockFactory._generate_mock_model(response_model)
            
            if asyncio.iscoroutinefunction(func):
                return AsyncMock(return_value=mock_response)
            return Mock(return_value=mock_response)
        
        return patch(f"mirascope.{provider}.{provider}.call", side_effect=mock_decorator)

    @staticmethod
    def _generate_mock_model(model_class: type[BaseModel]) -> BaseModel:
        """Generate a mock instance of a Pydantic model.
        
        Args:
            model_class: The model class to instantiate
            
        Returns:
            Mock instance with default values
        """
        mock_data: dict[str, Any] = {}
        
        for field_name, field_info in model_class.model_fields.items():
            field_type = field_info.annotation
            
            # Generate appropriate mock values based on type
            if field_type is str:
                mock_data[field_name] = f"mock_{field_name}"
            elif field_type is int:
                mock_data[field_name] = 42
            elif field_type is float:
                mock_data[field_name] = 0.95
            elif field_type is bool:
                mock_data[field_name] = True
            elif field_type is not None and hasattr(field_type, "__origin__"):
                if field_type.__origin__ is list:
                    mock_data[field_name] = ["item1", "item2"]
                elif field_type.__origin__ is dict:
                    mock_data[field_name] = {"key": "value"}
            else:
                # For complex types, try None if optional
                if not field_info.is_required():
                    mock_data[field_name] = None
        
        return model_class(**mock_data)

    @staticmethod
    def mock_tool_call(
        tool_func: Callable,
        return_value: Any = "Mock tool result",
        side_effect: Exception | None = None
    ):
        """Mock a tool function call.
        
        Args:
            tool_func: Tool function to mock
            return_value: Value to return
            side_effect: Exception to raise
            
        Returns:
            Mock patch object
        """
        if side_effect:
            return patch.object(
                tool_func,
                "__call__",
                side_effect=side_effect
            )
        
        return patch.object(
            tool_func,
            "__call__",
            return_value=return_value
        )


class MirascopeTestCase:
    """Base test case for Mirascope components following best practices."""

    @pytest.mark.asyncio
    async def test_retry_behavior(
        self,
        func_with_retry: Callable,
        mock_failure_count: int = 2
    ):
        """Test retry behavior with Tenacity.
        
        Args:
            func_with_retry: Function decorated with @retry
            mock_failure_count: Number of failures before success
        """
        call_count = 0
        
        async def mock_response(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count <= mock_failure_count:
                raise ValidationError("Mock validation error")
            
            return Mock(content="Success after retries")
        
        with patch("mirascope.llm.call", side_effect=mock_response):
            result = await func_with_retry("test input")
            
            assert call_count == mock_failure_count + 1
            assert result.content == "Success after retries"

    @pytest.mark.asyncio
    async def test_validation_error_handling(
        self,
        func_with_response_model: Callable,
        invalid_response_data: dict[str, Any]
    ):
        """Test handling of Pydantic validation errors.
        
        Args:
            func_with_response_model: Function with response_model
            invalid_response_data: Data that should fail validation
        """
        mock_response = Mock()
        mock_response.parsed = invalid_response_data
        
        with patch("mirascope.llm.call", return_value=mock_response):
            with pytest.raises(ValidationError) as exc_info:
                await func_with_response_model("test input")
            
            assert "validation error" in str(exc_info.value).lower()

    def test_tool_error_handling(
        self,
        agent_with_tools: Callable,
        tool_error: Exception
    ):
        """Test agent behavior when tools fail.
        
        Args:
            agent_with_tools: Agent that uses tools
            tool_error: Exception to raise from tool
        """
        # Mock the tool to raise an error
        with patch("tool_function", side_effect=tool_error):
            # Agent should handle tool errors gracefully
            result = agent_with_tools("test query")
            
            # Check that error is handled
            assert "error" in result.lower() or hasattr(result, "error")


# Pytest fixtures for Mirascope testing
@pytest.fixture
def mock_mirascope_response():
    """Create a mock Mirascope response."""
    def _create_response(
        content: str = "Mock response",
        provider: str = "openai",
        model: str = "gpt-4",
        **kwargs
    ):
        response = Mock()
        response.content = content
        response.provider = provider
        response.model = model
        
        for key, value in kwargs.items():
            setattr(response, key, value)
        
        return response
    
    return _create_response


@pytest.fixture
def mock_structured_response():
    """Create a mock structured response with Pydantic model."""
    def _create_response(
        model_class: type[BaseModel],
        data: dict[str, Any] | None = None
    ):
        if data:
            return model_class(**data)
        return MirascopeMockFactory._generate_mock_model(model_class)
    
    return _create_response


@pytest.fixture
def assert_mirascope_best_practices():
    """Fixture that provides assertions for Mirascope best practices."""
    return MirascopeTestHelper
