from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Optional


class DecisionType(str, Enum):
    """Types of decisions to assess."""
    STRATEGIC = "strategic"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    HIRING = "hiring"
    INVESTMENT = "investment"
    PRODUCT = "product"
    MARKETING = "marketing"
    TECHNICAL = "technical"
    POLICY = "policy"
    PERSONAL = "personal"
    CRISIS = "crisis"
    INNOVATION = "innovation"


class BiasType(str, Enum):
    """Types of cognitive biases to check for."""
    CONFIRMATION_BIAS = "confirmation_bias"
    ANCHORING_BIAS = "anchoring_bias"
    AVAILABILITY_HEURISTIC = "availability_heuristic"
    SUNK_COST_FALLACY = "sunk_cost_fallacy"
    OVERCONFIDENCE_BIAS = "overconfidence_bias"
    GROUPTHINK = "groupthink"
    RECENCY_BIAS = "recency_bias"
    SURVIVORSHIP_BIAS = "survivorship_bias"
    PLANNING_FALLACY = "planning_fallacy"
    STATUS_QUO_BIAS = "status_quo_bias"
    HINDSIGHT_BIAS = "hindsight_bias"
    FRAMING_EFFECT = "framing_effect"
    BANDWAGON_EFFECT = "bandwagon_effect"
    DUNNING_KRUGER_EFFECT = "dunning_kruger_effect"
    HALO_EFFECT = "halo_effect"


class QualityDimension(str, Enum):
    """Dimensions of decision quality."""
    INFORMATION_QUALITY = "information_quality"
    ALTERNATIVE_GENERATION = "alternative_generation"
    STAKEHOLDER_CONSIDERATION = "stakeholder_consideration"
    RISK_ASSESSMENT = "risk_assessment"
    TIMELINE_APPROPRIATENESS = "timeline_appropriateness"
    RESOURCE_CONSIDERATION = "resource_consideration"
    REVERSIBILITY_ANALYSIS = "reversibility_analysis"
    ETHICAL_CONSIDERATION = "ethical_consideration"
    IMPLEMENTATION_FEASIBILITY = "implementation_feasibility"
    OUTCOME_MEASURABILITY = "outcome_measurability"
    ADAPTABILITY = "adaptability"
    SUSTAINABILITY = "sustainability"


class DecisionContext(BaseModel):
    """Context surrounding a decision."""
    decision_type: DecisionType = Field(..., description="Type of decision being made")
    stakeholders: list[str] = Field(..., description="Key stakeholders affected")
    constraints: list[str] = Field(..., description="Constraints and limitations")
    timeline: str = Field(..., description="Decision timeline and urgency")
    resources_available: list[str] = Field(..., description="Available resources")
    success_metrics: list[str] = Field(..., description="How success will be measured")
    risk_tolerance: str = Field(..., description="Risk tolerance level")
    decision_authority: str = Field(..., description="Who has decision-making authority")
    external_factors: list[str] = Field(..., description="External factors influencing decision")
    organizational_culture: str = Field(..., description="Cultural context and values")


class BiasAnalysis(BaseModel):
    """Analysis of potential cognitive biases."""
    bias_type: BiasType = Field(..., description="Type of bias identified")
    evidence: list[str] = Field(..., description="Evidence of this bias")
    severity: float = Field(..., description="Severity of bias impact (0-1)")
    mitigation_strategies: list[str] = Field(..., description="Strategies to mitigate this bias")
    impact_on_decision: str = Field(..., description="How this bias affects the decision")
    likelihood_of_occurrence: float = Field(..., description="Likelihood this bias is present (0-1)")
    detection_confidence: float = Field(..., description="Confidence in bias detection (0-1)")


class QualityAssessment(BaseModel):
    """Assessment of decision quality across dimensions."""
    dimension: QualityDimension = Field(..., description="Quality dimension assessed")
    score: float = Field(..., description="Quality score for this dimension (0-1)")
    strengths: list[str] = Field(..., description="Strengths in this dimension")
    weaknesses: list[str] = Field(..., description="Weaknesses in this dimension")
    improvement_suggestions: list[str] = Field(..., description="Suggestions for improvement")
    critical_gaps: list[str] = Field(..., description="Critical gaps identified")
    best_practices_applied: list[str] = Field(..., description="Best practices already in use")
    priority_level: str = Field(..., description="Priority for improvement (low/medium/high/critical)")


