"""Fair dice rolling tool for tabletop RPGs."""

import random
import time
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class DiceType(str, Enum):
    """Standard dice types used in tabletop RPGs."""

    D4 = "d4"
    D6 = "d6"
    D8 = "d8"
    D10 = "d10"
    D12 = "d12"
    D20 = "d20"
    D100 = "d100"


class DiceRoll(BaseModel):
    """Result of a dice roll with full transparency."""

    dice_type: DiceType = Field(..., description="Type of dice rolled")
    num_dice: int = Field(..., description="Number of dice rolled")
    modifier: int = Field(default=0, description="Modifier to add to the total")
    rolls: list[int] = Field(..., description="Individual roll results")
    total: int = Field(..., description="Total result including modifier")
    natural_total: int = Field(..., description="Total before modifier")
    critical_success: bool = Field(default=False, description="Natural 20 on d20")
    critical_failure: bool = Field(default=False, description="Natural 1 on d20")
    purpose: str = Field(default="", description="What the roll was for")
    timestamp: float = Field(..., description="Unix timestamp of the roll")
    seed: int | None = Field(None, description="Random seed used if deterministic")
    advantage: bool | None = Field(None, description="Whether rolled with advantage")
    disadvantage: bool | None = Field(None, description="Whether rolled with disadvantage")


class DiceRollRequest(BaseModel):
    """Request for a dice roll."""

    dice_type: DiceType = Field(..., description="Type of dice to roll")
    num_dice: int = Field(default=1, description="Number of dice to roll")
    modifier: int = Field(default=0, description="Modifier to add")
    purpose: str = Field(default="", description="Purpose of the roll")
    advantage: bool = Field(default=False, description="Roll with advantage (2d20, keep highest)")
    disadvantage: bool = Field(default=False, description="Roll with disadvantage (2d20, keep lowest)")
    seed: int | None = Field(None, description="Random seed for deterministic rolls")


def get_dice_value(dice_type: DiceType) -> int:
    """Get the maximum value for a dice type."""
    dice_values = {
        DiceType.D4: 4,
        DiceType.D6: 6,
        DiceType.D8: 8,
        DiceType.D10: 10,
        DiceType.D12: 12,
        DiceType.D20: 20,
        DiceType.D100: 100,
    }
    return dice_values[dice_type]


def roll_dice(
    dice_type: DiceType,
    num_dice: int = 1,
    modifier: int = 0,
    purpose: str = "",
    advantage: bool = False,
    disadvantage: bool = False,
    seed: int | None = None,
) -> DiceRoll:
    """
    Roll dice with full transparency and fairness.

    Args:
        dice_type: Type of dice to roll (d4, d6, d8, d10, d12, d20, d100)
        num_dice: Number of dice to roll
        modifier: Modifier to add to the total
        purpose: What the roll is for (e.g., "Attack roll", "Damage", "Saving throw")
        advantage: Roll with advantage (for d20 rolls)
        disadvantage: Roll with disadvantage (for d20 rolls)
        seed: Optional random seed for deterministic rolls

    Returns:
        DiceRoll object with complete roll information
    """
    # Set random seed if provided (for testing/replay)
    if seed is not None:
        random.seed(seed)

    max_value = get_dice_value(dice_type)
    timestamp = time.time()

    # Handle advantage/disadvantage for d20 rolls
    if dice_type == DiceType.D20 and num_dice == 1 and (advantage or disadvantage):
        # Roll twice
        rolls = [random.randint(1, max_value) for _ in range(2)]

        # Keep the appropriate roll
        if advantage:
            kept_roll = max(rolls)
            natural_total = kept_roll
        else:  # disadvantage
            kept_roll = min(rolls)
            natural_total = kept_roll

        # Check for criticals on the kept roll
        critical_success = kept_roll == 20
        critical_failure = kept_roll == 1

        total = natural_total + modifier

        return DiceRoll(
            dice_type=dice_type,
            num_dice=num_dice,
            modifier=modifier,
            rolls=rolls,  # Show both rolls for transparency
            total=total,
            natural_total=natural_total,
            critical_success=critical_success,
            critical_failure=critical_failure,
            purpose=purpose,
            timestamp=timestamp,
            seed=seed,
            advantage=advantage,
            disadvantage=disadvantage,
        )

    # Standard roll
    rolls = [random.randint(1, max_value) for _ in range(num_dice)]
    natural_total = sum(rolls)
    total = natural_total + modifier

    # Check for criticals on single d20 rolls
    critical_success = False
    critical_failure = False
    if dice_type == DiceType.D20 and num_dice == 1:
        critical_success = rolls[0] == 20
        critical_failure = rolls[0] == 1

    return DiceRoll(
        dice_type=dice_type,
        num_dice=num_dice,
        modifier=modifier,
        rolls=rolls,
        total=total,
        natural_total=natural_total,
        critical_success=critical_success,
        critical_failure=critical_failure,
        purpose=purpose,
        timestamp=timestamp,
        seed=seed,
        advantage=False,
        disadvantage=False,
    )


