from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Optional


class SocialPlatform(str, Enum):
    """Supported social media platforms."""
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    THREADS = "threads"
    MASTODON = "mastodon"
    REDDIT = "reddit"
    PINTEREST = "pinterest"
    BLUESKY = "bluesky"


class ContentType(str, Enum):
    """Types of social media content."""
    TEXT_POST = "text_post"
    IMAGE_POST = "image_post"
    VIDEO_POST = "video_post"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    THREAD = "thread"
    POLL = "poll"
    LIVE_STREAM = "live_stream"
    ARTICLE = "article"
    INFOGRAPHIC = "infographic"
    MEME = "meme"


class PostingTime(str, Enum):
    """Optimal posting times."""
    EARLY_MORNING = "early_morning"  # 5-7 AM
    MORNING = "morning"  # 7-9 AM
    MID_MORNING = "mid_morning"  # 9-11 AM
    LUNCH = "lunch"  # 11 AM-1 PM
    AFTERNOON = "afternoon"  # 1-4 PM
    EVENING = "evening"  # 4-7 PM
    NIGHT = "night"  # 7-10 PM
    LATE_NIGHT = "late_night"  # 10 PM-12 AM


class EngagementMetric(str, Enum):
    """Types of engagement metrics."""
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CLICKS = "clicks"
    IMPRESSIONS = "impressions"
    REACH = "reach"
    ENGAGEMENT_RATE = "engagement_rate"


class TrendAnalysis(BaseModel):
    """Analysis of current trends relevant to the campaign."""
    trending_topics: list[str] = Field(..., description="Currently trending topics")
    trending_hashtags: dict[str, list[str]] = Field(..., description="Trending hashtags per platform")
    viral_content_patterns: list[str] = Field(..., description="Patterns in viral content")
    audience_sentiment: dict[str, str] = Field(..., description="Current audience sentiment per topic")
    opportunity_windows: list[str] = Field(..., description="Time-sensitive opportunities")
    competitor_activity: list[str] = Field(..., description="Notable competitor activities")
    recommended_angles: list[str] = Field(..., description="Recommended content angles based on trends")


class EngagementAnalysis(BaseModel):
    """Predicted engagement analysis for content."""
    predicted_metrics: dict[EngagementMetric, float] = Field(..., description="Predicted engagement metrics")
    engagement_score: float = Field(..., description="Overall engagement score (0-1)")
    virality_potential: float = Field(..., description="Potential for viral spread (0-1)")
    audience_resonance: float = Field(..., description="Expected audience resonance (0-1)")
    optimal_timing_score: float = Field(..., description="Timing optimization score (0-1)")
    improvement_suggestions: list[str] = Field(..., description="Suggestions to improve engagement")


class PlatformStrategy(BaseModel):
    """Enhanced strategy for a specific platform."""
    platform: SocialPlatform = Field(..., description="Social media platform")
    target_audience: str = Field(..., description="Target audience for this platform")
    audience_size: str = Field(..., description="Estimated audience size")
    content_pillars: list[str] = Field(..., description="Main content themes/pillars")
    posting_frequency: str = Field(..., description="How often to post")
    optimal_times: list[PostingTime] = Field(..., description="Best times to post")
    content_types: list[ContentType] = Field(..., description="Preferred content types")
    hashtag_strategy: str = Field(..., description="Hashtag usage strategy")
    engagement_tactics: list[str] = Field(..., description="Tactics to increase engagement")
    platform_specific_tips: list[str] = Field(..., description="Platform-specific best practices")
    algorithm_considerations: list[str] = Field(..., description="Platform algorithm optimization tips")
    community_management: str = Field(..., description="Community engagement approach")


class PlatformContent(BaseModel):
    """Enhanced content optimized for a specific platform."""
    platform: SocialPlatform = Field(..., description="Target platform")
    content_type: ContentType = Field(..., description="Type of content")
    primary_text: str = Field(..., description="Main text content")
    secondary_text: str | None = Field(None, description="Secondary text (e.g., first comment)")
    hashtags: list[str] = Field(..., description="Relevant hashtags")
    mentions: list[str] = Field(default_factory=list, description="Accounts to mention")
    call_to_action: str = Field(..., description="Call to action")
    visual_description: str | None = Field(None, description="Description of visual elements")
    alt_text: str | None = Field(None, description="Accessibility alt text")
    posting_time: PostingTime = Field(..., description="Recommended posting time")
    engagement_hooks: list[str] = Field(..., description="Elements to drive engagement")
    character_count: int = Field(..., description="Character count for the post")
    platform_compliance: list[str] = Field(..., description="Platform-specific compliance notes")
    engagement_prediction: EngagementAnalysis = Field(..., description="Predicted engagement metrics")


