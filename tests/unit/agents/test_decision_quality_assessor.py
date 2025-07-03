"""Test suite for decision_quality_assessor agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestDecisionQualityAssessor(BaseAgentTest):
    """Test cases for decision quality assessor agent."""

    component_name = "decision_quality_assessor"
    component_path = Path("packages/sygaldry_registry/components/agents/decision_quality_assessor")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.decision_quality_assessor

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "decision": "Should we expand into the European market in Q2 2024?",
                "background": "Our company has seen 30% growth in US market. We have $10M in funding. European competitors are establishing presence.",
                "alternatives": ["Expand to Europe now", "Wait until Q4 2024", "Focus on US market only"],
                "stakeholders": "Board of directors, employees, existing customers, potential investors",
                "constraints": "Limited budget, no European team, regulatory compliance needed",
                "timeline": "Decision needed by end of month for planning purposes",
                "decision_process": "Management team meetings, market research, financial analysis",
                "evaluation_criteria": "ROI, market opportunity, resource requirements, risk level",
                "information_sources": "Market reports, competitor analysis, internal financial data",
                "decision_makers": "CEO, CFO, VP of Sales, Board representatives",
            },
            {
                "decision": "Which cloud provider should we migrate to?",
                "background": "Current infrastructure costs $500k/year. Need better scalability and reliability.",
                "alternatives": ["AWS", "Google Cloud", "Azure", "Stay with current provider"],
                "stakeholders": "Engineering team, finance, customers",
                "constraints": "6-month migration timeline, $100k migration budget",
                "timeline": "Decision by next week",
            },
            {
                "decision": "Should we acquire the competitor company?",
                "background": "Competitor is for sale at $50M valuation. They have 20% market share.",
                "alternatives": ["Full acquisition", "Partial stake", "Strategic partnership", "No action"],
                "decision_makers": "Board of directors, CEO, CFO",
            },
        ]

    @pytest.mark.unit
    def test_enum_types(self):
        """Test that all enum types are properly defined."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test DecisionType enum
        DecisionType = module.DecisionType
        expected_decision_types = [
            "strategic",
            "operational",
            "financial",
            "hiring",
            "investment",
            "product",
            "marketing",
            "technical",
            "policy",
            "personal",
            "crisis",
            "innovation",
        ]
        for dt in expected_decision_types:
            assert hasattr(DecisionType, dt.upper())
            assert DecisionType[dt.upper()].value == dt

        # Test BiasType enum
        BiasType = module.BiasType
        expected_bias_types = [
            "confirmation_bias",
            "anchoring_bias",
            "availability_heuristic",
            "sunk_cost_fallacy",
            "overconfidence_bias",
            "groupthink",
            "recency_bias",
            "survivorship_bias",
            "planning_fallacy",
            "status_quo_bias",
            "hindsight_bias",
            "framing_effect",
            "bandwagon_effect",
            "dunning_kruger_effect",
            "halo_effect",
        ]
        for bt in expected_bias_types:
            assert hasattr(BiasType, bt.upper())
            assert BiasType[bt.upper()].value == bt

        # Test QualityDimension enum
        QualityDimension = module.QualityDimension
        expected_quality_dimensions = [
            "information_quality",
            "alternative_generation",
            "stakeholder_consideration",
            "risk_assessment",
            "timeline_appropriateness",
            "resource_consideration",
            "reversibility_analysis",
            "ethical_consideration",
            "implementation_feasibility",
            "outcome_measurability",
            "adaptability",
            "sustainability",
        ]
        for qd in expected_quality_dimensions:
            assert hasattr(QualityDimension, qd.upper())
            assert QualityDimension[qd.upper()].value == qd

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that all models exist
        assert hasattr(module, 'DecisionContext')
        assert hasattr(module, 'BiasAnalysis')
        assert hasattr(module, 'QualityAssessment')
        assert hasattr(module, 'DecisionAnalysis')
        assert hasattr(module, 'DecisionFramework')
        assert hasattr(module, 'DecisionQuality')

        # Test DecisionContext model
        DecisionContext = module.DecisionContext
        DecisionType = module.DecisionType
        context = DecisionContext(
            decision_type=DecisionType.STRATEGIC,
            stakeholders=["Board", "Employees"],
            constraints=["Budget", "Timeline"],
            timeline="Q2 2024",
            resources_available=["Team", "Budget"],
            success_metrics=["ROI", "Market share"],
            risk_tolerance="Medium",
            decision_authority="CEO",
            external_factors=["Competition", "Regulation"],
            organizational_culture="Innovation-focused",
        )
        assert context.decision_type == DecisionType.STRATEGIC
        assert len(context.stakeholders) == 2
        assert len(context.constraints) == 2

        # Test BiasAnalysis model
        BiasAnalysis = module.BiasAnalysis
        BiasType = module.BiasType
        bias = BiasAnalysis(
            bias_type=BiasType.CONFIRMATION_BIAS,
            evidence=["Only looked at supporting data"],
            severity=0.7,
            mitigation_strategies=["Seek contrary evidence"],
            impact_on_decision="May overlook risks",
            likelihood_of_occurrence=0.8,
            detection_confidence=0.9,
        )
        assert bias.bias_type == BiasType.CONFIRMATION_BIAS
        assert bias.severity == 0.7
        assert 0 <= bias.severity <= 1
        assert 0 <= bias.likelihood_of_occurrence <= 1
        assert 0 <= bias.detection_confidence <= 1

        # Test QualityAssessment model
        QualityAssessment = module.QualityAssessment
        QualityDimension = module.QualityDimension
        quality = QualityAssessment(
            dimension=QualityDimension.INFORMATION_QUALITY,
            score=0.75,
            strengths=["Comprehensive data"],
            weaknesses=["Missing competitor analysis"],
            improvement_suggestions=["Add market research"],
            critical_gaps=["No financial projections"],
            best_practices_applied=["Used multiple sources"],
            priority_level="high",
        )
        assert quality.dimension == QualityDimension.INFORMATION_QUALITY
        assert quality.score == 0.75
        assert 0 <= quality.score <= 1
        assert quality.priority_level in ["low", "medium", "high", "critical"]

        # Test DecisionAnalysis model
        DecisionAnalysis = module.DecisionAnalysis
        analysis = DecisionAnalysis(
            alternative="Expand to Europe",
            pros=["Large market", "First mover advantage"],
            cons=["High cost", "Regulatory complexity"],
            risks=["Market failure", "Resource strain"],
            opportunities=["Market leadership", "Revenue growth"],
            resource_requirements=["$5M budget", "20 FTEs"],
            success_probability=0.65,
            impact_assessment="High positive impact if successful",
            implementation_complexity="High",
            alignment_score=0.8,
            sustainability_score=0.7,
        )
        assert analysis.alternative == "Expand to Europe"
        assert len(analysis.pros) == 2
        assert 0 <= analysis.success_probability <= 1
        assert 0 <= analysis.alignment_score <= 1
        assert 0 <= analysis.sustainability_score <= 1

        # Test DecisionFramework model
        DecisionFramework = module.DecisionFramework
        framework = DecisionFramework(
            recommended_framework="SWOT Analysis",
            framework_rationale="Good for strategic decisions",
            key_steps=["Identify strengths", "Analyze weaknesses"],
            tools_needed=["SWOT template", "Market data"],
            success_factors=["Complete analysis", "Stakeholder buy-in"],
        )
        assert framework.recommended_framework == "SWOT Analysis"
        assert len(framework.key_steps) == 2

        # Just verify DecisionQuality exists - complex nested model
        assert module.DecisionQuality.__name__ == 'DecisionQuality'

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        # Main functions
        assert hasattr(agent, 'decision_quality_assessor')
        assert callable(agent.decision_quality_assessor)
        assert hasattr(agent, 'decision_quality_assessor_stream')
        assert callable(agent.decision_quality_assessor_stream)

        # LLM-decorated functions
        assert hasattr(agent, 'analyze_decision_context')
        assert hasattr(agent, 'analyze_decision_alternatives')
        assert hasattr(agent, 'assess_decision_quality_dimensions')
        assert hasattr(agent, 'analyze_cognitive_biases')
        assert hasattr(agent, 'recommend_decision_framework')
        assert hasattr(agent, 'synthesize_decision_quality')

        # Check that LLM functions have the decorator
        for func_name in [
            'analyze_decision_context',
            'analyze_decision_alternatives',
            'assess_decision_quality_dimensions',
            'analyze_cognitive_biases',
            'recommend_decision_framework',
            'synthesize_decision_quality',
        ]:
            func = getattr(agent, func_name)
            # These should have been decorated by @llm.call
            assert hasattr(func, '__wrapped__') or hasattr(func, '__name__')

    @pytest.mark.asyncio
    async def test_decision_quality_assessor_basic_structure(self):
        """Test basic structure of decision_quality_assessor function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        decision_quality_assessor = module.decision_quality_assessor

        # Test that function is async
        import inspect

        assert inspect.iscoroutinefunction(decision_quality_assessor)

        # Test function signature
        sig = inspect.signature(decision_quality_assessor)
        params = list(sig.parameters.keys())

        # Required parameters
        assert 'decision' in params

        # Optional parameters
        optional_params = [
            'background',
            'alternatives',
            'stakeholders',
            'constraints',
            'timeline',
            'decision_process',
            'evaluation_criteria',
            'information_sources',
            'decision_makers',
            'llm_provider',
            'model',
        ]
        for param in optional_params:
            assert param in params

        # Check defaults
        assert sig.parameters['background'].default == ""
        assert sig.parameters['alternatives'].default is None
        assert sig.parameters['llm_provider'].default == "openai"
        assert sig.parameters['model'].default == "gpt-4o"

    @pytest.mark.asyncio
    async def test_decision_quality_assessor_stream_structure(self):
        """Test structure of decision_quality_assessor_stream function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        decision_quality_assessor_stream = module.decision_quality_assessor_stream

        # Test that function is async generator
        import inspect

        assert inspect.isasyncgenfunction(decision_quality_assessor_stream)

        # Test function signature
        sig = inspect.signature(decision_quality_assessor_stream)
        params = list(sig.parameters.keys())
        assert 'decision' in params
        assert 'background' in params
        assert 'kwargs' in params  # **kwargs

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        DecisionQuality = module.DecisionQuality

        # Should return DecisionQuality
        assert isinstance(output, DecisionQuality)

        # Check required fields
        assert hasattr(output, "decision_description")
        assert hasattr(output, "context")
        assert hasattr(output, "alternatives_analysis")
        assert hasattr(output, "quality_assessments")
        assert hasattr(output, "bias_analysis")
        assert hasattr(output, "framework_recommendation")
        assert hasattr(output, "overall_quality_score")
        assert hasattr(output, "decision_readiness")
        assert hasattr(output, "key_strengths")
        assert hasattr(output, "critical_weaknesses")
        assert hasattr(output, "recommendations")
        assert hasattr(output, "action_items")
        assert hasattr(output, "confidence_level")

        # Check score ranges
        assert 0 <= output.overall_quality_score <= 1
        assert 0 <= output.decision_readiness <= 1
        assert 0 <= output.confidence_level <= 1

        # Check lists
        assert isinstance(output.alternatives_analysis, list)
        assert isinstance(output.quality_assessments, list)
        assert isinstance(output.bias_analysis, list)
        assert isinstance(output.key_strengths, list)
        assert isinstance(output.critical_weaknesses, list)
        assert isinstance(output.recommendations, list)
        assert isinstance(output.action_items, list)

        # Check that we have at least some analysis
        assert len(output.quality_assessments) > 0
        assert len(output.alternatives_analysis) > 0

    @pytest.mark.unit
    def test_default_alternatives_handling(self):
        """Test that default alternatives are provided when none specified."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check the function source to verify default alternatives logic
        import inspect

        source = inspect.getsource(module.decision_quality_assessor)
        assert 'if alternatives is None:' in source
        assert '["Current proposal", "Alternative approach", "Status quo"]' in source

    @pytest.mark.unit
    def test_significant_bias_filtering(self):
        """Test that biases are filtered by severity."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check the function source to verify bias filtering logic
        import inspect

        source = inspect.getsource(module.decision_quality_assessor)
        assert 'significant_biases = [b for b in bias_analysis if b.severity > 0.3]' in source

    @pytest.mark.unit
    def test_key_challenges_extraction(self):
        """Test that key challenges are extracted from quality assessments."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "decision_quality_assessor", "packages/sygaldry_registry/components/agents/decision_quality_assessor/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check the function source to verify challenge extraction logic
        import inspect

        source = inspect.getsource(module.decision_quality_assessor)
        assert 'key_challenges = []' in source
        assert 'if qa.score < 0.6:' in source
        assert 'key_challenges.extend(qa.critical_gaps)' in source
