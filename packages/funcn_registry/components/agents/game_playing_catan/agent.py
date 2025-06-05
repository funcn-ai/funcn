from __future__ import annotations

import asyncio
import random
from collections import defaultdict
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Optional


class Resource(str, Enum):
    """Resources in Catan."""

    WOOD = "wood"
    BRICK = "brick"
    SHEEP = "sheep"
    WHEAT = "wheat"
    ORE = "ore"
    DESERT = "desert"  # No resource


class DevelopmentCard(str, Enum):
    """Development cards in Catan."""

    KNIGHT = "knight"
    VICTORY_POINT = "victory_point"
    ROAD_BUILDING = "road_building"
    YEAR_OF_PLENTY = "year_of_plenty"
    MONOPOLY = "monopoly"


class CatanPhase(str, Enum):
    """Game phases in Catan."""

    SETUP_FIRST_SETTLEMENT = "setup_first_settlement"
    SETUP_FIRST_ROAD = "setup_first_road"
    SETUP_SECOND_SETTLEMENT = "setup_second_settlement"
    SETUP_SECOND_ROAD = "setup_second_road"
    ROLL_DICE = "roll_dice"
    ROBBER_DISCARD = "robber_discard"
    ROBBER_MOVE = "robber_move"
    ROBBER_STEAL = "robber_steal"
    MAIN_TURN = "main_turn"
    TRADE_OFFER = "trade_offer"
    BUILD_PHASE = "build_phase"
    END_TURN = "end_turn"


class BuildingType(str, Enum):
    """Types of buildings in Catan."""

    SETTLEMENT = "settlement"
    CITY = "city"
    ROAD = "road"


class ActionType(str, Enum):
    """Types of actions in Catan."""

    BUILD_SETTLEMENT = "build_settlement"
    BUILD_CITY = "build_city"
    BUILD_ROAD = "build_road"
    BUY_DEVELOPMENT_CARD = "buy_development_card"
    PLAY_DEVELOPMENT_CARD = "play_development_card"
    PROPOSE_TRADE = "propose_trade"
    ACCEPT_TRADE = "accept_trade"
    REJECT_TRADE = "reject_trade"
    MOVE_ROBBER = "move_robber"
    STEAL_FROM_PLAYER = "steal_from_player"
    DISCARD_CARDS = "discard_cards"
    END_TURN = "end_turn"
    ROLL_DICE = "roll_dice"


class PlayerType(str, Enum):
    """Types of players."""

    HUMAN = "human"
    AI = "ai"


class HexTile(BaseModel):
    """A hex tile on the Catan board."""

    position: tuple[int, int] = Field(..., description="Hex coordinates (q, r)")
    resource: Resource = Field(..., description="Resource type of this hex")
    number_token: int | None = Field(None, description="Number token (2-12, None for desert)")
    has_robber: bool = Field(default=False, description="Whether the robber is on this hex")


class Intersection(BaseModel):
    """An intersection where settlements/cities can be built."""

    position: tuple[int, int, int] = Field(..., description="Intersection coordinates")
    building: BuildingType | None = Field(None, description="Building at this intersection")
    owner: int | None = Field(None, description="Player who owns the building")
    adjacent_hexes: list[tuple[int, int]] = Field(..., description="Adjacent hex positions")
    adjacent_edges: list[tuple[tuple[int, int, int], tuple[int, int, int]]] = Field(..., description="Adjacent edges")


class Edge(BaseModel):
    """An edge where roads can be built."""

    start: tuple[int, int, int] = Field(..., description="Start intersection")
    end: tuple[int, int, int] = Field(..., description="End intersection")
    has_road: bool = Field(default=False, description="Whether there's a road")
    owner: int | None = Field(None, description="Player who owns the road")


class TradeOffer(BaseModel):
    """A trade offer between players."""

    proposing_player: int = Field(..., description="Player making the offer")
    target_player: int | None = Field(None, description="Specific target player (None for all)")
    offering: dict[Resource, int] = Field(..., description="Resources being offered")
    requesting: dict[Resource, int] = Field(..., description="Resources being requested")
    timestamp: datetime = Field(..., description="When the offer was made")
    is_bank_trade: bool = Field(default=False, description="Whether this is a bank/port trade")


