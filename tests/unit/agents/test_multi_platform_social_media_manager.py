"""Test suite for multi_platform_social_media_manager following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestMultiPlatformSocialMediaManager(BaseAgentTest):
    """Test cases for multi-platform social media manager agent."""

    component_name = "multi_platform_social_media_manager"
    component_path = Path("packages/sygaldry_registry/components/agents/multi_platform_social_media_manager")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.multi_platform_social_media_manager

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "campaign_goal": "Increase brand awareness for eco-friendly products",
                "target_audience": "Millennials and Gen Z interested in sustainability",
                "brand_voice": "Friendly, informative, and passionate about the environment",
                "platforms": ["twitter", "instagram", "linkedin"],
                "content_themes": ["sustainability", "eco-tips", "product features"],
                "campaign_duration": "1 month",
                "sample_message": "Discover our new line of sustainable products that help you live green!",
            },
            {
                "campaign_goal": "Launch new SaaS product for remote teams",
                "target_audience": "Tech professionals and remote team managers",
                "brand_voice": "Professional, innovative, and solution-focused",
                "platforms": ["linkedin", "twitter", "facebook"],
                "content_themes": ["productivity", "remote work", "team collaboration"],
                "budget": "$5,000",
                "timeline": "Q1 2024",
                "industry": "Technology/SaaS",
            },
            {
                "campaign_goal": "Drive holiday sales for fashion brand",
                "target_audience": "Fashion-conscious women aged 25-45",
                "brand_voice": "Trendy, inspiring, and luxurious",
                "platforms": ["instagram", "tiktok", "pinterest"],
                "content_themes": ["holiday fashion", "gift ideas", "style tips"],
                "campaign_duration": "6 weeks",
                "performance_goals": "50% increase in website traffic, 30% boost in sales",
            },
        ]

    @pytest.mark.unit
    def test_enum_definitions(self):
        """Test that all enums are properly defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test SocialPlatform enum
        assert hasattr(module, 'SocialPlatform')
        SocialPlatform = module.SocialPlatform
        expected_platforms = [
            "TWITTER",
            "LINKEDIN",
            "INSTAGRAM",
            "FACEBOOK",
            "TIKTOK",
            "YOUTUBE",
            "THREADS",
            "MASTODON",
            "REDDIT",
            "PINTEREST",
            "BLUESKY",
        ]
        for platform in expected_platforms:
            assert hasattr(SocialPlatform, platform)

        # Test ContentType enum
        assert hasattr(module, 'ContentType')
        ContentType = module.ContentType
        expected_content_types = [
            "TEXT_POST",
            "IMAGE_POST",
            "VIDEO_POST",
            "CAROUSEL",
            "STORY",
            "REEL",
            "THREAD",
            "POLL",
            "LIVE_STREAM",
            "ARTICLE",
            "INFOGRAPHIC",
            "MEME",
        ]
        for content_type in expected_content_types:
            assert hasattr(ContentType, content_type)

        # Test PostingTime enum
        assert hasattr(module, 'PostingTime')
        PostingTime = module.PostingTime
        expected_times = ["EARLY_MORNING", "MORNING", "MID_MORNING", "LUNCH", "AFTERNOON", "EVENING", "NIGHT", "LATE_NIGHT"]
        for time_slot in expected_times:
            assert hasattr(PostingTime, time_slot)

        # Test EngagementMetric enum
        assert hasattr(module, 'EngagementMetric')
        EngagementMetric = module.EngagementMetric
        expected_metrics = ["LIKES", "COMMENTS", "SHARES", "SAVES", "CLICKS", "IMPRESSIONS", "REACH", "ENGAGEMENT_RATE"]
        for metric in expected_metrics:
            assert hasattr(EngagementMetric, metric)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test model existence
        assert hasattr(module, 'TrendAnalysis')
        assert hasattr(module, 'EngagementAnalysis')
        assert hasattr(module, 'PlatformStrategy')
        assert hasattr(module, 'PlatformContent')
        assert hasattr(module, 'ContentOptimization')
        assert hasattr(module, 'ContentCalendar')
        assert hasattr(module, 'SocialMediaCampaign')

        # Test TrendAnalysis model
        TrendAnalysis = module.TrendAnalysis
        trend = TrendAnalysis(
            trending_topics=["sustainability", "eco-friendly"],
            trending_hashtags={"twitter": ["#EcoLife", "#Sustainable"]},
            viral_content_patterns=["before/after transformations"],
            audience_sentiment={"sustainability": "positive"},
            opportunity_windows=["Earth Day coming up"],
            competitor_activity=["Competitor launched green line"],
            recommended_angles=["Personal sustainability stories"],
        )
        assert len(trend.trending_topics) == 2
        assert isinstance(trend.trending_hashtags, dict)
        assert isinstance(trend.viral_content_patterns, list)

        # Test EngagementAnalysis model
        EngagementAnalysis = module.EngagementAnalysis
        EngagementMetric = module.EngagementMetric
        engagement = EngagementAnalysis(
            predicted_metrics={EngagementMetric.LIKES: 150.0, EngagementMetric.COMMENTS: 25.0},
            engagement_score=0.75,
            virality_potential=0.6,
            audience_resonance=0.8,
            optimal_timing_score=0.9,
            improvement_suggestions=["Add trending hashtags", "Include CTA"],
        )
        assert engagement.engagement_score == 0.75
        assert engagement.virality_potential == 0.6
        assert len(engagement.improvement_suggestions) == 2

        # Test PlatformStrategy model
        PlatformStrategy = module.PlatformStrategy
        SocialPlatform = module.SocialPlatform
        PostingTime = module.PostingTime
        ContentType = module.ContentType
        strategy = PlatformStrategy(
            platform=SocialPlatform.TWITTER,
            target_audience="Tech professionals",
            audience_size="50K-100K",
            content_pillars=["Tech tips", "Industry news"],
            posting_frequency="3x daily",
            optimal_times=[PostingTime.MORNING, PostingTime.LUNCH],
            content_types=[ContentType.TEXT_POST, ContentType.THREAD],
            hashtag_strategy="2-3 relevant hashtags per post",
            engagement_tactics=["Ask questions", "Create polls"],
            platform_specific_tips=["Keep under 280 chars"],
            algorithm_considerations=["Engagement in first hour crucial"],
            community_management="Respond within 2 hours",
        )
        assert strategy.platform == SocialPlatform.TWITTER
        assert len(strategy.content_pillars) == 2
        assert len(strategy.optimal_times) == 2

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        # Main functions
        assert hasattr(agent, 'multi_platform_social_media_manager')
        assert callable(agent.multi_platform_social_media_manager)
        assert hasattr(agent, 'multi_platform_social_media_manager_stream')
        assert callable(agent.multi_platform_social_media_manager_stream)

        # LLM-decorated functions
        assert hasattr(agent, 'analyze_current_trends')
        assert hasattr(agent, 'develop_platform_strategies')
        assert hasattr(agent, 'predict_content_engagement')
        assert hasattr(agent, 'optimize_content_for_platforms')
        assert hasattr(agent, 'create_content_calendar')
        assert hasattr(agent, 'synthesize_social_media_campaign')

    @pytest.mark.asyncio
    async def test_main_function_structure(self):
        """Test basic structure of main agent function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        multi_platform_social_media_manager = module.multi_platform_social_media_manager

        # Test that function is async
        import inspect

        assert inspect.iscoroutinefunction(multi_platform_social_media_manager)

        # Test function signature
        sig = inspect.signature(multi_platform_social_media_manager)
        params = list(sig.parameters.keys())
        required_params = ['campaign_goal', 'target_audience', 'brand_voice', 'platforms', 'content_themes']
        for param in required_params:
            assert param in params

        # Test optional parameters
        optional_params = [
            'campaign_duration',
            'budget',
            'timeline',
            'sample_message',
            'industry',
            'competitive_landscape',
            'performance_goals',
            'llm_provider',
            'model',
        ]
        for param in optional_params:
            assert param in params

    @pytest.mark.asyncio
    async def test_stream_function_structure(self):
        """Test structure of streaming function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stream_func = module.multi_platform_social_media_manager_stream

        # Test that function is async generator
        import inspect

        assert inspect.isasyncgenfunction(stream_func)

        # Test function signature
        sig = inspect.signature(stream_func)
        params = list(sig.parameters.keys())
        assert 'campaign_goal' in params
        assert 'target_audience' in params
        assert 'brand_voice' in params
        assert 'platforms' in params
        assert 'content_themes' in params
        assert 'kwargs' in params

    @pytest.mark.unit
    def test_llm_function_decorators(self):
        """Test that LLM functions have proper decorators."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # List of LLM functions to check
        llm_functions = [
            'analyze_current_trends',
            'develop_platform_strategies',
            'predict_content_engagement',
            'optimize_content_for_platforms',
            'create_content_calendar',
            'synthesize_social_media_campaign',
        ]

        for func_name in llm_functions:
            func = getattr(module, func_name)
            # Check that function exists and is callable
            assert callable(func)
            # Check function has __wrapped__ attribute (indicates decorators)
            assert hasattr(func, '__wrapped__') or hasattr(func, '_decorator_name')

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SocialMediaCampaign = module.SocialMediaCampaign

        # Check output is correct type
        assert isinstance(output, SocialMediaCampaign)

        # Check required fields exist
        assert hasattr(output, 'campaign_overview')
        assert hasattr(output, 'trend_analysis')
        assert hasattr(output, 'platform_strategies')
        assert hasattr(output, 'content_optimization')
        assert hasattr(output, 'content_calendar')
        assert hasattr(output, 'success_metrics')
        assert hasattr(output, 'budget_allocation')
        assert hasattr(output, 'risk_mitigation')
        assert hasattr(output, 'monitoring_plan')
        assert hasattr(output, 'crisis_management')
        assert hasattr(output, 'growth_projections')

        # Validate types
        assert isinstance(output.campaign_overview, str)
        assert isinstance(output.platform_strategies, list)
        assert isinstance(output.success_metrics, list)
        assert isinstance(output.budget_allocation, dict)
        assert isinstance(output.risk_mitigation, list)
        assert isinstance(output.monitoring_plan, str)
        assert isinstance(output.crisis_management, list)
        assert isinstance(output.growth_projections, dict)

        # Validate nested structures
        assert hasattr(output.trend_analysis, 'trending_topics')
        assert hasattr(output.trend_analysis, 'trending_hashtags')
        assert hasattr(output.trend_analysis, 'opportunity_windows')

        assert hasattr(output.content_optimization, 'original_message')
        assert hasattr(output.content_optimization, 'platform_adaptations')
        assert hasattr(output.content_optimization, 'cross_platform_strategy')

        assert hasattr(output.content_calendar, 'campaign_name')
        assert hasattr(output.content_calendar, 'duration')
        assert hasattr(output.content_calendar, 'daily_schedule')

        # Validate platform strategies match requested platforms
        requested_platforms = input_data.get('platforms', [])
        strategy_platforms = [s.platform.value for s in output.platform_strategies]
        for platform in requested_platforms:
            assert platform in strategy_platforms

    @pytest.mark.unit
    def test_platform_content_model(self):
        """Test PlatformContent model with engagement predictions."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        PlatformContent = module.PlatformContent
        SocialPlatform = module.SocialPlatform
        ContentType = module.ContentType
        PostingTime = module.PostingTime
        EngagementAnalysis = module.EngagementAnalysis
        EngagementMetric = module.EngagementMetric

        # Create engagement analysis
        engagement = EngagementAnalysis(
            predicted_metrics={EngagementMetric.LIKES: 100.0},
            engagement_score=0.8,
            virality_potential=0.7,
            audience_resonance=0.85,
            optimal_timing_score=0.9,
            improvement_suggestions=["Add video"],
        )

        # Create platform content with engagement
        content = PlatformContent(
            platform=SocialPlatform.INSTAGRAM,
            content_type=ContentType.IMAGE_POST,
            primary_text="Check out our new eco-friendly products!",
            secondary_text="Link in bio for 20% off",
            hashtags=["#EcoFriendly", "#Sustainable"],
            call_to_action="Shop now and save the planet!",
            visual_description="Product showcase with nature background",
            alt_text="Eco-friendly products displayed on wooden table",
            posting_time=PostingTime.EVENING,
            engagement_hooks=["Question in caption", "Limited time offer"],
            character_count=42,
            platform_compliance=["No banned hashtags", "Follows community guidelines"],
            engagement_prediction=engagement,
        )

        assert content.platform == SocialPlatform.INSTAGRAM
        assert content.content_type == ContentType.IMAGE_POST
        assert len(content.hashtags) == 2
        assert content.engagement_prediction.engagement_score == 0.8
        assert content.character_count == 42

    @pytest.mark.unit
    def test_content_calendar_structure(self):
        """Test ContentCalendar model structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_platform_social_media_manager",
            "packages/sygaldry_registry/components/agents/multi_platform_social_media_manager/agent.py",
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Verify the ContentCalendar model exists and has expected attributes
        assert hasattr(module, 'ContentCalendar')
        ContentCalendar = module.ContentCalendar

        # Check the model fields are defined (without instantiating due to forward refs)
        model_fields = ContentCalendar.model_fields
        expected_fields = [
            'campaign_name',
            'duration',
            'daily_schedule',
            'weekly_themes',
            'key_dates',
            'content_mix',
            'engagement_goals',
            'contingency_content',
            'real_time_slots',
        ]

        for field in expected_fields:
            assert field in model_fields, f"ContentCalendar missing field: {field}"

        # Verify field types where possible
        assert model_fields['campaign_name'].annotation == str
        assert model_fields['duration'].annotation == str
        assert 'dict' in str(model_fields['daily_schedule'].annotation)
        assert 'list' in str(model_fields['weekly_themes'].annotation)
        assert 'dict' in str(model_fields['key_dates'].annotation)
        assert 'dict' in str(model_fields['content_mix'].annotation)
        assert 'dict' in str(model_fields['engagement_goals'].annotation)
        assert 'list' in str(model_fields['contingency_content'].annotation)
        assert 'list' in str(model_fields['real_time_slots'].annotation)
