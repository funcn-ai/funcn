"""Integration tests for dataset builder agent with Exa Websets.

Tests the complete pipeline of building custom datasets using
Exa Websets, including search criteria, data enrichment, and
export functionality for various use cases.
"""

import asyncio
import json
import pytest
from datetime import datetime

# Import the real dataset builder agent
from packages.funcn_registry.components.agents.dataset_builder.agent import (
    DatasetAnalysis,
    DatasetBuilderResponse,
    DatasetPlan,
    DatasetRequirements,
    DatasetStatus,
    build_company_dataset,
    build_competitor_dataset,
    build_dataset,
    build_influencer_dataset,
    build_investment_dataset,
    build_location_dataset,
    build_market_dataset,
    build_news_trends_dataset,
    build_product_launch_dataset,
    build_research_dataset,
    build_talent_dataset,
)
from typing import Any, Dict, List, Literal, Optional
from unittest.mock import AsyncMock, Mock, patch


class TestDatasetBuilderPipeline:
    """Test complete dataset building pipelines for various use cases."""
    
    @pytest.fixture
    def mock_exa_tools(self):
        """Mock Exa websets tools for testing."""
        with patch('packages.funcn_registry.components.agents.dataset_builder.agent.create_webset') as mock_create, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.get_webset') as mock_get, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.list_webset_items') as mock_list, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.export_webset') as mock_export:
            
            # Mock successful webset creation
            mock_create.return_value = {"webset_id": "test-webset-123"}
            
            # Mock webset status
            mock_get.return_value = {
                "id": "test-webset-123",
                "status": "completed",
                "items_count": 50
            }
            
            # Mock webset items
            mock_list.return_value = {
                "items": [
                    {"title": "Item 1", "url": "https://example.com/1"},
                    {"title": "Item 2", "url": "https://example.com/2"}
                ]
            }
            
            # Mock export
            mock_export.return_value = {"download_url": "https://example.com/export.csv"}
            
            yield {
                "create": mock_create,
                "get": mock_get,
                "list": mock_list,
                "export": mock_export
            }
    
    @pytest.mark.asyncio
    async def test_ai_research_dataset_building(self, mock_exa_tools):
        """Test building a dataset of AI research papers and findings."""
        # Mock the LLM calls for planning and analysis
        with patch('packages.funcn_registry.components.agents.dataset_builder.agent.create_dataset_plan') as mock_plan, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.execute_dataset_plan') as mock_execute, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.monitor_dataset_progress') as mock_monitor, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.analyze_dataset') as mock_analyze:
            
            # Mock planning response
            mock_plan.return_value = DatasetPlan(
                name="AI Research 2024",
                description="Collection of AI research papers from 2024",
                search_config={"query": "AI research 2024", "count": 100},
                entity_config={"type": "research"},
                criteria_config=[{"field": "year", "value": "2024"}],
                enrichment_config=[{"key": "abstract"}, {"key": "authors"}],
                metadata={"created_at": "2024-01-01"}
            )
            
            # Mock execution response
            mock_execute.return_value = {"webset_id": "test-webset-123"}
            
            # Mock monitoring response
            mock_monitor.return_value = DatasetStatus(
                webset_id="test-webset-123",
                status="completed",
                items_found=98,
                items_enriched=98,
                progress_percentage=100.0,
                estimated_completion=None
            )
            
            # Mock analysis response
            mock_analyze.return_value = DatasetAnalysis(
                total_items=98,
                data_quality_score=0.92,
                key_insights=[
                    "Transformers dominate the research landscape",
                    "Multimodal approaches are trending",
                    "12 breakthrough papers identified"
                ],
                data_distribution={"NeurIPS": 25, "ICML": 20, "ICLR": 18, "Other": 35},
                recommendations=["Focus on transformer variants", "Include workshop papers"]
            )
            
            # Build the research dataset using the convenience function
            result = await build_research_dataset(
                research_topic="artificial intelligence breakthroughs",
                time_range="2024",
                target_count=100,
                wait_for_completion=False  # Don't wait in tests
            )
            
            # Verify the dataset was built successfully
            assert isinstance(result, DatasetBuilderResponse)
            assert result.webset_id == "test-webset-123"
            assert result.status.items_found == 98
            assert result.status.status == "completed"
            
            # Verify analysis was performed
            assert result.analysis is not None
            assert result.analysis.total_items == 98
            assert result.analysis.data_quality_score == 0.92
            assert len(result.analysis.key_insights) == 3
            assert "Transformers" in result.analysis.key_insights[0]
            
            # Verify export URL
            assert result.export_url == "https://example.com/export.csv"
    
    @pytest.mark.asyncio
    async def test_competitor_intelligence_dataset(self, mock_exa_tools):
        """Test building a competitor intelligence dataset for market analysis."""
        # Mock the LLM calls
        with patch('packages.funcn_registry.components.agents.dataset_builder.agent.create_dataset_plan') as mock_plan, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.execute_dataset_plan') as mock_execute, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.monitor_dataset_progress') as mock_monitor, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.analyze_dataset') as mock_analyze:
            
            # Setup mocks
            mock_plan.return_value = DatasetPlan(
                name="Cloud Computing Competitors",
                description="Analysis of cloud service providers",
                search_config={"query": "cloud computing competitors", "count": 50},
                entity_config={"type": "company"},
                criteria_config=[],
                enrichment_config=[],
                metadata={}
            )
            
            mock_execute.return_value = {"webset_id": "cloud-dataset-456"}
            
            mock_monitor.return_value = DatasetStatus(
                webset_id="cloud-dataset-456",
                status="completed",
                items_found=48,
                items_enriched=48,
                progress_percentage=100.0,
                estimated_completion=None
            )
            
            mock_analyze.return_value = DatasetAnalysis(
                total_items=48,
                data_quality_score=0.88,
                key_insights=[
                    "AWS maintains market leadership",
                    "Azure growing in enterprise segment",
                    "Emerging players focus on developer experience"
                ],
                data_distribution={
                    "Major Players": 10,
                    "Regional Providers": 15,
                    "Specialized Services": 23
                },
                recommendations=["Monitor pricing changes", "Track new service launches"]
            )
            
            # Use the competitor dataset builder
            result = await build_competitor_dataset(
                company_name="AWS",
                industry="cloud computing",
                aspects=["pricing", "services", "market share"],
                target_count=50,
                wait_for_completion=False
            )
            
            # Verify results
            assert isinstance(result, DatasetBuilderResponse)
            assert result.webset_id == "cloud-dataset-456"
            assert result.status.items_found == 48
            assert result.analysis.key_insights[0] == "AWS maintains market leadership"
    
    @pytest.mark.asyncio
    async def test_investment_opportunities_dataset(self, mock_exa_tools):
        """Test building dataset of investment opportunities in specific sectors."""
        with patch('packages.funcn_registry.components.agents.dataset_builder.agent.create_dataset_plan') as mock_plan, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.execute_dataset_plan') as mock_execute, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.monitor_dataset_progress') as mock_monitor, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.analyze_dataset') as mock_analyze:
            
            # Setup mocks
            mock_plan.return_value = DatasetPlan(
                name="Renewable Energy Investments",
                description="Investment opportunities in renewable sector",
                search_config={"query": "renewable energy investments", "count": 75},
                entity_config={"type": "company"},
                criteria_config=[
                    {"field": "funding_stage", "value": "series_a"},
                    {"field": "sector", "value": "renewable_energy"}
                ],
                enrichment_config=[
                    {"key": "valuation"},
                    {"key": "funding_stage"},
                    {"key": "investors"}
                ],
                metadata={"focus": "early_stage"}
            )
            
            mock_execute.return_value = {"webset_id": "renewable-inv-789"}
            
            mock_monitor.return_value = DatasetStatus(
                webset_id="renewable-inv-789",
                status="completed",
                items_found=72,
                items_enriched=70,
                progress_percentage=100.0,
                estimated_completion=None
            )
            
            mock_analyze.return_value = DatasetAnalysis(
                total_items=72,
                data_quality_score=0.91,
                key_insights=[
                    "Battery storage dominates funding",
                    "Average valuation: $45M",
                    "Green hydrogen emerging as hot sector",
                    "Total funding available: $2.3B"
                ],
                data_distribution={
                    "Battery Storage": 25,
                    "Solar": 20,
                    "Wind": 15,
                    "Green Hydrogen": 12
                },
                recommendations=[
                    "Focus on Series A companies",
                    "Monitor battery technology innovations"
                ]
            )
            
            # Build investment dataset
            result = await build_investment_dataset(
                sector="renewable energy",
                investment_stage="series_a",
                geography="US",
                target_count=75,
                wait_for_completion=False
            )
            
            # Verify results
            assert isinstance(result, DatasetBuilderResponse)
            assert result.webset_id == "renewable-inv-789"
            assert result.status.items_found == 72
            assert result.status.items_enriched == 70
            
            # Check insights
            assert result.analysis is not None
            assert "Battery storage" in result.analysis.key_insights[0]
            assert "$45M" in result.analysis.key_insights[1]
    
    @pytest.mark.asyncio
    async def test_social_media_influencer_dataset(self, mock_exa_tools):
        """Test building dataset of social media influencers for marketing."""
        with patch('packages.funcn_registry.components.agents.dataset_builder.agent.create_dataset_plan') as mock_plan, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.execute_dataset_plan') as mock_execute, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.monitor_dataset_progress') as mock_monitor, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.analyze_dataset') as mock_analyze:
            
            # Setup mocks
            mock_plan.return_value = DatasetPlan(
                name="Sustainable Fashion Influencers",
                description="Social media influencers in sustainable fashion",
                search_config={"query": "sustainable fashion influencers", "count": 100},
                entity_config={"type": "person"},
                criteria_config=[
                    {"field": "followers", "operator": ">", "value": 10000}
                ],
                enrichment_config=[
                    {"key": "follower_count"},
                    {"key": "engagement_rate"},
                    {"key": "platform_handles"}
                ],
                metadata={"niche": "sustainable_fashion"}
            )
            
            mock_execute.return_value = {"webset_id": "influencer-set-999"}
            
            mock_monitor.return_value = DatasetStatus(
                webset_id="influencer-set-999",
                status="completed",
                items_found=95,
                items_enriched=95,
                progress_percentage=100.0,
                estimated_completion=None
            )
            
            mock_analyze.return_value = DatasetAnalysis(
                total_items=95,
                data_quality_score=0.94,
                key_insights=[
                    "Average follower count: 125,000",
                    "Average engagement rate: 5.2%",
                    "Instagram dominates with 45% of influencers",
                    "67% have brand partnerships"
                ],
                data_distribution={
                    "Instagram": 45,
                    "TikTok": 30,
                    "YouTube": 20,
                    "Multi-platform": 5
                },
                recommendations=[
                    "Focus on micro-influencers for better engagement",
                    "Consider TikTok creators for younger demographics"
                ]
            )
            
            # Build influencer dataset
            result = await build_influencer_dataset(
                niche="sustainable fashion",
                platforms=["instagram", "tiktok", "youtube"],
                min_followers=10000,
                target_count=100,
                wait_for_completion=False
            )
            
            # Verify results
            assert isinstance(result, DatasetBuilderResponse)
            assert result.webset_id == "influencer-set-999"
            assert result.status.items_found == 95
            
            # Check insights
            assert "125,000" in result.analysis.key_insights[0]
            assert "5.2%" in result.analysis.key_insights[1]
            assert result.analysis.data_distribution["Instagram"] == 45
    
    @pytest.mark.asyncio
    async def test_market_intelligence_dataset_with_monitoring(self, mock_exa_tools):
        """Test building market intelligence dataset with progress monitoring."""
        with patch('packages.funcn_registry.components.agents.dataset_builder.agent.create_dataset_plan') as mock_plan, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.execute_dataset_plan') as mock_execute, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.monitor_dataset_progress') as mock_monitor, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.analyze_dataset') as mock_analyze:
            
            # Setup mocks
            mock_plan.return_value = DatasetPlan(
                name="EV Market Trends 2024",
                description="Electric vehicle market analysis",
                search_config={"query": "electric vehicle market 2024", "count": 60},
                entity_config={"type": "article"},
                criteria_config=[],
                enrichment_config=[],
                metadata={}
            )
            
            mock_execute.return_value = {"webset_id": "ev-market-888"}
            
            # Mock progressive status updates
            mock_monitor.side_effect = [
                DatasetStatus(
                    webset_id="ev-market-888",
                    status="running",
                    items_found=20,
                    items_enriched=0,
                    progress_percentage=30.0,
                    estimated_completion="5 minutes"
                ),
                DatasetStatus(
                    webset_id="ev-market-888",
                    status="running",
                    items_found=55,
                    items_enriched=25,
                    progress_percentage=60.0,
                    estimated_completion="3 minutes"
                ),
                DatasetStatus(
                    webset_id="ev-market-888",
                    status="completed",
                    items_found=58,
                    items_enriched=56,
                    progress_percentage=100.0,
                    estimated_completion=None
                )
            ]
            
            mock_analyze.return_value = DatasetAnalysis(
                total_items=58,
                data_quality_score=0.89,
                key_insights=[
                    "Market size 2024: $1.2T",
                    "YoY growth: 23%",
                    "China leads with 45% market share",
                    "Solid-state batteries emerging as key trend"
                ],
                data_distribution={
                    "Market Reports": 20,
                    "Technology Analysis": 18,
                    "Policy Updates": 10,
                    "Consumer Studies": 10
                },
                recommendations=[
                    "Monitor battery technology advances",
                    "Track infrastructure investments"
                ]
            )
            
            # Build market dataset with custom monitoring
            result = await build_market_dataset(
                market_segment="electric vehicles",
                data_types=["trends", "technology", "policy", "consumer"],
                target_count=60,
                wait_for_completion=False
            )
            
            # Verify results
            assert isinstance(result, DatasetBuilderResponse)
            assert result.webset_id == "ev-market-888"
            
            # Check final status
            assert result.status.items_found == 58
            assert result.status.items_enriched == 56
            
            # Verify market insights
            assert "$1.2T" in result.analysis.key_insights[0]
            assert "23%" in result.analysis.key_insights[1]
            assert "Solid-state batteries" in result.analysis.key_insights[3]
    
    @pytest.mark.asyncio
    async def test_news_monitoring_dataset_realtime(self, mock_exa_tools):
        """Test building real-time news monitoring dataset."""
        with patch('packages.funcn_registry.components.agents.dataset_builder.agent.create_dataset_plan') as mock_plan, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.execute_dataset_plan') as mock_execute, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.monitor_dataset_progress') as mock_monitor, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.analyze_dataset') as mock_analyze:
            
            # Setup mocks
            mock_plan.return_value = DatasetPlan(
                name="Crypto Regulation News",
                description="Real-time cryptocurrency regulation news",
                search_config={"query": "cryptocurrency regulation news", "count": 30},
                entity_config={"type": "article"},
                criteria_config=[
                    {"field": "published_date", "operator": "within", "value": "24h"}
                ],
                enrichment_config=[
                    {"key": "headline"},
                    {"key": "sentiment"},
                    {"key": "regulatory_body"}
                ],
                metadata={"real_time": True}
            )
            
            mock_execute.return_value = {"webset_id": "crypto-news-live"}
            
            mock_monitor.return_value = DatasetStatus(
                webset_id="crypto-news-live",
                status="completed",
                items_found=28,
                items_enriched=28,
                progress_percentage=100.0,
                estimated_completion=None
            )
            
            mock_analyze.return_value = DatasetAnalysis(
                total_items=28,
                data_quality_score=0.95,
                key_insights=[
                    "3 breaking stories in last hour",
                    "SEC most mentioned regulatory body",
                    "Neutral sentiment dominates (64%)",
                    "US leads geographic coverage"
                ],
                data_distribution={
                    "US": 12,
                    "EU": 8,
                    "UK": 5,
                    "Asia": 3
                },
                recommendations=[
                    "Set up alerts for SEC announcements",
                    "Monitor EU regulatory changes"
                ]
            )
            
            # Build news trends dataset
            result = await build_news_trends_dataset(
                topic="cryptocurrency regulation",
                time_period="last 24 hours",
                sources=["Reuters", "Bloomberg", "CoinDesk"],
                target_count=30,
                wait_for_completion=False
            )
            
            # Verify results
            assert isinstance(result, DatasetBuilderResponse)
            assert result.webset_id == "crypto-news-live"
            assert result.status.items_found == 28
            
            # Check news insights
            assert "3 breaking stories" in result.analysis.key_insights[0]
            assert "SEC" in result.analysis.key_insights[1]
            assert "64%" in result.analysis.key_insights[2]
    
    @pytest.mark.asyncio
    async def test_location_based_business_dataset(self, mock_exa_tools):
        """Test building location-based dataset for business opportunities."""
        with patch('packages.funcn_registry.components.agents.dataset_builder.agent.create_dataset_plan') as mock_plan, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.execute_dataset_plan') as mock_execute, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.monitor_dataset_progress') as mock_monitor, \
             patch('packages.funcn_registry.components.agents.dataset_builder.agent.analyze_dataset') as mock_analyze:
            
            # Setup mocks
            mock_plan.return_value = DatasetPlan(
                name="LA Coffee Shop Locations",
                description="Location analysis for coffee shops in Los Angeles",
                search_config={"query": "coffee shop locations Los Angeles", "count": 40},
                entity_config={"type": "general"},
                criteria_config=[
                    {"field": "commercial_zoning", "value": "available"},
                    {"field": "foot_traffic", "operator": ">", "value": 1000}
                ],
                enrichment_config=[
                    {"key": "demographics"},
                    {"key": "rent_prices"},
                    {"key": "competitor_density"}
                ],
                metadata={"city": "Los Angeles", "business_type": "coffee_shop"}
            )
            
            mock_execute.return_value = {"webset_id": "location-set-333"}
            
            mock_monitor.return_value = DatasetStatus(
                webset_id="location-set-333",
                status="completed",
                items_found=38,
                items_enriched=38,
                progress_percentage=100.0,
                estimated_completion=None
            )
            
            mock_analyze.return_value = DatasetAnalysis(
                total_items=38,
                data_quality_score=0.93,
                key_insights=[
                    "Top opportunity: Arts District",
                    "Average rent: $42.50 per sq ft",
                    "Average competitor density: 2.3 shops per sq mile",
                    "8 demographic sweet spots identified"
                ],
                data_distribution={
                    "High Opportunity": 8,
                    "Medium Opportunity": 15,
                    "Saturated": 10,
                    "Emerging": 5
                },
                recommendations=[
                    "Focus on Arts District and Highland Park",
                    "Consider emerging areas like West Adams"
                ]
            )
            
            # Build location dataset
            result = await build_location_dataset(
                business_type="coffee shop",
                geography="Los Angeles",
                criteria_list=[
                    "Commercial zoning available",
                    "Foot traffic > 1000 daily",
                    "Rent < $50 per sq ft"
                ],
                target_count=40,
                wait_for_completion=False
            )
            
            # Verify results
            assert isinstance(result, DatasetBuilderResponse)
            assert result.webset_id == "location-set-333"
            assert result.status.items_found == 38
            
            # Check location insights
            assert "Arts District" in result.analysis.key_insights[0]
            assert "$42.50" in result.analysis.key_insights[1]
            assert result.analysis.data_distribution["High Opportunity"] == 8