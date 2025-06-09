"""Test suite for youtube_video_search_tool following best practices."""

import pytest

# Import the tool functions
from packages.funcn_registry.components.tools.youtube_video_search_tool.tool import (
    get_video_transcript,
    search_youtube_videos,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestYoutubeVideoSearchTool(BaseToolTest):
    """Test cases for YouTube video search and transcript extraction tool."""

    component_name = "youtube_video_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/youtube_video_search_tool")

    def get_component_function(self):
        """Get the main tool function."""
        return search_youtube_videos

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {"query": "python programming tutorial", "max_results": 5},
            {"query": "machine learning basics", "max_results": 10},
            {"query": "data science projects", "max_results": 3},
        ]

    def test_search_youtube_videos_success(self):
        """Test successful YouTube video search."""
        mock_search_results = {
            "items": [
                {
                    "id": {"videoId": "abc123"},
                    "snippet": {
                        "title": "Python Programming Tutorial",
                        "description": "Learn Python basics in this tutorial",
                        "channelTitle": "Code Academy",
                        "publishedAt": "2024-01-15T10:00:00Z",
                    },
                },
                {
                    "id": {"videoId": "def456"},
                    "snippet": {
                        "title": "Advanced Python Techniques",
                        "description": "Master advanced Python concepts",
                        "channelTitle": "Python Masters",
                        "publishedAt": "2024-01-20T15:30:00Z",
                    },
                },
            ]
        }

        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.googleapiclient.discovery.build"
        ) as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            mock_search = Mock()
            mock_youtube.search.return_value = mock_search
            mock_search.list.return_value.execute.return_value = mock_search_results

            results = search_youtube_videos("python programming", max_results=2)

            assert len(results) == 2
            assert results[0]["video_id"] == "abc123"
            assert results[0]["title"] == "Python Programming Tutorial"
            assert results[0]["channel"] == "Code Academy"
            assert "url" in results[0]
            assert "abc123" in results[0]["url"]

    def test_search_with_no_results(self):
        """Test search that returns no results."""
        mock_search_results = {"items": []}

        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.googleapiclient.discovery.build"
        ) as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            mock_search = Mock()
            mock_youtube.search.return_value = mock_search
            mock_search.list.return_value.execute.return_value = mock_search_results

            results = search_youtube_videos("very specific unusual query 12345", max_results=5)

            assert results == []

    def test_get_video_transcript_success(self):
        """Test successful transcript retrieval."""
        mock_transcript = [
            {"text": "Welcome to this Python tutorial.", "start": 0.0, "duration": 3.5},
            {"text": "Today we'll learn about functions.", "start": 3.5, "duration": 4.0},
            {"text": "Functions are reusable blocks of code.", "start": 7.5, "duration": 3.8},
        ]

        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.YouTubeTranscriptApi.get_transcript"
        ) as mock_get_transcript:
            mock_get_transcript.return_value = mock_transcript

            result = get_video_transcript("abc123")

            assert result["video_id"] == "abc123"
            assert result["transcript"] == (
                "Welcome to this Python tutorial. Today we'll learn about functions. Functions are reusable blocks of code."
            )
            assert result["segments"] == mock_transcript
            assert result["duration"] > 0

    def test_get_transcript_with_language(self):
        """Test transcript retrieval with specific language."""
        mock_transcript = [
            {"text": "Bienvenue dans ce tutoriel Python.", "start": 0.0, "duration": 3.5},
            {"text": "Aujourd'hui, nous apprendrons les fonctions.", "start": 3.5, "duration": 4.0},
        ]

        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.YouTubeTranscriptApi.get_transcript"
        ) as mock_get_transcript:
            mock_get_transcript.return_value = mock_transcript

            result = get_video_transcript("abc123", languages=["fr"])

            assert "Bienvenue" in result["transcript"]
            mock_get_transcript.assert_called_once_with("abc123", languages=["fr"])

    def test_get_transcript_not_available(self):
        """Test handling when transcript is not available."""
        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.YouTubeTranscriptApi.get_transcript"
        ) as mock_get_transcript:
            mock_get_transcript.side_effect = Exception("No transcript available")

            with pytest.raises(Exception) as exc_info:
                get_video_transcript("xyz789")

            assert "No transcript available" in str(exc_info.value)

    def test_search_with_api_error(self):
        """Test handling of YouTube API errors."""
        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.googleapiclient.discovery.build"
        ) as mock_build:
            mock_build.side_effect = Exception("API quota exceeded")

            with pytest.raises(Exception) as exc_info:
                search_youtube_videos("test query")

            assert "API quota exceeded" in str(exc_info.value)

    def test_search_with_invalid_max_results(self):
        """Test search with invalid max_results parameter."""
        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.googleapiclient.discovery.build"
        ) as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            mock_search = Mock()
            mock_youtube.search.return_value = mock_search

            # YouTube API has a max limit of 50 results per request
            mock_search.list.side_effect = Exception("Invalid max_results value")

            with pytest.raises(Exception) as exc_info:
                search_youtube_videos("test", max_results=100)

            assert "Invalid max_results" in str(exc_info.value)

    def test_video_url_construction(self):
        """Test that video URLs are correctly constructed."""
        mock_search_results = {
            "items": [
                {
                    "id": {"videoId": "test123"},
                    "snippet": {
                        "title": "Test Video",
                        "description": "Test description",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2024-01-01T00:00:00Z",
                    },
                }
            ]
        }

        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.googleapiclient.discovery.build"
        ) as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            mock_search = Mock()
            mock_youtube.search.return_value = mock_search
            mock_search.list.return_value.execute.return_value = mock_search_results

            results = search_youtube_videos("test", max_results=1)

            assert results[0]["url"] == "https://www.youtube.com/watch?v=test123"

    def test_transcript_duration_calculation(self):
        """Test that transcript duration is correctly calculated."""
        mock_transcript = [
            {"text": "Part 1", "start": 0.0, "duration": 10.5},
            {"text": "Part 2", "start": 10.5, "duration": 15.3},
            {"text": "Part 3", "start": 25.8, "duration": 8.7},
        ]

        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.YouTubeTranscriptApi.get_transcript"
        ) as mock_get_transcript:
            mock_get_transcript.return_value = mock_transcript

            result = get_video_transcript("test123")

            # Total duration should be sum of all durations
            expected_duration = 10.5 + 15.3 + 8.7
            assert abs(result["duration"] - expected_duration) < 0.1

    def test_empty_transcript_handling(self):
        """Test handling of empty transcript."""
        mock_transcript = []

        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.YouTubeTranscriptApi.get_transcript"
        ) as mock_get_transcript:
            mock_get_transcript.return_value = mock_transcript

            result = get_video_transcript("empty123")

            assert result["transcript"] == ""
            assert result["segments"] == []
            assert result["duration"] == 0

    def test_search_results_fields(self):
        """Test that all expected fields are present in search results."""
        mock_search_results = {
            "items": [
                {
                    "id": {"videoId": "field_test"},
                    "snippet": {
                        "title": "Complete Video",
                        "description": "Full description here",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2024-02-01T12:00:00Z",
                        "thumbnails": {
                            "default": {"url": "https://example.com/thumb.jpg"},
                            "high": {"url": "https://example.com/thumb_hq.jpg"},
                        },
                    },
                }
            ]
        }

        with patch(
            "packages.funcn_registry.components.tools.youtube_video_search_tool.tool.googleapiclient.discovery.build"
        ) as mock_build:
            mock_youtube = Mock()
            mock_build.return_value = mock_youtube
            mock_search = Mock()
            mock_youtube.search.return_value = mock_search
            mock_search.list.return_value.execute.return_value = mock_search_results

            results = search_youtube_videos("test", max_results=1)

            result = results[0]
            assert "video_id" in result
            assert "title" in result
            assert "description" in result
            assert "channel" in result
            assert "published_at" in result
            assert "url" in result

    def test_missing_api_key(self):
        """Test behavior when YouTube API key is missing."""
        with patch("packages.funcn_registry.components.tools.youtube_video_search_tool.tool.os.getenv", return_value=None):
            with pytest.raises(ValueError) as exc_info:
                search_youtube_videos("test query")

            assert "YOUTUBE_API_KEY" in str(exc_info.value)

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        # For search results
        if isinstance(output, list):
            for item in output:
                assert isinstance(item, dict), "Each search result should be a dictionary"
                assert "video_id" in item
                assert "title" in item
                assert "url" in item
        # For transcript results
        elif isinstance(output, dict) and "transcript" in output:
            assert "video_id" in output
            assert "transcript" in output
            assert "segments" in output
            assert isinstance(output["segments"], list)

    @pytest.mark.unit
    def test_both_functions_have_docstrings(self):
        """Test that both exported functions have proper docstrings."""
        functions = [search_youtube_videos, get_video_transcript]

        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 20
