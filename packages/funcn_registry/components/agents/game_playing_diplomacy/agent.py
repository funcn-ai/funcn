from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Optional


class DiplomacyPower(str, Enum):
    """The seven Great Powers in Diplomacy."""

    AUSTRIA = "Austria-Hungary"
    ENGLAND = "England"
    FRANCE = "France"
    GERMANY = "Germany"
    ITALY = "Italy"
    RUSSIA = "Russia"
    TURKEY = "Turkey"


class DiplomacyPhase(str, Enum):
    """Game phases in Diplomacy."""

    SPRING_DIPLOMACY = "spring_diplomacy"
    SPRING_ORDERS = "spring_orders"
    SPRING_RETREATS = "spring_retreats"
    FALL_DIPLOMACY = "fall_diplomacy"
    FALL_ORDERS = "fall_orders"
    FALL_RETREATS = "fall_retreats"
    WINTER_BUILDS = "winter_builds"


class UnitType(str, Enum):
    """Types of units in Diplomacy."""

    ARMY = "army"
    FLEET = "fleet"


class OrderType(str, Enum):
    """Types of orders in Diplomacy."""

    HOLD = "hold"
    MOVE = "move"
    SUPPORT = "support"
    CONVOY = "convoy"
    BUILD = "build"
    DISBAND = "disband"
    RETREAT = "retreat"


class PlayerType(str, Enum):
    """Types of players."""

    HUMAN = "human"
    AI = "ai"


class DiplomacyUnit(BaseModel):
    """A military unit in Diplomacy."""

    unit_type: UnitType = Field(..., description="Type of unit (army or fleet)")
    location: str = Field(..., description="Current location/province")
    power: DiplomacyPower = Field(..., description="Controlling power")
    can_retreat_to: list[str] = Field(default_factory=list, description="Valid retreat locations")


class DiplomacyOrder(BaseModel):
    """An order for a unit."""

    unit_location: str = Field(..., description="Location of the unit")
    order_type: OrderType = Field(..., description="Type of order")
    destination: str | None = Field(None, description="Destination for move/retreat")
    target_unit: str | None = Field(None, description="Unit being supported")
    target_destination: str | None = Field(None, description="Destination being supported to")
    via_convoy: list[str] | None = Field(None, description="Convoy route")


class DiplomacyMessage(BaseModel):
    """A diplomatic message between powers."""

    from_power: DiplomacyPower = Field(..., description="Sending power")
    to_power: DiplomacyPower = Field(..., description="Receiving power")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When sent")
    is_public: bool = Field(default=False, description="Whether message is public")


class DiplomacyPlayer(BaseModel):
    """A player in the game."""

    power: DiplomacyPower = Field(..., description="Which power they control")
    player_type: PlayerType = Field(..., description="Human or AI")
    model: str | None = Field(None, description="AI model if AI player")
    provider: str | None = Field(None, description="AI provider if AI player")
    personality: str | None = Field(None, description="AI personality traits")
    strategy_style: str | None = Field(None, description="Preferred strategy style")


class ProvinceControl(BaseModel):
    """Control status of a province."""

    province: str = Field(..., description="Province name")
    controller: DiplomacyPower | None = Field(None, description="Controlling power")
    has_supply_center: bool = Field(..., description="Whether it's a supply center")
    unit: DiplomacyUnit | None = Field(None, description="Unit in the province")


class DiplomacyState(BaseModel):
    """Current state of the Diplomacy game."""

    year: int = Field(..., description="Current game year")
    phase: DiplomacyPhase = Field(..., description="Current phase")
    provinces: list[ProvinceControl] = Field(..., description="All provinces and control")
    units: list[DiplomacyUnit] = Field(..., description="All units on the board")
    supply_centers: dict[str, int] = Field(..., description="Supply center count per power")
    recent_messages: list[DiplomacyMessage] = Field(..., description="Recent diplomatic messages")
    eliminated_powers: list[DiplomacyPower] = Field(default_factory=list, description="Eliminated powers")


class DiplomacyMove(BaseModel):
    """A complete move including orders and diplomacy."""

    power: DiplomacyPower = Field(..., description="Power making the move")
    orders: list[DiplomacyOrder] = Field(..., description="Military orders")
    messages: list[DiplomacyMessage] = Field(..., description="Diplomatic messages")
    reasoning: str = Field(..., description="Strategic reasoning")
    contingency_plans: list[str] = Field(..., description="Backup plans")


