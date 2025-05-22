# Unified Web Search Agent for Funcn Registry

This document provides an overview of the **unified web search system** in the funcn registry. Unlike traditional approaches that require separate agents for different providers, this system offers a single, flexible interface that can use multiple search providers with configurable strategies.

## 🎯 **Unified Architecture Benefits**

- **Single Interface**: One agent API for all search providers  
- **Configurable Strategies**: Choose `duckduckgo`, `qwant`, `auto`, or `all`
- **Privacy Options**: Built-in privacy-focused and comprehensive modes
- **Multi-Provider LLMs**: Support for OpenAI, Anthropic, Google, and more
- **Convenience Functions**: Simple shortcuts for common use cases

## 🌐 Available Components

### Core Agent

#### `web_search_agent` (v0.3.0)

**Purpose**: Unified web search agent supporting multiple providers with configurable strategies.

**Key Features**:

- **Provider Strategies**: `duckduckgo`, `qwant`, `auto`, `all`
- **Search Modes**: Fast, private, comprehensive
- **Multi-Provider LLM**: OpenAI, Anthropic, Google, etc.
- **Streaming Support**: Real-time response streaming
- **Locale Support**: International search capabilities
- **Privacy Protection**: Built-in privacy-focused modes

**Dependencies**: `mirascope`, `pydantic`  
**Registry Dependencies**: `duckduckgo_search_tools`, `qwant_search_tools`

### Supporting Tools

#### 1. `duckduckgo_search_tools`

**Purpose**: DuckDuckGo search and URL parsing with Mirascope integration.

**Features**:

- DuckDuckGo web search with fallback implementations
- URL content extraction and parsing  
- Mirascope pre-made tools integration
- Structured response models

#### 2. `qwant_search_tools`

**Purpose**: Privacy-focused search using Qwant search engine.

**Features**:

- Privacy-respecting search (no user tracking)
- Multi-locale support (en_US, fr_FR, de_DE, etc.)
- EU-based privacy compliance
- Multi-engine search capabilities

## 🚀 Quick Start Guide

### Installation

```bash
# Install the unified web search system
funcn add duckduckgo_search_tools  # DuckDuckGo search capabilities
funcn add qwant_search_tools       # Privacy-focused Qwant search
funcn add web_search_agent         # Unified agent (requires both tools)
```

### Basic Usage

#### Simple Auto-Selection

```python
import asyncio
from web_search import web_search_agent

async def main():
    # Agent automatically selects the best provider
    response = await web_search_agent(
        "What is Mirascope and how does it work?",
        search_provider="auto"
    )
    
    print(f"Answer: {response.answer}")
    print(f"Providers used: {response.search_providers}")
    print(f"Sources: {response.sources}")

asyncio.run(main())
```

#### Provider-Specific Strategies

```python
# Privacy-focused search using Qwant
response = await web_search_agent(
    "AI privacy best practices",
    search_provider="qwant"
)

# Comprehensive search using all providers
response = await web_search_agent(
    "Latest AI developments",
    search_provider="all"  
)

# Fast search using DuckDuckGo only
response = await web_search_agent(
    "Python tutorial",
    search_provider="duckduckgo"
)
```

#### Convenience Functions

```python
from web_search import web_search_private, web_search_comprehensive, web_search_fast

# Privacy-focused (uses Qwant automatically)
private_response = await web_search_private("How do companies protect user data?")

# Comprehensive (uses all available providers)  
comprehensive_response = await web_search_comprehensive("AI safety research")

# Fast (uses DuckDuckGo only)
fast_response = await web_search_fast("Weather in San Francisco")
```

## 🔧 Provider Strategies

The unified agent supports four search strategies:

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `"duckduckgo"` | Uses only DuckDuckGo | Fast, general-purpose search |
| `"qwant"` | Uses only Qwant | Privacy-focused, no tracking |  
| `"auto"` | Intelligent selection | Adapts to query characteristics |
| `"all"` | Uses multiple providers | Maximum coverage and validation |

### Auto-Selection Logic

When using `search_provider="auto"`, the agent intelligently selects providers based on:

- **Query characteristics**: Privacy-sensitive queries prefer Qwant
- **Locale requirements**: International queries use appropriate providers
- **Privacy mode**: `privacy_mode=True` prioritizes Qwant
- **Fallback logic**: Graceful degradation if providers are unavailable

## 🛡️ Privacy Features

### Privacy-First Modes

```python
# Explicit privacy mode
response = await web_search_agent(
    "Personal health information privacy",
    search_provider="qwant",
    privacy_mode=True
)

# Convenience function for privacy
response = await web_search_private("Sensitive query")

# Response includes privacy information
print(response.privacy_note)
# "This search was performed using Qwant, a privacy-focused search engine that doesn't track users."
```

### Privacy Benefits

- **No user tracking**: Qwant doesn't track users or build profiles
- **No data storage**: Search history isn't stored by the search engine
- **EU compliance**: Operates under strict EU privacy regulations
- **Anonymous searches**: No personal data collection or profiling

## 🌍 Multi-Provider & Locale Support

### LLM Provider Configuration

```python
from web_search import web_search_agent_multi_provider

# Use different LLM providers
response = await web_search_agent_multi_provider(
    question="AI developments in healthcare",
    search_provider="auto",
    llm_provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    locale="en_US"
)

# Localized search
response = await web_search_agent_multi_provider(
    question="Quelles sont les dernières nouvelles en IA?",
    search_provider="qwant",
    locale="fr_FR",
    privacy_mode=True
)
```

### Supported LLM Providers

- **OpenAI**: `gpt-4o-mini`, `gpt-4o`, etc.
- **Anthropic**: `claude-3-5-sonnet-20241022`, etc.
- **Google**: `gemini-1.5-flash`, etc.
- **Groq**: Various Llama and Mistral models
- **And more**: Any Mirascope-supported provider

