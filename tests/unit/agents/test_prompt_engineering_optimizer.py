"""Test suite for prompt_engineering_optimizer following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestPromptEngineeringOptimizerAgent(BaseAgentTest):
    """Test cases for prompt engineering optimizer agent."""

    component_name = "prompt_engineering_optimizer"
    component_path = Path("packages/funcn_registry/components/agents/prompt_engineering_optimizer")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "prompt_engineering_optimizer", "packages/funcn_registry/components/agents/prompt_engineering_optimizer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.prompt_engineering_optimizer

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "original_prompt": "Summarize this text",
                "task_description": "Text summarization for news articles",
                "test_cases": ["Article 1 content", "Article 2 content"],
                "optimization_goal": "clarity_and_accuracy",
                "num_variants": 5,
            },
            {
                "original_prompt": "Extract key information from the document",
                "task_description": "Information extraction from business reports",
                "test_cases": ["Business report example"],
                "optimization_goal": "structured_output",
                "num_variants": 3,
            },
            {
                "original_prompt": "Answer the following question",
                "task_description": "Q&A system for technical documentation",
                "test_cases": ["How do I install Python?"],
                "optimization_goal": "accuracy",
                "num_variants": 4,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "prompt_engineering_optimizer", "packages/funcn_registry/components/agents/prompt_engineering_optimizer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions found in the agent
        assert hasattr(module, 'prompt_engineering_optimizer')
        assert callable(module.prompt_engineering_optimizer)
        assert hasattr(module, 'prompt_engineering_optimizer_stream')
        assert callable(module.prompt_engineering_optimizer_stream)
        assert hasattr(module, 'analyze_prompt_effectiveness')
        assert callable(module.analyze_prompt_effectiveness)
        assert hasattr(module, 'generate_prompt_variants')
        assert callable(module.generate_prompt_variants)
        assert hasattr(module, 'test_prompt_variant')
        assert callable(module.test_prompt_variant)
        assert hasattr(module, 'compare_variants_ab_test')
        assert callable(module.compare_variants_ab_test)
        assert hasattr(module, 'synthesize_optimization_results')
        assert callable(module.synthesize_optimization_results)
        assert hasattr(module, 'run_variant_tests')
        assert callable(module.run_variant_tests)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "prompt_engineering_optimizer", "packages/funcn_registry/components/agents/prompt_engineering_optimizer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'PromptAnalysis')
        assert hasattr(module, 'PromptVariant')
        assert hasattr(module, 'TestResult')
        assert hasattr(module, 'ABTestComparison')
        assert hasattr(module, 'OptimizedPromptResult')

        # Test basic model instantiation
        PromptAnalysis = module.PromptAnalysis
        analysis = PromptAnalysis(
            strengths=["Clear", "Concise"],
            weaknesses=["Too generic"],
            improvement_areas=["Add specificity"],
            clarity_score=0.8,
            specificity_score=0.6,
            effectiveness_score=0.7,
        )
        assert analysis.clarity_score == 0.8
        assert len(analysis.strengths) == 2

        # Test PromptVariant model
        PromptVariant = module.PromptVariant
        variant = PromptVariant(
            variant_id="v1",
            prompt_text="Enhanced prompt text",
            optimization_technique="few-shot",
            expected_improvement="Better accuracy",
        )
        assert variant.variant_id == "v1"
        assert variant.optimization_technique == "few-shot"

    @pytest.mark.unit
    def test_optimizer_structure(self):
        """Test basic structure of prompt_engineering_optimizer function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'original_prompt' in params
        assert 'task_description' in params
        assert 'test_cases' in params
        assert 'optimization_goal' in params
        assert 'num_variants' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "prompt_engineering_optimizer", "packages/funcn_registry/components/agents/prompt_engineering_optimizer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        OptimizedPromptResult = module.OptimizedPromptResult

        # Optimizer should return an OptimizedPromptResult
        assert isinstance(output, OptimizedPromptResult)
        assert hasattr(output, "original_prompt")
        assert hasattr(output, "best_variant")
        assert hasattr(output, "all_variants")
        assert hasattr(output, "performance_comparison")
        assert hasattr(output, "optimization_insights")
        assert hasattr(output, "implementation_guide")
        assert isinstance(output.all_variants, list)

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "prompt_engineering_optimizer", "packages/funcn_registry/components/agents/prompt_engineering_optimizer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test analyze_prompt_effectiveness - not async
        func = module.analyze_prompt_effectiveness
        assert callable(func)
        assert not inspect.iscoroutinefunction(func)

        # Test generate_prompt_variants - not async
        func = module.generate_prompt_variants
        assert callable(func)
        assert not inspect.iscoroutinefunction(func)

        # Test run_variant_tests - async
        func = module.run_variant_tests
        assert callable(func)
        assert inspect.iscoroutinefunction(func)

    @pytest.mark.unit
    def test_optimization_techniques(self):
        """Test that various optimization techniques are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "prompt_engineering_optimizer", "packages/funcn_registry/components/agents/prompt_engineering_optimizer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for optimization techniques
        import inspect

        source = inspect.getsource(module)
        assert 'few-shot' in source or 'few_shot' in source
        assert 'chain-of-thought' in source or 'chain_of_thought' in source
        assert 'instruction' in source.lower()
        assert 'variant' in source

    @pytest.mark.unit
    def test_ab_testing_support(self):
        """Test that A/B testing is supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "prompt_engineering_optimizer", "packages/funcn_registry/components/agents/prompt_engineering_optimizer/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for A/B testing features
        import inspect

        source = inspect.getsource(module)
        assert 'ab_test' in source.lower() or 'a/b' in source.lower()
        assert 'compare' in source
        assert 'performance' in source
