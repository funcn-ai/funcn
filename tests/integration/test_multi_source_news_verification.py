"""Integration tests for multi-source news verification agent.

Tests complex news verification scenarios using academic sources,
government data, social media verification, and expert validation
to identify misinformation and coordinated disinformation campaigns.
"""

import asyncio
import pytest
from datetime import datetime

# Import the actual news verification agent
from packages.funcn_registry.components.agents.multi_source_news_verification.agent import (
    CredibilityLevel,
    MisinformationType,
    VerificationResult,
    VerificationStatus,
    analyze_news_content,
    assess_source_credibility,
    fact_check_claims,
    multi_source_news_verification,
)
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch


class TestMultiSourceNewsVerification:
    """Test multi-source news verification with comprehensive fact-checking pipelines."""
    
    @pytest.mark.asyncio
    async def test_pandemic_misinformation_verification(self):
        """Test verification of pandemic-related misinformation using WHO/CDC sources.
        
        Simulates checking health claims against official medical sources,
        academic papers, and fact-checking databases.
        """
        test_article = """
        Breaking: New study shows that vitamin D alone can prevent COVID-19 infection 
        with 95% effectiveness. Researchers claim that daily supplementation eliminates 
        the need for vaccines. The study, conducted by independent researchers, analyzed 
        data from 50,000 participants across 10 countries.
        
        Dr. John Smith, lead researcher, stated: "Our findings clearly demonstrate that 
        vitamin D is more effective than any vaccine currently available."
        """
        
        # Mock the verification tools
        with patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.DUCKDUCKGO_AVAILABLE", True), \
             patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.EXA_AVAILABLE", True):
            
            # Run verification
            result = await multi_source_news_verification(
                article_content=test_article,
                headline="Vitamin D Prevents COVID-19 with 95% Effectiveness, Study Shows",
                sources=["WHO", "CDC", "Mayo Clinic", "Johns Hopkins"],
                topic_area="health",
                check_fact_checkers=True,
                educational_mode=True,
                use_realtime_search=False  # Disable real search for testing
            )
            
            # Verify detection of misinformation
            assert isinstance(result, VerificationResult)
            assert result.overall_verification_status in [
                VerificationStatus.CONTRADICTED,
                VerificationStatus.MISLEADING_CONTEXT,
                VerificationStatus.UNVERIFIED
            ]
            assert result.confidence_score < 0.5  # Low confidence in the claims
            
            # Check that misinformation indicators were found
            assert any(
                indicator in str(result.warning_signs).lower() 
                for indicator in ["vaccine", "95%", "prevents"]
            )
            
            # Educational content should be included
            if result.media_literacy_insights:
                assert len(result.media_literacy_insights) > 0
    
    @pytest.mark.asyncio
    async def test_election_misinformation_with_official_sources(self):
        """Test verification of election-related claims using official government sources."""
        test_content = """
        URGENT: Electronic voting machines in Michigan were found to be switching votes 
        from one candidate to another. A software "glitch" affected 6,000 votes in one 
        county alone. Election officials are refusing to investigate, raising concerns 
        about widespread fraud. Anonymous whistleblowers claim this is happening in 
        multiple states.
        """
        
        with patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.assess_source_credibility") as mock_assess, \
             patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.analyze_news_content") as mock_analyze, \
             patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.fact_check_claims") as mock_fact_check, \
             patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.synthesize_news_verification") as mock_synthesize:
            
            # Mock source credibility assessment
            mock_assess.return_value = [
                {"source": "Anonymous whistleblowers", "credibility_level": CredibilityLevel.VERY_LOW}
            ]
            
            # Mock content analysis
            mock_analyze.return_value = Mock(
                main_claims=[
                    "Voting machines switching votes",
                    "6,000 votes affected by glitch",
                    "Officials refusing to investigate"
                ],
                misinformation_indicators=["anonymous sources", "unverified claims", "conspiracy language"],
                bias_assessment={"direction": "partisan", "severity": "high"}
            )
            
            # Mock fact checking
            mock_fact_check.return_value = [
                Mock(
                    claim="Voting machines switching votes",
                    verification_status=VerificationStatus.CONTRADICTED,
                    sources_checked=["Michigan Secretary of State", "Reuters Fact Check"],
                    evidence_summary="No evidence of vote switching found"
                )
            ]
            
            # Mock final synthesis
            mock_synthesize.return_value = VerificationResult(
                overall_verification_status=VerificationStatus.CONTRADICTED,
                confidence_score=0.15,
                verified_facts=[],
                disputed_claims=["All major claims disputed by official sources"],
                missing_context=["Software updates are routine", "All votes were properly counted"],
                warning_signs=["Anonymous sources", "Conspiracy narrative", "No official confirmation"],
                media_literacy_insights=["Check official election sources", "Be wary of anonymous claims"]
            )
            
            # Run verification
            result = await multi_source_news_verification(
                article_content=test_content,
                headline="BREAKING: Voting Machines Caught Switching Votes",
                sources=["State Election Officials", "Associated Press", "Reuters"],
                topic_area="politics",
                check_fact_checkers=True
            )
            
            # Verify proper handling of election misinformation
            assert result.overall_verification_status == VerificationStatus.CONTRADICTED
            assert result.confidence_score < 0.3
            assert len(result.disputed_claims) > 0
            assert "anonymous" in str(result.warning_signs).lower()
    
    @pytest.mark.asyncio
    async def test_expert_source_verification_pipeline(self):
        """Test verification of claims requiring expert validation."""
        test_article = """
        Climate scientists at Oxford University announce breakthrough: New data shows 
        global warming stopped in 2016. Professor Jane Doe, lead climatologist, presents 
        findings showing temperature plateau despite rising CO2 levels. The research 
        challenges IPCC reports and suggests natural cooling cycles are offsetting 
        human impacts.
        """
        
        with patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.analyze_news_content") as mock_analyze, \
             patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.fact_check_claims") as mock_fact_check:
            
            # Mock finding expert claims that need verification
            mock_analyze.return_value = Mock(
                main_claims=[
                    "Global warming stopped in 2016",
                    "Temperature plateau despite rising CO2",
                    "Natural cycles offsetting human impacts"
                ],
                expert_claims=[
                    {"expert": "Professor Jane Doe", "institution": "Oxford", "claim": "warming stopped"}
                ],
                misinformation_indicators=[]
            )
            
            # Mock expert verification showing contradiction
            mock_fact_check.return_value = [
                Mock(
                    claim="Global warming stopped in 2016",
                    verification_status=VerificationStatus.CONTRADICTED,
                    expert_consensus="97% of climate scientists disagree",
                    primary_sources=["NASA", "NOAA", "Met Office"],
                    evidence_summary="Temperature data shows continued warming trend"
                )
            ]
            
            # Run verification focusing on expert claims
            result = await multi_source_news_verification(
                article_content=test_article,
                sources=["NASA", "NOAA", "IPCC", "Oxford University"],
                topic_area="science",
                author_info="Science correspondent with 10 years experience"
            )
            
            # Should identify as contradicted by expert consensus
            assert result.overall_verification_status in [
                VerificationStatus.CONTRADICTED,
                VerificationStatus.MISLEADING_CONTEXT
            ]
            assert result.confidence_score < 0.5
    
    @pytest.mark.asyncio
    async def test_coordinated_disinformation_detection(self):
        """Test detection of coordinated disinformation campaigns."""
        test_content = """
        Multiple independent citizen journalists report seeing unusual military movements 
        near major cities. Videos shared on social media show convoys of unmarked vehicles. 
        #MilitaryTakeover is trending with over 100,000 posts. Government officials have 
        not responded to requests for comment. Similar reports are emerging from 
        Australia, Canada, and the UK simultaneously.
        """
        
        # Test the agent's ability to detect coordinated campaigns
        result = await multi_source_news_verification(
            article_content=test_content,
            headline="Citizens Report Mysterious Military Movements Worldwide",
            sources=["Reuters", "AP", "BBC", "Military Times", "Defense Department"],
            context="Social media campaign analysis",
            topic_area="security",
            check_fact_checkers=True,
            educational_mode=True
        )
        
        # Should identify coordination patterns
        assert isinstance(result, VerificationResult)
        assert result.overall_verification_status in [
            VerificationStatus.UNVERIFIED,
            VerificationStatus.INSUFFICIENT_EVIDENCE,
            VerificationStatus.MISLEADING_CONTEXT
        ]
        
        # Should note social media patterns in warnings
        if result.warning_signs:
            warning_text = " ".join(result.warning_signs).lower()
            assert any(
                pattern in warning_text 
                for pattern in ["social media", "coordinated", "trending", "simultaneous"]
            )
    
    @pytest.mark.asyncio
    async def test_deepfake_and_manipulated_media_verification(self):
        """Test verification of claims about manipulated media and deepfakes."""
        test_article = """
        Shocking video emerges showing CEO of major tech company making controversial 
        statements about user privacy. In the leaked footage, the executive appears to 
        say "We sell all user data to the highest bidder" during what seems to be an 
        internal meeting. The video, first posted on an anonymous forum, has been 
        viewed over 5 million times. The company has not yet commented.
        """
        
        with patch("packages.funcn_registry.components.agents.multi_source_news_verification.agent.analyze_news_content") as mock_analyze:
            # Mock detection of potential deepfake indicators
            mock_analyze.return_value = Mock(
                main_claims=["CEO admits to selling user data"],
                misinformation_indicators=[
                    "anonymous source",
                    "unverified video",
                    "no official response yet",
                    "potential deepfake"
                ],
                media_verification_needed=True,
                claim_types=["image_video"]
            )
            
            result = await multi_source_news_verification(
                article_content=test_article,
                headline="LEAKED: Tech CEO Admits to Selling User Data",
                sources=["TechCrunch", "The Verge", "Company PR", "Video forensics experts"],
                topic_area="technology",
                author_info="Anonymous submission"
            )
            
            # Should flag for video verification
            assert result.overall_verification_status in [
                VerificationStatus.UNVERIFIED,
                VerificationStatus.INSUFFICIENT_EVIDENCE
            ]
            assert result.confidence_score < 0.5
            
            # Should identify need for media verification
            assert any(
                "video" in warning.lower() or "deepfake" in warning.lower() 
                for warning in (result.warning_signs or [])
            )
    
    @pytest.mark.asyncio
    async def test_real_time_breaking_news_verification(self):
        """Test verification of breaking news with limited initial sources."""
        breaking_news = """
        JUST IN: Major earthquake strikes Tokyo, Japan. Initial reports suggest 
        magnitude 7.5. Buildings swaying, people evacuating to streets. Power outages 
        reported in several districts. Tsunami warning issued for coastal areas. 
        Death toll unknown at this time. More updates to follow.
        """
        
        # For breaking news, verification should acknowledge limitations
        result = await multi_source_news_verification(
            article_content=breaking_news,
            headline="BREAKING: Major 7.5 Earthquake Strikes Tokyo",
            sources=["Japan Meteorological Agency", "NHK", "Reuters", "USGS"],
            context="Breaking news - 10 minutes old",
            topic_area="disaster",
            use_realtime_search=False  # Can't use real search in tests
        )
        
        # Should handle breaking news appropriately
        assert isinstance(result, VerificationResult)
        # Breaking news often has insufficient evidence initially
        assert result.overall_verification_status in [
            VerificationStatus.PARTIALLY_VERIFIED,
            VerificationStatus.INSUFFICIENT_EVIDENCE,
            VerificationStatus.UNVERIFIED
        ]
        
        # Should note the breaking nature in context
        if result.missing_context:
            assert any(
                "breaking" in ctx.lower() or "developing" in ctx.lower() 
                for ctx in result.missing_context
            )