class NegotiationProposal(BaseModel):
    """A negotiation proposal between powers."""

    proposing_power: DiplomacyPower = Field(..., description="Power making proposal")
    target_powers: list[DiplomacyPower] = Field(..., description="Powers involved")
    proposal_type: str = Field(..., description="Type of proposal (alliance, NAP, DMZ, etc.)")
    terms: list[str] = Field(..., description="Specific terms")
    duration: str = Field(..., description="How long the agreement lasts")
    mutual_benefits: list[str] = Field(..., description="Benefits for all parties")
    trust_level: float = Field(..., description="Confidence in agreement (0-1)")


class StrategicAnalysis(BaseModel):
    """Strategic analysis of the game state."""

    power_rankings: dict[str, int] = Field(..., description="Power rankings by strength")
    threat_assessment: dict[str, float] = Field(..., description="Threat level per power (0-1)")
    opportunity_zones: list[str] = Field(..., description="Provinces ripe for expansion")
    defensive_priorities: list[str] = Field(..., description="Provinces to defend")
    alliance_recommendations: list[tuple[str, str]] = Field(..., description="Recommended alliances")
    key_chokepoints: list[str] = Field(..., description="Strategic chokepoints")


class DiplomacyGame(BaseModel):
    """Complete game state and history."""

    game_id: str = Field(..., description="Unique game identifier")
    current_state: DiplomacyState = Field(..., description="Current game state")
    players: list[DiplomacyPlayer] = Field(..., description="All players")
    move_history: list[DiplomacyMove] = Field(..., description="History of all moves")
    active_agreements: list[NegotiationProposal] = Field(..., description="Active diplomatic agreements")
    strategic_analysis: StrategicAnalysis = Field(..., description="Current strategic analysis")


