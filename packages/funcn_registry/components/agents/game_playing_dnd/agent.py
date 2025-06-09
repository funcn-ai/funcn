from __future__ import annotations

import asyncio
import json
import math
import random
import time
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template

# Import our tools
from packages.funcn_registry.components.tools.dice_roller.tool import (
    DiceRoll as ToolDiceRoll,
    DiceType as ToolDiceType,
    format_roll_result,
    roll_dice as tool_roll_dice,
)
from packages.funcn_registry.components.tools.dnd_5e_api.tool import (
    get_ability_score_info,
    get_class_info,
    get_condition_info,
    get_equipment_info,
    get_feat_info,
    get_magic_item_info,
    get_monster_info,
    get_proficiency_info,
    get_race_info,
    get_skill_info,
    get_spell_info,
    search_dnd_content,
)

# Add SQLite state management imports
from packages.funcn_registry.components.tools.sqlite_db.tool import (
    cleanup_old_state,
    create_agent_state_table,
    delete_agent_state,
    execute_sqlite_query,
    get_agent_state,
    query_agent_history,
    store_agent_state,
)
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import Any, Optional, Union


class PlayerType(str, Enum):
    """Types of players in the game."""


    HUMAN = "human"
    AI = "ai"
    DM = "dm"


class CharacterClass(str, Enum):
    """D&D character classes."""


    BARBARIAN = "barbarian"
    BARD = "bard"
    CLERIC = "cleric"
    DRUID = "druid"
    FIGHTER = "fighter"
    MONK = "monk"
    PALADIN = "paladin"
    RANGER = "ranger"
    ROGUE = "rogue"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    WIZARD = "wizard"


class ActionType(str, Enum):
    """Types of actions players can take."""


    MOVEMENT = "movement"
    ATTACK = "attack"
    SPELL = "spell"
    SKILL_CHECK = "skill_check"
    ROLEPLAY = "roleplay"
    ITEM_USE = "item_use"
    INVESTIGATION = "investigation"
    DIALOGUE = "dialogue"
    REST = "rest"
    SPECIAL = "special"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    FREE_ACTION = "free_action"


class GamePhase(str, Enum):
    """Current phase of the game."""


    EXPLORATION = "exploration"
    COMBAT = "combat"
    ROLEPLAY = "roleplay"
    PUZZLE = "puzzle"
    REST = "rest"
    SHOPPING = "shopping"
    TRAVEL = "travel"


class DiceType(str, Enum):
    """Types of dice in D&D."""


    D4 = "d4"
    D6 = "d6"
    D8 = "d8"
    D10 = "d10"
    D12 = "d12"
    D20 = "d20"
    D100 = "d100"


class RestType(str, Enum):
    """Types of rest in D&D."""


    SHORT = "short"
    LONG = "long"


class SkillType(str, Enum):
    """D&D 5e skills."""


    ACROBATICS = "acrobatics"
    ANIMAL_HANDLING = "animal-handling"
    ARCANA = "arcana"
    ATHLETICS = "athletics"
    DECEPTION = "deception"
    HISTORY = "history"
    INSIGHT = "insight"
    INTIMIDATION = "intimidation"
    INVESTIGATION = "investigation"
    MEDICINE = "medicine"
    NATURE = "nature"
    PERCEPTION = "perception"
    PERFORMANCE = "performance"
    PERSUASION = "persuasion"
    RELIGION = "religion"
    SLEIGHT_OF_HAND = "sleight-of-hand"
    STEALTH = "stealth"
    SURVIVAL = "survival"


class AbilityType(str, Enum):
    """D&D ability scores."""


    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class DiceRoll(BaseModel):
    """Result of a dice roll."""


    dice_type: DiceType = Field(..., description="Type of dice rolled")
    num_dice: int = Field(..., description="Number of dice rolled")
    rolls: list[int] = Field(..., description="Individual roll results")
    modifier: int = Field(default=0, description="Modifier to add")
    total: int = Field(..., description="Total result including modifier")
    purpose: str = Field(..., description="What the roll was for")
    critical: bool | None = Field(None, description="Whether it was a critical success/failure")
    ability_used: AbilityType | None = Field(None, description="Ability score used for the roll")
    skill_used: SkillType | None = Field(None, description="Skill used for the roll")
    proficiency_applied: bool = Field(False, description="Whether proficiency bonus was applied")


class Position(BaseModel):
    """Position on the battle grid."""


    x: int = Field(..., description="X coordinate")
    y: int = Field(..., description="Y coordinate")
    z: int = Field(0, description="Z coordinate (elevation)")

    def distance_to(self, other: Position) -> float:
        """Calculate distance to another position."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) * 5  # 5 feet per square
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) * 5  # 5 feet per square

    def is_adjacent(self, other: Position) -> bool:
        """Check if positions are adjacent (including diagonals)."""
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1 and abs(self.z - other.z) <= 1


class CharacterStats(BaseModel):
    """D&D character ability scores."""


    strength: int = Field(..., description="Strength score")
    dexterity: int = Field(..., description="Dexterity score")
    constitution: int = Field(..., description="Constitution score")
    intelligence: int = Field(..., description="Intelligence score")
    wisdom: int = Field(..., description="Wisdom score")
    charisma: int = Field(..., description="Charisma score")

    def get_modifier(self, ability: str) -> int:
        """Calculate ability modifier."""
        score = getattr(self, ability.lower())
        return (score - 10) // 2

    def get_saving_throw_modifier(self, ability: str, proficiency_bonus: int, proficient: bool) -> int:
        """Calculate saving throw modifier."""
        base_mod = self.get_modifier(ability)
        return base_mod + (proficiency_bonus if proficient else 0)


class SpellSlots(BaseModel):
    """Spell slot tracking."""


    level_1: int = Field(0, description="1st level slots")
    level_2: int = Field(0, description="2nd level slots")
    level_3: int = Field(0, description="3rd level slots")
    level_4: int = Field(0, description="4th level slots")
    level_5: int = Field(0, description="5th level slots")
    level_6: int = Field(0, description="6th level slots")
    level_7: int = Field(0, description="7th level slots")
    level_8: int = Field(0, description="8th level slots")
    level_9: int = Field(0, description="9th level slots")

    level_1_used: int = Field(0, description="1st level slots used")
    level_2_used: int = Field(0, description="2nd level slots used")
    level_3_used: int = Field(0, description="3rd level slots used")
    level_4_used: int = Field(0, description="4th level slots used")
    level_5_used: int = Field(0, description="5th level slots used")
    level_6_used: int = Field(0, description="6th level slots used")
    level_7_used: int = Field(0, description="7th level slots used")
    level_8_used: int = Field(0, description="8th level slots used")
    level_9_used: int = Field(0, description="9th level slots used")

    def get_available_slots(self, level: int) -> int:
        """Get available slots for a spell level."""
        total = getattr(self, f"level_{level}")
        used = getattr(self, f"level_{level}_used")
        return total - used

    def use_slot(self, level: int) -> bool:
        """Use a spell slot if available."""
        if self.get_available_slots(level) > 0:
            setattr(self, f"level_{level}_used", getattr(self, f"level_{level}_used") + 1)
            return True
        return False

    def reset_slots(self):
        """Reset all spell slots (long rest)."""
        for i in range(1, 10):
            setattr(self, f"level_{i}_used", 0)


class InventoryItem(BaseModel):
    """An item in inventory."""


    name: str = Field(..., description="Item name")
    quantity: int = Field(1, description="Number of items")
    weight: float = Field(0, description="Weight per item")
    equipped: bool = Field(False, description="Whether item is equipped")
    attunement_required: bool = Field(False, description="Whether attunement is required")
    attuned: bool = Field(False, description="Whether character is attuned")
    magical: bool = Field(False, description="Whether item is magical")
    description: str = Field("", description="Item description")


class CharacterCondition(BaseModel):
    """A condition affecting a character."""


    name: str = Field(..., description="Condition name")
    description: str = Field(..., description="Condition effects")
    duration_rounds: int | None = Field(None, description="Duration in rounds")
    save_dc: int | None = Field(None, description="DC to end condition")
    save_ability: AbilityType | None = Field(None, description="Ability for save")
    source: str = Field(..., description="What caused the condition")


class CharacterSheet(BaseModel):
    """Complete D&D character sheet."""


    name: str = Field(..., description="Character name")
    race: str = Field(..., description="Character race")
    character_class: CharacterClass = Field(..., description="Character class")
    level: int = Field(..., description="Character level")
    experience_points: int = Field(0, description="Current XP")
    stats: CharacterStats = Field(..., description="Ability scores")
    hit_points: int = Field(..., description="Current hit points")
    max_hit_points: int = Field(..., description="Maximum hit points")
    temp_hit_points: int = Field(0, description="Temporary hit points")
    hit_dice_remaining: int = Field(..., description="Hit dice remaining")
    armor_class: int = Field(..., description="Armor class")
    proficiency_bonus: int = Field(..., description="Proficiency bonus")
    speed: int = Field(30, description="Movement speed in feet")
    initiative_bonus: int = Field(0, description="Initiative modifier")

    # Proficiencies
    skill_proficiencies: list[SkillType] = Field(default_factory=list, description="Proficient skills")
    expertise_skills: list[SkillType] = Field(default_factory=list, description="Expertise skills")
    saving_throw_proficiencies: list[AbilityType] = Field(default_factory=list, description="Saving throw proficiencies")

    # Combat tracking
    actions_available: int = Field(1, description="Actions remaining this turn")
    bonus_actions_available: int = Field(1, description="Bonus actions remaining")
    reactions_available: int = Field(1, description="Reactions remaining")
    movement_remaining: int = Field(..., description="Movement remaining this turn")

    # Resources
    spell_slots: SpellSlots | None = Field(None, description="Spell slots for casters")
    spells_known: list[str] = Field(default_factory=list, description="Known/prepared spells")
    cantrips_known: list[str] = Field(default_factory=list, description="Known cantrips")

    # Inventory
    inventory: list[InventoryItem] = Field(default_factory=list, description="Items carried")
    equipped_armor: str | None = Field(None, description="Currently worn armor")
    equipped_weapons: list[str] = Field(default_factory=list, description="Wielded weapons")
    attunement_slots_used: int = Field(0, description="Magic items attuned to")

    # Status
    conditions: list[CharacterCondition] = Field(default_factory=list, description="Active conditions")
    exhaustion_level: int = Field(0, description="Exhaustion level (0-6)")
    death_saves_success: int = Field(0, description="Successful death saves")
    death_saves_failure: int = Field(0, description="Failed death saves")

    # Character details
    background: str = Field(..., description="Character background story")
    personality_traits: list[str] = Field(..., description="Personality traits")
    ideals: list[str] = Field(default_factory=list, description="Character ideals")
    bonds: list[str] = Field(default_factory=list, description="Character bonds")
    flaws: list[str] = Field(default_factory=list, description="Character flaws")

    @validator('proficiency_bonus')
    def calculate_proficiency_bonus(cls, v, values):
        """Calculate proficiency bonus based on level."""
        if 'level' in values:
            level = values['level']
            return 2 + ((level - 1) // 4)
        return v

    @validator('movement_remaining', always=True)
    def set_movement_remaining(cls, v, values):
        """Set movement remaining to speed if not specified."""
        if v is None and 'speed' in values:
            return values['speed']
        return v

    def get_skill_modifier(self, skill: SkillType) -> int:
        """Calculate total skill modifier."""
        # Map skills to abilities
        skill_ability_map = {
            SkillType.ACROBATICS: AbilityType.DEXTERITY,
            SkillType.ANIMAL_HANDLING: AbilityType.WISDOM,
            SkillType.ARCANA: AbilityType.INTELLIGENCE,
            SkillType.ATHLETICS: AbilityType.STRENGTH,
            SkillType.DECEPTION: AbilityType.CHARISMA,
            SkillType.HISTORY: AbilityType.INTELLIGENCE,
            SkillType.INSIGHT: AbilityType.WISDOM,
            SkillType.INTIMIDATION: AbilityType.CHARISMA,
            SkillType.INVESTIGATION: AbilityType.INTELLIGENCE,
            SkillType.MEDICINE: AbilityType.WISDOM,
            SkillType.NATURE: AbilityType.INTELLIGENCE,
            SkillType.PERCEPTION: AbilityType.WISDOM,
            SkillType.PERFORMANCE: AbilityType.CHARISMA,
            SkillType.PERSUASION: AbilityType.CHARISMA,
            SkillType.RELIGION: AbilityType.INTELLIGENCE,
            SkillType.SLEIGHT_OF_HAND: AbilityType.DEXTERITY,
            SkillType.STEALTH: AbilityType.DEXTERITY,
            SkillType.SURVIVAL: AbilityType.WISDOM,
        }

        ability = skill_ability_map[skill]
        modifier = self.stats.get_modifier(ability.value)

        if skill in self.expertise_skills:
            modifier += self.proficiency_bonus * 2
        elif skill in self.skill_proficiencies:
            modifier += self.proficiency_bonus

        return modifier

    def get_xp_for_next_level(self) -> int:
        """Get XP required for next level."""
        xp_thresholds = {
            1: 0,
            2: 300,
            3: 900,
            4: 2700,
            5: 6500,
            6: 14000,
            7: 23000,
            8: 34000,
            9: 48000,
            10: 64000,
            11: 85000,
            12: 100000,
            13: 120000,
            14: 140000,
            15: 165000,
            16: 195000,
            17: 225000,
            18: 265000,
            19: 305000,
            20: 355000,
            1: 0,
            2: 300,
            3: 900,
            4: 2700,
            5: 6500,
            6: 14000,
            7: 23000,
            8: 34000,
            9: 48000,
            10: 64000,
            11: 85000,
            12: 100000,
            13: 120000,
            14: 140000,
            15: 165000,
            16: 195000,
            17: 225000,
            18: 265000,
            19: 305000,
            20: 355000,
        }
        if self.level >= 20:
            return 0
        return xp_thresholds.get(self.level + 1, 0)

    def add_experience(self, xp: int) -> bool:
        """Add XP and check for level up."""
        self.experience_points += xp
        next_level_xp = self.get_xp_for_next_level()
        return next_level_xp > 0 and self.experience_points >= next_level_xp

    def reset_turn_resources(self):
        """Reset resources at start of turn."""
        self.actions_available = 1
        self.bonus_actions_available = 1
        self.reactions_available = 1
        self.movement_remaining = self.speed

    def take_damage(self, damage: int) -> int:
        """Apply damage, handling temp HP."""
        remaining_damage = damage

        # Apply to temp HP first
        if self.temp_hit_points > 0:
            if self.temp_hit_points >= remaining_damage:
                self.temp_hit_points -= remaining_damage
                return 0
            else:
                remaining_damage -= self.temp_hit_points
                self.temp_hit_points = 0

        # Apply to regular HP
        self.hit_points = max(0, self.hit_points - remaining_damage)
        return remaining_damage

    def heal(self, healing: int) -> int:
        """Apply healing, capped at max HP."""
        old_hp = self.hit_points
        self.hit_points = min(self.max_hit_points, self.hit_points + healing)
        return self.hit_points - old_hp


class CombatantInfo(BaseModel):
    """Information about a combatant in battle."""


    name: str = Field(..., description="Combatant name")
    position: Position = Field(..., description="Current position")
    initiative: int = Field(..., description="Initiative roll result")
    is_player: bool = Field(..., description="Whether this is a player character")
    is_surprised: bool = Field(False, description="Whether combatant is surprised")
    has_acted: bool = Field(False, description="Whether they've acted this round")
    conditions: list[str] = Field(default_factory=list, description="Active conditions")
    ac: int = Field(..., description="Armor class")
    current_hp: int = Field(..., description="Current hit points")
    max_hp: int = Field(..., description="Maximum hit points")


class BattleMap(BaseModel):
    """Battle map tracking positions."""


    width: int = Field(20, description="Map width in squares")
    height: int = Field(20, description="Map height in squares")
    combatants: dict[str, CombatantInfo] = Field(default_factory=dict, description="Combatant positions")
    obstacles: list[Position] = Field(default_factory=list, description="Impassable squares")
    difficult_terrain: list[Position] = Field(default_factory=list, description="Difficult terrain squares")

    def get_combatant_at(self, pos: Position) -> str | None:
        """Get combatant at a position."""
        for name, info in self.combatants.items():
            if info.position == pos:
                return name
        return None

    def is_valid_position(self, pos: Position) -> bool:
        """Check if position is valid and unoccupied."""
        if pos.x < 0 or pos.x >= self.width or pos.y < 0 or pos.y >= self.height:
            return False
        if pos in self.obstacles:
            return False
        return self.get_combatant_at(pos) is None

    def calculate_movement_cost(self, from_pos: Position, to_pos: Position) -> int:
        """Calculate movement cost between positions."""
        base_cost = int(from_pos.distance_to(to_pos))

        # Check for difficult terrain
        if to_pos in self.difficult_terrain:
            base_cost *= 2

        return base_cost


class PlayerCharacter(BaseModel):
    """A player character in the game."""


    character: CharacterSheet = Field(..., description="Character sheet")
    player_type: PlayerType = Field(..., description="Human or AI player")
    model: str | None = Field(None, description="AI model if AI player")
    provider: str | None = Field(None, description="AI provider if AI player")
    personality_prompt: str | None = Field(None, description="AI personality instructions")
    is_active: bool = Field(True, description="Whether player is active")
    last_action_time: datetime | None = Field(None, description="Time of last action")
    position: Position | None = Field(None, description="Current position in combat")


class PlayerAction(BaseModel):
    """An action taken by a player."""


    player_name: str = Field(..., description="Name of the acting player")
    action_type: ActionType = Field(..., description="Type of action")
    description: str = Field(..., description="Detailed description of the action")
    target: str | None = Field(None, description="Target of the action")
    target_position: Position | None = Field(None, description="Target position for movement")
    dice_rolls: list[DiceRoll] = Field(default_factory=list, description="Any dice rolls involved")
    success: bool | None = Field(None, description="Whether the action succeeded")
    consequences: list[str] = Field(default_factory=list, description="Results of the action")
    resources_used: dict[str, int] = Field(default_factory=dict, description="Resources consumed")


class CombatAction(BaseModel):
    """A combat-specific action."""


    attacker: str = Field(..., description="Name of the attacker")
    target: str = Field(..., description="Name of the target")
    attack_type: str = Field(..., description="Type of attack")
    attack_roll: DiceRoll = Field(..., description="Attack roll result")
    damage_roll: DiceRoll | None = Field(None, description="Damage roll if hit")
    hit: bool = Field(..., description="Whether the attack hit")
    damage_dealt: int = Field(default=0, description="Total damage dealt")
    special_effects: list[str] = Field(default_factory=list, description="Special effects")
    advantage: bool = Field(False, description="Whether attack had advantage")
    disadvantage: bool = Field(False, description="Whether attack had disadvantage")


class RoleplayExchange(BaseModel):
    """A roleplay dialogue exchange."""


    speaker: str = Field(..., description="Who is speaking")
    dialogue: str = Field(..., description="What they say")
    tone: str = Field(..., description="Tone of delivery")
    actions: str | None = Field(None, description="Physical actions while speaking")
    target_audience: list[str] = Field(default_factory=list, description="Who they're speaking to")
    requires_response: bool = Field(True, description="Whether a response is expected")
    skill_check: DiceRoll | None = Field(None, description="Any skill check involved")


class GameEvent(BaseModel):
    """A significant game event."""


    event_type: str = Field(..., description="Type of event")
    description: str = Field(..., description="Detailed description")
    participants: list[str] = Field(..., description="Characters involved")
    location: str = Field(..., description="Where it happened")
    timestamp: datetime = Field(..., description="When it happened")
    consequences: list[str] = Field(default_factory=list, description="Results of the event")
    xp_awarded: dict[str, int] = Field(default_factory=dict, description="XP awarded to characters")


class EncounterInfo(BaseModel):
    """Information about an encounter."""


    name: str = Field(..., description="Encounter name")
    difficulty: str = Field(..., description="Encounter difficulty")
    enemies: list[str] = Field(..., description="Enemy types")
    total_xp: int = Field(..., description="Total XP value")
    environment: str = Field(..., description="Environment description")
    objectives: list[str] = Field(default_factory=list, description="Encounter objectives")


class GameState(BaseModel):
    """Current state of the D&D game."""


    session_id: str = Field(..., description="Unique session identifier")
    campaign_name: str = Field(..., description="Name of the campaign")
    current_phase: GamePhase = Field(..., description="Current game phase")
    location: str = Field(..., description="Current location in the game world")
    scene_description: str = Field(..., description="Description of the current scene")
    active_players: list[PlayerCharacter] = Field(..., description="Active player characters")
    npcs_present: list[str] = Field(default_factory=list, description="NPCs in the scene")

    # Combat tracking
    combat_round: int = Field(0, description="Current combat round")
    combat_order: list[str] = Field(default_factory=list, description="Initiative order if in combat")
    battle_map: BattleMap | None = Field(None, description="Battle map for combat")
    current_encounter: EncounterInfo | None = Field(None, description="Current encounter info")

    # Game tracking
    recent_events: list[GameEvent] = Field(default_factory=list, description="Recent game events")
    quest_status: dict[str, str] = Field(default_factory=dict, description="Active quests and status")
    world_state: dict[str, Any] = Field(default_factory=dict, description="World state variables")
    session_xp_earned: dict[str, int] = Field(default_factory=dict, description="XP earned this session")

    # Time tracking
    game_time: str = Field("Morning", description="In-game time of day")
    days_elapsed: int = Field(0, description="Days since campaign start")
    long_rest_available: bool = Field(True, description="Whether party can take long rest")


class DMResponse(BaseModel):
    """Dungeon Master's response to player actions."""


    narration: str = Field(..., description="Narrative description")
    dice_rolls: list[DiceRoll] = Field(default_factory=list, description="DM's dice rolls")
    npc_actions: list[PlayerAction] = Field(default_factory=list, description="NPC actions")
    npc_dialogue: list[RoleplayExchange] = Field(default_factory=list, description="NPC dialogue")
    scene_changes: str | None = Field(None, description="Changes to the scene")
    phase_change: GamePhase | None = Field(None, description="New game phase if changed")
    player_prompts: dict[str, str] = Field(default_factory=dict, description="Specific prompts for players")
    rules_clarification: str | None = Field(None, description="Rules explanations if needed")
    xp_awards: dict[str, int] = Field(default_factory=dict, description="XP awarded this turn")
    battle_map_update: BattleMap | None = Field(None, description="Updated battle map")
    conditions_applied: dict[str, list[str]] = Field(default_factory=dict, description="Conditions applied to characters")
    secret_notes: str | None = Field(None, description="DM notes not shared with players")


