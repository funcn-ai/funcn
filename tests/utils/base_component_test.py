"""Base test classes for funcn components."""

import json
import pytest
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock


class BaseComponentTest(ABC):
    """Base class for testing funcn components."""
    
    component_type: str | None = None  # "agent" or "tool"
    component_name: str | None = None
    component_path: Path | None = None
    
    @abstractmethod
    def get_component_function(self) -> Callable:
        """Get the main component function to test."""
        pass
    
    @abstractmethod
    def get_test_inputs(self) -> list[dict[str, Any]]:
        """Get test input cases for the component."""
        pass
    
    def test_component_json_exists(self):
        """Test that component.json exists."""
        assert self.component_path is not None
        component_json = self.component_path / "component.json"
        assert component_json.exists(), f"component.json not found at {component_json}"
        
    def test_component_json_valid(self):
        """Test that component.json is valid."""
        component_json = self.component_path / "component.json"
        with open(component_json) as f:
            data = json.load(f)
            
        # Check required fields
        assert "name" in data
        assert "description" in data
        assert "authors" in data  # Changed from author to authors
        assert "version" in data
        assert "type" in data
        
        # Check component name matches (without type suffix now)
        assert data["name"] == self.component_name
        
    def test_funcn_md_exists(self):
        """Test that funcn.md documentation exists."""
        funcn_md = self.component_path / "funcn.md"
        assert funcn_md.exists(), f"funcn.md not found at {funcn_md}"
        
    def test_component_has_type_hints(self):
        """Test that the component function has type hints."""
        func = self.get_component_function()
        assert func.__annotations__, f"{func.__name__} should have type hints"
        
    def test_component_has_docstring(self):
        """Test that the component function has a docstring."""
        func = self.get_component_function()
        assert func.__doc__ is not None
        assert len(func.__doc__) > 50, "Docstring should be descriptive"
        
    @abstractmethod
    def validate_component_output(self, output: Any, input_data: dict[str, Any]):
        """Validate the component output structure."""
        pass


class BaseAgentTest(BaseComponentTest):
    """Base class for testing agent components."""
    
    component_type = "agent"
    
    def validate_component_output(self, output: Any, input_data: dict[str, Any]):
        """Default validation for agent output."""
        # Agents typically return structured data or strings
        assert output is not None
        # Subclasses should override for specific validation
        self.validate_agent_output(output, input_data)
        
    @abstractmethod
    def validate_agent_output(self, output: Any, input_data: dict[str, Any]):
        """Validate agent-specific output."""
        pass
    
    @pytest.fixture
    def mock_llm_call(self):
        """Mock LLM calls for testing."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_mirascope_decorator(self):
        """Mock Mirascope decorators."""
        def decorator(*args, **kwargs):
            def wrapper(func):
                # Return the original function
                return func
            return wrapper
        return decorator


class BaseToolTest(BaseComponentTest):
    """Base class for testing tool components."""
    
    component_type = "tool"
    
    def validate_component_output(self, output: Any, input_data: dict[str, Any]):
        """Default validation for tool output."""
        # Tools typically return data structures
        assert output is not None
        # Subclasses should override for specific validation
        self.validate_tool_output(output, input_data)
        
    @abstractmethod  
    def validate_tool_output(self, output: Any, input_data: dict[str, Any]):
        """Validate tool-specific output."""
        pass
    
    @pytest.mark.asyncio
    async def test_tool_basic_functionality(self):
        """Test basic tool functionality with mock data."""
        func = self.get_component_function()
        test_inputs = self.get_test_inputs()
        
        if not test_inputs:
            pytest.skip("No test inputs provided")
            
        # Test first input case
        input_data = test_inputs[0]
        
        # Tools are typically sync functions
        if callable(func):
            # This is a placeholder - actual test would mock external dependencies
            # and verify the tool works correctly
            pass