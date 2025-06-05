"""Base test classes for testing funcn components (agents and tools)."""

import asyncio
import inspect
import json
import pytest
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Type
from unittest.mock import AsyncMock, Mock, patch


class BaseComponentTest(ABC):
    """Base class for testing funcn components."""

    # Override these in subclasses
    component_type: str | None = None  # "agent" or "tool"
    component_name: str | None = None
    component_path: Path | None = None

    @abstractmethod
    def get_component_function(self) -> Callable:
        """Get the main function/class to test.

        Returns:
            The component's main callable
        """
        pass

    @abstractmethod
    def get_test_inputs(self) -> list[dict[str, Any]]:
        """Get test input cases.

        Returns:
            List of test input dictionaries
        """
        pass

    def setup_method(self, method):
        """Set up test method."""
        self.mocks = {}

    def teardown_method(self, method):
        """Clean up after test method."""
        for mock in self.mocks.values():
            if hasattr(mock, "stop"):
                mock.stop()

    def test_component_metadata_exists(self):
        """Test that component.json exists and is valid."""
        component_json_path = self.component_path / "component.json"
        assert component_json_path.exists(), f"component.json not found at {component_json_path}"

        with open(component_json_path) as f:
            metadata = json.load(f)

        # Validate required fields
        assert metadata.get("name") == self.component_name
        assert metadata.get("type") == self.component_type
        assert "version" in metadata
        assert "description" in metadata
        assert "config" in metadata

    def test_component_documentation_exists(self):
        """Test that funcn.md documentation exists."""
        funcn_md_path = self.component_path / "funcn.md"
        assert funcn_md_path.exists(), f"funcn.md not found at {funcn_md_path}"

        content = funcn_md_path.read_text()
        assert len(content) > 50, "funcn.md appears to be empty or too short"
        assert "## Usage" in content or "## Example" in content, "funcn.md should contain usage examples"

    def test_component_imports(self):
        """Test that the component can be imported successfully."""
        try:
            component = self.get_component_function()
            assert component is not None
            assert callable(component)
        except ImportError as e:
            pytest.fail(f"Failed to import component: {e}")

    def test_component_signature(self):
        """Test that the component has proper type hints."""
        component = self.get_component_function()
        sig = inspect.signature(component)

        # Check that parameters have type hints
        for param_name, param in sig.parameters.items():
            if param_name not in ("self", "cls"):
                assert param.annotation != inspect.Parameter.empty, f"Parameter '{param_name}' lacks type annotation"

        # Check return type annotation exists
        assert sig.return_annotation != inspect.Signature.empty, "Component function lacks return type annotation"


