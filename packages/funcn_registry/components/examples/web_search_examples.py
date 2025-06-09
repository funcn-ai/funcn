#!/usr/bin/env python3
"""
Comprehensive examples of the unified web search agent in the funcn registry.

This file demonstrates the unified web search agent capabilities including:
- Multi-provider search strategies (DuckDuckGo, Qwant, auto-selection)
- Privacy-focused vs comprehensive search modes
- Multi-provider LLM configurations
- Streaming vs structured responses
- Tool usage patterns

Usage:
    python web_search_examples.py
"""

import asyncio
import os
from collections.abc import AsyncGenerator

# Example imports (these would be available after adding components via funcn)
try:
    # Unified web search agent with all capabilities
    from duckduckgo_search_tools import DuckDuckGoSearchArgs, URLParseArgs, duckduckgo_search, parse_url_content
    from qwant_search_tools import QwantSearchArgs, qwant_search
    from web_search import (
        SearchProvider,
        web_search_agent,
        web_search_agent_multi_provider,
        web_search_agent_stream,
        web_search_comprehensive,
        web_search_fast,
        web_search_private,
    )

    COMPONENTS_AVAILABLE = True
except ImportError:
    print("⚠️  Web search components not yet installed. Run:")
    print("   funcn add duckduckgo_search_tools")
    print("   funcn add qwant_search_tools")
    print("   funcn add web_search_agent")
    COMPONENTS_AVAILABLE = False


async def example_unified_agent_basic():
    """Example 1: Basic unified agent with auto provider selection"""
    print("🔍 Example 1: Unified Agent with Auto Provider Selection")
    print("=" * 60)

    question = "What is Mirascope and how does it help with LLM development?"
    response = await web_search_agent(
        question=question,
        search_provider="auto",  # Let the agent choose the best provider
    )

    print(f"Question: {question}")
    print(f"Answer: {response.answer}")
    print(f"Search providers used: {response.search_providers}")
    print(f"Sources found: {len(response.sources)}")
    print(f"Search queries: {response.search_queries}")
    if response.privacy_note:
        print(f"Privacy note: {response.privacy_note}")
    print()


async def example_provider_strategies():
    """Example 2: Different search provider strategies"""
    print("🎯 Example 2: Different Search Provider Strategies")
    print("=" * 60)

    question = "AI privacy regulations 2024"

    strategies = [
        ("duckduckgo", "Fast, comprehensive search"),
        ("qwant", "Privacy-focused, no tracking"),
        ("auto", "Intelligent provider selection"),
        ("all", "Multi-provider comprehensive search"),
    ]

    for strategy, description in strategies:
        print(f"\n--- Strategy: {strategy} ({description}) ---")
        try:
            response = await web_search_agent(question=question, search_provider=strategy)
            print(f"Providers used: {response.search_providers}")
            print(f"Answer length: {len(response.answer)} characters")
            print(f"Sources: {len(response.sources)}")
            if response.privacy_note:
                print(f"Privacy: {response.privacy_note}")
        except Exception as e:
            print(f"Error with {strategy}: {e}")
    print()


async def example_convenience_functions():
    """Example 3: Convenience functions for common use cases"""
    print("⚡ Example 3: Convenience Functions")
    print("=" * 60)

    question = "How do AI companies handle user data privacy?"

    print("--- Fast Search (DuckDuckGo only) ---")
    fast_response = await web_search_fast(question)
    print(f"Providers: {fast_response.search_providers}")
    print(f"Answer length: {len(fast_response.answer)} chars")

    print("\n--- Private Search (Qwant only) ---")
    private_response = await web_search_private(question)
    print(f"Providers: {private_response.search_providers}")
    print(f"Privacy note: {private_response.privacy_note}")

    print("\n--- Comprehensive Search (All providers) ---")
    comprehensive_response = await web_search_comprehensive(question)
    print(f"Providers: {comprehensive_response.search_providers}")
    print(f"Total sources: {len(comprehensive_response.sources)}")
    print()


async def example_streaming_agent():
    """Example 4: Streaming web search agent"""
    print("🌊 Example 4: Streaming Unified Agent")
    print("=" * 60)

    question = "Latest developments in AI agent frameworks"
    print(f"Question: {question}")
    print("Streaming response with auto provider selection:")
    print("-" * 50)

    async for chunk in web_search_agent_stream(
        question=question, search_provider="auto", privacy_mode=False, provider="openai", model="gpt-4o-mini"
    ):
        print(chunk, end="", flush=True)
    print("\n")


