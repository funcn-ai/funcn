"""
Dataset Builder Agent

An AI-powered agent that builds curated datasets using Exa Websets.
Automates the process of creating, monitoring, and analyzing data collections
with custom search criteria, verification rules, and enrichments.

Key capabilities:
- Asynchronous dataset creation with real-time monitoring
- Custom criteria for data verification
- AI-powered enrichments to extract structured data
- Analysis and export of completed datasets
"""

from .agent import (
    DatasetAnalysis,
    DatasetBuilderResponse,
    DatasetPlan,
    DatasetRequirements,
    DatasetStatus,
    analyze_dataset,
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
    create_dataset_plan,
    execute_dataset_plan,
    monitor_dataset_progress,
)

__all__ = [
    "build_dataset",
    "build_company_dataset",
    "build_research_dataset",
    "build_market_dataset",
    "build_competitor_dataset",
    "build_influencer_dataset",
    "build_news_trends_dataset",
    "build_investment_dataset",
    "build_talent_dataset",
    "build_product_launch_dataset",
    "build_location_dataset",
    "create_dataset_plan",
    "execute_dataset_plan",
    "monitor_dataset_progress",
    "analyze_dataset",
    "DatasetRequirements",
    "DatasetPlan",
    "DatasetStatus",
    "DatasetAnalysis",
    "DatasetBuilderResponse",
]
