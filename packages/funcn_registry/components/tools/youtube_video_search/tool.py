"""YouTube Video Search Tool for video content analysis and transcript extraction."""

import asyncio
import httpx
import re
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional
from urllib.parse import parse_qs, quote_plus, urlparse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled


class TranscriptSegment(BaseModel):
    """Represents a segment of video transcript."""

    text: str = Field(..., description="The transcript text")
    start: float = Field(..., description="Start time in seconds")
    duration: float = Field(..., description="Duration of the segment")
    end: float = Field(..., description="End time in seconds")

    @property
    def formatted_time(self) -> str:
        """Get formatted timestamp (HH:MM:SS)."""
        hours = int(self.start // 3600)
        minutes = int((self.start % 3600) // 60)
        seconds = int(self.start % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class VideoInfo(BaseModel):
    """Information about a YouTube video."""

    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    channel_name: str = Field(..., description="Channel name")
    description: str | None = Field(None, description="Video description")
    duration: str | None = Field(None, description="Video duration")
    view_count: int | None = Field(None, description="Number of views")
    published_at: datetime | None = Field(None, description="Publication date")
    thumbnail_url: str | None = Field(None, description="Thumbnail URL")
    video_url: str = Field(..., description="Full YouTube URL")
    has_transcript: bool = Field(False, description="Whether transcript is available")

    @classmethod
    def from_search_result(cls, item: dict[str, Any]) -> "VideoInfo":
        """Create VideoInfo from YouTube API search result."""
        video_id = item.get("id", {}).get("videoId", "")
        snippet = item.get("snippet", {})

        # Parse published date
        published_at = None
        if snippet.get("publishedAt"):
            try:
                published_at = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))
            except:
                pass

        return cls(
            video_id=video_id,
            title=snippet.get("title", ""),
            channel_name=snippet.get("channelTitle", ""),
            description=snippet.get("description"),
            published_at=published_at,
            thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
            video_url=f"https://www.youtube.com/watch?v={video_id}"
        )


class VideoSearchResult(BaseModel):
    """Result of YouTube video search."""

    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="The search query used")
    total_results: int = Field(..., description="Total number of results found")
    videos: list[VideoInfo] = Field(default_factory=list, description="List of videos found")
    error: str | None = Field(None, description="Error message if search failed")
    next_page_token: str | None = Field(None, description="Token for next page of results")


async def search_youtube_videos(
    query: str,
    api_key: str,
    max_results: int = 10,
    order: Literal["relevance", "date", "rating", "viewCount", "title"] = "relevance",
    published_after: datetime | None = None,
    published_before: datetime | None = None,
    channel_id: str | None = None,
    video_duration: Literal["short", "medium", "long"] | None = None,
    region_code: str = "US",
    language: str = "en"
) -> VideoSearchResult:
    """Search YouTube videos using the YouTube Data API.

    Args:
        query: Search query string
        api_key: YouTube Data API key
        max_results: Maximum number of results to return (1-50)
        order: Sort order for results
        published_after: Only return videos published after this date
        published_before: Only return videos published before this date
        channel_id: Only return videos from this channel
        video_duration: Filter by duration (short: <4min, medium: 4-20min, long: >20min)
        region_code: Region code for results
        language: Language code for results

    Returns:
        VideoSearchResult with found videos
    """
    try:
        # Build API request
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results, 50),
            "order": order,
            "regionCode": region_code,
            "relevanceLanguage": language,
            "key": api_key
        }

        # Add optional filters
        if published_after:
            params["publishedAfter"] = published_after.isoformat() + "Z"
        if published_before:
            params["publishedBefore"] = published_before.isoformat() + "Z"
        if channel_id:
            params["channelId"] = channel_id
        if video_duration:
            params["videoDuration"] = video_duration

        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

        # Parse results
        videos = []
        for item in data.get("items", []):
            video_info = VideoInfo.from_search_result(item)
            videos.append(video_info)

        return VideoSearchResult(
            success=True,
            query=query,
            total_results=data.get("pageInfo", {}).get("totalResults", len(videos)),
            videos=videos,
            next_page_token=data.get("nextPageToken")
        )

    except Exception as e:
        return VideoSearchResult(
            success=False,
            query=query,
            total_results=0,
            error=str(e)
        )


async def get_video_transcript(
    video_id: str,
    languages: list[str] | None = None,
    preserve_formatting: bool = True,
    include_timestamps: bool = True
) -> tuple[bool, list[TranscriptSegment], str | None]:
    """Get transcript for a YouTube video.

    Args:
        video_id: YouTube video ID
        languages: Preferred languages for transcript (e.g., ['en', 'es'])
        preserve_formatting: Whether to preserve text formatting
        include_timestamps: Whether to include timestamp information

    Returns:
        Tuple of (success, transcript_segments, error_message)
    """
    try:
        # Extract video ID from URL if provided
        if "youtube.com" in video_id or "youtu.be" in video_id:
            parsed = urlparse(video_id)
            if "youtube.com" in parsed.netloc:
                video_id = parse_qs(parsed.query).get("v", [None])[0]
            elif "youtu.be" in parsed.netloc:
                video_id = parsed.path.lstrip("/")

        if not video_id:
            return False, [], "Invalid video ID or URL"

        # Get transcript
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to find transcript in preferred languages
        transcript = None
        if languages:
            try:
                transcript = transcript_list.find_transcript(languages)
            except:
                # Fall back to any available transcript
                transcript = transcript_list.find_generated_transcript(languages) if languages else None

        # If no preferred language found, get first available
        if not transcript:
            for t in transcript_list:
                transcript = t
                break

        if not transcript:
            return False, [], "No transcript available for this video"

        # Fetch the transcript data
        transcript_data = transcript.fetch()

        # Convert to TranscriptSegment objects
        segments = []
        for item in transcript_data:
            segment = TranscriptSegment(
                text=item["text"],
                start=item["start"],
                duration=item["duration"],
                end=item["start"] + item["duration"]
            )
            segments.append(segment)

        # Format if requested
        if not preserve_formatting:
            for segment in segments:
                segment.text = segment.text.replace("\n", " ").strip()

        return True, segments, None

    except TranscriptsDisabled:
        return False, [], "Transcripts are disabled for this video"
    except NoTranscriptFound:
        return False, [], "No transcript found for this video"
    except Exception as e:
        return False, [], f"Error fetching transcript: {str(e)}"


