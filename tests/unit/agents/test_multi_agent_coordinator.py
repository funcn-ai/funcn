"""Test suite for multi_agent_coordinator following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestMultiAgentCoordinator(BaseAgentTest):
    """Test cases for multi agent coordinator."""

    component_name = "multi_agent_coordinator"
    component_path = Path("packages/funcn_registry/components/agents/multi_agent_coordinator")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_agent_coordinator", "packages/funcn_registry/components/agents/multi_agent_coordinator/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.coordinate_task

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "task": "Analyze market trends and create a comprehensive report with financial projections",
                "available_agents": ["research", "analysis", "writing"],
                "coordination_strategy": "parallel",
                "max_iterations": 5,
                "quality_threshold": 0.8,
            },
            {
                "task": "Debug and optimize a Python application",
                "available_agents": ["code_review", "optimization", "testing"],
                "coordination_strategy": "sequential",
                "max_iterations": 3,
                "quality_threshold": 0.9,
            },
            {
                "task": "Plan a product launch campaign",
                "available_agents": ["marketing", "design", "copywriting", "analytics"],
                "coordination_strategy": "hierarchical",
                "max_iterations": 4,
                "quality_threshold": 0.85,
            },
        ]

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_agent_coordinator", "packages/funcn_registry/components/agents/multi_agent_coordinator/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Main functions mentioned in component.json
        assert hasattr(module, 'coordinate_task')
        assert callable(module.coordinate_task)
        assert hasattr(module, 'analyze_task')
        assert callable(module.analyze_task)
        assert hasattr(module, 'select_agents')
        assert callable(module.select_agents)
        assert hasattr(module, 'execute_agent_task')
        assert callable(module.execute_agent_task)
        assert hasattr(module, 'synthesize_results')
        assert callable(module.synthesize_results)
        assert hasattr(module, 'evaluate_quality')
        assert callable(module.evaluate_quality)

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_agent_coordinator", "packages/funcn_registry/components/agents/multi_agent_coordinator/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'TaskAnalysis')
        assert hasattr(module, 'AgentSelection')
        assert hasattr(module, 'AgentTaskResult')
        assert hasattr(module, 'CoordinationResult')
        assert hasattr(module, 'QualityEvaluation')

        # Test basic model instantiation
        TaskAnalysis = module.TaskAnalysis
        analysis = TaskAnalysis(
            task_type="research_and_report",
            complexity="high",
            required_capabilities=["research", "analysis", "writing"],
            subtasks=["gather data", "analyze trends", "write report"],
            estimated_time_minutes=120,
            priority_order=["research", "analysis", "writing"],
        )
        assert analysis.task_type == "research_and_report"
        assert analysis.complexity == "high"
        assert len(analysis.required_capabilities) == 3

        # Test AgentSelection model
        AgentSelection = module.AgentSelection
        selection = AgentSelection(
            selected_agents=["research_agent", "analysis_agent"],
            agent_roles={"research_agent": "data gathering", "analysis_agent": "trend analysis"},
            coordination_plan="Sequential execution with data handoff",
            rationale="Agents selected based on task requirements",
        )
        assert len(selection.selected_agents) == 2
        assert "research_agent" in selection.agent_roles

        # Test AgentTaskResult model
        AgentTaskResult = module.AgentTaskResult
        task_result = AgentTaskResult(
            agent_name="research_agent",
            subtask="gather market data",
            status="completed",
            result="Market data collected",
            confidence_score=0.9,
            execution_time_seconds=45.5,
            errors=[],
        )
        assert task_result.status == "completed"
        assert task_result.confidence_score == 0.9

    @pytest.mark.unit
    def test_coordinate_task_structure(self):
        """Test basic structure of coordinate_task function."""
        # Import the function
        func = self.get_component_function()

        # Test that function exists and is callable
        import inspect

        assert callable(func)
        assert inspect.iscoroutinefunction(func)

        # Test function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'task' in params
        assert 'available_agents' in params
        assert 'coordination_strategy' in params
        assert 'max_iterations' in params
        assert 'quality_threshold' in params
        assert 'llm_provider' in params
        assert 'model' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_agent_coordinator", "packages/funcn_registry/components/agents/multi_agent_coordinator/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        CoordinationResult = module.CoordinationResult

        # Coordinator should return a CoordinationResult
        assert isinstance(output, CoordinationResult)
        assert hasattr(output, "original_task")
        assert hasattr(output, "task_analysis")
        assert hasattr(output, "agents_used")
        assert hasattr(output, "execution_results")
        assert hasattr(output, "final_output")
        assert hasattr(output, "quality_score")
        assert hasattr(output, "total_execution_time")
        assert hasattr(output, "iterations_used")
        assert hasattr(output, "coordination_strategy")
        assert isinstance(output.execution_results, list)
        assert 0 <= output.quality_score <= 1
        assert output.iterations_used >= 1

    @pytest.mark.unit
    def test_helper_functions(self):
        """Test helper functions exist and have correct signatures."""
        # Use direct import to avoid __init__.py chain
        import importlib.util
        import inspect

        spec = importlib.util.spec_from_file_location(
            "multi_agent_coordinator", "packages/funcn_registry/components/agents/multi_agent_coordinator/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test analyze_task
        func = module.analyze_task
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'task' in params

        # Test select_agents
        func = module.select_agents
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'task_analysis' in params
        assert 'available_agents' in params

        # Test synthesize_results
        func = module.synthesize_results
        assert callable(func)
        assert inspect.iscoroutinefunction(func)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert 'task' in params
        assert 'results' in params

    @pytest.mark.unit
    def test_coordination_strategies(self):
        """Test that multiple coordination strategies are supported."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_agent_coordinator", "packages/funcn_registry/components/agents/multi_agent_coordinator/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for strategy support
        import inspect

        source = inspect.getsource(module)
        assert 'parallel' in source or 'sequential' in source or 'hierarchical' in source
        assert 'strategy' in source.lower()

        # Verify coordination logic
        assert 'coordinate' in source or 'orchestrate' in source

    @pytest.mark.unit
    def test_quality_evaluation(self):
        """Test that quality evaluation is implemented."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "multi_agent_coordinator", "packages/funcn_registry/components/agents/multi_agent_coordinator/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check for quality evaluation
        import inspect

        source = inspect.getsource(module)
        assert 'quality' in source.lower()
        assert 'evaluate' in source or 'score' in source or 'assess' in source
        assert 'threshold' in source
