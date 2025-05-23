from __future__ import annotations

import os
from firecrawl import FirecrawlApp

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field, validator
from typing import Any, Optional
from urllib.parse import urlparse


class FirecrawlScrapeArgs(BaseModel):
    """Arguments for Firecrawl scraping operations."""

    url: str = Field(..., description="URL of the webpage to scrape")
    formats: list[str] = Field(
        default=["markdown", "html"],
        description="Formats to return. Options: 'markdown', 'html', 'rawHtml', 'content', 'links', 'screenshot'"
    )
    only_main_content: bool = Field(
        default=True,
        description="Only return the main content of the page, excluding headers, navs, footers, etc."
    )
    include_tags: list[str] | None = Field(
        None,
        description="CSS selectors to include in the scrape (e.g., ['article', '.content', '#main'])"
    )
    exclude_tags: list[str] | None = Field(
        None,
        description="CSS selectors to exclude from the scrape (e.g., ['.ads', '#sidebar', 'nav'])"
    )
    wait_for: int | None = Field(
        None,
        description="Time to wait in milliseconds for the page to load before scraping"
    )
    screenshot: bool = Field(
        default=False,
        description="Whether to take a screenshot of the page"
    )
    remove_scripts: bool = Field(
        default=True,
        description="Remove script tags from the HTML"
    )

    @validator('formats')
    def validate_formats(cls, v):
        valid_formats = {'markdown', 'html', 'rawHtml', 'content', 'links', 'screenshot'}
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid format: {fmt}. Must be one of {valid_formats}")
        return v


class PageMetadata(BaseModel):
    """Metadata extracted from the webpage."""

    title: str | None = Field(None, description="Page title")
    description: str | None = Field(None, description="Page meta description")
    language: str | None = Field(None, description="Page language")
    keywords: str | None = Field(None, description="Page keywords")
    robots: str | None = Field(None, description="Robots meta tag")
    og_title: str | None = Field(None, description="Open Graph title")
    og_description: str | None = Field(None, description="Open Graph description")
    og_url: str | None = Field(None, description="Open Graph URL")
    og_image: str | None = Field(None, description="Open Graph image")
    og_locale: str | None = Field(None, description="Open Graph locale")
    og_site_name: str | None = Field(None, description="Open Graph site name")
    twitter_card: str | None = Field(None, description="Twitter card type")
    twitter_title: str | None = Field(None, description="Twitter title")
    twitter_description: str | None = Field(None, description="Twitter description")
    twitter_image: str | None = Field(None, description="Twitter image")


class FirecrawlScrapeResponse(BaseModel):
    """Response from Firecrawl scraping operation."""

    success: bool = Field(..., description="Whether the scraping was successful")
    url: str = Field(..., description="The URL that was scraped")
    markdown: str | None = Field(None, description="Page content in Markdown format")
    html: str | None = Field(None, description="Cleaned HTML content")
    raw_html: str | None = Field(None, description="Raw HTML content")
    content: str | None = Field(None, description="Plain text content")
    links: list[str] | None = Field(None, description="List of links found on the page")
    screenshot: str | None = Field(None, description="Base64 encoded screenshot")
    metadata: PageMetadata | None = Field(None, description="Page metadata")
    error: str | None = Field(None, description="Error message if scraping failed")


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def scrape_website(args: FirecrawlScrapeArgs) -> FirecrawlScrapeResponse:
    """Scrape a website using Firecrawl to extract structured content.

    This function uses Firecrawl's advanced scraping capabilities to extract
    clean, structured content from web pages, including handling JavaScript-rendered
    content and providing multiple output formats.
    """
    try:
        # Initialize Firecrawl with API key
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return FirecrawlScrapeResponse(
                success=False,
                url=args.url,
                markdown=None,
                html=None,
                raw_html=None,
                content=None,
                links=None,
                screenshot=None,
                metadata=None,
                error="FIRECRAWL_API_KEY environment variable not set"
            )

        app = FirecrawlApp(api_key=api_key)

        # Prepare scrape parameters
        params = {
            "formats": args.formats,
            "onlyMainContent": args.only_main_content,
            "removeScripts": args.remove_scripts
        }

        # Add optional parameters
        if args.include_tags:
            params["includeTags"] = args.include_tags
        if args.exclude_tags:
            params["excludeTags"] = args.exclude_tags
        if args.wait_for:
            params["waitFor"] = args.wait_for
        if args.screenshot:
            params["screenshot"] = True

        # Perform the scrape
        result = app.scrape_url(args.url, params=params)

        if not result or not result.get("success"):
            error_msg = result.get("error", "Unknown error occurred") if result else "No response from Firecrawl"
            return FirecrawlScrapeResponse(
                success=False,
                url=args.url,
                markdown=None,
                html=None,
                raw_html=None,
                content=None,
                links=None,
                screenshot=None,
                metadata=None,
                error=error_msg
            )

        # Extract metadata if available
        metadata = None
        if "metadata" in result:
            meta_data = result["metadata"]
            metadata = PageMetadata(
                title=meta_data.get("title"),
                description=meta_data.get("description"),
                language=meta_data.get("language"),
                keywords=meta_data.get("keywords"),
                robots=meta_data.get("robots"),
                og_title=meta_data.get("ogTitle"),
                og_description=meta_data.get("ogDescription"),
                og_url=meta_data.get("ogUrl"),
                og_image=meta_data.get("ogImage"),
                og_locale=meta_data.get("ogLocale"),
                og_site_name=meta_data.get("ogSiteName"),
                twitter_card=meta_data.get("twitterCard"),
                twitter_title=meta_data.get("twitterTitle"),
                twitter_description=meta_data.get("twitterDescription"),
                twitter_image=meta_data.get("twitterImage")
            )

        # Build response
        response = FirecrawlScrapeResponse(
            success=True,
            url=args.url,
            markdown=result.get("markdown") if "markdown" in args.formats else None,
            html=result.get("html") if "html" in args.formats else None,
            raw_html=result.get("rawHtml") if "rawHtml" in args.formats else None,
            content=result.get("content") if "content" in args.formats else None,
            links=result.get("links") if "links" in args.formats else None,
            screenshot=result.get("screenshot") if "screenshot" in args.formats else None,
            metadata=metadata,
            error=None
        )

        return response

    except Exception as e:
        return FirecrawlScrapeResponse(
            success=False,
            url=args.url,
            markdown=None,
            html=None,
            raw_html=None,
            content=None,
            links=None,
            screenshot=None,
            metadata=None,
            error=f"Error scraping website: {str(e)}"
        )
