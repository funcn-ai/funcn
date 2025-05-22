from __future__ import annotations

import asyncio
from datetime import datetime
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

# Import Exa websets tools
try:
    from exa_websets_tools import (
        WebsetCancelArgs,
        WebsetCreateArgs,
        WebsetExportArgs,
        WebsetGetArgs,
        WebsetItemsArgs,
        WebsetListArgs,
        WebsetSearchArgs,
        WebsetUpdateArgs,
        cancel_webset,
        create_webset,
        exa_wait_until_idle,
        export_webset,
        get_webset,
        list_webset_items,
        list_websets,
        update_webset,
    )
except ImportError:
    # Fallback imports
    WebsetCreateArgs = None
    create_webset = None
    get_webset = None
    list_websets = None
    list_webset_items = None
    update_webset = None
    cancel_webset = None
    export_webset = None
    exa_wait_until_idle = None


# Response models
class DatasetRequirements(BaseModel):
    """Requirements for the dataset to build."""
    topic: str = Field(..., description="Main topic or theme of the dataset")
    entity_type: str = Field(..., description="Type of entities to collect (company, person, article, etc)")
    search_queries: list[str] = Field(..., description="Search queries to use")
    criteria: list[str] = Field(..., description="Criteria for including items in the dataset")
    enrichments: list[str] = Field(..., description="Data points to extract from each item")
    target_count: int = Field(default=50, description="Target number of items to collect")


class DatasetPlan(BaseModel):
    """Plan for building the dataset."""
    name: str = Field(..., description="Name for the webset")
    description: str = Field(..., description="Description of what this dataset contains")
    search_config: dict[str, Any] = Field(..., description="Search configuration for the webset")
    entity_config: dict[str, Any] = Field(..., description="Entity type configuration")
    criteria_config: list[dict[str, Any]] = Field(..., description="Criteria for verification")
    enrichment_config: list[dict[str, Any]] = Field(..., description="Enrichments to apply")
    metadata: dict[str, Any] = Field(..., description="Metadata for tracking")


class DatasetStatus(BaseModel):
    """Current status of dataset building."""
    webset_id: str = Field(..., description="ID of the webset")
    status: str = Field(..., description="Current status: running, completed, idle")
    items_found: int = Field(..., description="Number of items found so far")
    items_enriched: int = Field(..., description="Number of items enriched")
    progress_percentage: float = Field(..., description="Overall progress percentage")
    estimated_completion: str | None = Field(default=None, description="Estimated completion time")


class DatasetAnalysis(BaseModel):
    """Analysis of the built dataset."""
    total_items: int = Field(..., description="Total number of items collected")
    data_quality_score: float = Field(..., description="Quality score 0-1")
    key_insights: list[str] = Field(..., description="Key insights from the dataset")
    data_distribution: dict[str, int] = Field(..., description="Distribution of data across categories")
    recommendations: list[str] = Field(..., description="Recommendations for using the dataset")


class DatasetBuilderResponse(BaseModel):
    """Complete response from dataset builder."""
    webset_id: str = Field(..., description="ID of the created webset")
    name: str = Field(..., description="Name of the dataset")
    status: DatasetStatus = Field(..., description="Current status")
    export_url: str | None = Field(default=None, description="URL to download the dataset when ready")
    analysis: DatasetAnalysis | None = Field(default=None, description="Analysis of the dataset")


# Step 1: Analyze requirements and create plan
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=DatasetPlan,
)
@prompt_template(
    """
    You are a data architect specializing in building curated datasets using Exa Websets.

    Requirements:
    {requirements}

    Create a comprehensive plan for building this dataset:

    1. **Name**: A descriptive name for the webset

    2. **Search Configuration**:
       - Query: Combine the search queries into an effective search
       - Count: Set based on target_count

    3. **Entity Configuration**:
       - Type: Match the entity_type requirement
       - Any additional entity-specific settings

    4. **Criteria Configuration**:
       - Convert each criterion into a structured format
       - Each should have: description, field (if applicable), operator, value

    5. **Enrichment Configuration**:
       - Convert each enrichment need into structured format
       - Each should have: key, description, prompt/field specification

    6. **Metadata**:
       - Include tracking information
       - Dataset purpose and use case
       - Creation timestamp

    Ensure the plan is optimized for the specific dataset requirements.
    """
)
async def create_dataset_plan(requirements: str):
    """Create a plan for building the dataset."""
    pass


