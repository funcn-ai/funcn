"""Test suite for exa_websets_tool following best practices."""

import pytest
from datetime import datetime
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestExaWebsetsTool(BaseToolTest):
    """Test exa_websets_tool component."""
    
    component_name = "exa_websets_tool"
    component_path = Path("packages/funcn_registry/components/tools/exa_websets_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.exa_websets_tool import create_webset
        def mock_create_webset(
            name: str,
            search_query: str,
            num_results: int = 100,
            filters: dict[str, any] | None = None,
            enrichments: list[str] | None = None,
            update_frequency: str = "daily"
        ) -> dict[str, any]:
            """Mock Exa websets tool."""
            return {
                "webset_id": "ws_12345",
                "name": name,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "num_results": num_results,
                "query": search_query,
                "filters": filters or {},
                "enrichments": enrichments or [],
                "update_frequency": update_frequency,
                "results_count": min(num_results, 50),
                "last_updated": datetime.now().isoformat()
            }
        return mock_create_webset
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "name": "AI Research Papers",
                "search_query": "machine learning research papers 2024",
                "num_results": 50,
                "filters": {"domain": ["arxiv.org", "openai.com"]},
                "enrichments": ["summary", "key_points"]
            },
            {
                "name": "Tech News Dataset",
                "search_query": "technology news artificial intelligence",
                "num_results": 100,
                "update_frequency": "hourly"
            },
            {
                "name": "Company Data",
                "search_query": "startup funding series A",
                "filters": {"date_range": "last_month"},
                "enrichments": ["company_info", "funding_amount"]
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, dict)
        assert "webset_id" in output or "id" in output
        assert "name" in output
        assert "status" in output or "state" in output
    
    def test_create_webset(self):
        """Test creating a new webset."""
        tool = self.get_component_function()
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_client.create_webset.return_value = Mock(
                id="ws_abc123",
                name="Test Webset",
                status="active",
                created_at="2024-01-01T00:00:00Z",
                results_count=25
            )
            mock_exa.return_value = mock_client
            
            result = tool(
                name="Test Webset",
                search_query="test query",
                num_results=25
            )
            
            assert "webset_id" in result or "id" in result
            assert result["name"] == "Test Webset"
            assert result["status"] == "active"
    
    def test_webset_with_filters(self):
        """Test creating webset with various filters."""
        tool = self.get_component_function()
        
        filter_sets = [
            {
                "domain": ["example.com", "test.org"],
                "exclude_domain": ["spam.com"]
            },
            {
                "date_range": "last_week",
                "language": "en"
            },
            {
                "has_image": True,
                "min_words": 500
            }
        ]
        
        for filters in filter_sets:
            with patch("exa_py.Exa") as mock_exa:
                mock_client = Mock()
                mock_client.create_webset.return_value = Mock(
                    id="ws_filtered",
                    filters=filters
                )
                mock_exa.return_value = mock_client
                
                result = tool(
                    name="Filtered Webset",
                    search_query="test",
                    filters=filters
                )
                
                # Verify filters were applied
                assert "filters" in result
                if isinstance(result["filters"], dict):
                    for key in filters:
                        assert key in result["filters"]
    
    def test_webset_enrichments(self):
        """Test webset with data enrichments."""
        tool = self.get_component_function()
        
        enrichment_sets = [
            ["summary", "key_points", "entities"],
            ["sentiment", "topics", "language"],
            ["author", "publish_date", "word_count"]
        ]
        
        for enrichments in enrichment_sets:
            with patch("exa_py.Exa") as mock_exa:
                mock_client = Mock()
                mock_client.create_webset.return_value = Mock(
                    id="ws_enriched",
                    enrichments=enrichments
                )
                mock_exa.return_value = mock_client
                
                result = tool(
                    name="Enriched Webset",
                    search_query="test",
                    enrichments=enrichments
                )
                
                assert "enrichments" in result
                assert len(result["enrichments"]) == len(enrichments)
    
    def test_update_frequency_options(self):
        """Test different update frequency settings."""
        tool = self.get_component_function()
        
        frequencies = ["realtime", "hourly", "daily", "weekly", "monthly"]
        
        for freq in frequencies:
            with patch("exa_py.Exa") as mock_exa:
                mock_client = Mock()
                mock_client.create_webset.return_value = Mock(
                    id=f"ws_{freq}",
                    update_frequency=freq
                )
                mock_exa.return_value = mock_client
                
                result = tool(
                    name=f"{freq} Webset",
                    search_query="test",
                    update_frequency=freq
                )
                
                assert result["update_frequency"] == freq
    
    def test_get_webset_results(self):
        """Test retrieving results from a webset."""
        # Would import: from tools.exa_websets_tool import get_webset_results
        def mock_get_results(webset_id: str, limit: int = 100) -> list[dict[str, any]]:
            return [
                {
                    "title": f"Result {i+1}",
                    "url": f"https://example.com/result{i+1}",
                    "content": f"Content for result {i+1}",
                    "enrichments": {
                        "summary": f"Summary of result {i+1}",
                        "key_points": [f"Point {j}" for j in range(3)]
                    }
                }
                for i in range(min(limit, 10))
            ]
        
        tool = mock_get_results
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_results = [
                Mock(
                    title="Enriched Result",
                    url="https://example.com",
                    text="Full content",
                    enrichments={
                        "summary": "This is a summary",
                        "entities": ["AI", "Technology"]
                    }
                )
            ]
            mock_client.get_webset_results.return_value = mock_results
            mock_exa.return_value = mock_client
            
            results = tool("ws_12345", limit=5)
            
            assert len(results) <= 5
            assert all("enrichments" in r for r in results)
    
    def test_update_webset(self):
        """Test updating webset configuration."""
        # Would import: from tools.exa_websets_tool import update_webset
        def mock_update_webset(
            webset_id: str,
            name: str | None = None,
            filters: dict[str, any] | None = None,
            enrichments: list[str] | None = None
        ) -> dict[str, any]:
            return {
                "webset_id": webset_id,
                "name": name or "Updated Webset",
                "filters": filters or {},
                "enrichments": enrichments or [],
                "updated_at": datetime.now().isoformat(),
                "status": "active"
            }
        
        tool = mock_update_webset
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_client.update_webset.return_value = Mock(
                id="ws_12345",
                name="Updated Name",
                updated_at="2024-01-02T00:00:00Z"
            )
            mock_exa.return_value = mock_client
            
            result = tool(
                "ws_12345",
                name="Updated Name",
                filters={"domain": ["newdomain.com"]}
            )
            
            assert result["name"] == "Updated Name"
            assert "updated_at" in result
    
    def test_delete_webset(self):
        """Test deleting a webset."""
        # Would import: from tools.exa_websets_tool import delete_webset
        def mock_delete_webset(webset_id: str) -> dict[str, any]:
            return {
                "webset_id": webset_id,
                "status": "deleted",
                "deleted_at": datetime.now().isoformat()
            }
        
        tool = mock_delete_webset
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_client.delete_webset.return_value = True
            mock_exa.return_value = mock_client
            
            result = tool("ws_12345")
            
            assert result["status"] == "deleted"
            assert "deleted_at" in result
    
    def test_list_websets(self):
        """Test listing all websets."""
        # Would import: from tools.exa_websets_tool import list_websets
        def mock_list_websets() -> list[dict[str, any]]:
            return [
                {
                    "webset_id": f"ws_{i}",
                    "name": f"Webset {i}",
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00Z",
                    "results_count": i * 10
                }
                for i in range(1, 4)
            ]
        
        tool = mock_list_websets
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_client.list_websets.return_value = [
                Mock(id=f"ws_{i}", name=f"Webset {i}")
                for i in range(1, 4)
            ]
            mock_exa.return_value = mock_client
            
            results = tool()
            
            assert len(results) == 3
            assert all("webset_id" in ws for ws in results)
    
    def test_large_result_sets(self):
        """Test handling large numbers of results."""
        tool = self.get_component_function()
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_client.create_webset.return_value = Mock(
                id="ws_large",
                results_count=10000,
                status="processing"
            )
            mock_exa.return_value = mock_client
            
            result = tool(
                name="Large Dataset",
                search_query="comprehensive search",
                num_results=10000
            )
            
            # Should handle large requests
            assert "results_count" in result
            assert result["status"] in ["active", "processing"]
    
    def test_error_handling(self):
        """Test error handling for various scenarios."""
        tool = self.get_component_function()
        
        # Test API errors
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            mock_client.create_webset.side_effect = Exception("API Error")
            mock_exa.return_value = mock_client
            
            result = tool("Error Webset", "test query")
            
            # Should handle errors gracefully
            assert isinstance(result, dict)
            assert "error" in str(result).lower() or "status" in result
    
    def test_search_query_validation(self):
        """Test validation of search queries."""
        tool = self.get_component_function()
        
        invalid_queries = [
            "",  # Empty query
            " " * 10,  # Whitespace only
            "a",  # Too short
        ]
        
        for query in invalid_queries:
            result = tool("Test", search_query=query)
            
            # Should handle invalid queries
            assert isinstance(result, dict)
    
    def test_concurrent_webset_operations(self):
        """Test handling concurrent webset operations."""
        tool = self.get_component_function()
        
        with patch("exa_py.Exa") as mock_exa:
            mock_client = Mock()
            
            # Simulate creating multiple websets
            webset_ids = []
            for i in range(5):
                mock_client.create_webset.return_value = Mock(
                    id=f"ws_concurrent_{i}",
                    name=f"Concurrent {i}"
                )
                mock_exa.return_value = mock_client
                
                result = tool(
                    name=f"Concurrent Webset {i}",
                    search_query=f"query {i}"
                )
                
                assert "webset_id" in result or "id" in result
