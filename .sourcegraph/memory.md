# Funcn Codebase Memory

## Overview
The Funcn AI framework provides reusable components for building LLM-powered applications using Mirascope.

## Key Architecture
- **Component System**: Registry-based components with JSON manifests
- **LLM Integration**: Mirascope for provider-agnostic LLM calls
- **Type Safety**: Pydantic models for all data structures
- **Async First**: All LLM operations use async/await

## Component Categories
- **Agent**: text_summarization_agent, recruiting_assistant, enhanced_knowledge_graph_agent, document_segmentation_agent, knowledge_graph_agent, academic_research, research_assistant, pii_scrubbing_agent, dataset_builder, sales_intelligence, market_intelligence, web_search_agent, hallucination_detector, sourcing_assistant, code_generation_execution_agent
- **Tool**: docx_search, directory_search, firecrawl_scrape, git_repo_search, code_interpreter, pg_search, mdx_search, csv_search, code_docs_search, json_search, pdf_search, exa_websets_tools, url_content_parser, nimble_search, qwant_search_tools, duckduckgo_search_tools, exa_search_tools, youtube_video_search, xml_search

## Available Components
- **text_summarization_agent** (agent): Advanced text summarization agent using chain-of-thought reasoning, few-shot learning, and iterative refinement. Supports multiple styles (technical, executive, simple, academic, journalistic) and progressive summarization with validation.
- **recruiting_assistant** (agent): Recruiting assistant for finding qualified candidates using Exa websets. Helps with technical recruiting, sales hiring, and executive search.
- **enhanced_knowledge_graph_agent** (agent): Enhanced knowledge graph extraction using advanced prompt engineering. Features meta-reasoning for strategy planning, chain-of-thought entity extraction with detailed reasoning, multi-pass relationship detection, and self-consistency validation for high-accuracy results.
- **document_segmentation_agent** (agent): Agent for intelligently segmenting documents into logical parts. Supports multiple strategies including semantic, structural, hybrid, and fixed-size segmentation. Features document structure analysis, segment summarization, and optimized chunking for vector embeddings.
- **knowledge_graph_agent** (agent): Agent for extracting structured knowledge from text by identifying entities and their relationships. Builds comprehensive knowledge graph representations with support for hierarchical relationships, graph enrichment, and visualization-ready outputs.
- **academic_research** (agent): Academic research agent for finding research papers using Exa websets. Perfect for academics, researchers, and anyone needing to discover scholarly publications.
- **research_assistant** (agent): AI-powered research agent that conducts comprehensive research using Exa search
- **pii_scrubbing_agent** (agent): Agent for detecting and removing Personally Identifiable Information (PII) from text. Combines regex patterns and LLM analysis for comprehensive PII detection. Supports multiple scrubbing methods including masking, redaction, generalization, and synthetic data replacement.
- **dataset_builder** (agent): AI-powered dataset builder that creates curated data collections using Exa Websets with custom criteria and enrichments
- **sales_intelligence** (agent): Sales intelligence agent for finding targeted business contacts and companies using Exa websets. Perfect for sales prospecting, lead generation, and market intelligence.
- **market_intelligence** (agent): Market intelligence agent for tracking investment opportunities and market trends using Exa websets. Perfect for VCs, analysts, and business development professionals.
- **web_search_agent** (agent): Unified web search agent supporting multiple providers (DuckDuckGo, Qwant, Exa, Nimble) with configurable search strategies. Features privacy-focused, AI-powered semantic search, structured data extraction, comprehensive, and auto-selection modes.
- **hallucination_detector** (agent): AI-powered hallucination detection agent that verifies factual claims using Exa search
- **sourcing_assistant** (agent): Sourcing assistant for finding suppliers, manufacturers, and solutions using Exa websets. Perfect for procurement, supply chain management, and technology sourcing.
- **code_generation_execution_agent** (agent): Agent for generating and safely executing Python code. Analyzes code for safety, supports multiple safety levels, and provides recommendations for improvement. Features sandboxed execution environment and comprehensive code analysis.
- **docx_search** (tool): Microsoft Word document search and content extraction tool with advanced text search, regex support, and metadata extraction
- **directory_search** (tool): Advanced file system navigation and search tool with pattern matching, content search, and filtering capabilities
- **firecrawl_scrape** (tool): Firecrawl-powered web scraping tool that extracts clean, structured content from websites. Handles JavaScript-rendered pages and provides multiple output formats including Markdown, HTML, and screenshots.
- **git_repo_search** (tool): Git repository search tool for searching code, files, and commits in both local Git repositories and GitHub. Supports pattern matching, file filtering, and commit history search.
- **code_interpreter** (tool): Safe Python code execution tool with sandboxing, timeout controls, and variable capture
- **pg_search** (tool): PostgreSQL database search and query tool with full-text search, connection pooling, and schema introspection
- **mdx_search** (tool): MDX documentation search tool with JSX component parsing, frontmatter support, and section extraction
- **csv_search** (tool): CSV search tool for searching and filtering structured data within CSV files. Supports column-specific searches, data filtering, and both exact and fuzzy matching capabilities.
- **code_docs_search** (tool): Technical documentation search tool for API docs, README files, code comments, docstrings, and code examples
- **json_search** (tool): JSON search tool for searching and querying within JSON files and data structures. Supports JSONPath expressions, fuzzy matching, and searching in both keys and values.
- **pdf_search** (tool): PDF search tool that enables searching for text within PDF documents using fuzzy matching. Extracts text from PDFs and provides context-aware search results with page numbers and match scores.
- **exa_websets_tools** (tool): Advanced web data collection tools using Exa Websets. Create curated collections of web data with search criteria and structured enrichments for building datasets.
- **url_content_parser** (tool): URL content parsing tool that extracts clean text content from web pages. Removes scripts, styles, and other noise to provide readable text content.
- **nimble_search** (tool): Multi-API search tool using Nimble's Web, SERP, and Maps APIs for comprehensive search capabilities
- **qwant_search_tools** (tool): Privacy-focused web search tools using Qwant search engine. Provides structured search results with no user tracking, using unified models compatible with other search providers.
- **duckduckgo_search_tools** (tool): DuckDuckGo web search tools with clean, structured results. Provides comprehensive search coverage using the duckduckgo-search library.
- **exa_search_tools** (tool): AI-powered search tools using Exa. Features neural search, direct Q&A, and similarity search with advanced filtering and relevance scoring.
- **youtube_video_search** (tool): YouTube video search and transcript extraction tool for content analysis and research
- **xml_search** (tool): XML data processing tool with XPath queries, namespace support, validation, and advanced search capabilities