async def example_multi_provider_llm():
    """Example 5: Multi-provider LLM with unified search"""
    print("🔄 Example 5: Multi-Provider LLM Configuration")
    print("=" * 60)

    question = "Compare different approaches to AI safety"

    # Try different LLM providers with unified search
    llm_providers = [
        ("openai", "gpt-4o-mini"),
        ("anthropic", "claude-3-5-sonnet-20241022"),
    ]

    for llm_provider, model in llm_providers:
        if f"{llm_provider.upper()}_API_KEY" in os.environ:
            print(f"\n--- Testing {llm_provider} {model} ---")
            try:
                response = await web_search_agent_multi_provider(
                    question=question,
                    search_provider="auto",  # Let agent choose search provider
                    llm_provider=llm_provider,
                    model=model,
                    privacy_mode=True,  # Prefer privacy-focused search
                )
                print(f"Search providers used: {response.search_providers}")
                print(f"Answer length: {len(response.answer)} characters")
                print(f"Sources found: {len(response.sources)}")
                if response.privacy_note:
                    print("Privacy protection: ✓")
            except Exception as e:
                print(f"Error with {llm_provider}: {e}")
        else:
            print(f"Skipping {llm_provider} (no API key found)")
    print()


async def example_advanced_configuration():
    """Example 6: Advanced configuration and locale support"""
    print("🌍 Example 6: Advanced Configuration & Locale Support")
    print("=" * 60)

    # Multi-locale search
    locales = [
        ("en_US", "What are the latest AI developments?"),
        ("fr_FR", "Quelles sont les dernières nouvelles en IA?"),
        ("de_DE", "Was sind die neuesten KI-Entwicklungen?"),
    ]

    for locale, question in locales:
        print(f"\n--- Locale: {locale} ---")
        print(f"Question: {question}")
        try:
            response = await web_search_agent_multi_provider(
                question=question,
                search_provider="qwant",  # Qwant supports multiple locales
                locale=locale,
                privacy_mode=True,
            )
            print(f"Answer preview: {response.answer[:100]}...")
            print(f"Sources: {len(response.sources)}")
        except Exception as e:
            print(f"Error: {e}")
    print()


async def example_advanced_workflow():
    """Example 7: Advanced workflow with tool composition"""
    print("⚡ Example 7: Advanced Multi-Tool Workflow")
    print("=" * 60)

    question = "Best practices for building AI agents with Mirascope"

    print(f"Question: {question}")
    print("Workflow:")
    print("1. Use unified agent with comprehensive search strategy")
    print("2. Combine multiple providers for validation")
    print("3. Extract detailed content from top sources")
    print()

    # Step 1: Comprehensive search using all providers
    print("Step 1: Comprehensive search...")
    comprehensive_response = await web_search_comprehensive(question)
    print(f"✓ Found {len(comprehensive_response.sources)} sources using: {comprehensive_response.search_providers}")

    # Step 2: Privacy-focused validation search
    print("\nStep 2: Privacy-focused validation...")
    privacy_response = await web_search_private(f"{question} privacy considerations")
    print(f"✓ Privacy search completed: {len(privacy_response.sources)} additional sources")

    # Step 3: Content extraction from top sources
    print("\nStep 3: Detailed content extraction...")
    all_sources = comprehensive_response.sources + privacy_response.sources
    unique_sources = list(dict.fromkeys(all_sources))  # Remove duplicates

    extracted_content = []
    for url in unique_sources[:3]:  # Limit to top 3
        try:
            parse_args = URLParseArgs(url=url, max_chars=1000)
            content = await parse_url_content(parse_args)
            extracted_content.append((url, content))
            print(f"✓ Extracted content from: {url}")
        except Exception as e:
            print(f"✗ Failed to extract from {url}: {e}")

    print("\nWorkflow Summary:")
    print(f"- Total unique sources: {len(unique_sources)}")
    print(f"- Content extracted: {len(extracted_content)} pages")
    print(f"- Search providers used: {set(comprehensive_response.search_providers + privacy_response.search_providers)}")
    print(f"- Privacy protection: {'✓' if privacy_response.privacy_note else '✗'}")
    print()


def check_environment():
    """Check if required environment variables are set"""
    print("🔧 Environment Check")
    print("=" * 60)

    required_vars = ["OPENAI_API_KEY"]
    recommended_vars = ["ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]

    print("Required API keys:")
    for var in required_vars:
        status = "✓ Set" if os.getenv(var) else "✗ Missing"
        print(f"  {var}: {status}")

    print("\nRecommended API keys (for multi-provider examples):")
    for var in recommended_vars:
        status = "✓ Set" if os.getenv(var) else "✗ Missing"
        print(f"  {var}: {status}")
    print()


async def main():
    """Run all examples"""
    print("🚀 Funcn Unified Web Search Agent Examples")
    print("=" * 70)
    print()

    check_environment()

    if not COMPONENTS_AVAILABLE:
        return

    try:
        # Run all examples
        await example_unified_agent_basic()
        await example_provider_strategies()
        await example_convenience_functions()
        await example_streaming_agent()
        await example_multi_provider_llm()
        await example_advanced_configuration()
        await example_advanced_workflow()

        print("✅ All examples completed successfully!")
        print("\n🎯 Key Takeaways:")
        print("- Single agent interface for all search providers")
        print("- Configurable search strategies (duckduckgo, qwant, auto, all)")
        print("- Privacy-focused and comprehensive search modes")
        print("- Multi-provider LLM support")
        print("- Locale support for international searches")
        print("- Convenient functions for common use cases")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Make sure you have the required API keys set and components installed.")


if __name__ == "__main__":
    asyncio.run(main())
