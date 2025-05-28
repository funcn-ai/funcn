# decision_quality_assessor
> Comprehensive decision quality assessment agent that analyzes context, evaluates alternatives, detects cognitive biases, and provides actionable recommendations for better decision-making

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Comprehensive decision quality assessment agent that analyzes context, evaluates alternatives, detects cognitive biases, and provides actionable recommendations for better decision-making

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add decision_quality_assessor
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
from decision_quality_assessor import decision_quality_assessor, decision_quality_assessor_stream

# Example 1: Assess a strategic business decision
result = await decision_quality_assessor(
    decision="Should we expand into the European market next year?",
    background="Our company has been growing 30% YoY in North America. We have $10M in funding.",
    alternatives=[
        "Expand to Europe immediately",
        "Wait 6 months and gather more data",
        "Focus on North America growth",
        "Partner with European distributor"
    ],
    stakeholders="Executive team, investors, employees, potential European customers",
    constraints="Limited budget, no European presence, regulatory requirements",
    timeline="Decision needed within 30 days",
    decision_process="Executive team discussions, market research, financial modeling"
)

print(f"Overall Quality Score: {result.overall_quality_score:.2f}")
print(f"Decision Readiness: {result.decision_readiness:.2f}")
print(f"\nRecommended Framework: {result.framework_recommendation.recommended_framework}")

# Example 2: Stream assessment for a hiring decision
async for update in decision_quality_assessor_stream(
    decision="Should we hire a senior engineer or two junior engineers?",
    background="Growing startup, limited budget, need to scale engineering team",
    alternatives=[
        "Hire one senior engineer",
        "Hire two junior engineers",
        "Hire one mid-level engineer"
    ],
    evaluation_criteria="Technical skills, team fit, cost, mentorship capacity"
):
    print(update, end='')

# Example 3: Assess a personal decision with bias detection
result = await decision_quality_assessor(
    decision="Should I accept the job offer from Company X?",
    background="Current job is stable but limited growth. New offer: 30% salary increase, relocation required.",
    alternatives=[
        "Accept the new offer",
        "Negotiate current position",
        "Decline and continue job search"
    ],
    stakeholders="Family, current employer, potential employer",
    constraints="Need to relocate within 60 days if accepted, family considerations",
    timeline="Response needed within 1 week",
    decision_makers="Self, spouse",
    information_sources="Job offer details, Glassdoor reviews, industry contacts"
)

# Access detailed bias analysis
for bias in result.bias_analysis:
    if bias.severity > 0.5:
        print(f"\nHigh Severity Bias: {bias.bias_type.value}")
        print(f"Impact: {bias.impact_on_decision}")
        print(f"Mitigation: {bias.mitigation_strategies[0]}")
```

## Agent Configuration

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with funcn tools for enhanced capabilities
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

### Template Variables

- None

### Advanced Configuration

Configure template variables using CLI options or environment variables.

### LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models
- **Groq**: Set `GROQ_API_KEY` for Groq models

Configure the provider and model using template variables or function parameters.

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

## Troubleshooting

The Decision Quality Assessor helps you make better decisions through systematic analysis. It identifies cognitive biases, evaluates alternatives, and provides actionable recommendations. Configure your OpenAI API key and provide comprehensive decision context for best results.

## Migration Notes

---

**Key Benefits:**

- **Decision-Making**
- **Bias-Detection**
- **Quality-Assessment**
- **Strategic-Planning**
- **Risk-Analysis**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add decision_quality_assessor` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

### Custom Configuration

```python
# Custom configuration example
from decision_quality_assessor import decision_quality_assessor_custom

result = await decision_quality_assessor_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await decision_quality_assessor(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await decision_quality_assessor(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```