# Step 2: Execute the plan and create webset
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    tools=[create_webset, get_webset] if create_webset else [],
)
@prompt_template(
    """
    You are executing a dataset building plan using Exa Websets.

    Plan details:
    {plan}

    Execute the following steps:

    1. Create a new webset using the create_webset tool with:
       - search configuration from the plan
       - entity type configuration
       - criteria for verification
       - enrichments to extract data
       - metadata for tracking

    2. After creation, use get_webset to verify it was created successfully

    3. Return the webset ID and initial status

    The webset will run asynchronously, collecting and enriching data based on the configuration.
    """
)
async def execute_dataset_plan(plan: str):
    """Execute the plan and create the webset."""
    pass


# Step 3: Monitor progress
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=DatasetStatus,
    tools=[get_webset, list_webset_items] if get_webset else [],
)
@prompt_template(
    """
    Monitor the progress of a dataset being built.

    Webset ID: {webset_id}

    Check the current status by:
    1. Getting the webset details using get_webset
    2. Listing items to see how many have been collected
    3. Calculate progress based on target count

    Return a comprehensive status update including:
    - Current status (running, completed, idle)
    - Number of items found
    - Number of items enriched
    - Progress percentage
    - Estimated completion time if still running
    """
)
async def monitor_dataset_progress(webset_id: str):
    """Monitor the progress of dataset building."""
    pass


# Step 4: Analyze the dataset
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=DatasetAnalysis,
    tools=[list_webset_items, export_webset] if list_webset_items else [],
)
@prompt_template(
    """
    Analyze the completed dataset.

    Webset ID: {webset_id}
    Dataset name: {name}

    Perform the following analysis:

    1. List items to understand the data collected
    2. Assess data quality based on:
       - Completeness of enrichments
       - Diversity of sources
       - Relevance to original criteria

    3. Extract key insights from the dataset

    4. Analyze data distribution across different categories

    5. Provide recommendations for using the dataset:
       - Best use cases
       - Potential limitations
       - Suggested next steps

    Return a comprehensive analysis.
    """
)
async def analyze_dataset(webset_id: str, name: str):
    """Analyze the completed dataset."""
    pass


async def build_dataset(
    topic: str,
    entity_type: Literal["company", "person", "article", "research", "product", "general"] = "general",
    search_queries: list[str] | None = None,
    criteria: list[str] | None = None,
    enrichments: list[str] | None = None,
    target_count: int = 50,
    wait_for_completion: bool = True,
    max_wait_minutes: int = 30,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini"
) -> DatasetBuilderResponse:
    """
    Build a curated dataset using Exa Websets.

    This agent automates the process of:
    1. Planning dataset requirements
    2. Creating and configuring a webset
    3. Monitoring progress
    4. Analyzing results
    5. Exporting the final dataset

    Args:
        topic: Main topic for the dataset
        entity_type: Type of entities to collect
        search_queries: Custom search queries (auto-generated if not provided)
        criteria: Criteria for including items (auto-generated if not provided)
        enrichments: Data points to extract (auto-generated if not provided)
        target_count: Number of items to collect
        wait_for_completion: Whether to wait for the dataset to complete
        max_wait_minutes: Maximum time to wait for completion
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        DatasetBuilderResponse with webset details and analysis
    """
    # Prepare requirements
    requirements = DatasetRequirements(
        topic=topic,
        entity_type=entity_type,
        search_queries=search_queries or [f"{topic} {entity_type}"],
        criteria=criteria or ["High relevance to topic", "Verified information", "Recent data"],
        enrichments=enrichments or ["summary", "key_facts", "category", "relevance_score"],
        target_count=target_count
    )

    # Step 1: Create plan
    plan = await create_dataset_plan(requirements.model_dump_json())

    # Step 2: Execute plan
    execution_result = await execute_dataset_plan(plan.model_dump_json())
    webset_id = execution_result.get("webset_id")

    if not webset_id:
        raise ValueError("Failed to create webset")

    # Step 3: Monitor progress
    if wait_for_completion:
        print(f"Dataset building started. Webset ID: {webset_id}")
        print("Waiting for completion...")

        # Wait for idle status
        start_time = datetime.now()
        max_wait_seconds = max_wait_minutes * 60

        while True:
            status = await monitor_dataset_progress(webset_id)

            if status.status in ["completed", "idle"]:
                break

            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > max_wait_seconds:
                print(f"Timeout waiting for completion after {max_wait_minutes} minutes")
                break

            # Progress update
            print(f"Progress: {status.progress_percentage:.1f}% - {status.items_found} items found")
            await asyncio.sleep(30)  # Check every 30 seconds
    else:
        status = await monitor_dataset_progress(webset_id)

    # Step 4: Analyze if completed
    analysis = None
    export_url = None

    if status.status in ["completed", "idle"]:
        analysis = await analyze_dataset(webset_id, plan.name)

        # Export dataset
        export_args = WebsetExportArgs(webset_id=webset_id)
        export_result = await export_webset(export_args)
        export_url = export_result.get("download_url")

    return DatasetBuilderResponse(
        webset_id=webset_id,
        name=plan.name,
        status=status,
        export_url=export_url,
        analysis=analysis
    )