class HumanInputRequest(BaseModel):
    """Request for human input during gameplay."""


    request_type: str = Field(..., description="Type of input needed")
    prompt: str = Field(..., description="Prompt for the human player")
    context: str = Field(..., description="Context for the decision")
    options: list[str] = Field(default_factory=list, description="Available options if applicable")
    time_limit: int | None = Field(None, description="Time limit in seconds")
    can_interrupt: bool = Field(True, description="Whether player can interrupt ongoing RP")


# SQLite State Management Functions
async def initialize_campaign_database(campaign_name: str, db_path: str | None = None) -> str:
    """Initialize SQLite database for campaign state persistence.

    Args:
        campaign_name: Name of the campaign
        db_path: Optional custom database path

    Returns:
        Path to the database file
    """
    if db_path is None:
        # Create a campaigns directory if it doesn't exist
        campaigns_dir = Path("campaigns")
        campaigns_dir.mkdir(exist_ok=True)

        # Create a safe filename from campaign name
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in campaign_name)
        db_path = str(campaigns_dir / f"{safe_name}.db")

    # Create the necessary tables
    await create_agent_state_table(db_path, "game_state")
    await create_agent_state_table(db_path, "character_sheets")
    await create_agent_state_table(db_path, "game_events")
    await create_agent_state_table(db_path, "combat_logs")

    # Create campaign metadata
    await store_agent_state(
        db_path,
        agent_id="campaign",
        key="metadata",
        value={"campaign_name": campaign_name, "created_at": datetime.now().isoformat(), "version": "1.0"},
        table_name="game_state",
        value={"campaign_name": campaign_name, "created_at": datetime.now().isoformat(), "version": "1.0"},
        table_name="game_state",
    )

    return db_path


async def save_game_state(game_state: GameState, db_path: str) -> None:
    """Save the current game state to SQLite database.

    Args:
        game_state: Current game state to save
        db_path: Path to the database
    """
    # Save main game state
    state_dict = game_state.model_dump()

    # Extract and save character sheets separately for easier querying
    characters = state_dict.pop("active_players", [])

    # Save the main game state
    await store_agent_state(
        db_path,
        agent_id="game",
        key="current_state",
        value=state_dict,
        conversation_id=game_state.session_id,
        metadata={
            "campaign_name": game_state.campaign_name,
            "phase": game_state.current_phase.value,
            "location": game_state.location,
            "combat_round": game_state.combat_round,
            "days_elapsed": game_state.days_elapsed,
            "days_elapsed": game_state.days_elapsed,
        },
        table_name="game_state",
        table_name="game_state",
    )

    # Save each character sheet
    for player_data in characters:
        character = player_data["character"]
        await store_agent_state(
            db_path,
            agent_id="character",
            key=character["name"],
            value=player_data,
            conversation_id=game_state.session_id,
            metadata={
                "level": character["level"],
                "class": character["character_class"],
                "hp": f"{character['hit_points']}/{character['max_hit_points']}",
                "xp": character["experience_points"],
                "xp": character["experience_points"],
            },
            table_name="character_sheets",
            table_name="character_sheets",
        )

    # Save recent events
    for event in game_state.recent_events[-10:]:  # Keep last 10 events
        await store_agent_state(
            db_path,
            agent_id="event",
            key=f"{event.timestamp.isoformat()}_{event.event_type}",
            value=event.model_dump(),
            conversation_id=game_state.session_id,
            metadata={"event_type": event.event_type, "location": event.location, "participants": ",".join(event.participants)},
            table_name="game_events",
            metadata={"event_type": event.event_type, "location": event.location, "participants": ",".join(event.participants)},
            table_name="game_events",
        )


async def load_game_state(session_id: str, db_path: str) -> GameState | None:
    """Load a game state from the database.

    Args:
        session_id: Session ID to load
        db_path: Path to the database

    Returns:
        Loaded GameState or None if not found
    """
    # Load main game state
    result = await get_agent_state(
        db_path, agent_id="game", key="current_state", conversation_id=session_id, table_name="game_state"
        db_path, agent_id="game", key="current_state", conversation_id=session_id, table_name="game_state"
    )

    if not result.success or not result.results:
        return None

    state_data = result.results[0]["value"]

    # Load character sheets
    char_result = await get_agent_state(db_path, agent_id="character", conversation_id=session_id, table_name="character_sheets")
    char_result = await get_agent_state(db_path, agent_id="character", conversation_id=session_id, table_name="character_sheets")

    if char_result.success and char_result.results:
        # Reconstruct PlayerCharacter objects
        active_players = []
        for char_row in char_result.results:
            player_data = char_row["value"]
            # Convert character class string back to enum if needed
            char_sheet = player_data["character"]
            if isinstance(char_sheet["character_class"], str):
                char_sheet["character_class"] = CharacterClass(char_sheet["character_class"])

            # Reconstruct nested objects
            char_sheet["stats"] = CharacterStats(**char_sheet["stats"])
            if char_sheet.get("spell_slots"):
                char_sheet["spell_slots"] = SpellSlots(**char_sheet["spell_slots"])

            # Reconstruct inventory items
            char_sheet["inventory"] = [InventoryItem(**item) for item in char_sheet.get("inventory", [])]

            # Reconstruct conditions
            char_sheet["conditions"] = [CharacterCondition(**cond) for cond in char_sheet.get("conditions", [])]

            # Reconstruct skill and ability enums
            char_sheet["skill_proficiencies"] = [SkillType(s) for s in char_sheet.get("skill_proficiencies", [])]
            char_sheet["expertise_skills"] = [SkillType(s) for s in char_sheet.get("expertise_skills", [])]
            char_sheet["saving_throw_proficiencies"] = [AbilityType(a) for a in char_sheet.get("saving_throw_proficiencies", [])]

            # Create CharacterSheet
            character = CharacterSheet(**char_sheet)

            # Reconstruct position if present
            if player_data.get("position"):
                player_data["position"] = Position(**player_data["position"])

            # Create PlayerCharacter
            player = PlayerCharacter(
                character=character,
                player_type=PlayerType(player_data["player_type"]),
                model=player_data.get("model"),
                provider=player_data.get("provider"),
                personality_prompt=player_data.get("personality_prompt"),
                is_active=player_data.get("is_active", True),
                last_action_time=datetime.fromisoformat(player_data["last_action_time"])
                if player_data.get("last_action_time")
                else None,
                position=player_data.get("position"),
                last_action_time=datetime.fromisoformat(player_data["last_action_time"])
                if player_data.get("last_action_time")
                else None,
                position=player_data.get("position"),
            )
            active_players.append(player)

        state_data["active_players"] = active_players

    # Reconstruct enums and complex objects
    state_data["current_phase"] = GamePhase(state_data["current_phase"])

    # Reconstruct battle map if present
    if state_data.get("battle_map"):
        battle_data = state_data["battle_map"]
        combatants = {}
        for name, info in battle_data.get("combatants", {}).items():
            info["position"] = Position(**info["position"])
            combatants[name] = CombatantInfo(**info)
        battle_data["combatants"] = combatants
        battle_data["obstacles"] = [Position(**pos) for pos in battle_data.get("obstacles", [])]
        battle_data["difficult_terrain"] = [Position(**pos) for pos in battle_data.get("difficult_terrain", [])]
        state_data["battle_map"] = BattleMap(**battle_data)

    # Reconstruct encounter info if present
    if state_data.get("current_encounter"):
        state_data["current_encounter"] = EncounterInfo(**state_data["current_encounter"])

    # Reconstruct recent events
    event_result = await get_agent_state(db_path, agent_id="event", conversation_id=session_id, table_name="game_events")
    event_result = await get_agent_state(db_path, agent_id="event", conversation_id=session_id, table_name="game_events")

    if event_result.success and event_result.results:
        events = []
        for event_row in event_result.results:
            event_data = event_row["value"]
            event_data["timestamp"] = datetime.fromisoformat(event_data["timestamp"])
            events.append(GameEvent(**event_data))
        state_data["recent_events"] = sorted(events, key=lambda e: e.timestamp)

    return GameState(**state_data)


async def save_combat_log(
    session_id: str, combat_round: int, actions: list[PlayerAction], dm_response: DMResponse, db_path: str
    session_id: str, combat_round: int, actions: list[PlayerAction], dm_response: DMResponse, db_path: str
) -> None:
    """Save combat log entry to database.

    Args:
        session_id: Current session ID
        combat_round: Combat round number
        actions: Player actions taken
        dm_response: DM's response
        db_path: Path to the database
    """
    await store_agent_state(
        db_path,
        agent_id="combat",
        key=f"round_{combat_round}",
        value={
            "round": combat_round,
            "timestamp": datetime.now().isoformat(),
            "player_actions": [action.model_dump() for action in actions],
            "dm_response": dm_response.model_dump(),
        },
        conversation_id=session_id,
        metadata={"round": combat_round, "num_actions": len(actions), "xp_awarded": sum(dm_response.xp_awards.values())},
        table_name="combat_logs",
        metadata={"round": combat_round, "num_actions": len(actions), "xp_awarded": sum(dm_response.xp_awards.values())},
        table_name="combat_logs",
    )


