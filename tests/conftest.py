"""Global pytest configuration and fixtures for funcn tests."""

import asyncio
import json
import pytest
import shutil
import tempfile
from funcn_cli.config_manager import ConfigManager
from funcn_cli.core.models import Author, ComponentManifest, FileMapping
from pathlib import Path
from typer.testing import CliRunner
from typing import Any
from unittest.mock import AsyncMock, Mock, patch


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def tmp_project_dir(tmp_path):
    """Create a temporary project directory with basic structure."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create basic project structure
    (project_dir / "src").mkdir()
    (project_dir / "src" / "agents").mkdir()
    (project_dir / "src" / "tools").mkdir()
    (project_dir / "src" / "prompts").mkdir()

    # Create a basic funcn.json
    funcn_config = {
        "directories": {
            "agents": "src/agents",
            "tools": "src/tools",
            "prompt_templates": "src/prompts",
            "response_models": "src/models",
            "evals": "src/evals",
        },
        "provider": "openai",
        "model": "gpt-4",
    }

    with open(project_dir / "funcn.json", "w") as f:
        json.dump(funcn_config, f, indent=2)

    return project_dir


@pytest.fixture
def funcn_config():
    """Create a sample funcn configuration dict."""
    return {
        "directories": {
            "agents": "src/agents",
            "tools": "src/tools",
            "prompt_templates": "src/prompts",
            "response_models": "src/models",
            "evals": "src/evals",
        },
        "provider": "openai",
        "model": "gpt-4",
    }


@pytest.fixture
def sample_component():
    """Create a sample ComponentManifest instance for testing."""
    return ComponentManifest(
        name="test-agent",
        type="agent",
        version="0.1.0",
        description="A test agent for unit testing",
        authors=[Author(name="Test Author", email="test@example.com")],
        license="MIT",
        mirascope_version_min="1.24.0",
        files_to_copy=[
            FileMapping(source="agent.py", destination="agent.py"),
            FileMapping(source="funcn.md", destination="funcn.md"),
        ],
        target_directory_key="agents",
        python_dependencies=["mirascope>=1.24.0", "pydantic>=2.0.0"],
        registry_dependencies=[],
        environment_variables=[],
        post_add_instructions="Test agent installed successfully!",
        tags=["test", "sample"],
        supports_lilypad=True,
        template_variables={"provider": "openai", "model": "gpt-4"},
    )


@pytest.fixture
def sample_tool_component():
    """Create a sample tool ComponentManifest instance for testing."""
    return ComponentManifest(
        name="test-tool",
        type="tool",
        version="0.1.0",
        description="A test tool for unit testing",
        authors=[Author(name="Test Author", email="test@example.com")],
        license="MIT",
        mirascope_version_min="1.24.0",
        files_to_copy=[
            FileMapping(source="tool.py", destination="tool.py"),
            FileMapping(source="funcn.md", destination="funcn.md"),
        ],
        target_directory_key="tools",
        python_dependencies=["requests>=2.0.0"],
        registry_dependencies=[],
        environment_variables=[],
        post_add_instructions="Test tool installed successfully!",
        tags=["test", "sample", "tool"],
        supports_lilypad=False,
        template_variables={},
    )


@pytest.fixture
def mock_registry_response(sample_component):
    """Mock HTTP response for registry API."""
    return {
        "components": [
            {
                "name": sample_component.name,
                "type": sample_component.type,
                "version": sample_component.version,
                "description": sample_component.description,
                "dependencies": sample_component.dependencies,
                "author": sample_component.author,
                "tags": sample_component.tags,
                "mirascope_providers": sample_component.mirascope_providers,
            }
        ]
    }


@pytest.fixture
def cli_runner():
    """Create a CliRunner instance for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for testing registry interactions."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def config_manager(tmp_project_dir):
    """Create a ConfigManager instance with a temporary project directory."""
    with patch("funcn_cli.config_manager.Path.cwd", return_value=tmp_project_dir):
        return ConfigManager()


@pytest.fixture
def sample_component_files(tmp_path):
    """Create sample component files in a temporary directory."""
    component_dir = tmp_path / "test_agent"
    component_dir.mkdir()

    # Create component.json
    component_json = {
        "name": "test_agent",
        "type": "agent",
        "version": "0.1.0",
        "description": "A test agent",
        "dependencies": ["mirascope"],
        "config": {
            "min_python_version": "3.12",
            "dependencies": [{"name": "mirascope", "version": ">=1.0.0"}],
            "files": [{"src": "agent.py", "dest": "agent.py"}, {"src": "funcn.md", "dest": "funcn.md"}],
            "template_variables": ["provider", "model"],
        },
    }

    with open(component_dir / "component.json", "w") as f:
        json.dump(component_json, f, indent=2)

    # Create agent.py
    agent_code = '''"""Test agent implementation."""

from mirascope.core import Messages, prompt_template
from mirascope.{{provider}} import {{provider}}.call
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Response model for the test agent."""

    result: str
    confidence: float


@{{provider}}.call(model="{{model}}", response_model=AgentResponse)
@prompt_template()
async def test_agent(query: str) -> Messages.Type:
    """A test agent that processes queries.

    Args:
        query: The input query to process

    Returns:
        AgentResponse with result and confidence
    """
    return Messages.User(f"Process this query: {query}")
'''

    with open(component_dir / "agent.py", "w") as f:
        f.write(agent_code)

    # Create funcn.md
    funcn_md = """# Test Agent

A simple test agent for unit testing.

## Usage

```python
from agents.test_agent import test_agent

result = await test_agent("Hello world")
print(result.result)
```
"""

    with open(component_dir / "funcn.md", "w") as f:
        f.write(funcn_md)

    return component_dir


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response for testing agents."""

    class MockResponse:
        def __init__(self, content):
            self.content = content
            self.tool_calls = []
            self.usage = {"total_tokens": 100}

    return MockResponse


@pytest.fixture
def async_mock():
    """Helper to create async mock objects."""
    return AsyncMock


# Markers for test organization
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "benchmark: Performance benchmark tests")
    config.addinivalue_line("markers", "slow: Tests that take a long time to run")
    config.addinivalue_line("markers", "requires_api_key: Tests that require API keys")
