"""
Multi-step reasoning examples using Mirascope.

Multi-step reasoning chains break down complex problems into sequential analytical
steps, enabling deep understanding and sophisticated problem-solving.
"""

import lilypad
from mirascope import llm, prompt_template
from mirascope.core import BaseDynamicConfig
from pydantic import BaseModel, Field

# Multi-step analysis

class ProblemDecomposition(BaseModel):
    """Model for problem decomposition."""

    main_problem: str = Field(..., description="The main problem statement")
    sub_problems: list[str] = Field(..., description="Decomposed sub-problems")
    dependencies: dict[str, list[str]] = Field(..., description="Dependencies between sub-problems")
    solving_order: list[str] = Field(..., description="Optimal order to solve sub-problems")


class SubProblemSolution(BaseModel):
    """Model for sub-problem solutions."""

    sub_problem: str = Field(..., description="The sub-problem")
    solution: str = Field(..., description="Solution to the sub-problem")
    methodology: str = Field(..., description="Methodology used")
    confidence: float = Field(..., ge=0, le=1, description="Solution confidence")


class IntegratedSolution(BaseModel):
    """Model for integrated solutions."""

    problem_statement: str = Field(..., description="Original problem")
    sub_solutions: dict[str, str] = Field(..., description="Solutions to sub-problems")
    integrated_solution: str = Field(..., description="Complete integrated solution")
    key_insights: list[str] = Field(..., description="Key insights from the analysis")
    limitations: list[str] = Field(..., description="Limitations of the solution")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ProblemDecomposition)
@prompt_template(
    """
    Decompose this complex problem into manageable sub-problems:

    Problem: {problem}
    Domain: {domain}

    Identify:
    1. Main problem statement
    2. Sub-problems that need solving
    3. Dependencies between sub-problems
    4. Optimal solving order

    Consider the complexity and interconnections.
    """
)
def decompose_problem(problem: str, domain: str):
    """Decompose complex problem into sub-problems."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=SubProblemSolution)
@prompt_template(
    """
    Solve this sub-problem:

    Sub-problem: {sub_problem}
    Context: Part of larger problem: {main_problem}

    Previous solutions:
    {previous_solutions:lists}

    Dependencies resolved: {dependencies_met}

    Provide detailed solution with methodology.
    """
)
def solve_sub_problem(
    sub_problem: str,
    main_problem: str,
    previous_solutions: list[dict],
    dependencies_met: bool
) -> BaseDynamicConfig:
    """Solve individual sub-problem."""
    formatted_solutions = []
    for sol in previous_solutions:
        formatted_solutions.append([
            f"Sub-problem: {sol['sub_problem']}",
            f"Solution: {sol['solution']}",
            ""
        ])

    return {
        "computed_fields": {
            "previous_solutions": formatted_solutions
        }
    }


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=IntegratedSolution)
@prompt_template(
    """
    Integrate sub-problem solutions into comprehensive solution:

    Original Problem: {problem}

    Sub-problem Solutions:
    {sub_solutions_text:lists}

    Synthesize:
    1. Complete integrated solution
    2. Key insights discovered
    3. Limitations to acknowledge
    """
)
def integrate_solutions(
    problem: str,
    sub_solutions: dict[str, SubProblemSolution]
) -> BaseDynamicConfig:
    """Integrate all sub-solutions."""
    formatted_solutions = []
    for sub_prob, solution in sub_solutions.items():
        formatted_solutions.append([
            f"Sub-problem: {sub_prob}",
            f"Solution: {solution.solution}",
            f"Methodology: {solution.methodology}",
            f"Confidence: {solution.confidence}",
            ""
        ])

    return {
        "computed_fields": {
            "sub_solutions_text": formatted_solutions
        }
    }


def multi_step_analysis(
    problem: str,
    domain: str = "general"
) -> IntegratedSolution:
    """
    Multi-step analytical reasoning for complex problems.

    This demonstrates:
    1. Problem decomposition
    2. Sequential sub-problem solving
    3. Solution integration

    Args:
        problem: Complex problem to solve
        domain: Problem domain

    Returns:
        IntegratedSolution with complete analysis
    """
    # Step 1: Decompose problem
    decomposition = decompose_problem(problem, domain)

    # Step 2: Solve sub-problems in order
    sub_solutions = {}
    previous_solutions: list[dict] = []

    for sub_problem in decomposition.solving_order:
        # Check dependencies
        deps = decomposition.dependencies.get(sub_problem, [])
        dependencies_met = all(dep in sub_solutions for dep in deps)

        # Solve sub-problem
        solution = solve_sub_problem(
            sub_problem=sub_problem,
            main_problem=decomposition.main_problem,
            previous_solutions=previous_solutions,
            dependencies_met=dependencies_met
        )

        sub_solutions[sub_problem] = solution
        previous_solutions.append({
            "sub_problem": sub_problem,
            "solution": solution.solution
        })

    # Step 3: Integrate solutions
    integrated = integrate_solutions(
        problem=problem,
        sub_solutions=sub_solutions
    )

    return integrated


# Multi-step synthesis

class InformationGathering(BaseModel):
    """Model for information gathering results."""

    sources: list[str] = Field(..., description="Information sources identified")
    key_facts: list[str] = Field(..., description="Key facts gathered")
    data_quality: float = Field(..., ge=0, le=1, description="Overall data quality")
    gaps: list[str] = Field(..., description="Information gaps identified")


class PatternAnalysis(BaseModel):
    """Model for pattern analysis."""

    patterns_found: list[str] = Field(..., description="Patterns identified")
    correlations: dict[str, str] = Field(..., description="Correlations between elements")
    anomalies: list[str] = Field(..., description="Anomalies detected")
    significance: dict[str, float] = Field(..., description="Pattern significance scores")


class Synthesis(BaseModel):
    """Model for synthesis results."""

    synthesis: str = Field(..., description="Synthesized understanding")
    supporting_evidence: list[str] = Field(..., description="Supporting evidence")
    new_insights: list[str] = Field(..., description="New insights generated")
    applications: list[str] = Field(..., description="Practical applications")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=InformationGathering)
@prompt_template(
    """
    Gather information for synthesis on topic: {topic}

    Context: {context}
    Focus areas: {focus_areas:list}

    Identify:
    1. Relevant information sources
    2. Key facts to consider
    3. Data quality assessment
    4. Information gaps
    """
)
def gather_information(
    topic: str,
    context: str,
    focus_areas: list[str]
):
    """Gather information for synthesis."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=PatternAnalysis)