class ContentOptimization(BaseModel):
    """Enhanced content optimization analysis."""
    original_message: str = Field(..., description="Original message to optimize")
    platform_adaptations: list[PlatformContent] = Field(..., description="Platform-specific versions")
    cross_platform_strategy: str = Field(..., description="Strategy for cross-platform consistency")
    timing_recommendations: dict[str, str] = Field(..., description="Timing for each platform")
    performance_predictions: dict[str, float] = Field(..., description="Predicted engagement scores")
    a_b_test_suggestions: list[str] = Field(..., description="A/B testing recommendations")
    trend_alignment: list[str] = Field(..., description="How content aligns with current trends")
    risk_assessment: list[str] = Field(..., description="Potential risks or sensitivities")


class ContentCalendar(BaseModel):
    """Enhanced social media content calendar."""
    campaign_name: str = Field(..., description="Name of the campaign")
    duration: str = Field(..., description="Campaign duration")
    daily_schedule: dict[str, list[PlatformContent]] = Field(..., description="Daily content schedule")
    weekly_themes: list[str] = Field(..., description="Weekly content themes")
    key_dates: dict[str, str] = Field(..., description="Important dates and events")
    content_mix: dict[str, float] = Field(..., description="Percentage breakdown of content types")
    engagement_goals: dict[str, str] = Field(..., description="Engagement goals per platform")
    contingency_content: list[str] = Field(..., description="Backup content for flexibility")
    real_time_slots: list[str] = Field(..., description="Slots reserved for real-time content")


