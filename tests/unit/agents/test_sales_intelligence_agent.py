"""Test suite for sales_intelligence_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, MagicMock, patch


class TestSalesIntelligenceAgent(BaseAgentTest):
    """Test cases for sales intelligence agent."""

    component_name = "sales_intelligence_agent"
    component_path = Path("packages/funcn_registry/components/agents/sales_intelligence")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.sales_intelligence_agent

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "role_or_company": "Head of Sales",
                "company_size": "50-200 employees",
                "location": "United States",
                "industry": "SaaS",
                "company_stage": "Series B",
                "additional_requirements": ["Must have engineering background"],
            },
            {
                "role_or_company": "Marketing agency",
                "company_size": "less than 50 employees",
                "location": "Europe",
                "industry": None,
                "company_stage": None,
                "additional_requirements": None,
            },
            {
                "role_or_company": "VP Engineering",
                "company_size": None,
                "location": "San Francisco Bay Area",
                "industry": "AI/ML",
                "company_stage": "Seed funding in 2024",
                "additional_requirements": ["Remote-first companies", "B2B focus"],
            },
        ]

    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist and have the expected fields
        assert hasattr(module, 'SalesTarget')
        assert hasattr(module, 'SalesIntelligenceResponse')

        # Test SalesTarget model
        SalesTarget = module.SalesTarget
        target = SalesTarget(
            role_title="Head of Sales",
            company_size="50-200 employees",
            location="United States",
            industry="SaaS",
            company_stage="Series B",
            additional_criteria=["Remote-first"],
        )
        assert target.role_title == "Head of Sales"
        assert target.company_size == "50-200 employees"
        assert target.location == "United States"
        assert target.industry == "SaaS"
        assert target.company_stage == "Series B"
        assert len(target.additional_criteria) == 1
        assert target.additional_criteria[0] == "Remote-first"

        # Test with None values
        target_minimal = SalesTarget()
        assert target_minimal.role_title is None
        assert target_minimal.company_size is None
        assert target_minimal.location is None
        assert target_minimal.industry is None
        assert target_minimal.company_stage is None
        assert target_minimal.additional_criteria == []

        # Test SalesIntelligenceResponse model
        SalesIntelligenceResponse = module.SalesIntelligenceResponse
        response = SalesIntelligenceResponse(
            webset_id="ws_123456",
            search_query="Head of Sales at Series B SaaS companies",
            entity_type="person",
            criteria=["Has sales leadership experience", "At Series B company"],
            enrichments=["LinkedIn profile", "Company information"],
            estimated_results=150,
            status="processing",
        )
        assert response.webset_id == "ws_123456"
        assert response.search_query == "Head of Sales at Series B SaaS companies"
        assert response.entity_type == "person"
        assert len(response.criteria) == 2
        assert len(response.enrichments) == 2
        assert response.estimated_results == 150
        assert response.status == "processing"

        # Test with minimal fields
        response_minimal = SalesIntelligenceResponse(
            webset_id="ws_789", search_query="Marketing agencies", entity_type="company", status="created"
        )
        assert response_minimal.webset_id == "ws_789"
        assert response_minimal.search_query == "Marketing agencies"
        assert response_minimal.entity_type == "company"
        assert response_minimal.criteria == []
        assert response_minimal.enrichments == []
        assert response_minimal.estimated_results is None
        assert response_minimal.status == "created"

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        # Main function
        assert hasattr(agent, 'sales_intelligence_agent')
        assert callable(agent.sales_intelligence_agent)

        # Convenience functions
        assert hasattr(agent, 'find_sales_leaders')
        assert callable(agent.find_sales_leaders)

        assert hasattr(agent, 'find_marketing_agencies')
        assert callable(agent.find_marketing_agencies)

        assert hasattr(agent, 'find_startup_executives')
        assert callable(agent.find_startup_executives)

    @pytest.mark.asyncio
    async def test_sales_intelligence_agent_structure(self):
        """Test basic structure of sales_intelligence_agent function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sales_intelligence_agent = module.sales_intelligence_agent

        # Test that function is callable (may be wrapped by @llm.call)
        import inspect

        assert callable(sales_intelligence_agent)

        # For @llm.call decorated functions, we need to check the wrapped function
        # The decorator may change the signature, so we'll just verify it's callable
        # and has the expected behavior through the convenience functions

    @pytest.mark.asyncio
    async def test_find_sales_leaders_convenience_function(self):
        """Test find_sales_leaders convenience function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Mock the main agent function after module is loaded
        mock_response = MagicMock()
        mock_response.webset_id = "ws_123"
        mock_response.search_query = "Head of Sales"
        mock_response.entity_type = "person"
        mock_response.status = "processing"

        original_agent = module.sales_intelligence_agent
        mock_agent = AsyncMock(return_value=mock_response)
        module.sales_intelligence_agent = mock_agent

        try:
            # Test the function
            result = await module.find_sales_leaders(company_size="50-200 employees", location="United States", industry="SaaS")

            # Verify the call was made with correct parameters
            mock_agent.assert_called_once_with(
                role_or_company="Head of Sales", company_size="50-200 employees", location="United States", industry="SaaS"
            )
        finally:
            # Restore original function
            module.sales_intelligence_agent = original_agent

    @pytest.mark.asyncio
    async def test_find_marketing_agencies_convenience_function(self):
        """Test find_marketing_agencies convenience function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Mock the main agent function after module is loaded
        mock_response = MagicMock()
        mock_response.webset_id = "ws_456"
        mock_response.search_query = "Marketing agency"
        mock_response.entity_type = "company"
        mock_response.status = "complete"

        original_agent = module.sales_intelligence_agent
        mock_agent = AsyncMock(return_value=mock_response)
        module.sales_intelligence_agent = mock_agent

        try:
            # Test with default max_employees
            result = await module.find_marketing_agencies(location="Europe")

            # Verify the call was made with correct parameters
            mock_agent.assert_called_once_with(
                role_or_company="Marketing agency", company_size="less than 50 employees", location="Europe"
            )

            # Test with custom max_employees
            mock_agent.reset_mock()
            result = await module.find_marketing_agencies(
                location="United States", max_employees=100, industry="Digital Marketing"
            )

            mock_agent.assert_called_once_with(
                role_or_company="Marketing agency",
                company_size="less than 100 employees",
                location="United States",
                industry="Digital Marketing",
            )
        finally:
            # Restore original function
            module.sales_intelligence_agent = original_agent

    @pytest.mark.asyncio
    async def test_find_startup_executives_convenience_function(self):
        """Test find_startup_executives convenience function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Mock the main agent function after module is loaded
        mock_response = MagicMock()
        mock_response.webset_id = "ws_789"
        mock_response.search_query = "VP Engineering"
        mock_response.entity_type = "person"
        mock_response.status = "processing"

        original_agent = module.sales_intelligence_agent
        mock_agent = AsyncMock(return_value=mock_response)
        module.sales_intelligence_agent = mock_agent

        try:
            # Test with default year
            result = await module.find_startup_executives(
                role="VP Engineering", funding_stage="Series A", location="San Francisco"
            )

            # Verify the call was made with correct parameters
            mock_agent.assert_called_once_with(
                role_or_company="VP Engineering",
                company_stage="Series A in 2024",
                additional_requirements=["Must have a VP Engineering position filled"],
                location="San Francisco",
            )

            # Test with custom year
            mock_agent.reset_mock()
            result = await module.find_startup_executives(role="CTO", funding_stage="Seed", year=2023)

            mock_agent.assert_called_once_with(
                role_or_company="CTO", company_stage="Seed in 2023", additional_requirements=["Must have a CTO position filled"]
            )
        finally:
            # Restore original function
            module.sales_intelligence_agent = original_agent

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SalesIntelligenceResponse = module.SalesIntelligenceResponse

        # Check that output is the correct type
        assert isinstance(output, SalesIntelligenceResponse)

        # Check required fields
        assert hasattr(output, "webset_id")
        assert hasattr(output, "search_query")
        assert hasattr(output, "entity_type")
        assert hasattr(output, "criteria")
        assert hasattr(output, "enrichments")
        assert hasattr(output, "estimated_results")
        assert hasattr(output, "status")

        # Validate field types
        assert isinstance(output.webset_id, str)
        assert isinstance(output.search_query, str)
        assert isinstance(output.entity_type, str)
        assert isinstance(output.criteria, list)
        assert isinstance(output.enrichments, list)
        assert output.estimated_results is None or isinstance(output.estimated_results, int)
        assert isinstance(output.status, str)

        # Validate entity type is appropriate
        if "Head of Sales" in input_data.get("role_or_company", "") or "VP" in input_data.get("role_or_company", ""):
            assert output.entity_type in ["person", "people"]
        elif (
            "agency" in input_data.get("role_or_company", "").lower()
            or "company" in input_data.get("role_or_company", "").lower()
        ):
            assert output.entity_type in ["company", "organization"]

        # Check that search query contains relevant information
        assert len(output.search_query) > 0

        # Validate status is reasonable
        assert output.status in ["created", "processing", "complete", "failed", "pending"]

    @pytest.mark.unit
    def test_tool_imports(self):
        """Test that the agent handles tool imports gracefully."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "sales_intelligence_agent", "packages/funcn_registry/components/agents/sales_intelligence/agent.py"
        )
        module = importlib.util.module_from_spec(spec)

        # Test with tools unavailable (import error scenario)
        with patch.dict('sys.modules', {'exa_websets_tools': None}):
            spec.loader.exec_module(module)

            # Verify fallback values are set
            assert module.create_webset is None
            assert module.get_webset_status is None
            assert module.list_webset_items is None
            assert module.WebsetSearchConfig is None
            assert module.WebsetEnrichment is None
            assert module.WebsetCriteria is None

            # Verify agent can still be imported
            assert hasattr(module, 'sales_intelligence_agent')
            assert hasattr(module, 'SalesIntelligenceResponse')