@prompt_template(
    """
    Analyze patterns in gathered information:

    Topic: {topic}
    Key Facts: {key_facts:list}

    Identify:
    1. Recurring patterns
    2. Correlations between elements
    3. Anomalies or outliers
    4. Significance of patterns
    """
)
def analyze_patterns(topic: str, key_facts: list[str]):
    """Analyze patterns in information."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=Synthesis)
@prompt_template(
    """
    Synthesize comprehensive understanding:

    Topic: {topic}

    Information gathered:
    - Key facts: {key_facts:list}
    - Information gaps: {gaps:list}

    Patterns identified:
    - Patterns: {patterns:list}
    - Anomalies: {anomalies:list}

    Create synthesis with new insights and applications.
    """
)
def synthesize_understanding(
    topic: str,
    key_facts: list[str],
    gaps: list[str],
    patterns: list[str],
    anomalies: list[str]
):
    """Synthesize final understanding."""
    pass


def multi_step_synthesis(
    topic: str,
    context: str,
    focus_areas: list[str] = None
) -> Synthesis:
    """
    Multi-step synthesis reasoning.

    Features:
    1. Information gathering
    2. Pattern analysis
    3. Insight synthesis

    Args:
        topic: Topic to synthesize understanding
        context: Context for synthesis
        focus_areas: Specific areas to focus on

    Returns:
        Synthesis with comprehensive understanding
    """
    if focus_areas is None:
        focus_areas = ["key concepts", "relationships", "implications"]

    # Step 1: Gather information
    info = gather_information(topic, context, focus_areas)

    # Step 2: Analyze patterns
    patterns = analyze_patterns(topic, info.key_facts)

    # Step 3: Synthesize understanding
    synthesis = synthesize_understanding(
        topic=topic,
        key_facts=info.key_facts,
        gaps=info.gaps,
        patterns=patterns.patterns_found,
        anomalies=patterns.anomalies
    )

    return synthesis


# Multi-step decision making

class DecisionCriteria(BaseModel):
    """Model for decision criteria."""

    criteria: list[str] = Field(..., description="Decision criteria identified")
    weights: dict[str, float] = Field(..., description="Criteria weights")
    thresholds: dict[str, float] = Field(..., description="Minimum thresholds")


class OptionEvaluation(BaseModel):
    """Model for option evaluation."""

    option: str = Field(..., description="Option being evaluated")
    scores: dict[str, float] = Field(..., description="Scores per criterion")
    pros: list[str] = Field(..., description="Advantages")
    cons: list[str] = Field(..., description="Disadvantages")
    overall_score: float = Field(..., description="Weighted overall score")


class Decision(BaseModel):
    """Model for final decision."""

    selected_option: str = Field(..., description="Selected option")
    rationale: str = Field(..., description="Decision rationale")
    confidence: float = Field(..., ge=0, le=1, description="Decision confidence")
    risks: list[str] = Field(..., description="Identified risks")
    mitigation_strategies: list[str] = Field(..., description="Risk mitigation strategies")


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=DecisionCriteria)
@prompt_template(
    """
    Establish decision criteria for: {decision_context}

    Constraints: {constraints:list}
    Goals: {goals:list}

    Define:
    1. Relevant criteria
    2. Importance weights (0-1)
    3. Minimum acceptable thresholds
    """
)
def establish_criteria(
    decision_context: str,
    constraints: list[str],
    goals: list[str]
):
    """Establish decision criteria."""
    pass


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=OptionEvaluation)
@prompt_template(
    """
    Evaluate option against criteria:

    Option: {option}
    Decision Context: {decision_context}

    Criteria and weights:
    {criteria_weights:lists}

    Score each criterion and calculate overall score.
    """
)
def evaluate_option(
    option: str,
    decision_context: str,
    criteria: DecisionCriteria
) -> BaseDynamicConfig:
    """Evaluate single option."""
    criteria_weights = []
    for criterion, weight in criteria.weights.items():
        threshold = criteria.thresholds.get(criterion, 0)
        criteria_weights.append([
            f"- {criterion}: weight={weight}, threshold={threshold}"
        ])

    return {
        "computed_fields": {
            "criteria_weights": criteria_weights
        }
    }


@lilypad.trace(versioning="automatic")
@llm.call(provider="openai", model="gpt-4o-mini", response_model=Decision)
@prompt_template(
    """
    Make final decision based on evaluations:

    Decision Context: {decision_context}

    Option Evaluations:
    {evaluations_text:lists}

    Select best option with rationale, confidence, and risk analysis.
    """
)
def make_final_decision(
    decision_context: str,
    evaluations: list[OptionEvaluation]
) -> BaseDynamicConfig:
    """Make final decision."""
    evaluations_text = []
    for eval in evaluations:
        evaluations_text.append([
            f"Option: {eval.option}",
            f"Overall Score: {eval.overall_score}",
            f"Pros: {', '.join(eval.pros)}",
            f"Cons: {', '.join(eval.cons)}",
            ""
        ])

    return {
        "computed_fields": {
            "evaluations_text": evaluations_text
        }
    }


def multi_step_decision(
    decision_context: str,
    options: list[str],
    constraints: list[str] = None,
    goals: list[str] = None
) -> Decision:
    """
    Multi-step decision making process.

    Features:
    1. Criteria establishment
    2. Systematic evaluation
    3. Risk-aware decision

    Args:
        decision_context: Context for decision
        options: Available options
        constraints: Decision constraints
        goals: Decision goals

    Returns:
        Decision with full analysis
    """
    if constraints is None:
        constraints = []
    if goals is None:
        goals = ["maximize value", "minimize risk"]

    # Step 1: Establish criteria
    criteria = establish_criteria(decision_context, constraints, goals)

    # Step 2: Evaluate each option
    evaluations = []
    for option in options:
        evaluation = evaluate_option(option, decision_context, criteria)
        evaluations.append(evaluation)

    # Step 3: Make decision
    decision = make_final_decision(decision_context, evaluations)

    return decision