async def get_campaign_sessions(db_path: str) -> list[dict[str, Any]]:
    """Get all sessions for a campaign.

    Args:
        db_path: Path to the database

    Returns:
        List of session summaries
    """
    result = await execute_sqlite_query(
        db_path,
        """
        SELECT DISTINCT conversation_id,
               MAX(updated_at) as last_played,
               COUNT(*) as num_saves
        FROM game_state
        WHERE agent_id = 'game'
        GROUP BY conversation_id
        ORDER BY last_played DESC
        """,
        """,
    )

    if result.success and result.results:
        sessions = []
        for row in result.results:
            # Get the actual game state for more details
            state_result = await get_agent_state(
                db_path, agent_id="game", key="current_state", conversation_id=row["conversation_id"], table_name="game_state"
                db_path, agent_id="game", key="current_state", conversation_id=row["conversation_id"], table_name="game_state"
            )

            if state_result.success and state_result.results:
                metadata = state_result.results[0].get("metadata", {})
                sessions.append(
                    {
                        "session_id": row["conversation_id"],
                        "last_played": row["last_played"],
                        "num_saves": row["num_saves"],
                        "location": metadata.get("location", "Unknown"),
                        "phase": metadata.get("phase", "Unknown"),
                        "days_elapsed": metadata.get("days_elapsed", 0),
                    }
                )
                sessions.append(
                    {
                        "session_id": row["conversation_id"],
                        "last_played": row["last_played"],
                        "num_saves": row["num_saves"],
                        "location": metadata.get("location", "Unknown"),
                        "phase": metadata.get("phase", "Unknown"),
                        "days_elapsed": metadata.get("days_elapsed", 0),
                    }
                )

        return sessions

    return []


async def create_campaign_backup(db_path: str, backup_name: str | None = None) -> str:
    """Create a backup of the campaign database.

    Args:
        db_path: Path to the database
        backup_name: Optional custom backup name

    Returns:
        Path to the backup file
    """
    import shutil

    db_file = Path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    # Create backups directory
    backup_dir = db_file.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Generate backup filename
    if backup_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{db_file.stem}_backup_{timestamp}.db"

    backup_path = backup_dir / backup_name

    # Copy the database
    shutil.copy2(db_file, backup_path)

    return str(backup_path)


# Enhanced tool functions with proper rule enforcement
async def roll_ability_check(
    character_name: str,
    ability: str,
    skill: str | None = None,
    modifier: int = 0,
    advantage: bool = False,
    disadvantage: bool = False,
    proficiency_bonus: int = 0,
    is_proficient: bool = False,
    has_expertise: bool = False,
) -> str:
    """
    Roll an ability check with proper modifiers.

    Args:
        character_name: Name of the character making the check
        ability: Ability score to use (strength, dexterity, etc.)
        skill: Specific skill if applicable
        modifier: Base ability modifier
        advantage: Roll with advantage
        disadvantage: Roll with disadvantage
        proficiency_bonus: Character's proficiency bonus
        is_proficient: Whether character is proficient
        has_expertise: Whether character has expertise

    Returns:
        Formatted check result with all modifiers
    """
    # Calculate total modifier
    total_modifier = modifier
    if is_proficient:
        total_modifier += proficiency_bonus
    if has_expertise:
        total_modifier += proficiency_bonus  # Expertise doubles proficiency

    purpose = f"{ability.title()} check"
    if skill:
        purpose = f"{skill.title()} ({ability.title()}) check"

    # Roll the check
    result = tool_roll_dice(
        dice_type=ToolDiceType.D20,
        num_dice=1,
        modifier=total_modifier,
        purpose=f"{character_name}'s {purpose}",
        advantage=advantage,
        disadvantage=disadvantage,
        disadvantage=disadvantage,
    )

    # Add details about modifiers
    details = [format_roll_result(result)]
    if is_proficient:
        details.append(f"Proficiency: +{proficiency_bonus}")
    if has_expertise:
        details.append(f"Expertise: +{proficiency_bonus} (additional)")

    return "\n".join(details)


async def roll_saving_throw(
    character_name: str,
    ability: str,
    dc: int,
    modifier: int = 0,
    proficiency_bonus: int = 0,
    is_proficient: bool = False,
    advantage: bool = False,
    disadvantage: bool = False,
    bonus: int = 0,
    bonus: int = 0,
) -> str:
    """
    Roll a saving throw against a DC.

    Args:
        character_name: Name of the character
        ability: Ability score for the save
        dc: Difficulty class to beat
        modifier: Base ability modifier
        proficiency_bonus: Character's proficiency bonus
        is_proficient: Whether character is proficient in this save
        advantage: Roll with advantage
        disadvantage: Roll with disadvantage
        bonus: Additional bonuses (e.g., from magic items)

    Returns:
        Formatted save result with success/failure
    """
    # Calculate total modifier
    total_modifier = modifier
    if is_proficient:
        total_modifier += proficiency_bonus
    total_modifier += bonus

    # Roll the save
    result = tool_roll_dice(
        dice_type=ToolDiceType.D20,
        num_dice=1,
        modifier=total_modifier,
        purpose=f"{character_name}'s {ability.title()} save vs DC {dc}",
        advantage=advantage,
        disadvantage=disadvantage,
        disadvantage=disadvantage,
    )

    # Determine success
    success = result.total >= dc

    # Format result
    output = [format_roll_result(result)]
    output.append(f"**{'SUCCESS' if success else 'FAILURE'}** (DC {dc})")

    if is_proficient:
        output.append(f"Proficiency: +{proficiency_bonus}")
    if bonus > 0:
        output.append(f"Additional bonus: +{bonus}")

    return "\n".join(output)


async def roll_attack(
    attacker_name: str,
    target_ac: int,
    attack_bonus: int,
    damage_dice: str,
    damage_type: str,
    is_melee: bool = True,
    advantage: bool = False,
    disadvantage: bool = False,
    critical_range: int = 20,
    weapon_name: str = "weapon",
    weapon_name: str = "weapon",
) -> str:
    """
    Roll a complete attack with hit and damage.

    Args:
        attacker_name: Name of the attacker
        target_ac: Target's armor class
        attack_bonus: Total attack bonus
        damage_dice: Damage dice formula (e.g., "1d8+3")
        damage_type: Type of damage
        is_melee: Whether this is a melee attack
        advantage: Roll with advantage
        disadvantage: Roll with disadvantage
        critical_range: Minimum roll for critical (usually 20)
        weapon_name: Name of the weapon

    Returns:
        Complete attack resolution
    """
    # Roll attack
    attack_result = tool_roll_dice(
        dice_type=ToolDiceType.D20,
        num_dice=1,
        modifier=attack_bonus,
        purpose=f"{attacker_name}'s attack roll",
        advantage=advantage,
        disadvantage=disadvantage,
        disadvantage=disadvantage,
    )

    # Check for critical
    is_critical = attack_result.rolls[0] >= critical_range
    is_fumble = attack_result.rolls[0] == 1

    # Determine hit
    hits = attack_result.total >= target_ac and not is_fumble

    output = [f"**{attacker_name} attacks with {weapon_name}!**"]
    output.append(format_roll_result(attack_result))

    if is_fumble:
        output.append("**CRITICAL FUMBLE!** The attack fails spectacularly!")
        return "\n".join(output)

    if is_critical and hits:
        output.append("**CRITICAL HIT!**")

    if hits:
        output.append(f"**HIT!** (AC {target_ac})")

        # Parse damage dice
        parts = damage_dice.split('+')
        if len(parts) == 2:
            dice_part = parts[0]
            modifier_part = int(parts[1])
        else:
            dice_part = damage_dice
            modifier_part = 0

        # Extract number of dice and die type
        dice_split = dice_part.split('d')
        num_dice = int(dice_split[0])
        die_type = f"d{dice_split[1]}"

        # Roll damage (double dice for critical)
        damage_result = tool_roll_dice(
            dice_type=ToolDiceType(die_type),
            num_dice=num_dice * (2 if is_critical else 1),
            modifier=modifier_part,
            purpose=f"Damage ({damage_type})",
            purpose=f"Damage ({damage_type})",
        )

        output.append(format_roll_result(damage_result))
        output.append(f"**Total Damage: {damage_result.total} {damage_type}**")
    else:
        output.append(f"**MISS!** (AC {target_ac})")

    return "\n".join(output)


async def calculate_movement(
    character_name: str,
    from_position: tuple[int, int],
    to_position: tuple[int, int],
    base_speed: int,
    movement_used: int = 0,
    difficult_terrain: bool = False,
    dash_action: bool = False,
    dash_action: bool = False,
) -> str:
    """
    Calculate movement cost and validity.

    Args:
        character_name: Name of the character moving
        from_position: Starting position (x, y)
        to_position: Target position (x, y)
        base_speed: Character's base movement speed
        movement_used: Movement already used this turn
        difficult_terrain: Whether path includes difficult terrain
        dash_action: Whether using dash action

    Returns:
        Movement calculation and validity
    """
    # Calculate distance
    from_pos = Position(x=from_position[0], y=from_position[1], z=0)
    to_pos = Position(x=to_position[0], y=to_position[1], z=0)
    distance = from_pos.distance_to(to_pos)

    # Apply difficult terrain
    if difficult_terrain:
        distance *= 2

    # Calculate available movement
    total_movement = base_speed * (2 if dash_action else 1)
    remaining_movement = total_movement - movement_used

    output = [f"**{character_name}'s Movement**"]
    output.append(f"Distance: {distance} ft")
    output.append(f"Movement available: {remaining_movement}/{total_movement} ft")

    if distance <= remaining_movement:
        output.append("**Movement VALID** ✓")
        output.append(f"Movement remaining after: {remaining_movement - distance} ft")
    else:
        output.append("**Movement INVALID** ✗")
        output.append(f"Need {distance - remaining_movement} more feet of movement")

    if difficult_terrain:
        output.append("*Difficult terrain doubles movement cost*")
    if dash_action:
        output.append("*Dash action doubles movement*")

    return "\n".join(output)


async def check_spell_requirements(
    caster_name: str,
    spell_name: str,
    spell_level: int,
    available_slots: dict[int, int],
    components_available: list[str],
    concentration_active: bool = False,
    concentration_active: bool = False,
) -> str:
    """
    Check if a spell can be cast.

    Args:
        caster_name: Name of the spellcaster
        spell_name: Name of the spell
        spell_level: Level of the spell (0 for cantrips)
        available_slots: Dict of spell level to available slots
        components_available: Available components (V, S, M)
        concentration_active: Whether already concentrating

    Returns:
        Spell casting validity check
    """
    try:
        # Look up spell info
        spell = await get_spell_info(spell_name)

        output = [f"**{caster_name} attempts to cast {spell.name}**"]

        can_cast = True
        issues = []

        # Check spell slots
        if spell_level > 0:
            if spell_level not in available_slots or available_slots[spell_level] <= 0:
                can_cast = False
                issues.append(f"No level {spell_level} spell slots available")
            else:
                output.append(f"Spell slot available: Level {spell_level} ✓")
        else:
            output.append("Cantrip - no spell slot needed ✓")

        # Check components
        for component in spell.components:
            if component not in components_available:
                can_cast = False
                issues.append(f"Missing {component} component")
        if all(c in components_available for c in spell.components):
            output.append(f"Components available: {', '.join(spell.components)} ✓")

        # Check concentration
        if spell.concentration and concentration_active:
            issues.append("Already concentrating on another spell")
            output.append("⚠️ Casting this will end current concentration")

        # Final verdict
        if can_cast and not issues:
            output.append("\n**Spell can be cast!** ✓")
        else:
            output.append("\n**Cannot cast spell:**")
            for issue in issues:
                output.append(f"- {issue}")

        # Add spell details
        output.append(f"\nCasting Time: {spell.casting_time}")
        output.append(f"Range: {spell.range}")
        output.append(f"Duration: {spell.duration}")

        return "\n".join(output)

    except ValueError as e:
        return f"Error: {str(e)}"


async def apply_condition(
    character_name: str,
    condition_name: str,
    duration_rounds: int | None = None,
    save_dc: int | None = None,
    save_ability: str | None = None,
    save_ability: str | None = None,
) -> str:
    """
    Apply a condition to a character.

    Args:
        character_name: Name of the affected character
        condition_name: Name of the condition
        duration_rounds: How many rounds it lasts
        save_dc: DC to end the condition
        save_ability: Ability used for saves

    Returns:
        Condition application details
    """
    try:
        # Look up condition effects
        condition = await get_condition_info(condition_name)

        output = [f"**{character_name} is {condition.name}!**"]
        output.append("\nEffects:")
        for effect in condition.desc:
            output.append(f"• {effect}")

        if duration_rounds:
            output.append(f"\nDuration: {duration_rounds} rounds")
        if save_dc and save_ability:
            output.append(f"Save: DC {save_dc} {save_ability} at end of turn")

        return "\n".join(output)

    except ValueError as e:
        return f"Error: {str(e)}"


async def calculate_encounter_xp(monster_names: list[str], party_size: int, party_levels: list[int]) -> str:
    """
    Calculate XP for an encounter.

    Args:
        monster_names: List of monster names
        party_size: Number of party members
        party_levels: List of party member levels

    Returns:
        XP calculation and difficulty
    """
    total_xp = 0
    monster_details = []

    # Get XP for each monster
    for monster_name in monster_names:
        try:
            monster = await get_monster_info(monster_name)
            monster_details.append(f"{monster.name}: {monster.xp} XP (CR {monster.challenge_rating})")
            total_xp += monster.xp
        except ValueError:
            monster_details.append(f"{monster_name}: Unknown")

    # Calculate encounter multiplier
    num_monsters = len(monster_names)
    multipliers = {1: 1.0, 2: 1.5, (3, 6): 2.0, (7, 10): 2.5, (11, 14): 3.0, (15, float('inf')): 4.0}
    multipliers = {1: 1.0, 2: 1.5, (3, 6): 2.0, (7, 10): 2.5, (11, 14): 3.0, (15, float('inf')): 4.0}

    multiplier = 1.0
    for key, value in multipliers.items():
        if isinstance(key, tuple):
            if key[0] <= num_monsters <= key[1]:
                multiplier = value
                break
        elif num_monsters == key:
            multiplier = value
            break

    # Adjust for party size
    if party_size < 3:
        multiplier *= 1.5
    elif party_size > 5:
        multiplier *= 0.5

    adjusted_xp = int(total_xp * multiplier)

    # Calculate difficulty thresholds
    avg_level = sum(party_levels) // len(party_levels)
    thresholds = {
        1: (25, 50, 75, 100),
        2: (50, 100, 150, 200),
        3: (75, 150, 225, 400),
        4: (125, 250, 375, 500),
        5: (250, 500, 750, 1100),
        6: (300, 600, 900, 1400),
        7: (350, 750, 1100, 1700),
        8: (450, 900, 1400, 2100),
        9: (550, 1100, 1600, 2400),
        10: (600, 1200, 1900, 2800),
        11: (800, 1600, 2400, 3600),
        12: (1000, 2000, 3000, 4500),
        13: (1100, 2200, 3400, 5100),
        14: (1250, 2500, 3800, 5700),
        15: (1400, 2800, 4300, 6400),
        16: (1600, 3200, 4800, 7200),
        17: (2000, 3900, 5900, 8800),
        18: (2100, 4200, 6300, 9500),
        19: (2400, 4900, 7300, 10900),
        20: (2800, 5700, 8500, 12700),
        20: (2800, 5700, 8500, 12700),
    }

    party_thresholds = thresholds.get(avg_level, thresholds[20])  # Default to level 20 if beyond
    total_thresholds = tuple(t * party_size for t in party_thresholds)

    # Determine difficulty
    if adjusted_xp < total_thresholds[0]:
        difficulty = "Easy"
    elif adjusted_xp < total_thresholds[1]:
        difficulty = "Medium"
    elif adjusted_xp < total_thresholds[2]:
        difficulty = "Hard"
    else:
        difficulty = "Deadly"

    output = ["**Encounter XP Calculation**"]
    output.append("\nMonsters:")
    output.extend(monster_details)
    output.append(f"\nBase XP: {total_xp}")
    output.append(f"Multiplier: x{multiplier} ({num_monsters} monsters, {party_size} party members)")
    output.append(f"Adjusted XP: {adjusted_xp}")
    output.append(f"\n**Difficulty: {difficulty}**")
    output.append(
        f"Party thresholds - Easy: {total_thresholds[0]}, Medium: {total_thresholds[1]}, Hard: {total_thresholds[2]}, Deadly: {total_thresholds[3]}"
    )
    output.append(
        f"Party thresholds - Easy: {total_thresholds[0]}, Medium: {total_thresholds[1]}, Hard: {total_thresholds[2]}, Deadly: {total_thresholds[3]}"
    )
    output.append(f"\nXP per character: {total_xp // party_size}")

    return "\n".join(output)


async def manage_rest(
    character_name: str,
    rest_type: str,
    current_hp: int,
    max_hp: int,
    hit_dice_remaining: int,
    hit_die_size: int,
    con_modifier: int,
    spell_slots_used: dict[int, int] | None = None,
    exhaustion_level: int = 0,
    exhaustion_level: int = 0,
) -> str:
    """
    Handle short or long rest mechanics.

    Args:
        character_name: Name of the character
        rest_type: "short" or "long"
        current_hp: Current hit points
        max_hp: Maximum hit points
        hit_dice_remaining: Number of hit dice available
        hit_die_size: Size of hit die (d6, d8, etc.)
        con_modifier: Constitution modifier
        spell_slots_used: Dict of spell level to slots used
        exhaustion_level: Current exhaustion level

    Returns:
        Rest results and recovery
    """
    output = [f"**{character_name} takes a {rest_type} rest**"]

    if rest_type.lower() == "short":
        output.append("\nShort Rest (1 hour):")

        # Hit dice healing
        if hit_dice_remaining > 0 and current_hp < max_hp:
            output.append(f"\nHit Dice available: {hit_dice_remaining}d{hit_die_size}")
            output.append("You can spend hit dice to heal")
            output.append(f"Each die heals 1d{hit_die_size} + {con_modifier}")
        else:
            output.append("\nNo hit dice available for healing")

        # Class features
        output.append("\nFeatures recovered:")
        output.append("• Warlock spell slots")
        output.append("• Fighter's Second Wind")
        output.append("• Monk's Ki points")
        output.append("• Other short rest abilities")

    else:  # Long rest
        output.append("\nLong Rest (8 hours):")

        # HP recovery
        hp_recovered = max_hp - current_hp
        output.append(f"\nHP recovered: {hp_recovered} (full heal to {max_hp})")

        # Hit dice recovery
        hit_dice_recovered = max(1, hit_dice_remaining // 2)
        output.append(f"Hit Dice recovered: {hit_dice_recovered}")

        # Spell slots
        if spell_slots_used:
            output.append("\nSpell slots recovered: All")

        # Exhaustion
        if exhaustion_level > 0:
            output.append(f"Exhaustion reduced: {exhaustion_level} → {max(0, exhaustion_level - 1)}")

        # All features
        output.append("\nAll features recovered:")
        output.append("• All spell slots")
        output.append("• All class features")
        output.append("• All racial abilities")
        output.append("• Death saves reset")

    return "\n".join(output)


# Existing tool functions remain the same
async def roll_for_action(
    dice_type: str, num_dice: int = 1, modifier: int = 0, purpose: str = "", advantage: bool = False, disadvantage: bool = False
    dice_type: str, num_dice: int = 1, modifier: int = 0, purpose: str = "", advantage: bool = False, disadvantage: bool = False
) -> str:
    """
    Roll dice for any game action.

    Args:
        dice_type: Type of dice (d4, d6, d8, d10, d12, d20, d100)
        num_dice: Number of dice to roll
        modifier: Modifier to add to the roll
        purpose: What the roll is for
        advantage: Roll with advantage (d20 only)
        disadvantage: Roll with disadvantage (d20 only)

    Returns:
        Formatted roll result
    """
    # Convert to tool dice type
    tool_dice_type = ToolDiceType(dice_type.lower())

    # Use the dice roller tool
    result = tool_roll_dice(
        dice_type=tool_dice_type,
        num_dice=num_dice,
        modifier=modifier,
        purpose=purpose,
        advantage=advantage,
        disadvantage=disadvantage,
        disadvantage=disadvantage,
    )

    # Format and return the result
    return format_roll_result(result)


async def lookup_spell(spell_name: str) -> str:
    """
    Look up D&D 5e spell information.

    Args:
        spell_name: Name of the spell to look up

    Returns:
        Spell details including level, school, casting time, etc.
    """
    try:
        spell = await get_spell_info(spell_name)
        return f"""**{spell.name}**
Level: {spell.level} {spell.school}
Casting Time: {spell.casting_time}
Range: {spell.range}
Components: {', '.join(spell.components)}
Duration: {spell.duration} {'(Concentration)' if spell.concentration else ''}

{' '.join(spell.description)}

Classes: {', '.join(spell.classes)}"""
    except ValueError as e:
        return str(e)


async def lookup_monster(monster_name: str) -> str:
    """
    Look up D&D 5e monster statistics.

    Args:
        monster_name: Name of the monster to look up

    Returns:
        Monster stats including AC, HP, abilities, and actions
    """
    try:
        monster = await get_monster_info(monster_name)
        return f"""**{monster.name}**
{monster.size} {monster.type}, {monster.alignment}
AC: {monster.armor_class}, HP: {monster.hit_points} ({monster.hit_dice})
Speed: {', '.join(f"{k}: {v}" for k, v in monster.speed.items())}
CR: {monster.challenge_rating}

STR: {monster.abilities['strength']} DEX: {monster.abilities['dexterity']} CON: {monster.abilities['constitution']}
INT: {monster.abilities['intelligence']} WIS: {monster.abilities['wisdom']} CHA: {monster.abilities['charisma']}

Senses: {', '.join(f"{k}: {v}" for k, v in monster.senses.items())}
Languages: {', '.join(monster.languages)}

Actions: {len(monster.actions)} available"""
    except ValueError as e:
        return str(e)


async def lookup_equipment(item_name: str) -> str:
    """
    Look up D&D 5e equipment information.

    Args:
        item_name: Name of the equipment to look up

    Returns:
        Equipment details including cost, weight, and properties
    """
    try:
        equipment = await get_equipment_info(item_name)
        details = [f"**{equipment.name}**"]
        details.append(f"Category: {equipment.equipment_category}")
        details.append(f"Cost: {equipment.cost['quantity']} {equipment.cost['unit']}")

        if equipment.weight:
            details.append(f"Weight: {equipment.weight} lbs")

        if equipment.armor_class:
            details.append(f"AC: {equipment.armor_class}")

        if equipment.damage:
            details.append(f"Damage: {equipment.damage}")

        if equipment.properties:
            details.append(f"Properties: {', '.join(equipment.properties)}")

        if equipment.description:
            details.append("\n" + " ".join(equipment.description))

        return "\n".join(details)
    except ValueError as e:
        return str(e)


async def search_rules(content_type: str, query: str = "") -> str:
    """
    Search D&D 5e rules and content.

    Args:
        content_type: Type of content (spells, monsters, equipment, etc.)
        query: Optional search query

    Returns:
        List of matching content
    """
    try:
        results = await search_dnd_content(content_type, query)
        if results.count == 0:
            return f"No {content_type} found matching '{query}'"

        items = [f"- {r['name']}" for r in results.results[:10]]  # Limit to 10
        return f"Found {results.count} {content_type}:\n" + "\n".join(items)
    except ValueError as e:
        return str(e)


async def lookup_race(race_name: str) -> str:
    """
    Look up D&D 5e race information.

    Args:
        race_name: Name of the race to look up

    Returns:
        Race details including abilities, traits, and bonuses
    """
    try:
        race = await get_race_info(race_name)
        details = [f"**{race.name}**"]
        details.append(f"Size: {race.size}, Speed: {race.speed} ft")

        # Ability bonuses
        bonuses = [f"{ab.ability_score.name} +{ab.bonus}" for ab in race.ability_bonuses]
        details.append(f"Ability Bonuses: {', '.join(bonuses)}")

        # Languages
        langs = [lang.name for lang in race.languages]
        details.append(f"Languages: {', '.join(langs)}")

        # Traits
        if race.traits:
            trait_names = [t.name for t in race.traits]
            details.append(f"Racial Traits: {', '.join(trait_names)}")

        details.append(f"\n{race.alignment}")

        return "\n".join(details)
    except ValueError as e:
        return str(e)


async def lookup_condition(condition_name: str) -> str:
    """
    Look up D&D 5e condition effects.

    Args:
        condition_name: Name of the condition

    Returns:
        Condition effects and rules
    """
    try:
        condition = await get_condition_info(condition_name)
        return f"**{condition.name}**\n\n" + "\n".join(f"• {effect}" for effect in condition.desc)
    except ValueError as e:
        return str(e)


async def lookup_skill(skill_name: str) -> str:
    """
    Look up D&D 5e skill information.

    Args:
        skill_name: Name of the skill

    Returns:
        Skill details and associated ability
    """
    try:
        skill = await get_skill_info(skill_name)
        return f"**{skill.name}** ({skill.ability_score.name})\n\n{' '.join(skill.desc)}"
    except ValueError as e:
        return str(e)


async def lookup_magic_item(item_name: str) -> str:
    """
    Look up D&D 5e magic item information.

    Args:
        item_name: Name of the magic item

    Returns:
        Magic item details including rarity and effects
    """
    try:
        item = await get_magic_item_info(item_name)
        details = [f"**{item.name}**"]
        details.append(f"Rarity: {item.rarity['name']}")
        details.append(f"Category: {item.equipment_category.name}")

        if item.variants:
            variant_names = [v.name for v in item.variants]
            details.append(f"Variants: {', '.join(variant_names)}")

        details.append("\n" + "\n".join(item.desc))

        return "\n".join(details)
    except ValueError as e:
        return str(e)


async def search_content(
    content_type: str, query: str = "", level: int | None = None, school: str | None = None, challenge_rating: float | None = None
) -> str:
    """
    Search D&D 5e content with filters.

    Args:
        content_type: Type of content (spells, monsters, equipment, etc.)
        query: Search query
        level: Spell level filter (for spells)
        school: Magic school filter (for spells)
        challenge_rating: CR filter (for monsters)

    Returns:
        List of matching content
    """
    try:
        filters: dict[str, int | str | float] = {}
        if level is not None:
            filters["level"] = level
        if school:
            filters["school"] = school
        if challenge_rating is not None:
            filters["challenge_rating"] = challenge_rating

        results = await search_dnd_content(content_type, query, **filters)

        if results.count == 0:
            return f"No {content_type} found matching your criteria"

        items = [f"- {r['name']}" for r in results.results[:20]]  # Limit to 20
        return f"Found {results.count} {content_type}:\n" + "\n".join(items)
    except ValueError as e:
        return str(e)


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=DMResponse,
    tools=[
        roll_for_action,
        roll_ability_check,
        roll_saving_throw,
        roll_attack,
        calculate_movement,
        check_spell_requirements,
        apply_condition,
        calculate_encounter_xp,
        manage_rest,
        lookup_spell,
        lookup_monster,
        lookup_equipment,
        search_rules,
        lookup_race,
        lookup_condition,
        lookup_skill,
        lookup_magic_item,
        search_content,
        search_content,
    ],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert Dungeon Master running a D&D 5th Edition game.
    Your style is {dm_style}.

    Core DM Principles:
    1. Player agency - Let players drive the story through their choices
    2. Yes, and... - Build on player ideas creatively
    3. Balanced challenge - Not too easy, not impossible
    4. Immersive narration - Paint vivid scenes with all senses
    5. Fair adjudication - Apply rules consistently but flexibly

    Current Campaign: {campaign_name}
    Tone: {campaign_tone}

    You have access to these enhanced tools:

    DICE & CHECKS:
    - roll_for_action: Basic dice rolls
    - roll_ability_check: Ability/skill checks with proper modifiers
    - roll_saving_throw: Saving throws vs DC
    - roll_attack: Complete attack sequences with damage

    COMBAT & MOVEMENT:
    - calculate_movement: Validate movement and track position
    - apply_condition: Apply status conditions
    - calculate_encounter_xp: Determine encounter difficulty and XP

    RESOURCES:
    - check_spell_requirements: Validate spellcasting
    - manage_rest: Handle short/long rest mechanics

    LOOKUPS:
    - lookup_spell/monster/equipment/race/condition/skill/magic_item: Get official stats
    - search_content: Search with filters

    RULES TO ENFORCE:
    1. Action Economy: Each turn allows 1 action, 1 bonus action, 1 reaction, and movement
    2. Spell Slots: Track and consume spell slots appropriately
    3. Concentration: Only one concentration spell at a time
    4. Movement: Characters can move up to their speed each turn
    5. Conditions: Apply condition effects consistently
    6. Death Saves: At 0 HP, track death saving throws
    7. Exhaustion: Track exhaustion levels (disadvantage, half speed, etc.)
    8. Ability Checks: Always use proper ability modifiers and proficiency
    9. Advantage/Disadvantage: Apply when appropriate
    10. XP & Leveling: Award XP for encounters and milestones

    Remember to:
    - Use tools for ALL dice rolls and rule lookups
    - Track resources (HP, spell slots, abilities)
    - Describe scenes cinematically
    - Give each player spotlight time
    - React dynamically to unexpected actions
    - Maintain narrative consistency
    - Build tension and excitement
    - Reward creative problem-solving
    - Apply conditions and their effects
    - Track positions in combat

    USER:
    Respond to the current game situation:

    Game State: {game_state}
    Recent Actions: {recent_actions}
    Player Requests: {player_requests}

    Phase: {current_phase}
    Special Considerations: {special_considerations}

    Provide an engaging DM response that:
    1. Narrates the results of player actions
    2. Uses tools for any necessary rolls or lookups
    3. Tracks changes to HP, resources, positions
    4. Awards XP when appropriate
    5. Applies conditions when needed
    6. Prompts for the next player actions
    """
)
def generate_dm_response(
    game_state: GameState,
    recent_actions: list[PlayerAction],
    player_requests: dict[str, str],
    current_phase: GamePhase,
    special_considerations: str = "",
    campaign_name: str = "The Lost Mines of Phandelver",
    campaign_tone: str = "Classic fantasy adventure with mystery elements",
    dm_style: str = "Engaging storyteller who balances combat, roleplay, and exploration",
    provider: str = "openai",
    model: str = "gpt-4o",
    model: str = "gpt-4o",
) -> BaseDynamicConfig:
    """Generate DM response to game situation."""
    return {
        "computed_fields": {
            "game_state": game_state,
            "recent_actions": recent_actions,
        }
    }


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=PlayerAction,
    tools=[
        roll_for_action,
        roll_ability_check,
        roll_saving_throw,
        roll_attack,
        calculate_movement,
        check_spell_requirements,
        lookup_spell,
        lookup_equipment,
        lookup_skill,
        lookup_skill,
    ],
)
@prompt_template(
    """
    SYSTEM:
    You are playing {character_name}, a level {level} {race} {character_class} in a D&D game.

    Character Personality: {personality}
    Background: {background}

    Roleplaying Guidelines:
    1. Stay true to your character's personality and motivations
    2. Consider your abilities and resources
    3. Work with the party but maintain your unique voice
    4. Make decisions your character would make, not optimal ones
    5. React emotionally to events as your character would

    Your Stats:
    {stats}

    Current Resources:
    - HP: {current_hp}/{max_hp}
    - Movement: {movement_remaining} ft remaining
    - Actions: {actions_available}
    - Bonus Actions: {bonus_actions_available}
    - Reactions: {reactions_available}
    - Spell Slots: {spell_slots}
    - Conditions: {conditions}
    - Position: {position}

    Key Abilities:
    - Proficient Skills: {proficient_skills}
    - Saving Throws: {saving_throws}
    - Attacks: {available_attacks}
    - Spells Known: {spells_known}

    You have access to these tools:
    - roll_ability_check: Make skill/ability checks with proper modifiers
    - roll_saving_throw: Roll saves against effects
    - roll_attack: Make attack rolls with damage
    - calculate_movement: Check if movement is valid
    - check_spell_requirements: Verify you can cast a spell
    - lookup_spell/equipment/skill: Get details on abilities

    ACTION ECONOMY RULES:
    - You can take ONE action (attack, cast spell, dash, dodge, help, hide, ready, search)
    - You can take ONE bonus action (if you have abilities that use it)
    - You can move up to your speed
    - Reactions happen outside your turn

    USER:
    Decide your action in this situation:

    Current Scene: {scene_description}
    DM Prompt: {dm_prompt}
    Party Status: {party_status}
    Your Position: {your_position}
    Enemies: {enemies_visible}
    Available Options: {available_options}

    What does {character_name} do? Be specific and in-character.
    Consider:
    1. What action will you take? (attack, spell, skill check, etc.)
    2. Will you move? Where?
    3. Any bonus actions?
    4. Are you setting up any reactions?

    Use tools for any dice rolls or rule lookups needed.
    Specify target positions as coordinates if moving.
    """
)
def generate_ai_player_action(
    character_name: str,
    level: int,
    race: str,
    character_class: str,
    personality: str,
    background: str,
    stats: str,
    current_hp: int,
    max_hp: int,
    movement_remaining: int,
    actions_available: int,
    bonus_actions_available: int,
    reactions_available: int,
    spell_slots: str,
    conditions: str,
    position: str,
    proficient_skills: str,
    saving_throws: str,
    available_attacks: str,
    spells_known: str,
    scene_description: str,
    dm_prompt: str,
    party_status: str,
    your_position: str,
    enemies_visible: str,
    available_options: str,
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    model: str = "gpt-4o-mini",
) -> BaseDynamicConfig:
    """Generate AI player action."""
    return {}


