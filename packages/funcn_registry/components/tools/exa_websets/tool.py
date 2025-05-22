from __future__ import annotations

import os
from exa_py import Exa

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field
from typing import Any, Optional


# Websets models
class WebsetSearchCriteria(BaseModel):
    """Search criteria for a webset."""

    description: str
    success_rate: float | None = Field(None, alias="successRate")

    class Config:
        populate_by_name = True


class WebsetSearchProgress(BaseModel):
    """Progress information for a webset search."""

    found: int | None = None
    completion: float | None = None


class WebsetSearchConfig(BaseModel):
    """Configuration for creating a webset search."""

    query: str = Field(..., description="Search query for finding web pages")
    count: int = Field(..., description="Target number of items to find")
    entity: dict | None = Field(default=None, description="Entity to search for")
    criteria: list[dict] | None = Field(default=None, description="Search criteria")
    metadata: dict | None = Field(default=None, description="Additional metadata")


class WebsetEnrichmentConfig(BaseModel):
    """Configuration for creating a webset enrichment."""

    description: str = Field(..., description="Description of the enrichment")
    format: str = Field(..., description="Format of the enrichment result")
    options: list[dict] | None = Field(default=None, description="Enrichment options")
    instructions: str | None = Field(default=None, description="Additional instructions")
    metadata: dict | None = Field(default=None, description="Additional metadata")


class CreateWebsetArgs(BaseModel):
    """Arguments for creating a new webset."""

    search: WebsetSearchConfig
    enrichments: list[WebsetEnrichmentConfig] | None = Field(default=None)
    metadata: dict | None = Field(default=None)


class WebsetResponse(BaseModel):
    """Response containing webset information."""

    id: str
    status: str
    searches: list[dict] | None = None
    enrichments: list[dict] | None = None
    metadata: dict | None = None
    created_at: str | None = Field(None, alias="createdAt")
    items_count: int = Field(default=0, description="Number of items in the webset")

    class Config:
        populate_by_name = True


class WebsetItem(BaseModel):
    """A single item in a webset."""

    id: str
    url: str | None = None
    properties: dict | None = None
    evaluations: list[dict] | None = None
    enrichments: list[dict] | None = None
    created_at: str | None = Field(None, alias="createdAt")

    class Config:
        populate_by_name = True


class WebsetItemsResponse(BaseModel):
    """Response containing webset items."""

    items: list[WebsetItem]
    has_more: bool = Field(default=False)
    total_count: int | None = None


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def exa_create_webset(args: CreateWebsetArgs) -> WebsetResponse:
    """Create a new webset for collecting and enriching web data.

    Websets allow you to define search criteria and enrichments to build
    curated collections of web data with structured information extraction.
    """
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return WebsetResponse(
            id="error",
            status="error",
            items_count=0,
            metadata={"error": "EXA_API_KEY environment variable is required"}
        )

    try:
        exa = Exa(api_key)

        import asyncio
        def _create():
            return exa.websets.create(params=args.model_dump())

        result = await asyncio.to_thread(_create)

        # Convert to our response format
        return WebsetResponse(
            id=result.id,
            status=result.status,
            searches=result.searches,
            enrichments=result.enrichments,
            metadata=result.metadata,
            created_at=result.created_at,
            items_count=len(result.items) if hasattr(result, 'items') and result.items else 0
        )

    except Exception as e:
        return WebsetResponse(
            id="error",
            status="error",
            items_count=0,
            metadata={"error": str(e)}
        )


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def exa_get_webset(webset_id: str) -> WebsetResponse:
    """Get information about an existing webset."""
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return WebsetResponse(
            id=webset_id,
            status="error",
            items_count=0,
            metadata={"error": "EXA_API_KEY environment variable is required"}
        )

    try:
        exa = Exa(api_key)

        import asyncio
        def _get():
            return exa.websets.get(webset_id)

        result = await asyncio.to_thread(_get)

        return WebsetResponse(
            id=result.id,
            status=result.status,
            searches=result.searches,
            enrichments=result.enrichments,
            metadata=result.metadata,
            created_at=result.created_at,
            items_count=len(result.items) if hasattr(result, 'items') and result.items else 0
        )

    except Exception as e:
        return WebsetResponse(
            id=webset_id,
            status="error",
            items_count=0,
            metadata={"error": str(e)}
        )


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def exa_list_webset_items(webset_id: str, limit: int = 100) -> WebsetItemsResponse:
    """List items in a webset."""
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return WebsetItemsResponse(
            items=[],
            has_more=False,
            total_count=0
        )

    try:
        exa = Exa(api_key)

        import asyncio
        def _list_items():
            return exa.websets.items.list(webset_id)

        result = await asyncio.to_thread(_list_items)

        # Convert items to our format
        items = []
        if hasattr(result, 'data') and result.data:
            for item in result.data[:limit]:
                items.append(WebsetItem(
                    id=item.id,
                    url=item.properties.url if item.properties else None,
                    properties=item.properties.__dict__ if item.properties else None,
                    evaluations=item.evaluations,
                    enrichments=item.enrichments,
                    created_at=item.created_at
                ))

        return WebsetItemsResponse(
            items=items,
            has_more=result.has_more if hasattr(result, 'has_more') else False,
            total_count=len(items)
        )

    except Exception as e:
        return WebsetItemsResponse(
            items=[],
            has_more=False,
            total_count=0
        )


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def exa_delete_webset(webset_id: str) -> WebsetResponse:
    """Delete a webset and all its data."""
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return WebsetResponse(
            id=webset_id,
            status="error",
            items_count=0,
            metadata={"error": "EXA_API_KEY environment variable is required"}
        )

    try:
        exa = Exa(api_key)

        import asyncio
        def _delete():
            return exa.websets.delete(webset_id)

        result = await asyncio.to_thread(_delete)

        return WebsetResponse(
            id=result.id,
            status="deleted",
            metadata={"deleted_at": result.updated_at if hasattr(result, 'updated_at') else None}
        )

    except Exception as e:
        return WebsetResponse(
            id=webset_id,
            status="error",
            items_count=0,
            metadata={"error": str(e)}
        )


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def exa_wait_until_idle(webset_id: str, timeout: int = 300) -> WebsetResponse:
    """Wait for a webset to finish processing (become idle).

    This is useful when you want to ensure all searches and enrichments
    have completed before retrieving the results.
    """
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return WebsetResponse(
            id=webset_id,
            status="error",
            items_count=0,
            metadata={"error": "EXA_API_KEY environment variable is required"}
        )

    try:
        exa = Exa(api_key)

        import asyncio
        def _wait():
            return exa.websets.wait_until_idle(webset_id)

        result = await asyncio.to_thread(_wait)

        return WebsetResponse(
            id=result.id,
            status=result.status,
            searches=result.searches,
            enrichments=result.enrichments,
            metadata=result.metadata,
            created_at=result.created_at,
            items_count=len(result.items) if hasattr(result, 'items') and result.items else 0
        )

    except Exception as e:
        return WebsetResponse(
            id=webset_id,
            status="error",
            items_count=0,
            metadata={"error": str(e)}
        )
