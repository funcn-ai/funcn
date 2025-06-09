"""Mock factories for LLM providers used in Mirascope."""

import asyncio
from pydantic import BaseModel
from typing import Any
from unittest.mock import AsyncMock, Mock, patch


class MockLLMResponse(Mock):
    """Base mock LLM response class."""

    def __init__(
        self,
        content: str = "Mock response",
        tool_calls: list[dict[str, Any]] | None = None,
        model: str = "mock-model",
        usage: dict[str, int] | None = None,
        finish_reason: str = "stop",
        response_model: type[BaseModel] | None = None,
        parsed_data: BaseModel | None = None,
        **kwargs
    ):
        super().__init__()
        self.content = content
        self.tool_calls = tool_calls or []
        self.model = model
        self.usage = usage or {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        self.finish_reason = finish_reason

        # For structured outputs
        if response_model and parsed_data:
            self.parsed = parsed_data
        elif response_model:
            # Auto-generate mock data for the model
            self.parsed = self._generate_mock_model_instance(response_model)
        
        # Allow additional attributes to be set
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _generate_mock_model_instance(self, model_class: type[BaseModel]) -> BaseModel:
        """Generate a mock instance of a Pydantic model."""
        mock_data: dict[str, Any] = {}

        for field_name, field_info in model_class.model_fields.items():
            field_type = field_info.annotation

            # Generate appropriate mock values
            if field_type is str:
                mock_data[field_name] = f"mock_{field_name}"
            elif field_type is int:
                mock_data[field_name] = 42
            elif field_type is float:
                mock_data[field_name] = 0.95
            elif field_type is bool:
                mock_data[field_name] = True
            elif field_type is not None and hasattr(field_type, "__origin__"):
                origin = field_type.__origin__
                if origin is list:
                    mock_data[field_name] = []
                elif origin is dict:
                    mock_data[field_name] = {}
                elif origin is type(None) or (field_type is not None and hasattr(field_type, "__args__") and type(None) in field_type.__args__):
                    # Handle Optional types
                    if not field_info.is_required():
                        mock_data[field_name] = None
                    else:
                        # Get the non-None type from Optional[T]
                        args = getattr(field_type, "__args__", ())
                        for arg in args:
                            if arg is not type(None):
                                if arg is str:
                                    mock_data[field_name] = f"mock_{field_name}"
                                elif arg is int:
                                    mock_data[field_name] = 42
                                elif arg is float:
                                    mock_data[field_name] = 0.95
                                elif arg is bool:
                                    mock_data[field_name] = True
                                else:
                                    mock_data[field_name] = f"mock_{field_name}"
                                break
                        else:
                            mock_data[field_name] = None
                else:
                    mock_data[field_name] = {}
            else:
                # For complex types, use None if optional
                if not field_info.is_required():
                    mock_data[field_name] = None
                else:
                    # Try to instantiate with empty args
                    try:
                        if field_type is not None and callable(field_type):
                            mock_data[field_name] = field_type()
                        else:
                            mock_data[field_name] = f"mock_{field_name}"
                    except Exception:
                        mock_data[field_name] = f"mock_{field_name}"

        return model_class(**mock_data)


class MockToolCall:
    """Mock tool call for LLM responses."""

    def __init__(self, function_name: str, arguments: dict[str, Any]):
        self.function = Mock()
        self.function.name = function_name
        self.function.arguments = arguments
        self.id = f"call_{function_name}_123"

    def call(self):
        """Simulate calling the tool."""
        # Return mock tool result
        return f"Result from {self.function.name}"


class LLMMockFactory:
    """Factory for creating mocks for different LLM providers."""

    @staticmethod
    def create_openai_mock(content: str = "Mock OpenAI response", model: str = "gpt-4", **kwargs) -> Mock:
        """Create a mock for OpenAI responses."""
        response = MockLLMResponse(content=content, model=model, **kwargs)

        # Add OpenAI-specific attributes
        response.choices = [
            Mock(message=Mock(content=content, tool_calls=response.tool_calls), finish_reason=response.finish_reason)
        ]

        return response  # type: ignore[return-value]

    @staticmethod
    def create_anthropic_mock(content: str = "Mock Anthropic response", model: str = "claude-3-opus-20240229", **kwargs) -> Mock:
        """Create a mock for Anthropic responses."""
        response = MockLLMResponse(content=content, model=model, **kwargs)

        # Add Anthropic-specific attributes
        response.stop_reason = response.finish_reason
        response.stop_sequence = None

        return response  # type: ignore[return-value]

    @staticmethod
    def create_google_mock(content: str = "Mock Google response", model: str = "gemini-pro", **kwargs) -> Mock:
        """Create a mock for Google Gemini responses."""
        response = MockLLMResponse(content=content, model=model, **kwargs)

        # Add Google-specific attributes
        response.candidates = [Mock(content=Mock(parts=[Mock(text=content)]), finish_reason=response.finish_reason)]

        return response  # type: ignore[return-value]

    @staticmethod
    def create_mistral_mock(content: str = "Mock Mistral response", model: str = "mistral-large", **kwargs) -> Mock:
        """Create a mock for Mistral responses."""
        response = MockLLMResponse(content=content, model=model, **kwargs)

        # Add Mistral-specific attributes
        response.choices = [
            Mock(message=Mock(content=content, tool_calls=response.tool_calls), finish_reason=response.finish_reason)
        ]

        return response  # type: ignore[return-value]

    @staticmethod
    def create_groq_mock(content: str = "Mock Groq response", model: str = "mixtral-8x7b-32768", **kwargs) -> Mock:
        """Create a mock for Groq responses."""
        response = MockLLMResponse(content=content, model=model, **kwargs)

        # Add Groq-specific attributes (similar to OpenAI)
        response.choices = [
            Mock(message=Mock(content=content, tool_calls=response.tool_calls), finish_reason=response.finish_reason)
        ]

        return response  # type: ignore[return-value]

    @staticmethod
    def create_cohere_mock(content: str = "Mock Cohere response", model: str = "command", **kwargs) -> Mock:
        """Create a mock for Cohere responses."""
        response = MockLLMResponse(content=content, model=model, **kwargs)

        # Add Cohere-specific attributes
        response.text = content
        response.generation_id = "mock-generation-123"

        return response  # type: ignore[return-value]

    @staticmethod
    def create_litellm_mock(content: str = "Mock LiteLLM response", model: str = "gpt-3.5-turbo", **kwargs) -> Mock:
        """Create a mock for LiteLLM responses."""
        # LiteLLM wraps other providers, so it follows OpenAI format
        response = MockLLMResponse(content=content, model=model, **kwargs)

        response.choices = [
            Mock(message=Mock(content=content, tool_calls=response.tool_calls), finish_reason=response.finish_reason)
        ]

        return response  # type: ignore[return-value]

    @staticmethod
    def create_mock_for_provider(provider: str, content: str = None, **kwargs) -> Mock:
        """Create a mock response for any provider.

        Args:
            provider: The provider name (openai, anthropic, google, etc.)
            content: The response content
            **kwargs: Additional provider-specific arguments

        Returns:
            Mock response object
        """
        provider_lower = provider.lower()

        if content is None:
            content = f"Mock {provider} response"

        mock_creators = {
            "openai": LLMMockFactory.create_openai_mock,
            "anthropic": LLMMockFactory.create_anthropic_mock,
            "google": LLMMockFactory.create_google_mock,
            "gemini": LLMMockFactory.create_google_mock,
            "mistral": LLMMockFactory.create_mistral_mock,
            "groq": LLMMockFactory.create_groq_mock,
            "cohere": LLMMockFactory.create_cohere_mock,
            "litellm": LLMMockFactory.create_litellm_mock,
        }

        creator = mock_creators.get(provider_lower, LLMMockFactory.create_openai_mock)
        return creator(content=content, **kwargs)

    @staticmethod
    def create_streaming_mock(provider: str, chunks: list[str], model: str = None) -> AsyncMock:
        """Create a mock for streaming responses.

        Args:
            provider: The provider name
            chunks: List of text chunks to stream
            model: Model name

        Returns:
            AsyncMock that yields chunks
        """

        async def async_generator():
            for chunk in chunks:
                if provider.lower() in ["openai", "groq", "mistral", "litellm"]:
                    # OpenAI-style chunks
                    yield Mock(choices=[Mock(delta=Mock(content=chunk))], model=model or "mock-model")
                elif provider.lower() == "anthropic":
                    # Anthropic-style chunks
                    yield Mock(delta=Mock(text=chunk), model=model or "claude-3-opus-20240229")
                elif provider.lower() in ["google", "gemini"]:
                    # Google-style chunks
                    yield Mock(text=chunk, model=model or "gemini-pro")
                else:
                    # Generic chunk
                    yield Mock(content=chunk)

        return async_generator()

    @staticmethod
    def create_tool_use_mock(
        provider: str, tool_name: str, tool_args: dict[str, Any], tool_result: Any = "Mock tool result"
    ) -> Mock:
        """Create a mock response that includes tool usage.

        Args:
            provider: The provider name
            tool_name: Name of the tool to call
            tool_args: Arguments for the tool
            tool_result: Result to return when tool is called

        Returns:
            Mock response with tool calls
        """
        tool_call = MockToolCall(tool_name, tool_args)
        # Create a mock for the call method
        mock_call = Mock(return_value=tool_result)
        # Replace the method with a mock
        object.__setattr__(tool_call, 'call', mock_call)

        return LLMMockFactory.create_mock_for_provider(provider, content="", tool_calls=[tool_call])


def mock_llm_decorator(provider: str, model: str = None):
    """Decorator to mock LLM calls for a specific provider.

    Usage:
        @mock_llm_decorator("openai")
        async def test_my_agent():
            # LLM calls will be mocked
            result = await my_agent("test")
    """

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            # Patch the provider's call method
            patch_path = f"mirascope.{provider}.{provider}.call"

            with patch(patch_path) as mock_call:
                # Create a mock that returns our mock response
                mock_response = LLMMockFactory.create_mock_for_provider(provider)

                if asyncio.iscoroutinefunction(test_func):
                    mock_call.return_value = AsyncMock(return_value=mock_response)
                else:
                    mock_call.return_value = Mock(return_value=mock_response)

                # Pass the mock to the test function
                kwargs["mock_llm"] = mock_call
                return test_func(*args, **kwargs)

        return wrapper

    return decorator


# Convenience functions for common mocking scenarios
def mock_successful_response(provider: str, content: str = None) -> Mock:
    """Create a successful LLM response mock."""
    return LLMMockFactory.create_mock_for_provider(provider, content=content)


def mock_error_response(provider: str, error_message: str = "API Error") -> Exception:
    """Create an LLM error mock."""
    provider_errors = {
        "openai": "OpenAIError",
        "anthropic": "AnthropicError",
        "google": "GoogleAPIError",
        "mistral": "MistralAPIError",
        "groq": "GroqError",
        "cohere": "CohereError",
    }

    error_class = provider_errors.get(provider.lower(), "Exception")
    return type(error_class, (Exception,), {})(error_message)


def mock_rate_limit_response(provider: str) -> Exception:
    """Create a rate limit error mock."""
    return mock_error_response(provider, "Rate limit exceeded")


def mock_timeout_response(provider: str) -> Exception:
    """Create a timeout error mock."""
    return mock_error_response(provider, "Request timeout")