def roll_multiple(requests: list[DiceRollRequest]) -> list[DiceRoll]:
    """
    Roll multiple dice requests at once.

    Args:
        requests: List of dice roll requests

    Returns:
        List of DiceRoll results
    """
    results = []
    for request in requests:
        result = roll_dice(
            dice_type=request.dice_type,
            num_dice=request.num_dice,
            modifier=request.modifier,
            purpose=request.purpose,
            advantage=request.advantage,
            disadvantage=request.disadvantage,
            seed=request.seed,
        )
        results.append(result)
    return results


def format_roll_result(roll: DiceRoll) -> str:
    """
    Format a dice roll result for display.

    Args:
        roll: DiceRoll result to format

    Returns:
        Formatted string representation
    """
    # Build the base string
    base = f"{roll.dice_type.value}" if roll.num_dice == 1 else f"{roll.num_dice}{roll.dice_type.value}"

    if roll.modifier > 0:
        base += f"+{roll.modifier}"
    elif roll.modifier < 0:
        base += f"{roll.modifier}"

    # Add purpose if provided
    result = f"{roll.purpose}: {base} = " if roll.purpose else f"{base} = "

    # Show individual rolls
    if roll.advantage or roll.disadvantage:
        result += f"[{roll.rolls[0]}, {roll.rolls[1]}]"
        if roll.advantage:
            result += " (advantage)"
        else:
            result += " (disadvantage)"
        result += f" = {roll.natural_total}"
    else:
        if len(roll.rolls) == 1:
            result += f"{roll.rolls[0]}"
        else:
            result += f"[{', '.join(map(str, roll.rolls))}] = {roll.natural_total}"

    # Add modifier to get total
    if roll.modifier != 0:
        if roll.modifier > 0:
            result += f" + {roll.modifier}"
        else:
            result += f" - {abs(roll.modifier)}"
        result += f" = {roll.total}"

    # Add critical indicators
    if roll.critical_success:
        result += " 🎯 CRITICAL SUCCESS!"
    elif roll.critical_failure:
        result += " 💀 CRITICAL FAILURE!"

    return result


# Example usage functions
def roll_attack(attack_bonus: int, advantage: bool = False, disadvantage: bool = False) -> DiceRoll:
    """Roll an attack with the given bonus."""
    return roll_dice(DiceType.D20, modifier=attack_bonus, purpose="Attack roll", advantage=advantage, disadvantage=disadvantage)


def roll_damage(num_dice: int, dice_type: DiceType, damage_bonus: int = 0, damage_type: str = "damage") -> DiceRoll:
    """Roll damage dice."""
    return roll_dice(dice_type, num_dice=num_dice, modifier=damage_bonus, purpose=f"{damage_type} damage")


def roll_saving_throw(save_bonus: int, save_type: str, advantage: bool = False, disadvantage: bool = False) -> DiceRoll:
    """Roll a saving throw."""
    return roll_dice(
        DiceType.D20, modifier=save_bonus, purpose=f"{save_type} saving throw", advantage=advantage, disadvantage=disadvantage
    )


def roll_ability_check(ability_bonus: int, ability_name: str, advantage: bool = False, disadvantage: bool = False) -> DiceRoll:
    """Roll an ability check."""
    return roll_dice(
        DiceType.D20, modifier=ability_bonus, purpose=f"{ability_name} check", advantage=advantage, disadvantage=disadvantage
    )
