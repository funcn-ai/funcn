from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Optional


class GameType(str, Enum):
    """Types of game theory scenarios."""
    ZERO_SUM = "zero_sum"
    NON_ZERO_SUM = "non_zero_sum"
    COOPERATIVE = "cooperative"
    NON_COOPERATIVE = "non_cooperative"
    SEQUENTIAL = "sequential"
    SIMULTANEOUS = "simultaneous"
    REPEATED = "repeated"
    AUCTION = "auction"
    BARGAINING = "bargaining"
    VOTING = "voting"
    EVOLUTIONARY = "evolutionary"


class StrategyType(str, Enum):
    """Types of strategies in game theory."""
    DOMINANT = "dominant"
    DOMINATED = "dominated"
    NASH_EQUILIBRIUM = "nash_equilibrium"
    MIXED = "mixed"
    PURE = "pure"
    MINIMAX = "minimax"
    MAXIMIN = "maximin"
    TIT_FOR_TAT = "tit_for_tat"
    COOPERATIVE = "cooperative"
    GRIM_TRIGGER = "grim_trigger"
    EVOLUTIONARY_STABLE = "evolutionary_stable"


class PlayerProfile(BaseModel):
    """Profile of a player in the game."""
    name: str = Field(..., description="Player identifier")
    objectives: list[str] = Field(..., description="Player's primary objectives")
    constraints: list[str] = Field(..., description="Constraints or limitations")
    risk_tolerance: str = Field(..., description="Risk tolerance level (low/medium/high)")
    information_level: str = Field(..., description="Level of information available")
    bargaining_power: float = Field(..., description="Relative bargaining power (0-1)")
    historical_behavior: str = Field(..., description="Past behavior patterns")
    resources: str = Field(default="", description="Available resources")
    time_preference: str = Field(default="neutral", description="Time preference (patient/neutral/impatient)")


class GameStrategy(BaseModel):
    """A strategy available to a player."""
    strategy_name: str = Field(..., description="Name of the strategy")
    description: str = Field(..., description="Detailed description of the strategy")
    strategy_type: StrategyType = Field(..., description="Type of strategy")
    conditions: list[str] = Field(..., description="Conditions when this strategy is optimal")
    expected_payoff: str = Field(..., description="Expected payoff or outcome")
    risks: list[str] = Field(..., description="Potential risks or downsides")
    counter_strategies: list[str] = Field(..., description="Potential counter-strategies")
    implementation_requirements: list[str] = Field(default_factory=list, description="Requirements to implement")


class GameOutcome(BaseModel):
    """Possible outcome of the game."""
    outcome_name: str = Field(..., description="Name of the outcome")
    probability: float = Field(..., description="Probability of this outcome (0-1)")
    player_payoffs: dict[str, str] = Field(..., description="Payoffs for each player")
    stability: str = Field(..., description="Stability of this outcome")
    efficiency: str = Field(..., description="Pareto efficiency assessment")
    conditions: list[str] = Field(..., description="Conditions leading to this outcome")
    social_welfare: str = Field(default="", description="Impact on overall social welfare")
    fairness_assessment: str = Field(default="", description="Fairness of the outcome")


class GameScenario(BaseModel):
    """Complete game scenario definition."""
    scenario_name: str = Field(..., description="Name of the game scenario")
    game_type: GameType = Field(..., description="Type of game")
    description: str = Field(..., description="Detailed scenario description")
    players: list[PlayerProfile] = Field(..., description="Players in the game")
    rules: list[str] = Field(..., description="Rules and constraints of the game")
    information_structure: str = Field(..., description="Information available to players")
    payoff_structure: str = Field(..., description="How payoffs are determined")
    time_horizon: str = Field(..., description="Single round, repeated, or infinite")
    external_factors: list[str] = Field(default_factory=list, description="External factors affecting the game")
    real_world_context: str = Field(default="", description="Real-world context or application")


