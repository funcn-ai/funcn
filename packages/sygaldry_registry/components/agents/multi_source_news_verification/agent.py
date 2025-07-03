from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import BaseDynamicConfig, BaseTool, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Optional

# Import search tools for real-time verification
try:
    from duckduckgo_search import DDGS

    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False

try:
    import os
    from exa_py import Exa

    EXA_AVAILABLE = bool(os.environ.get("EXA_API_KEY"))
except ImportError:
    EXA_AVAILABLE = False


class CredibilityLevel(str, Enum):
    """Source credibility levels."""

    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    """Verification status of claims."""

    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    UNVERIFIED = "unverified"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    MISLEADING_CONTEXT = "misleading_context"


class BiasDirection(str, Enum):
    """Political/ideological bias direction."""

    FAR_LEFT = "far_left"
    LEFT = "left"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    RIGHT = "right"
    FAR_RIGHT = "far_right"
    UNKNOWN = "unknown"


class MisinformationType(str, Enum):
    """Types of misinformation."""

    FABRICATION = "fabrication"
    MANIPULATION = "manipulation"
    MISREPRESENTATION = "misrepresentation"
    FALSE_CONTEXT = "false_context"
    SATIRE = "satire"
    CLICKBAIT = "clickbait"
    PROPAGANDA = "propaganda"
    CONSPIRACY_THEORY = "conspiracy_theory"


class ClaimType(str, Enum):
    """Types of claims for verification routing."""

    STATISTICAL = "statistical"
    SCIENTIFIC = "scientific"
    MEDICAL = "medical"
    POLITICAL = "political"
    HISTORICAL = "historical"
    QUOTE = "quote"
    IMAGE_VIDEO = "image_video"
    SOCIAL_MEDIA = "social_media"
    FINANCIAL = "financial"
    LEGAL = "legal"
    GENERAL = "general"