class CatanPlayer(BaseModel):
    """A player in Catan."""

    player_id: int = Field(..., description="Player ID (0-3)")
    name: str = Field(..., description="Player name")
    player_type: PlayerType = Field(..., description="Human or AI")
    model: str | None = Field(None, description="AI model if AI player")
    provider: str | None = Field(None, description="AI provider if AI player")
    personality: str | None = Field(None, description="AI personality traits")
    resources: dict[Resource, int] = Field(default_factory=lambda: defaultdict(int), description="Resource cards")
    development_cards: list[DevelopmentCard] = Field(default_factory=list, description="Development cards")
    settlements: list[tuple[int, int, int]] = Field(default_factory=list, description="Settlement positions")
    cities: list[tuple[int, int, int]] = Field(default_factory=list, description="City positions")
    roads: list[Edge] = Field(default_factory=list, description="Road positions")
    victory_points: int = Field(default=0, description="Total victory points")
    knights_played: int = Field(default=0, description="Number of knights played")
    longest_road_length: int = Field(default=0, description="Length of longest road")
    has_largest_army: bool = Field(default=False, description="Whether player has largest army")
    has_longest_road: bool = Field(default=False, description="Whether player has longest road")


class CatanState(BaseModel):
    """Current state of the Catan game."""

    board: list[HexTile] = Field(..., description="All hex tiles on the board")
    intersections: list[Intersection] = Field(..., description="All intersections")
    edges: list[Edge] = Field(..., description="All edges")
    current_player: int = Field(..., description="Current player's turn")
    phase: CatanPhase = Field(..., description="Current game phase")
    dice_roll: tuple[int, int] | None = Field(None, description="Last dice roll")
    robber_position: tuple[int, int] = Field(..., description="Current robber position")
    development_cards_remaining: int = Field(default=25, description="Development cards left")
    active_trade_offers: list[TradeOffer] = Field(default_factory=list, description="Active trade offers")
    turn_number: int = Field(default=0, description="Current turn number")
    winner: int | None = Field(None, description="Winner player ID if game ended")


class CatanAction(BaseModel):
    """An action taken by a player."""

    player_id: int = Field(..., description="Player taking the action")
    action_type: ActionType = Field(..., description="Type of action")
    position: tuple[int, int, int] | None = Field(None, description="Position for building")
    edge: tuple[tuple[int, int, int], tuple[int, int, int]] | None = Field(None, description="Edge for road")
    resources: dict[Resource, int] | None = Field(None, description="Resources for trade/discard")
    target_player: int | None = Field(None, description="Target player for stealing")
    development_card: DevelopmentCard | None = Field(None, description="Development card to play")
    trade_offer: TradeOffer | None = Field(None, description="Trade offer details")
    reasoning: str = Field(..., description="Strategic reasoning for the action")


class StrategicAnalysis(BaseModel):
    """Strategic analysis of the game state."""

    resource_scarcity: dict[Resource, float] = Field(..., description="Scarcity score per resource (0-1)")
    player_threats: dict[int, float] = Field(..., description="Threat level per player (0-1)")
    expansion_opportunities: list[tuple[int, int, int]] = Field(..., description="Best expansion spots")
    trade_opportunities: list[str] = Field(..., description="Potential beneficial trades")
    development_card_strategy: str = Field(..., description="When to buy/play development cards")
    blocking_opportunities: list[str] = Field(..., description="Ways to block opponents")
    win_probability: float = Field(..., description="Estimated probability of winning (0-1)")


class CatanGame(BaseModel):
    """Complete game state and history."""

    game_id: str = Field(..., description="Unique game identifier")
    current_state: CatanState = Field(..., description="Current game state")
    players: list[CatanPlayer] = Field(..., description="All players")
    action_history: list[CatanAction] = Field(..., description="History of all actions")
    strategic_analyses: dict[int, StrategicAnalysis] = Field(..., description="Strategic analysis per player")