@llm.call(
    provider="{provider}",
    model="{model}",
    response_model=RoleplayExchange,
)
@prompt_template(
    """
    SYSTEM:
    You are roleplaying as {character_name} in a D&D game.

    Character Details:
    - Personality: {personality}
    - Speaking Style: {speaking_style}
    - Current Mood: {current_mood}
    - Relationship with others: {relationships}

    Roleplay Guidelines:
    1. Speak in character with appropriate vocabulary and mannerisms
    2. Express emotions through tone and actions
    3. Reference your background and experiences
    4. React authentically to the situation
    5. Use your character's knowledge, not player knowledge

    USER:
    Respond in character to this situation:

    Scene: {scene}
    Speaking To: {speaking_to}
    Previous Dialogue: {previous_dialogue}
    Your Goal: {character_goal}
    Emotional State: {emotional_state}

    Provide your character's response with appropriate dialogue and actions.
    """
)
def generate_character_dialogue(
    character_name: str,
    personality: str,
    speaking_style: str,
    current_mood: str,
    relationships: str,
    scene: str,
    speaking_to: str,
    previous_dialogue: str,
    character_goal: str,
    emotional_state: str,
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    model: str = "gpt-4o-mini",
) -> BaseDynamicConfig:
    """Generate in-character dialogue."""
    return {}