# Web Search Tools for Real-time Verification
class WebSearchTool(BaseTool):
    """Search the web for real-time information to verify claims."""

    query: str = Field(..., description="Search query to find relevant information")
    max_results: int = Field(default=5, description="Maximum number of results to return")

    def call(self) -> str:
        """Execute web search and return formatted results."""
        results = []

        # Try DuckDuckGo first
        if DUCKDUCKGO_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    search_results = list(ddgs.text(self.query, max_results=self.max_results))
                    for result in search_results:
                        results.append(
                            f"Title: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )
                return "\n\n".join(results) if results else "No search results found."
            except Exception as e:
                pass

        # Fallback to Exa if available
        if EXA_AVAILABLE:
            try:
                exa = Exa(os.environ.get("EXA_API_KEY"))
                search_result = exa.search(query=self.query, num_results=self.max_results)
                for item in search_result.results:
                    results.append(f"Title: {item.title}\nURL: {item.url}\nScore: {item.score}")
                return "\n\n".join(results) if results else "No search results found."
            except Exception as e:
                pass

        return "Web search unavailable. Please install duckduckgo-search or configure EXA_API_KEY."


class FactCheckSearchTool(BaseTool):
    """Search fact-checking websites for existing verification of claims."""

    claim: str = Field(..., description="The claim to search for fact-checks")

    def call(self) -> str:
        """Search fact-checking sites for existing verifications."""
        fact_check_sites = [
            "site:snopes.com",
            "site:factcheck.org",
            "site:politifact.com",
            "site:fullfact.org",
            "site:apnews.com/APFactCheck",
            "site:reuters.com/fact-check",
            "site:washingtonpost.com/news/fact-checker",
            "site:cnn.com/factsfirst",
            "site:nytimes.com/spotlight/fact-checks",
            "site:usatoday.com/news/factcheck",
            "site:factcheck.afp.com",
            "site:poynter.org",
            "site:leadstories.com",
            "site:factcheckni.org",
            "site:chequeado.com",
            "site:africacheck.org",
            "site:teyit.org",
            "site:factly.in",
            "site:boomlive.in",
            "site:altnews.in",
            "site:maldita.es",
            "site:newtral.es",
        ]

        results = []
        if DUCKDUCKGO_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    # Search top fact-checking sites
                    for site in fact_check_sites[:5]:  # Limit to avoid rate limiting
                        query = f"{site} {self.claim}"
                        search_results = list(ddgs.text(query, max_results=2))
                        for result in search_results:
                            results.append(
                                f"Source: {site.replace('site:', '')}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                            )

                    # Also do a general fact-check search
                    general_query = f'"{self.claim}" fact check OR debunked OR false OR verified'
                    general_results = list(ddgs.text(general_query, max_results=3))
                    for result in general_results:
                        results.append(
                            f"General Search:\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

                return "\n\n".join(results) if results else "No fact-checks found for this claim."
            except Exception:
                pass

        return "Fact-check search unavailable. Unable to search fact-checking databases."


class AcademicSearchTool(BaseTool):
    """Search academic sources and research papers to verify scientific claims."""

    query: str = Field(..., description="Scientific or academic claim to verify")

    def call(self) -> str:
        """Search academic databases for peer-reviewed sources."""
        academic_sites = [
            "site:scholar.google.com",
            "site:pubmed.ncbi.nlm.nih.gov",
            "site:arxiv.org",
            "site:jstor.org",
            "site:sciencedirect.com",
            "site:nature.com",
            "site:science.org",
            "site:plos.org",
            "site:academic.oup.com",
            "site:springer.com",
        ]

        results = []
        if DUCKDUCKGO_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    # Search academic sources
                    for site in academic_sites[:3]:
                        query = f"{site} {self.query}"
                        search_results = list(ddgs.text(query, max_results=2))
                        for result in search_results:
                            results.append(
                                f"Academic Source: {site.replace('site:', '')}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                            )

                    # Search for meta-analyses and systematic reviews
                    meta_query = f'"{self.query}" meta-analysis OR systematic review OR peer-reviewed'
                    meta_results = list(ddgs.text(meta_query, max_results=2))
                    for result in meta_results:
                        results.append(
                            f"Research:\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

                return "\n\n".join(results) if results else "No academic sources found."
            except Exception:
                pass

        return "Academic search unavailable."


class GovernmentDataTool(BaseTool):
    """Search official government sources and databases for statistics and official statements."""

    query: str = Field(..., description="Claim involving government data, statistics, or official statements")
    country: str = Field(default="US", description="Country code for government sources (US, UK, EU, etc.)")

    def call(self) -> str:
        """Search government databases and official sources."""
        gov_sites = {
            "US": [
                "site:data.gov",
                "site:census.gov",
                "site:bls.gov",
                "site:cdc.gov",
                "site:fbi.gov/stats-services",
                "site:whitehouse.gov",
                "site:congress.gov",
                "site:gao.gov",
                "site:cbo.gov",
                "site:federalregister.gov",
            ],
            "UK": ["site:gov.uk", "site:ons.gov.uk", "site:parliament.uk", "site:data.gov.uk"],
            "EU": ["site:europa.eu", "site:ec.europa.eu", "site:eurostat.ec.europa.eu"],
            "GLOBAL": ["site:who.int", "site:un.org", "site:worldbank.org", "site:imf.org", "site:oecd.org"],
        }

        results = []
        sites_to_search = gov_sites.get(self.country, []) + gov_sites["GLOBAL"]

        if DUCKDUCKGO_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    for site in sites_to_search[:4]:
                        query = f"{site} {self.query}"
                        search_results = list(ddgs.text(query, max_results=2))
                        for result in search_results:
                            results.append(
                                f"Official Source: {site.replace('site:', '')}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                            )

                return "\n\n".join(results) if results else "No government data found."
            except Exception:
                pass

        return "Government data search unavailable."


class ReverseImageSearchTool(BaseTool):
    """Verify images and videos by searching for their original source and context."""

    image_description: str = Field(..., description="Description of the image or video to verify")

    def call(self) -> str:
        """Search for original sources of images/videos and their context."""
        if DUCKDUCKGO_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    results = []

                    # Search for the image description with verification keywords
                    queries = [
                        f'"{self.image_description}" original source',
                        f'"{self.image_description}" fake OR manipulated OR doctored',
                        f'"{self.image_description}" fact check image',
                        f'"{self.image_description}" reverse image search results',
                    ]

                    for query in queries:
                        search_results = list(ddgs.text(query, max_results=2))
                        for result in search_results:
                            results.append(
                                f"Image Search:\nQuery: {query}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                            )

                    return "\n\n".join(results) if results else "No image verification results found."
            except Exception:
                pass

        return "Image verification search unavailable. Consider using Google Reverse Image Search or TinEye directly."


class SocialMediaVerificationTool(BaseTool):
    """Verify claims originating from social media by searching for original posts and context."""

    claim: str = Field(..., description="Claim or quote from social media")
    platform: str = Field(default="", description="Social media platform (twitter, facebook, instagram, etc.)")

    def call(self) -> str:
        """Search for original social media posts and verify authenticity."""
        results = []

        if DUCKDUCKGO_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    # Platform-specific searches
                    if self.platform:
                        platform_query = f'site:{self.platform}.com "{self.claim}"'
                        search_results = list(ddgs.text(platform_query, max_results=3))
                        for result in search_results:
                            results.append(
                                f"Platform Search ({self.platform}):\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                            )

                    # General social media verification
                    verification_queries = [
                        f'"{self.claim}" verified account OR official statement',
                        f'"{self.claim}" deleted tweet OR deleted post OR screenshot',
                        f'"{self.claim}" social media hoax OR fake',
                    ]

                    for query in verification_queries:
                        search_results = list(ddgs.text(query, max_results=2))
                        for result in search_results:
                            results.append(
                                f"Verification Search:\nQuery: {query}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                            )

                return "\n\n".join(results) if results else "No social media verification results found."
            except Exception:
                pass

        return "Social media verification unavailable."


class ExpertSourceTool(BaseTool):
    """Find and verify expert opinions and authoritative sources on specific topics."""

    topic: str = Field(..., description="Topic requiring expert verification")
    claim: str = Field(..., description="Specific claim to verify with experts")

    def call(self) -> str:
        """Search for expert opinions and authoritative sources."""
        expert_sources = [
            "site:harvard.edu",
            "site:stanford.edu",
            "site:mit.edu",
            "site:oxford.ac.uk",
            "site:cambridge.org",
            "site:mayoclinic.org",
            "site:clevelandclinic.org",
            "site:johnshopkins.edu",
            "site:scientificamerican.com",
            "site:theconversation.com",
        ]

        results = []
        if DUCKDUCKGO_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    # Search expert sources
                    for source in expert_sources[:3]:
                        query = f"{source} {self.topic} {self.claim}"
                        search_results = list(ddgs.text(query, max_results=2))
                        for result in search_results:
                            results.append(
                                f"Expert Source: {source.replace('site:', '')}\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                            )

                    # Search for expert quotes
                    expert_query = f'"{self.topic}" expert OR professor OR researcher "{self.claim}"'
                    expert_results = list(ddgs.text(expert_query, max_results=3))
                    for result in expert_results:
                        results.append(
                            f"Expert Opinion:\nTitle: {result.get('title', '')}\nURL: {result.get('href', '')}\nSnippet: {result.get('body', '')}"
                        )

                return "\n\n".join(results) if results else "No expert sources found."
            except Exception:
                pass

        return "Expert source search unavailable."


class SourceCredibility(BaseModel):
    """Enhanced credibility assessment of a news source."""

    source_name: str = Field(..., description="Name of the news source")
    url: str = Field(..., description="URL of the source")
    credibility_level: CredibilityLevel = Field(..., description="Overall credibility assessment")
    bias_direction: BiasDirection = Field(..., description="Political/ideological bias")
    factual_reporting: str = Field(..., description="Assessment of factual reporting quality")
    transparency: str = Field(..., description="Transparency of ownership and funding")
    editorial_standards: str = Field(..., description="Editorial standards and corrections policy")
    track_record: str = Field(..., description="Historical accuracy track record")
    red_flags: list[str] = Field(..., description="Potential credibility concerns")
    strengths: list[str] = Field(..., description="Credibility strengths")
    fact_checker_ratings: dict[str, str] = Field(default_factory=dict, description="Ratings from fact-checkers")
    media_literacy_notes: list[str] = Field(..., description="Media literacy education points")


class FactCheck(BaseModel):
    """Enhanced fact-checking result for a specific claim."""

    claim: str = Field(..., description="The specific claim being fact-checked")
    verification_status: VerificationStatus = Field(..., description="Verification result")
    supporting_sources: list[str] = Field(..., description="Sources that support the claim")
    contradicting_sources: list[str] = Field(..., description="Sources that contradict the claim")
    primary_sources: list[str] = Field(..., description="Primary source documents")
    evidence_quality: str = Field(..., description="Quality of available evidence")
    confidence_level: float = Field(..., description="Confidence in verification (0-1)")
    context: str = Field(..., description="Important context for the claim")
    missing_context: list[str] = Field(..., description="Context that may be missing")
    fact_checker_consensus: str | None = Field(None, description="Consensus from fact-checkers")
    limitations: list[str] = Field(..., description="Limitations in verification")


class BiasAnalysis(BaseModel):
    """Analysis of bias in news content."""

    bias_type: str = Field(..., description="Type of bias detected")
    bias_indicators: list[str] = Field(..., description="Specific indicators of bias")
    loaded_language: list[str] = Field(..., description="Examples of loaded language")
    framing_analysis: str = Field(..., description="How the story is framed")
    missing_perspectives: list[str] = Field(..., description="Perspectives not included")
    source_selection_bias: str = Field(..., description="Bias in source selection")
    visual_bias: str | None = Field(None, description="Bias in visual elements")
    headline_bias: str = Field(..., description="Bias in headline vs content")


class NewsAnalysis(BaseModel):
    """Enhanced analysis of news content and claims."""

    headline: str = Field(..., description="News headline")
    main_claims: list[str] = Field(..., description="Key claims made in the article")
    claim_types: dict[str, ClaimType] = Field(..., description="Type categorization for each claim")
    claim_sources: dict[str, list[str]] = Field(..., description="Sources for each claim")
    emotional_language: list[str] = Field(..., description="Emotionally charged language used")
    missing_context: list[str] = Field(..., description="Important context that may be missing")
    potential_biases: list[str] = Field(..., description="Potential biases in presentation")
    bias_analysis: BiasAnalysis = Field(..., description="Detailed bias analysis")
    factual_vs_opinion: dict[str, str] = Field(..., description="Distinction between facts and opinions")
    sensationalism_score: float = Field(..., description="Level of sensationalism (0-1)")
    completeness_score: float = Field(..., description="Completeness of reporting (0-1)")
    transparency_score: float = Field(..., description="Transparency about sources (0-1)")
    misinformation_indicators: list[MisinformationType] = Field(..., description="Potential misinformation types")
    verification_priority: list[str] = Field(..., description="Claims prioritized for verification")


class MediaLiteracyReport(BaseModel):
    """Media literacy education component."""

    key_questions: list[str] = Field(..., description="Questions readers should ask")
    red_flags_found: list[str] = Field(..., description="Red flags in this content")
    verification_tips: list[str] = Field(..., description="Tips for verifying similar content")
    critical_thinking_prompts: list[str] = Field(..., description="Prompts for critical analysis")
    fact_checking_resources: list[str] = Field(..., description="Resources for fact-checking")
    media_literacy_lessons: list[str] = Field(..., description="Key media literacy lessons")


class NewsVerification(BaseModel):
    """Enhanced comprehensive news verification result."""

    original_article: str = Field(..., description="Original article or claim")
    source_credibility: list[SourceCredibility] = Field(..., description="Credibility of sources")
    news_analysis: NewsAnalysis = Field(..., description="Analysis of the news content")
    fact_checks: list[FactCheck] = Field(..., description="Fact-checking results")
    cross_reference_analysis: str = Field(..., description="Cross-reference analysis across sources")
    consensus_level: str = Field(..., description="Level of consensus across sources")
    reliability_indicators: list[str] = Field(..., description="Indicators of reliability")
    warning_signs: list[str] = Field(..., description="Warning signs of misinformation")
    media_literacy_report: MediaLiteracyReport = Field(..., description="Media literacy education")
    recommendations: list[str] = Field(..., description="Recommendations for readers")
    alternative_sources: list[str] = Field(..., description="Alternative sources to consult")


class VerificationResult(BaseModel):
    """Enhanced final verification result with summary."""

    verification: NewsVerification
    overall_credibility: CredibilityLevel = Field(..., description="Overall credibility assessment")
    misinformation_risk: str = Field(..., description="Risk level of misinformation")
    key_findings: list[str] = Field(..., description="Key findings from verification")
    confidence_score: float = Field(..., description="Overall confidence in assessment (0-1)")
    action_recommendations: list[str] = Field(..., description="Recommended actions for readers")
    follow_up_suggestions: list[str] = Field(..., description="Suggestions for further verification")
    share_recommendations: str = Field(..., description="Recommendations about sharing this content")
    educational_value: str = Field(..., description="Educational insights from this verification")


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[SourceCredibility],
    tools=[WebSearchTool],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert media literacy specialist and fact-checker with deep knowledge
    of journalism standards, media bias, and misinformation patterns. You have access
    to web search to verify source credibility and check current reputation.
    Your role is to assess news source credibility using established frameworks,
    real-time information, and provide educational insights.

    Credibility Assessment Framework:
    1. Editorial Standards: Corrections policy, transparency, accountability, ethics
    2. Factual Reporting: Accuracy track record, source diversity, verification practices
    3. Transparency: Ownership disclosure, funding sources, conflicts of interest, author info
    4. Professional Standards: Journalistic ethics, separation of news/opinion, bylines
    5. Track Record: Historical accuracy, retractions, fact-checker ratings, awards
    6. Technical Indicators: HTTPS, about page, contact info, domain age
    7. Real-time Reputation: Current controversies, recent fact-checks, public trust

    Use WebSearchTool to:
    - Search for "[source name] media bias fact check"
    - Search for "[source name] credibility rating"
    - Search for "[source name] controversies retractions"
    - Search for "[source name] ownership funding"
    - Verify current reputation and recent issues

    Credibility Levels:
    - VERY_HIGH: Exemplary standards, minimal bias, excellent track record, transparent
    - HIGH: Strong standards, minor bias, good track record, mostly transparent
    - MODERATE: Adequate standards, some bias, mixed track record, some transparency
    - LOW: Poor standards, significant bias, questionable track record, limited transparency
    - VERY_LOW: No standards, extreme bias, poor track record, no transparency
    - UNKNOWN: Insufficient information to assess

    Bias Spectrum:
    - FAR_LEFT/FAR_RIGHT: Extreme bias, propaganda, activism over journalism
    - LEFT/RIGHT: Clear bias, selective reporting, partisan framing
    - CENTER_LEFT/CENTER_RIGHT: Slight bias, generally balanced
    - CENTER: Minimal bias, balanced reporting

    Include fact-checker ratings from:
    - Snopes, FactCheck.org, PolitiFact
    - Media Bias/Fact Check, AllSides
    - International Fact-Checking Network members

    USER:
    Assess the credibility of these news sources:

    Sources: {sources}
    Context: {context}
    Topic Area: {topic_area}
    Time Period: {time_period}

    Use web search to verify current credibility and reputation.
    Provide detailed credibility assessments with educational insights and fact-checker consensus.
    """
)
def assess_source_credibility(
    sources: list[str], context: str = "", topic_area: str = "", time_period: str = "current"
) -> list[SourceCredibility]:
    """Assess the credibility of news sources with enhanced analysis and real-time verification."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=NewsAnalysis,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert news analyst, media literacy educator, and bias detection specialist.
    Your role is to analyze news content for reliability, bias, completeness, potential
    misinformation, and categorize claims for appropriate verification methods.

    Analysis Framework:
    1. Claim Extraction: Identify all factual claims and their sources
    2. Claim Categorization: Classify each claim by type for verification routing
    3. Language Analysis: Detect emotional, loaded, or manipulative language
    4. Context Assessment: Identify missing context, background, or perspectives
    5. Bias Detection: Analyze framing, source selection, and presentation bias
    6. Fact vs Opinion: Clearly distinguish factual claims from opinions
    7. Completeness: Assess how complete and balanced the reporting is
    8. Transparency: Evaluate source attribution and transparency
    9. Misinformation Indicators: Check for common misinformation patterns
    10. Verification Priority: Prioritize claims for fact-checking

    Claim Type Categories:
    - STATISTICAL: Claims involving numbers, percentages, data
    - SCIENTIFIC: Scientific findings, research results
    - MEDICAL: Health claims, medical advice, treatments
    - POLITICAL: Political statements, policy claims
    - HISTORICAL: Historical facts, past events
    - QUOTE: Direct quotes from individuals
    - IMAGE_VIDEO: Claims about visual content
    - SOCIAL_MEDIA: Claims originating from social platforms
    - FINANCIAL: Economic data, market claims
    - LEGAL: Legal claims, court decisions
    - GENERAL: Other factual claims

    Bias Analysis Components:
    - Framing bias: How the story angle affects perception
    - Selection bias: Which facts are included/excluded
    - Source bias: Diversity and balance of sources
    - Language bias: Loaded or emotional language
    - Visual bias: Misleading images or graphics
    - Headline bias: Clickbait or misrepresentation

    Misinformation Types:
    - FABRICATION: Completely false information
    - MANIPULATION: Doctored content or quotes
    - MISREPRESENTATION: True info presented misleadingly
    - FALSE_CONTEXT: Real content in wrong context
    - SATIRE: Humor mistaken for news
    - CLICKBAIT: Sensationalized for clicks
    - PROPAGANDA: Systematic bias for agenda
    - CONSPIRACY_THEORY: Unfounded conspiracy claims

    Verification Priority Factors:
    - Claims that could cause harm if false
    - Claims central to the story's thesis
    - Claims that seem extraordinary or unlikely
    - Claims lacking clear sources
    - Claims contradicting known facts

    USER:
    Analyze this news content comprehensively:

    Article/Content: {article_content}
    Headline: {headline}
    Source Context: {source_context}
    Publication Date: {publication_date}
    Author Information: {author_info}

    Provide detailed analysis with claim categorization for verification routing.
    Identify which claims should be prioritized for fact-checking and why.
    """
)
def analyze_news_content(
    article_content: str, headline: str = "", source_context: str = "", publication_date: str = "", author_info: str = ""
) -> NewsAnalysis:
    """Analyze news content with enhanced bias detection and claim categorization."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[FactCheck],
    tools=[
        WebSearchTool,
        FactCheckSearchTool,
        AcademicSearchTool,
        GovernmentDataTool,
        ReverseImageSearchTool,
        SocialMediaVerificationTool,
        ExpertSourceTool,
    ],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert fact-checker with access to comprehensive verification tools.
    You can search the web, academic databases, government sources, and more.
    Your role is to verify claims using multiple sources and methodologies,
    identify missing context, and provide transparent assessments based on
    the most current and authoritative information available.

    Fact-Checking Methodology:
    1. Claim Isolation: Extract specific, verifiable claims
    2. Multi-Source Verification: Use appropriate tools based on claim type
    3. Cross-Reference: Check multiple independent sources
    4. Context Analysis: Identify crucial missing context
    5. Evidence Quality: Assess strength and reliability of evidence
    6. Consensus Check: Look for fact-checker and expert consensus
    7. Transparency: Document verification process and limitations

    Tool Selection Guide:
    - WebSearchTool: General current information and news
    - FactCheckSearchTool: Existing fact-checks from major organizations
    - AcademicSearchTool: Scientific claims, research findings, medical information
    - GovernmentDataTool: Statistics, official statements, policy claims
    - ReverseImageSearchTool: Verify images or videos mentioned in claims
    - SocialMediaVerificationTool: Quotes, viral posts, social media claims
    - ExpertSourceTool: Complex topics requiring expert analysis

    Verification Strategy:
    1. For statistical claims: Use GovernmentDataTool and AcademicSearchTool
    2. For scientific/medical claims: Use AcademicSearchTool and ExpertSourceTool
    3. For political claims: Use FactCheckSearchTool and GovernmentDataTool
    4. For viral content: Use SocialMediaVerificationTool and ReverseImageSearchTool
    5. For breaking news: Use WebSearchTool and FactCheckSearchTool
    6. Always cross-reference with multiple tool types

    Verification Categories:
    - VERIFIED: Multiple reliable sources confirm, strong evidence
    - PARTIALLY_VERIFIED: Some aspects confirmed, others unclear
    - UNVERIFIED: Insufficient evidence to confirm or deny
    - CONTRADICTED: Reliable sources contradict the claim
    - INSUFFICIENT_EVIDENCE: Not enough information available
    - MISLEADING_CONTEXT: True but presented misleadingly

    Evidence Quality Hierarchy:
    1. Primary sources (official documents, data, recordings)
    2. Peer-reviewed academic research
    3. Government statistics and official statements
    4. Expert consensus from recognized authorities
    5. Established fact-checking organizations
    6. Quality journalism from reputable sources
    7. Direct observations and eyewitness accounts

    Consider these factors:
    - Temporal relevance (when was the claim made vs. current data)
    - Geographic relevance (local vs. global claims)
    - Source authority (expertise in the specific domain)
    - Potential conflicts of interest
    - Consensus across different types of sources

    USER:
    Fact-check these claims with comprehensive verification:

    Claims: {claims}
    Available Sources: {available_sources}
    Context: {context}
    Time Sensitivity: {time_sensitivity}
    Related Fact-Checks: {related_fact_checks}

    Use multiple verification tools appropriate to each claim type.
    Provide comprehensive fact-checking with evidence assessment and missing context identification.
    Document which tools were used and why for transparency.
    """
)
def fact_check_claims(
    claims: list[str], available_sources: list[str], context: str = "", time_sensitivity: str = "", related_fact_checks: str = ""
) -> list[FactCheck]:
    """Fact-check specific claims with enhanced verification methodology and comprehensive tool suite."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=MediaLiteracyReport,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert media literacy educator. Your role is to help readers
    develop critical thinking skills for evaluating news and information.
    Create educational content that empowers readers to verify information independently.

    Media Literacy Framework:
    1. Critical Questions: What readers should ask about any news
    2. Red Flag Identification: Warning signs in this specific content
    3. Verification Skills: Practical tips for fact-checking
    4. Critical Thinking: Prompts for deeper analysis
    5. Resources: Tools and websites for verification
    6. Key Lessons: Transferable media literacy skills

    Educational Approach:
    - Make it practical and actionable
    - Use this content as a teaching example
    - Provide specific, not just general advice
    - Encourage healthy skepticism, not cynicism
    - Promote information verification habits

    Key Questions Framework:
    - Who created this and why?
    - What's the evidence?
    - What's missing?
    - Who benefits from this message?
    - Is this the whole story?

    USER:
    Create a media literacy report for this verification:

    News Analysis: {news_analysis}
    Fact Check Results: {fact_check_results}
    Source Credibility: {source_credibility}
    Verification Findings: {verification_findings}

    Provide educational insights and practical verification guidance.
    """
)
def create_media_literacy_report(
    news_analysis: NewsAnalysis,
    fact_check_results: list[FactCheck],
    source_credibility: list[SourceCredibility],
    verification_findings: str,
) -> BaseDynamicConfig:
    """Create educational media literacy report."""
    return {
        "computed_fields": {
            "news_analysis": news_analysis,
            "fact_check_results": fact_check_results,
            "source_credibility": source_credibility,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=NewsVerification,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert news verification specialist combining fact-checking,
    source analysis, and media literacy education. Your role is to synthesize
    all verification components into a comprehensive, educational report.

    Verification Synthesis Framework:
    1. Source Reliability: Weight findings by source credibility
    2. Claim Verification: Assess overall verification status
    3. Cross-Reference: Analyze consistency across sources
    4. Consensus Level: Determine agreement among reliable sources
    5. Red Flags: Identify misinformation warning signs
    6. Reliability Indicators: Highlight positive credibility factors
    7. Educational Value: Extract media literacy lessons
    8. Actionable Guidance: Provide clear recommendations

    Consider:
    - Pattern recognition in misinformation
    - Common manipulation techniques
    - Importance of primary sources
    - Role of context in understanding
    - Difference between bias and misinformation
    - Value of diverse perspectives

    Alternative Source Recommendations:
    - Suggest diverse, credible sources
    - Include different perspectives
    - Recommend primary sources
    - Suggest fact-checking resources

    USER:
    Synthesize comprehensive news verification:

    Original Article: {original_article}
    Source Credibility: {source_credibility}
    Content Analysis: {content_analysis}
    Fact-Check Results: {fact_check_results}
    Media Literacy Report: {media_literacy_report}
    Additional Context: {additional_context}

    Provide complete verification with educational insights and actionable recommendations.
    """
)
def synthesize_news_verification(
    original_article: str,
    source_credibility: list[SourceCredibility],
    content_analysis: NewsAnalysis,
    fact_check_results: list[FactCheck],
    media_literacy_report: MediaLiteracyReport,
    additional_context: str = "",
) -> BaseDynamicConfig:
    """Synthesize comprehensive news verification with education focus."""
    return {
        "computed_fields": {
            "source_credibility": source_credibility,
            "content_analysis": content_analysis,
            "fact_check_results": fact_check_results,
            "media_literacy_report": media_literacy_report,
        }
    }


async def multi_source_news_verification(
    article_content: str,
    headline: str = "",
    sources: list[str] = None,
    context: str = "",
    topic_area: str = "",
    author_info: str = "",
    check_fact_checkers: bool = True,
    educational_mode: bool = True,
    use_realtime_search: bool = True,
    llm_provider: str = "openai",
    model: str = "gpt-4o",
) -> VerificationResult:
    """
    Verify news articles and claims using enhanced multi-source analysis,
    fact-checking with real-time web search, and media literacy education.

    This enhanced agent assesses source credibility, analyzes content for biases
    and misinformation, fact-checks claims against multiple sources including
    real-time web search, and provides educational insights to improve media literacy.

    Real-time search capabilities:
    - Search current web for claim verification
    - Check fact-checking databases for existing verifications
    - Verify source credibility and recent reputation
    - Find primary sources and official statements

    Args:
        article_content: The news article or content to verify
        headline: Article headline
        sources: List of sources to check against
        context: Additional context about the topic
        topic_area: Subject area of the news
        author_info: Information about the author
        check_fact_checkers: Whether to include fact-checker consensus
        educational_mode: Whether to include media literacy education
        use_realtime_search: Whether to use web search for real-time verification
        llm_provider: LLM provider to use
        model: Model to use for verification

    Returns:
        VerificationResult with comprehensive analysis and educational insights
    """

    if sources is None:
        sources = [
            "Reuters",
            "Associated Press",
            "BBC News",
            "NPR",
            "The Guardian",
            "The New York Times",
            "The Washington Post",
            "Financial Times",
            "The Economist",
            "ProPublica",
        ]

    # Check if real-time search is available
    search_available = DUCKDUCKGO_AVAILABLE or EXA_AVAILABLE
    if use_realtime_search and not search_available:
        print("Real-time search not available. Install duckduckgo-search or set EXA_API_KEY for enhanced verification.")
        use_realtime_search = False

    # Step 1: Assess source credibility
    print("Assessing source credibility...")
    if use_realtime_search:
        print("  ↳ Using real-time web search to verify current reputation...")
    source_credibility = assess_source_credibility(sources=sources, context=context, topic_area=topic_area, time_period="current")
    print(f"Assessed {len(source_credibility)} sources")

    # Step 2: Analyze news content
    print("Analyzing news content...")
    content_analysis = analyze_news_content(
        article_content=article_content,
        headline=headline,
        source_context=context,
        publication_date=datetime.now().strftime("%Y-%m-%d"),
        author_info=author_info,
    )
    print(f"Identified {len(content_analysis.main_claims)} main claims")
    print(f"Found {len(content_analysis.misinformation_indicators)} potential misinformation indicators")

    # Step 3: Fact-check claims
    print("Fact-checking claims...")
    fact_check_results = fact_check_claims(
        claims=content_analysis.main_claims,
        available_sources=sources,
        context=context,
        time_sensitivity="current",
        related_fact_checks="checking fact-checker databases" if check_fact_checkers else "",
    )
    print(f"Fact-checked {len(fact_check_results)} claims")

    # Step 4: Create media literacy report
    media_literacy_report = None
    if educational_mode:
        print("Creating media literacy report...")
        media_literacy_report = create_media_literacy_report(
            news_analysis=content_analysis,
            fact_check_results=fact_check_results,
            source_credibility=source_credibility,
            verification_findings="comprehensive verification completed",
        )
        print(f"Generated {len(media_literacy_report.key_questions)} critical thinking questions")

    # Step 5: Synthesize verification results
    print("Synthesizing verification results...")
    verification = synthesize_news_verification(
        original_article=article_content,
        source_credibility=source_credibility,
        content_analysis=content_analysis,
        fact_check_results=fact_check_results,
        media_literacy_report=media_literacy_report,
        additional_context=context,
    )

    # Step 6: Create final result with enhanced assessments
    verified_claims = sum(1 for fc in fact_check_results if fc.verification_status == VerificationStatus.VERIFIED)
    contradicted_claims = sum(1 for fc in fact_check_results if fc.verification_status == VerificationStatus.CONTRADICTED)
    total_claims = len(fact_check_results)

    # Calculate confidence score
    confidence_score = 0.0
    if total_claims > 0:
        verification_weight = verified_claims / total_claims * 0.4
        source_weight = (
            sum(
                {"very_high": 1.0, "high": 0.8, "moderate": 0.6, "low": 0.3, "very_low": 0.1, "unknown": 0.5}[
                    sc.credibility_level.value
                ]
                for sc in source_credibility
            )
            / len(source_credibility)
            * 0.3
            if source_credibility
            else 0.15
        )
        transparency_weight = content_analysis.transparency_score * 0.2
        completeness_weight = content_analysis.completeness_score * 0.1
        confidence_score = verification_weight + source_weight + transparency_weight + completeness_weight

    # Determine overall credibility
    avg_credibility_score = (
        sum(
            {"very_high": 5, "high": 4, "moderate": 3, "low": 2, "very_low": 1, "unknown": 2.5}[sc.credibility_level.value]
            for sc in source_credibility
        )
        / len(source_credibility)
        if source_credibility
        else 2.5
    )

    if contradicted_claims > total_claims * 0.5:
        overall_credibility = CredibilityLevel.VERY_LOW
    elif avg_credibility_score >= 4.5 and verified_claims > total_claims * 0.8:
        overall_credibility = CredibilityLevel.VERY_HIGH
    elif avg_credibility_score >= 3.5 and verified_claims > total_claims * 0.6:
        overall_credibility = CredibilityLevel.HIGH
    elif avg_credibility_score >= 2.5:
        overall_credibility = CredibilityLevel.MODERATE
    elif avg_credibility_score >= 1.5:
        overall_credibility = CredibilityLevel.LOW
    else:
        overall_credibility = CredibilityLevel.VERY_LOW

    # Assess misinformation risk
    misinformation_risk = "Low"
    if len(content_analysis.misinformation_indicators) > 3:
        misinformation_risk = "High"
    elif len(content_analysis.misinformation_indicators) > 1 or contradicted_claims > 0:
        misinformation_risk = "Moderate"

    # Determine sharing recommendations
    if overall_credibility in [CredibilityLevel.VERY_HIGH, CredibilityLevel.HIGH] and misinformation_risk == "Low":
        share_recommendations = "Safe to share with confidence. Consider adding context about verification."
    elif overall_credibility == CredibilityLevel.MODERATE:
        share_recommendations = "Share with caution. Include caveats about unverified claims."
    else:
        share_recommendations = "Not recommended for sharing. High risk of spreading misinformation."

    final_result = VerificationResult(
        verification=verification,
        overall_credibility=overall_credibility,
        misinformation_risk=misinformation_risk,
        key_findings=[
            f"Verified {verified_claims}/{total_claims} main claims",
            f"Average source credibility: {overall_credibility.value}",
            f"Bias level: {content_analysis.bias_analysis.bias_type}",
            f"Transparency score: {content_analysis.transparency_score:.2f}",
            f"Misinformation indicators: {len(content_analysis.misinformation_indicators)}",
        ],
        confidence_score=confidence_score,
        action_recommendations=[
            "Cross-reference with primary sources when available",
            "Check for updates or corrections to this story",
            "Consider the source's track record and potential biases",
            "Look for expert opinions on technical claims",
            "Be aware of emotional language that may influence perception",
        ],
        follow_up_suggestions=[
            "Monitor how this story develops over time",
            "Check specialized fact-checking websites",
            "Seek out diverse perspectives on this topic",
            "Consult subject matter experts for technical details",
            "Review primary documents if referenced",
        ],
        share_recommendations=share_recommendations,
        educational_value=f"This verification demonstrates {len(verification.media_literacy_report.media_literacy_lessons)} key media literacy concepts",
    )

    print("Enhanced news verification complete!")
    return final_result


async def multi_source_news_verification_stream(
    article_content: str, headline: str = "", use_realtime_search: bool = True, **kwargs
) -> AsyncGenerator[str, None]:
    """Stream the enhanced news verification process with optional real-time search."""

    yield "Starting enhanced multi-source news verification...\n\n"
    if headline:
        yield f"**Headline:** {headline}\n\n"

    if use_realtime_search:
        if DUCKDUCKGO_AVAILABLE or EXA_AVAILABLE:
            yield "Real-time web search enabled for current information\n\n"
        else:
            yield "Real-time search not available - install duckduckgo-search or set EXA_API_KEY\n\n"

    # Perform verification
    result = await multi_source_news_verification(article_content, headline, use_realtime_search=use_realtime_search, **kwargs)

    yield "## Overall Assessment\n\n"
    yield f"**Credibility Level:** {result.overall_credibility.value.replace('_', ' ').title()}\n"
    yield f"**Misinformation Risk:** {result.misinformation_risk}\n"
    yield f"**Confidence Score:** {result.confidence_score:.2f}/1.0\n\n"

    yield "## Source Credibility Analysis\n\n"
    for source in result.verification.source_credibility[:5]:  # Show top 5
        yield f"**{source.source_name}**\n"
        yield f"- Credibility: {source.credibility_level.value.replace('_', ' ').title()}\n"
        yield f"- Bias: {source.bias_direction.value.replace('_', ' ').title()}\n"
        yield f"- Factual Reporting: {source.factual_reporting}\n"
        if source.fact_checker_ratings:
            yield f"- Fact-Checker Ratings: {', '.join(source.fact_checker_ratings.values())}\n"
        yield "\n"

    yield "## Content Analysis\n\n"
    analysis = result.verification.news_analysis
    yield f"**Main Claims:** {len(analysis.main_claims)}\n"
    yield f"**Transparency Score:** {analysis.transparency_score:.2f}/1.0\n"
    yield f"**Completeness Score:** {analysis.completeness_score:.2f}/1.0\n"
    yield f"**Sensationalism Score:** {analysis.sensationalism_score:.2f}/1.0\n\n"

    if analysis.misinformation_indicators:
        yield "**Misinformation Indicators:**\n"
        for indicator in analysis.misinformation_indicators:
            yield f"- {indicator.value.replace('_', ' ').title()}\n"
        yield "\n"

    yield "**Bias Analysis:**\n"
    yield f"- Type: {analysis.bias_analysis.bias_type}\n"
    yield f"- Framing: {analysis.bias_analysis.framing_analysis}\n"
    if analysis.bias_analysis.loaded_language:
        yield f"- Loaded Language: {', '.join(analysis.bias_analysis.loaded_language[:3])}\n"
    yield "\n"

    yield "## Fact-Check Results\n\n"
    for i, fc in enumerate(result.verification.fact_checks[:5], 1):  # Show first 5
        yield f"**Claim {i}:** {fc.claim[:100]}...\n"
        yield f"- Status: {fc.verification_status.value.replace('_', ' ').title()}\n"
        yield f"- Confidence: {fc.confidence_level:.2f}/1.0\n"
        if fc.fact_checker_consensus:
            yield f"- Fact-Checker Consensus: {fc.fact_checker_consensus}\n"
        yield "\n"

    if kwargs.get('educational_mode', True):
        yield "## Media Literacy Insights\n\n"
        ml_report = result.verification.media_literacy_report

        yield "**Key Questions to Ask:**\n"
        for question in ml_report.key_questions[:3]:
            yield f"- {question}\n"

        yield "\n**Red Flags Found:**\n"
        for flag in ml_report.red_flags_found[:3]:
            yield f"- {flag}\n"

        yield "\n**Verification Tips:**\n"
        for tip in ml_report.verification_tips[:3]:
            yield f"- {tip}\n"
        yield "\n"

    yield "## Key Findings\n\n"
    for finding in result.key_findings:
        yield f"- {finding}\n"

    yield "\n## Sharing Recommendation\n\n"
    yield f"{result.share_recommendations}\n\n"

    yield "## Action Recommendations\n\n"
    for rec in result.action_recommendations:
        yield f"- {rec}\n"

    yield "\n## Follow-up Suggestions\n\n"
    for suggestion in result.follow_up_suggestions:
        yield f"- {suggestion}\n"

    yield f"\n**Educational Value:** {result.educational_value}\n"