async def search_videos_with_transcript(
    query: str,
    api_key: str,
    transcript_search: str | None = None,
    max_results: int = 10,
    languages: list[str] | None = None
) -> list[dict[str, Any]]:
    """Search YouTube videos and include transcript search.

    Args:
        query: YouTube search query
        api_key: YouTube Data API key
        transcript_search: Optional text to search within transcripts
        max_results: Maximum number of results
        languages: Preferred transcript languages

    Returns:
        List of video results with transcript matches
    """
    # First, search for videos
    search_result = await search_youtube_videos(query, api_key, max_results)

    if not search_result.success:
        return []

    results = []

    for video in search_result.videos:
        video_data = video.dict()

        # Get transcript
        success, segments, error = await get_video_transcript(
            video.video_id,
            languages=languages
        )

        video_data["has_transcript"] = success
        video_data["transcript_error"] = error

        if success and transcript_search:
            # Search within transcript
            matching_segments = []
            full_transcript = " ".join(s.text for s in segments)

            if transcript_search.lower() in full_transcript.lower():
                # Find matching segments
                for segment in segments:
                    if transcript_search.lower() in segment.text.lower():
                        matching_segments.append(segment.dict())

                video_data["transcript_matches"] = matching_segments
                video_data["match_count"] = len(matching_segments)
            else:
                video_data["transcript_matches"] = []
                video_data["match_count"] = 0

        results.append(video_data)

    # Sort by match count if transcript search was provided
    if transcript_search:
        results.sort(key=lambda x: x.get("match_count", 0), reverse=True)

    return results


async def analyze_video_content(
    video_id: str,
    api_key: str,
    include_stats: bool = True,
    include_comments: bool = False,
    max_comments: int = 100
) -> dict[str, Any]:
    """Analyze video content including metadata, transcript, and optionally comments.

    Args:
        video_id: YouTube video ID
        api_key: YouTube Data API key
        include_stats: Whether to include video statistics
        include_comments: Whether to include top comments
        max_comments: Maximum number of comments to retrieve

    Returns:
        Dictionary with comprehensive video analysis
    """
    analysis = {
        "video_id": video_id,
        "success": False,
        "error": None
    }

    try:
        # Get video details
        async with httpx.AsyncClient() as client:
            # Video details request
            video_url = "https://www.googleapis.com/youtube/v3/videos"
            video_params = {
                "part": "snippet,contentDetails,statistics",
                "id": video_id,
                "key": api_key
            }

            response = await client.get(video_url, params=video_params)
            response.raise_for_status()
            video_data = response.json()

            if not video_data.get("items"):
                analysis["error"] = "Video not found"
                return analysis

            video_item = video_data["items"][0]
            snippet = video_item.get("snippet", {})

            # Parse video info
            analysis.update({
                "success": True,
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "channel": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "tags": snippet.get("tags", []),
                "category_id": snippet.get("categoryId"),
                "duration": video_item.get("contentDetails", {}).get("duration")
            })

            # Add statistics if requested
            if include_stats:
                stats = video_item.get("statistics", {})
                analysis["statistics"] = {
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0))
                }

            # Get transcript
            success, segments, error = await get_video_transcript(video_id)

            if success:
                analysis["transcript"] = {
                    "available": True,
                    "segment_count": len(segments),
                    "total_duration": segments[-1].end if segments else 0,
                    "full_text": " ".join(s.text for s in segments),
                    "word_count": sum(len(s.text.split()) for s in segments)
                }
            else:
                analysis["transcript"] = {
                    "available": False,
                    "error": error
                }

            # Get comments if requested
            if include_comments:
                comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"
                comments_params = {
                    "part": "snippet",
                    "videoId": video_id,
                    "maxResults": min(max_comments, 100),
                    "order": "relevance",
                    "key": api_key
                }

                try:
                    response = await client.get(comments_url, params=comments_params)
                    response.raise_for_status()
                    comments_data = response.json()

                    comments = []
                    for item in comments_data.get("items", []):
                        comment = item["snippet"]["topLevelComment"]["snippet"]
                        comments.append({
                            "author": comment.get("authorDisplayName"),
                            "text": comment.get("textDisplay"),
                            "likes": comment.get("likeCount", 0),
                            "published_at": comment.get("publishedAt")
                        })

                    analysis["comments"] = {
                        "available": True,
                        "count": len(comments),
                        "comments": comments
                    }
                except:
                    analysis["comments"] = {
                        "available": False,
                        "error": "Could not retrieve comments"
                    }

        return analysis

    except Exception as e:
        analysis["error"] = str(e)
        return analysis