class DecisionAnalysis(BaseModel):
    """Comprehensive analysis of decision alternatives."""
    alternative: str = Field(..., description="Decision alternative being analyzed")
    pros: list[str] = Field(..., description="Advantages of this alternative")
    cons: list[str] = Field(..., description="Disadvantages of this alternative")
    risks: list[str] = Field(..., description="Risks associated with this alternative")
    opportunities: list[str] = Field(..., description="Opportunities this alternative creates")
    resource_requirements: list[str] = Field(..., description="Resources required")
    success_probability: float = Field(..., description="Estimated probability of success (0-1)")
    impact_assessment: str = Field(..., description="Assessment of potential impact")
    implementation_complexity: str = Field(..., description="Complexity of implementation")
    alignment_score: float = Field(..., description="Alignment with objectives (0-1)")
    sustainability_score: float = Field(..., description="Long-term sustainability (0-1)")


class DecisionFramework(BaseModel):
    """Framework recommendations for decision-making."""
    recommended_framework: str = Field(..., description="Recommended decision framework")
    framework_rationale: str = Field(..., description="Why this framework is appropriate")
    key_steps: list[str] = Field(..., description="Key steps in the framework")
    tools_needed: list[str] = Field(..., description="Tools or methods to support decision")
    success_factors: list[str] = Field(..., description="Critical success factors")


