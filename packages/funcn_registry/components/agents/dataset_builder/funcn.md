# dataset_builder_agent

> AI-powered dataset builder that creates curated data collections using Exa Websets with custom criteria and enrichments

**Version**: 0.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

AI-powered dataset builder that creates curated data collections using Exa Websets with custom criteria and enrichments

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add dataset_builder_agent
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**
- `exa_websets`

**Python Dependencies:**
- `mirascope[openai]` >=1.24.0
- `pydantic` >=2.0.0
- `exa-py` >=1.0.0

**Environment Variables:**
- `EXA_API_KEY`: API key for Exa services (**Required**)
- `OPENAI_API_KEY`: API key for OpenAI services (**Required**)

### Basic Usage

```python
from ai_agents.dataset_builder import (
    build_dataset, build_company_dataset, build_competitor_dataset,
    build_influencer_dataset, build_investment_dataset
)

async def main():
    # Build a general dataset
    dataset = await build_dataset(
        topic="AI startups",
        entity_type="company",
        target_count=100
    )
    print(f"Dataset created: {dataset.name}")
    print(f"Items collected: {dataset.status.items_found}")
    
    # Build a competitor analysis dataset
    competitor_data = await build_competitor_dataset(
        company_name="OpenAI",
        industry="AI",
        aspects=["products", "pricing", "strategy"]
    )
    
    # Find influencers in a niche
    influencers = await build_influencer_dataset(
        niche="AI and machine learning",
        platforms=["twitter", "linkedin"],
        min_followers=50000
    )
    
    # Investment opportunities
    investments = await build_investment_dataset(
        sector="healthtech",
        investment_stage="Series A",
        geography="United States"
    )
```

## Agent Configuration

### Template Variables

- `provider`: `openai`
- `model`: `gpt-4o-mini`
- `default_entity_type`: `general`
- `default_target_count`: `50`
- `default_wait_for_completion`: `True`
- `default_max_wait_minutes`: `30`

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
result_openai = await dataset_builder(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await dataset_builder(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from dataset_builder import dataset_builder_custom

result = await dataset_builder_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

You can now import the dataset builder with `from ai_agents.dataset_builder import build_dataset`. Make sure to set your EXA_API_KEY and OPENAI_API_KEY environment variables.

The agent provides specialized dataset builders:

**Core Functions:**
- `build_dataset()` - General dataset building with custom criteria
- `build_company_dataset()` - Company information and analysis
- `build_research_dataset()` - Academic papers and research

**Market Intelligence:**
- `build_market_dataset()` - Market analysis and trends
- `build_competitor_dataset()` - Competitive landscape analysis
- `build_news_trends_dataset()` - News monitoring and sentiment

**Business Development:**
- `build_influencer_dataset()` - Social media influencer discovery
- `build_investment_dataset()` - Investment opportunities
- `build_talent_dataset()` - Recruiting and talent sourcing
- `build_product_launch_dataset()` - Product launch tracking
- `build_location_dataset()` - Location/real estate analysis

Datasets are built asynchronously using Exa Websets. Monitor progress in real-time or run in background. For optional tracing, install lilypad: `pip install lilypad`.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add dataset_builder` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes



---

**Key Benefits:**
- **Dataset**
- **Exa**
- **Websets**
- **Data-Collection**
- **Enrichment**

**Related Components:**
- `exa_websets`

**References:**
- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