async def wait_for_human_input(request: HumanInputRequest, timeout: int | None = None) -> str | None:
async def wait_for_human_input(request: HumanInputRequest, timeout: int | None = None) -> str | None:
    """Wait for human input with optional timeout and interrupt capability."""
    print(f"\n{request.prompt}")
    if request.context:
        print(f"Context: {request.context}")

    if request.options:
        print("Options:")
        for i, option in enumerate(request.options, 1):
            print(f"  {i}. {option}")

    if request.can_interrupt:
        print("(Press Ctrl+C to interrupt ongoing roleplay)")

    start_time = time.time()
    timeout = timeout or request.time_limit

    try:
        if timeout:
            print(f"You have {timeout} seconds to respond...")
            # Use asyncio to handle timeout properly
            try:
                response = await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, input, "> "), timeout=timeout)
                response = await asyncio.wait_for(asyncio.get_event_loop().run_in_executor(None, input, "> "), timeout=timeout)
                return response
            except TimeoutError:
                print("\nTime's up! Moving on...")
                return None
        else:
            # No timeout - wait indefinitely
            response = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            return response
    except KeyboardInterrupt:
        if request.can_interrupt:
            return "INTERRUPT"
        raise
    except Exception as e:
        print(f"Error getting input: {e}")
        return None


async def process_player_turn(player: PlayerCharacter, game_state: GameState, dm_prompt: str, party_status: str) -> PlayerAction:
async def process_player_turn(player: PlayerCharacter, game_state: GameState, dm_prompt: str, party_status: str) -> PlayerAction:
    """Process a single player's turn."""
    if player.player_type == PlayerType.HUMAN:
        # Human player turn
        request = HumanInputRequest(
            request_type="action",
            prompt=f"{player.character.name}'s turn! What do you do?",
            context=dm_prompt,
            options=[
                "Attack",
                "Cast a spell",
                "Move",
                "Use an item",
                "Roleplay/speak",
                "Investigate",
                "Help another player",
                "Custom action",
                "Custom action",
            ],
            time_limit=120,  # 2 minutes
            can_interrupt=True,
            can_interrupt=True,
        )

        human_input = await wait_for_human_input(request)

        if human_input == "INTERRUPT":
            return PlayerAction(
                player_name=player.character.name,
                action_type=ActionType.ROLEPLAY,
                description="*interrupts the current scene*",
                target=None,
                target_position=None,
                success=True,
                success=True,
            )

        # Parse human input into action
        action_type = ActionType.SPECIAL
        description = human_input or "No action taken"

        # Parse action type from input
        if human_input:
            lower_input = human_input.lower()
            if any(word in lower_input for word in ["attack", "hit", "strike"]):
                action_type = ActionType.ATTACK
            elif any(word in lower_input for word in ["cast", "spell", "magic"]):
                action_type = ActionType.SPELL
            elif any(word in lower_input for word in ["move", "walk", "run"]):
                action_type = ActionType.MOVEMENT
            elif any(word in lower_input for word in ["say", "speak", "tell", "ask"]):
                action_type = ActionType.DIALOGUE
            elif any(word in lower_input for word in ["search", "investigate", "look"]):
                action_type = ActionType.INVESTIGATION
            elif any(word in lower_input for word in ["use", "item", "potion"]):
                action_type = ActionType.ITEM_USE
            elif any(word in lower_input for word in ["rest", "heal"]):
                action_type = ActionType.REST
            elif any(word in lower_input for word in ["help", "aid", "assist"]):
                action_type = ActionType.SPECIAL
                description = f"Help action: {human_input}"

        return PlayerAction(
            player_name=player.character.name,
            action_type=action_type,
            description=description,
            target=None,
            target_position=None,
            success=True,
            success=True,
        )

    else:
        # AI player turn
        # Prepare character data
        position_str = "Not in combat"
        if player.position:
            position_str = f"({player.position.x}, {player.position.y})"

        conditions_str = "None"
        if player.character.conditions:
            conditions_str = ", ".join([c.name for c in player.character.conditions])

        proficient_skills_str = "None"
        if player.character.skill_proficiencies:
            proficient_skills_str = ", ".join([s.value for s in player.character.skill_proficiencies])

        saving_throws_str = "None"
        if player.character.saving_throw_proficiencies:
            saving_throws_str = ", ".join([s.value for s in player.character.saving_throw_proficiencies])

        available_attacks_str = "Unarmed strike"
        if player.character.equipped_weapons:
            available_attacks_str = ", ".join(player.character.equipped_weapons)

        spells_known_str = "None"
        if player.character.spells_known:
            spells_known_str = ", ".join(player.character.spells_known[:5])  # Limit to 5 for brevity

        # Calculate spell slots string
        spell_slots_str = "N/A"
        if player.character.spell_slots:
            slots_available = []
            for level in range(1, 10):
                available = player.character.spell_slots.get_available_slots(level)
                if available > 0:
                    slots_available.append(f"L{level}: {available}")
            if slots_available:
                spell_slots_str = ", ".join(slots_available)

        # Get visible enemies
        enemies_visible_str = "None"
        if game_state.current_phase == GamePhase.COMBAT and game_state.battle_map:
            enemy_names = []
            for name, info in game_state.battle_map.combatants.items():
                if not info.is_player and info.current_hp > 0:
                    enemy_names.append(f"{name} (AC {info.ac})")
            if enemy_names:
                enemies_visible_str = ", ".join(enemy_names)

        action = generate_ai_player_action(
            character_name=player.character.name,
            level=player.character.level,
            race=player.character.race,
            character_class=player.character.character_class.value,
            personality=" ".join(player.character.personality_traits),
            background=player.character.background,
            stats=str(player.character.stats),
            current_hp=player.character.hit_points,
            max_hp=player.character.max_hit_points,
            movement_remaining=player.character.movement_remaining,
            actions_available=player.character.actions_available,
            bonus_actions_available=player.character.bonus_actions_available,
            reactions_available=player.character.reactions_available,
            spell_slots=spell_slots_str,
            conditions=conditions_str,
            position=position_str,
            proficient_skills=proficient_skills_str,
            saving_throws=saving_throws_str,
            available_attacks=available_attacks_str,
            spells_known=spells_known_str,
            scene_description=game_state.scene_description,
            dm_prompt=dm_prompt,
            party_status=party_status,
            your_position=f"With the party in {game_state.location}",
            enemies_visible=enemies_visible_str,
            available_options="Any appropriate action",
            provider=player.provider or "openai",
            model=player.model or "gpt-4o-mini",
            model=player.model or "gpt-4o-mini",
        )

        # Add a small delay for AI players to make it feel more natural
        await asyncio.sleep(2)

        return action


async def handle_level_up(character: CharacterSheet) -> dict[str, Any]:
    """Handle character level up."""
    character.level += 1

    # Update proficiency bonus
    character.proficiency_bonus = 2 + ((character.level - 1) // 4)

    # Calculate HP increase
    con_modifier = character.stats.get_modifier("constitution")

    # Map class to hit die
    hit_die_map = {
        CharacterClass.BARBARIAN: 12,
        CharacterClass.FIGHTER: 10,
        CharacterClass.PALADIN: 10,
        CharacterClass.RANGER: 10,
        CharacterClass.BARD: 8,
        CharacterClass.CLERIC: 8,
        CharacterClass.DRUID: 8,
        CharacterClass.MONK: 8,
        CharacterClass.ROGUE: 8,
        CharacterClass.WARLOCK: 8,
        CharacterClass.SORCERER: 6,
        CharacterClass.WIZARD: 6,
    }

    hit_die = hit_die_map.get(character.character_class, 8)
    hp_increase = (hit_die // 2 + 1) + con_modifier  # Average HP increase

    character.max_hit_points += hp_increase
    character.hit_points += hp_increase
    character.hit_dice_remaining += 1

    # Update spell slots for casters
    if (
        character.character_class
        in [
            CharacterClass.WIZARD,
            CharacterClass.SORCERER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.BARD,
            CharacterClass.WARLOCK,
        ]
        and character.spell_slots
    ):
    if (
        character.character_class
        in [
            CharacterClass.WIZARD,
            CharacterClass.SORCERER,
            CharacterClass.CLERIC,
            CharacterClass.DRUID,
            CharacterClass.BARD,
            CharacterClass.WARLOCK,
        ]
        and character.spell_slots
    ):
        # Full spell slot progression table
        # Full caster progression (Wizard, Sorcerer, Cleric, Druid, Bard)
        full_caster_slots = {
            1: {"level_1": 2},
            2: {"level_1": 3},
            3: {"level_1": 4, "level_2": 2},
            4: {"level_1": 4, "level_2": 3},
            5: {"level_1": 4, "level_2": 3, "level_3": 2},
            6: {"level_1": 4, "level_2": 3, "level_3": 3},
            7: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 1},
            8: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 2},
            9: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 3, "level_5": 1},
            10: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 3, "level_5": 2},
            11: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 3, "level_5": 2, "level_6": 1},
            12: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 3, "level_5": 2, "level_6": 1},
            13: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 3, "level_5": 2, "level_6": 1, "level_7": 1},
            14: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 3, "level_5": 2, "level_6": 1, "level_7": 1},
            15: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 3, "level_5": 2, "level_6": 1, "level_7": 1, "level_8": 1},
            16: {"level_1": 4, "level_2": 3, "level_3": 3, "level_4": 3, "level_5": 2, "level_6": 1, "level_7": 1, "level_8": 1},
            17: {
                "level_1": 4,
                "level_2": 3,
                "level_3": 3,
                "level_4": 3,
                "level_5": 2,
                "level_6": 1,
                "level_7": 1,
                "level_8": 1,
                "level_9": 1,
            },
            18: {
                "level_1": 4,
                "level_2": 3,
                "level_3": 3,
                "level_4": 3,
                "level_5": 3,
                "level_6": 1,
                "level_7": 1,
                "level_8": 1,
                "level_9": 1,
            },
            19: {
                "level_1": 4,
                "level_2": 3,
                "level_3": 3,
                "level_4": 3,
                "level_5": 3,
                "level_6": 2,
                "level_7": 1,
                "level_8": 1,
                "level_9": 1,
            },
            20: {
                "level_1": 4,
                "level_2": 3,
                "level_3": 3,
                "level_4": 3,
                "level_5": 3,
                "level_6": 2,
                "level_7": 2,
                "level_8": 1,
                "level_9": 1,
            },
            17: {
                "level_1": 4,
                "level_2": 3,
                "level_3": 3,
                "level_4": 3,
                "level_5": 2,
                "level_6": 1,
                "level_7": 1,
                "level_8": 1,
                "level_9": 1,
            },
            18: {
                "level_1": 4,
                "level_2": 3,
                "level_3": 3,
                "level_4": 3,
                "level_5": 3,
                "level_6": 1,
                "level_7": 1,
                "level_8": 1,
                "level_9": 1,
            },
            19: {
                "level_1": 4,
                "level_2": 3,
                "level_3": 3,
                "level_4": 3,
                "level_5": 3,
                "level_6": 2,
                "level_7": 1,
                "level_8": 1,
                "level_9": 1,
            },
            20: {
                "level_1": 4,
                "level_2": 3,
                "level_3": 3,
                "level_4": 3,
                "level_5": 3,
                "level_6": 2,
                "level_7": 2,
                "level_8": 1,
                "level_9": 1,
            },
        }

        # Warlock has different progression (Pact Magic)
        warlock_slots = {
            1: {"level_1": 1},
            2: {"level_1": 2},
            3: {"level_2": 2},
            4: {"level_2": 2},
            5: {"level_3": 2},
            6: {"level_3": 2},
            7: {"level_4": 2},
            8: {"level_4": 2},
            9: {"level_5": 2},
            10: {"level_5": 2},
            11: {"level_5": 3},
            12: {"level_5": 3},
            13: {"level_5": 3},
            14: {"level_5": 3},
            15: {"level_5": 3},
            16: {"level_5": 3},
            17: {"level_5": 4},
            18: {"level_5": 4},
            19: {"level_5": 4},
            20: {"level_5": 4},
        }

        # Choose appropriate table
        slots_table = warlock_slots if character.character_class == CharacterClass.WARLOCK else full_caster_slots

        if character.level in slots_table:
            for slot_level, count in slots_table[character.level].items():
                setattr(character.spell_slots, slot_level, count)

    return {
        "level": character.level,
        "hp_increase": hp_increase,
        "new_max_hp": character.max_hit_points,
        "proficiency_bonus": character.proficiency_bonus,
        "features": f"Check class features for level {character.level}",
        "features": f"Check class features for level {character.level}",
    }


async def award_experience(game_state: GameState, xp_awards: dict[str, int]) -> list[tuple[str, dict[str, Any]]]:
async def award_experience(game_state: GameState, xp_awards: dict[str, int]) -> list[tuple[str, dict[str, Any]]]:
    """Award XP to characters and handle level ups."""
    level_ups = []

    for player in game_state.active_players:
        if player.character.name in xp_awards:
            xp_gained = xp_awards[player.character.name]

            # Add to session XP
            if player.character.name not in game_state.session_xp_earned:
                game_state.session_xp_earned[player.character.name] = 0
            game_state.session_xp_earned[player.character.name] += xp_gained

            # Check for level up
            if player.character.add_experience(xp_gained):
                level_up_info = await handle_level_up(player.character)
                level_ups.append((player.character.name, level_up_info))

    return level_ups


