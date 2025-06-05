"""Component type-specific templates for generating customized funcn.md documentation."""

from __future__ import annotations

# Agent-specific template
AGENT_TEMPLATE = """# {component_name}

> {description}

**Version**: {version} | **Type**: {type} | **License**: {license}
**Authors**: {authors} | **Repository**: {repository_url}

## Overview

{detailed_description}

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add {component_name}
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

{registry_dependencies}

**Python Dependencies:**

{python_dependencies}

**Environment Variables:**

{environment_variables}

### Basic Usage

{example_usage}

## Agent Configuration

### Template Variables

{template_variables}

### LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models
- **Groq**: Set `GROQ_API_KEY` for Groq models

Configure the provider and model using template variables or function parameters.

### Advanced Configuration

{advanced_configuration}

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with funcn tools for enhanced capabilities
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance{lilypad_support}

## Integration with Mirascope

This agent follows Mirascope best practices:

- Uses `@prompt_template` decorators for all prompts
- Implements Pydantic response models for structured outputs
- Supports async/await patterns for optimal performance
- Compatible with multiple LLM providers
- Includes comprehensive error handling{lilypad_support}

## API Reference

{api_reference}

## Advanced Examples

{advanced_examples}

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await {component_name}(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await {component_name}(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from {component_name} import {component_name}_custom

result = await {component_name}_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

{troubleshooting}

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add {component_name}` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes

{migration_notes}

---

**Key Benefits:**

{key_benefits}

**Related Components:**

{related_components}

**References:**

{references}
"""

# Tool-specific template
TOOL_TEMPLATE = """# {component_name}

> {description}

**Version**: {version} | **Type**: {type} | **License**: {license}
**Authors**: {authors} | **Repository**: {repository_url}

## Overview

{detailed_description}

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add {component_name}
```

### Dependencies

**Python Dependencies:**

{python_dependencies}

**Environment Variables:**

{environment_variables}

### Basic Usage

{example_usage}

## Tool Configuration

{template_variables}

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from {component_name} import ToolArgs, ToolResult

# Input model defines the expected parameters
args = ToolArgs(
    param1="value1",
    param2="value2"
)

# Output model provides structured results
result: ToolResult = await tool_function(args)
```

## Integration with Agents

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from {component_name} import tool_function

@llm.call(provider="openai", model="gpt-4o-mini", tools=[tool_function])
@prompt_template("Use the tool to help answer: {{query}}")
def agent_with_tool(query: str): ...

response = agent_with_tool("your question")
if response.tool:
    result = response.tool.call()
    print(result)
```

### Tool Chaining

```python
# Chain multiple tools together
from funcn_registry.tools import tool1, tool2

async def chained_workflow(input_data):
    result1 = await tool1(input_data)
    result2 = await tool2(result1.output)
    return result2
```

## API Reference

{api_reference}

### Function Signature

The main tool function follows this pattern:

```python
async def tool_function(args: ToolArgs) -> ToolResult:
    \"\"\"
    Tool description and usage.

    Args:
        args: Structured input parameters

    Returns:
        Structured result with typed fields

    Raises:
        ToolError: When operation fails
    \"\"\"
```

## Advanced Examples

{advanced_examples}

### Error Handling

```python
from {component_name} import tool_function, ToolError

try:
    result = await tool_function(args)
    print(f"Success: {{result}}")
except ToolError as e:
    print(f"Tool error: {{e}}")
    # Handle gracefully
```

### Batch Processing

```python
import asyncio
from {component_name} import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## Integration with Mirascope

This tool follows Mirascope best practices:

- Uses Pydantic models for structured inputs and outputs
- Supports async/await patterns for optimal performance
- Compatible with all Mirascope LLM providers
- Includes comprehensive error handling{lilypad_support}

## Troubleshooting

{troubleshooting}

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes

{migration_notes}

---

**Key Benefits:**

{key_benefits}

**Related Components:**

{related_components}

**References:**

{references}
"""