# Convenience functions for specific dataset types
async def build_company_dataset(
    industry: str,
    criteria: list[str] | None = None,
    **kwargs
) -> DatasetBuilderResponse:
    """
    Build a dataset of companies in a specific industry.

    Optimized for company data with enrichments like:
    - Company description
    - Industry classification
    - Size and location
    - Recent news
    - Key products/services
    """
    default_criteria = [
        f"Company operates in {industry}",
        "Active business operations",
        "Publicly available information"
    ]

    default_enrichments = [
        "company_description",
        "industry_classification",
        "headquarters_location",
        "employee_count",
        "recent_news",
        "key_products"
    ]

    return await build_dataset(
        topic=f"{industry} companies",
        entity_type="company",
        criteria=criteria or default_criteria,
        enrichments=default_enrichments,
        **kwargs
    )


async def build_research_dataset(
    research_topic: str,
    time_range: str = "last 2 years",
    **kwargs
) -> DatasetBuilderResponse:
    """
    Build a dataset of research papers and articles.

    Optimized for academic content with enrichments like:
    - Abstract/summary
    - Key findings
    - Methodology
    - Authors and affiliations
    - Citations
    """
    search_queries = [
        f"{research_topic} research papers",
        f"{research_topic} academic studies",
        f"{research_topic} peer reviewed"
    ]

    criteria = [
        f"Published within {time_range}",
        "Academic or research source",
        "Peer-reviewed or credible publication"
    ]

    enrichments = [
        "abstract",
        "key_findings",
        "methodology",
        "authors",
        "publication_date",
        "journal_name"
    ]

    return await build_dataset(
        topic=research_topic,
        entity_type="research",
        search_queries=search_queries,
        criteria=criteria,
        enrichments=enrichments,
        **kwargs
    )


async def build_market_dataset(
    market_segment: str,
    data_types: list[str] | None = None,
    **kwargs
) -> DatasetBuilderResponse:
    """
    Build a market analysis dataset.

    Collects diverse market data including:
    - Market trends
    - Competitor information
    - Customer insights
    - Industry reports
    """
    data_types = data_types or ["trends", "competitors", "reports", "analysis"]

    search_queries = [f"{market_segment} market {dt}" for dt in data_types]

    enrichments = [
        "market_size",
        "growth_rate",
        "key_players",
        "trends",
        "opportunities",
        "challenges"
    ]

    return await build_dataset(
        topic=f"{market_segment} market analysis",
        entity_type="article",
        search_queries=search_queries,
        enrichments=enrichments,
        **kwargs
    )