async def run_combat_round(game_state: GameState, dm_provider: str, dm_model: str) -> tuple[list[PlayerAction], DMResponse]:
async def run_combat_round(game_state: GameState, dm_provider: str, dm_model: str) -> tuple[list[PlayerAction], DMResponse]:
    """Run a single round of combat."""
    actions = []

    # Increment round counter
    game_state.combat_round += 1

    print(f"\n=== COMBAT ROUND {game_state.combat_round} ===")
    print(f"Initiative Order: {' → '.join(game_state.combat_order)}")

    # Reset turn resources for all combatants at start of round
    for player in game_state.active_players:
        player.character.reset_turn_resources()

    for character_name in game_state.combat_order:
        # Find the player
        current_player: PlayerCharacter | None = next(
            (p for p in game_state.active_players if p.character.name == character_name), None
            (p for p in game_state.active_players if p.character.name == character_name), None
        )

        if current_player:
            # Check if character is conscious
            if current_player.character.hit_points <= 0:
                print(f"\n{character_name} is unconscious!")

                # Death saving throw
                death_save_roll = tool_roll_dice(
                    dice_type=ToolDiceType.D20, num_dice=1, modifier=0, purpose=f"{character_name}'s death saving throw"
                    dice_type=ToolDiceType.D20, num_dice=1, modifier=0, purpose=f"{character_name}'s death saving throw"
                )

                if death_save_roll.total >= 10:
                    current_player.character.death_saves_success += 1
                    print(f"Death Save SUCCESS! ({current_player.character.death_saves_success}/3 successes)")
                else:
                    current_player.character.death_saves_failure += 1
                    print(f"Death Save FAILURE! ({current_player.character.death_saves_failure}/3 failures)")

                # Check for stabilization or death
                if current_player.character.death_saves_success >= 3:
                    print(f"{character_name} is stabilized!")
                    current_player.character.hit_points = 1
                    current_player.character.death_saves_success = 0
                    current_player.character.death_saves_failure = 0
                elif current_player.character.death_saves_failure >= 3:
                    print(f"{character_name} has died!")
                    current_player.is_active = False

                continue

            # Process conditions at start of turn
            for condition in current_player.character.conditions[:]:  # Copy list to allow removal
                if condition.duration_rounds is not None:
                    condition.duration_rounds -= 1
                    if condition.duration_rounds <= 0:
                        current_player.character.conditions.remove(condition)
                        print(f"{character_name} is no longer {condition.name}")

            # Show character status
            print(f"\n{character_name}'s turn:")
            print(f"  HP: {current_player.character.hit_points}/{current_player.character.max_hit_points}")
            print(
                f"  Position: ({current_player.position.x}, {current_player.position.y})"
            ) if current_player.position else print("  Position: Unknown")
            print(
                f"  Position: ({current_player.position.x}, {current_player.position.y})"
            ) if current_player.position else print("  Position: Unknown")
            print(f"  Movement: {current_player.character.movement_remaining} ft")
            if current_player.character.conditions:
                print(f"  Conditions: {', '.join([c.name for c in current_player.character.conditions])}")

            action = await process_player_turn(
                current_player,
                game_state,
                "You are in combat! Choose your action.",
                f"{len([p for p in game_state.active_players if p.character.hit_points > 0])} allies standing",
                f"{len([p for p in game_state.active_players if p.character.hit_points > 0])} allies standing",
            )

            # Process movement if specified
            if action.target_position and current_player.position and game_state.battle_map:
                movement_cost = game_state.battle_map.calculate_movement_cost(current_player.position, action.target_position)
                movement_cost = game_state.battle_map.calculate_movement_cost(current_player.position, action.target_position)

                if movement_cost <= current_player.character.movement_remaining:
                    # Update position
                    old_pos = current_player.position
                    current_player.position = action.target_position
                    current_player.character.movement_remaining -= movement_cost

                    # Update battle map
                    if game_state.battle_map:
                        combatant_info = game_state.battle_map.combatants.get(character_name)
                        if combatant_info:
                            combatant_info.position = action.target_position

                    action.consequences.append(
                        f"Moved from ({old_pos.x}, {old_pos.y}) to ({action.target_position.x}, {action.target_position.y})"
                    )
                    action.consequences.append(
                        f"Moved from ({old_pos.x}, {old_pos.y}) to ({action.target_position.x}, {action.target_position.y})"
                    )
                else:
                    action.consequences.append(
                        f"Not enough movement! Need {movement_cost} ft, have {current_player.character.movement_remaining} ft"
                    )
                    action.consequences.append(
                        f"Not enough movement! Need {movement_cost} ft, have {current_player.character.movement_remaining} ft"
                    )

            # Track resource usage
            if action.action_type == ActionType.ATTACK:
                current_player.character.actions_available -= 1
            elif action.action_type == ActionType.BONUS_ACTION:
                current_player.character.bonus_actions_available -= 1
            elif action.action_type == ActionType.SPELL:
                current_player.character.actions_available -= 1
                # Handle spell slot usage
                if action.resources_used.get("spell_slot_level"):
                    level = action.resources_used["spell_slot_level"]
                    if current_player.character.spell_slots:
                        current_player.character.spell_slots.use_slot(level)

            actions.append(action)

            # Show action to all players
            print(f"\n{character_name}: {action.description}")
            if action.dice_rolls:
                for roll in action.dice_rolls:
                    print(f"  {roll.purpose}: {roll.total}")

            # Process conditions at end of turn (for saves)
            for condition in current_player.character.conditions:
                if condition.save_dc and condition.save_ability:
                    # Prompt for saving throw
                    save_mod = current_player.character.stats.get_saving_throw_modifier(
                        condition.save_ability.value,
                        current_player.character.proficiency_bonus,
                        condition.save_ability in current_player.character.saving_throw_proficiencies,
                        condition.save_ability in current_player.character.saving_throw_proficiencies,
                    )

                    save_result = tool_roll_dice(
                        dice_type=ToolDiceType.D20,
                        num_dice=1,
                        modifier=save_mod,
                        purpose=f"{character_name}'s {condition.save_ability.value} save vs {condition.name}",
                        purpose=f"{character_name}'s {condition.save_ability.value} save vs {condition.name}",
                    )

                    if save_result.total >= condition.save_dc:
                        current_player.character.conditions.remove(condition)
                        print(f"{character_name} saves against {condition.name}!")

    # Generate DM response to all actions
    dm_response = generate_dm_response(
        game_state=game_state,
        recent_actions=actions,
        player_requests={},
        current_phase=GamePhase.COMBAT,
        special_considerations=f"Combat round {game_state.combat_round}. Resolve all actions in initiative order. Track HP changes and conditions.",
        provider=dm_provider,
        model=dm_model,
        model=dm_model,
    )

    # Apply any XP awards
    if dm_response.xp_awards:
        level_ups = await award_experience(game_state, dm_response.xp_awards)
        for char_name, level_info in level_ups:
            print(f"\n{char_name} has reached level {level_info['level']}!")
            print(f"  HP increased by {level_info['hp_increase']} to {level_info['new_max_hp']}")
            print(f"  Proficiency bonus is now +{level_info['proficiency_bonus']}")

    return actions, dm_response


async def run_roleplay_scene(
    game_state: GameState,
    dm_provider: str,
    dm_model: str,
    scene_duration: int = 300,  # 5 minutes default
    scene_duration: int = 300,  # 5 minutes default
) -> tuple[list[RoleplayExchange], DMResponse]:
    """Run a roleplay scene with dynamic interactions."""
    exchanges = []
    start_time = time.time()

    print("\nROLEPLAY SCENE")
    print("(Players can speak at any time. Type 'PAUSE' to pause for actions)")

    # Initial DM scene setting
    initial_response = generate_dm_response(
        game_state=game_state,
        recent_actions=[],
        player_requests={},
        current_phase=GamePhase.ROLEPLAY,
        special_considerations="Set the scene for roleplay",
        provider=dm_provider,
        model=dm_model,
        model=dm_model,
    )

    print(f"\nDM: {initial_response.narration}")

    # Roleplay loop
    while time.time() - start_time < scene_duration:
        # Check for human input with short timeout
        for player in game_state.active_players:
            if player.player_type == PlayerType.HUMAN:
                request = HumanInputRequest(
                    request_type="roleplay",
                    prompt=f"Speak as {player.character.name} (or 'pass'):",
                    context="Roleplay scene in progress",
                    options=[],
                    time_limit=10,  # Quick timeout to keep scene flowing
                    can_interrupt=True,
                    can_interrupt=True,
                )

                human_input = await wait_for_human_input(request)

                if human_input and human_input.lower() not in ["pass", "none", ""]:
                    if human_input.upper() == "PAUSE":
                        print("Scene paused for actions")
                        break

                    # Create roleplay exchange
                    exchange = RoleplayExchange(
                        speaker=player.character.name,
                        dialogue=human_input,
                        tone="conversational",
                        actions=None,
                        target_audience=[p.character.name for p in game_state.active_players],
                        requires_response=True,
                        skill_check=None,
                        skill_check=None,
                    )
                    exchanges.append(exchange)

        # AI players respond to recent exchanges
        for player in game_state.active_players:
            if player.player_type == PlayerType.AI and len(exchanges) > 0 and random.random() < 0.3:
                # Only respond 30% of the time to avoid overwhelming dialogue
                recent_dialogue = "\n".join(
                    [
                        f"{ex.speaker}: {ex.dialogue}"
                        for ex in exchanges[-3:]  # Last 3 exchanges
                    ]
                )
                recent_dialogue = "\n".join(
                    [
                        f"{ex.speaker}: {ex.dialogue}"
                        for ex in exchanges[-3:]  # Last 3 exchanges
                    ]
                )

                ai_dialogue = generate_character_dialogue(
                    character_name=player.character.name,
                    personality=" ".join(player.character.personality_traits),
                    speaking_style=player.personality_prompt or "Natural speech",
                    current_mood="Engaged",
                    relationships="Party member",
                    scene=game_state.scene_description,
                    speaking_to="The party",
                    previous_dialogue=recent_dialogue,
                    character_goal="Contribute to the conversation",
                    emotional_state="Normal",
                    provider=player.provider or "openai",
                    model=player.model or "gpt-4o-mini",
                    model=player.model or "gpt-4o-mini",
                )

                exchanges.append(ai_dialogue)
                print(f"\n{ai_dialogue.speaker}: {ai_dialogue.dialogue}")
                if ai_dialogue.actions:
                    print(f"*{ai_dialogue.actions}*")

    # Final DM response
    dm_response = generate_dm_response(
        game_state=game_state,
        recent_actions=[],
        player_requests={},
        current_phase=GamePhase.ROLEPLAY,
        special_considerations=f"Conclude roleplay scene with {len(exchanges)} exchanges",
        provider=dm_provider,
        model=dm_model,
        model=dm_model,
    )

    return exchanges, dm_response


async def initialize_combat(
    game_state: GameState,
    dm_provider: str,
    dm_model: str,
    enemies: list[tuple[str, str]] = None,  # List of (name, monster_type)
    enemies: list[tuple[str, str]] = None,  # List of (name, monster_type)
) -> tuple[list[str], BattleMap]:
    """Initialize combat by rolling initiative and setting up the battle map."""
    print("\n⚔️ COMBAT INITIATED! ⚔️")
    print("Rolling initiative...")

    initiative_order = []

    # Create battle map
    battle_map = BattleMap(
        width=30,  # 150 feet
        height=30,  # 150 feet
        combatants={},
        obstacles=[],
        difficult_terrain=[],
        difficult_terrain=[],
    )

    # Roll initiative for players
    for i, player in enumerate(game_state.active_players):
        # Calculate initiative modifier
        dex_mod = player.character.stats.get_modifier("dexterity")
        init_mod = dex_mod + player.character.initiative_bonus

        # Roll initiative
        init_roll = tool_roll_dice(
            dice_type=ToolDiceType.D20, modifier=init_mod, purpose=f"Initiative for {player.character.name}"
            dice_type=ToolDiceType.D20, modifier=init_mod, purpose=f"Initiative for {player.character.name}"
        )

        initiative_order.append((player.character.name, init_roll.total))
        print(format_roll_result(init_roll))

        # Set initial position for players (left side of map)
        position = Position(x=5, y=10 + (i * 2), z=0)
        player.position = position

        # Add to battle map
        battle_map.combatants[player.character.name] = CombatantInfo(
            name=player.character.name,
            position=position,
            initiative=init_roll.total,
            is_player=True,
            is_surprised=False,
            has_acted=False,
            ac=player.character.armor_class,
            current_hp=player.character.hit_points,
            max_hp=player.character.max_hit_points,
            max_hp=player.character.max_hit_points,
        )

    # Roll initiative for enemies
    if enemies:
        for i, (enemy_name, monster_type) in enumerate(enemies):
            try:
                # Look up monster stats
                monster = await get_monster_info(monster_type)

                # Calculate initiative
                dex_mod = (monster.dexterity - 10) // 2
                init_roll = tool_roll_dice(dice_type=ToolDiceType.D20, modifier=dex_mod, purpose=f"Initiative for {enemy_name}")
                init_roll = tool_roll_dice(dice_type=ToolDiceType.D20, modifier=dex_mod, purpose=f"Initiative for {enemy_name}")

                initiative_order.append((enemy_name, init_roll.total))
                print(format_roll_result(init_roll))

                # Set initial position for enemies (right side of map)
                position = Position(x=25, y=10 + (i * 2), z=0)

                # Add to battle map
                battle_map.combatants[enemy_name] = CombatantInfo(
                    name=enemy_name,
                    position=position,
                    initiative=init_roll.total,
                    is_player=False,
                    is_surprised=False,
                    has_acted=False,
                    ac=monster.armor_class[0]["value"] if isinstance(monster.armor_class, list) else monster.armor_class,
                    current_hp=monster.hit_points,
                    max_hp=monster.hit_points,
                    max_hp=monster.hit_points,
                )

            except ValueError as e:
                print(f"Error loading {monster_type}: {e}")
                # Use default stats
                init_roll = tool_roll_dice(dice_type=ToolDiceType.D20, modifier=0, purpose=f"Initiative for {enemy_name}")
                init_roll = tool_roll_dice(dice_type=ToolDiceType.D20, modifier=0, purpose=f"Initiative for {enemy_name}")

                initiative_order.append((enemy_name, init_roll.total))

                position = Position(x=25, y=10 + (i * 2), z=0)
                battle_map.combatants[enemy_name] = CombatantInfo(
                    name=enemy_name,
                    position=position,
                    initiative=init_roll.total,
                    is_player=False,
                    is_surprised=False,
                    has_acted=False,
                    ac=12,  # Default AC
                    current_hp=20,  # Default HP
                    max_hp=20,
                    max_hp=20,
                )

    # Sort by initiative (highest first)
    initiative_order.sort(key=lambda x: x[1], reverse=True)

    # Display battle map
    print("\n📍 BATTLE MAP:")
    print("Players:")
    for name, info in battle_map.combatants.items():
        if info.is_player:
            print(f"  {name}: Position ({info.position.x}, {info.position.y})")

    print("\nEnemies:")
    for name, info in battle_map.combatants.items():
        if not info.is_player:
            print(f"  {name}: Position ({info.position.x}, {info.position.y}), AC {info.ac}, HP {info.current_hp}/{info.max_hp}")

    # Return just the names in order
    return [name for name, _ in initiative_order], battle_map


