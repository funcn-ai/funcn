"""Test suite for exa_websets_tool following best practices."""

import asyncio
import pytest
from datetime import datetime

# Import the actual tool functions and models
from packages.sygaldry_registry.components.tools.exa_websets.tool import (
    CreateWebsetArgs,
    WebsetEnrichmentConfig,
    WebsetItem,
    WebsetItemsResponse,
    WebsetResponse,
    WebsetSearchConfig,
    WebsetSearchCriteria,
    WebsetSearchProgress,
    exa_create_webset,
    exa_delete_webset,
    exa_get_webset,
    exa_list_webset_items,
    exa_wait_until_idle,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch


class TestExaWebsetsTool(BaseToolTest):
    """Test exa_websets_tool component."""

    component_name = "exa_websets_tool"
    component_path = Path("packages/sygaldry_registry/components/tools/exa_websets")

    def get_component_function(self):
        """Import the tool function."""
        return exa_create_webset

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            CreateWebsetArgs(
                search=WebsetSearchConfig(
                    query="machine learning research papers 2024",
                    count=50,
                    entity={"type": "research_paper"},
                    criteria=[{"description": "Published in 2024", "successRate": 0.8}],
                    metadata={"category": "AI research"}
                ),
                enrichments=[
                    WebsetEnrichmentConfig(
                        description="Extract paper summary",
                        format="text",
                        options=[{"max_length": 500}],
                        instructions="Summarize the key findings",
                        metadata={"type": "summary"}
                    )
                ],
                metadata={"created_by": "test_suite"}
            ),
            CreateWebsetArgs(
                search=WebsetSearchConfig(
                    query="technology news artificial intelligence",
                    count=100,
                    metadata={"update_frequency": "hourly"}
                )
            ),
            CreateWebsetArgs(
                search=WebsetSearchConfig(
                    query="startup funding series A",
                    count=25,
                    criteria=[{"description": "Recent funding rounds", "successRate": 0.9}]
                ),
                enrichments=[
                    WebsetEnrichmentConfig(
                        description="Extract company info",
                        format="json"
                    ),
                    WebsetEnrichmentConfig(
                        description="Extract funding amount",
                        format="number"
                    )
                ]
            )
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        # This is an async tool, validation happens in async tests
        pass

    @pytest.mark.asyncio
    async def test_create_webset_basic(self):
        """Test creating a basic webset."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                # Mock the create method
                mock_result = Mock(
                    id="ws_12345",
                    status="active",
                    searches=[{"query": "test"}],
                    enrichments=[],
                    metadata={"test": True},
                    created_at="2024-01-01T00:00:00Z",
                    items=[]
                )
                mock_exa.return_value.websets.create.return_value = mock_result

                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(
                        query="test query",
                        count=10
                    )
                )

                result = await exa_create_webset(args)

                assert result.id == "ws_12345"
                assert result.status == "active"
                assert result.searches == [{"query": "test"}]
                assert result.created_at == "2024-01-01T00:00:00Z"
                assert result.items_count == 0

    @pytest.mark.asyncio
    async def test_create_webset_with_enrichments(self):
        """Test creating webset with enrichments."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    id="ws_enriched",
                    status="active",
                    searches=[],
                    enrichments=[
                        {"description": "Summary extraction"},
                        {"description": "Entity recognition"}
                    ],
                    metadata={},
                    created_at="2024-01-01T00:00:00Z",
                    items=None  # Explicitly set items to None
                )
                mock_exa.return_value.websets.create.return_value = mock_result

                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(
                        query="AI research",
                        count=20
                    ),
                    enrichments=[
                        WebsetEnrichmentConfig(
                            description="Summary extraction",
                            format="text"
                        ),
                        WebsetEnrichmentConfig(
                            description="Entity recognition",
                            format="json"
                        )
                    ]
                )

                result = await exa_create_webset(args)

                assert result.id == "ws_enriched"
                assert len(result.enrichments) == 2
                assert result.enrichments[0]["description"] == "Summary extraction"

    @pytest.mark.asyncio
    async def test_create_webset_with_criteria(self):
        """Test creating webset with search criteria."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    id="ws_criteria",
                    status="active",
                    searches=[{"criteria": [{"description": "High quality", "successRate": 0.9}]}],
                    enrichments=[],
                    metadata={},
                    created_at="2024-01-01T00:00:00Z",
                    items=None  # Explicitly set items to None
                )
                mock_exa.return_value.websets.create.return_value = mock_result

                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(
                        query="technical documentation",
                        count=30,
                        criteria=[{"description": "High quality", "successRate": 0.9}]
                    )
                )

                result = await exa_create_webset(args)

                assert result.id == "ws_criteria"
                assert result.searches[0]["criteria"][0]["description"] == "High quality"

    @pytest.mark.asyncio
    async def test_create_webset_no_api_key(self):
        """Test creating webset without API key."""
        with patch.dict('os.environ', {}, clear=True):
            args = CreateWebsetArgs(
                search=WebsetSearchConfig(
                    query="test",
                    count=10
                )
            )

            result = await exa_create_webset(args)

            assert result.id == "error"
            assert result.status == "error"
            assert "EXA_API_KEY" in result.metadata["error"]

    @pytest.mark.asyncio
    async def test_create_webset_api_error(self):
        """Test handling API errors during creation."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_exa.return_value.websets.create.side_effect = Exception("API Error")

                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(
                        query="test",
                        count=10
                    )
                )

                result = await exa_create_webset(args)

                assert result.id == "error"
                assert result.status == "error"
                assert "API Error" in result.metadata["error"]

    @pytest.mark.asyncio
    async def test_get_webset(self):
        """Test getting webset information."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    id="ws_12345",
                    status="idle",
                    searches=[{"query": "test"}],
                    enrichments=[],
                    metadata={"total_items": 25},
                    created_at="2024-01-01T00:00:00Z",
                    items=[Mock(), Mock(), Mock()]  # 3 items
                )
                mock_exa.return_value.websets.get.return_value = mock_result

                result = await exa_get_webset("ws_12345")

                assert result.id == "ws_12345"
                assert result.status == "idle"
                assert result.items_count == 3
                assert result.metadata["total_items"] == 25

    @pytest.mark.asyncio
    async def test_get_webset_not_found(self):
        """Test getting non-existent webset."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_exa.return_value.websets.get.side_effect = Exception("Webset not found")

                result = await exa_get_webset("ws_nonexistent")

                assert result.id == "ws_nonexistent"
                assert result.status == "error"
                assert "Webset not found" in result.metadata["error"]

    @pytest.mark.asyncio
    async def test_list_webset_items(self):
        """Test listing items in a webset."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                # Mock items with proper properties
                # Create custom mock objects to avoid recursion
                class MockProperties:
                    def __init__(self, url):
                        self.url = url
                        self.__dict__ = {"url": url}

                mock_item1 = Mock(
                    id="item_1",
                    properties=MockProperties("https://example1.com"),
                    evaluations=[{"score": 0.9}],
                    enrichments=[{"summary": "Test summary 1"}],
                    created_at="2024-01-01T00:00:00Z"
                )
                mock_item2 = Mock(
                    id="item_2",
                    properties=MockProperties("https://example2.com"),
                    evaluations=[{"score": 0.8}],
                    enrichments=[{"summary": "Test summary 2"}],
                    created_at="2024-01-01T00:01:00Z"
                )

                mock_result = Mock(
                    data=[mock_item1, mock_item2],
                    has_more=True
                )
                mock_exa.return_value.websets.items.list.return_value = mock_result

                result = await exa_list_webset_items("ws_12345", limit=10)

                assert len(result.items) == 2
                assert result.items[0].id == "item_1"
                assert result.items[0].url == "https://example1.com"
                assert result.items[0].evaluations[0]["score"] == 0.9
                assert result.items[1].id == "item_2"
                assert result.has_more is True
                assert result.total_count == 2

    @pytest.mark.asyncio
    async def test_list_webset_items_empty(self):
        """Test listing items in empty webset."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    data=[],
                    has_more=False
                )
                mock_exa.return_value.websets.items.list.return_value = mock_result

                result = await exa_list_webset_items("ws_empty")

                assert len(result.items) == 0
                assert result.has_more is False
                assert result.total_count == 0

    @pytest.mark.asyncio
    async def test_list_webset_items_with_limit(self):
        """Test limiting number of items returned."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                # Create 10 mock items
                class MockProperties:
                    def __init__(self, url):
                        self.url = url
                        self.__dict__ = {"url": url}

                mock_items = []
                for i in range(10):
                    mock_items.append(Mock(
                        id=f"item_{i}",
                        properties=MockProperties(f"https://example{i}.com"),
                        evaluations=[],
                        enrichments=[],
                        created_at=f"2024-01-01T00:0{i}:00Z"
                    ))

                mock_result = Mock(
                    data=mock_items,
                    has_more=True
                )
                mock_exa.return_value.websets.items.list.return_value = mock_result

                result = await exa_list_webset_items("ws_12345", limit=5)

                assert len(result.items) == 5  # Limited to 5
                assert result.items[0].id == "item_0"
                assert result.items[4].id == "item_4"

    @pytest.mark.asyncio
    async def test_delete_webset(self):
        """Test deleting a webset."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    id="ws_12345",
                    updated_at="2024-01-01T12:00:00Z"
                )
                mock_exa.return_value.websets.delete.return_value = mock_result

                result = await exa_delete_webset("ws_12345")

                assert result.id == "ws_12345"
                assert result.status == "deleted"
                assert result.metadata["deleted_at"] == "2024-01-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_delete_webset_not_found(self):
        """Test deleting non-existent webset."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_exa.return_value.websets.delete.side_effect = Exception("Webset not found")

                result = await exa_delete_webset("ws_nonexistent")

                assert result.id == "ws_nonexistent"
                assert result.status == "error"
                assert "Webset not found" in result.metadata["error"]

    @pytest.mark.asyncio
    async def test_wait_until_idle(self):
        """Test waiting for webset to become idle."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    id="ws_12345",
                    status="idle",
                    searches=[{"query": "test", "progress": {"found": 50, "completion": 1.0}}],
                    enrichments=[{"status": "completed"}],
                    metadata={"processing_time": 45},
                    created_at="2024-01-01T00:00:00Z",
                    items=[Mock() for _ in range(50)]  # 50 items
                )
                mock_exa.return_value.websets.wait_until_idle.return_value = mock_result

                result = await exa_wait_until_idle("ws_12345")

                assert result.id == "ws_12345"
                assert result.status == "idle"
                assert result.items_count == 50
                assert result.searches[0]["progress"]["completion"] == 1.0

    @pytest.mark.asyncio
    async def test_wait_until_idle_timeout(self):
        """Test timeout while waiting for webset."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_exa.return_value.websets.wait_until_idle.side_effect = Exception("Timeout waiting for webset")

                result = await exa_wait_until_idle("ws_12345", timeout=10)

                assert result.id == "ws_12345"
                assert result.status == "error"
                assert "Timeout" in result.metadata["error"]

    @pytest.mark.asyncio
    async def test_complex_webset_workflow(self):
        """Test complete webset workflow: create, wait, list items, delete."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                # Mock create
                mock_create_result = Mock(
                    id="ws_workflow",
                    status="processing",
                    searches=[],
                    enrichments=[],
                    metadata={},
                    created_at="2024-01-01T00:00:00Z",
                    items=None  # Explicitly set items to None
                )
                mock_exa.return_value.websets.create.return_value = mock_create_result

                # Create webset
                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(
                        query="workflow test",
                        count=5
                    )
                )
                create_result = await exa_create_webset(args)
                assert create_result.status == "processing"

                # Mock wait until idle
                mock_idle_result = Mock(
                    id="ws_workflow",
                    status="idle",
                    searches=[],
                    enrichments=[],
                    metadata={},
                    created_at="2024-01-01T00:00:00Z",
                    items=[Mock() for _ in range(5)]
                )
                mock_exa.return_value.websets.wait_until_idle.return_value = mock_idle_result

                # Wait for completion
                wait_result = await exa_wait_until_idle("ws_workflow")
                assert wait_result.status == "idle"
                assert wait_result.items_count == 5

                # Mock list items
                class MockProperties:
                    def __init__(self, url):
                        self.url = url
                        self.__dict__ = {"url": url}

                mock_items = []
                for i in range(5):
                    mock_items.append(Mock(
                        id=f"item_{i}",
                        properties=MockProperties(f"https://example{i}.com"),
                        evaluations=[],
                        enrichments=[],
                        created_at="2024-01-01T00:00:00Z"
                    ))
                mock_list_result = Mock(data=mock_items, has_more=False)
                mock_exa.return_value.websets.items.list.return_value = mock_list_result

                # List items
                items_result = await exa_list_webset_items("ws_workflow")
                assert len(items_result.items) == 5

                # Mock delete
                mock_delete_result = Mock(
                    id="ws_workflow",
                    updated_at="2024-01-01T01:00:00Z"
                )
                mock_exa.return_value.websets.delete.return_value = mock_delete_result

                # Delete webset
                delete_result = await exa_delete_webset("ws_workflow")
                assert delete_result.status == "deleted"

    @pytest.mark.asyncio
    async def test_webset_with_large_count(self):
        """Test creating webset with large item count."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    id="ws_large",
                    status="processing",
                    searches=[{"query": "large dataset", "count": 10000}],
                    enrichments=[],
                    metadata={"estimated_time": "2 hours"},
                    created_at="2024-01-01T00:00:00Z",
                    items=None  # Explicitly set items to None
                )
                mock_exa.return_value.websets.create.return_value = mock_result

                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(
                        query="large dataset",
                        count=10000
                    )
                )

                result = await exa_create_webset(args)

                assert result.id == "ws_large"
                assert result.status == "processing"
                assert result.searches[0]["count"] == 10000

    @pytest.mark.asyncio
    async def test_webset_with_multiple_enrichments(self):
        """Test webset with multiple enrichment types."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    id="ws_multi_enrich",
                    status="active",
                    searches=[],
                    enrichments=[
                        {"description": "Extract title", "format": "text"},
                        {"description": "Extract author", "format": "text"},
                        {"description": "Extract date", "format": "date"},
                        {"description": "Extract keywords", "format": "json"},
                        {"description": "Sentiment analysis", "format": "number"}
                    ],
                    metadata={},
                    created_at="2024-01-01T00:00:00Z",
                    items=None  # Explicitly set items to None
                )
                mock_exa.return_value.websets.create.return_value = mock_result

                enrichments = [
                    WebsetEnrichmentConfig(description="Extract title", format="text"),
                    WebsetEnrichmentConfig(description="Extract author", format="text"),
                    WebsetEnrichmentConfig(description="Extract date", format="date"),
                    WebsetEnrichmentConfig(description="Extract keywords", format="json"),
                    WebsetEnrichmentConfig(description="Sentiment analysis", format="number")
                ]

                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(query="research papers", count=100),
                    enrichments=enrichments
                )

                result = await exa_create_webset(args)

                assert len(result.enrichments) == 5
                assert any(e["format"] == "date" for e in result.enrichments)
                assert any(e["format"] == "json" for e in result.enrichments)
                assert any(e["format"] == "number" for e in result.enrichments)

    @pytest.mark.asyncio
    async def test_model_validation(self):
        """Test Pydantic model validation."""
        # Test WebsetSearchConfig validation - missing required fields
        with pytest.raises(Exception):  # ValidationError
            WebsetSearchConfig()  # Missing required fields

        # Test valid config
        config = WebsetSearchConfig(
            query="valid query",
            count=100,
            entity={"type": "article"},
            criteria=[{"description": "Recent", "successRate": 0.95}],
            metadata={"source": "test"}
        )
        assert config.query == "valid query"
        assert config.count == 100

        # Test WebsetEnrichmentConfig
        enrichment = WebsetEnrichmentConfig(
            description="Extract summary",
            format="text",
            options=[{"max_length": 200}],
            instructions="Focus on key points"
        )
        assert enrichment.description == "Extract summary"
        assert enrichment.format == "text"

        # Test CreateWebsetArgs
        args = CreateWebsetArgs(
            search=config,
            enrichments=[enrichment],
            metadata={"test": True}
        )
        assert args.search.query == "valid query"
        assert len(args.enrichments) == 1

        # Test empty query is allowed (no validation on empty string)
        empty_config = WebsetSearchConfig(query="", count=10)
        assert empty_config.query == ""

        # Test missing enrichment required fields
        with pytest.raises(Exception):  # ValidationError
            WebsetEnrichmentConfig()  # Missing required fields

    @pytest.mark.asyncio
    async def test_items_without_properties(self):
        """Test handling items without properties."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                # Mock item without properties
                mock_item = Mock(
                    id="item_no_props",
                    properties=None,
                    evaluations=[],
                    enrichments=[{"content": "Some content"}],
                    created_at="2024-01-01T00:00:00Z"
                )

                mock_result = Mock(
                    data=[mock_item],
                    has_more=False
                )
                mock_exa.return_value.websets.items.list.return_value = mock_result

                result = await exa_list_webset_items("ws_12345")

                assert len(result.items) == 1
                assert result.items[0].id == "item_no_props"
                assert result.items[0].url is None
                assert result.items[0].properties is None

    @pytest.mark.asyncio
    async def test_concurrent_webset_operations(self):
        """Test handling multiple concurrent webset operations."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                # Mock different results for different websets
                mock_results = {
                    "ws_1": Mock(id="ws_1", status="active", searches=[], enrichments=[], metadata={}, created_at="2024-01-01T00:00:00Z", items=None),
                    "ws_2": Mock(id="ws_2", status="idle", searches=[], enrichments=[], metadata={}, created_at="2024-01-01T00:00:00Z", items=None),
                    "ws_3": Mock(id="ws_3", status="processing", searches=[], enrichments=[], metadata={}, created_at="2024-01-01T00:00:00Z", items=None)
                }

                def get_side_effect(webset_id):
                    return mock_results.get(webset_id, Mock(id=webset_id, status="unknown"))

                mock_exa.return_value.websets.get.side_effect = get_side_effect

                # Run concurrent operations
                tasks = [
                    exa_get_webset("ws_1"),
                    exa_get_webset("ws_2"),
                    exa_get_webset("ws_3")
                ]

                results = await asyncio.gather(*tasks)

                assert results[0].status == "active"
                assert results[1].status == "idle"
                assert results[2].status == "processing"

    @pytest.mark.asyncio
    async def test_webset_metadata_handling(self):
        """Test proper handling of metadata at different levels."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                mock_result = Mock(
                    id="ws_metadata",
                    status="active",
                    searches=[{"metadata": {"search_meta": "value"}}],
                    enrichments=[{"metadata": {"enrich_meta": "value"}}],
                    metadata={"webset_meta": "value", "nested": {"key": "value"}},
                    created_at="2024-01-01T00:00:00Z",
                    items=None  # Explicitly set items to None
                )
                mock_exa.return_value.websets.create.return_value = mock_result

                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(
                        query="test",
                        count=10,
                        metadata={"search_level": "metadata"}
                    ),
                    enrichments=[
                        WebsetEnrichmentConfig(
                            description="Test",
                            format="text",
                            metadata={"enrichment_level": "metadata"}
                        )
                    ],
                    metadata={"top_level": "metadata"}
                )

                result = await exa_create_webset(args)

                assert result.metadata["webset_meta"] == "value"
                assert result.metadata["nested"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_error_handling_edge_cases(self):
        """Test various error handling edge cases."""
        with patch.dict('os.environ', {'EXA_API_KEY': 'test-key'}):
            with patch('packages.sygaldry_registry.components.tools.exa_websets.tool.Exa') as mock_exa:
                # Test network error
                mock_exa.return_value.websets.create.side_effect = ConnectionError("Network unreachable")

                args = CreateWebsetArgs(
                    search=WebsetSearchConfig(query="test", count=10)
                )

                result = await exa_create_webset(args)
                assert result.status == "error"
                assert "Network unreachable" in result.metadata["error"]

                # Test timeout error
                mock_exa.return_value.websets.get.side_effect = TimeoutError("Request timed out")

                result = await exa_get_webset("ws_timeout")
                assert result.status == "error"
                assert "Request timed out" in result.metadata["error"]

                # Test value error
                mock_exa.return_value.websets.delete.side_effect = ValueError("Invalid webset ID")

                result = await exa_delete_webset("invalid_id")
                assert result.status == "error"
                assert "Invalid webset ID" in result.metadata["error"]