# Prompt Template-specific template
PROMPT_TEMPLATE_TEMPLATE = """# {component_name}

> {description}

**Version**: {version} | **Type**: {type} | **License**: {license}
**Authors**: {authors} | **Repository**: {repository_url}

## Overview

{detailed_description}

This collection provides reusable prompt templates that follow Mirascope best practices and can be easily integrated into your AI applications.

## Quick Start

### Installation

```bash
funcn add {component_name}
```

### Dependencies

**Python Dependencies:**

{python_dependencies}

### Basic Usage

{example_usage}

## Prompt Templates

This component includes the following prompt templates:

### Template Functions

Each template is implemented as a decorated function following Mirascope patterns:

```python
from mirascope.core import llm, prompt_template
from pydantic import BaseModel

class ResponseModel(BaseModel):
    field1: str
    field2: int

@llm.call(provider="openai", model="gpt-4o-mini", response_model=ResponseModel)
@prompt_template("Your prompt template here with {{variable}}")
def template_function(variable: str): ...
```

## Template Categories

### Available Templates

{template_variables}

### Usage Patterns

- **Zero-shot**: Direct prompting without examples
- **Few-shot**: Prompting with example inputs/outputs
- **Chain-of-thought**: Step-by-step reasoning prompts
- **Role-based**: Prompts with specific persona/role definitions

## Integration with Mirascope

These templates follow Mirascope best practices:

- Uses `@prompt_template` decorators for all prompts
- Implements Pydantic response models for structured outputs
- Supports multiple LLM providers
- Includes comprehensive type hints{lilypad_support}

### Advanced Usage

```python
# Customize provider and model
@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022", response_model=ResponseModel)
@prompt_template("Custom prompt with {{input}}")
def custom_template(input: str): ...

# Chain templates together
def chained_workflow(initial_input: str):
    result1 = template1(initial_input)
    result2 = template2(result1.content)
    return result2
```

## Template Customization

### Modifying Templates

You can customize these templates by:

1. **Parameter Adjustment**: Modify function parameters
2. **Prompt Engineering**: Adjust the prompt text
3. **Response Models**: Update Pydantic models
4. **Provider Settings**: Change LLM provider/model

### Creating Variants

```python
# Create a variant with different settings
@llm.call(provider="openai", model="gpt-4o", response_model=EnhancedModel)
@prompt_template("Enhanced version: {{input}}")
def enhanced_template(input: str): ...
```

## Advanced Examples

{advanced_examples}

## Prompt Engineering Best Practices

- **Be Specific**: Clearly define the task and expected output
- **Use Examples**: Provide few-shot examples for complex tasks
- **Structure Output**: Use Pydantic models for structured responses
- **Handle Edge Cases**: Include instructions for error scenarios
- **Iterate and Test**: Continuously refine prompts based on results

## Troubleshooting

{troubleshooting}

### Common Issues

- **Poor Results**: Refine prompt wording and add examples
- **Inconsistent Output**: Use stricter Pydantic models
- **Token Limits**: Break down complex prompts into smaller chunks

## Migration Notes

{migration_notes}

---

**Key Benefits:**

{key_benefits}

**Related Components:**

{related_components}

**References:**

{references}
"""

