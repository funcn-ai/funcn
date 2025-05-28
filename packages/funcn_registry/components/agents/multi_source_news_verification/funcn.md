# multi_source_news_verification

> Advanced multi-source news verification agent with comprehensive fact-checking tools including academic search, government data verification, social media verification, and expert source validation for combating misinformation

**Version**: 0.4.1 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

Advanced multi-source news verification agent with comprehensive fact-checking tools including academic search, government data verification, social media verification, and expert source validation for combating misinformation

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add multi_source_news_verification
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
- `EXA_API_KEY`: Exa API key for advanced web search (optional, enhances real-time verification) (Optional)

### Basic Usage

```python
from multi_source_news_verification import (
    multi_source_news_verification,
    multi_source_news_verification_stream
)

# Example 1: Verify scientific/medical claims with academic sources
result = await multi_source_news_verification(
    article_content="""New study claims vitamin D supplements can prevent 90% of COVID-19 cases.
    Researchers at unnamed institute say results are conclusive.
    No peer review mentioned.""",
    headline="Vitamin D: The COVID Cure We've Been Waiting For?",
    topic_area="Health/Medical",
    use_realtime_search=True
)

# The agent will automatically:
# - Search academic databases (PubMed, Google Scholar)
# - Check medical fact-checking sites
# - Consult expert medical sources
# - Verify with WHO/CDC data

print(f"Credibility: {result.overall_credibility.value}")
print(f"Misinformation Risk: {result.misinformation_risk}")

# Example 2: Verify statistical/government claims
result = await multi_source_news_verification(
    article_content="""Unemployment hits record low of 2.1% according to sources.
    Economy growing at 8% annually. Crime down 75% nationwide.""",
    headline="Economic Miracle: All Indicators Point to Success",
    topic_area="Economics/Politics",
    use_realtime_search=True
)

# The agent will:
# - Search government databases (BLS, Census, FBI stats)
# - Cross-reference with economic fact-checkers
# - Verify with official government sources
# - Check historical data for context

# Example 3: Verify social media viral claims
result = await multi_source_news_verification(
    article_content="""Celebrity tweet goes viral claiming new law bans all pets.
    Screenshot shows verified account. 10 million retweets in 2 hours.
    Government officials silent.""",
    headline="Celebrity Exposes Secret Pet Ban Law",
    context="Claim originated on Twitter/X",
    use_realtime_search=True
)

# The agent will:
# - Search for original social media posts
# - Verify account authenticity
# - Check for deleted posts or manipulated screenshots
# - Search government sources for actual laws
# - Look for official responses

# Example 4: Verify images/videos in news
result = await multi_source_news_verification(
    article_content="""Shocking video shows massive crowds at political rally.
    Aerial footage reveals unprecedented turnout.
    Opposition claims video is from different event.""",
    headline="Record-Breaking Rally or Recycled Footage?",
    use_realtime_search=True
)

# The agent will:
# - Search for original source of images/video
# - Check reverse image search results
# - Look for fact-checks on the visual content
# - Verify date and location claims

# Example 5: Academic research verification
result = await multi_source_news_verification(
    article_content="""MIT researchers discover room temperature superconductor.
    Paper published in prestigious journal. Other labs confirming results.
    Could revolutionize technology.""",
    headline="Scientific Breakthrough of the Century?",
    topic_area="Science/Technology",
    use_realtime_search=True
)

# Access detailed verification by claim type
analysis = result.verification.news_analysis
for claim, claim_type in analysis.claim_types.items():
    print(f"\nClaim: {claim}")
    print(f"Type: {claim_type.value}")
    # Agent uses appropriate tools based on claim type

# Example 6: Multi-faceted story verification
result = await multi_source_news_verification(
    article_content="""Senator claims crime up 200% citing new study.
    Posts graph on social media showing dramatic spike.
    Opponents say data is manipulated. Police chief disputes numbers.
    Academic researchers call methodology flawed.""",
    headline="Crime Statistics Spark Political Firestorm",
    use_realtime_search=True
)

# The agent will use multiple tools:
# - GovernmentDataTool for official crime statistics
# - AcademicSearchTool for the mentioned study
# - SocialMediaVerificationTool for the posted graph
# - ExpertSourceTool for criminology experts
# - FactCheckSearchTool for existing fact-checks

# View which tools were used for each claim
for fact_check in result.verification.fact_checks:
    print(f"\nClaim: {fact_check.claim}")
    print(f"Verification Status: {fact_check.verification_status.value}")
    print(f"Evidence Quality: {fact_check.evidence_quality}")
    print(f"Primary Sources: {', '.join(fact_check.primary_sources[:2])}")
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
result_openai = await multi_source_news_verification(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await multi_source_news_verification(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from multi_source_news_verification import multi_source_news_verification_custom

result = await multi_source_news_verification_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

The Multi-Source News Verification Agent now includes comprehensive verification tools:

**Verification Tools Available:**
1. **Web Search**: General current information
2. **Fact-Check Search**: 20+ verified fact-checking organizations
3. **Academic Search**: Scientific papers, peer-reviewed research
4. **Government Data**: Official statistics and statements
5. **Reverse Image Search**: Verify visual content
6. **Social Media Verification**: Authenticate viral claims
7. **Expert Sources**: Academic and professional expertise

**Trusted Fact-Checking Sources:**
- **International**: Snopes, FactCheck.org, PolitiFact, Reuters Fact Check
- **News Organizations**: AP Fact Check, Washington Post Fact Checker, CNN Facts First
- **Regional**: Full Fact (UK), Chequeado (Latin America), Africa Check
- **Specialized**: Lead Stories, Poynter Institute, Factly (India), Teyit (Turkey)
- **Multi-language**: Maldita (Spain), Newtral (Spain), Boom Live (India)

**Automatic Claim Routing:**
The agent automatically categorizes claims and uses appropriate tools:
- Statistical claims → Government databases + Academic sources
- Medical claims → PubMed + Medical fact-checkers + Expert sources
- Political claims → Fact-checkers + Government sources
- Social media claims → Platform verification + Original source search
- Visual content → Reverse image search + Fact-checkers

**Enhanced Capabilities:**
- Searches verified fact-checking organizations globally
- Accesses academic databases for scientific verification
- Queries government statistics for data claims
- Verifies social media posts and viral content
- Checks expert opinions from universities and research institutions
- Identifies manipulated images and videos

**Setup:**
1. Install optional dependencies for web search:
   ```bash
   pip install duckduckgo-search  # Free, no API key needed
   pip install exa-py  # Advanced search, requires API key
   ```

2. Configure environment:
   ```bash
   export OPENAI_API_KEY=your_key
   export EXA_API_KEY=your_key  # Optional, for enhanced search
   ```

The agent provides transparent verification showing which tools were used and why, helping users understand the verification process and develop media literacy skills.

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add multi_source_news_verification` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes



---

**Key Benefits:**

- **News-Verification**
- **Fact-Checking**
- **Media-Literacy**
- **Misinformation**
- **Bias-Detection**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
