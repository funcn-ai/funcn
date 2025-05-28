# game_theory_analysis

> Analyzes complex strategic situations using game theory principles, identifying equilibria, predicting outcomes, and providing actionable recommendations

**Version**: 0.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Analyzes complex strategic situations using game theory principles, identifying equilibria, predicting outcomes, and providing actionable recommendations

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add game_theory_analysis
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**
- None

**Python Dependencies:**
- `mirascope>=1.24.0`
- `pydantic>=2.0.0`
- `asyncio`

**Environment Variables:**
- `OPENAI_API_KEY`: OpenAI API key for LLM calls (**Required**)

### Basic Usage

```python
from game_theory_analysis import game_theory_analyzer, game_theory_analyzer_stream

# Example 1: Analyze a business competition scenario
analysis = await game_theory_analyzer(
    situation="Two tech companies competing for market share in cloud services",
    context="Company A has 60% market share but higher costs, Company B has innovative technology but limited resources",
    stakeholders="Company A (incumbent), Company B (challenger), Enterprise customers, Developers",
    objectives="A wants to maintain dominance, B wants to gain share, customers want best value",
    environmental_factors="Increasing demand for AI services, regulatory scrutiny on monopolies"
)

print(f"Game Type: {analysis.scenario.game_type.value}")
print(f"\nPredicted Outcomes:")
for outcome in analysis.predicted_outcomes[:3]:
    print(f"- {outcome.outcome_name}: {outcome.probability:.1%} probability")

print(f"\nStrategic Recommendations:")
for player, recs in analysis.strategic_recommendations.items():
    print(f"\n{player}:")
    for rec in recs[:2]:
        print(f"  - {rec}")

# Example 2: Stream analysis of a negotiation scenario
async for update in game_theory_analyzer_stream(
    situation="Labor union negotiating with company management for better wages",
    context="Company profitable but facing competition, union has strong support"
):
    print(update, end='')

# Example 3: Analyze a multi-party political scenario
analysis = await game_theory_analyzer(
    situation="Three political parties forming coalition government",
    context="Party A (35%), Party B (30%), Party C (20%), need 50% to govern",
    stakeholders="Party A (center), Party B (left), Party C (right), Voters",
    objectives="Each party wants maximum cabinet positions and policy influence"
)
```

## Agent Configuration

### Template Variables

- None

### LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models
- **Groq**: Set `GROQ_API_KEY` for Groq models

Configure the provider and model using template variables or function parameters.

### Advanced Configuration

Configure template variables using CLI options or environment variables.

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with funcn tools for enhanced capabilities
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## Integration with Mirascope

This agent follows Mirascope best practices:

- Uses `@prompt_template` decorators for all prompts
- Implements Pydantic response models for structured outputs
- Supports async/await patterns for optimal performance
- Compatible with multiple LLM providers
- Includes comprehensive error handling
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## API Reference

See component source code for detailed API documentation.

## Advanced Examples

Check the examples directory for advanced usage patterns.

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await game_theory_analysis(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await game_theory_analysis(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from game_theory_analysis import game_theory_analysis_custom

result = await game_theory_analysis_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

The Game Theory Analysis agent helps analyze strategic interactions and conflicts. Configure your OpenAI API key and provide clear descriptions of the players, their objectives, and constraints for best results.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add game_theory_analysis` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes



---

**Key Benefits:**

- **Game-Theory**
- **Strategy**
- **Decision-Analysis**
- **Nash-Equilibrium**
- **Conflict-Resolution**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