# Catan-specific prompts for different AI personalities
PERSONALITY_PROMPTS = {
    "builder": "You are a builder-focused Catan player who prioritizes settlements and cities for points.",
    "trader": "You are a trade-focused Catan player who builds a diverse economy through trading.",
    "expansionist": "You are an expansion-focused Catan player who claims territory aggressively.",
    "developer": "You are a development card-focused Catan player who uses cards strategically.",
    "balanced": "You are a balanced Catan player who adapts strategy based on the situation.",
    "blocker": "You are a blocking-focused Catan player who denies resources to opponents.",
}


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=StrategicAnalysis,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert Catan player analyzing the current game state.
    {personality_prompt}

    Catan is a game of resource management, strategic building, and trading where
    players compete to reach 10 victory points through settlements, cities, and bonuses.

    Key Strategic Principles:
    1. Resource diversity - access to all five resources
    2. High-probability numbers - 6 and 8 are most frequent
    3. Port access - enables better trading ratios
    4. Expansion paths - plan where to grow
    5. Blocking opponents - deny key spots and resources
    6. Development cards - hidden victory points and strategic advantages

    Victory Points:
    - Settlement: 1 point
    - City: 2 points
    - Longest Road (5+ roads): 2 points
    - Largest Army (3+ knights): 2 points
    - Victory Point cards: 1 point each

    USER:
    Analyze the strategic situation for Player {player_id}:

    Game State: {game_state}
    Player Resources: {player_resources}
    Opponents: {opponent_analysis}
    Board Position: {board_position}
    Turn Number: {turn_number}

    Provide comprehensive strategic analysis with opportunities and threats.
    """
)
def analyze_catan_strategy(
    player_id: int,
    game_state: CatanState,
    player_resources: dict[Resource, int],
    opponent_analysis: str,
    board_position: str,
    turn_number: int,
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Analyze the strategic situation for a Catan player."""
    return {
        "computed_fields": {
            "game_state": game_state,
            "player_resources": player_resources,
        }
    }


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=list[TradeOffer],
)
@prompt_template(
    """
    SYSTEM:
    You are a master Catan trader for Player {player_id}.
    {personality_prompt}

    Trading Principles:
    1. Value scarcity - rare resources are worth more
    2. Consider opponent needs - they won't trade what they need
    3. Future planning - trade for what you'll need next
    4. Port efficiency - use ports for better ratios
    5. Timing - trade before others realize resource value

    Trade Ratios:
    - Player to player: Negotiable
    - Generic port: 3:1
    - Specific port: 2:1 for specific resource
    - No port: 4:1 with bank

    USER:
    Develop trade proposals for Player {player_id}:

    Current Resources: {current_resources}
    Needed Resources: {needed_resources}
    Strategic Goals: {strategic_goals}
    Opponent Resources: {opponent_resources}
    Available Ports: {available_ports}

    Create beneficial trade proposals that advance your strategy.
    """
)
def develop_trade_proposals(
    player_id: int,
    current_resources: dict[Resource, int],
    needed_resources: list[Resource],
    strategic_goals: str,
    opponent_resources: str,
    available_ports: list[str],
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> list[TradeOffer]:
    """Develop trade proposals for the current situation."""
    pass


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=CatanAction,
)
@prompt_template(
    """
    SYSTEM:
    You are making building decisions for Player {player_id} in Catan.
    {personality_prompt}

    Building Costs:
    - Road: 1 wood + 1 brick
    - Settlement: 1 wood + 1 brick + 1 sheep + 1 wheat
    - City: 3 ore + 2 wheat
    - Development Card: 1 ore + 1 sheep + 1 wheat

    Building Rules:
    - Settlements need 2 road distance from other settlements
    - Cities replace settlements
    - Roads must connect to your network
    - Longest road needs 5+ continuous roads

    Consider:
    - Resource production potential
    - Blocking opponent expansion
    - Port access
    - Future expansion paths
    - Victory point efficiency

    USER:
    Plan building action for Player {player_id}:

    Available Resources: {available_resources}
    Possible Builds: {possible_builds}
    Strategic Analysis: {strategic_analysis}
    Board State: {board_state}
    Victory Points: {victory_points}/10

    Choose the best building action with clear reasoning.
    """
)
def plan_building_action(
    player_id: int,
    available_resources: dict[Resource, int],
    possible_builds: list[str],
    strategic_analysis: StrategicAnalysis,
    board_state: str,
    victory_points: int,
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Plan the best building action for the current turn."""
    return {
        "computed_fields": {
            "strategic_analysis": strategic_analysis,
        }
    }


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=CatanAction,
)
@prompt_template(
    """
    SYSTEM:
    You are handling the robber for Player {player_id} in Catan.
    {personality_prompt}

    Robber Strategy:
    1. Block high-production hexes (6 and 8)
    2. Target the leading player
    3. Protect your own production
    4. Consider who to steal from
    5. Create resource scarcity

    When moving the robber:
    - Cannot stay on same hex
    - Must steal from adjacent player if possible
    - Blocks resource production on that hex

    USER:
    Decide robber placement for Player {player_id}:

    Current Robber Position: {current_robber_position}
    Player Positions: {player_positions}
    Resource Production: {resource_production}
    Player Standings: {player_standings}
    Strategic Goals: {strategic_goals}

    Choose optimal robber placement and stealing target.
    """
)
def handle_robber_action(
    player_id: int,
    current_robber_position: tuple[int, int],
    player_positions: str,
    resource_production: str,
    player_standings: str,
    strategic_goals: str,
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> CatanAction:
    """Decide where to move the robber and who to steal from."""
    pass


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=list[CatanAction],
)
@prompt_template(
    """
    SYSTEM:
    You are planning the complete turn for Player {player_id} in Catan.
    {personality_prompt}

    Turn Structure:
    1. Roll dice (automatic)
    2. Collect resources
    3. Trade with players/bank
    4. Build roads/settlements/cities
    5. Buy/play development cards
    6. End turn

    Turn Optimization:
    - Trade before building to get needed resources
    - Play knight before rolling if beneficial
    - Consider development cards for hidden points
    - Block opponents when ahead
    - Focus on points when behind

    USER:
    Plan complete turn for Player {player_id}:

    Current Phase: {current_phase}
    Resources Available: {resources}
    Strategic Analysis: {strategic_analysis}
    Trade Opportunities: {trade_opportunities}
    Building Options: {building_options}
    Victory Points: {victory_points}/10

    Provide ordered list of actions for this turn with reasoning.
    """
)
def plan_complete_turn(
    player_id: int,
    current_phase: CatanPhase,
    resources: dict[Resource, int],
    strategic_analysis: StrategicAnalysis,
    trade_opportunities: list[TradeOffer],
    building_options: str,
    victory_points: int,
    personality_prompt: str = PERSONALITY_PROMPTS["balanced"],
    provider: str = "openai",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Plan all actions for the current turn."""
    return {
        "computed_fields": {
            "strategic_analysis": strategic_analysis,
            "trade_opportunities": trade_opportunities,
        }
    }


async def process_human_catan_input(game: CatanGame, human_player: CatanPlayer, phase: CatanPhase) -> CatanAction:
    """Process human player input for their turn."""
    print(f"\n{human_player.name}'s turn - {phase.value}")
    print(f"Victory Points: {human_player.victory_points}/10")
    print(f"Resources: {dict(human_player.resources)}")

    if phase == CatanPhase.ROLL_DICE:
        input("Press Enter to roll dice...")
        dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
        print(f"Rolled: {dice1} + {dice2} = {dice1 + dice2}")
        return CatanAction(
            player_id=human_player.player_id,
            action_type=ActionType.ROLL_DICE,
            position=None,
            edge=None,
            resources=None,
            target_player=None,
            development_card=None,
            trade_offer=None,
            reasoning=f"Rolled {dice1 + dice2}",
        )

    elif phase == CatanPhase.MAIN_TURN:
        print("\nAvailable actions:")
        print("1. Build (road/settlement/city)")
        print("2. Buy development card")
        print("3. Play development card")
        print("4. Propose trade")
        print("5. End turn")

        choice = input("\nChoose action (1-5): ").strip()

        if choice == "1":
            build_type = input("Build what? (road/settlement/city): ").strip().lower()
            # In real implementation, would show valid positions and let player choose
            position_str = input("Enter position (simplified - just enter any text): ")

            action_type = {
                "road": ActionType.BUILD_ROAD,
                "settlement": ActionType.BUILD_SETTLEMENT,
                "city": ActionType.BUILD_CITY,
            }.get(build_type, ActionType.BUILD_ROAD)

            return CatanAction(
                player_id=human_player.player_id,
                action_type=action_type,
                position=(0, 0, 0),  # Simplified
                edge=None,
                resources=None,
                target_player=None,
                development_card=None,
                trade_offer=None,
                reasoning=f"Building {build_type}",
            )

        elif choice == "5":
            return CatanAction(
                player_id=human_player.player_id,
                action_type=ActionType.END_TURN,
                position=None,
                edge=None,
                resources=None,
                target_player=None,
                development_card=None,
                trade_offer=None,
                reasoning="Ending turn",
            )

        # Simplified - other actions would be implemented similarly
        return CatanAction(
            player_id=human_player.player_id,
            action_type=ActionType.END_TURN,
            position=None,
            edge=None,
            resources=None,
            target_player=None,
            development_card=None,
            trade_offer=None,
            reasoning="Default end turn",
        )

    # Default action
    return CatanAction(
        player_id=human_player.player_id,
        action_type=ActionType.END_TURN,
        position=None,
        edge=None,
        resources=None,
        target_player=None,
        development_card=None,
        trade_offer=None,
        reasoning="Default end turn",
    )


async def catan_game_agent(
    game_state: CatanState,
    players: list[CatanPlayer],
    action_history: list[CatanAction] = None,
    game_id: str = "catan_001",
    llm_provider: str = "openai",
    default_model: str = "gpt-4o",
) -> CatanGame:
    """
    Run a turn of Catan with multiple AI models and human players.

    This agent coordinates different AI models playing different players, processes
    human input, and manages resource collection, trading, and building.

    Args:
        game_state: Current state of the game
        players: List of players (human and AI with different models)
        action_history: History of previous actions
        game_id: Unique game identifier
        llm_provider: Default LLM provider
        default_model: Default model for AI players

    Returns:
        Updated CatanGame with all actions processed
    """

    if action_history is None:
        action_history = []

    current_player = players[game_state.current_player]
    print(f"\nCatan - Turn {game_state.turn_number}")
    print(f"Current Player: {current_player.name} (Player {current_player.player_id})")
    print(f"Phase: {game_state.phase.value}")

    # Process current player's action based on phase
    if current_player.player_type == PlayerType.HUMAN:
        # Human player input
        action = await process_human_catan_input(
            CatanGame(
                game_id=game_id, current_state=game_state, players=players, action_history=action_history, strategic_analyses={}
            ),
            current_player,
            game_state.phase,
        )
        action_history.append(action)
    else:
        # AI player with specific model
        model = current_player.model or default_model
        provider = current_player.provider or llm_provider
        personality_prompt = PERSONALITY_PROMPTS.get(current_player.personality or "balanced", PERSONALITY_PROMPTS["balanced"])

        # Step 1: Strategic analysis
        print(f"  {current_player.name} analyzing board...")
        strategic_analysis = await analyze_catan_strategy(
            player_id=current_player.player_id,
            game_state=game_state,
            player_resources=dict(current_player.resources),
            opponent_analysis=f"{len(players) - 1} opponents",
            board_position=f"Turn {game_state.turn_number}",
            turn_number=game_state.turn_number,
            personality_prompt=personality_prompt,
            provider=provider,
            model=model,
        )

        # Step 2: Handle specific phase
        if game_state.phase == CatanPhase.ROLL_DICE:
            dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
            print(f"  {current_player.name} rolled: {dice1} + {dice2} = {dice1 + dice2}")
            action = CatanAction(
                player_id=current_player.player_id,
                action_type=ActionType.ROLL_DICE,
                position=None,
                edge=None,
                resources=None,
                target_player=None,
                development_card=None,
                trade_offer=None,
                reasoning=f"Rolled {dice1 + dice2}",
            )
            action_history.append(action)
            game_state.dice_roll = (dice1, dice2)

        elif game_state.phase == CatanPhase.ROBBER_MOVE and game_state.dice_roll and sum(game_state.dice_roll) == 7:
            print(f"  {current_player.name} moving robber...")
            action = await handle_robber_action(
                player_id=current_player.player_id,
                current_robber_position=game_state.robber_position,
                player_positions="",  # Would analyze actual positions
                resource_production="",  # Would analyze production
                player_standings=str({p.player_id: p.victory_points for p in players}),
                strategic_goals="Block leading player",
                personality_prompt=personality_prompt,
                provider=provider,
                model=model,
            )
            action_history.append(action)

        elif game_state.phase == CatanPhase.MAIN_TURN:
            print(f"  {current_player.name} planning turn...")

            # Develop trade proposals
            trade_proposals = await develop_trade_proposals(
                player_id=current_player.player_id,
                current_resources=dict(current_player.resources),
                needed_resources=[r for r in Resource if r != Resource.DESERT],
                strategic_goals="Maximize building potential",
                opponent_resources="",  # Would analyze
                available_ports=[],  # Would check actual ports
                personality_prompt=personality_prompt,
                provider=provider,
                model=model,
            )

            # Plan complete turn
            turn_actions = await plan_complete_turn(
                player_id=current_player.player_id,
                current_phase=game_state.phase,
                resources=dict(current_player.resources),
                strategic_analysis=strategic_analysis,
                trade_opportunities=trade_proposals,
                building_options="",  # Would analyze valid builds
                victory_points=current_player.victory_points,
                personality_prompt=personality_prompt,
                provider=provider,
                model=model,
            )

            # Execute first action (simplified)
            if turn_actions:
                action_history.append(turn_actions[0])
            else:
                # Default to end turn
                action_history.append(
                    CatanAction(
                        player_id=current_player.player_id,
                        action_type=ActionType.END_TURN,
                        position=None,
                        edge=None,
                        resources=None,
                        target_player=None,
                        development_card=None,
                        trade_offer=None,
                        reasoning="No beneficial actions available",
                    )
                )

    # Create updated game
    strategic_analyses = {
        current_player.player_id: strategic_analysis
        if current_player.player_type == PlayerType.AI
        else StrategicAnalysis(
            resource_scarcity={},
            player_threats={},
            expansion_opportunities=[],
            trade_opportunities=[],
            development_card_strategy="",
            blocking_opportunities=[],
            win_probability=0.25,
        )
    }

    updated_game = CatanGame(
        game_id=game_id,
        current_state=game_state,
        players=players,
        action_history=action_history,
        strategic_analyses=strategic_analyses,
    )

    # Check for winner
    for player in players:
        if player.victory_points >= 10:
            game_state.winner = player.player_id
            print(f"\n{player.name} wins with {player.victory_points} points!")
            break

    print("\nAction complete!")
    return updated_game


async def catan_game_stream(game_state: CatanState, players: list[CatanPlayer], **kwargs) -> AsyncGenerator[str, None]:
    """Stream the Catan game turn with live updates."""

    yield f"**Settlers of Catan - Turn {game_state.turn_number}**\n\n"

    current_player = players[game_state.current_player]
    yield f"**Current Player:** {current_player.name} (Player {current_player.player_id})\n"
    yield f"**Phase:** {game_state.phase.value}\n\n"

    yield "## Current Standings\n\n"
    for player in sorted(players, key=lambda p: p.victory_points, reverse=True):
        vp_breakdown = f"{player.victory_points}VP"
        if player.has_longest_road:
            vp_breakdown += " (LR)"
        if player.has_largest_army:
            vp_breakdown += " (LA)"
        yield f"**{player.name}:** {vp_breakdown}\n"
    yield "\n"

    yield "## Resources\n\n"
    for player in players:
        total_resources = sum(player.resources.values())
        yield f"**{player.name}:** {total_resources} cards\n"
    yield "\n"

    # Run the game turn
    game = await catan_game_agent(game_state, players, **kwargs)

    # Show last action
    if game.action_history:
        last_action = game.action_history[-1]
        acting_player = next(p for p in players if p.player_id == last_action.player_id)

        yield "## Last Action\n\n"
        yield f"**{acting_player.name}** - {last_action.action_type.value}\n"
        yield f"*{last_action.reasoning}*\n\n"

    if game_state.dice_roll:
        yield "## Dice Roll\n\n"
        d1, d2 = game_state.dice_roll
        yield f"Rolled: **{d1} + {d2} = {d1 + d2}**\n\n"

    if game_state.active_trade_offers:
        yield "## Active Trades\n\n"
        for offer in game_state.active_trade_offers[:3]:
            proposer = next(p for p in players if p.player_id == offer.proposing_player)
            yield f"**{proposer.name}** offers "
            yield f"{dict(offer.offering)} for {dict(offer.requesting)}\n"

    if game_state.winner is not None:
        winner = next(p for p in players if p.player_id == game_state.winner)
        yield "\n## Game Over!\n\n"
        yield f"**{winner.name} wins with {winner.victory_points} victory points!**\n"
    else:
        yield "\n## Next Turn\n\n"
        next_player = players[(game_state.current_player + 1) % len(players)]
        yield f"Ready for {next_player.name}'s turn!\n"