# Response Model-specific template
RESPONSE_MODEL_TEMPLATE = """# {component_name}

> {description}

**Version**: {version} | **Type**: {type} | **License**: {license}
**Authors**: {authors} | **Repository**: {repository_url}

## Overview

{detailed_description}

This component provides Pydantic response models for structured LLM outputs, ensuring type safety and validation.

## Quick Start

### Installation

```bash
funcn add {component_name}
```

### Dependencies

**Python Dependencies:**

{python_dependencies}

### Basic Usage

{example_usage}

## Response Models

### Model Definitions

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class YourResponseModel(BaseModel):
    \"\"\"Structured response model with validation.\"\"\"

    field1: str = Field(..., description="Required string field")
    field2: int = Field(..., gt=0, description="Positive integer")
    field3: Optional[str] = Field(None, description="Optional field")
    items: List[str] = Field(default_factory=list, description="List of items")
    timestamp: datetime = Field(default_factory=datetime.now)
```

### Using with Mirascope

```python
from mirascope.core import llm, prompt_template
from {component_name} import YourResponseModel

@llm.call(provider="openai", model="gpt-4o-mini", response_model=YourResponseModel)
@prompt_template("Generate structured data for: {{input}}")
def structured_llm_call(input: str): ...

result: YourResponseModel = structured_llm_call("your input")
print(result.field1)  # Type-safe access
```

## Model Features

### Validation Rules

- **Type Safety**: Automatic type conversion and validation
- **Field Constraints**: Min/max values, string patterns, etc.
- **Custom Validators**: Complex validation logic
- **Default Values**: Sensible defaults for optional fields

### Advanced Validation

```python
from pydantic import validator, root_validator

class AdvancedModel(BaseModel):
    name: str
    age: int

    @validator('age')
    def age_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Age must be positive')
        return v

    @root_validator
    def validate_combination(cls, values):
        # Complex validation logic
        return values
```

## Integration with Mirascope

These models work seamlessly with Mirascope:

- **Structured Outputs**: Ensure LLM responses match expected schema
- **Type Safety**: Full typing support with IDE autocompletion
- **Validation**: Automatic validation of LLM outputs
- **Error Handling**: Clear error messages for invalid responses{lilypad_support}

### Multi-Model Usage

```python
from {component_name} import Model1, Model2

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Model1)
@prompt_template("Generate type 1 data: {{input}}")
def generate_model1(input: str): ...

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Model2)
@prompt_template("Generate type 2 data: {{input}}")
def generate_model2(input: str): ...
```

## Advanced Examples

{advanced_examples}

### Model Composition

```python
from typing import Union

# Union types for multiple possible outputs
ResponseUnion = Union[Model1, Model2, Model3]

@llm.call(provider="openai", model="gpt-4o-mini", response_model=ResponseUnion)
@prompt_template("Generate appropriate model for: {{input}}")
def dynamic_model_selection(input: str): ...
```

### Nested Models

```python
class NestedModel(BaseModel):
    id: str
    data: YourResponseModel  # Nested model
    metadata: Dict[str, Any]
```

## Model Guidelines

### Design Principles

- **Single Responsibility**: Each model should have a clear purpose
- **Descriptive Fields**: Use clear field names and descriptions
- **Appropriate Types**: Choose the most specific type possible
- **Validation**: Include appropriate validation rules
- **Documentation**: Provide clear docstrings and field descriptions

## Troubleshooting

{troubleshooting}

### Common Issues

- **Validation Errors**: LLM output doesn't match model schema
- **Type Mismatches**: Incorrect field types in model definition
- **Missing Fields**: Required fields not generated by LLM

## Migration Notes

{migration_notes}

---

**Key Benefits:**

{key_benefits}

**Related Components:**

{related_components}

**References:**

{references}
"""