async def dnd_game_master(
    campaign_name: str = "The Lost Mines of Phandelver",
    players: list[PlayerCharacter] = None,
    starting_location: str = "The town of Neverwinter",
    campaign_tone: str = "Classic fantasy adventure",
    dm_style: str = "Balanced storyteller",
    dm_provider: str = "openai",
    dm_model: str = "gpt-4o",
    session_length: int = 3600,  # 1 hour default
    enable_combat: bool = True,
    enable_roleplay: bool = True,
    enable_exploration: bool = True,
    initial_scene: str = None,
    quest_hooks: list[str] = None,
    encounter_tables: dict[str, list[tuple[str, str]]] = None,
    # New persistence parameters
    enable_persistence: bool = True,
    db_path: str | None = None,
    load_session_id: str | None = None,
    auto_save_interval: int = 300,  # Auto-save every 5 minutes
    auto_save_interval: int = 300,  # Auto-save every 5 minutes
) -> GameState:
    """
    Run a D&D game session with human and AI players.

    This agent acts as a Dungeon Master, orchestrating gameplay between human
    and AI players using different models. It manages combat, roleplay, and
    exploration with dynamic turn-based interactions.

    Args:
        campaign_name: Name of the D&D campaign
        players: List of player characters (human and AI)
        starting_location: Where the adventure begins
        campaign_tone: Tone and style of the campaign
        dm_style: DM personality and approach
        dm_provider: LLM provider for the DM
        dm_model: Model to use for DM (e.g., "gpt-4o", "o1-preview")
        session_length: Maximum session length in seconds
        enable_combat: Whether to include combat encounters
        enable_roleplay: Whether to include roleplay scenes
        enable_exploration: Whether to include exploration
        initial_scene: Custom opening scene description
        quest_hooks: List of potential quest hooks to introduce
        encounter_tables: Dict of location to possible encounters
        enable_persistence: Whether to enable SQLite state persistence
        db_path: Custom database path (auto-generated if None)
        load_session_id: Session ID to load and continue
        auto_save_interval: How often to auto-save (in seconds)

    Returns:
        Final GameState after the session
    """

    # Initialize or load game state
    if enable_persistence and load_session_id and db_path:
        # Try to load existing session
        print(f"Loading session {load_session_id}...")
        game_state = await load_game_state(load_session_id, db_path)

        if game_state:
            print(f"Resumed campaign: {game_state.campaign_name}")
            print(f"Current location: {game_state.location}")
            print(f"Days elapsed: {game_state.days_elapsed}")
            print(f"Party: {', '.join([p.character.name for p in game_state.active_players])}")
        else:
            print(f"Session {load_session_id} not found. Starting new session.")
            game_state = None
    else:
        game_state = None

    # Create new game state if not loaded
    if game_state is None:
        game_state = GameState(
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            campaign_name=campaign_name,
            current_phase=GamePhase.EXPLORATION,
            location=starting_location,
            scene_description=initial_scene or "The adventure begins...",
            active_players=players or [],
            npcs_present=[],
            combat_round=0,
            combat_order=[],
            battle_map=None,
            current_encounter=None,
            recent_events=[],
            quest_status={},
            world_state={},
            session_xp_earned={},
            game_time="Morning",
            days_elapsed=0,
            long_rest_available=True,
            long_rest_available=True,
        )

        # Add quest hooks if provided
        if quest_hooks:
            for i, hook in enumerate(quest_hooks):
                game_state.quest_status[f"quest_{i + 1}"] = f"Available: {hook}"
                game_state.quest_status[f"quest_{i + 1}"] = f"Available: {hook}"

    # Initialize database if persistence is enabled
    if enable_persistence:
        if not db_path:
            db_path = await initialize_campaign_database(campaign_name)
        else:
            # Ensure database is initialized
            await initialize_campaign_database(campaign_name, db_path)

        print(f"Campaign database: {db_path}")

        # Save initial state
        await save_game_state(game_state, db_path)

    print(f"Welcome to {campaign_name}!")
    print(f"Session ID: {game_state.session_id}")
    print(f"DM: {dm_model} ({dm_style})")
    print(f"Players: {', '.join([p.character.name for p in game_state.active_players])}")
    print("-" * 50)

    session_start = time.time()
    last_save_time = time.time()

    # Main game loop
    while time.time() - session_start < session_length:
        current_phase = game_state.current_phase

        if current_phase == GamePhase.EXPLORATION and enable_exploration:
            print("\nEXPLORATION PHASE")

            # Get actions from all players
            actions = []
            for player in game_state.active_players:
                action = await process_player_turn(
                    player,
                    game_state,
                    "What would you like to do?",
                    f"{len([p for p in game_state.active_players if p.character.hit_points > 0])} allies standing",
                    f"{len([p for p in game_state.active_players if p.character.hit_points > 0])} allies standing",
                )
                actions.append(action)

            # DM responds
            dm_response = generate_dm_response(
                game_state=game_state,
                recent_actions=actions,
                player_requests={},
                current_phase=current_phase,
                provider=dm_provider,
                model=dm_model,
                campaign_name=campaign_name,
                campaign_tone=campaign_tone,
                dm_style=dm_style,
                dm_style=dm_style,
            )

            print(f"\nDM: {dm_response.narration}")

            # Update game state based on response
            if dm_response.phase_change:
                game_state.current_phase = dm_response.phase_change

                # Initialize combat if transitioning to combat
                if dm_response.phase_change == GamePhase.COMBAT:
                    # Check for encounter table for current location
                    enemies: list[tuple[str, str]] | None = None
                    if encounter_tables and game_state.location in encounter_tables:
                        # Randomly select an encounter from the table
                        encounter_list = encounter_tables[game_state.location]
                        enemies = [random.choice(encounter_list)]
                    elif dm_response.battle_map_update and dm_response.battle_map_update.combatants:
                        # Extract enemies from DM response
                        enemies = []
                        for name, info in dm_response.battle_map_update.combatants.items():
                            if not info.is_player:
                                # Try to determine monster type from name
                                monster_type = name.lower().split()[-1]  # Last word often indicates type
                                enemies.append((name, monster_type))

                    if enemies:
                        initiative_order, battle_map = await initialize_combat(game_state, dm_provider, dm_model, enemies)
                        initiative_order, battle_map = await initialize_combat(game_state, dm_provider, dm_model, enemies)
                        game_state.combat_order = initiative_order
                        game_state.battle_map = battle_map

                        # Calculate encounter XP
                        monster_types = [e[1] for e in enemies]
                        party_levels = [p.character.level for p in game_state.active_players]

                        xp_calc = await calculate_encounter_xp(monster_types, len(game_state.active_players), party_levels)
                        xp_calc = await calculate_encounter_xp(monster_types, len(game_state.active_players), party_levels)

                        # Set encounter info
                        game_state.current_encounter = EncounterInfo(
                            name=dm_response.narration.split('.')[0],  # First sentence as name
                            difficulty="Unknown",  # Will be set by XP calc
                            enemies=monster_types,
                            total_xp=0,  # Will be calculated
                            environment=game_state.location,
                            objectives=["Survive the encounter"],
                            objectives=["Survive the encounter"],
                        )

        elif current_phase == GamePhase.COMBAT and enable_combat:
            # Run combat round
            actions, dm_response = await run_combat_round(game_state, dm_provider, dm_model)
            actions, dm_response = await run_combat_round(game_state, dm_provider, dm_model)

            print(f"\nDM: {dm_response.narration}")

            # Save combat log if persistence is enabled
            if enable_persistence and db_path:
                await save_combat_log(game_state.session_id, game_state.combat_round, actions, dm_response, db_path)
                await save_combat_log(game_state.session_id, game_state.combat_round, actions, dm_response, db_path)

            # Check for combat end
            if "combat ends" in dm_response.narration.lower():
                game_state.current_phase = GamePhase.EXPLORATION
                game_state.combat_order = []

        elif current_phase == GamePhase.ROLEPLAY and enable_roleplay:
            # Run roleplay scene
            exchanges, dm_response = await run_roleplay_scene(game_state, dm_provider, dm_model)
            exchanges, dm_response = await run_roleplay_scene(game_state, dm_provider, dm_model)

            print(f"\nDM: {dm_response.narration}")

            # Transition back to exploration
            game_state.current_phase = GamePhase.EXPLORATION

        # Add event to history
        event = GameEvent(
            event_type=current_phase.value,
            description=dm_response.narration[:200] + "...",
            participants=[p.character.name for p in game_state.active_players],
            location=game_state.location,
            timestamp=datetime.now(),
            consequences=dm_response.scene_changes.split(", ") if dm_response.scene_changes else [],
            xp_awarded=dm_response.xp_awards,
            xp_awarded=dm_response.xp_awards,
        )
        game_state.recent_events.append(event)

        # Update location if mentioned in scene changes
        if dm_response.scene_changes and "location:" in dm_response.scene_changes.lower():
            # Extract new location from scene changes
            location_start = dm_response.scene_changes.lower().find("location:") + 9
            new_location = dm_response.scene_changes[location_start:].split(",")[0].strip()
            if new_location:
                game_state.location = new_location

        # Award XP if any
        if dm_response.xp_awards:
            level_ups = await award_experience(game_state, dm_response.xp_awards)
            for character_name, level_up_info in level_ups:
                print(f"\n🎉 {character_name} leveled up to level {level_up_info['new_level']}!")

        # Auto-save if enabled and interval has passed
        if enable_persistence and db_path and (time.time() - last_save_time) >= auto_save_interval:
            await save_game_state(game_state, db_path)
            last_save_time = time.time()
            print("\n[Auto-saved]")

        # Check for session end conditions
        if any(keyword in dm_response.narration.lower() for keyword in ["session ends", "to be continued", "fade to black"]):
            print("\nSession ending...")
            break

        # Brief pause between phases
        await asyncio.sleep(3)

    # Final save if persistence is enabled
    if enable_persistence and db_path:
        await save_game_state(game_state, db_path)
        print("\n[Session saved]")

        # Create backup after session
        backup_path = await create_campaign_backup(db_path)
        print(f"[Backup created: {backup_path}]")

    print("\nSession Complete!")
    print(f"Duration: {(time.time() - session_start) / 60:.1f} minutes")
    print(f"Events: {len(game_state.recent_events)}")
    print(f"Session ID: {game_state.session_id}")

    return game_state


async def dnd_game_master_stream(
    campaign_name: str = "The Lost Mines of Phandelver",
    players: list[PlayerCharacter] = None,
    create_sample_party: bool = True,
    **kwargs,
    **kwargs,
) -> AsyncGenerator[str, None]:
    """Stream the D&D game session with real-time updates.

    Args:
        campaign_name: Name of the campaign
        players: List of player characters
        create_sample_party: Whether to create sample players if none provided
        **kwargs: Additional arguments passed to dnd_game_master
    """

    yield f"**{campaign_name}** \n\n"
    yield "Initializing game session...\n\n"

    # Create sample players only if requested and none provided
    if not players and create_sample_party:
        yield "Creating sample party...\n\n"

        # Create spell slots for casters
        wizard_spell_slots = SpellSlots(
            level_1=4,
            level_2=2,
            level_3=0,
            level_4=0,
            level_5=0,
            level_6=0,
            level_7=0,
            level_8=0,
            level_9=0,
            level_1_used=0,
            level_2_used=0,
            level_3_used=0,
            level_4_used=0,
            level_5_used=0,
            level_6_used=0,
            level_7_used=0,
            level_8_used=0,
            level_9_used=0,
            level_1=4,
            level_2=2,
            level_3=0,
            level_4=0,
            level_5=0,
            level_6=0,
            level_7=0,
            level_8=0,
            level_9=0,
            level_1_used=0,
            level_2_used=0,
            level_3_used=0,
            level_4_used=0,
            level_5_used=0,
            level_6_used=0,
            level_7_used=0,
            level_8_used=0,
            level_9_used=0,
        )

        players = [
            PlayerCharacter(
                character=CharacterSheet(
                    name="Thorin Ironforge",
                    race="Dwarf",
                    character_class=CharacterClass.FIGHTER,
                    level=3,
                    experience_points=900,
                    stats=CharacterStats(strength=16, dexterity=12, constitution=15, intelligence=10, wisdom=13, charisma=8),
                    stats=CharacterStats(strength=16, dexterity=12, constitution=15, intelligence=10, wisdom=13, charisma=8),
                    hit_points=28,
                    max_hit_points=28,
                    temp_hit_points=0,
                    hit_dice_remaining=3,
                    armor_class=16,
                    proficiency_bonus=2,
                    speed=25,  # Dwarf speed
                    initiative_bonus=0,
                    skill_proficiencies=[SkillType.ATHLETICS, SkillType.INTIMIDATION],
                    saving_throw_proficiencies=[AbilityType.STRENGTH, AbilityType.CONSTITUTION],
                    actions_available=1,
                    bonus_actions_available=1,
                    reactions_available=1,
                    movement_remaining=25,
                    spell_slots=None,
                    inventory=[
                        InventoryItem(
                            name="Battleaxe",
                            equipped=True,
                            quantity=1,
                            weight=4.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="A sturdy battleaxe",
                        ),
                        InventoryItem(
                            name="Shield",
                            equipped=True,
                            quantity=1,
                            weight=6.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="A metal shield",
                        ),
                        InventoryItem(
                            name="Chain Mail",
                            equipped=True,
                            quantity=1,
                            weight=55.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="Heavy armor",
                        ),
                        InventoryItem(
                            name="Battleaxe",
                            equipped=True,
                            quantity=1,
                            weight=4.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="A sturdy battleaxe",
                        ),
                        InventoryItem(
                            name="Shield",
                            equipped=True,
                            quantity=1,
                            weight=6.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="A metal shield",
                        ),
                        InventoryItem(
                            name="Chain Mail",
                            equipped=True,
                            quantity=1,
                            weight=55.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="Heavy armor",
                        ),
                    ],
                    equipped_armor="Chain Mail",
                    equipped_weapons=["Battleaxe"],
                    attunement_slots_used=0,
                    exhaustion_level=0,
                    death_saves_success=0,
                    death_saves_failure=0,
                    background="Soldier",
                    personality_traits=["Gruff but loyal", "Loves a good fight"],
                    ideals=["Honor in battle"],
                    bonds=["My clan is everything"],
                    flaws=["Too stubborn for my own good"],
                    flaws=["Too stubborn for my own good"],
                ),
                player_type=PlayerType.AI,
                model="gpt-4o-mini",
                provider="openai",
                personality_prompt="Gruff dwarf warrior who speaks in a Scottish accent",
                is_active=True,
                last_action_time=None,
                position=None,
                position=None,
            ),
            PlayerCharacter(
                character=CharacterSheet(
                    name="Lyra Moonwhisper",
                    race="Elf",
                    character_class=CharacterClass.WIZARD,
                    level=3,
                    experience_points=900,
                    stats=CharacterStats(strength=8, dexterity=14, constitution=12, intelligence=16, wisdom=13, charisma=10),
                    stats=CharacterStats(strength=8, dexterity=14, constitution=12, intelligence=16, wisdom=13, charisma=10),
                    hit_points=14,
                    max_hit_points=14,
                    temp_hit_points=0,
                    hit_dice_remaining=3,
                    armor_class=12,
                    proficiency_bonus=2,
                    speed=30,  # Elf speed
                    initiative_bonus=0,
                    skill_proficiencies=[SkillType.ARCANA, SkillType.INVESTIGATION],
                    saving_throw_proficiencies=[AbilityType.INTELLIGENCE, AbilityType.WISDOM],
                    actions_available=1,
                    bonus_actions_available=1,
                    reactions_available=1,
                    movement_remaining=30,
                    spell_slots=wizard_spell_slots,
                    spells_known=["Magic Missile", "Shield", "Detect Magic", "Burning Hands", "Mage Armor"],
                    cantrips_known=["Fire Bolt", "Mage Hand", "Prestidigitation"],
                    inventory=[
                        InventoryItem(
                            name="Spellbook",
                            equipped=True,
                            quantity=1,
                            weight=3.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="A wizard's spellbook",
                        ),
                        InventoryItem(
                            name="Wand",
                            equipped=True,
                            magical=True,
                            quantity=1,
                            weight=1.0,
                            attunement_required=False,
                            attuned=False,
                            description="A magical wand",
                        ),
                        InventoryItem(
                            name="Component Pouch",
                            equipped=True,
                            quantity=1,
                            weight=2.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="Spell components",
                        ),
                        InventoryItem(
                            name="Spellbook",
                            equipped=True,
                            quantity=1,
                            weight=3.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="A wizard's spellbook",
                        ),
                        InventoryItem(
                            name="Wand",
                            equipped=True,
                            magical=True,
                            quantity=1,
                            weight=1.0,
                            attunement_required=False,
                            attuned=False,
                            description="A magical wand",
                        ),
                        InventoryItem(
                            name="Component Pouch",
                            equipped=True,
                            quantity=1,
                            weight=2.0,
                            attunement_required=False,
                            attuned=False,
                            magical=False,
                            description="Spell components",
                        ),
                    ],
                    equipped_armor=None,
                    equipped_weapons=["Wand"],
                    attunement_slots_used=0,
                    exhaustion_level=0,
                    death_saves_success=0,
                    death_saves_failure=0,
                    background="Sage",
                    personality_traits=["Curious about magic", "Cautious in combat"],
                    ideals=["Knowledge is power"],
                    bonds=["I seek lost magical knowledge"],
                    flaws=["I overlook obvious solutions in favor of complicated ones"],
                    flaws=["I overlook obvious solutions in favor of complicated ones"],
                ),
                player_type=PlayerType.AI,
                model="claude-3-5-sonnet-20241022",
                provider="anthropic",
                personality_prompt="Scholarly elf wizard who speaks eloquently",
                is_active=True,
                last_action_time=None,
                position=None,
            ),
                position=None,
            ),
        ]
    elif not players:
        yield "**No players provided!**\n"
        yield "Please provide a list of PlayerCharacter objects or set create_sample_party=True\n"
        return

    yield "**Players:**\n"
    for player in players:
        yield f"- {player.character.name} ({player.character.race} {player.character.character_class.value})"
        if player.player_type == PlayerType.AI:
            yield f" [AI: {player.model}]"
        else:
            yield " [Human Player]"
        yield "\n"

    yield "\n**Starting Adventure...**\n\n"

    # Run abbreviated game session for streaming
    game_state = GameState(
        session_id=f"stream_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        campaign_name=campaign_name,
        current_phase=GamePhase.EXPLORATION,
        location=kwargs.get('starting_location', "The Sleeping Giant Tavern"),
        scene_description=kwargs.get('initial_scene', "The tavern is dimly lit, filled with the smell of ale and pipe smoke."),
        active_players=players,
        npcs_present=["Toblen Stonehill (Innkeeper)"],
        combat_round=0,
        combat_order=[],
        battle_map=None,
        current_encounter=None,
        recent_events=[],
        quest_status={},
        world_state={},
        session_xp_earned={},
        game_time="Morning",
        days_elapsed=0,
        long_rest_available=True,
        long_rest_available=True,
    )

    # Add quest hooks if provided
    if 'quest_hooks' in kwargs and kwargs['quest_hooks']:
        for i, hook in enumerate(kwargs['quest_hooks']):
            game_state.quest_status[f"quest_{i + 1}"] = f"Available: {hook}"
            game_state.quest_status[f"quest_{i + 1}"] = f"Available: {hook}"

    # Generate opening scene
    dm_response = generate_dm_response(
        game_state=game_state,
        recent_actions=[],
        player_requests={},
        current_phase=GamePhase.EXPLORATION,
        special_considerations="Opening scene of the adventure",
        provider=kwargs.get("dm_provider", "openai"),
        model=kwargs.get("dm_model", "gpt-4o"),
        model=kwargs.get("dm_model", "gpt-4o"),
    )

    yield f"**DM:** {dm_response.narration}\n\n"

    # Simulate a few turns
    for i in range(min(3, len(players))):  # Show up to 3 player turns
        yield f"**Round {i + 1}**\n\n"
        yield f"**Round {i + 1}**\n\n"

        player = players[i % len(players)]
        if player.player_type == PlayerType.AI:
            # Prepare character data for the example
            position_str = "Not in combat"
            conditions_str = "None"
            proficient_skills_str = (
                ", ".join([s.value for s in player.character.skill_proficiencies])
                if player.character.skill_proficiencies
                else "None"
            )
            saving_throws_str = (
                ", ".join([s.value for s in player.character.saving_throw_proficiencies])
                if player.character.saving_throw_proficiencies
                else "None"
            )
            available_attacks_str = (
                ", ".join(player.character.equipped_weapons) if player.character.equipped_weapons else "Unarmed strike"
            )
            proficient_skills_str = (
                ", ".join([s.value for s in player.character.skill_proficiencies])
                if player.character.skill_proficiencies
                else "None"
            )
            saving_throws_str = (
                ", ".join([s.value for s in player.character.saving_throw_proficiencies])
                if player.character.saving_throw_proficiencies
                else "None"
            )
            available_attacks_str = (
                ", ".join(player.character.equipped_weapons) if player.character.equipped_weapons else "Unarmed strike"
            )
            spells_known_str = ", ".join(player.character.spells_known[:3]) if player.character.spells_known else "None"

            # Calculate spell slots string
            spell_slots_str = "N/A"
            if player.character.spell_slots:
                slots_available = []
                for level in range(1, 10):
                    available = player.character.spell_slots.get_available_slots(level)
                    if available > 0:
                        slots_available.append(f"L{level}: {available}")
                if slots_available:
                    spell_slots_str = ", ".join(slots_available[:2])  # Show first 2 levels

            # Generate AI action
            action = generate_ai_player_action(
                character_name=player.character.name,
                level=player.character.level,
                race=player.character.race,
                character_class=player.character.character_class.value,
                personality=" ".join(player.character.personality_traits),
                background=player.character.background,
                stats=str(player.character.stats),
                current_hp=player.character.hit_points,
                max_hp=player.character.max_hit_points,
                movement_remaining=player.character.movement_remaining,
                actions_available=player.character.actions_available,
                bonus_actions_available=player.character.bonus_actions_available,
                reactions_available=player.character.reactions_available,
                spell_slots=spell_slots_str,
                conditions=conditions_str,
                position=position_str,
                proficient_skills=proficient_skills_str,
                saving_throws=saving_throws_str,
                available_attacks=available_attacks_str,
                spells_known=spells_known_str,
                scene_description=game_state.scene_description,
                dm_prompt="What do you do?",
                party_status="Ready for adventure",
                your_position="In the tavern",
                enemies_visible="None",
                available_options="Any appropriate action",
                provider=player.provider or "openai",
                model=player.model or "gpt-4o-mini",
                model=player.model or "gpt-4o-mini",
            )

            yield f"**{player.character.name}:** {action.description}\n\n"
            await asyncio.sleep(1)  # Dramatic pause
        else:
            yield f"**{player.character.name}:** [Awaiting human input...]\n\n"

    yield "\n*...Adventure continues with dynamic interactions between human and AI players...*\n"

    yield "\n**Enhanced Features:**\n"
    yield "- Fair dice rolling with transparent results and proper modifiers\n"
    yield "- Official D&D 5e rules integration via API\n"
    yield "- Multi-model orchestration (different AI models for different characters)\n"
    yield "- Human-in-the-loop gameplay with interrupt capabilities\n"
    yield "- Turn-based combat with initiative tracking and action economy\n"
    yield "- Movement and positioning on battle maps with distance calculations\n"
    yield "- Spell slot tracking and component requirements\n"
    yield "- Condition management with duration and saving throws\n"
    yield "- Death saving throws at 0 HP\n"
    yield "- Experience and leveling system with automatic level-ups\n"
    yield "- Exhaustion tracking and rest mechanics\n"
    yield "- Proper ability modifiers for all rolls\n"
    yield "- Skill proficiencies and expertise\n"
    yield "- Inventory management with equipped items and attunement\n"
    yield "- Dynamic roleplay scenes with natural conversation flow\n"
    yield "- Encounter difficulty calculations and XP awards\n"
    yield "- Persistent game state and session history\n"
    yield "- Customizable DM styles and campaign tones\n"
    yield "- Real-time rule lookups for spells, monsters, and equipment\n"

    # Only show examples if we have players
    if players and len(players) > 0:
        yield "\n**Example Tools in Action:**\n"

        # Use first player for examples
        example_player = players[0]

        # Show an example ability check
        yield "\n*Perception Check:*\n"
        example_check = await roll_ability_check(
            character_name=example_player.character.name,
            ability="wisdom",
            skill="perception",
            modifier=example_player.character.stats.get_modifier("wisdom"),
            proficiency_bonus=example_player.character.proficiency_bonus,
            is_proficient=SkillType.PERCEPTION in example_player.character.skill_proficiencies,
            is_proficient=SkillType.PERCEPTION in example_player.character.skill_proficiencies,
        )
        yield f"{example_check}\n"

        # Show an example attack if they have a weapon
        if example_player.character.equipped_weapons:
            yield "\n*Attack Roll:*\n"
            # Calculate attack bonus based on character
            if example_player.character.character_class in [
                CharacterClass.FIGHTER,
                CharacterClass.BARBARIAN,
                CharacterClass.PALADIN,
            ]:
            if example_player.character.character_class in [
                CharacterClass.FIGHTER,
                CharacterClass.BARBARIAN,
                CharacterClass.PALADIN,
            ]:
                attack_stat = example_player.character.stats.get_modifier("strength")
            else:
                attack_stat = example_player.character.stats.get_modifier("dexterity")

            attack_bonus = attack_stat + example_player.character.proficiency_bonus

            example_attack = await roll_attack(
                attacker_name=example_player.character.name,
                target_ac=15,
                attack_bonus=attack_bonus,
                damage_dice=f"1d8+{attack_stat}",
                damage_type="slashing",
                weapon_name=example_player.character.equipped_weapons[0],
                weapon_name=example_player.character.equipped_weapons[0],
            )
            yield f"{example_attack}\n"

        # Show movement calculation
        yield "\n*Movement Check:*\n"
        example_movement = await calculate_movement(
            character_name=example_player.character.name,
            from_position=(5, 10),
            to_position=(8, 13),
            base_speed=example_player.character.speed,
            movement_used=0,
            movement_used=0,
        )
        yield f"{example_movement}\n"

    yield "\n**Ready to run epic D&D adventures with proper rules enforcement!**"


