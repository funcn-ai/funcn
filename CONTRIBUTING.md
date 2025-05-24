# Contributing to funcn

Thank you for your interest in contributing to funcn! We're excited to have you join our community of developers building the future of Mirascope applications.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Components](#contributing-components)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Community Guidelines](#community-guidelines)

## Getting Started

funcn welcomes contributions of all kinds:

- New Mirascope components (agents, tools, prompts, etc.)
- Bug fixes
- Documentation improvements
- Test coverage
- Feature suggestions
- UI/UX improvements

## Development Setup

### Prerequisites

- Python 3.12+
- [devbox](https://www.jetpack.io/devbox/) (recommended)
- [task](https://taskfile.dev/) (recommended)
- [doppler](https://docs.doppler.com/docs/install-cli) (for secrets management)

### Setting Up Your Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/funcn.git
   cd funcn
   ```

2. **Install Dependencies**
   ```bash
   # Using task
   task install

   # Using devbox
   devbox install

   # Using uv
   uv sync
   ```

3. **Enter Development Shell**
   ```bash
   devbox shell
   ```

4. **Set Up Pre-commit Hooks**
   ```bash
   task pre-commit
   ```

5. **Run Tests**
   ```bash
   task test
   ```

## Contributing Components

### Component Structure

Each component must follow this structure:

```
component_name/
├── component.json      # Metadata and configuration
├── README.md          # Component documentation
├── __init__.py        # Python module initialization
├── agent.py           # For agents
├── tool.py            # For tools
├── prompt.py          # For prompts
├── model.py           # For response models
└── tests/             # Component tests
    └── test_component.py
```

### Component Metadata (component.json)

```json
{
  "$schema": "https://funcn.ai/schemas/component.json",
  "name": "your_component",
  "version": "0.1.0",
  "type": "tool|agent|prompt|response_model|eval",
  "description": "Clear description of what this component does",
  "authors": [
    {
      "name": "Your Name",
      "email": "you@example.com"
    }
  ],
  "license": "MIT",
  "mirascope_version_min": "1.24.0",
  "python_dependencies": [
    {"name": "package_name", "version": ">=1.0.0"}
  ],
  "registry_dependencies": [
    "other_component_name"
  ],
  "supports_lilypad": true,
  "tags": ["tag1", "tag2"],
  "example_usage": "```python\n# Example code\n```"
}
```

### Component Guidelines

1. **Single Responsibility**: Each component should do one thing well
2. **Mirascope Native**: Use proper Mirascope decorators (`@llm.call`, `@llm.tool`, `@prompt_template`)
3. **Provider Agnostic**: Use the generic `@llm.call` decorator with configurable provider/model
4. **Type Everything**: Use type hints and Pydantic models for all inputs/outputs
5. **Async First**: Use `async def` for all LLM operations and I/O
6. **Response Models**: Always define Pydantic response models for structured outputs
7. **Error Handling**: Handle errors gracefully with informative messages
8. **Documentation**: Include docstrings, usage examples, and funcn.md

### Example Tool Component (Mirascope Functional Pattern)

```python
# tool.py - Tools as functions (preferred pattern)
def search_database(query: str, max_results: int = 5) -> dict:
    """
    Search the database for matching records.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (1-100)
        
    Returns:
        Dictionary with results and metadata
    """
    # Implementation
    results = []  # Your actual search logic here
    return {
        "results": results,
        "total_found": len(results),
        "query": query
    }

# agent.py - Agent using the tool
from mirascope import llm, prompt_template
from tools.my_tool import search_database
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    """Structured output for analysis."""
    summary: str
    key_findings: list[str]
    confidence: float

@llm.call(
    provider="{{provider}}", 
    model="{{model}}", 
    tools=[search_database],  # Pass tools here
    response_model=AnalysisResult
)
@prompt_template("""
Analyze the following data: {data}
Focus on: {focus_areas}

You have access to a search_database tool to find additional information.
""")
async def analyze_data(data: str, focus_areas: list[str]) -> AnalysisResult:
    """Analyze data with specified focus areas."""
    ...

# Usage example
response = await analyze_data("market trends", ["growth", "risks"])
if tool := response.tool:
    # The LLM wants to call the search_database tool
    result = tool.call()  # Executes with LLM-provided arguments
```

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 130 characters
- Use descriptive variable names

### Formatting and Linting

```bash
# Format code
task format

# Run linters
task lint

# Type checking
task mypy
```

### Import Order

1. Standard library imports
2. Third-party imports
3. Local imports

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Use pytest for all tests
- Include unit and integration tests
- Mock external API calls

### Running Tests

```bash
# Run all tests
task test

# Run with coverage
task test:coverage

# Run specific test
pytest tests/test_specific.py
```

### Test Structure

```python
import pytest
from your_component import your_function

@pytest.mark.asyncio
async def test_your_function():
    """Test description."""
    # Arrange
    args = YourArgs(...)
    
    # Act
    result = await your_function(args)
    
    # Assert
    assert result.success
    assert len(result.data) > 0
```

## Documentation

### Component Documentation

Each component must include:

1. **README.md**: Detailed documentation with examples
2. **Docstrings**: For all functions and classes
3. **Type hints**: For all parameters and returns
4. **Usage examples**: In component.json

### Documentation Style

- Use clear, concise language
- Include code examples
- Document edge cases
- Explain configuration options

## Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write code
   - Add tests
   - Update documentation

3. **Commit with Conventional Commits**
   ```bash
   git commit -m "feat: add new pdf parsing tool"
   git commit -m "fix: handle empty PDF files"
   git commit -m "docs: update PDF tool documentation"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] Added new tests
   - [ ] Updated documentation
   
   ## Screenshots (if applicable)
   ```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what is best for the community

### Getting Help

- **Discord**: [discord.gg/funcn](https://discord.gg/funcn)
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas

### Recognition

Contributors will be:

- Listed in our README
- Mentioned in release notes
- Invited to our contributor Discord channel

## Component Ideas

Looking for inspiration? Here are some component ideas:

- **Tools**: 
  - Slack integration
  - Email parser
  - Database query tool
  - Image analysis
  
- **Agents**:
  - Customer support agent
  - Code review assistant
  - Data analyst
  
- **Prompts**:
  - Creative writing templates
  - Technical documentation
  - Code explanation

## Questions?

If you have questions, please:

1. Check existing issues
2. Ask in Discord
3. Create a discussion

Thank you for contributing to funcn! Together, we're building the future of AI development. 
