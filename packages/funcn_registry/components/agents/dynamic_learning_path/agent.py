from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Optional


class LearningStyle(str, Enum):
    """Different learning style preferences."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"


class SkillLevel(str, Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ResourceType(str, Enum):
    """Types of learning resources."""
    VIDEO = "video"
    ARTICLE = "article"
    BOOK = "book"
    COURSE = "course"
    TUTORIAL = "tutorial"
    PRACTICE = "practice"
    PROJECT = "project"
    QUIZ = "quiz"
    INTERACTIVE = "interactive"
    PODCAST = "podcast"
    WORKSHOP = "workshop"
    MENTORSHIP = "mentorship"


class SkillAssessment(BaseModel):
    """Assessment of current skill levels."""
    skill: str = Field(..., description="Name of the skill")
    current_level: SkillLevel = Field(..., description="Current proficiency level")
    confidence: float = Field(..., description="Confidence in assessment (0-1)")
    evidence: list[str] = Field(..., description="Evidence supporting this assessment")
    gaps: list[str] = Field(..., description="Identified knowledge gaps")
    improvement_areas: list[str] = Field(default_factory=list, description="Specific areas for improvement")


class LearningGoal(BaseModel):
    """Specific learning goal with timeline."""
    goal: str = Field(..., description="Clear, specific learning goal")
    target_level: SkillLevel = Field(..., description="Target proficiency level")
    timeline: str = Field(..., description="Realistic timeline to achieve goal")
    priority: int = Field(..., description="Priority ranking (1-10)")
    prerequisites: list[str] = Field(..., description="Required prerequisite knowledge")
    success_criteria: list[str] = Field(..., description="Measurable success criteria")
    milestones: list[str] = Field(default_factory=list, description="Key milestones along the way")


class LearningResource(BaseModel):
    """Individual learning resource."""
    title: str = Field(..., description="Resource title")
    type: ResourceType = Field(..., description="Type of resource")
    url: str | None = Field(None, description="URL if available")
    description: str = Field(..., description="Brief description of content")
    estimated_time: str = Field(..., description="Estimated time to complete")
    difficulty: SkillLevel = Field(..., description="Difficulty level")
    learning_styles: list[LearningStyle] = Field(..., description="Suitable learning styles")
    skills_covered: list[str] = Field(..., description="Skills this resource covers")
    quality_score: float = Field(default=0.8, description="Quality rating (0-1)")
    cost: str = Field(default="Free", description="Cost of the resource")
    prerequisites: list[str] = Field(default_factory=list, description="Prerequisites for this resource")


class LearningModule(BaseModel):
    """A module within the learning path."""
    module_name: str = Field(..., description="Name of the learning module")
    learning_goals: list[str] = Field(..., description="Goals addressed by this module")
    resources: list[LearningResource] = Field(..., description="Resources for this module")
    estimated_duration: str = Field(..., description="Estimated time for module")
    assessment_method: str = Field(..., description="How to assess completion")
    prerequisites: list[str] = Field(..., description="Required prior modules")
    practice_exercises: list[str] = Field(default_factory=list, description="Hands-on exercises")
    real_world_applications: list[str] = Field(default_factory=list, description="Real-world use cases")


class LearningPath(BaseModel):
    """Complete personalized learning path."""
    path_name: str = Field(..., description="Name of the learning path")
    description: str = Field(..., description="Overview of the learning path")
    target_audience: str = Field(..., description="Who this path is designed for")
    total_duration: str = Field(..., description="Total estimated time")
    modules: list[LearningModule] = Field(..., description="Ordered learning modules")
    milestones: list[str] = Field(..., description="Key milestones and checkpoints")
    adaptation_strategy: str = Field(..., description="How to adapt based on progress")
    success_metrics: list[str] = Field(..., description="How to measure success")
    learning_outcomes: list[str] = Field(default_factory=list, description="Expected outcomes upon completion")
    career_relevance: str = Field(default="", description="How this path relates to career goals")


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[SkillAssessment],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert learning assessment specialist. Your role is to evaluate a learner's
    current skill levels based on their background, experience, and self-reported knowledge.

    Consider:
    1. Be realistic about skill levels - most people overestimate their abilities
    2. Look for concrete evidence of skills in their background
    3. Identify specific knowledge gaps that need to be addressed
    4. Consider both technical and soft skills relevant to their goals
    5. Assess confidence based on practical experience vs theoretical knowledge

    Skill Levels:
    - BEGINNER: No prior experience or knowledge
    - NOVICE: Basic understanding, limited practical experience
    - INTERMEDIATE: Solid foundation with some practical experience
    - ADVANCED: Strong skills with extensive practical experience
    - EXPERT: Deep expertise with ability to teach and innovate

    USER:
    Assess the current skill levels for this learner:

    Background: {background}
    Experience: {experience}
    Learning Goals: {learning_goals}
    Self-Assessment: {self_assessment}

    Provide detailed skill assessments with evidence and identified gaps.
    """
)
def assess_current_skills(
    background: str,
    experience: str,
    learning_goals: str,
    self_assessment: str = ""
) -> list[SkillAssessment]:
    """Assess learner's current skill levels."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[LearningGoal],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert learning goal designer. Your role is to create specific, measurable,
    achievable, relevant, and time-bound (SMART) learning goals based on the learner's
    current skills and desired outcomes.

    Consider:
    1. Goals should be specific and measurable
    2. Timeline should be realistic based on current skill level
    3. Break down large goals into smaller, achievable milestones
    4. Consider prerequisites and logical learning progression
    5. Align with learner's motivation and available time
    6. Include both short-term and long-term goals

    USER:
    Create learning goals for this learner:

    Current Skills: {current_skills}
    Desired Outcomes: {desired_outcomes}
    Available Time: {available_time}
    Learning Preferences: {learning_preferences}
    Constraints: {constraints}

    Design a set of prioritized, achievable learning goals with clear success criteria.
    """
)
def design_learning_goals(
    current_skills: list[SkillAssessment],
    desired_outcomes: str,
    available_time: str,
    learning_preferences: str = "",
    constraints: str = ""
) -> BaseDynamicConfig:
    """Design specific learning goals based on assessment."""
    return {
        "computed_fields": {
            "current_skills": current_skills,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[LearningResource],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert learning resource curator. Your role is to identify and recommend
    high-quality learning resources that match the learner's goals, style, and skill level.

    Consider:
    1. Match resources to learning style preferences
    2. Ensure appropriate difficulty progression
    3. Include diverse resource types for engagement
    4. Prioritize practical, hands-on learning opportunities
    5. Consider time constraints and accessibility
    6. Balance free and paid resources
    7. Include community and peer learning opportunities

    Resource Types:
    - VIDEO: Video tutorials, lectures, demonstrations
    - ARTICLE: Blog posts, documentation, written guides
    - BOOK: Comprehensive books and ebooks
    - COURSE: Structured online courses
    - TUTORIAL: Step-by-step tutorials
    - PRACTICE: Coding challenges, exercises
    - PROJECT: Real-world projects to build
    - QUIZ: Assessments and knowledge checks
    - INTERACTIVE: Interactive learning platforms
    - PODCAST: Audio content for learning on the go
    - WORKSHOP: Live or recorded workshops
    - MENTORSHIP: One-on-one guidance opportunities

    USER:
    Find learning resources for these goals:

    Learning Goals: {learning_goals}
    Current Skill Level: {current_level}
    Learning Style: {learning_style}
    Time Constraints: {time_constraints}
    Specific Topics: {topics}
    Budget: {budget}

    Recommend diverse, high-quality resources that support these learning goals.
    """
)
def curate_learning_resources(
    learning_goals: list[LearningGoal],
    current_level: str,
    learning_style: str,
    time_constraints: str = "",
    topics: str = "",
    budget: str = "Mixed"
) -> BaseDynamicConfig:
    """Curate appropriate learning resources."""
    return {
        "computed_fields": {
            "learning_goals": learning_goals,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=LearningPath,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert learning path architect. Your role is to design comprehensive,
    personalized learning paths that efficiently guide learners from their current
    state to their desired goals.

    Consider:
    1. Logical progression from basic to advanced concepts
    2. Balance theory with practical application
    3. Include regular assessment and feedback points
    4. Design for adaptability based on progress
    5. Maintain learner engagement and motivation
    6. Respect time constraints and learning preferences
    7. Include career development aspects
    8. Build in reflection and review periods

    Design Principles:
    - Start with foundational concepts
    - Build complexity gradually
    - Include hands-on practice
    - Provide multiple learning modalities
    - Create clear milestones
    - Allow for different paces
    - Include real-world applications
    - Foster community learning

    USER:
    Design a comprehensive learning path:

    Learning Goals: {learning_goals}
    Available Resources: {resources}
    Learner Profile: {learner_profile}
    Time Constraints: {time_constraints}
    Success Criteria: {success_criteria}
    Career Goals: {career_goals}

    Create a structured, adaptive learning path with clear modules and progression.
    """
)
def design_learning_path(
    learning_goals: list[LearningGoal],
    resources: list[LearningResource],
    learner_profile: str,
    time_constraints: str = "",
    success_criteria: str = "",
    career_goals: str = ""
) -> BaseDynamicConfig:
    """Design comprehensive learning path."""
    return {
        "computed_fields": {
            "learning_goals": learning_goals,
            "resources": resources,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=str,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert learning advisor. Provide personalized learning recommendations
    based on the learner's progress and challenges.

    USER:
    Provide adaptive recommendations for this learner:

    Current Progress: {progress}
    Challenges Faced: {challenges}
    Learning Path: {learning_path}
    Time Spent: {time_spent}

    Suggest adjustments to optimize their learning journey.
    """
)
def generate_adaptive_recommendations(
    progress: str,
    challenges: str,
    learning_path: str,
    time_spent: str
) -> str:
    """Generate adaptive recommendations based on progress."""
    pass


async def dynamic_learning_path_generator(
    background: str,
    experience: str,
    learning_goals: str,
    available_time: str,
    learning_style: LearningStyle = LearningStyle.MULTIMODAL,
    constraints: str = "",
    budget: str = "Mixed",
    career_goals: str = "",
    llm_provider: str = "openai",
    model: str = "gpt-4o"
) -> LearningPath:
    """
    Generate a personalized, adaptive learning path based on individual needs and goals.

    This agent assesses current skills, designs specific learning goals, curates appropriate
    resources, and creates a structured learning path with built-in adaptation strategies.

    Args:
        background: Educational and professional background
        experience: Relevant experience and previous learning
        learning_goals: Desired learning outcomes and objectives
        available_time: Time available for learning (e.g., "2 hours/week")
        learning_style: Preferred learning style
        constraints: Any constraints or limitations
        budget: Budget for learning resources
        career_goals: Long-term career aspirations
        llm_provider: LLM provider to use
        model: Model to use for generation

    Returns:
        LearningPath with personalized modules, resources, and progression
    """

    # Step 1: Assess current skills
    print("Assessing current skill levels...")
    current_skills = await assess_current_skills(
        background=background,
        experience=experience,
        learning_goals=learning_goals,
        self_assessment=""
    )
    print(f"Assessed {len(current_skills)} skill areas")

    # Step 2: Design specific learning goals
    print("Designing learning goals...")
    specific_goals = await design_learning_goals(
        current_skills=current_skills,
        desired_outcomes=learning_goals,
        available_time=available_time,
        learning_preferences=learning_style.value,
        constraints=constraints
    )
    print(f"Created {len(specific_goals)} specific goals")

    # Step 3: Curate learning resources
    print("Curating learning resources...")

    # Determine overall skill level for resource curation
    skill_levels = [skill.current_level for skill in current_skills]
    if SkillLevel.BEGINNER in skill_levels:
        overall_level = "beginner to intermediate"
    elif SkillLevel.EXPERT in skill_levels:
        overall_level = "advanced to expert"
    else:
        overall_level = "intermediate"

    resources = await curate_learning_resources(
        learning_goals=specific_goals,
        current_level=overall_level,
        learning_style=learning_style.value,
        time_constraints=available_time,
        topics=learning_goals,
        budget=budget
    )
    print(f"Found {len(resources)} learning resources")

    # Step 4: Design comprehensive learning path
    print("Designing learning path...")
    learner_profile = f"""
    Background: {background}
    Experience: {experience}
    Learning Style: {learning_style.value}
    Current Skills: {', '.join([f"{s.skill} ({s.current_level.value})" for s in current_skills[:3]])}
    """

    learning_path = await design_learning_path(
        learning_goals=specific_goals,
        resources=resources,
        learner_profile=learner_profile,
        time_constraints=available_time,
        success_criteria=learning_goals,
        career_goals=career_goals
    )

    print("Dynamic learning path generated!")
    return learning_path


async def dynamic_learning_path_stream(
    background: str,
    experience: str,
    learning_goals: str,
    available_time: str,
    **kwargs
) -> AsyncGenerator[str, None]:
    """Stream the learning path generation process."""

    yield "Generating personalized learning path...\n\n"
    yield f"**Background:** {background}\n"
    yield f"**Goals:** {learning_goals}\n"
    yield f"**Available Time:** {available_time}\n\n"

    # Generate the learning path
    learning_path = await dynamic_learning_path_generator(
        background, experience, learning_goals, available_time, **kwargs
    )

    yield f"## {learning_path.path_name}\n\n"
    yield f"{learning_path.description}\n\n"
    yield f"**Target Audience:** {learning_path.target_audience}\n"
    yield f"**Total Duration:** {learning_path.total_duration}\n"
    yield f"**Career Relevance:** {learning_path.career_relevance}\n\n"

    yield "## Learning Modules\n\n"
    for i, module in enumerate(learning_path.modules, 1):
        yield f"### Module {i}: {module.module_name}\n"
        yield f"**Duration:** {module.estimated_duration}\n"
        yield f"**Goals:** {', '.join(module.learning_goals[:2])}\n"
        yield f"**Assessment:** {module.assessment_method}\n\n"

        if module.resources:
            yield "**Key Resources:**\n"
            for resource in module.resources[:3]:  # Show first 3 resources
                yield f"- [{resource.title}]({resource.url if resource.url else '#'}) "
                yield f"({resource.type.value}) - {resource.estimated_time}\n"
            if len(module.resources) > 3:
                yield f"- ... and {len(module.resources) - 3} more resources\n"

        if module.practice_exercises:
            yield f"\n**Practice:** {', '.join(module.practice_exercises[:2])}\n"

        yield "\n"

    yield "## Key Milestones\n\n"
    for milestone in learning_path.milestones:
        yield f"- {milestone}\n"

    yield "\n## Success Metrics\n\n"
    for metric in learning_path.success_metrics:
        yield f"- {metric}\n"

    yield "\n## Learning Outcomes\n\n"
    for outcome in learning_path.learning_outcomes:
        yield f"- {outcome}\n"

    yield f"\n**Adaptation Strategy:** {learning_path.adaptation_strategy}\n"