class SocialMediaCampaign(BaseModel):
    """Enhanced complete social media campaign."""
    campaign_overview: str = Field(..., description="Campaign overview and objectives")
    trend_analysis: TrendAnalysis = Field(..., description="Current trend analysis")
    platform_strategies: list[PlatformStrategy] = Field(..., description="Strategies per platform")
    content_optimization: ContentOptimization = Field(..., description="Content optimization analysis")
    content_calendar: ContentCalendar = Field(..., description="Content calendar and schedule")
    success_metrics: list[str] = Field(..., description="Key performance indicators")
    budget_allocation: dict[str, str] = Field(..., description="Budget allocation per platform")
    risk_mitigation: list[str] = Field(..., description="Risk mitigation strategies")
    monitoring_plan: str = Field(..., description="Plan for monitoring and adjustments")
    crisis_management: list[str] = Field(..., description="Crisis management protocols")
    growth_projections: dict[str, str] = Field(..., description="Expected growth metrics")


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=TrendAnalysis,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert social media trend analyst with deep knowledge of viral content,
    platform algorithms, and audience behavior patterns. Your role is to identify
    current trends and opportunities for maximum campaign impact.

    Analyze trends across:
    1. Trending topics and conversations
    2. Viral content patterns and formats
    3. Hashtag performance and reach
    4. Audience sentiment and mood
    5. Competitor strategies and successes
    6. Platform algorithm changes
    7. Cultural moments and events

    Consider:
    - Real-time relevance
    - Brand safety and appropriateness
    - Audience alignment
    - Competitive advantage
    - Timing opportunities
    - Content format trends

    USER:
    Analyze current trends for this campaign:

    Campaign Goal: {campaign_goal}
    Target Audience: {target_audience}
    Industry: {industry}
    Platforms: {platforms}
    Time Period: {time_period}
    Brand Values: {brand_values}

    Provide comprehensive trend analysis with actionable opportunities.
    """
)
def analyze_current_trends(
    campaign_goal: str,
    target_audience: str,
    industry: str,
    platforms: list[str],
    time_period: str = "next 30 days",
    brand_values: str = ""
) -> TrendAnalysis:
    """Analyze current social media trends relevant to the campaign."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[PlatformStrategy],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert social media strategist with deep knowledge of all major platforms.
    Your role is to create platform-specific strategies that maximize engagement and reach
    while maintaining brand consistency and leveraging current trends.

    Platform Characteristics (Updated 2024):
    - TWITTER: Real-time, 280 chars, threads, communities, audio spaces
    - LINKEDIN: Professional, thought leadership, video priority, newsletters
    - INSTAGRAM: Visual-first, reels dominance, stories, shopping, broadcast channels
    - FACEBOOK: Community groups, video priority, events, marketplace integration
    - TIKTOK: Short videos, trends, sounds, effects, live streaming, shop
    - YOUTUBE: Long-form, shorts, community posts, memberships, premieres
    - THREADS: Text-based conversations, Twitter alternative, Meta integration
    - REDDIT: Community-driven, authenticity crucial, AMAs, awards
    - PINTEREST: Visual discovery, idea pins, shopping, seasonal content
    - BLUESKY: Decentralized, customizable feeds, developer-friendly

    For each platform, consider:
    1. Latest algorithm changes and priorities
    2. Emerging content formats and features
    3. Platform-specific audience behaviors
    4. Optimal content mix and frequency
    5. Community building strategies
    6. Monetization opportunities
    7. Cross-platform synergies

    USER:
    Create platform-specific strategies for this campaign:

    Campaign Goal: {campaign_goal}
    Target Audience: {target_audience}
    Brand Voice: {brand_voice}
    Platforms: {platforms}
    Budget: {budget}
    Timeline: {timeline}
    Trend Analysis: {trend_analysis}
    Competitive Landscape: {competitive_landscape}

    Develop comprehensive strategies for each platform with specific tactics and recommendations.
    """
)
def develop_platform_strategies(
    campaign_goal: str,
    target_audience: str,
    brand_voice: str,
    platforms: list[str],
    budget: str = "",
    timeline: str = "",
    trend_analysis: TrendAnalysis = None,
    competitive_landscape: str = ""
) -> BaseDynamicConfig:
    """Develop enhanced platform-specific social media strategies."""
    return {
        "computed_fields": {
            "trend_analysis": trend_analysis,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=EngagementAnalysis,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert in social media analytics and engagement prediction.
    Your role is to analyze content and predict its engagement performance
    based on current trends, platform algorithms, and audience behavior.

    Engagement Factors to Consider:
    1. Content relevance to target audience
    2. Timing and platform algorithm alignment
    3. Visual appeal and format optimization
    4. Emotional triggers and hooks
    5. Call-to-action effectiveness
    6. Hashtag and keyword optimization
    7. Current trend alignment
    8. Competition and content saturation

    Prediction Methodology:
    - Historical performance patterns
    - Current platform algorithm preferences
    - Audience activity patterns
    - Content quality indicators
    - Viral potential markers
    - Engagement rate benchmarks

    USER:
    Predict engagement for this content:

    Platform: {platform}
    Content Type: {content_type}
    Content: {content}
    Target Audience: {target_audience}
    Posting Time: {posting_time}
    Current Trends: {current_trends}
    Historical Performance: {historical_performance}

    Provide detailed engagement predictions with improvement suggestions.
    """
)
def predict_content_engagement(
    platform: str,
    content_type: str,
    content: str,
    target_audience: str,
    posting_time: str,
    current_trends: str = "",
    historical_performance: str = ""
) -> EngagementAnalysis:
    """Predict engagement metrics for social media content."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=ContentOptimization,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert content optimization specialist with deep knowledge of
    platform-specific best practices, viral content patterns, and audience psychology.
    Your role is to adapt content for maximum impact across different platforms.

    Platform Optimization Guidelines (2024 Updates):

    TWITTER:
    - 280 character limit, but shorter performs better
    - Thread for complex topics (number each tweet)
    - 1-2 hashtags max, trending topics integration
    - Include polls, GIFs, or images for 2x engagement
    - Best times: 9-10 AM, 7-9 PM (user timezone)

    LINKEDIN:
    - Professional tone, 1300-2000 characters optimal
    - Start with a hook, use line breaks
    - 3-5 professional hashtags
    - Native video gets 5x more engagement
    - Document posts for thought leadership

    INSTAGRAM:
    - Reels prioritized by algorithm (7-15 seconds optimal)
    - Carousel posts for educational content
    - 5-10 hashtags in first comment
    - Stories for behind-the-scenes
    - Use trending audio for reels

    TIKTOK:
    - 15-30 seconds optimal for completion rate
    - Hook in first 3 seconds crucial
    - Trending sounds and effects essential
    - Native creation preferred over reposts
    - Respond to comments with videos

    For each platform:
    1. Adapt message for platform culture
    2. Optimize for algorithm preferences
    3. Include platform-specific features
    4. Predict engagement performance
    5. Suggest A/B test variations
    6. Align with current trends

    USER:
    Optimize this content for multiple platforms:

    Original Message: {original_message}
    Target Platforms: {target_platforms}
    Campaign Context: {campaign_context}
    Brand Guidelines: {brand_guidelines}
    Target Audience: {target_audience}
    Trend Analysis: {trend_analysis}
    Performance Goals: {performance_goals}

    Create platform-optimized versions with engagement predictions and testing suggestions.
    """
)
def optimize_content_for_platforms(
    original_message: str,
    target_platforms: list[str],
    campaign_context: str = "",
    brand_guidelines: str = "",
    target_audience: str = "",
    trend_analysis: TrendAnalysis = None,
    performance_goals: str = ""
) -> BaseDynamicConfig:
    """Optimize content for multiple social media platforms with engagement predictions."""
    # For each platform, predict engagement
    platform_contents: list[PlatformContent] = []

    return {
        "computed_fields": {
            "trend_analysis": trend_analysis,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=ContentCalendar,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert social media calendar strategist specializing in
    multi-platform campaign orchestration. Your role is to create comprehensive
    content calendars that balance consistency, variety, platform optimization,
    and real-time flexibility.

    Calendar Planning Principles:
    1. Platform-Specific Optimization: Respect each platform's peak times and audience behavior
    2. Content Variety: Balance educational (40%), entertaining (30%), promotional (20%), engaging (10%)
    3. Trend Integration: Reserve slots for trending topics and real-time marketing
    4. Cross-Platform Storytelling: Create narrative arcs across platforms
    5. Algorithm Optimization: Space content to maximize algorithmic reach
    6. Community Building: Include interactive and user-generated content

    Weekly Structure Framework:
    - Monday: Motivational/Week ahead content
    - Tuesday: Educational/How-to content
    - Wednesday: Community engagement/UGC
    - Thursday: Behind-the-scenes/Culture
    - Friday: Entertainment/Fun content
    - Weekend: Inspirational/Lifestyle content

    Timing Optimization:
    - Consider timezone differences for global audiences
    - Platform-specific peak times
    - Audience online behavior patterns
    - Competition posting schedules

    USER:
    Create a comprehensive content calendar:

    Campaign Duration: {campaign_duration}
    Platform Strategies: {platform_strategies}
    Content Themes: {content_themes}
    Key Events/Dates: {key_events}
    Posting Frequency: {posting_frequency}
    Resource Constraints: {resource_constraints}
    Trend Windows: {trend_windows}
    Performance Targets: {performance_targets}

    Develop a detailed calendar with daily content recommendations, timing, and contingencies.
    """
)
def create_content_calendar(
    campaign_duration: str,
    platform_strategies: list[PlatformStrategy],
    content_themes: list[str],
    key_events: str = "",
    posting_frequency: str = "",
    resource_constraints: str = "",
    trend_windows: str = "",
    performance_targets: str = ""
) -> BaseDynamicConfig:
    """Create an enhanced social media content calendar with flexibility for trends."""
    return {
        "computed_fields": {
            "platform_strategies": platform_strategies,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=SocialMediaCampaign,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert social media campaign director with expertise in
    multi-platform orchestration, trend leveraging, and performance optimization.
    Your role is to synthesize all campaign elements into a comprehensive,
    executable strategy with built-in adaptability and crisis management.

    Campaign Synthesis Framework:
    1. Strategic Alignment: Ensure all elements support core objectives
    2. Platform Synergy: Create cross-platform amplification effects
    3. Trend Integration: Build in flexibility for real-time opportunities
    4. Risk Management: Identify and mitigate potential issues
    5. Performance Tracking: Define clear KPIs and monitoring systems
    6. Budget Optimization: Allocate resources for maximum ROI
    7. Crisis Protocols: Establish response procedures
    8. Growth Planning: Project outcomes and scaling strategies

    Success Metrics Framework:
    - Awareness: Reach, impressions, brand mention growth
    - Engagement: Likes, comments, shares, saves, engagement rate
    - Community: Follower growth, community sentiment, UGC volume
    - Conversion: Click-through rate, conversion rate, ROI
    - Brand Health: Sentiment analysis, share of voice, brand affinity

    Risk Considerations:
    - Platform algorithm changes
    - Negative feedback or crisis situations
    - Competitor responses
    - Content saturation
    - Budget constraints
    - Team capacity

    USER:
    Synthesize the complete social media campaign:

    Campaign Objective: {campaign_objective}
    Trend Analysis: {trend_analysis}
    Platform Strategies: {platform_strategies}
    Content Optimization: {content_optimization}
    Content Calendar: {content_calendar}
    Budget: {budget}
    Success Criteria: {success_criteria}
    Risk Factors: {risk_factors}

    Create a comprehensive campaign plan with execution details, success metrics, and contingencies.
    """
)
def synthesize_social_media_campaign(
    campaign_objective: str,
    trend_analysis: TrendAnalysis,
    platform_strategies: list[PlatformStrategy],
    content_optimization: ContentOptimization,
    content_calendar: ContentCalendar,
    budget: str = "",
    success_criteria: str = "",
    risk_factors: str = ""
) -> BaseDynamicConfig:
    """Synthesize complete social media campaign with enhanced features."""
    return {
        "computed_fields": {
            "trend_analysis": trend_analysis,
            "platform_strategies": platform_strategies,
            "content_optimization": content_optimization,
            "content_calendar": content_calendar,
        }
    }


async def multi_platform_social_media_manager(
    campaign_goal: str,
    target_audience: str,
    brand_voice: str,
    platforms: list[str],
    content_themes: list[str],
    campaign_duration: str = "1 month",
    budget: str = "",
    timeline: str = "",
    sample_message: str = "",
    industry: str = "",
    competitive_landscape: str = "",
    performance_goals: str = "",
    llm_provider: str = "openai",
    model: str = "gpt-4o"
) -> SocialMediaCampaign:
    """
    Create and manage comprehensive multi-platform social media campaigns with
    trend analysis, engagement prediction, and real-time adaptation capabilities.

    This enhanced agent develops platform-specific strategies, analyzes trends,
    optimizes content with engagement predictions, creates flexible content calendars,
    and provides comprehensive campaign management with crisis protocols.

    Args:
        campaign_goal: Primary goal of the social media campaign
        target_audience: Target audience description
        brand_voice: Brand voice and personality
        platforms: List of social media platforms to target
        content_themes: Main content themes and topics
        campaign_duration: Duration of the campaign
        budget: Available budget for the campaign
        timeline: Campaign timeline and milestones
        sample_message: Sample message to optimize across platforms
        industry: Industry or sector for trend analysis
        competitive_landscape: Information about competitors
        performance_goals: Specific performance targets
        llm_provider: LLM provider to use
        model: Model to use for campaign creation

    Returns:
        SocialMediaCampaign with comprehensive multi-platform strategy
    """

    # Step 1: Analyze current trends
    print("Analyzing current trends and opportunities...")
    trend_analysis = analyze_current_trends(
        campaign_goal=campaign_goal,
        target_audience=target_audience,
        industry=industry or "general",
        platforms=platforms,
        time_period=campaign_duration,
        brand_values=brand_voice
    )
    print(f"Identified {len(trend_analysis.trending_topics)} trending topics and {len(trend_analysis.opportunity_windows)} opportunity windows")

    # Step 2: Develop platform-specific strategies
    print("Developing platform-specific strategies...")
    platform_strategies = develop_platform_strategies(
        campaign_goal=campaign_goal,
        target_audience=target_audience,
        brand_voice=brand_voice,
        platforms=platforms,
        budget=budget,
        timeline=timeline,
        trend_analysis=trend_analysis,
        competitive_landscape=competitive_landscape
    )
    print(f"Created strategies for {len(platform_strategies)} platforms")

    # Step 3: Optimize content for platforms with engagement predictions
    print("Optimizing content for platforms...")
    if not sample_message:
        sample_message = f"Exciting campaign about {campaign_goal} for {target_audience}"

    content_optimization = optimize_content_for_platforms(
        original_message=sample_message,
        target_platforms=platforms,
        campaign_context=campaign_goal,
        brand_guidelines=brand_voice,
        target_audience=target_audience,
        trend_analysis=trend_analysis,
        performance_goals=performance_goals
    )

    # Predict engagement for each platform adaptation
    for platform_content in content_optimization.platform_adaptations:
        engagement_prediction = predict_content_engagement(
            platform=platform_content.platform.value,
            content_type=platform_content.content_type.value,
            content=platform_content.primary_text,
            target_audience=target_audience,
            posting_time=platform_content.posting_time.value,
            current_trends=", ".join(trend_analysis.trending_topics[:3]),
            historical_performance=""
        )
        platform_content.engagement_prediction = engagement_prediction

    print(f"Optimized content for {len(content_optimization.platform_adaptations)} platforms with engagement predictions")

    # Step 4: Create flexible content calendar
    print("Creating adaptive content calendar...")
    content_calendar = create_content_calendar(
        campaign_duration=campaign_duration,
        platform_strategies=platform_strategies,
        content_themes=content_themes,
        key_events=timeline,
        posting_frequency="optimized per platform",
        resource_constraints=budget,
        trend_windows=", ".join(trend_analysis.opportunity_windows),
        performance_targets=performance_goals
    )
    print(f"Created {campaign_duration} content calendar with trend flexibility")

    # Step 5: Synthesize complete campaign
    print("Synthesizing comprehensive campaign strategy...")
    complete_campaign = synthesize_social_media_campaign(
        campaign_objective=campaign_goal,
        trend_analysis=trend_analysis,
        platform_strategies=platform_strategies,
        content_optimization=content_optimization,
        content_calendar=content_calendar,
        budget=budget,
        success_criteria=performance_goals or f"Achieve {campaign_goal} through multi-platform engagement",
        risk_factors=competitive_landscape
    )

    print("Enhanced multi-platform social media campaign ready!")
    return complete_campaign


async def multi_platform_social_media_manager_stream(
    campaign_goal: str,
    target_audience: str,
    brand_voice: str,
    platforms: list[str],
    content_themes: list[str],
    **kwargs
) -> AsyncGenerator[str, None]:
    """Stream the enhanced social media campaign creation process."""

    yield "Creating enhanced multi-platform social media campaign...\n\n"
    yield f"**Campaign Goal:** {campaign_goal}\n"
    yield f"**Target Audience:** {target_audience}\n"
    yield f"**Platforms:** {', '.join(platforms)}\n"
    yield f"**Content Themes:** {', '.join(content_themes)}\n\n"

    # Create the campaign
    campaign = await multi_platform_social_media_manager(
        campaign_goal, target_audience, brand_voice, platforms, content_themes, **kwargs
    )

    yield "## Campaign Overview\n\n"
    yield f"{campaign.campaign_overview}\n\n"

    yield "## Trend Analysis\n\n"
    yield f"**Trending Topics:** {', '.join(campaign.trend_analysis.trending_topics[:5])}\n"
    yield "**Opportunity Windows:**\n"
    for opportunity in campaign.trend_analysis.opportunity_windows[:3]:
        yield f"- {opportunity}\n"
    yield "\n"

    yield "## Platform Strategies\n\n"
    for strategy in campaign.platform_strategies:
        yield f"### {strategy.platform.value.title()}\n"
        yield f"**Target Audience:** {strategy.target_audience}\n"
        yield f"**Posting Frequency:** {strategy.posting_frequency}\n"
        yield f"**Content Pillars:** {', '.join(strategy.content_pillars)}\n"
        yield f"**Algorithm Tips:** {', '.join(strategy.algorithm_considerations[:2])}\n\n"

    yield "## Content Optimization\n\n"
    yield f"**Cross-Platform Strategy:** {campaign.content_optimization.cross_platform_strategy}\n\n"

    yield "**Platform Adaptations with Engagement Predictions:**\n"
    for content in campaign.content_optimization.platform_adaptations[:3]:  # Show first 3
        yield f"\n**{content.platform.value.title()}:**\n"
        yield f"- Content: {content.primary_text[:100]}...\n"
        yield f"- Engagement Score: {content.engagement_prediction.engagement_score:.2f}/1.0\n"
        yield f"- Virality Potential: {content.engagement_prediction.virality_potential:.2f}/1.0\n"
    yield "\n"

    yield "## Content Calendar\n\n"
    yield f"**Campaign Duration:** {campaign.content_calendar.duration}\n"
    yield f"**Weekly Themes:** {', '.join(campaign.content_calendar.weekly_themes)}\n"
    yield f"**Real-Time Slots:** {len(campaign.content_calendar.real_time_slots)} reserved for trending content\n\n"

    yield "## Success Metrics\n\n"
    for metric in campaign.success_metrics:
        yield f"- {metric}\n"

    yield "\n## Growth Projections\n\n"
    for platform, projection in campaign.growth_projections.items():
        yield f"- **{platform}:** {projection}\n"

    yield "\n## Crisis Management Protocols\n\n"
    for protocol in campaign.crisis_management[:3]:
        yield f"- {protocol}\n"

    yield "\n## Monitoring Plan\n\n"
    yield f"{campaign.monitoring_plan}\n"
