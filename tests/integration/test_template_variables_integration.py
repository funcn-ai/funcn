"""Integration tests for template variable substitution functionality."""

from __future__ import annotations

import json
import pytest
import tempfile
from pathlib import Path
from sygaldry_cli.config_manager import ConfigManager
from sygaldry_cli.core.component_manager import ComponentManager
from sygaldry_cli.core.models import Author, ComponentManifest, FileMapping, TemplateVariable


@pytest.mark.integration
class TestTemplateVariablesIntegration:
    """Integration tests for template variable substitution."""

    @pytest.fixture
    def temp_component_dir(self):
        """Create a temporary directory with a sample component."""
        with tempfile.TemporaryDirectory() as temp_dir:
            component_dir = Path(temp_dir) / "test-component"
            component_dir.mkdir()

            # Create component files with template variables
            agent_py = component_dir / "agent.py"
            agent_py.write_text("""from mirascope import llm
import logging

# Template variable substitutions
API_TIMEOUT = {{api_timeout}}
ENABLE_LOGGING = {{enable_logging}}
SERVICE_NAME = "{{service_name|upper}}"

if ENABLE_LOGGING:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

class {{component_class_name}}:
    '''{{component_description}}'''

    def __init__(self):
        self.timeout = API_TIMEOUT
        self.service = SERVICE_NAME
        if ENABLE_LOGGING:
            logger.info(f"Initialized {{component_class_name}} with timeout={API_TIMEOUT}")

    @llm.call(provider="{{provider}}", model="{{model}}")
    def process(self, question: str) -> str:
        return f"Processing question: {question}"

# Export the component
{{component_class_name|lower}}_instance = {{component_class_name}}()
""")

            init_py = component_dir / "__init__.py"
            init_py.write_text("""from .agent import {{component_class_name|lower}}_instance

__all__ = ["{{component_class_name|lower}}_instance"]
""")

            # Create component manifest
            manifest = ComponentManifest(
                name="test-component",
                version="1.0.0",
                type="agent",
                description="Test component with template variables",
                authors=[Author(name="Test Author", email="test@example.com")],
                license="MIT",
                mirascope_version_min="0.1.0",
                files_to_copy=[
                    FileMapping(source="agent.py", destination="agent.py"),
                    FileMapping(source="__init__.py", destination="__init__.py")
                ],
                target_directory_key="agents",
                python_dependencies=[],
                registry_dependencies=[],
                environment_variables=[],
                tags=["test"],
                template_variables=[
                    TemplateVariable(
                        name="component_class_name",
                        description="Class name for the component",
                        default="TemplateAgent"
                    ),
                    TemplateVariable(
                        name="component_description",
                        description="Description of the component",
                        default="A template-based agent component"
                    ),
                    TemplateVariable(
                        name="api_timeout",
                        description="API timeout in seconds",
                        default="30"
                    ),
                    TemplateVariable(
                        name="enable_logging",
                        description="Enable debug logging",
                        default="True"
                    ),
                    TemplateVariable(
                        name="service_name",
                        description="Service name for the component",
                        default="template_service"
                    ),
                    TemplateVariable(
                        name="provider",
                        description="LLM provider",
                        default="openai"
                    ),
                    TemplateVariable(
                        name="model",
                        description="LLM model",
                        default="gpt-4o-mini"
                    )
                ]
            )

            manifest_path = component_dir / "component.json"
            manifest_path.write_text(manifest.model_dump_json(indent=2))

            yield component_dir

    @pytest.fixture
    def component_manager(self, tmp_path):
        """Create a ComponentManager instance with test directory."""
        test_project_dir = tmp_path / "test_project"
        test_project_dir.mkdir()
        (test_project_dir / "src").mkdir()
        (test_project_dir / "src" / "agents").mkdir()

        # Create ConfigManager with the test project directory
        config = ConfigManager(project_root=test_project_dir)
        return ComponentManager(cfg=config)

    def test_template_substitution_with_defaults(self, component_manager, temp_component_dir):
        """Test template variable substitution using default values."""
        # Copy component files to destination
        dest_dir = component_manager._cfg.project_root / "src" / "agents" / "test-component"
        dest_dir.mkdir(parents=True)

        # Copy files
        for file in ["agent.py", "__init__.py"]:
            src_file = temp_component_dir / file
            dest_file = dest_dir / file
            dest_file.write_text(src_file.read_text())

        # Apply template substitution with default values
        variables = {
            "component_class_name": "TemplateAgent",
            "component_description": "A template-based agent component",
            "api_timeout": "30",
            "enable_logging": "True",
            "service_name": "template_service",
            "provider": "openai",
            "model": "gpt-4o-mini"
        }

        # Render templates
        ComponentManager._render_template(dest_dir / "agent.py", variables, enable_lilypad=False)
        ComponentManager._render_template(dest_dir / "__init__.py", variables, enable_lilypad=False)

        # Verify substitutions in agent.py
        agent_content = (dest_dir / "agent.py").read_text()
        assert "API_TIMEOUT = 30" in agent_content
        assert "ENABLE_LOGGING = True" in agent_content
        assert 'SERVICE_NAME = "TEMPLATE_SERVICE"' in agent_content  # |upper transformation
        assert "class TemplateAgent:" in agent_content
        assert "'A template-based agent component'" in agent_content
        assert 'logger.info(f"Initialized TemplateAgent with timeout={API_TIMEOUT}")' in agent_content
        assert '@llm.call(provider="openai", model="gpt-4o-mini")' in agent_content
        assert "templateagent_instance = TemplateAgent()" in agent_content  # |lower transformation

        # Verify substitutions in __init__.py
        init_content = (dest_dir / "__init__.py").read_text()
        assert "from .agent import templateagent_instance" in init_content
        assert '__all__ = ["templateagent_instance"]' in init_content

    def test_template_substitution_with_custom_values(self, component_manager, temp_component_dir):
        """Test template variable substitution with custom values."""
        # Copy component files to destination
        dest_dir = component_manager._cfg.project_root / "src" / "agents" / "test_component"
        dest_dir.mkdir(parents=True)

        # Copy files
        for file in ["agent.py", "__init__.py"]:
            src_file = temp_component_dir / file
            dest_file = dest_dir / file
            dest_file.write_text(src_file.read_text())

        # Apply template substitution with custom values
        variables = {
            "component_class_name": "MyCustomAgent",
            "component_description": "A custom AI agent for processing",
            "api_timeout": "60",
            "enable_logging": "False",
            "service_name": "my_custom_service",
            "provider": "anthropic",
            "model": "claude-3-opus-20240229"
        }

        # Render templates
        component_manager._render_template(dest_dir / "agent.py", variables, enable_lilypad=False)
        component_manager._render_template(dest_dir / "__init__.py", variables, enable_lilypad=False)

        # Verify substitutions in agent.py
        agent_content = (dest_dir / "agent.py").read_text()
        assert "API_TIMEOUT = 60" in agent_content
        assert "ENABLE_LOGGING = False" in agent_content
        assert 'SERVICE_NAME = "MY_CUSTOM_SERVICE"' in agent_content  # |upper transformation
        assert "class MyCustomAgent:" in agent_content
        assert "'A custom AI agent for processing'" in agent_content
        assert 'logger.info(f"Initialized MyCustomAgent with timeout={API_TIMEOUT}")' in agent_content
        assert '@llm.call(provider="anthropic", model="claude-3-opus-20240229")' in agent_content
        assert "mycustomagent_instance = MyCustomAgent()" in agent_content  # |lower transformation

        # Verify substitutions in __init__.py
        init_content = (dest_dir / "__init__.py").read_text()
        assert "from .agent import mycustomagent_instance" in init_content
        assert '__all__ = ["mycustomagent_instance"]' in init_content

    def test_template_case_transformations(self, component_manager, tmp_path):
        """Test template variable case transformations (upper, lower, title)."""
        # Create test file with case transformations
        test_file = tmp_path / "test_case.py"
        test_file.write_text("""
# Test case transformations
CONSTANT_NAME = "{{service_name|upper}}"
module_name = "{{service_name|lower}}"
ClassTitle = "{{service_name|title}}"

# Mixed case handling
snake_case_var = "{{snake_case_name|title}}"
camelCaseVar = "{{camel_case_name|title}}"
kebab_case_var = "{{kebab-case-name|title}}"
""")

        variables = {
            "service_name": "My_Custom_Service",
            "snake_case_name": "my_snake_case_var",
            "camel_case_name": "myCamelCaseVar",
            "kebab-case-name": "my-kebab-case-var"
        }

        ComponentManager._render_template(test_file, variables, enable_lilypad=False)

        content = test_file.read_text()
        assert 'CONSTANT_NAME = "MY_CUSTOM_SERVICE"' in content  # |upper
        assert 'module_name = "my_custom_service"' in content  # |lower
        assert 'ClassTitle = "MyCustomService"' in content  # |title removes underscores

        # Title case handling - the implementation replaces underscores/hyphens with spaces, capitalizes, then joins
        assert 'snake_case_var = "MySnakeCaseVar"' in content
        assert 'camelCaseVar = "Mycamelcasevar"' in content  # Title case doesn't handle camelCase perfectly
        assert 'kebab_case_var = "MyKebabCaseVar"' in content

    def test_missing_template_variables(self, component_manager, tmp_path):
        """Test behavior when template variables are not provided."""
        # Create test file with undefined variables
        test_file = tmp_path / "test_missing.py"
        test_file.write_text("""
# These variables are not defined
UNDEFINED = "{{undefined_var}}"
ANOTHER = "{{another_undefined|upper}}"
""")

        # Render with empty variables dict
        component_manager._render_template(test_file, {}, enable_lilypad=False)

        # Undefined variables should remain unchanged
        content = test_file.read_text()
        assert 'UNDEFINED = "{{undefined_var}}"' in content
        assert 'ANOTHER = "{{another_undefined|upper}}"' in content

    def test_lilypad_integration_placeholders(self, component_manager, tmp_path):
        """Test Lilypad integration placeholder handling."""
        # Create test file with Lilypad decorators
        test_file = tmp_path / "test_lilypad.py"
        test_file.write_text("""
from lilypad import lilypad_observe

@lilypad_observe
@llm.call(provider="{{provider}}", model="{{model}}")
def my_function():
    pass

@lilypad_observe(name="custom_span")
def another_function():
    pass
""")

        variables = {
            "provider": "openai",
            "model": "gpt-4"
        }

        # Test with Lilypad enabled
        ComponentManager._render_template(test_file, variables, enable_lilypad=True)

        content = test_file.read_text()
        assert "from lilypad import lilypad_observe" in content
        assert "@lilypad_observe" in content
        assert '@llm.call(provider="openai", model="gpt-4")' in content

        # Test with Lilypad disabled using SYGALDRY placeholders
        test_file.write_text("""
# SYGALDRY_LILYPAD_IMPORT_PLACEHOLDER

# SYGALDRY_LILYPAD_DECORATOR_PLACEHOLDER
@llm.call(provider="{{provider}}", model="{{model}}")
def my_function():
    pass
""")

        ComponentManager._render_template(test_file, variables, enable_lilypad=False)

        content = test_file.read_text()
        # Placeholders should be removed when Lilypad is disabled
        assert "# SYGALDRY_LILYPAD_IMPORT_PLACEHOLDER" not in content
        assert "# SYGALDRY_LILYPAD_DECORATOR_PLACEHOLDER" not in content
        assert "import lilypad" not in content
        assert '@llm.call(provider="openai", model="gpt-4")' in content

    def test_complex_template_substitution(self, component_manager, tmp_path):
        """Test complex template substitution scenarios."""
        # Create test file with nested and complex templates
        test_file = tmp_path / "test_complex.py"
        test_file.write_text("""
class {{class_name}}Config:
    '''Configuration for {{class_name|title}}'''

    def __init__(self):
        self.name = "{{class_name|lower}}_config"
        self.display_name = "{{class_name|title}} Configuration"
        self.env_var = "{{class_name|upper}}_CONFIG"

    def get_{{method_prefix|lower}}_endpoint(self):
        return "https://api.example.com/{{api_version}}/{{class_name|lower}}"

    def is_{{feature_flag|lower}}_enabled(self):
        return {{feature_enabled}}

# Multiple transformations on same line
logger.info(f"{{class_name|title}} ({{class_name|upper}}) initialized as {{class_name|lower}}")
""")

        variables = {
            "class_name": "neural_network",
            "method_prefix": "API",
            "api_version": "v2",
            "feature_flag": "AutoScaling",
            "feature_enabled": "True"
        }

        ComponentManager._render_template(test_file, variables, enable_lilypad=False)

        content = test_file.read_text()

        # Verify all substitutions
        assert "class neural_networkConfig:" in content
        assert "'Configuration for NeuralNetwork'" in content
        assert 'self.name = "neural_network_config"' in content
        assert 'self.display_name = "NeuralNetwork Configuration"' in content
        assert 'self.env_var = "NEURAL_NETWORK_CONFIG"' in content
        assert "def get_api_endpoint(self):" in content
        assert 'return "https://api.example.com/v2/neural_network"' in content
        assert "def is_autoscaling_enabled(self):" in content
        assert "return True" in content
        assert 'logger.info(f"NeuralNetwork (NEURAL_NETWORK) initialized as neural_network")' in content
