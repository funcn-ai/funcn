"""
Role-based prompting examples using Mirascope.

Role-based prompting assigns specific personas or expertise to the model,
helping it generate responses that align with particular perspectives,
knowledge domains, or communication styles.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field


class ExpertAnalysis(BaseModel):
    """Model for expert analysis outputs."""

    domain: str = Field(..., description="Domain of expertise")
    analysis: str = Field(..., description="Expert analysis")
    key_insights: list[str] = Field(..., description="Key insights from the analysis")
    recommendations: list[str] = Field(..., description="Expert recommendations")
    confidence_level: str = Field(..., description="Confidence level (high/medium/low)")


class CreativeOutput(BaseModel):
    """Model for creative outputs."""

    content: str = Field(..., description="The creative content")
    style: str = Field(..., description="Creative style used")
    inspiration: str = Field(..., description="Source of inspiration")
    techniques: list[str] = Field(..., description="Creative techniques employed")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ExpertAnalysis)
@prompt_template(
    """
    SYSTEM: You are a {expertise} with {years_experience} years of experience.
    Your specializations include: {specializations:list}
    You are known for your {approach} approach to problem-solving.

    USER: Please analyze the following situation from your expert perspective:

    {situation}

    Provide:
    1. Your expert analysis
    2. Key insights
    3. Actionable recommendations
    4. Your confidence level in this assessment
    """
)
def role_based_expert(
    situation: str,
    expertise: str = "business strategy consultant",
    years_experience: int = 15,
    specializations: list[str] = None,
    approach: str = "data-driven and pragmatic",
):
    """
    Expert role-based analysis with configurable expertise.

    This demonstrates:
    1. Detailed role specification
    2. Configurable expertise parameters
    3. Structured expert output

    Args:
        situation: Situation to analyze
        expertise: Type of expert role
        years_experience: Years of experience
        specializations: List of specializations
        approach: Problem-solving approach

    Returns:
        ExpertAnalysis with insights and recommendations
    """
    if specializations is None:
        specializations = ["strategic planning", "market analysis", "risk assessment"]
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=CreativeOutput)
@prompt_template(
    """
    SYSTEM: You are a {creative_role} known for your {style_descriptor} style.
    Your work is influenced by {influences:list}.
    You believe that {creative_philosophy}.

    USER: Create {content_type} about: {topic}

    Requirements:
    - Target audience: {audience}
    - Tone: {tone}
    - Length: {length}

    Let your creativity flow while maintaining your unique voice.
    """
)
def role_based_creative(
    topic: str,
    content_type: str,
    audience: str = "general public",
    tone: str = "engaging and thoughtful",
    length: str = "medium",
    creative_role: str = "renowned author",
    style_descriptor: str = "vivid and emotionally resonant",
    influences: list[str] = None,
    creative_philosophy: str = "art should challenge and inspire",
):
    """
    Creative role-based content generation.

    Features:
    1. Artistic persona configuration
    2. Style and influence parameters
    3. Creative philosophy integration

    Args:
        topic: Topic for creative content
        content_type: Type of content (story/poem/essay)
        audience: Target audience
        tone: Desired tone
        length: Content length
        creative_role: Creative persona
        style_descriptor: Style description
        influences: Creative influences
        creative_philosophy: Artistic philosophy

    Returns:
        CreativeOutput with styled content
    """
    if influences is None:
        influences = ["classical literature", "modern philosophy", "human psychology"]
    pass


# Advanced role-based with dynamic persona


class AnalyticalReport(BaseModel):
    """Model for analytical reports."""

    executive_summary: str = Field(..., description="Executive summary")
    data_analysis: str = Field(..., description="Detailed data analysis")
    methodology: str = Field(..., description="Analytical methodology used")
    findings: list[str] = Field(..., description="Key findings")
    limitations: list[str] = Field(..., description="Analysis limitations")
    next_steps: list[str] = Field(..., description="Recommended next steps")


@lilypad.trace(versioning="automatic")
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=AnalyticalReport,
    call_params={"temperature": 0.2},  # Lower for analytical consistency
)
@prompt_template(
    """
    SYSTEM: You are a {analyst_type} with expertise in {domains:list}.
    Your analytical framework is based on {framework}.
    You prioritize {priorities:list} in your analysis.

    USER: Analyze the following data/scenario:

    {data}

    Context: {context}

    Specific questions to address:
    {questions:list}

    Provide a comprehensive analytical report including methodology,
    findings, limitations, and actionable next steps.
    """
)
def role_based_analytical(
    data: str,
    context: str,
    questions: list[str] = None,
    analyst_type: str = "senior data analyst",
    domains: list[str] = None,
    framework: str = "evidence-based statistical analysis",
    priorities: list[str] = None,
) -> BaseDynamicConfig:
    """
    Analytical role-based reporting with dynamic configuration.

    Advanced features:
    1. Configurable analytical framework
    2. Domain-specific expertise
    3. Priority-driven analysis

    Args:
        data: Data or scenario to analyze
        context: Additional context
        questions: Specific questions to address
        analyst_type: Type of analyst role
        domains: Expertise domains
        framework: Analytical framework
        priorities: Analysis priorities

    Returns:
        AnalyticalReport with comprehensive analysis
    """
    if questions is None:
        questions = ["What are the key patterns?", "What are the implications?"]

    if domains is None:
        domains = ["quantitative analysis", "trend identification", "risk assessment"]

    if priorities is None:
        priorities = ["accuracy", "actionability", "clarity"]

    return {}


# Multi-role collaboration example


class CollaborativeResponse(BaseModel):
    """Model for multi-role collaborative responses."""

    perspectives: dict[str, str] = Field(..., description="Different role perspectives")
    synthesis: str = Field(..., description="Synthesized conclusion")
    agreements: list[str] = Field(..., description="Points of agreement")
    disagreements: list[str] = Field(..., description="Points of disagreement")
    recommendation: str = Field(..., description="Final recommendation")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=CollaborativeResponse)
@prompt_template(
    """
    Consider the following question from multiple expert perspectives:

    Question: {question}

    {role_perspectives:lists}

    Now synthesize these perspectives:
    1. Identify areas of agreement
    2. Note points of disagreement
    3. Provide a balanced recommendation

    Consider all viewpoints fairly and provide a nuanced conclusion.
    """
)
def role_based_multi_perspective(question: str, roles: list[tuple[str, str]] = None) -> BaseDynamicConfig:
    """
    Multi-role perspective analysis for complex questions.

    This advanced pattern:
    1. Simulates multiple expert viewpoints
    2. Synthesizes diverse perspectives
    3. Identifies consensus and conflicts

    Args:
        question: Question to analyze
        roles: List of (role, perspective) tuples

    Returns:
        CollaborativeResponse with synthesized analysis
    """
    if roles is None:
        roles = [
            ("Economist", "Focus on market efficiency and economic impact"),
            ("Ethicist", "Consider moral implications and fairness"),
            ("Technologist", "Evaluate technical feasibility and innovation"),
            ("Sociologist", "Analyze social impact and community effects"),
        ]

    role_perspectives = []
    for role, focus in roles:
        role_perspectives.append([f"As a {role} ({focus}):", "Consider the implications from this perspective.", ""])

    return {"computed_fields": {"role_perspectives": role_perspectives}}


# Adaptive role with context awareness


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", call_params={"temperature": 0.5})
@prompt_template(
    """
    SYSTEM: You are a {adaptive_role}.

    Given the context, adjust your expertise level and communication style:
    - Audience expertise: {audience_level}
    - Formality required: {formality}
    - Time constraints: {time_constraint}

    USER: {query}

    Respond appropriately, adapting your role to best serve the user's needs.
    """
)
def role_based_adaptive(
    query: str,
    context_type: str,
    audience_level: str = "intermediate",
    formality: str = "professional",
    time_constraint: str = "standard",
) -> BaseDynamicConfig:
    """
    Adaptive role-based response with context awareness.

    Features:
    1. Dynamic role adaptation
    2. Audience-aware communication
    3. Context-sensitive responses

    Args:
        query: User query
        context_type: Type of context (technical/business/academic)
        audience_level: Audience expertise level
        formality: Required formality level
        time_constraint: Time constraint for response

    Returns:
        Contextually adapted response
    """
    # Determine adaptive role based on context
    role_mapping = {
        "technical": "senior software architect",
        "business": "business strategy consultant",
        "academic": "research professor",
        "creative": "creative director",
        "general": "knowledgeable assistant",
    }

    adaptive_role = role_mapping.get(context_type, "expert advisor")

    return {"computed_fields": {"adaptive_role": adaptive_role}}
