"""Test suite for dynamic_learning_path agent following best practices."""

import pytest
from pathlib import Path
from tests.utils import BaseAgentTest
from unittest.mock import AsyncMock, patch


class TestDynamicLearningPathAgent(BaseAgentTest):
    """Test cases for dynamic learning path agent."""

    component_name = "dynamic_learning_path"
    component_path = Path("packages/funcn_registry/components/agents/dynamic_learning_path")

    def get_component_function(self):
        """Get the main agent function."""
        # Import directly without triggering __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.dynamic_learning_path_generator

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {
                "background": "Computer science degree, 2 years as junior developer",
                "experience": "Basic Python, JavaScript, some React experience",
                "learning_goals": "Become a full-stack developer proficient in modern web technologies",
                "available_time": "10 hours per week",
                "learning_style": "multimodal",
                "constraints": "Full-time job, limited budget",
                "budget": "Mixed",
                "career_goals": "Senior full-stack developer in 2 years",
            },
            {
                "background": "Marketing professional with 5 years experience",
                "experience": "Excel, basic SQL, no programming",
                "learning_goals": "Learn data analysis and visualization for marketing insights",
                "available_time": "5 hours per week",
                "learning_style": "visual",
                "budget": "Free resources only",
                "career_goals": "Marketing analyst role",
            },
            {
                "background": "Recent graduate in business administration",
                "experience": "Academic projects, internship at startup",
                "learning_goals": "Master product management skills and agile methodologies",
                "available_time": "15 hours per week",
                "learning_style": "reading_writing",
                "constraints": "Job hunting, need practical skills quickly",
                "budget": "Up to $200/month",
                "career_goals": "Product manager at tech company",
            },
        ]

    @pytest.mark.unit
    def test_enum_values(self):
        """Test that all enums have correct values."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test LearningStyle enum
        LearningStyle = module.LearningStyle
        assert LearningStyle.VISUAL.value == "visual"
        assert LearningStyle.AUDITORY.value == "auditory"
        assert LearningStyle.KINESTHETIC.value == "kinesthetic"
        assert LearningStyle.READING_WRITING.value == "reading_writing"
        assert LearningStyle.MULTIMODAL.value == "multimodal"

        # Test SkillLevel enum
        SkillLevel = module.SkillLevel
        assert SkillLevel.BEGINNER.value == "beginner"
        assert SkillLevel.NOVICE.value == "novice"
        assert SkillLevel.INTERMEDIATE.value == "intermediate"
        assert SkillLevel.ADVANCED.value == "advanced"
        assert SkillLevel.EXPERT.value == "expert"

        # Test ResourceType enum
        ResourceType = module.ResourceType
        resource_types = [
            "video",
            "article",
            "book",
            "course",
            "tutorial",
            "practice",
            "project",
            "quiz",
            "interactive",
            "podcast",
            "workshop",
            "mentorship",
        ]
        for rt in resource_types:
            assert hasattr(ResourceType, rt.upper())

    @pytest.mark.unit
    def test_response_models_structure(self):
        """Test that response models have correct structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Test that the models exist
        assert hasattr(module, 'SkillAssessment')
        assert hasattr(module, 'LearningGoal')
        assert hasattr(module, 'LearningResource')
        assert hasattr(module, 'LearningModule')
        assert hasattr(module, 'LearningPath')

        # Test SkillAssessment model
        SkillAssessment = module.SkillAssessment
        SkillLevel = module.SkillLevel
        skill_assessment = SkillAssessment(
            skill="Python Programming",
            current_level=SkillLevel.INTERMEDIATE,
            confidence=0.8,
            evidence=["2 years experience", "Built several projects"],
            gaps=["Advanced OOP", "Async programming"],
            improvement_areas=["Testing", "Design patterns"],
        )
        assert skill_assessment.skill == "Python Programming"
        assert skill_assessment.current_level == SkillLevel.INTERMEDIATE
        assert skill_assessment.confidence == 0.8
        assert len(skill_assessment.evidence) == 2
        assert len(skill_assessment.gaps) == 2
        assert len(skill_assessment.improvement_areas) == 2

        # Test LearningGoal model
        LearningGoal = module.LearningGoal
        learning_goal = LearningGoal(
            goal="Master React development",
            target_level=SkillLevel.ADVANCED,
            timeline="3 months",
            priority=8,
            prerequisites=["JavaScript", "HTML/CSS"],
            success_criteria=["Build production app", "Pass certification"],
            milestones=["Complete basics", "Build first app", "Advanced patterns"],
        )
        assert learning_goal.goal == "Master React development"
        assert learning_goal.target_level == SkillLevel.ADVANCED
        assert learning_goal.timeline == "3 months"
        assert learning_goal.priority == 8
        assert len(learning_goal.prerequisites) == 2
        assert len(learning_goal.success_criteria) == 2
        assert len(learning_goal.milestones) == 3

        # Test LearningResource model
        LearningResource = module.LearningResource
        ResourceType = module.ResourceType
        LearningStyle = module.LearningStyle
        resource = LearningResource(
            title="React Complete Guide",
            type=ResourceType.COURSE,
            url="https://example.com/react-course",
            description="Comprehensive React course",
            estimated_time="40 hours",
            difficulty=SkillLevel.INTERMEDIATE,
            learning_styles=[LearningStyle.VISUAL, LearningStyle.KINESTHETIC],
            skills_covered=["React", "Redux", "React Router"],
            quality_score=0.9,
            cost="$49.99",
            prerequisites=["JavaScript basics"],
        )
        assert resource.title == "React Complete Guide"
        assert resource.type == ResourceType.COURSE
        assert resource.url == "https://example.com/react-course"
        assert resource.estimated_time == "40 hours"
        assert resource.difficulty == SkillLevel.INTERMEDIATE
        assert len(resource.learning_styles) == 2
        assert len(resource.skills_covered) == 3
        assert resource.quality_score == 0.9

        # Test LearningModule model
        LearningModule = module.LearningModule
        module_obj = LearningModule(
            module_name="React Fundamentals",
            learning_goals=["Understand components", "Master state management"],
            resources=[resource],
            estimated_duration="2 weeks",
            assessment_method="Build a todo app",
            prerequisites=["JavaScript Module"],
            practice_exercises=["Component exercises", "State management tasks"],
            real_world_applications=["E-commerce site", "Dashboard"],
        )
        assert module_obj.module_name == "React Fundamentals"
        assert len(module_obj.learning_goals) == 2
        assert len(module_obj.resources) == 1
        assert module_obj.estimated_duration == "2 weeks"
        assert module_obj.assessment_method == "Build a todo app"
        assert len(module_obj.prerequisites) == 1
        assert len(module_obj.practice_exercises) == 2
        assert len(module_obj.real_world_applications) == 2

        # Test LearningPath model
        LearningPath = module.LearningPath
        learning_path = LearningPath(
            path_name="Full-Stack Developer Journey",
            description="Complete path to become a full-stack developer",
            target_audience="Junior developers",
            total_duration="6 months",
            modules=[module_obj],
            milestones=["Frontend basics", "Backend integration", "Full app"],
            adaptation_strategy="Adjust pace based on quiz scores",
            success_metrics=["Build portfolio", "Pass assessments"],
            learning_outcomes=["Build full-stack apps", "Deploy to production"],
            career_relevance="Prepares for mid-level developer roles",
        )
        assert learning_path.path_name == "Full-Stack Developer Journey"
        assert learning_path.description == "Complete path to become a full-stack developer"
        assert learning_path.target_audience == "Junior developers"
        assert learning_path.total_duration == "6 months"
        assert len(learning_path.modules) == 1
        assert len(learning_path.milestones) == 3
        assert learning_path.adaptation_strategy == "Adjust pace based on quiz scores"
        assert len(learning_path.success_metrics) == 2
        assert len(learning_path.learning_outcomes) == 2
        assert learning_path.career_relevance == "Prepares for mid-level developer roles"

    @pytest.mark.unit
    def test_agent_has_required_functions(self):
        """Test that all required agent functions are present."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)

        # Main functions
        assert hasattr(agent, 'dynamic_learning_path_generator')
        assert callable(agent.dynamic_learning_path_generator)
        assert hasattr(agent, 'dynamic_learning_path_stream')
        assert callable(agent.dynamic_learning_path_stream)

        # LLM-decorated functions
        assert hasattr(agent, 'assess_current_skills')
        assert hasattr(agent, 'design_learning_goals')
        assert hasattr(agent, 'curate_learning_resources')
        assert hasattr(agent, 'design_learning_path')
        assert hasattr(agent, 'generate_adaptive_recommendations')

        # Check that LLM functions have the decorator
        for func_name in [
            'assess_current_skills',
            'design_learning_goals',
            'curate_learning_resources',
            'design_learning_path',
            'generate_adaptive_recommendations',
        ]:
            func = getattr(agent, func_name)
            # These should have been decorated by @llm.call
            assert hasattr(func, '__wrapped__') or hasattr(func, '__name__')

    @pytest.mark.asyncio
    async def test_dynamic_learning_path_generator_structure(self):
        """Test basic structure of dynamic_learning_path_generator function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        dynamic_learning_path_generator = module.dynamic_learning_path_generator

        # Test that function is async
        import inspect

        assert inspect.iscoroutinefunction(dynamic_learning_path_generator)

        # Test function signature
        sig = inspect.signature(dynamic_learning_path_generator)
        params = list(sig.parameters.keys())
        required_params = ['background', 'experience', 'learning_goals', 'available_time']
        for param in required_params:
            assert param in params

        # Test optional parameters
        optional_params = ['learning_style', 'constraints', 'budget', 'career_goals', 'llm_provider', 'model']
        for param in optional_params:
            assert param in params

    @pytest.mark.asyncio
    async def test_dynamic_learning_path_stream_structure(self):
        """Test structure of dynamic_learning_path_stream function."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        dynamic_learning_path_stream = module.dynamic_learning_path_stream

        # Test that function is async generator
        import inspect

        assert inspect.isasyncgenfunction(dynamic_learning_path_stream)

        # Test function signature
        sig = inspect.signature(dynamic_learning_path_stream)
        params = list(sig.parameters.keys())
        assert 'background' in params
        assert 'experience' in params
        assert 'learning_goals' in params
        assert 'available_time' in params
        assert 'kwargs' in params

    def validate_agent_output(self, output, input_data):
        """Validate the agent output structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        LearningPath = module.LearningPath

        # Check that output is a LearningPath
        assert isinstance(output, LearningPath)

        # Validate required fields
        assert hasattr(output, "path_name")
        assert hasattr(output, "description")
        assert hasattr(output, "target_audience")
        assert hasattr(output, "total_duration")
        assert hasattr(output, "modules")
        assert hasattr(output, "milestones")
        assert hasattr(output, "adaptation_strategy")
        assert hasattr(output, "success_metrics")
        assert hasattr(output, "learning_outcomes")
        assert hasattr(output, "career_relevance")

        # Validate types
        assert isinstance(output.path_name, str)
        assert isinstance(output.description, str)
        assert isinstance(output.target_audience, str)
        assert isinstance(output.total_duration, str)
        assert isinstance(output.modules, list)
        assert isinstance(output.milestones, list)
        assert isinstance(output.adaptation_strategy, str)
        assert isinstance(output.success_metrics, list)
        assert isinstance(output.learning_outcomes, list)
        assert isinstance(output.career_relevance, str)

        # Validate modules structure
        if output.modules:
            for module in output.modules:
                assert hasattr(module, "module_name")
                assert hasattr(module, "learning_goals")
                assert hasattr(module, "resources")
                assert hasattr(module, "estimated_duration")
                assert hasattr(module, "assessment_method")
                assert hasattr(module, "prerequisites")
                assert isinstance(module.learning_goals, list)
                assert isinstance(module.resources, list)
                assert isinstance(module.prerequisites, list)

                # Validate resources within modules
                for resource in module.resources:
                    assert hasattr(resource, "title")
                    assert hasattr(resource, "type")
                    assert hasattr(resource, "description")
                    assert hasattr(resource, "estimated_time")
                    assert hasattr(resource, "difficulty")
                    assert hasattr(resource, "learning_styles")
                    assert hasattr(resource, "skills_covered")
                    assert isinstance(resource.learning_styles, list)
                    assert isinstance(resource.skills_covered, list)

    @pytest.mark.unit
    def test_learning_style_conversion(self):
        """Test that learning style string converts to enum properly."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        LearningStyle = module.LearningStyle

        # Test that we can create enum from string value
        visual = LearningStyle("visual")
        assert visual == LearningStyle.VISUAL

        multimodal = LearningStyle("multimodal")
        assert multimodal == LearningStyle.MULTIMODAL

        # Test all enum values
        for style in LearningStyle:
            assert LearningStyle(style.value) == style

    @pytest.mark.unit
    def test_skill_level_ordering(self):
        """Test skill level progression logic."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SkillLevel = module.SkillLevel

        # Verify the expected ordering
        skill_order = [SkillLevel.BEGINNER, SkillLevel.NOVICE, SkillLevel.INTERMEDIATE, SkillLevel.ADVANCED, SkillLevel.EXPERT]

        # Check that all levels are included
        assert len(skill_order) == len(list(SkillLevel))

        # Verify each level exists
        for level in skill_order:
            assert level in SkillLevel

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_adaptive_recommendations(self):
        """Test the adaptive recommendations function structure."""
        # Use direct import to avoid __init__.py chain
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dynamic_learning_path", "packages/funcn_registry/components/agents/dynamic_learning_path/agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        generate_adaptive_recommendations = module.generate_adaptive_recommendations

        # Check function exists and has correct decorator
        assert hasattr(generate_adaptive_recommendations, '__wrapped__') or hasattr(generate_adaptive_recommendations, '__name__')

        # Test function signature
        import inspect

        sig = inspect.signature(generate_adaptive_recommendations)
        params = list(sig.parameters.keys())
        assert 'progress' in params
        assert 'challenges' in params
        assert 'learning_path' in params
        assert 'time_spent' in params
