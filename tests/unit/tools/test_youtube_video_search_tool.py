"""Test suite for youtube_video_search_tool following best practices."""

import asyncio
import os
import pytest
from datetime import datetime, timedelta

# Import the tool functions and models
from packages.funcn_registry.components.tools.youtube_video_search.tool import (
    TranscriptSegment,
    VideoInfo,
    VideoSearchResult,
    analyze_video_content,
    get_video_transcript,
    search_videos_with_transcript,
    search_youtube_videos,
)
from pathlib import Path
from pydantic import ValidationError
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class TestYoutubeVideoSearchTool(BaseToolTest):
    """Test cases for YouTube video search and transcript extraction tool."""

    component_name = "youtube_video_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/youtube_video_search")
    
    def create_mock_search_item(self, video_id="test123", title="Test Video", 
                                channel="Test Channel", description="Test description",
                                published_at="2024-01-15T10:00:00Z"):
        """Create a mock YouTube API search result item."""
        return {
            "id": {"videoId": video_id},
            "snippet": {
                "title": title,
                "description": description,
                "channelTitle": channel,
                "publishedAt": published_at,
                "thumbnails": {
                    "default": {"url": f"https://i.ytimg.com/vi/{video_id}/default.jpg"},
                    "high": {"url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"}
                }
            }
        }
    
    def create_mock_video_item(self, video_id="test123", title="Test Video",
                               channel="Test Channel", view_count=1000, like_count=100):
        """Create a mock YouTube API video item with full details."""
        return {
            "id": video_id,
            "snippet": {
                "title": title,
                "description": "Full video description",
                "channelTitle": channel,
                "publishedAt": "2024-01-15T10:00:00Z",
                "tags": ["test", "video"],
                "categoryId": "22"
            },
            "contentDetails": {
                "duration": "PT10M30S"
            },
            "statistics": {
                "viewCount": str(view_count),
                "likeCount": str(like_count),
                "commentCount": "50"
            }
        }
    
    def create_mock_transcript_segment(self, text, start, duration):
        """Create a mock transcript segment."""
        return {
            "text": text,
            "start": start,
            "duration": duration,
            "end": start + duration
        }
    
    def create_mock_comment(self, author="Test User", text="Great video!", likes=5):
        """Create a mock YouTube comment."""
        return {
            "snippet": {
                "topLevelComment": {
                    "snippet": {
                        "authorDisplayName": author,
                        "textDisplay": text,
                        "likeCount": likes,
                        "publishedAt": "2024-01-16T12:00:00Z"
                    }
                }
            }
        }

    def get_component_function(self):
        """Get the main tool function."""
        return search_youtube_videos

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {"query": "python programming tutorial", "api_key": "test_key", "max_results": 5},
            {"query": "machine learning basics", "api_key": "test_key", "max_results": 10},
            {"query": "data science projects", "api_key": "test_key", "max_results": 3},
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        assert isinstance(output, VideoSearchResult)
        assert hasattr(output, 'success')
        assert hasattr(output, 'query')
        assert hasattr(output, 'total_results')
        assert hasattr(output, 'videos')
        assert isinstance(output.videos, list)
        
        for video in output.videos:
            assert isinstance(video, VideoInfo)
            assert hasattr(video, 'video_id')
            assert hasattr(video, 'title')
            assert hasattr(video, 'channel_name')
            assert hasattr(video, 'video_url')

    @pytest.mark.asyncio
    async def test_search_youtube_videos_basic(self):
        """Test basic YouTube video search functionality."""
        mock_response = {
            "items": [
                self.create_mock_search_item("abc123", "Python Tutorial"),
                self.create_mock_search_item("def456", "Python Advanced")
            ],
            "pageInfo": {"totalResults": 100},
            "nextPageToken": "NEXT_TOKEN"
        }
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response_obj)
            
            result = await search_youtube_videos("python tutorial", "test_api_key", max_results=2)
            
            assert result.success is True
            assert result.query == "python tutorial"
            assert result.total_results == 100
            assert len(result.videos) == 2
            assert result.videos[0].video_id == "abc123"
            assert result.videos[0].title == "Python Tutorial"
            assert result.next_page_token == "NEXT_TOKEN"

    @pytest.mark.asyncio
    async def test_search_with_all_filters(self):
        """Test search with all optional filters."""
        mock_response = {"items": [], "pageInfo": {"totalResults": 0}}
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response_obj)
            
            published_after = datetime.now() - timedelta(days=7)
            published_before = datetime.now()
            
            result = await search_youtube_videos(
                query="test",
                api_key="test_key",
                max_results=25,
                order="viewCount",
                published_after=published_after,
                published_before=published_before,
                channel_id="UC_test_channel",
                video_duration="medium",
                region_code="GB",
                language="es"
            )
            
            # Verify API call parameters
            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            
            assert params["order"] == "viewCount"
            assert params["channelId"] == "UC_test_channel"
            assert params["videoDuration"] == "medium"
            assert params["regionCode"] == "GB"
            assert params["relevanceLanguage"] == "es"
            assert "publishedAfter" in params
            assert "publishedBefore" in params

    @pytest.mark.asyncio
    async def test_search_api_error_handling(self):
        """Test handling of API errors during search."""
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get.side_effect = Exception("API quota exceeded")
            
            result = await search_youtube_videos("test", "test_key")
            
            assert result.success is False
            assert "API quota exceeded" in result.error
            assert result.total_results == 0
            assert len(result.videos) == 0

    @pytest.mark.asyncio
    async def test_get_video_transcript_basic(self):
        """Test basic transcript retrieval."""
        mock_transcript_data = [
            self.create_mock_transcript_segment("Welcome to Python.", 0.0, 3.5),
            self.create_mock_transcript_segment("Today we learn functions.", 3.5, 4.0),
            self.create_mock_transcript_segment("Functions are reusable.", 7.5, 3.8)
        ]
        
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = mock_transcript_data
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.YouTubeTranscriptApi") as mock_api:
            mock_transcript_list = MagicMock()
            mock_api.list_transcripts.return_value = mock_transcript_list
            mock_transcript_list.__iter__.return_value = [mock_transcript]
            
            success, segments, error = await get_video_transcript("test123")
            
            assert success is True
            assert error is None
            assert len(segments) == 3
            assert segments[0].text == "Welcome to Python."
            assert segments[0].start == 0.0
            assert segments[0].duration == 3.5
            assert segments[0].end == 3.5
            assert segments[0].formatted_time == "00:00:00"

    @pytest.mark.asyncio
    async def test_get_transcript_from_url(self):
        """Test extracting video ID from YouTube URL."""
        mock_transcript_data = [
            self.create_mock_transcript_segment("Test content", 0.0, 5.0)
        ]
        
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = mock_transcript_data
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.YouTubeTranscriptApi") as mock_api:
            mock_transcript_list = MagicMock()
            mock_api.list_transcripts.return_value = mock_transcript_list
            mock_transcript_list.__iter__.return_value = [mock_transcript]
            
            # Test standard YouTube URL
            success, segments, error = await get_video_transcript("https://www.youtube.com/watch?v=abc123")
            assert success is True
            mock_api.list_transcripts.assert_called_with("abc123")
            
            # Test short YouTube URL
            mock_api.list_transcripts.reset_mock()
            success, segments, error = await get_video_transcript("https://youtu.be/xyz789")
            assert success is True
            mock_api.list_transcripts.assert_called_with("xyz789")

    @pytest.mark.asyncio
    async def test_get_transcript_with_languages(self):
        """Test transcript retrieval with specific languages."""
        mock_transcript_data = [
            self.create_mock_transcript_segment("Bonjour Python", 0.0, 3.0)
        ]
        
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = mock_transcript_data
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.YouTubeTranscriptApi") as mock_api:
            mock_transcript_list = MagicMock()
            mock_api.list_transcripts.return_value = mock_transcript_list
            mock_transcript_list.find_transcript.return_value = mock_transcript
            
            success, segments, error = await get_video_transcript("test123", languages=["fr", "es"])
            
            assert success is True
            mock_transcript_list.find_transcript.assert_called_with(["fr", "es"])

    @pytest.mark.asyncio
    async def test_get_transcript_disabled(self):
        """Test handling when transcripts are disabled."""
        from youtube_transcript_api._errors import TranscriptsDisabled
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.YouTubeTranscriptApi") as mock_api:
            mock_api.list_transcripts.side_effect = TranscriptsDisabled("test123")
            
            success, segments, error = await get_video_transcript("test123")
            
            assert success is False
            assert segments == []
            assert "Transcripts are disabled" in error

    @pytest.mark.asyncio
    async def test_get_transcript_not_found(self):
        """Test handling when no transcript is found."""
        from youtube_transcript_api._errors import NoTranscriptFound
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.YouTubeTranscriptApi") as mock_api:
            mock_api.list_transcripts.side_effect = NoTranscriptFound("test123", [], [])
            
            success, segments, error = await get_video_transcript("test123")
            
            assert success is False
            assert segments == []
            assert "No transcript found" in error

    @pytest.mark.asyncio
    async def test_get_transcript_formatting_options(self):
        """Test transcript formatting options."""
        mock_transcript_data = [
            self.create_mock_transcript_segment("Line one\nLine two", 0.0, 3.0),
            self.create_mock_transcript_segment("Line three\nLine four", 3.0, 3.0)
        ]
        
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = mock_transcript_data
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.YouTubeTranscriptApi") as mock_api:
            mock_transcript_list = MagicMock()
            mock_api.list_transcripts.return_value = mock_transcript_list
            mock_transcript_list.__iter__.return_value = [mock_transcript]
            
            # Test without preserving formatting
            success, segments, error = await get_video_transcript("test123", preserve_formatting=False)
            
            assert success is True
            assert segments[0].text == "Line one Line two"
            assert segments[1].text == "Line three Line four"

    @pytest.mark.asyncio
    async def test_search_videos_with_transcript(self):
        """Test combined video search with transcript search."""
        mock_search_response = {
            "items": [
                self.create_mock_search_item("video1", "Python Functions Tutorial"),
                self.create_mock_search_item("video2", "Python Classes Tutorial")
            ],
            "pageInfo": {"totalResults": 2}
        }
        
        mock_transcript1 = [
            self.create_mock_transcript_segment("Let's learn about functions", 0.0, 5.0),
            self.create_mock_transcript_segment("Functions are important", 5.0, 5.0)
        ]
        
        mock_transcript2 = [
            self.create_mock_transcript_segment("Classes in Python", 0.0, 5.0),
            self.create_mock_transcript_segment("Object-oriented programming", 5.0, 5.0)
        ]
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_search_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response_obj)
            
            # Mock transcript API
            with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.YouTubeTranscriptApi") as mock_api:
                # Setup different transcripts for each video
                def mock_list_transcripts(video_id):
                    mock_transcript_list = MagicMock()
                    mock_transcript = MagicMock()
                    
                    if video_id == "video1":
                        mock_transcript.fetch.return_value = mock_transcript1
                    else:
                        mock_transcript.fetch.return_value = mock_transcript2
                    
                    mock_transcript_list.__iter__.return_value = [mock_transcript]
                    return mock_transcript_list
                
                mock_api.list_transcripts.side_effect = mock_list_transcripts
                
                results = await search_videos_with_transcript(
                    "python tutorial", "test_key", transcript_search="functions", max_results=2
                )
                
                assert len(results) == 2
                # First video should have matches
                assert results[0]["has_transcript"] is True
                assert results[0]["match_count"] == 2
                assert len(results[0]["transcript_matches"]) == 2
                # Second video should have no matches
                assert results[1]["has_transcript"] is True
                assert results[1]["match_count"] == 0

    @pytest.mark.asyncio
    async def test_analyze_video_content_comprehensive(self):
        """Test comprehensive video content analysis."""
        mock_video_response = {
            "items": [self.create_mock_video_item("test123", view_count=5000, like_count=500)]
        }
        
        mock_comments_response = {
            "items": [
                self.create_mock_comment("User1", "Great tutorial!", 10),
                self.create_mock_comment("User2", "Very helpful", 5)
            ]
        }
        
        mock_transcript_data = [
            self.create_mock_transcript_segment("Introduction to Python", 0.0, 10.0),
            self.create_mock_transcript_segment("Variables and data types", 10.0, 20.0)
        ]
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Setup different responses for video details and comments
            async def mock_get(url, params):
                mock_response_obj = Mock()
                mock_response_obj.raise_for_status = Mock()
                
                if "videos" in url:
                    mock_response_obj.json.return_value = mock_video_response
                elif "commentThreads" in url:
                    mock_response_obj.json.return_value = mock_comments_response
                
                return mock_response_obj
            
            mock_client.get = mock_get
            
            # Mock transcript
            with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.get_video_transcript") as mock_transcript:
                segments = [TranscriptSegment(**seg) for seg in mock_transcript_data]
                mock_transcript.return_value = (True, segments, None)
                
                analysis = await analyze_video_content(
                    "test123", "test_key", include_stats=True, include_comments=True, max_comments=50
                )
                
                assert analysis["success"] is True
                assert analysis["video_id"] == "test123"
                assert analysis["title"] == "Test Video"
                assert analysis["channel"] == "Test Channel"
                
                # Check statistics
                assert analysis["statistics"]["view_count"] == 5000
                assert analysis["statistics"]["like_count"] == 500
                assert analysis["statistics"]["comment_count"] == 50
                
                # Check transcript
                assert analysis["transcript"]["available"] is True
                assert analysis["transcript"]["segment_count"] == 2
                assert analysis["transcript"]["word_count"] > 0
                
                # Check comments
                assert analysis["comments"]["available"] is True
                assert analysis["comments"]["count"] == 2
                assert len(analysis["comments"]["comments"]) == 2

    @pytest.mark.asyncio
    async def test_analyze_video_not_found(self):
        """Test analysis when video is not found."""
        mock_response = {"items": []}
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response_obj)
            
            analysis = await analyze_video_content("nonexistent", "test_key")
            
            assert analysis["success"] is False
            assert analysis["error"] == "Video not found"

    @pytest.mark.asyncio
    async def test_video_info_from_search_result(self):
        """Test VideoInfo creation from search result."""
        search_item = self.create_mock_search_item(
            video_id="test123",
            title="Test Title",
            channel="Test Channel",
            description="Test Description",
            published_at="2024-01-15T10:00:00Z"
        )
        
        video_info = VideoInfo.from_search_result(search_item)
        
        assert video_info.video_id == "test123"
        assert video_info.title == "Test Title"
        assert video_info.channel_name == "Test Channel"
        assert video_info.description == "Test Description"
        assert video_info.video_url == "https://www.youtube.com/watch?v=test123"
        assert video_info.thumbnail_url == "https://i.ytimg.com/vi/test123/hqdefault.jpg"
        assert video_info.published_at.year == 2024
        assert video_info.published_at.month == 1
        assert video_info.published_at.day == 15

    @pytest.mark.asyncio
    async def test_transcript_segment_formatting(self):
        """Test TranscriptSegment formatted time property."""
        segment = TranscriptSegment(
            text="Test segment",
            start=3665.5,  # 1 hour, 1 minute, 5.5 seconds
            duration=10.0,
            end=3675.5
        )
        
        assert segment.formatted_time == "01:01:05"
        
        # Test with smaller time
        segment2 = TranscriptSegment(
            text="Short segment",
            start=65.0,  # 1 minute, 5 seconds
            duration=5.0,
            end=70.0
        )
        
        assert segment2.formatted_time == "00:01:05"

    @pytest.mark.asyncio
    async def test_search_max_results_limit(self):
        """Test that max_results is capped at 50 per API limits."""
        mock_response = {"items": [], "pageInfo": {"totalResults": 0}}
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response_obj)
            
            await search_youtube_videos("test", "test_key", max_results=100)
            
            # Verify the maxResults param was capped at 50
            call_args = mock_client.get.call_args
            params = call_args[1]["params"]
            assert params["maxResults"] == 50

    @pytest.mark.asyncio
    async def test_empty_search_results(self):
        """Test handling of empty search results."""
        mock_response = {"items": [], "pageInfo": {"totalResults": 0}}
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = Mock()
            mock_client.get = AsyncMock(return_value=mock_response_obj)
            
            result = await search_youtube_videos("very specific unusual query xyz123", "test_key")
            
            assert result.success is True
            assert result.total_results == 0
            assert len(result.videos) == 0
            assert result.error is None

    @pytest.mark.asyncio
    async def test_concurrent_searches(self):
        """Test concurrent video searches."""
        mock_responses = [
            {"items": [self.create_mock_search_item("video1")], "pageInfo": {"totalResults": 1}},
            {"items": [self.create_mock_search_item("video2")], "pageInfo": {"totalResults": 1}},
            {"items": [self.create_mock_search_item("video3")], "pageInfo": {"totalResults": 1}}
        ]
        
        call_count = 0
        
        async def mock_get(*args, **kwargs):
            nonlocal call_count
            mock_response_obj = Mock()
            mock_response_obj.json.return_value = mock_responses[call_count]
            mock_response_obj.raise_for_status = Mock()
            call_count += 1
            return mock_response_obj
        
        with patch("packages.funcn_registry.components.tools.youtube_video_search.tool.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get = mock_get
            
            # Run concurrent searches
            results = await asyncio.gather(
                search_youtube_videos("query1", "key"),
                search_youtube_videos("query2", "key"),
                search_youtube_videos("query3", "key")
            )
            
            assert all(r.success for r in results)
            assert results[0].videos[0].video_id == "video1"
            assert results[1].videos[0].video_id == "video2"
            assert results[2].videos[0].video_id == "video3"

    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        functions = [search_youtube_videos, get_video_transcript, 
                     search_videos_with_transcript, analyze_video_content]
        
        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 20