class BaseAgentTest(BaseComponentTest):
    """Base class for testing agents."""

    component_type = "agent"

    # Override these in subclasses
    mock_llm_provider: str = "openai"  # Provider to mock
    mock_model: str = "gpt-4"  # Model to mock

    def get_mock_llm_response(self, content: str, tool_calls: list | None = None) -> Any:
        """Create a mock LLM response.

        Args:
            content: The text content of the response
            tool_calls: Optional list of tool calls

        Returns:
            Mock response object
        """
        response = Mock()
        response.content = content
        response.tool_calls = tool_calls or []
        response.usage = {"total_tokens": 100}
        response.model = self.mock_model
        return response

    @pytest.mark.asyncio
    async def test_agent_basic_functionality(self):
        """Test basic agent functionality with mocked LLM."""
        agent_func = self.get_component_function()
        test_inputs = self.get_test_inputs()

        if not test_inputs:
            pytest.skip("No test inputs provided")

        # Test with first input case
        test_input = test_inputs[0]

        # Mock the LLM call
        mock_response = self.get_mock_llm_response("Test response")

        # Mock the @llm.call decorator behavior
        # The decorator wraps the function and handles the LLM call internally
        with patch("mirascope.llm.call") as mock_llm_call:
            # Mock the decorator to return a function that returns our response
            def mock_decorator(**kwargs):
                def decorator(func):
                    if asyncio.iscoroutinefunction(func):
                        async def wrapper(*args, **kw):
                            return mock_response
                        return wrapper
                    else:
                        def wrapper(*args, **kw):
                            return mock_response
                        return wrapper
                return decorator
            
            mock_llm_call.side_effect = mock_decorator
            
            # For already decorated functions, mock the underlying call
            if asyncio.iscoroutinefunction(agent_func):
                with patch.object(agent_func, "__wrapped__", return_value=mock_response):
                    result = await agent_func(**test_input)
            else:
                result = agent_func(**test_input)

        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_with_response_model(self):
        """Test agent with structured response model."""
        agent_func = self.get_component_function()

        # Check if agent uses response_model
        if hasattr(agent_func, "__wrapped__"):
            # Look for response_model in decorators
            func = agent_func
            while hasattr(func, "__wrapped__"):
                if hasattr(func, "_mirascope_call_kwargs"):
                    response_model = func._mirascope_call_kwargs.get("response_model")
                    if response_model and issubclass(response_model, BaseModel):
                        # Test with structured output
                        test_inputs = self.get_test_inputs()
                        if test_inputs:
                            # Create mock structured response
                            mock_data = self.get_mock_structured_response(response_model)
                            mock_response = Mock()
                            mock_response.parsed = mock_data

                            with patch(f"mirascope.{self.mock_llm_provider}.{self.mock_llm_provider}.call") as mock_call:
                                if asyncio.iscoroutinefunction(agent_func):
                                    mock_call.return_value = AsyncMock(return_value=mock_response)
                                    result = await agent_func(**test_inputs[0])
                                else:
                                    mock_call.return_value = Mock(return_value=mock_response)
                                    result = agent_func(**test_inputs[0])

                            assert isinstance(result, response_model)
                            return
                func = func.__wrapped__

    def get_mock_structured_response(self, model_class: type[BaseModel]) -> BaseModel:
        """Create a mock instance of a Pydantic model.

        Override this method to provide custom mock data for specific models.

        Args:
            model_class: The Pydantic model class

        Returns:
            Instance of the model with mock data
        """
        # Create a simple instance with default/mock values
        mock_data: dict[str, Any] = {}
        for field_name, field_info in model_class.model_fields.items():
            field_type = field_info.annotation

            # Provide basic mock values based on type
            if field_type == str:
                mock_data[field_name] = f"mock_{field_name}"
            elif field_type == int:
                mock_data[field_name] = 42
            elif field_type == float:
                mock_data[field_name] = 0.95
            elif field_type == bool:
                mock_data[field_name] = True
            elif field_type is not None and hasattr(field_type, '__origin__'):
                # Handle generic types like List[str], Dict[str, Any], etc.
                origin = field_type.__origin__
                if origin == list:
                    mock_data[field_name] = []
                elif origin == dict:
                    mock_data[field_name] = {}
                elif origin == Optional or origin == type(Optional[int]):
                    # Handle Optional types
                    if not field_info.is_required():
                        mock_data[field_name] = None
                    else:
                        # Get the actual type from Optional[T]
                        args = getattr(field_type, '__args__', ())
                        if args and args[0] == str:
                            mock_data[field_name] = f"mock_{field_name}"
                        elif args and args[0] == int:
                            mock_data[field_name] = 42
                        elif args and args[0] == float:
                            mock_data[field_name] = 0.95
                        else:
                            mock_data[field_name] = f"mock_{field_name}"
                else:
                    mock_data[field_name] = None
            else:
                # For complex types, try None if optional
                if not field_info.is_required():
                    mock_data[field_name] = None
                else:
                    # Provide a default string value for unknown required fields
                    mock_data[field_name] = f"mock_{field_name}"

        return model_class(**mock_data)

    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test agent error handling."""
        agent_func = self.get_component_function()
        test_inputs = self.get_test_inputs()

        if not test_inputs:
            pytest.skip("No test inputs provided")

        # Test with LLM error
        with patch(f"mirascope.{self.mock_llm_provider}.{self.mock_llm_provider}.call") as mock_call:
            mock_call.side_effect = Exception("LLM API Error")

            with pytest.raises(Exception) as exc_info:
                if asyncio.iscoroutinefunction(agent_func):
                    await agent_func(**test_inputs[0])
                else:
                    agent_func(**test_inputs[0])

            assert "LLM API Error" in str(exc_info.value)


class BaseToolTest(BaseComponentTest):
    """Base class for testing tools."""

    component_type = "tool"

    def test_tool_is_function_not_class(self):
        """Test that tools are implemented as functions, not classes."""
        tool_func = self.get_component_function()
        assert inspect.isfunction(tool_func) or inspect.iscoroutinefunction(tool_func), (
            "Tools should be implemented as functions, not classes"
        )

    @pytest.mark.asyncio
    async def test_tool_basic_functionality(self):
        """Test basic tool functionality."""
        tool_func = self.get_component_function()
        test_inputs = self.get_test_inputs()

        if not test_inputs:
            pytest.skip("No test inputs provided")

        # Test with first input case
        test_input = test_inputs[0]

        # Call the tool
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**test_input)
        else:
            result = tool_func(**test_input)

        assert result is not None
        self.validate_tool_output(result, test_input)

    def validate_tool_output(self, output: Any, input_data: dict[str, Any]):
        """Validate tool output. Override in subclasses for specific validation.

        Args:
            output: The tool's output
            input_data: The input that was provided to the tool
        """
        pass

    @pytest.mark.asyncio
    async def test_tool_with_invalid_inputs(self):
        """Test tool behavior with invalid inputs."""
        tool_func = self.get_component_function()

        # Get function signature to test with wrong types
        sig = inspect.signature(tool_func)
        params = sig.parameters

        if not params:
            pytest.skip("Tool has no parameters to test")

        # Create invalid input based on parameter types
        invalid_input = {}
        for param_name, param in params.items():
            if param.annotation == str:
                invalid_input[param_name] = 123  # Wrong type
            elif param.annotation == int:
                invalid_input[param_name] = "not a number"  # Wrong type
            elif param.annotation == list:
                invalid_input[param_name] = "not a list"  # Wrong type
            else:
                invalid_input[param_name] = None  # Potentially invalid

        # Tools should handle invalid inputs gracefully or raise clear errors
        try:
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**invalid_input)
            else:
                result = tool_func(**invalid_input)
        except (TypeError, ValueError) as e:
            # Expected behavior - tool validates inputs
            assert str(e), "Error message should not be empty"
        except Exception as e:
            # Unexpected error type
            pytest.fail(f"Unexpected error type: {type(e).__name__}: {e}")


class ComponentTestHelper:
    """Helper utilities for component testing."""

    @staticmethod
    def mock_external_api(url_pattern: str, response_data: Any, status_code: int = 200):
        """Create a mock for external API calls.

        Args:
            url_pattern: URL pattern to match
            response_data: Data to return
            status_code: HTTP status code

        Returns:
            Mock object
        """
        mock_response = Mock()
        mock_response.json.return_value = response_data
        mock_response.status_code = status_code
        mock_response.raise_for_status = Mock()

        if status_code >= 400:
            mock_response.raise_for_status.side_effect = Exception(f"HTTP {status_code}")

        return mock_response

    @staticmethod
    def create_mock_file(tmp_path: Path, filename: str, content: str) -> Path:
        """Create a mock file for testing.

        Args:
            tmp_path: Temporary directory path
            filename: Name of the file
            content: File content

        Returns:
            Path to created file
        """
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path

    @staticmethod
    async def assert_async_raises(exception_type: type[Exception], coro):
        """Assert that an async function raises a specific exception.

        Args:
            exception_type: Expected exception type
            coro: Coroutine to execute
        """
        with pytest.raises(exception_type):
            await coro