## Development Patterns
- Use `@prompt_template` decorators for all prompts
- Define Pydantic response models for structured outputs
- Implement async functions for LLM calls
- Support multiple LLM providers
- Include comprehensive error handling

## Environment Variables
- ANTHROPIC_API_KEY: API key for Anthropic services (if using Anthropic provider).
- DATABASE_URL: PostgreSQL connection string
- EXA_API_KEY: API key for Exa AI search services (if using Exa provider).
- EXA_API_KEY: API key for Exa services
- EXA_API_KEY: API key for Exa services. Get it from https://exa.ai
- FIRECRAWL_API_KEY: API key for Firecrawl services
- GITHUB_TOKEN: GitHub personal access token for searching GitHub repositories
- GOOGLE_API_KEY: API key for Google services (if using Google provider).
- NIMBLE_API_KEY: API key for Nimble search services (Web API, SERP API, Maps API) (if using Nimble provider).
- NIMBLE_API_KEY: API key for Nimble services
- OPENAI_API_KEY: API key for OpenAI services
- OPENAI_API_KEY: API key for OpenAI services (if using OpenAI provider).
- YOUTUBE_API_KEY: YouTube Data API v3 key

## Common Issues
- Always await async LLM calls
- Include proper type hints
- Follow the component.json manifest structure
- Test with multiple LLM providers
