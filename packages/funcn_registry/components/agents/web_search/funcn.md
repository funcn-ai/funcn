# web_search_agent

> Unified web search agent supporting multiple providers (DuckDuckGo, Qwant, Exa, Nimble) with configurable search strategies. Features privacy-focused, AI-powered semantic search, structured data extraction, comprehensive, and auto-selection modes.

**Version**: 0.4.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Unified web search agent supporting multiple providers (DuckDuckGo, Qwant, Exa, Nimble) with configurable search strategies. Features privacy-focused, AI-powered semantic search, structured data extraction, comprehensive, and auto-selection modes.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add web_search_agent
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- `duckduckgo_search_tools`
- `qwant_search_tools`
- `exa_search_tools`
- `nimble_search_tools`
- `url_content_parser`

**Python Dependencies:**

- `mirascope` >=1.24.0
- `pydantic` >=2.0.0

**Environment Variables:**

- `OPENAI_API_KEY`: API key for OpenAI services (if using OpenAI provider). (Optional)
- `ANTHROPIC_API_KEY`: API key for Anthropic services (if using Anthropic provider). (Optional)
- `GOOGLE_API_KEY`: API key for Google services (if using Google provider). (Optional)
- `EXA_API_KEY`: API key for Exa AI search services (if using Exa provider). (Optional)
- `NIMBLE_API_KEY`: API key for Nimble search services (Web API, SERP API, Maps API) (if using Nimble provider). (Optional)

### Basic Usage

```python
import asyncio
from web_search import web_search_agent, web_search_private, web_search_comprehensive, web_search_ai, web_search_structured

async def main():
    # Auto-select best search provider
    response = await web_search_agent(
        "What is Mirascope and how does it work?",
        search_provider="auto"
    )
    print(f"Answer: {response.answer}")
    print(f"Providers used: {response.search_providers}")
    
    # Privacy-focused search (uses Qwant)
    privacy_response = await web_search_private(
        "How do AI companies handle user data?"
    )
    print(f"Privacy note: {privacy_response.privacy_note}")
    
    # AI-powered semantic search (uses Exa)
    ai_response = await web_search_ai(
        "Latest breakthroughs in quantum computing research papers"
    )
    print(f"Answer: {ai_response.answer}")
    print(f"AI search found {len(ai_response.sources)} sources")
    
    # Structured data and location search (uses Nimble)
    nimble_response = await web_search_structured(
        "Best restaurants near Times Square New York"
    )
    print(f"Answer: {nimble_response.answer}")
    print(f"Nimble found: {nimble_response.search_providers}")
    
    # Comprehensive search (uses all available providers)
    comprehensive_response = await web_search_comprehensive(
        "Latest AI safety research"
    )
    print(f"Sources found: {len(comprehensive_response.sources)}")
    
    # Custom configuration with Exa
    custom_response = await web_search_agent_multi_provider(
        question="Machine learning frameworks comparison",
        search_provider="exa",
        llm_provider="anthropic",
        model="claude-3-5-sonnet-20241022"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## Agent Configuration

### Template Variables

- `provider`: `openai`
- `model`: `gpt-4o-mini`
- `search_provider`: `auto`

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
result_openai = await web_search_agent(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await web_search_agent(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from web_search_agent import web_search_agent_custom

result = await web_search_agent_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

This unified agent requires 'duckduckgo_search_tools', 'qwant_search_tools', 'exa_search_tools', 'nimble_search_tools', and 'url_content_parser' for full functionality. Add them with: funcn add duckduckgo_search_tools && funcn add qwant_search_tools && funcn add exa_search_tools && funcn add nimble_search_tools && funcn add url_content_parser. The agent automatically selects the best search provider or you can specify: 'duckduckgo' for general search, 'qwant' for privacy, 'exa' for AI-powered semantic search, 'nimble' for structured data and location-based searches, 'auto' for intelligent selection, or 'all' for comprehensive coverage. Set your preferred LLM provider's API key and EXA_API_KEY if using Exa, NIMBLE_API_KEY if using Nimble.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add web_search_agent` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes

---

**Key Benefits:**

- **Web Search**
- **Agent**
- **Mirascope**
- **Multi Provider**
- **Privacy**

**Related Components:**

- `duckduckgo_search_tools`
- `qwant_search_tools`
- `exa_search_tools`
- `nimble_search_tools`
- `url_content_parser`

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