# Eval-specific template
EVAL_TEMPLATE = """# {component_name}

> {description}

**Version**: {version} | **Type**: {type} | **License**: {license}
**Authors**: {authors} | **Repository**: {repository_url}

## Overview

{detailed_description}

This component provides evaluation functions for testing and measuring LLM performance using Mirascope's evaluation framework.

## Quick Start

### Installation

```bash
funcn add {component_name}
```

### Dependencies

**Python Dependencies:**

{python_dependencies}

**Environment Variables:**

{environment_variables}

### Basic Usage

{example_usage}

## Evaluation Framework

### Eval Functions

```python
from mirascope.core import llm, prompt_template
from pydantic import BaseModel, Field

class EvalResult(BaseModel):
    score: float = Field(..., ge=0, le=1, description="Score between 0 and 1")
    reasoning: str = Field(..., description="Explanation of the score")

@llm.call(provider="openai", model="gpt-4o-mini", response_model=EvalResult)
@prompt_template(\"\"\"
Evaluate the following based on criteria:
Input: {{input}}
Output: {{output}}
Criteria: {{criteria}}
\"\"\")
def evaluate_response(input: str, output: str, criteria: str): ...
```

### Running Evaluations

```python
from {component_name} import evaluation_function

# Single evaluation
result = evaluation_function(
    input_data="test input",
    model_output="model response",
    ground_truth="expected response"
)

print(f"Score: {{result.score}}")
print(f"Reasoning: {{result.reasoning}}")
```

### Batch Evaluation

```python
import asyncio
from typing import List

async def batch_evaluate(test_cases: List[dict]):
    tasks = [
        evaluation_function(
            input_data=case["input"],
            model_output=case["output"],
            ground_truth=case["expected"]
        )
        for case in test_cases
    ]

    results = await asyncio.gather(*tasks)
    return results
```

## Evaluation Metrics

### Supported Metrics

{template_variables}

### Custom Metrics

```python
@llm.call(provider="openai", model="gpt-4o-mini", response_model=EvalResult)
@prompt_template("Custom evaluation prompt: {{input}}")
def custom_metric(input: str, output: str): ...
```

## Integration with Mirascope

This evaluation component integrates with Mirascope's eval framework:

- **Structured Eval Results**: Pydantic models for evaluation outputs
- **LLM-as-a-Judge**: Use LLMs to evaluate other LLM outputs
- **Batch Processing**: Efficient evaluation of multiple examples
- **Multi-Provider Support**: Evaluate across different LLM providers{lilypad_support}

### Evaluation Pipeline

```python
from mirascope.core import llm_eval

@llm_eval(
    evaluators=[evaluation_function],
    datasets=["test_dataset.json"]
)
def run_evaluation():
    # Evaluation pipeline configuration
    pass
```

## Advanced Examples

{advanced_examples}

### A/B Testing

```python
async def compare_models(test_cases, model_a, model_b):
    results_a = await batch_evaluate_model(test_cases, model_a)
    results_b = await batch_evaluate_model(test_cases, model_b)

    return analyze_comparison(results_a, results_b)
```

### Evaluation Datasets

```python
# Load evaluation dataset
import json

def load_eval_dataset(path: str):
    with open(path) as f:
        return json.load(f)

dataset = load_eval_dataset("eval_data.json")
results = await batch_evaluate(dataset)
```

## Best Practices

### Evaluation Design

- **Clear Criteria**: Define specific evaluation criteria
- **Representative Data**: Use diverse test cases
- **Human Validation**: Validate eval results with human judgment
- **Iterative Improvement**: Continuously refine evaluation methods

### Reliability

- **Inter-rater Agreement**: Check consistency across evaluators
- **Calibration**: Ensure eval scores align with human judgment
- **Edge Case Testing**: Include challenging examples

## Troubleshooting

{troubleshooting}

### Common Issues

- **Inconsistent Scores**: Review evaluation criteria and examples
- **Low Agreement**: Refine evaluation prompts and scoring rubrics
- **Performance Issues**: Optimize batch processing and concurrent execution

## Migration Notes

{migration_notes}

---

**Key Benefits:**

{key_benefits}

**Related Components:**

{related_components}

**References:**

{references}
"""

# Default template for unknown types
DEFAULT_TEMPLATE = """# {component_name}

> {description}

**Version**: {version} | **Type**: {type} | **License**: {license}
**Authors**: {authors} | **Repository**: {repository_url}

## Overview

{detailed_description}

## Quick Start

### Installation

```bash
funcn add {component_name}
```

### Dependencies

**Registry Dependencies:**

{registry_dependencies}

**Python Dependencies:**

{python_dependencies}

**Environment Variables:**

{environment_variables}

### Basic Usage

{example_usage}

## Configuration

### Template Variables

{template_variables}

### Advanced Configuration

{advanced_configuration}

## Integration with Mirascope

This component follows Mirascope best practices:

- Uses appropriate decorators and patterns
- Implements structured outputs where applicable
- Supports async/await patterns for optimal performance
- Compatible with multiple LLM providers
- Includes comprehensive error handling{lilypad_support}

## API Reference

{api_reference}

## Advanced Examples

{advanced_examples}

## Troubleshooting

{troubleshooting}

## Migration Notes

{migration_notes}

---

**Key Benefits:**

{key_benefits}

**Related Components:**

{related_components}

**References:**

{references}
"""

# Template mapping by component type
COMPONENT_TYPE_TEMPLATES = {
    "agent": AGENT_TEMPLATE,
    "tool": TOOL_TEMPLATE,
    "prompt_template": PROMPT_TEMPLATE_TEMPLATE,
    "response_model": RESPONSE_MODEL_TEMPLATE,
    "eval": EVAL_TEMPLATE,
    "example": DEFAULT_TEMPLATE,  # Examples use default template
}


def get_template_for_type(component_type: str) -> str:
    """Get the appropriate template for a component type."""
    return COMPONENT_TYPE_TEMPLATES.get(component_type, DEFAULT_TEMPLATE)