# Helper function to create characters easily
def create_character(
    name: str,
    race: str,
    character_class: CharacterClass | str,
    level: int = 1,
    stats: dict[str, int] = None,
    background: str = "Adventurer",
    personality: list[str] = None,
    player_type: PlayerType = PlayerType.HUMAN,
    ai_model: str = None,
    ai_provider: str = None,
    ai_personality: str = None,
    ai_personality: str = None,
) -> PlayerCharacter:
    """
    Helper function to create a D&D character easily.

    Args:
        name: Character name
        race: Character race (e.g., "Human", "Elf", "Dwarf")
        character_class: Character class (enum or string)
        level: Character level (1-20)
        stats: Dict of ability scores (defaults to standard array)
        background: Character background
        personality: List of personality traits
        player_type: Whether this is a human or AI player
        ai_model: Model to use for AI players
        ai_provider: Provider for AI players
        ai_personality: Personality prompt for AI players

    Returns:
        PlayerCharacter ready to use in the game
    """
    # Convert string to enum if needed
    if isinstance(character_class, str):
        character_class = CharacterClass(character_class.lower())

    # Default stats if not provided (standard array)
    if stats is None:
        stats = {"strength": 15, "dexterity": 14, "constitution": 13, "intelligence": 12, "wisdom": 10, "charisma": 8}
        stats = {"strength": 15, "dexterity": 14, "constitution": 13, "intelligence": 12, "wisdom": 10, "charisma": 8}

    # Create CharacterStats
    char_stats = CharacterStats(**stats)

    # Calculate derived values
    con_modifier = char_stats.get_modifier("constitution")

    # Hit die by class
    hit_die_map = {
        CharacterClass.BARBARIAN: 12,
        CharacterClass.FIGHTER: 10,
        CharacterClass.PALADIN: 10,
        CharacterClass.RANGER: 10,
        CharacterClass.BARD: 8,
        CharacterClass.CLERIC: 8,
        CharacterClass.DRUID: 8,
        CharacterClass.MONK: 8,
        CharacterClass.ROGUE: 8,
        CharacterClass.WARLOCK: 8,
        CharacterClass.SORCERER: 6,
        CharacterClass.WIZARD: 6,
    }

    hit_die = hit_die_map.get(character_class, 8)

    # Calculate HP
    max_hp = hit_die + con_modifier  # Level 1
    for _ in range(1, level):
        max_hp += (hit_die // 2 + 1) + con_modifier

    # Proficiency bonus
    proficiency_bonus = 2 + ((level - 1) // 4)

    # Default skills by class
    default_skills = {
        CharacterClass.FIGHTER: [SkillType.ATHLETICS, SkillType.INTIMIDATION],
        CharacterClass.WIZARD: [SkillType.ARCANA, SkillType.INVESTIGATION],
        CharacterClass.ROGUE: [SkillType.STEALTH, SkillType.SLEIGHT_OF_HAND],
        CharacterClass.CLERIC: [SkillType.RELIGION, SkillType.MEDICINE],
        CharacterClass.RANGER: [SkillType.SURVIVAL, SkillType.NATURE],
        CharacterClass.BARD: [SkillType.PERFORMANCE, SkillType.PERSUASION],
        CharacterClass.BARBARIAN: [SkillType.ATHLETICS, SkillType.SURVIVAL],
        CharacterClass.DRUID: [SkillType.NATURE, SkillType.ANIMAL_HANDLING],
        CharacterClass.MONK: [SkillType.ACROBATICS, SkillType.INSIGHT],
        CharacterClass.PALADIN: [SkillType.ATHLETICS, SkillType.RELIGION],
        CharacterClass.SORCERER: [SkillType.ARCANA, SkillType.DECEPTION],
        CharacterClass.WARLOCK: [SkillType.ARCANA, SkillType.DECEPTION],
    }

    # Saving throw proficiencies by class
    save_proficiencies = {
        CharacterClass.FIGHTER: [AbilityType.STRENGTH, AbilityType.CONSTITUTION],
        CharacterClass.WIZARD: [AbilityType.INTELLIGENCE, AbilityType.WISDOM],
        CharacterClass.ROGUE: [AbilityType.DEXTERITY, AbilityType.INTELLIGENCE],
        CharacterClass.CLERIC: [AbilityType.WISDOM, AbilityType.CHARISMA],
        CharacterClass.RANGER: [AbilityType.STRENGTH, AbilityType.DEXTERITY],
        CharacterClass.BARD: [AbilityType.DEXTERITY, AbilityType.CHARISMA],
        CharacterClass.BARBARIAN: [AbilityType.STRENGTH, AbilityType.CONSTITUTION],
        CharacterClass.DRUID: [AbilityType.INTELLIGENCE, AbilityType.WISDOM],
        CharacterClass.MONK: [AbilityType.STRENGTH, AbilityType.DEXTERITY],
        CharacterClass.PALADIN: [AbilityType.WISDOM, AbilityType.CHARISMA],
        CharacterClass.SORCERER: [AbilityType.CONSTITUTION, AbilityType.CHARISMA],
        CharacterClass.WARLOCK: [AbilityType.WISDOM, AbilityType.CHARISMA],
    }

    # Speed by race
    race_speeds = {
        "dwarf": 25,
        "halfling": 25,
        "gnome": 25,
        "elf": 30,
        "human": 30,
        "dragonborn": 30,
        "half-elf": 30,
        "half-orc": 30,
        "tiefling": 30,
    }

    speed = race_speeds.get(race.lower(), 30)

    # Create spell slots for casters
    spell_slots = None
    if character_class in [
        CharacterClass.WIZARD,
        CharacterClass.SORCERER,
        CharacterClass.CLERIC,
        CharacterClass.DRUID,
        CharacterClass.BARD,
        CharacterClass.WARLOCK,
    ]:
    if character_class in [
        CharacterClass.WIZARD,
        CharacterClass.SORCERER,
        CharacterClass.CLERIC,
        CharacterClass.DRUID,
        CharacterClass.BARD,
        CharacterClass.WARLOCK,
    ]:
        spell_slots = SpellSlots(
            level_1=0,
            level_2=0,
            level_3=0,
            level_4=0,
            level_5=0,
            level_6=0,
            level_7=0,
            level_8=0,
            level_9=0,
            level_1_used=0,
            level_2_used=0,
            level_3_used=0,
            level_4_used=0,
            level_5_used=0,
            level_6_used=0,
            level_7_used=0,
            level_8_used=0,
            level_9_used=0,
            level_1=0,
            level_2=0,
            level_3=0,
            level_4=0,
            level_5=0,
            level_6=0,
            level_7=0,
            level_8=0,
            level_9=0,
            level_1_used=0,
            level_2_used=0,
            level_3_used=0,
            level_4_used=0,
            level_5_used=0,
            level_6_used=0,
            level_7_used=0,
            level_8_used=0,
            level_9_used=0,
        )
        # Initialize based on level (simplified)
        if level >= 1:
            spell_slots.level_1 = 2
        if level >= 3:
            spell_slots.level_1 = 4
            spell_slots.level_2 = 2

    # Default personality if not provided
    if personality is None:
        personality = [f"A {race} {character_class.value}", "Seeks adventure"]

    # Calculate AC (simplified - 10 + DEX modifier)
    base_ac = 10 + char_stats.get_modifier("dexterity")

    # Create character sheet
    character = CharacterSheet(
        name=name,
        race=race,
        character_class=character_class,
        level=level,
        experience_points=0,
        stats=char_stats,
        hit_points=max_hp,
        max_hit_points=max_hp,
        temp_hit_points=0,
        hit_dice_remaining=level,
        armor_class=base_ac,
        proficiency_bonus=proficiency_bonus,
        speed=speed,
        initiative_bonus=0,
        skill_proficiencies=default_skills.get(character_class, []),
        saving_throw_proficiencies=save_proficiencies.get(character_class, []),
        actions_available=1,
        bonus_actions_available=1,
        reactions_available=1,
        movement_remaining=speed,
        spell_slots=spell_slots,
        spells_known=[],
        cantrips_known=[],
        inventory=[],
        equipped_armor=None,
        equipped_weapons=["Unarmed Strike"],
        attunement_slots_used=0,
        exhaustion_level=0,
        death_saves_success=0,
        death_saves_failure=0,
        background=background,
        personality_traits=personality,
        ideals=[],
        bonds=[],
        flaws=[],
        flaws=[],
    )

    # Create player character
    return PlayerCharacter(
        character=character,
        player_type=player_type,
        model=ai_model,
        provider=ai_provider,
        personality_prompt=ai_personality,
        is_active=True,
        last_action_time=None,
        position=None,
        position=None,
    )