## 🌊 Streaming Support

```python
from web_search import web_search_agent_stream

async def streaming_search():
    async for chunk in web_search_agent_stream(
        question="Explain quantum computing",
        search_provider="auto",
        privacy_mode=False,
        provider="openai",
        model="gpt-4o-mini"
    ):
        print(chunk, end="", flush=True)

asyncio.run(streaming_search())
```

## 📊 Response Format

All agent functions return a unified `WebSearchResponse`:

```python
class WebSearchResponse(BaseModel):
    answer: str                    # Comprehensive answer
    sources: list[str]             # URLs of sources used
    search_queries: list[str]      # Search queries performed
    search_providers: list[str]    # Providers used (e.g., ["duckduckgo", "qwant"])
    privacy_note: str | None       # Privacy information if applicable
```

## 🎯 Advanced Use Cases

### 1. Multi-Provider Research

```python
async def comprehensive_research(topic):
    # Get diverse perspectives using multiple providers
    response = await web_search_comprehensive(f"research on {topic}")
    
    return {
        "comprehensive_answer": response.answer,
        "providers_used": response.search_providers,
        "source_count": len(response.sources),
        "privacy_protected": bool(response.privacy_note)
    }
```

### 2. Privacy-Aware Search

```python
async def privacy_aware_search(query, sensitive=False):
    provider = "qwant" if sensitive else "auto"
    
    response = await web_search_agent(
        query,
        search_provider=provider,
        privacy_mode=sensitive
    )
    
    return response
```

### 3. Locale-Specific Research

```python
async def multilingual_research(query):
    locales = [
        ("en_US", "auto"),
        ("fr_FR", "qwant"),  # Qwant has good French support
        ("de_DE", "qwant")
    ]
    
    results = {}
    for locale, provider in locales:
        response = await web_search_agent_multi_provider(
            question=query,
            search_provider=provider,
            locale=locale
        )
        results[locale] = response.answer
    
    return results
```

### 4. Advanced Workflow

```python
async def advanced_search_workflow(query):
    # Step 1: Fast initial search
    initial = await web_search_fast(query)
    
    # Step 2: Privacy-focused validation
    privacy = await web_search_private(f"{query} privacy considerations")
    
    # Step 3: Comprehensive deep-dive
    comprehensive = await web_search_comprehensive(f"{query} detailed analysis")
    
    return {
        "quick_answer": initial.answer,
        "privacy_perspective": privacy.answer,
        "comprehensive_analysis": comprehensive.answer,
        "all_sources": initial.sources + privacy.sources + comprehensive.sources,
        "providers_used": set(initial.search_providers + privacy.search_providers + comprehensive.search_providers)
    }
```

## 🔗 Component Dependencies

```
web_search_agent (v0.3.0)
├── duckduckgo_search_tools (DuckDuckGo search & URL parsing)
│   ├── mirascope (with pre-made tools)
│   ├── beautifulsoup4
│   ├── duckduckgo-search
│   └── httpx
└── qwant_search_tools (Privacy-focused search)
    ├── httpx  
    └── beautifulsoup4
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required (choose at least one)
export OPENAI_API_KEY="your-openai-key"

# Optional (for multi-provider support)
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
export GROQ_API_KEY="your-groq-key"
```

### Default Configuration

The agent uses intelligent defaults that can be overridden:

```python
# Default configuration
response = await web_search_agent(
    question="Your question",
    search_provider="auto",      # Intelligent selection
    locale="en_US",              # English (US)
    max_results_per_search=5     # Reasonable result limit
)
```

## 🧪 Testing and Examples

Run the comprehensive examples:

```bash
cd packages/funcn_registry/components/examples
python web_search_examples.py
```

**Example Scenarios**:

- Auto provider selection
- Privacy-focused vs comprehensive search  
- Multi-provider LLM configurations
- Streaming responses
- Locale-specific searches
- Advanced multi-tool workflows

## 🚀 Migration from Separate Agents

If you were using separate agents before:

```python
# OLD: Separate agents
from qwant_web_search import qwant_search_agent
from web_search import web_search_agent_simple

qwant_response = await qwant_search_agent(question)
ddg_response = await web_search_agent_simple(question)

# NEW: Unified agent with provider selection
from web_search import web_search_agent

qwant_response = await web_search_agent(question, search_provider="qwant")
ddg_response = await web_search_agent(question, search_provider="duckduckgo")

# Even better: Let the agent choose automatically
auto_response = await web_search_agent(question, search_provider="auto")
```

## 🤝 Contributing

When extending the unified search system:

1. **Add new search providers** as tools in the `tools/` directory
2. **Update the agent** to recognize new providers in strategy logic
3. **Maintain the unified interface** - avoid breaking the single-agent pattern
4. **Include privacy considerations** for any new providers
5. **Add comprehensive tests** and examples for new functionality

## 📖 References

- [Mirascope Web Search Agent Guide](https://mirascope.com/docs/mirascope/guides/agents/web-search-agent)
- [Mirascope Tools Documentation](https://mirascope.com/docs/mirascope/learn/tools)
- [Mirascope Dynamic Configuration](https://mirascope.com/docs/mirascope/guides/dynamic-configuration-chaining)
- [Qwant Privacy Policy](https://about.qwant.com/legal/privacy/)

---

**🎯 Key Benefits Summary**:

- ✅ **Single interface** for all search providers
- ✅ **Configurable strategies** adapt to your needs  
- ✅ **Privacy protection** built-in when needed
- ✅ **Multi-provider LLM** support for flexibility
- ✅ **Intelligent auto-selection** reduces complexity
- ✅ **Convenience functions** for common patterns
