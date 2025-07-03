"""Nimble Search Tool - Implementation of Nimble's Web, SERP, and Maps APIs."""

import os
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import Any, Optional
from urllib.parse import quote

# Get Nimble API token from environment
NIMBLE_TOKEN = os.getenv("NIMBLE_API_KEY", "")


class NimbleSearchArgs(BaseModel):
    """Arguments for Nimble Web API search."""

    query: str = Field(..., description="The search query")
    parse: bool = Field(default=True, description="Whether to parse the results")
    render: bool = Field(default=True, description="Whether to render JavaScript")
    country: str = Field(default="US", description="Country code for search results")
    locale: str = Field(default="en", description="Locale for search results")


class NimbleSERPSearchArgs(BaseModel):
    """Arguments for Nimble SERP API search."""

    query: str = Field(..., description="The search query")
    search_engine: str = Field(default="google_search", description="Search engine to use")
    parse: bool = Field(default=True, description="Whether to parse the results")
    country: str = Field(default="US", description="Country code for search results")
    locale: str = Field(default="en", description="Locale for search results")
    page: int = Field(default=1, description="Page number for pagination")


class NimbleMapsSearchArgs(BaseModel):
    """Arguments for Nimble Maps API search."""

    query: str = Field(..., description="Search query for places")
    latitude: float | None = Field(None, description="Latitude for location-based search")
    longitude: float | None = Field(None, description="Longitude for location-based search")
    radius: int | None = Field(None, description="Search radius in meters")
    country: str = Field(default="US", description="Country code for search results")
    locale: str = Field(default="en", description="Locale for search results")


def get_content(url: str) -> str:
    """Extract text content from a URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content from paragraphs
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        # If no paragraphs, try to get all text
        if not content:
            content = soup.get_text(separator="\n", strip=True)

        return content[:5000]  # Limit content to 5000 characters
    except Exception as e:
        return f"Error fetching content from {url}: {str(e)}"


def nimble_serp_search(args: NimbleSERPSearchArgs) -> dict[str, Any]:
    """
    Use Nimble SERP API to get search engine results.

    This provides structured search results from various search engines including
    Google, Bing, DuckDuckGo, and others.

    Args:
        args: Search arguments including query, search engine, and locale

    Returns:
        Dictionary containing search results with sources and content
    """
    if not NIMBLE_TOKEN:
        return {"error": "NIMBLE_API_KEY environment variable not set"}

    url = "https://api.webit.live/api/v1/realtime/serp"
    headers = {
        "Authorization": f"Basic {NIMBLE_TOKEN}",
        "Content-Type": "application/json",
    }

    search_data = {
        "parse": args.parse,
        "query": args.query,
        "search_engine": args.search_engine,
        "format": "json",
        "render": True,
        "country": args.country,
        "locale": args.locale,
        "page": args.page,
    }

    try:
        response = requests.post(url, json=search_data, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract organic results
        results = data.get("parsing", {}).get("entities", {}).get("OrganicResult", [])

        # Build search results with content
        search_results: dict[str, Any] = {
            "query": args.query,
            "search_engine": args.search_engine,
            "results": [],
            "sources": [],
        }

        for result in results[:10]:  # Limit to top 10 results
            url = result.get("url", "")
            if url:
                search_results["sources"].append(url)
                search_results["results"].append(
                    {
                        "title": result.get("title", ""),
                        "url": url,
                        "snippet": result.get("snippet", ""),
                    }
                )

        # Optionally fetch content from top URLs
        if len(search_results["sources"]) > 0:
            # Get content from top 3 URLs
            for url in search_results["sources"][:3]:
                content = get_content(url)
                for result in search_results["results"]:
                    if result["url"] == url:
                        result["content"] = content
                        break

        return search_results

    except requests.exceptions.RequestException as e:
        return {"error": f"Nimble API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def nimble_search(args: NimbleSearchArgs) -> dict[str, Any]:
    """
    Use Nimble Web API for general web data collection.

    This is a more flexible API that can extract data from any URL with
    optional parsing and JavaScript rendering.

    Args:
        args: Search arguments including query and parsing options

    Returns:
        Dictionary containing extracted web data
    """
    # For general search, we'll use Google search via Web API
    if not NIMBLE_TOKEN:
        return {"error": "NIMBLE_API_KEY environment variable not set"}

    # First, construct a Google search URL
    search_url = f"https://www.google.com/search?q={quote(args.query)}"

    url = "https://api.webit.live/api/v1/realtime/web"
    headers = {
        "Authorization": f"Basic {NIMBLE_TOKEN}",
        "Content-Type": "application/json",
    }

    request_data = {
        "url": search_url,
        "parse": args.parse,
        "render": args.render,
        "country": args.country,
        "locale": args.locale,
    }

    try:
        response = requests.post(url, json=request_data, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract search results from parsed data
        parsing_data = data.get("parsing", {})

        return {
            "query": args.query,
            "url": search_url,
            "parsed_data": parsing_data,
            "html_content": data.get("html_content", "")[:1000] if not args.parse else None,
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Nimble Web API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def nimble_maps_search(args: NimbleMapsSearchArgs) -> dict[str, Any]:
    """
    Use Nimble Maps API to search for places and locations.

    This API provides location-based search results including businesses,
    landmarks, and geographic locations.

    Args:
        args: Search arguments including query and optional coordinates

    Returns:
        Dictionary containing place search results
    """
    if not NIMBLE_TOKEN:
        return {"error": "NIMBLE_API_KEY environment variable not set"}

    url = "https://api.webit.live/api/v1/realtime/maps"
    headers = {
        "Authorization": f"Basic {NIMBLE_TOKEN}",
        "Content-Type": "application/json",
    }

    search_data: dict[str, Any] = {
        "query": args.query,
        "search_engine": "google_maps_search",
        "country": args.country,
        "locale": args.locale,
    }

    # Add location parameters if provided
    if args.latitude is not None and args.longitude is not None:
        search_data["coordinates"] = {
            "latitude": args.latitude,
            "longitude": args.longitude,
        }
    if args.radius is not None:
        search_data["radius"] = args.radius

    try:
        response = requests.post(url, json=search_data, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract place results
        results = data.get("parsing", {}).get("entities", {}).get("PlaceResult", [])

        places = []
        for place in results[:10]:  # Limit to top 10 places
            places.append(
                {
                    "name": place.get("name", ""),
                    "address": place.get("address", ""),
                    "rating": place.get("rating", None),
                    "review_count": place.get("review_count", None),
                    "phone": place.get("phone", ""),
                    "website": place.get("website", ""),
                    "coordinates": place.get("coordinates", {}),
                    "place_id": place.get("place_id", ""),
                }
            )

        return {
            "query": args.query,
            "places": places,
            "total_results": len(results),
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Nimble Maps API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