# Diplomacy-specific prompts for different AI personalities
PERSONALITY_PROMPTS = {
    "aggressive": "You are an aggressive Diplomacy player who favors rapid expansion and military solutions.",
    "diplomatic": "You are a diplomatic Diplomacy player who builds coalitions and uses negotiation over force.",
    "defensive": "You are a defensive Diplomacy player who prioritizes security and careful expansion.",
    "opportunistic": "You are an opportunistic Diplomacy player who exploits weaknesses and broken alliances.",
    "balanced": "You are a balanced Diplomacy player who adapts strategy based on the situation.",
}


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=StrategicAnalysis,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert Diplomacy player analyzing the current game state.
    {personality_prompt}

    Diplomacy is a game of negotiation, strategy, and betrayal where seven Great Powers
    vie for control of Europe. Success requires both tactical military planning and
    diplomatic finesse.

    Key Strategic Principles:
    1. Geography is destiny - understand supply lines and chokepoints
    2. Alliances are temporary - all players ultimately compete
    3. Timing is crucial - know when to cooperate and when to betray
    4. Balance of power - prevent any player from growing too strong
    5. Diplomatic leverage - use position to extract concessions

    Analyze the current position considering:
    - Supply center distribution and growth potential
    - Military position and unit placement
    - Diplomatic relationships and trust levels
    - Strategic opportunities and threats
    - Long-term winning paths

    USER:
    Analyze the strategic situation for {power}:

    Current State: {game_state}
    Recent Diplomacy: {recent_messages}
    Active Agreements: {active_agreements}
    Historical Context: {historical_context}

    Provide comprehensive strategic analysis with power rankings, threats, and opportunities.
    """
)
def analyze_strategic_situation(
    power: DiplomacyPower,
    game_state: DiplomacyState,
    recent_messages: list[DiplomacyMessage],
    active_agreements: list[NegotiationProposal],
    historical_context: str = "",
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Analyze the strategic situation for a power."""
    return {
        "computed_fields": {
            "game_state": game_state,
            "recent_messages": recent_messages,
            "active_agreements": active_agreements,
        }
    }


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=list[NegotiationProposal],
)
@prompt_template(
    """
    SYSTEM:
    You are a master Diplomacy negotiator for {power}.
    {personality_prompt}

    Diplomatic Principles:
    1. Trust but verify - agreements need enforcement mechanisms
    2. Mutual benefit - both parties must gain from cooperation
    3. Flexibility - be ready to adapt as situations change
    4. Information warfare - control what others know
    5. Reputation matters - breaking agreements has consequences

    Consider these negotiation tactics:
    - Alliance proposals (temporary cooperation)
    - Non-aggression pacts (NAPs)
    - Demilitarized zones (DMZs)
    - Support agreements (specific military cooperation)
    - Information sharing (intelligence cooperation)
    - Partition agreements (dividing territories)

    USER:
    Develop negotiation proposals for {power}:

    Strategic Analysis: {strategic_analysis}
    Current Relationships: {current_relationships}
    Power Positions: {power_positions}
    Immediate Threats: {immediate_threats}
    Expansion Opportunities: {expansion_opportunities}

    Create specific, actionable negotiation proposals that advance {power}'s interests.
    """
)
def develop_negotiation_strategy(
    power: DiplomacyPower,
    strategic_analysis: StrategicAnalysis,
    current_relationships: str,
    power_positions: str,
    immediate_threats: str,
    expansion_opportunities: str,
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Develop negotiation proposals for diplomatic phase."""
    return {
        "computed_fields": {
            "strategic_analysis": strategic_analysis,
        }
    }


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=list[DiplomacyMessage],
)
@prompt_template(
    """
    SYSTEM:
    You are crafting diplomatic messages for {power} in Diplomacy.
    {personality_prompt}

    Message Crafting Guidelines:
    1. Be specific but not overly committal
    2. Leave room for interpretation and flexibility
    3. Build trust while maintaining strategic ambiguity
    4. Use leverage without appearing threatening
    5. Frame proposals as mutual benefits

    Message Types:
    - Alliance proposals
    - Intelligence sharing
    - Warning messages
    - Reassurances
    - Coordination requests
    - Betrayal justifications

    USER:
    Write diplomatic messages for {power}:

    Negotiation Proposals: {proposals}
    Target Powers: {target_powers}
    Current Phase: {current_phase}
    Relationship Status: {relationship_status}
    Strategic Goals: {strategic_goals}

    Craft persuasive messages that advance {power}'s diplomatic agenda.
    """
)
def craft_diplomatic_messages(
    power: DiplomacyPower,
    proposals: list[NegotiationProposal],
    target_powers: list[DiplomacyPower],
    current_phase: DiplomacyPhase,
    relationship_status: str,
    strategic_goals: str,
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Craft diplomatic messages to other powers."""
    return {
        "computed_fields": {
            "proposals": proposals,
        }
    }


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=list[DiplomacyOrder],
)
@prompt_template(
    """
    SYSTEM:
    You are planning military orders for {power} in Diplomacy.
    {personality_prompt}

    Military Planning Principles:
    1. Concentration of force - mass units for breakthroughs
    2. Supply line security - protect your centers
    3. Mutual support - units should support each other
    4. Flexibility - have contingency plans
    5. Deception - hide true intentions

    Order Types:
    - Hold: Unit stays in place
    - Move: Unit attempts to move to adjacent province
    - Support: Unit supports another unit's move or hold
    - Convoy: Fleet transports army across water

    Consider:
    - Current unit positions and possible moves
    - Enemy unit positions and likely moves
    - Support chains and cutting support
    - Convoy routes and vulnerabilities
    - Stalemate lines and breakthrough points

    USER:
    Plan military orders for {power}:

    Current Units: {current_units}
    Strategic Analysis: {strategic_analysis}
    Diplomatic Agreements: {agreements}
    Expected Enemy Moves: {expected_moves}
    Priority Targets: {priority_targets}

    Provide specific orders for each unit with clear strategic purpose.
    """
)
def plan_military_orders(
    power: DiplomacyPower,
    current_units: list[DiplomacyUnit],
    strategic_analysis: StrategicAnalysis,
    agreements: list[NegotiationProposal],
    expected_moves: str,
    priority_targets: str,
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Plan military orders for the current phase."""
    return {
        "computed_fields": {
            "current_units": current_units,
            "strategic_analysis": strategic_analysis,
            "agreements": agreements,
        }
    }


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=DiplomacyMove,
)
@prompt_template(
    """
    SYSTEM:
    You are synthesizing the complete move for {power} in Diplomacy.
    {personality_prompt}

    Move Synthesis Guidelines:
    1. Ensure orders and diplomacy align strategically
    2. Consider how messages support military plans
    3. Plan for multiple contingencies
    4. Balance short-term gains with long-term position
    5. Maintain plausible deniability for betrayals

    USER:
    Synthesize complete move for {power}:

    Military Orders: {military_orders}
    Diplomatic Messages: {diplomatic_messages}
    Strategic Analysis: {strategic_analysis}
    Current Phase: {current_phase}
    Key Objectives: {key_objectives}

    Create a cohesive move that integrates military and diplomatic actions with clear reasoning.
    """
)
def synthesize_complete_move(
    power: DiplomacyPower,
    military_orders: list[DiplomacyOrder],
    diplomatic_messages: list[DiplomacyMessage],
    strategic_analysis: StrategicAnalysis,
    current_phase: DiplomacyPhase,
    key_objectives: str,
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Synthesize complete move including orders and diplomacy."""
    return {
        "computed_fields": {
            "military_orders": military_orders,
            "diplomatic_messages": diplomatic_messages,
            "strategic_analysis": strategic_analysis,
        }
    }


async def process_human_input(game: DiplomacyGame, human_power: DiplomacyPower, phase: DiplomacyPhase) -> DiplomacyMove:
    """Process human player input for their turn."""
    print(f"\n{human_power.value}'s turn - {phase.value}")
    print("\nCurrent game state:")
    print(f"Year: {game.current_state.year}")
    print(f"Your supply centers: {game.current_state.supply_centers.get(human_power.value, 0)}")

    # Show current units
    your_units = [u for u in game.current_state.units if u.power == human_power]
    print(f"\nYour units ({len(your_units)}):")
    for unit in your_units:
        print(f"  - {unit.unit_type.value} in {unit.location}")

    # Collect orders
    orders = []
    messages = []

    if phase in [DiplomacyPhase.SPRING_DIPLOMACY, DiplomacyPhase.FALL_DIPLOMACY]:
        # Diplomatic phase
        print("\nDiplomatic Phase - Send messages to other powers")
        while True:
            target = input("Send message to (power name or 'done'): ").strip()
            if target.lower() == 'done':
                break
            try:
                target_power = DiplomacyPower(target)
                message = input(f"Message to {target_power.value}: ")
                messages.append(
                    DiplomacyMessage(
                        from_power=human_power, to_power=target_power, message=message, timestamp=datetime.now(), is_public=False
                    )
                )
            except ValueError:
                print("Invalid power name. Try again.")

    elif phase in [DiplomacyPhase.SPRING_ORDERS, DiplomacyPhase.FALL_ORDERS]:
        # Order phase
        print("\nOrder Phase - Issue orders to your units")
        print("Order format examples:")
        print("  - 'A Paris holds' or 'A Paris H'")
        print("  - 'A Paris moves to Burgundy' or 'A Paris - Burgundy'")
        print("  - 'A Paris supports A Burgundy to Munich' or 'A Paris S A Burgundy - Munich'")

        for unit in your_units:
            while True:
                order_str = input(f"Order for {unit.unit_type.value} in {unit.location}: ")
                # Parse order (simplified - in real implementation would be more robust)
                if 'hold' in order_str.lower() or ' h' in order_str.lower():
                    orders.append(
                        DiplomacyOrder(
                            unit_location=unit.location,
                            order_type=OrderType.HOLD,
                            destination=None,
                            target_unit=None,
                            target_destination=None,
                            via_convoy=None,
                        )
                    )
                    break
                elif '-' in order_str or 'move' in order_str.lower():
                    # Extract destination
                    parts = order_str.split('-') if '-' in order_str else order_str.split('to')
                    if len(parts) >= 2:
                        destination = parts[1].strip()
                        orders.append(
                            DiplomacyOrder(
                                unit_location=unit.location,
                                order_type=OrderType.MOVE,
                                destination=destination,
                                target_unit=None,
                                target_destination=None,
                                via_convoy=None,
                            )
                        )
                        break
                elif 'support' in order_str.lower() or ' s ' in order_str.lower():
                    # Simplified support parsing
                    orders.append(
                        DiplomacyOrder(
                            unit_location=unit.location,
                            order_type=OrderType.SUPPORT,
                            destination=None,
                            target_unit=None,
                            target_destination=None,
                            via_convoy=None,
                            # Would parse target unit and destination in full implementation
                        )
                    )
                    break
                else:
                    print("Invalid order format. Please try again.")

    reasoning = input("\nExplain your strategy (optional): ") or "Human player move"

    return DiplomacyMove(power=human_power, orders=orders, messages=messages, reasoning=reasoning, contingency_plans=[])


async def diplomacy_game_agent(
    game_state: DiplomacyState,
    players: list[DiplomacyPlayer],
    game_history: list[DiplomacyMove] = None,
    active_agreements: list[NegotiationProposal] = None,
    game_id: str = "game_001",
    current_phase: DiplomacyPhase = DiplomacyPhase.SPRING_DIPLOMACY,
    llm_provider: str = "openai",
    default_model: str = "gpt-4o",
) -> DiplomacyGame:
    """
    Run a turn of Diplomacy with multiple AI models and human players.

    This agent coordinates different AI models playing different powers, processes
    human input, and manages the complex diplomatic and military interactions.

    Args:
        game_state: Current state of the game
        players: List of players (human and AI with different models)
        game_history: History of previous moves
        active_agreements: Currently active diplomatic agreements
        game_id: Unique game identifier
        current_phase: Current game phase
        llm_provider: Default LLM provider
        default_model: Default model for AI players

    Returns:
        Updated DiplomacyGame with all moves processed
    """

    if game_history is None:
        game_history = []
    if active_agreements is None:
        active_agreements = []

    print(f"\nDiplomacy - Year {game_state.year}, {current_phase.value}")
    print(f"Phase: {current_phase.value}")

    # Process each player's turn
    current_moves = []

    for player in players:
        if player.power in game_state.eliminated_powers:
            continue

        print(f"\nProcessing {player.power.value}'s turn...")

        if player.player_type == PlayerType.HUMAN:
            # Human player input
            move = await process_human_input(
                DiplomacyGame(
                    game_id=game_id,
                    current_state=game_state,
                    players=players,
                    move_history=game_history,
                    active_agreements=active_agreements,
                    strategic_analysis=StrategicAnalysis(
                        power_rankings={},
                        threat_assessment={},
                        opportunity_zones=[],
                        defensive_priorities=[],
                        alliance_recommendations=[],
                        key_chokepoints=[],
                    ),
                ),
                player.power,
                current_phase,
            )
            current_moves.append(move)
        else:
            # AI player with specific model
            model = player.model or default_model
            provider = player.provider or llm_provider
            personality_prompt = PERSONALITY_PROMPTS.get(player.personality or "balanced", PERSONALITY_PROMPTS["balanced"])

            # Step 1: Strategic analysis
            print(f" {player.power.value} analyzing situation...")
            strategic_analysis = await analyze_strategic_situation(
                power=player.power,
                game_state=game_state,
                recent_messages=[
                    m for m in game_state.recent_messages if m.to_power == player.power or m.from_power == player.power
                ],
                active_agreements=[
                    a for a in active_agreements if player.power in a.target_powers or a.proposing_power == player.power
                ],
                historical_context=f"Turn {len(game_history)}",
                personality_prompt=personality_prompt,
                provider=provider,
                model=model,
            )

            # Step 2: Develop negotiation strategy (if diplomatic phase)
            diplomatic_messages = []
            if current_phase in [DiplomacyPhase.SPRING_DIPLOMACY, DiplomacyPhase.FALL_DIPLOMACY]:
                print(f" {player.power.value} planning diplomacy...")
                proposals = await develop_negotiation_strategy(
                    power=player.power,
                    strategic_analysis=strategic_analysis,
                    current_relationships="",  # Would analyze from game history
                    power_positions=str(game_state.supply_centers),
                    immediate_threats=", ".join(strategic_analysis.defensive_priorities[:3]),
                    expansion_opportunities=", ".join(strategic_analysis.opportunity_zones[:3]),
                    personality_prompt=personality_prompt,
                    provider=provider,
                    model=model,
                )

                # Craft messages based on proposals
                if proposals:
                    target_powers = list(set(power for proposal in proposals for power in proposal.target_powers))
                    diplomatic_messages = await craft_diplomatic_messages(
                        power=player.power,
                        proposals=proposals,
                        target_powers=target_powers,
                        current_phase=current_phase,
                        relationship_status="",  # Would analyze from history
                        strategic_goals=", ".join([p.proposal_type for p in proposals]),
                        personality_prompt=personality_prompt,
                        provider=provider,
                        model=model,
                    )

            # Step 3: Plan military orders (if order phase)
            military_orders = []
            if current_phase in [DiplomacyPhase.SPRING_ORDERS, DiplomacyPhase.FALL_ORDERS]:
                print(f"  {player.power.value} planning orders...")
                player_units = [u for u in game_state.units if u.power == player.power]
                if player_units:
                    military_orders = await plan_military_orders(
                        power=player.power,
                        current_units=player_units,
                        strategic_analysis=strategic_analysis,
                        agreements=active_agreements,
                        expected_moves="",  # Would analyze from patterns
                        priority_targets=", ".join(strategic_analysis.opportunity_zones[:3]),
                        personality_prompt=personality_prompt,
                        provider=provider,
                        model=model,
                    )

            # Step 4: Synthesize complete move
            print(f"  {player.power.value} finalizing move...")
            move = await synthesize_complete_move(
                power=player.power,
                military_orders=military_orders,
                diplomatic_messages=diplomatic_messages,
                strategic_analysis=strategic_analysis,
                current_phase=current_phase,
                key_objectives=f"Control {game_state.supply_centers.get(player.power.value, 0) + 1} centers",
                personality_prompt=personality_prompt,
                provider=provider,
                model=model,
            )
            current_moves.append(move)

    # Update game history
    game_history.extend(current_moves)

    # Create updated game state
    updated_game = DiplomacyGame(
        game_id=game_id,
        current_state=game_state,
        players=players,
        move_history=game_history,
        active_agreements=active_agreements,
        strategic_analysis=StrategicAnalysis(
            power_rankings={p.value: game_state.supply_centers.get(p.value, 0) for p in DiplomacyPower},
            threat_assessment={},
            opportunity_zones=[],
            defensive_priorities=[],
            alliance_recommendations=[],
            key_chokepoints=[],
        ),
    )

    print("\nTurn complete!")
    return updated_game


async def diplomacy_game_stream(
    game_state: DiplomacyState, players: list[DiplomacyPlayer], **kwargs
) -> AsyncGenerator[str, None]:
    """Stream the Diplomacy game turn with live updates."""

    yield f"**Diplomacy - Year {game_state.year}**\n\n"
    yield f"**Current Phase:** {kwargs.get('current_phase', DiplomacyPhase.SPRING_DIPLOMACY).value}\n\n"

    yield "## Current Standings\n\n"
    for power in DiplomacyPower:
        if power not in game_state.eliminated_powers:
            centers = game_state.supply_centers.get(power.value, 0)
            player = next((p for p in players if p.power == power), None)
            player_type = player.player_type.value if player else "none"
            yield f"**{power.value}:** {centers} centers ({player_type})\n"
    yield "\n"

    # Run the game turn
    game = await diplomacy_game_agent(game_state, players, **kwargs)

    yield "## Turn Summary\n\n"

    # Show moves for this turn
    current_turn_moves = game.move_history[-len(players) :]
    for move in current_turn_moves:
        yield f"### {move.power.value}\n"
        yield f"**Strategy:** {move.reasoning}\n"

        if move.orders:
            yield "**Orders:**\n"
            for order in move.orders[:3]:  # Show first 3 orders
                if order.order_type == OrderType.MOVE:
                    yield f"- {order.unit_location} → {order.destination}\n"
                elif order.order_type == OrderType.HOLD:
                    yield f"- {order.unit_location} holds\n"
                elif order.order_type == OrderType.SUPPORT:
                    yield f"- {order.unit_location} supports\n"
            if len(move.orders) > 3:
                yield f"- ... and {len(move.orders) - 3} more orders\n"

        if move.messages:
            yield f"**Diplomacy:** Sent {len(move.messages)} messages\n"
        yield "\n"

    yield "## Diplomatic Activity\n\n"
    recent_messages = game.current_state.recent_messages[-5:]
    for msg in recent_messages:
        yield f"- **{msg.from_power.value} → {msg.to_power.value}:** {msg.message[:100]}...\n"

    yield "\n## Next Phase\n\n"
    yield "Ready for next phase. Update game state and continue!\n"
