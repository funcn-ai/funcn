"""Test suite for dataset_builder_agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestDatasetBuilderAgent(BaseAgentTest):
    """Test cases for dataset builder agent."""

    component_name = "dataset_builder_agent"
    component_path = Path("packages/funcn_registry/components/agents/dataset_builder")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.build_dataset

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "topic": "AI startups",
                "entity_type": "company",
                "search_queries": ["AI companies", "artificial intelligence startups"],
                "criteria": ["Founded after 2020", "Has funding", "Active operations"],
                "enrichments": ["company_description", "funding_amount", "employee_count"],
                "target_count": 50,
                "wait_for_completion": False,
            },
            {
                "topic": "renewable energy",
                "entity_type": "research",
                "target_count": 100,
                "wait_for_completion": False,
                "max_wait_minutes": 10,
            },
            {
                "topic": "social media influencers",
                "entity_type": "person",
                "criteria": ["Over 10k followers", "Active in tech"],
                "target_count": 25,
                "wait_for_completion": False,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main function
        assert hasattr(module, 'build_dataset')
        assert callable(module.build_dataset)

        # Specialized dataset builders
        assert hasattr(module, 'build_company_dataset')
        assert callable(module.build_company_dataset)
        assert hasattr(module, 'build_research_dataset')
        assert callable(module.build_research_dataset)
        assert hasattr(module, 'build_market_dataset')
        assert callable(module.build_market_dataset)
        assert hasattr(module, 'build_competitor_dataset')
        assert callable(module.build_competitor_dataset)
        assert hasattr(module, 'build_influencer_dataset')
        assert callable(module.build_influencer_dataset)
        assert hasattr(module, 'build_news_trends_dataset')
        assert callable(module.build_news_trends_dataset)
        assert hasattr(module, 'build_investment_dataset')
        assert callable(module.build_investment_dataset)
        assert hasattr(module, 'build_talent_dataset')
        assert callable(module.build_talent_dataset)
        assert hasattr(module, 'build_product_launch_dataset')
        assert callable(module.build_product_launch_dataset)
        assert hasattr(module, 'build_location_dataset')
        assert callable(module.build_location_dataset)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'DatasetRequirements')
        assert hasattr(module, 'DatasetPlan')
        assert hasattr(module, 'DatasetStatus')
        assert hasattr(module, 'DatasetAnalysis')
        assert hasattr(module, 'DatasetBuilderResponse')

        # Test basic model instantiation
        # Test DatasetRequirements
        DatasetRequirements = module.DatasetRequirements
        requirements = DatasetRequirements(
            topic="AI startups",
            entity_type="company",
            search_queries=["AI companies"],
            criteria=["Has funding"],
            enrichments=["company_description"],
            target_count=50,
        )
        assert requirements.topic == "AI startups"
        assert requirements.entity_type == "company"
        assert len(requirements.search_queries) == 1
        assert requirements.target_count == 50

        # Test DatasetStatus
        DatasetStatus = module.DatasetStatus
        status = DatasetStatus(
            webset_id="test-123",
            status="running",
            items_found=25,
            items_enriched=20,
            progress_percentage=50.0,
            estimated_completion="2024-01-01T12:00:00",
        )
        assert status.webset_id == "test-123"
        assert status.status == "running"
        assert status.items_found == 25
        assert status.progress_percentage == 50.0

        # Test DatasetAnalysis
        DatasetAnalysis = module.DatasetAnalysis
        analysis = DatasetAnalysis(
            total_items=100,
            data_quality_score=0.85,
            key_insights=["Most companies are in Silicon Valley", "Average funding is $5M"],
            data_distribution={"california": 60, "new_york": 30, "other": 10},
            recommendations=["Use for market analysis", "Cross-reference with industry reports"],
        )
        assert analysis.total_items == 100
        assert analysis.data_quality_score == 0.85
        assert len(analysis.key_insights) == 2
        assert analysis.data_distribution["california"] == 60

        # Test DatasetBuilderResponse with forward references
        # Note: We test the structure without full instantiation due to forward references
        DatasetBuilderResponse = module.DatasetBuilderResponse
        # Check the class exists and has expected annotations
        assert hasattr(DatasetBuilderResponse, '__annotations__')
        annotations = DatasetBuilderResponse.__annotations__
        assert 'webset_id' in annotations
        assert 'name' in annotations
        assert 'status' in annotations
        assert 'export_url' in annotations
        assert 'analysis' in annotations

    @pytest.mark.unit
    def test_build_dataset_structure(self):
        """Test basic structure of build_dataset function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'topic' in params
        assert 'entity_type' in params
        assert 'search_queries' in params
        assert 'criteria' in params
        assert 'enrichments' in params
        assert 'target_count' in params
        assert 'wait_for_completion' in params
        assert 'max_wait_minutes' in params
        assert 'llm_provider' in params
        assert 'model' in params

        # Check default values
        defaults = {k: v.default for k, v in sig.parameters.items() if v.default is not inspect.Parameter.empty}
        assert defaults.get('entity_type') == "general"
        assert defaults.get('target_count') == 50
        assert defaults.get('wait_for_completion') is True
        assert defaults.get('max_wait_minutes') == 30
        assert defaults.get('llm_provider') == "openai"
        assert defaults.get('model') == "gpt-4o-mini"

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        DatasetBuilderResponse = module.DatasetBuilderResponse

        # Dataset builder should return a DatasetBuilderResponse
        assert isinstance(output, DatasetBuilderResponse)
        assert hasattr(output, "webset_id")
        assert hasattr(output, "name")
        assert hasattr(output, "status")
        assert hasattr(output, "export_url")
        assert hasattr(output, "analysis")

        # Validate status is a DatasetStatus
        assert hasattr(output.status, "webset_id")
        assert hasattr(output.status, "status")
        assert hasattr(output.status, "items_found")
        assert hasattr(output.status, "progress_percentage")

    @pytest.mark.unit
    def test_specialized_dataset_functions(self):
        """Test specialized dataset builder functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test build_company_dataset
        func = module.build_company_dataset
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'industry' in params
        assert 'criteria' in params

        # Test build_research_dataset
        func = module.build_research_dataset
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'research_topic' in params
        assert 'time_range' in params

        # Test build_influencer_dataset
        func = module.build_influencer_dataset
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'niche' in params
        assert 'platforms' in params
        assert 'min_followers' in params

        # Test build_competitor_dataset
        func = module.build_competitor_dataset
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'company_name' in params
        assert 'industry' in params
        assert 'aspects' in params

    @pytest.mark.unit
    def test_exa_websets_integration(self):
        """Test that the agent properly integrates with exa_websets tool."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check that the exa_websets imports are attempted
        import inspect

        source = inspect.getsource(module)
        assert 'from exa_websets_tools' in source or 'import exa_websets_tools' in source
        assert 'create_webset' in source
        assert 'get_webset' in source
        assert 'list_webset_items' in source
        assert 'export_webset' in source

        # Verify the imports are used in try/except for graceful fallback
        assert 'try:' in source
        assert 'except ImportError:' in source

    @pytest.mark.unit
    def test_llm_decorated_functions(self):
        """Test that LLM-decorated functions exist."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for LLM-decorated functions
        assert hasattr(module, 'create_dataset_plan')
        assert callable(module.create_dataset_plan)
        assert hasattr(module, 'execute_dataset_plan')
        assert callable(module.execute_dataset_plan)
        assert hasattr(module, 'monitor_dataset_progress')
        assert callable(module.monitor_dataset_progress)
        assert hasattr(module, 'analyze_dataset')
        assert callable(module.analyze_dataset)

        # Check that these functions are decorated with @llm.call and @prompt_template
        import inspect

        # These functions should have the mirascope decorators applied
        # We can check for the presence of decorators in the source
        source = inspect.getsource(module)
        assert '@llm.call' in source
        assert '@prompt_template' in source

        # Verify the functions are defined as async
        for func_name in ['create_dataset_plan', 'execute_dataset_plan', 'monitor_dataset_progress', 'analyze_dataset']:
            func_source = inspect.getsource(getattr(module, func_name))
            assert 'async def' in func_source or 'await' in func_source

    @pytest.mark.unit
    def test_entity_type_literal(self):
        """Test that entity_type uses proper Literal typing."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check build_dataset function signature
        sig = inspect.signature(module.build_dataset)
        entity_type_param = sig.parameters['entity_type']

        # The annotation should include Literal types
        annotation_str = str(entity_type_param.annotation)
        assert 'Literal' in annotation_str
        assert 'company' in annotation_str
        assert 'person' in annotation_str
        assert 'article' in annotation_str
        assert 'research' in annotation_str
        assert 'product' in annotation_str
        assert 'general' in annotation_str

    @pytest.mark.unit
    def test_dataset_plan_model_structure(self):
        """Test DatasetPlan model has proper field structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dataset_builder_agent", "packages/funcn_registry/components/agents/dataset_builder/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        DatasetPlan = module.DatasetPlan

        # Check that DatasetPlan has the expected annotations
        # Due to forward references with dict[str, Any], we check structure without instantiation
        assert hasattr(DatasetPlan, '__annotations__')
        annotations = DatasetPlan.__annotations__

        # Verify all expected fields are present
        expected_fields = [
            'name',
            'description',
            'search_config',
            'entity_config',
            'criteria_config',
            'enrichment_config',
            'metadata',
        ]
        for field in expected_fields:
            assert field in annotations, f"Field '{field}' not found in DatasetPlan annotations"

        # Verify the model has Field descriptors
        assert hasattr(DatasetPlan, 'model_fields')
        model_fields = DatasetPlan.model_fields

        # Check that fields have descriptions
        assert model_fields['name'].description == "Name for the webset"
        assert model_fields['description'].description == "Description of what this dataset contains"
        assert model_fields['search_config'].description == "Search configuration for the webset"
        assert model_fields['entity_config'].description == "Entity type configuration"
        assert model_fields['criteria_config'].description == "Criteria for verification"
        assert model_fields['enrichment_config'].description == "Enrichments to apply"
        assert model_fields['metadata'].description == "Metadata for tracking"