class GameAnalysis(BaseModel):
    """Complete game theory analysis."""
    scenario: GameScenario = Field(..., description="The game scenario analyzed")
    available_strategies: dict[str, list[GameStrategy]] = Field(
        ..., description="Strategies available to each player"
    )
    equilibrium_analysis: list[str] = Field(..., description="Nash equilibria and other solution concepts")
    predicted_outcomes: list[GameOutcome] = Field(..., description="Likely outcomes with probabilities")
    strategic_recommendations: dict[str, list[str]] = Field(
        ..., description="Strategic recommendations for each player"
    )
    sensitivity_analysis: list[str] = Field(..., description="How outcomes change with parameter changes")
    real_world_applications: list[str] = Field(..., description="Real-world applications and examples")
    limitations: list[str] = Field(..., description="Limitations of the analysis")
    policy_implications: list[str] = Field(default_factory=list, description="Policy recommendations if applicable")
    ethical_considerations: list[str] = Field(default_factory=list, description="Ethical aspects to consider")


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=GameScenario,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert game theorist. Your role is to analyze and structure game theory
    scenarios, identifying key players, rules, information structures, and payoff mechanisms.

    Consider:
    1. Clearly define all players and their objectives
    2. Identify the type of game (zero-sum, cooperative, etc.)
    3. Specify information available to each player
    4. Define the rules and constraints
    5. Clarify the payoff structure and time horizon
    6. Consider external factors and real-world context

    Game Types:
    - ZERO_SUM: One player's gain equals another's loss
    - NON_ZERO_SUM: Players can have mutual gains or losses
    - COOPERATIVE: Players can form binding agreements
    - NON_COOPERATIVE: No binding agreements possible
    - SEQUENTIAL: Players move in turns
    - SIMULTANEOUS: Players move at the same time
    - REPEATED: Game played multiple times
    - AUCTION: Bidding mechanism
    - BARGAINING: Negotiation over resource division
    - VOTING: Collective decision making
    - EVOLUTIONARY: Strategy evolution over time

    USER:
    Analyze and structure this game theory scenario:

    Situation: {situation}
    Context: {context}
    Stakeholders: {stakeholders}
    Objectives: {objectives}

    Provide a complete game scenario structure with all key elements defined.
    """
)
def structure_game_scenario(
    situation: str,
    context: str = "",
    stakeholders: str = "",
    objectives: str = ""
) -> GameScenario:
    """Structure and define the game theory scenario."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=dict[str, list[GameStrategy]],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert strategic analyst. Your role is to identify and analyze all
    possible strategies available to each player in a game theory scenario.

    Consider:
    1. Pure strategies (deterministic actions)
    2. Mixed strategies (probabilistic combinations)
    3. Dominant and dominated strategies
    4. Conditional strategies based on opponent actions
    5. Cooperative vs. non-cooperative strategies
    6. Implementation requirements and feasibility

    Strategy Types:
    - DOMINANT: Always optimal regardless of opponent actions
    - DOMINATED: Never optimal, always inferior to another strategy
    - NASH_EQUILIBRIUM: Best response to opponent's strategy
    - MIXED: Randomized combination of pure strategies
    - PURE: Single deterministic action
    - MINIMAX: Minimize maximum possible loss
    - MAXIMIN: Maximize minimum guaranteed payoff
    - TIT_FOR_TAT: Copy opponent's previous action
    - COOPERATIVE: Strategies involving collaboration
    - GRIM_TRIGGER: Cooperate until defection, then always defect
    - EVOLUTIONARY_STABLE: Resistant to invasion by mutant strategies

    USER:
    Identify strategies for each player in this game:

    Game Scenario: {game_scenario}
    Player Profiles: {player_profiles}
    Game Rules: {game_rules}
    Payoff Structure: {payoff_structure}

    Provide comprehensive strategy analysis for each player with detailed descriptions.
    """
)
def analyze_player_strategies(
    game_scenario: GameScenario,
    player_profiles: list[PlayerProfile],
    game_rules: list[str],
    payoff_structure: str
) -> BaseDynamicConfig:
    """Analyze available strategies for each player."""
    return {
        "computed_fields": {
            "game_scenario": game_scenario,
            "player_profiles": player_profiles,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[str],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert in game theory equilibrium analysis. Your role is to identify
    and analyze Nash equilibria and other solution concepts in game theory scenarios.

    Consider:
    1. Nash Equilibrium: No player can improve by unilaterally changing strategy
    2. Subgame Perfect Equilibrium: Nash equilibrium in every subgame
    3. Pareto Optimal outcomes: No outcome makes all players better off
    4. Dominant Strategy Equilibrium: All players play dominant strategies
    5. Mixed Strategy Equilibrium: Players randomize over strategies
    6. Evolutionary Stable Strategies: Strategies that resist invasion
    7. Correlated Equilibrium: Players coordinate through signals
    8. Bayesian Nash Equilibrium: Equilibrium with incomplete information

    Analysis should include:
    - Existence and uniqueness of equilibria
    - Stability and efficiency properties
    - Comparative statics
    - Robustness to parameter changes
    - Refinements and selection criteria

    USER:
    Analyze equilibria for this game:

    Game Scenario: {game_scenario}
    Player Strategies: {player_strategies}
    Payoff Matrix/Function: {payoff_structure}
    Information Structure: {information_structure}

    Provide detailed equilibrium analysis with mathematical reasoning where applicable.
    """
)
def analyze_equilibria(
    game_scenario: GameScenario,
    player_strategies: dict[str, list[GameStrategy]],
    payoff_structure: str,
    information_structure: str
) -> BaseDynamicConfig:
    """Analyze Nash equilibria and other solution concepts."""
    return {
        "computed_fields": {
            "game_scenario": game_scenario,
            "player_strategies": player_strategies,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[GameOutcome],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert in game theory outcome prediction. Your role is to predict
    likely outcomes of game theory scenarios based on equilibrium analysis and
    behavioral considerations.

    Consider:
    1. Equilibrium outcomes and their likelihood
    2. Behavioral factors that might deviate from pure rationality
    3. Learning and adaptation over repeated play
    4. Coordination problems and focal points
    5. Risk preferences and bounded rationality
    6. Social preferences (fairness, reciprocity, altruism)
    7. Communication and signaling effects

    For each outcome, assess:
    - Probability of occurrence
    - Payoffs for each player
    - Stability (resistance to deviations)
    - Efficiency (Pareto optimality)
    - Conditions that lead to this outcome
    - Social welfare implications
    - Fairness considerations

    USER:
    Predict outcomes for this game:

    Game Scenario: {game_scenario}
    Equilibrium Analysis: {equilibrium_analysis}
    Player Characteristics: {player_characteristics}
    Environmental Factors: {environmental_factors}

    Provide probabilistic outcome predictions with detailed reasoning.
    """
)
def predict_game_outcomes(
    game_scenario: GameScenario,
    equilibrium_analysis: list[str],
    player_characteristics: str,
    environmental_factors: str = ""
) -> BaseDynamicConfig:
    """Predict likely game outcomes with probabilities."""
    return {
        "computed_fields": {
            "game_scenario": game_scenario,
            "equilibrium_analysis": equilibrium_analysis,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=GameAnalysis,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert game theory consultant. Your role is to synthesize all game
    theory analysis into actionable strategic recommendations and insights.

    Consider:
    1. Strategic recommendations for each player
    2. Sensitivity analysis for key parameters
    3. Real-world applications and examples
    4. Limitations and assumptions of the analysis
    5. Policy implications if applicable
    6. Ethical considerations
    7. Implementation challenges
    8. Monitoring and adaptation strategies

    Provide:
    - Clear strategic guidance for each player
    - Robustness analysis
    - Practical implementation considerations
    - Connections to real-world scenarios
    - Limitations and caveats
    - Policy recommendations where relevant
    - Ethical implications

    USER:
    Synthesize the complete game theory analysis:

    Game Scenario: {game_scenario}
    Player Strategies: {player_strategies}
    Equilibrium Analysis: {equilibrium_analysis}
    Predicted Outcomes: {predicted_outcomes}
    Context: {context}

    Provide comprehensive analysis with strategic recommendations and insights.
    """
)
def synthesize_game_analysis(
    game_scenario: GameScenario,
    player_strategies: dict[str, list[GameStrategy]],
    equilibrium_analysis: list[str],
    predicted_outcomes: list[GameOutcome],
    context: str = ""
) -> BaseDynamicConfig:
    """Synthesize complete game theory analysis."""
    return {
        "computed_fields": {
            "game_scenario": game_scenario,
            "player_strategies": player_strategies,
            "equilibrium_analysis": equilibrium_analysis,
            "predicted_outcomes": predicted_outcomes,
        }
    }


async def game_theory_analyzer(
    situation: str,
    context: str = "",
    stakeholders: str = "",
    objectives: str = "",
    environmental_factors: str = "",
    llm_provider: str = "openai",
    model: str = "gpt-4o"
) -> GameAnalysis:
    """
    Analyze complex situations using game theory principles and solution concepts.

    This agent structures scenarios as formal games, identifies player strategies,
    analyzes equilibria, predicts outcomes, and provides strategic recommendations.

    Args:
        situation: The situation or conflict to analyze
        context: Additional context about the situation
        stakeholders: Key stakeholders and their roles
        objectives: Objectives and goals of different parties
        environmental_factors: External factors affecting the game
        llm_provider: LLM provider to use
        model: Model to use for analysis

    Returns:
        GameAnalysis with complete strategic analysis and recommendations
    """

    # Step 1: Structure the game scenario
    print("Structuring game scenario...")
    game_scenario = await structure_game_scenario(
        situation=situation,
        context=context,
        stakeholders=stakeholders,
        objectives=objectives
    )
    print(f"Identified {game_scenario.game_type.value} game with {len(game_scenario.players)} players")

    # Step 2: Analyze player strategies
    print("Analyzing player strategies...")
    player_strategies = await analyze_player_strategies(
        game_scenario=game_scenario,
        player_profiles=game_scenario.players,
        game_rules=game_scenario.rules,
        payoff_structure=game_scenario.payoff_structure
    )
    total_strategies = sum(len(strategies) for strategies in player_strategies.values())
    print(f"Identified {total_strategies} total strategies across all players")

    # Step 3: Analyze equilibria
    print("Analyzing equilibria...")
    equilibrium_analysis = await analyze_equilibria(
        game_scenario=game_scenario,
        player_strategies=player_strategies,
        payoff_structure=game_scenario.payoff_structure,
        information_structure=game_scenario.information_structure
    )
    print(f"Found {len(equilibrium_analysis)} equilibrium concepts")

    # Step 4: Predict outcomes
    print("Predicting outcomes...")
    player_chars = "\n".join([
        f"{p.name}: Risk tolerance={p.risk_tolerance}, Bargaining power={p.bargaining_power}"
        for p in game_scenario.players
    ])

    predicted_outcomes = await predict_game_outcomes(
        game_scenario=game_scenario,
        equilibrium_analysis=equilibrium_analysis,
        player_characteristics=player_chars,
        environmental_factors=environmental_factors
    )
    print(f"Predicted {len(predicted_outcomes)} possible outcomes")

    # Step 5: Synthesize complete analysis
    print("Synthesizing analysis...")
    complete_analysis = await synthesize_game_analysis(
        game_scenario=game_scenario,
        player_strategies=player_strategies,
        equilibrium_analysis=equilibrium_analysis,
        predicted_outcomes=predicted_outcomes,
        context=context
    )

    print("Game theory analysis complete!")
    return complete_analysis


async def game_theory_analyzer_stream(
    situation: str,
    context: str = "",
    **kwargs
) -> AsyncGenerator[str, None]:
    """Stream the game theory analysis process."""

    yield "Starting game theory analysis...\n\n"
    yield f"**Situation:** {situation}\n"
    if context:
        yield f"**Context:** {context}\n"
    yield "\n"

    # Perform the analysis
    analysis = await game_theory_analyzer(situation, context, **kwargs)

    yield f"## Game Scenario: {analysis.scenario.scenario_name}\n\n"
    yield f"**Type:** {analysis.scenario.game_type.value.replace('_', ' ').title()}\n"
    yield f"**Description:** {analysis.scenario.description}\n"
    yield f"**Time Horizon:** {analysis.scenario.time_horizon}\n\n"

    yield f"## Players ({len(analysis.scenario.players)})\n\n"
    for player in analysis.scenario.players:
        yield f"### {player.name}\n"
        yield f"- **Objectives:** {', '.join(player.objectives[:2])}\n"
        yield f"- **Risk Tolerance:** {player.risk_tolerance}\n"
        yield f"- **Bargaining Power:** {player.bargaining_power:.2f}\n"
        yield f"- **Information Level:** {player.information_level}\n\n"

    yield "## Strategic Analysis\n\n"
    for player_name, strategies in analysis.available_strategies.items():
        yield f"### {player_name} Strategies\n"
        for i, strategy in enumerate(strategies[:3], 1):  # Show first 3 strategies
            yield f"{i}. **{strategy.strategy_name}** ({strategy.strategy_type.value})\n"
            yield f"   - {strategy.description}\n"
            yield f"   - Expected Payoff: {strategy.expected_payoff}\n"
        if len(strategies) > 3:
            yield f"   - ... and {len(strategies) - 3} more strategies\n"
        yield "\n"

    yield "## Equilibrium Analysis\n\n"
    for i, equilibrium in enumerate(analysis.equilibrium_analysis[:5], 1):
        yield f"{i}. {equilibrium}\n"
    if len(analysis.equilibrium_analysis) > 5:
        yield f"... and {len(analysis.equilibrium_analysis) - 5} more equilibrium concepts\n"
    yield "\n"

    yield "## Predicted Outcomes\n\n"
    for outcome in sorted(analysis.predicted_outcomes, key=lambda x: x.probability, reverse=True)[:3]:
        yield f"### {outcome.outcome_name} (Probability: {outcome.probability:.2%})\n"
        yield f"- **Stability:** {outcome.stability}\n"
        yield f"- **Efficiency:** {outcome.efficiency}\n"
        yield f"- **Social Welfare:** {outcome.social_welfare}\n"
        yield "- **Player Payoffs:**\n"
        for player_name, payoff in outcome.player_payoffs.items():
            yield f"  - {player_name}: {payoff}\n"
        yield "\n"

    yield "## Strategic Recommendations\n\n"
    for player_name, recommendations in analysis.strategic_recommendations.items():
        yield f"### {player_name}\n"
        for rec in recommendations[:3]:
            yield f"- {rec}\n"
        if len(recommendations) > 3:
            yield f"- ... and {len(recommendations) - 3} more recommendations\n"
        yield "\n"

    if analysis.policy_implications:
        yield "## Policy Implications\n\n"
        for implication in analysis.policy_implications:
            yield f"- {implication}\n"
        yield "\n"

    if analysis.real_world_applications:
        yield "## Real-World Applications\n\n"
        for app in analysis.real_world_applications[:3]:
            yield f"- {app}\n"
        yield "\n"

    yield "## Limitations\n\n"
    for limitation in analysis.limitations[:3]:
        yield f"- {limitation}\n"
