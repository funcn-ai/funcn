# multi_platform_social_media_manager
> Enhanced multi-platform social media campaign manager with trend analysis, engagement prediction, and real-time adaptation capabilities for comprehensive campaign orchestration

**Version**: 0.2.0 | **Type**: agent | **License**: MIT

## Overview

Enhanced multi-platform social media campaign manager with trend analysis, engagement prediction, and real-time adaptation capabilities for comprehensive campaign orchestration

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
sygaldry add multi_platform_social_media_manager
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
from multi_platform_social_media_manager import (
    multi_platform_social_media_manager,
    multi_platform_social_media_manager_stream
)

# Example 1: Launch a product campaign across multiple platforms
result = await multi_platform_social_media_manager(
    campaign_goal="Launch our new AI-powered productivity app",
    target_audience="Tech-savvy professionals aged 25-45 interested in productivity",
    brand_voice="Innovative, helpful, professional yet approachable",
    platforms=["twitter", "linkedin", "instagram", "tiktok"],
    content_themes=["AI innovation", "productivity tips", "work-life balance", "success stories"],
    campaign_duration="6 weeks",
    budget="$50,000",
    industry="Technology/SaaS",
    performance_goals="100K app downloads, 500K social impressions, 10% engagement rate"
)

print(f"Campaign Overview: {result.campaign_overview}")
print(f"\nTrending Opportunities: {', '.join(result.trend_analysis.trending_topics[:3])}")
print(f"\nPlatform Strategies:")
for strategy in result.platform_strategies:
    print(f"  {strategy.platform.value}: {strategy.posting_frequency}")

# Example 2: Stream a brand awareness campaign
async for update in multi_platform_social_media_manager_stream(
    campaign_goal="Increase brand awareness for sustainable fashion brand",
    target_audience="Eco-conscious millennials and Gen Z interested in fashion",
    brand_voice="Authentic, sustainable, trendy, empowering",
    platforms=["instagram", "tiktok", "pinterest", "threads"],
    content_themes=["sustainable fashion", "eco-tips", "behind-the-scenes", "customer stories"],
    campaign_duration="3 months",
    sample_message="Discover fashion that doesn't cost the Earth. Our new collection is here!"
):
    print(update, end='')

# Example 3: B2B thought leadership campaign
result = await multi_platform_social_media_manager(
    campaign_goal="Establish thought leadership in AI/ML consulting",
    target_audience="C-suite executives and decision makers in Fortune 500 companies",
    brand_voice="Expert, insightful, data-driven, forward-thinking",
    platforms=["linkedin", "twitter", "youtube"],
    content_themes=["AI trends", "case studies", "industry insights", "ROI analysis"],
    campaign_duration="ongoing",
    competitive_landscape="Major consulting firms active in AI space",
    performance_goals="50 qualified leads per month, 20% engagement on LinkedIn"
)

# Access detailed engagement predictions
for content in result.content_optimization.platform_adaptations:
    print(f"\n{content.platform.value} Content:")
    print(f"  Engagement Score: {content.engagement_prediction.engagement_score:.2f}")
    print(f"  Virality Potential: {content.engagement_prediction.virality_potential:.2f}")
    print(f"  Top Suggestion: {content.engagement_prediction.improvement_suggestions[0]}")

# Example 4: Crisis management scenario
result = await multi_platform_social_media_manager(
    campaign_goal="Rebuild trust after product recall",
    target_audience="Existing customers and general public",
    brand_voice="Transparent, apologetic, solution-focused, responsible",
    platforms=["twitter", "facebook", "instagram", "linkedin"],
    content_themes=["transparency", "safety commitment", "customer support", "improvements"],
    campaign_duration="2 weeks intensive, 2 months follow-up",
    sample_message="We're committed to your safety and have taken immediate action..."
)

print(f"\nCrisis Management Protocols:")
for protocol in result.crisis_management:
    print(f"- {protocol}")
```

## Agent Configuration

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with sygaldry tools for enhanced capabilities
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

The Multi-Platform Social Media Manager helps you create comprehensive campaigns with trend analysis and engagement predictions. Configure your OpenAI API key and customize platform strategies based on your brand's unique voice and goals. The agent includes crisis management protocols and real-time adaptation capabilities.

## Migration Notes

---

**Key Benefits:**

- **Social-Media**
- **Marketing**
- **Campaign-Management**
- **Trend-Analysis**
- **Engagement-Prediction**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await multi_platform_social_media_manager(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await multi_platform_social_media_manager(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from multi_platform_social_media_manager import multi_platform_social_media_manager_custom

result = await multi_platform_social_media_manager_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `sygaldry add multi_platform_social_media_manager` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries
