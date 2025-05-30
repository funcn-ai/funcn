"""D&D 5e API tool for accessing official game content."""

import httpx
from pydantic import BaseModel, Field
from typing import Any, Optional


# Base models for common structures
class APIReference(BaseModel):
    """Minimal representation of a resource."""
    index: str = Field(..., description="Resource index for shorthand searching")
    name: str = Field(..., description="Name of the referenced resource")
    url: str = Field(..., description="URL of the referenced resource")


class DC(BaseModel):
    """Represents a difficulty check."""
    dc_type: APIReference = Field(..., description="Type of DC")
    dc_value: int = Field(..., description="DC value")
    success_type: str = Field(..., description="Type of success: none, half, or other")


class Damage(BaseModel):
    """Represents damage."""
    damage_type: APIReference = Field(..., description="Type of damage")
    damage_dice: str = Field(..., description="Damage dice formula")


class Choice(BaseModel):
    """Represents a choice made by a player."""
    desc: str = Field(..., description="Description of the choice")
    choose: int = Field(..., description="Number of options to choose")
    type: str = Field(..., description="Type of choice")
    from_option_set_type: str = Field(..., alias="from.option_set_type", description="Type of option set")
    from_options: list[dict[str, Any]] | None = Field(None, alias="from.options", description="Available options")


class AbilityBonus(BaseModel):
    """Represents an ability score bonus."""
    ability_score: APIReference = Field(..., description="Ability score reference")
    bonus: int = Field(..., description="Bonus value")


# Enhanced spell model with more fields
class DndSpell(BaseModel):
    """D&D 5e spell information."""
    index: str = Field(..., description="Spell index")
    name: str = Field(..., description="Spell name")
    level: int = Field(..., description="Spell level (0 for cantrips)")
    school: APIReference = Field(..., description="School of magic")
    casting_time: str = Field(..., description="Time required to cast")
    range: str = Field(..., description="Spell range")
    components: list[str] = Field(..., description="Required components (V, S, M)")
    material: str | None = Field(None, description="Material component details")
    duration: str = Field(..., description="Spell duration")
    concentration: bool = Field(..., description="Whether concentration is required")
    ritual: bool = Field(..., description="Whether it can be cast as a ritual")
    desc: list[str] = Field(..., description="Spell description")
    higher_level: list[str] | None = Field(None, description="Effects at higher levels")
    classes: list[APIReference] = Field(..., description="Classes that can cast this spell")
    subclasses: list[APIReference] | None = Field(None, description="Subclasses that get this spell")
    damage: dict[str, Any] | None = Field(None, description="Damage information if applicable")
    dc: DC | None = Field(None, description="DC information if applicable")
    area_of_effect: dict[str, Any] | None = Field(None, description="Area of effect information")
    url: str = Field(..., description="API URL for this spell")


# Enhanced class model
class DndClass(BaseModel):
    """D&D 5e class information."""
    index: str = Field(..., description="Class index")
    name: str = Field(..., description="Class name")
    hit_die: int = Field(..., description="Hit die size")
    proficiency_choices: list[Choice] = Field(..., description="Proficiency choices")
    proficiencies: list[APIReference] = Field(..., description="Proficiencies granted")
    saving_throws: list[APIReference] = Field(..., description="Saving throw proficiencies")
    starting_equipment: list[dict[str, Any]] = Field(..., description="Starting equipment")
    starting_equipment_options: list[Choice] = Field(..., description="Starting equipment choices")
    class_levels: str = Field(..., description="URL for class level progression")
    multi_classing: dict[str, Any] = Field(..., description="Multiclassing requirements and proficiencies")
    subclasses: list[APIReference] = Field(..., description="Available subclasses")
    spellcasting: dict[str, Any] | None = Field(None, description="Spellcasting information")
    url: str = Field(..., description="API URL for this class")


# Enhanced equipment model
class DndEquipment(BaseModel):
    """D&D 5e equipment information."""
    index: str = Field(..., description="Equipment index")
    name: str = Field(..., description="Equipment name")
    equipment_category: APIReference = Field(..., description="Category of equipment")
    gear_category: APIReference | None = Field(None, description="Gear category if applicable")
    cost: dict[str, Any] = Field(..., description="Cost in currency")
    weight: float | None = Field(None, description="Weight in pounds")
    desc: list[str] | None = Field(None, description="Equipment description")

    # Weapon-specific fields
    weapon_category: str | None = Field(None, description="Weapon category")
    weapon_range: str | None = Field(None, description="Weapon range")
    category_range: str | None = Field(None, description="Category range")
    damage: Damage | None = Field(None, description="Damage if weapon")
    two_handed_damage: Damage | None = Field(None, description="Two-handed damage if versatile")
    range: dict[str, int] | None = Field(None, description="Range if applicable")
    properties: list[APIReference] | None = Field(None, description="Special properties")

    # Armor-specific fields
    armor_category: str | None = Field(None, description="Armor category")
    armor_class: dict[str, Any] | None = Field(None, description="AC if armor")
    str_minimum: int | None = Field(None, description="Strength requirement")
    stealth_disadvantage: bool | None = Field(None, description="Whether armor gives stealth disadvantage")

    url: str = Field(..., description="API URL for this equipment")


# Enhanced monster model
class DndMonster(BaseModel):
    """D&D 5e monster information."""
    index: str = Field(..., description="Monster index")
    name: str = Field(..., description="Monster name")
    size: str = Field(..., description="Size category")
    type: str = Field(..., description="Creature type")
    subtype: str | None = Field(None, description="Creature subtype")
    alignment: str = Field(..., description="Typical alignment")
    armor_class: list[dict[str, Any]] = Field(..., description="Armor class with breakdown")
    hit_points: int = Field(..., description="Average hit points")
    hit_dice: str = Field(..., description="Hit dice formula")
    hit_points_roll: str = Field(..., description="Full HP roll formula")
    speed: dict[str, Any] = Field(..., description="Movement speeds")

    # Ability scores
    strength: int = Field(..., description="Strength score")
    dexterity: int = Field(..., description="Dexterity score")
    constitution: int = Field(..., description="Constitution score")
    intelligence: int = Field(..., description="Intelligence score")
    wisdom: int = Field(..., description="Wisdom score")
    charisma: int = Field(..., description="Charisma score")

    # Proficiencies and immunities
    proficiencies: list[dict[str, Any]] = Field(..., description="Skill/save proficiencies")
    damage_vulnerabilities: list[str] = Field(default_factory=list, description="Damage vulnerabilities")
    damage_resistances: list[str] = Field(default_factory=list, description="Damage resistances")
    damage_immunities: list[str] = Field(default_factory=list, description="Damage immunities")
    condition_immunities: list[APIReference] = Field(default_factory=list, description="Condition immunities")

    # Senses and communication
    senses: dict[str, Any] = Field(..., description="Senses and ranges")
    languages: str = Field(..., description="Languages spoken")
    telepathy: int | None = Field(None, description="Telepathy range if applicable")

    # Combat stats
    challenge_rating: float = Field(..., description="Challenge rating")
    proficiency_bonus: int = Field(..., description="Proficiency bonus")
    xp: int = Field(..., description="Experience points")

    # Abilities and actions
    special_abilities: list[dict[str, Any]] | None = Field(None, description="Special abilities")
    actions: list[dict[str, Any]] = Field(..., description="Available actions")
    legendary_actions: list[dict[str, Any]] | None = Field(None, description="Legendary actions")
    reactions: list[dict[str, Any]] | None = Field(None, description="Reactions")

    url: str = Field(..., description="API URL for this monster")


# New models for additional content types
class DndRace(BaseModel):
    """D&D 5e race information."""
    index: str = Field(..., description="Race index")
    name: str = Field(..., description="Race name")
    speed: int = Field(..., description="Base walking speed")
    ability_bonuses: list[AbilityBonus] = Field(..., description="Ability score bonuses")
    ability_bonus_options: Choice | None = Field(None, description="Optional ability bonuses")
    alignment: str = Field(..., description="Typical alignment description")
    age: str = Field(..., description="Age information")
    size: str = Field(..., description="Size category")
    size_description: str = Field(..., description="Size description")
    starting_proficiencies: list[APIReference] = Field(default_factory=list, description="Starting proficiencies")
    starting_proficiency_options: Choice | None = Field(None, description="Proficiency choices")
    languages: list[APIReference] = Field(..., description="Languages known")
    language_options: Choice | None = Field(None, description="Language choices")
    traits: list[APIReference] = Field(..., description="Racial traits")
    subraces: list[APIReference] = Field(default_factory=list, description="Available subraces")
    url: str = Field(..., description="API URL for this race")


class DndFeat(BaseModel):
    """D&D 5e feat information."""
    index: str = Field(..., description="Feat index")
    name: str = Field(..., description="Feat name")
    desc: list[str] = Field(..., description="Feat description")
    prerequisites: list[dict[str, Any]] = Field(default_factory=list, description="Prerequisites")
    url: str = Field(..., description="API URL for this feat")


class DndSkill(BaseModel):
    """D&D 5e skill information."""
    index: str = Field(..., description="Skill index")
    name: str = Field(..., description="Skill name")
    desc: list[str] = Field(..., description="Skill description")
    ability_score: APIReference = Field(..., description="Associated ability score")
    url: str = Field(..., description="API URL for this skill")


class DndCondition(BaseModel):
    """D&D 5e condition information."""
    index: str = Field(..., description="Condition index")
    name: str = Field(..., description="Condition name")
    desc: list[str] = Field(..., description="Condition effects")
    url: str = Field(..., description="API URL for this condition")


class DndMagicItem(BaseModel):
    """D&D 5e magic item information."""
    index: str = Field(..., description="Item index")
    name: str = Field(..., description="Item name")
    equipment_category: APIReference = Field(..., description="Equipment category")
    rarity: dict[str, str] = Field(..., description="Item rarity")
    variants: list[APIReference] = Field(default_factory=list, description="Item variants")
    variant: bool = Field(..., description="Whether this is a variant")
    desc: list[str] = Field(..., description="Item description")
    url: str = Field(..., description="API URL for this item")


class DndApiResponse(BaseModel):
    """Generic D&D API response."""
    count: int = Field(..., description="Number of results")
    results: list[dict[str, str]] = Field(..., description="List of results with name and url")


# Base URL for the D&D 5e API
DND_API_BASE_URL = "https://www.dnd5eapi.co/api"


async def get_spell_info(spell_name: str) -> DndSpell:
    """
    Get detailed information about a D&D 5e spell.

    Args:
        spell_name: Name of the spell to look up

    Returns:
        DndSpell object with spell details
    """
    spell_index = spell_name.lower().replace(" ", "-").replace("'", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/spells/{spell_index}")

        if response.status_code == 404:
            raise ValueError(f"Spell '{spell_name}' not found")

        data = response.json()

        # Parse the response into our enhanced model
        return DndSpell(
            index=data["index"],
            name=data["name"],
            level=data["level"],
            school=APIReference(**data["school"]),
            casting_time=data["casting_time"],
            range=data["range"],
            components=data["components"],
            material=data.get("material"),
            duration=data["duration"],
            concentration=data["concentration"],
            ritual=data.get("ritual", False),
            desc=data["desc"],
            higher_level=data.get("higher_level"),
            classes=[APIReference(**c) for c in data["classes"]],
            subclasses=[APIReference(**s) for s in data.get("subclasses", [])],
            damage=data.get("damage"),
            dc=DC(**data["dc"]) if "dc" in data else None,
            area_of_effect=data.get("area_of_effect"),
            url=data["url"]
        )


async def get_class_info(class_name: str) -> DndClass:
    """
    Get detailed information about a D&D 5e class.

    Args:
        class_name: Name of the class to look up

    Returns:
        DndClass object with class details
    """
    class_index = class_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/classes/{class_index}")

        if response.status_code == 404:
            raise ValueError(f"Class '{class_name}' not found")

        data = response.json()

        return DndClass(
            index=data["index"],
            name=data["name"],
            hit_die=data["hit_die"],
            proficiency_choices=[Choice(**c) for c in data.get("proficiency_choices", [])],
            proficiencies=[APIReference(**p) for p in data["proficiencies"]],
            saving_throws=[APIReference(**s) for s in data["saving_throws"]],
            starting_equipment=data["starting_equipment"],
            starting_equipment_options=[Choice(**c) for c in data.get("starting_equipment_options", [])],
            class_levels=data["class_levels"],
            multi_classing=data.get("multi_classing", {}),
            subclasses=[APIReference(**s) for s in data["subclasses"]],
            spellcasting=data.get("spellcasting"),
            url=data["url"]
        )


async def get_monster_info(monster_name: str) -> DndMonster:
    """
    Get detailed information about a D&D 5e monster.

    Args:
        monster_name: Name of the monster to look up

    Returns:
        DndMonster object with monster details
    """
    monster_index = monster_name.lower().replace(" ", "-").replace("'", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/monsters/{monster_index}")

        if response.status_code == 404:
            raise ValueError(f"Monster '{monster_name}' not found")

        data = response.json()

        return DndMonster(
            index=data["index"],
            name=data["name"],
            size=data["size"],
            type=data["type"],
            subtype=data.get("subtype"),
            alignment=data["alignment"],
            armor_class=data["armor_class"] if isinstance(data["armor_class"], list) else [{"type": "natural", "value": data["armor_class"]}],
            hit_points=data["hit_points"],
            hit_dice=data["hit_dice"],
            hit_points_roll=data["hit_points_roll"],
            speed=data["speed"],
            strength=data["strength"],
            dexterity=data["dexterity"],
            constitution=data["constitution"],
            intelligence=data["intelligence"],
            wisdom=data["wisdom"],
            charisma=data["charisma"],
            proficiencies=data.get("proficiencies", []),
            damage_vulnerabilities=data.get("damage_vulnerabilities", []),
            damage_resistances=data.get("damage_resistances", []),
            damage_immunities=data.get("damage_immunities", []),
            condition_immunities=[APIReference(**c) for c in data.get("condition_immunities", [])],
            senses=data["senses"],
            languages=data["languages"],
            telepathy=data.get("telepathy"),
            challenge_rating=data["challenge_rating"],
            proficiency_bonus=data["proficiency_bonus"],
            xp=data["xp"],
            special_abilities=data.get("special_abilities"),
            actions=data.get("actions", []),
            legendary_actions=data.get("legendary_actions"),
            reactions=data.get("reactions"),
            url=data["url"]
        )


async def get_equipment_info(equipment_name: str) -> DndEquipment:
    """
    Get detailed information about D&D 5e equipment.

    Args:
        equipment_name: Name of the equipment to look up

    Returns:
        DndEquipment object with equipment details
    """
    equipment_index = equipment_name.lower().replace(" ", "-").replace("'", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/equipment/{equipment_index}")

        if response.status_code == 404:
            raise ValueError(f"Equipment '{equipment_name}' not found")

        data = response.json()

        return DndEquipment(
            index=data["index"],
            name=data["name"],
            equipment_category=APIReference(**data["equipment_category"]),
            gear_category=APIReference(**data["gear_category"]) if "gear_category" in data else None,
            cost=data["cost"],
            weight=data.get("weight"),
            desc=data.get("desc"),
            weapon_category=data.get("weapon_category"),
            weapon_range=data.get("weapon_range"),
            category_range=data.get("category_range"),
            damage=Damage(**data["damage"]) if "damage" in data else None,
            two_handed_damage=Damage(**data["two_handed_damage"]) if "two_handed_damage" in data else None,
            range=data.get("range"),
            properties=[APIReference(**p) for p in data.get("properties", [])],
            armor_category=data.get("armor_category"),
            armor_class=data.get("armor_class"),
            str_minimum=data.get("str_minimum"),
            stealth_disadvantage=data.get("stealth_disadvantage"),
            url=data["url"]
        )


async def get_race_info(race_name: str) -> DndRace:
    """
    Get detailed information about a D&D 5e race.

    Args:
        race_name: Name of the race to look up

    Returns:
        DndRace object with race details
    """
    race_index = race_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/races/{race_index}")

        if response.status_code == 404:
            raise ValueError(f"Race '{race_name}' not found")

        data = response.json()

        return DndRace(
            index=data["index"],
            name=data["name"],
            speed=data["speed"],
            ability_bonuses=[AbilityBonus(
                ability_score=APIReference(**ab["ability_score"]),
                bonus=ab["bonus"]
            ) for ab in data["ability_bonuses"]],
            ability_bonus_options=Choice(**data["ability_bonus_options"]) if "ability_bonus_options" in data else None,
            alignment=data["alignment"],
            age=data["age"],
            size=data["size"],
            size_description=data["size_description"],
            starting_proficiencies=[APIReference(**p) for p in data.get("starting_proficiencies", [])],
            starting_proficiency_options=Choice(**data["starting_proficiency_options"]) if "starting_proficiency_options" in data else None,
            languages=[APIReference(**lang) for lang in data["languages"]],
            language_options=Choice(**data["language_options"]) if "language_options" in data else None,
            traits=[APIReference(**t) for t in data.get("traits", [])],
            subraces=[APIReference(**s) for s in data.get("subraces", [])],
            url=data["url"]
        )


async def get_feat_info(feat_name: str) -> DndFeat:
    """
    Get detailed information about a D&D 5e feat.

    Args:
        feat_name: Name of the feat to look up

    Returns:
        DndFeat object with feat details
    """
    feat_index = feat_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/feats/{feat_index}")

        if response.status_code == 404:
            raise ValueError(f"Feat '{feat_name}' not found")

        data = response.json()

        return DndFeat(
            index=data["index"],
            name=data["name"],
            desc=data["desc"],
            prerequisites=data.get("prerequisites", []),
            url=data["url"]
        )


async def get_skill_info(skill_name: str) -> DndSkill:
    """
    Get detailed information about a D&D 5e skill.

    Args:
        skill_name: Name of the skill to look up

    Returns:
        DndSkill object with skill details
    """
    skill_index = skill_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/skills/{skill_index}")

        if response.status_code == 404:
            raise ValueError(f"Skill '{skill_name}' not found")

        data = response.json()

        return DndSkill(
            index=data["index"],
            name=data["name"],
            desc=data["desc"],
            ability_score=APIReference(**data["ability_score"]),
            url=data["url"]
        )


async def get_condition_info(condition_name: str) -> DndCondition:
    """
    Get detailed information about a D&D 5e condition.

    Args:
        condition_name: Name of the condition to look up

    Returns:
        DndCondition object with condition details
    """
    condition_index = condition_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/conditions/{condition_index}")

        if response.status_code == 404:
            raise ValueError(f"Condition '{condition_name}' not found")

        data = response.json()

        return DndCondition(
            index=data["index"],
            name=data["name"],
            desc=data["desc"],
            url=data["url"]
        )


async def get_magic_item_info(item_name: str) -> DndMagicItem:
    """
    Get detailed information about a D&D 5e magic item.

    Args:
        item_name: Name of the magic item to look up

    Returns:
        DndMagicItem object with item details
    """
    item_index = item_name.lower().replace(" ", "-").replace("'", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/magic-items/{item_index}")

        if response.status_code == 404:
            raise ValueError(f"Magic item '{item_name}' not found")

        data = response.json()

        return DndMagicItem(
            index=data["index"],
            name=data["name"],
            equipment_category=APIReference(**data["equipment_category"]),
            rarity=data["rarity"],
            variants=[APIReference(**v) for v in data.get("variants", [])],
            variant=data.get("variant", False),
            desc=data["desc"],
            url=data["url"]
        )


async def search_dnd_content(
    content_type: str,
    query: str | None = None,
    **filters
) -> DndApiResponse:
    """
    Search for D&D 5e content by type with optional filtering.

    Args:
        content_type: Type of content (spells, classes, monsters, equipment, etc.)
        query: Optional search query to filter results
        **filters: Additional filters for spells and monsters
            For spells: level, school, name
            For monsters: challenge_rating, type, size

    Returns:
        DndApiResponse with search results
    """
    valid_types = [
        "ability-scores", "alignments", "backgrounds", "classes", "conditions",
        "damage-types", "equipment", "equipment-categories", "feats", "features",
        "languages", "magic-items", "magic-schools", "monsters", "proficiencies",
        "races", "rule-sections", "rules", "skills", "spells", "subclasses",
        "subraces", "traits", "weapon-properties"
    ]

    if content_type not in valid_types:
        raise ValueError(f"Invalid content type. Must be one of: {', '.join(valid_types)}")

    async with httpx.AsyncClient() as client:
        # Build URL with query parameters for supported endpoints
        url = f"{DND_API_BASE_URL}/{content_type}"
        params = {}

        # Add filters for spells and monsters
        if content_type == "spells" and filters:
            for key in ["level", "school", "name"]:
                if key in filters:
                    params[key] = filters[key]
        elif content_type == "monsters" and filters:
            for key in ["challenge_rating", "type", "size"]:
                if key in filters:
                    params[key] = filters[key]

        response = await client.get(url, params=params)

        if response.status_code != 200:
            raise ValueError(f"Failed to search {content_type}")

        data = response.json()

        # Filter results if query provided and not using API filters
        if query and not params:
            query_lower = query.lower()
            filtered_results = [
                r for r in data["results"]
                if query_lower in r["name"].lower()
            ]
            return DndApiResponse(
                count=len(filtered_results),
                results=filtered_results
            )

        return DndApiResponse(
            count=data["count"],
            results=data["results"]
        )


async def get_ability_score_info(ability_name: str) -> dict[str, Any]:
    """
    Get information about an ability score.

    Args:
        ability_name: Name or abbreviation of the ability score

    Returns:
        Dictionary with ability score details
    """
    ability_map = {
        "strength": "str", "str": "str",
        "dexterity": "dex", "dex": "dex",
        "constitution": "con", "con": "con",
        "intelligence": "int", "int": "int",
        "wisdom": "wis", "wis": "wis",
        "charisma": "cha", "cha": "cha"
    }

    ability_index = ability_map.get(ability_name.lower())
    if not ability_index:
        raise ValueError(f"Invalid ability score: {ability_name}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/ability-scores/{ability_index}")

        if response.status_code == 404:
            raise ValueError(f"Ability score '{ability_name}' not found")

        return response.json()


async def get_proficiency_info(proficiency_name: str) -> dict[str, Any]:
    """
    Get information about a proficiency.

    Args:
        proficiency_name: Name of the proficiency

    Returns:
        Dictionary with proficiency details
    """
    proficiency_index = proficiency_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/proficiencies/{proficiency_index}")

        if response.status_code == 404:
            raise ValueError(f"Proficiency '{proficiency_name}' not found")

        return response.json()


async def get_language_info(language_name: str) -> dict[str, Any]:
    """
    Get information about a language.

    Args:
        language_name: Name of the language

    Returns:
        Dictionary with language details
    """
    language_index = language_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/languages/{language_index}")

        if response.status_code == 404:
            raise ValueError(f"Language '{language_name}' not found")

        return response.json()


async def get_alignment_info(alignment_name: str) -> dict[str, Any]:
    """
    Get information about an alignment.

    Args:
        alignment_name: Name of the alignment

    Returns:
        Dictionary with alignment details
    """
    alignment_map = {
        "lawful good": "lawful-good", "lg": "lawful-good",
        "neutral good": "neutral-good", "ng": "neutral-good",
        "chaotic good": "chaotic-good", "cg": "chaotic-good",
        "lawful neutral": "lawful-neutral", "ln": "lawful-neutral",
        "true neutral": "neutral", "neutral": "neutral", "n": "neutral",
        "chaotic neutral": "chaotic-neutral", "cn": "chaotic-neutral",
        "lawful evil": "lawful-evil", "le": "lawful-evil",
        "neutral evil": "neutral-evil", "ne": "neutral-evil",
        "chaotic evil": "chaotic-evil", "ce": "chaotic-evil"
    }

    alignment_index = alignment_map.get(alignment_name.lower())
    if not alignment_index:
        raise ValueError(f"Invalid alignment: {alignment_name}")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/alignments/{alignment_index}")

        if response.status_code == 404:
            raise ValueError(f"Alignment '{alignment_name}' not found")

        return response.json()


async def get_damage_type_info(damage_type_name: str) -> dict[str, Any]:
    """
    Get information about a damage type.

    Args:
        damage_type_name: Name of the damage type

    Returns:
        Dictionary with damage type details
    """
    damage_index = damage_type_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/damage-types/{damage_index}")

        if response.status_code == 404:
            raise ValueError(f"Damage type '{damage_type_name}' not found")

        return response.json()


async def get_weapon_property_info(property_name: str) -> dict[str, Any]:
    """
    Get information about a weapon property.

    Args:
        property_name: Name of the weapon property

    Returns:
        Dictionary with weapon property details
    """
    property_index = property_name.lower().replace(" ", "-")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DND_API_BASE_URL}/weapon-properties/{property_index}")

        if response.status_code == 404:
            raise ValueError(f"Weapon property '{property_name}' not found")

        return response.json()