class DecisionQuality(BaseModel):
    """Complete decision quality assessment."""
    decision_description: str = Field(..., description="Description of the decision")
    context: DecisionContext = Field(..., description="Decision context")
    alternatives_analysis: list[DecisionAnalysis] = Field(..., description="Analysis of alternatives")
    quality_assessments: list[QualityAssessment] = Field(..., description="Quality assessments")
    bias_analysis: list[BiasAnalysis] = Field(..., description="Bias analysis")
    framework_recommendation: DecisionFramework = Field(..., description="Recommended decision framework")
    overall_quality_score: float = Field(..., description="Overall decision quality score (0-1)")
    decision_readiness: float = Field(..., description="Readiness to make decision (0-1)")
    key_strengths: list[str] = Field(..., description="Key strengths of the decision process")
    critical_weaknesses: list[str] = Field(..., description="Critical weaknesses to address")
    recommendations: list[str] = Field(..., description="Recommendations for improvement")
    action_items: list[str] = Field(..., description="Specific action items")
    confidence_level: float = Field(..., description="Confidence in the assessment (0-1)")


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=DecisionContext,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert decision analyst with deep expertise in organizational behavior,
    strategic planning, and decision science. Your role is to analyze and structure
    the context surrounding important decisions to ensure comprehensive evaluation.

    Consider:
    1. Type and nature of the decision
    2. All affected stakeholders (internal and external)
    3. Constraints and limitations (time, budget, resources, regulations)
    4. Timeline and urgency factors
    5. Available resources (human, financial, technological)
    6. Success metrics and criteria
    7. Risk tolerance and preferences
    8. Decision-making authority and governance
    9. External factors (market, competition, regulations)
    10. Organizational culture and values

    Decision Types:
    - STRATEGIC: Long-term direction and positioning
    - OPERATIONAL: Day-to-day operations and processes
    - FINANCIAL: Financial investments and resource allocation
    - HIRING: Personnel and team decisions
    - INVESTMENT: Investment and funding decisions
    - PRODUCT: Product development and features
    - MARKETING: Marketing strategy and campaigns
    - TECHNICAL: Technical architecture and implementation
    - POLICY: Policy and governance decisions
    - PERSONAL: Personal life and career decisions
    - CRISIS: Crisis response and management
    - INNOVATION: Innovation and R&D decisions

    USER:
    Analyze the context for this decision:

    Decision: {decision}
    Background: {background}
    Stakeholders: {stakeholders}
    Constraints: {constraints}
    Timeline: {timeline}

    Provide a comprehensive context analysis for decision quality assessment.
    """
)
def analyze_decision_context(
    decision: str,
    background: str = "",
    stakeholders: str = "",
    constraints: str = "",
    timeline: str = ""
) -> DecisionContext:
    """Analyze and structure the decision context."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[DecisionAnalysis],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert decision analyst specializing in multi-criteria decision analysis
    and alternative evaluation. Your role is to thoroughly analyze each decision
    alternative across multiple dimensions to support high-quality decision making.

    For each alternative, analyze:
    1. Advantages and benefits (pros) - both immediate and long-term
    2. Disadvantages and drawbacks (cons) - including hidden costs
    3. Risks and potential negative outcomes - with likelihood assessment
    4. Opportunities and potential positive outcomes - including synergies
    5. Resource requirements (time, money, people, technology)
    6. Probability of success based on evidence
    7. Overall impact assessment (strategic, operational, financial)
    8. Implementation complexity and challenges
    9. Alignment with objectives and values
    10. Long-term sustainability

    Consider:
    - Short-term vs. long-term implications
    - Direct vs. indirect effects
    - Quantifiable vs. qualitative impacts
    - Reversibility and flexibility
    - Second and third-order effects
    - Stakeholder reactions
    - Market and competitive dynamics

    USER:
    Analyze these decision alternatives:

    Decision Context: {decision_context}
    Alternatives: {alternatives}
    Evaluation Criteria: {evaluation_criteria}
    Success Metrics: {success_metrics}

    Provide comprehensive analysis for each alternative with realistic assessments.
    """
)
def analyze_decision_alternatives(
    decision_context: DecisionContext,
    alternatives: list[str],
    evaluation_criteria: str = "",
    success_metrics: str = ""
) -> BaseDynamicConfig:
    """Analyze decision alternatives comprehensively."""
    return {
        "computed_fields": {
            "decision_context": decision_context,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[QualityAssessment],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert in decision quality assessment with deep knowledge of
    decision science, organizational behavior, and best practices in decision-making.
    Your role is to evaluate decision-making processes across key quality dimensions.

    Quality Dimensions to Assess:
    1. INFORMATION_QUALITY: Completeness, accuracy, relevance, and timeliness of information
    2. ALTERNATIVE_GENERATION: Breadth, creativity, and feasibility of alternatives
    3. STAKEHOLDER_CONSIDERATION: Inclusion, engagement, and consideration of all stakeholders
    4. RISK_ASSESSMENT: Thoroughness of risk identification, analysis, and mitigation
    5. TIMELINE_APPROPRIATENESS: Appropriateness of decision timing and urgency
    6. RESOURCE_CONSIDERATION: Realistic assessment of resource requirements and availability
    7. REVERSIBILITY_ANALYSIS: Consideration of decision reversibility and flexibility
    8. ETHICAL_CONSIDERATION: Ethical implications and moral considerations
    9. IMPLEMENTATION_FEASIBILITY: Practicality and feasibility of implementation
    10. OUTCOME_MEASURABILITY: Clarity and measurability of success criteria
    11. ADAPTABILITY: Ability to adapt as conditions change
    12. SUSTAINABILITY: Long-term viability and sustainability

    For each dimension:
    - Assess current quality (0-1 scale)
    - Identify specific strengths and best practices
    - Identify specific weaknesses and gaps
    - Suggest concrete improvements
    - Flag critical gaps requiring immediate attention
    - Determine priority level for improvement

    Scoring Guidelines:
    - 0.0-0.2: Critical deficiencies, immediate action required
    - 0.2-0.4: Major gaps, significant improvements needed
    - 0.4-0.6: Moderate quality, several improvements recommended
    - 0.6-0.8: Good quality, minor refinements suggested
    - 0.8-1.0: Excellent quality, best practices demonstrated

    USER:
    Assess decision quality across all dimensions:

    Decision Context: {decision_context}
    Decision Process: {decision_process}
    Information Available: {information_available}
    Alternatives Considered: {alternatives_considered}

    Provide detailed quality assessment for each dimension.
    """
)
def assess_decision_quality_dimensions(
    decision_context: DecisionContext,
    decision_process: str,
    information_available: str = "",
    alternatives_considered: str = ""
) -> BaseDynamicConfig:
    """Assess decision quality across multiple dimensions."""
    return {
        "computed_fields": {
            "decision_context": decision_context,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[BiasAnalysis],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert in cognitive psychology and behavioral economics, specializing
    in cognitive bias detection and mitigation in decision-making processes.

    Common Biases to Check:
    1. CONFIRMATION_BIAS: Seeking information that confirms existing beliefs
    2. ANCHORING_BIAS: Over-relying on first information received
    3. AVAILABILITY_HEURISTIC: Overweighting easily recalled information
    4. SUNK_COST_FALLACY: Continuing due to past investments
    5. OVERCONFIDENCE_BIAS: Overestimating abilities or chances of success
    6. GROUPTHINK: Conformity pressure in group decisions
    7. RECENCY_BIAS: Overweighting recent events
    8. SURVIVORSHIP_BIAS: Focusing only on successful examples
    9. PLANNING_FALLACY: Underestimating time and resources needed
    10. STATUS_QUO_BIAS: Preference for current state of affairs
    11. HINDSIGHT_BIAS: Believing past events were predictable
    12. FRAMING_EFFECT: Being influenced by how information is presented
    13. BANDWAGON_EFFECT: Following the crowd
    14. DUNNING_KRUGER_EFFECT: Incompetent individuals overestimating ability
    15. HALO_EFFECT: One positive trait influencing overall perception

    For each bias identified:
    - Provide specific evidence from the decision process
    - Assess severity of impact (0-1)
    - Estimate likelihood of occurrence (0-1)
    - Suggest concrete mitigation strategies
    - Explain impact on decision quality
    - Rate detection confidence (0-1)

    Consider:
    - Individual vs. group biases
    - Cultural and organizational influences
    - Time pressure effects
    - Information availability constraints
    - Power dynamics and hierarchy

    USER:
    Analyze potential cognitive biases in this decision:

    Decision Context: {decision_context}
    Decision Process: {decision_process}
    Information Sources: {information_sources}
    Decision Makers: {decision_makers}

    Identify biases and provide mitigation strategies.
    """
)
def analyze_cognitive_biases(
    decision_context: DecisionContext,
    decision_process: str,
    information_sources: str = "",
    decision_makers: str = ""
) -> BaseDynamicConfig:
    """Analyze potential cognitive biases affecting the decision."""
    return {
        "computed_fields": {
            "decision_context": decision_context,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=DecisionFramework,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert in decision science and organizational strategy.
    Your role is to recommend the most appropriate decision-making framework
    based on the specific context and requirements of the decision.

    Available Frameworks:
    - Rational Decision Making: Systematic analysis of alternatives
    - Intuitive Decision Making: Experience-based rapid decisions
    - Recognition-Primed Decision: Pattern matching for experts
    - Vroom-Yetton Model: Determining level of participation
    - Cynefin Framework: Matching approach to problem complexity
    - OODA Loop: Rapid iterative decision cycles
    - Six Thinking Hats: Multiple perspective analysis
    - Cost-Benefit Analysis: Quantitative comparison
    - SWOT Analysis: Strengths, weaknesses, opportunities, threats
    - Decision Matrix: Multi-criteria weighted scoring
    - Scenario Planning: Multiple future scenarios
    - Real Options: Preserving flexibility
    - Game Theory: Strategic interaction analysis

    Consider:
    1. Decision complexity and uncertainty
    2. Time constraints and urgency
    3. Available information and resources
    4. Stakeholder involvement needs
    5. Reversibility and flexibility requirements
    6. Organizational culture and capabilities

    USER:
    Recommend a decision framework for:

    Decision Context: {decision_context}
    Quality Assessment: {quality_assessment}
    Key Challenges: {key_challenges}

    Provide framework recommendation with implementation guidance.
    """
)
def recommend_decision_framework(
    decision_context: DecisionContext,
    quality_assessment: list[QualityAssessment],
    key_challenges: str = ""
) -> BaseDynamicConfig:
    """Recommend appropriate decision-making framework."""
    return {
        "computed_fields": {
            "decision_context": decision_context,
            "quality_assessment": quality_assessment,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=DecisionQuality,
)
@prompt_template(
    """
    SYSTEM:
    You are a senior decision quality consultant with expertise in strategic
    decision-making, organizational psychology, and change management.
    Your role is to synthesize all decision analysis components into a
    comprehensive quality assessment with actionable recommendations.

    Consider:
    1. Overall decision quality across all dimensions
    2. Critical strengths to leverage
    3. Critical weaknesses to address urgently
    4. Impact of identified biases
    5. Quality of alternatives analysis
    6. Decision readiness assessment
    7. Implementation considerations
    8. Risk mitigation strategies
    9. Stakeholder alignment
    10. Long-term implications

    Provide:
    - Overall quality score (0-1) with justification
    - Decision readiness score (0-1)
    - Key strengths and weaknesses
    - Prioritized recommendations
    - Specific action items with owners
    - Confidence level in assessment
    - Framework implementation guidance

    Focus on:
    - Actionable insights over theoretical analysis
    - Risk-adjusted recommendations
    - Cultural and organizational fit
    - Implementation feasibility
    - Quick wins vs. long-term improvements

    USER:
    Synthesize the complete decision quality assessment:

    Decision: {decision}
    Context Analysis: {context_analysis}
    Alternatives Analysis: {alternatives_analysis}
    Quality Assessments: {quality_assessments}
    Bias Analysis: {bias_analysis}

    Provide comprehensive decision quality assessment with recommendations.
    """
)
def synthesize_decision_quality(
    decision: str,
    context_analysis: DecisionContext,
    alternatives_analysis: list[DecisionAnalysis],
    quality_assessments: list[QualityAssessment],
    bias_analysis: list[BiasAnalysis]
) -> BaseDynamicConfig:
    """Synthesize complete decision quality assessment."""
    return {
        "computed_fields": {
            "context_analysis": context_analysis,
            "alternatives_analysis": alternatives_analysis,
            "quality_assessments": quality_assessments,
            "bias_analysis": bias_analysis,
        }
    }


async def decision_quality_assessor(
    decision: str,
    background: str = "",
    alternatives: list[str] = None,
    stakeholders: str = "",
    constraints: str = "",
    timeline: str = "",
    decision_process: str = "",
    evaluation_criteria: str = "",
    information_sources: str = "",
    decision_makers: str = "",
    llm_provider: str = "openai",
    model: str = "gpt-4o"
) -> DecisionQuality:
    """
    Assess the quality of decisions using structured analysis and bias detection.

    This agent analyzes decision context, evaluates alternatives, assesses quality
    across multiple dimensions, identifies cognitive biases, recommends frameworks,
    and provides comprehensive improvement recommendations.

    Args:
        decision: The decision to be assessed
        background: Background context and information
        alternatives: List of alternatives being considered
        stakeholders: Key stakeholders involved
        constraints: Constraints and limitations
        timeline: Timeline and urgency factors
        decision_process: Description of the decision-making process
        evaluation_criteria: Criteria for evaluating alternatives
        information_sources: Sources of information used
        decision_makers: People involved in making the decision
        llm_provider: LLM provider to use
        model: Model to use for assessment

    Returns:
        DecisionQuality with comprehensive assessment and recommendations
    """

    if alternatives is None:
        alternatives = ["Current proposal", "Alternative approach", "Status quo"]

    # Step 1: Analyze decision context
    print("Analyzing decision context...")
    context = await analyze_decision_context(
        decision=decision,
        background=background,
        stakeholders=stakeholders,
        constraints=constraints,
        timeline=timeline
    )
    print(f"Context analysis complete - Type: {context.decision_type.value}")

    # Step 2: Analyze alternatives
    print("Analyzing decision alternatives...")
    alternatives_analysis = await analyze_decision_alternatives(
        decision_context=context,
        alternatives=alternatives,
        evaluation_criteria=evaluation_criteria,
        success_metrics=", ".join(context.success_metrics)
    )
    print(f"Analyzed {len(alternatives_analysis)} alternatives")

    # Step 3: Assess quality dimensions
    print("Assessing decision quality dimensions...")
    quality_assessments = await assess_decision_quality_dimensions(
        decision_context=context,
        decision_process=decision_process,
        information_available=background + "\n" + information_sources,
        alternatives_considered=", ".join(alternatives)
    )
    print(f"Assessed {len(quality_assessments)} quality dimensions")

    # Step 4: Analyze cognitive biases
    print("Analyzing cognitive biases...")
    bias_analysis = await analyze_cognitive_biases(
        decision_context=context,
        decision_process=decision_process,
        information_sources=information_sources,
        decision_makers=decision_makers
    )

    # Filter for significant biases
    significant_biases = [b for b in bias_analysis if b.severity > 0.3]
    print(f"Identified {len(significant_biases)} significant biases")

    # Step 5: Recommend decision framework
    print("Recommending decision framework...")

    # Identify key challenges from quality assessments
    key_challenges = []
    for qa in quality_assessments:
        if qa.score < 0.6:
            key_challenges.extend(qa.critical_gaps)

    framework_recommendation = await recommend_decision_framework(
        decision_context=context,
        quality_assessment=quality_assessments,
        key_challenges=", ".join(key_challenges[:5])  # Top 5 challenges
    )

    # Step 6: Synthesize quality assessment
    print("Synthesizing decision quality assessment...")
    quality_assessment = await synthesize_decision_quality(
        decision=decision,
        context_analysis=context,
        alternatives_analysis=alternatives_analysis,
        quality_assessments=quality_assessments,
        bias_analysis=bias_analysis
    )

    # Add framework recommendation
    quality_assessment.framework_recommendation = framework_recommendation

    print("Decision quality assessment complete!")
    return quality_assessment


async def decision_quality_assessor_stream(
    decision: str,
    background: str = "",
    **kwargs
) -> AsyncGenerator[str, None]:
    """Stream the decision quality assessment process."""

    yield "Starting decision quality assessment...\n\n"
    yield f"**Decision:** {decision}\n\n"

    # Perform assessment
    assessment = await decision_quality_assessor(decision, background, **kwargs)

    yield "## Overall Assessment\n\n"
    yield f"**Overall Quality Score:** {assessment.overall_quality_score:.2f}/1.0\n"
    yield f"**Decision Readiness:** {assessment.decision_readiness:.2f}/1.0\n"
    yield f"**Confidence Level:** {assessment.confidence_level:.2f}/1.0\n\n"

    yield "## Decision Context\n\n"
    yield f"**Type:** {assessment.context.decision_type.value}\n"
    yield f"**Timeline:** {assessment.context.timeline}\n"
    yield f"**Risk Tolerance:** {assessment.context.risk_tolerance}\n"
    yield f"**Decision Authority:** {assessment.context.decision_authority}\n\n"

    yield "## Alternatives Analysis\n\n"
    for i, alt in enumerate(assessment.alternatives_analysis, 1):
        yield f"### Alternative {i}: {alt.alternative}\n"
        yield f"**Success Probability:** {alt.success_probability:.2f}\n"
        yield f"**Alignment Score:** {alt.alignment_score:.2f}\n"
        yield f"**Sustainability:** {alt.sustainability_score:.2f}\n"
        yield f"**Implementation:** {alt.implementation_complexity}\n"
        yield f"**Key Pros:** {', '.join(alt.pros[:3])}\n"
        yield f"**Key Risks:** {', '.join(alt.risks[:2])}\n\n"

    yield "## Quality Dimensions\n\n"
    # Sort by score to show weakest areas first
    sorted_assessments = sorted(assessment.quality_assessments, key=lambda x: x.score)
    for qa in sorted_assessments[:5]:  # Show top 5 areas needing attention
        yield f"**{qa.dimension.value.replace('_', ' ').title()}:** {qa.score:.2f}/1.0 ({qa.priority_level} priority)\n"
        if qa.critical_gaps:
            yield f"  - Critical Gap: {qa.critical_gaps[0]}\n"
    yield "\n"

    if assessment.bias_analysis:
        yield "## Cognitive Biases Detected\n\n"
        # Show only significant biases
        significant_biases = sorted(
            [b for b in assessment.bias_analysis if b.severity > 0.3],
            key=lambda x: x.severity,
            reverse=True
        )
        for bias in significant_biases[:3]:
            yield f"**{bias.bias_type.value.replace('_', ' ').title()}**\n"
            yield f"- Severity: {bias.severity:.2f} | Likelihood: {bias.likelihood_of_occurrence:.2f}\n"
            yield f"- Impact: {bias.impact_on_decision}\n"
            yield f"- Mitigation: {bias.mitigation_strategies[0]}\n\n"

    yield "## Recommended Framework\n\n"
    yield f"**Framework:** {assessment.framework_recommendation.recommended_framework}\n"
    yield f"**Rationale:** {assessment.framework_recommendation.framework_rationale}\n"
    yield "**Key Steps:**\n"
    for step in assessment.framework_recommendation.key_steps[:3]:
        yield f"1. {step}\n"
    yield "\n"

    yield "## Key Strengths\n\n"
    for strength in assessment.key_strengths[:3]:
        yield f"- {strength}\n"

    yield "\n## Critical Weaknesses\n\n"
    for weakness in assessment.critical_weaknesses[:3]:
        yield f"- {weakness}\n"

    yield "\n## Top Recommendations\n\n"
    for i, rec in enumerate(assessment.recommendations[:5], 1):
        yield f"{i}. {rec}\n"

    yield "\n## Action Items\n\n"
    for item in assessment.action_items[:5]:
        yield f"- [ ] {item}\n"
