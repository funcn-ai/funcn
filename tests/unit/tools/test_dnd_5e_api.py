"""Test suite for dnd_5e_api tool following best practices."""

import asyncio
import pytest

# Import the tool functions
from packages.funcn_registry.components.tools.dnd_5e_api.tool import (
    get_class_info,
    get_condition_info,
    get_equipment_info,
    get_magic_item_info,
    get_monster_info,
    get_race_info,
    get_skill_info,
    get_spell_info,
    search_dnd_content,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, Mock, patch


class TestDnd5eApiTool(BaseToolTest):
    """Test cases for D&D 5e API tool."""

    component_name = "dnd_5e_api"
    component_path = Path("packages/funcn_registry/components/tools/dnd_5e_api")

    def get_component_function(self):
        """Get the main tool function."""
        # This tool has multiple functions, return a primary one
        return get_spell_info

    def get_test_inputs(self):
        """Get test input cases."""
        return [
            {"name": "fireball"},
            {"name": "magic-missile"},
            {"name": "cure-wounds"},
        ]

    @pytest.mark.asyncio
    async def test_get_spell_success(self):
        """Test successful spell retrieval."""
        mock_spell_data = {
            "index": "fireball",
            "name": "Fireball",
            "level": 3,
            "school": {"index": "evocation", "name": "Evocation", "url": "/api/magic-schools/evocation"},
            "casting_time": "1 action",
            "range": "150 feet",
            "components": ["V", "S", "M"],
            "material": "A tiny ball of bat guano and sulfur",
            "duration": "Instantaneous",
            "desc": ["A bright streak flashes from your pointing finger..."],
            "higher_level": ["When you cast this spell using a spell slot of 4th level or higher..."],
            "damage": {"damage_type": {"index": "fire", "name": "Fire", "url": "/api/damage-types/fire"}, "damage_at_slot_level": {"3": "8d6"}},
            "classes": [{"index": "wizard", "name": "Wizard", "url": "/api/classes/wizard"}],
            "concentration": False,
            "url": "/api/spells/fireball"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_spell_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_spell_info("fireball")

            assert result.name == "Fireball"
            assert result.level == 3
            assert result.school.name == "Evocation"
            assert "8d6" in str(result.damage)

    @pytest.mark.asyncio
    async def test_get_class_success(self):
        """Test successful class retrieval."""
        mock_class_data = {
            "index": "wizard",
            "name": "Wizard",
            "hit_die": 6,
            "proficiencies": [
                {"index": "daggers", "name": "Daggers", "url": "/api/proficiencies/daggers"},
                {"index": "darts", "name": "Darts", "url": "/api/proficiencies/darts"}
            ],
            "saving_throws": [
                {"index": "int", "name": "INT", "url": "/api/ability-scores/int"},
                {"index": "wis", "name": "WIS", "url": "/api/ability-scores/wis"}
            ],
            "starting_equipment": [{"equipment": {"name": "Spellbook"}}],
            "spellcasting": {"level": 1, "spellcasting_ability": {"name": "INT"}},
            "proficiency_choices": [],
            "starting_equipment_options": [],
            "class_levels": "/api/classes/wizard/levels",
            "multi_classing": {},
            "subclasses": [],
            "url": "/api/classes/wizard"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_class_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_class_info("wizard")

            assert result.name == "Wizard"
            assert result.hit_die == 6
            assert result.spellcasting["spellcasting_ability"]["name"] == "INT"

    @pytest.mark.asyncio
    async def test_get_monster_success(self):
        """Test successful monster retrieval."""
        mock_monster_data = {
            "index": "goblin",
            "name": "Goblin",
            "size": "Small",
            "type": "humanoid",
            "alignment": "neutral evil",
            "armor_class": [{"value": 15, "type": "leather armor, shield"}],
            "hit_points": 7,
            "hit_dice": "2d6",
            "hit_points_roll": "2d6",
            "speed": {"walk": "30 ft."},
            "strength": 8,
            "dexterity": 14,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 8,
            "charisma": 8,
            "proficiencies": [],
            "damage_vulnerabilities": [],
            "damage_resistances": [],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": {"darkvision": "60 ft.", "passive_perception": 9},
            "languages": "Common, Goblin",
            "challenge_rating": 0.25,
            "proficiency_bonus": 2,
            "xp": 50,
            "actions": [{"name": "Scimitar", "desc": "Melee Weapon Attack: +4 to hit..."}],
            "url": "/api/monsters/goblin"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_monster_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_monster_info("goblin")

            assert result.name == "Goblin"
            assert result.challenge_rating == 0.25
            assert result.armor_class[0]["value"] == 15

    @pytest.mark.asyncio
    async def test_search_spells_success(self):
        """Test spell search functionality."""
        mock_search_results = {
            "count": 3,
            "results": [
                {"index": "fire-bolt", "name": "Fire Bolt"},
                {"index": "fireball", "name": "Fireball"},
                {"index": "fire-shield", "name": "Fire Shield"},
            ],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await search_dnd_content(query="fire", content_type="spells")

            assert result.count == 3
            assert len(result.results) == 3
            assert any(spell["name"] == "Fireball" for spell in result.results)

    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """Test search with level and school filters."""
        mock_search_results = {
            "count": 1,
            "results": [
                {"index": "fireball", "name": "Fireball"},
            ],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await search_dnd_content(content_type="spells", query="fire", level=3, school="evocation")

            # Verify search was called
            assert result.count == 1

    @pytest.mark.asyncio
    async def test_get_equipment_success(self):
        """Test equipment retrieval."""
        mock_equipment_data = {
            "index": "longsword",
            "name": "Longsword",
            "equipment_category": {
                "index": "weapon",
                "name": "Weapon",
                "url": "/api/equipment-categories/weapon"
            },
            "weapon_category": "Martial",
            "weapon_range": "Melee",
            "cost": {"quantity": 15, "unit": "gp"},
            "damage": {
                "damage_dice": "1d8",
                "damage_type": {
                    "index": "slashing",
                    "name": "Slashing",
                    "url": "/api/damage-types/slashing"
                }
            },
            "weight": 3,
            "properties": [
                {"index": "versatile", "name": "Versatile", "url": "/api/weapon-properties/versatile"}
            ],
            "url": "/api/equipment/longsword"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_equipment_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_equipment_info("longsword")

            assert result.name == "Longsword"
            assert result.damage.damage_dice == "1d8"
            assert result.cost["quantity"] == 15

    @pytest.mark.asyncio
    async def test_not_found_error(self):
        """Test handling of 404 not found errors."""
        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = Mock(return_value="Not found")

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            with pytest.raises(ValueError) as exc_info:
                await get_spell_info("nonexistent-spell")

            assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test handling of API errors."""
        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Connection error"))

            with pytest.raises(Exception) as exc_info:
                await get_monster_info("goblin")

            assert "Connection error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_race_success(self):
        """Test race retrieval."""
        mock_race_data = {
            "index": "elf",
            "name": "Elf",
            "speed": 30,
            "ability_bonuses": [
                {"ability_score": {"index": "dex", "name": "DEX", "url": "/api/ability-scores/dex"}, "bonus": 2}
            ],
            "alignment": "Elves love freedom, variety, and self-expression...",
            "age": "Although elves reach physical maturity at about the same age as humans...",
            "size": "Medium",
            "size_description": "Elves range from under 5 to over 6 feet tall...",
            "starting_proficiencies": [],
            "languages": [
                {"index": "common", "name": "Common", "url": "/api/languages/common"},
                {"index": "elvish", "name": "Elvish", "url": "/api/languages/elvish"}
            ],
            "traits": [
                {"index": "darkvision", "name": "Darkvision", "url": "/api/traits/darkvision"},
                {"index": "keen-senses", "name": "Keen Senses", "url": "/api/traits/keen-senses"}
            ],
            "subraces": [],
            "url": "/api/races/elf"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_race_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_race_info("elf")

            assert result.name == "Elf"
            assert result.speed == 30
            assert len(result.languages) == 2

    @pytest.mark.asyncio
    async def test_get_condition_success(self):
        """Test condition retrieval."""
        mock_condition_data = {
            "index": "poisoned",
            "name": "Poisoned",
            "desc": [
                "A poisoned creature has disadvantage on attack rolls and ability checks.",
            ],
            "url": "/api/conditions/poisoned"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_condition_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_condition_info("poisoned")

            assert result.name == "Poisoned"
            assert "disadvantage" in result.desc[0]

    @pytest.mark.asyncio
    async def test_search_monsters_by_cr(self):
        """Test monster search by challenge rating."""
        mock_search_results = {
            "count": 2,
            "results": [
                {"index": "goblin", "name": "Goblin"},
                {"index": "kobold", "name": "Kobold"},
            ],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await search_dnd_content(query="cr:0.25", content_type="monsters")

            # Verify search was performed
            assert hasattr(result, "results")

    @pytest.mark.asyncio
    async def test_magic_item_search(self):
        """Test magic item search functionality."""
        mock_search_results = {
            "count": 2,
            "results": [
                {"index": "bag-of-holding", "name": "Bag of Holding"},
                {"index": "bag-of-tricks", "name": "Bag of Tricks"},
            ],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await search_dnd_content(query="bag", content_type="magic-items")

            assert result.count == 2
            assert any(item["name"] == "Bag of Holding" for item in result.results)

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of request timeouts."""
        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Request timeout"))

            with pytest.raises(Exception) as exc_info:
                await get_spell_info("fireball")

            assert "Request timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_feat_info_success(self):
        """Test feat retrieval."""
        mock_feat_data = {
            "index": "alert",
            "name": "Alert",
            "desc": [
                "Always on the lookout for danger, you gain the following benefits:",
                "• You gain a +5 bonus to initiative.",
                "• You can't be surprised while you are conscious.",
                "• Other creatures don't gain advantage on attack rolls against you as a result of being unseen by you."
            ],
            "prerequisites": [],
            "url": "/api/feats/alert"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_feat_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            # Import the function
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_feat_info
            
            result = await get_feat_info("alert")

            assert result.name == "Alert"
            assert len(result.desc) == 4
            assert "+5 bonus to initiative" in result.desc[1]

    @pytest.mark.asyncio
    async def test_get_ability_score_info_success(self):
        """Test ability score retrieval."""
        mock_ability_data = {
            "index": "str",
            "name": "STR",
            "full_name": "Strength",
            "desc": [
                "Strength measures bodily power, athletic training, and the extent to which you can exert raw physical force."
            ],
            "skills": [
                {"index": "athletics", "name": "Athletics", "url": "/api/skills/athletics"}
            ],
            "url": "/api/ability-scores/str"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_ability_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_ability_score_info
            
            result = await get_ability_score_info("strength")

            assert result["name"] == "STR"
            assert result["full_name"] == "Strength"
            assert len(result["skills"]) == 1

    @pytest.mark.asyncio
    async def test_get_proficiency_info_success(self):
        """Test proficiency retrieval."""
        mock_proficiency_data = {
            "index": "skill-acrobatics",
            "type": "Skills",
            "name": "Skill: Acrobatics",
            "classes": [
                {"index": "rogue", "name": "Rogue", "url": "/api/classes/rogue"}
            ],
            "races": [],
            "url": "/api/proficiencies/skill-acrobatics"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_proficiency_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_proficiency_info
            
            result = await get_proficiency_info("skill-acrobatics")

            assert result["name"] == "Skill: Acrobatics"
            assert result["type"] == "Skills"

    @pytest.mark.asyncio
    async def test_get_language_info_success(self):
        """Test language retrieval."""
        mock_language_data = {
            "index": "elvish",
            "name": "Elvish",
            "type": "Standard",
            "typical_speakers": ["Elves"],
            "script": "Elvish",
            "url": "/api/languages/elvish"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_language_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_language_info
            
            result = await get_language_info("elvish")

            assert result["name"] == "Elvish"
            assert result["type"] == "Standard"
            assert "Elves" in result["typical_speakers"]

    @pytest.mark.asyncio
    async def test_get_alignment_info_success(self):
        """Test alignment retrieval."""
        mock_alignment_data = {
            "index": "lawful-good",
            "name": "Lawful Good",
            "abbreviation": "LG",
            "desc": "Lawful good (LG) creatures can be counted on to do the right thing as expected by society.",
            "url": "/api/alignments/lawful-good"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_alignment_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_alignment_info
            
            result = await get_alignment_info("lawful good")

            assert result["name"] == "Lawful Good"
            assert result["abbreviation"] == "LG"

    @pytest.mark.asyncio
    async def test_get_damage_type_info_success(self):
        """Test damage type retrieval."""
        mock_damage_type_data = {
            "index": "fire",
            "name": "Fire",
            "desc": ["Fire damage is dealt by flames and extreme heat."],
            "url": "/api/damage-types/fire"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_damage_type_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_damage_type_info
            
            result = await get_damage_type_info("fire")

            assert result["name"] == "Fire"
            assert "flames" in result["desc"][0]

    @pytest.mark.asyncio
    async def test_get_weapon_property_info_success(self):
        """Test weapon property retrieval."""
        mock_property_data = {
            "index": "versatile",
            "name": "Versatile",
            "desc": [
                "This weapon can be used with one or two hands. A damage value in parentheses appears with the property—the damage when the weapon is used with two hands to make a melee attack."
            ],
            "url": "/api/weapon-properties/versatile"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_property_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_weapon_property_info
            
            result = await get_weapon_property_info("versatile")

            assert result["name"] == "Versatile"
            assert "one or two hands" in result["desc"][0]

    @pytest.mark.asyncio
    async def test_spell_with_special_characters(self):
        """Test spell names with special characters."""
        mock_spell_data = {
            "index": "melfs-acid-arrow",
            "name": "Melf's Acid Arrow",
            "level": 2,
            "school": {"index": "evocation", "name": "Evocation", "url": "/api/magic-schools/evocation"},
            "casting_time": "1 action",
            "range": "90 feet",
            "components": ["V", "S", "M"],
            "material": "Powdered rhubarb leaf and an adder's stomach",
            "duration": "Instantaneous",
            "desc": ["A shimmering green arrow streaks toward a target..."],
            "classes": [{"index": "wizard", "name": "Wizard", "url": "/api/classes/wizard"}],
            "concentration": False,
            "url": "/api/spells/melfs-acid-arrow"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_spell_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_spell_info("Melf's Acid Arrow")

            assert result.name == "Melf's Acid Arrow"
            assert result.level == 2

    @pytest.mark.asyncio
    async def test_invalid_content_type_search(self):
        """Test search with invalid content type."""
        with pytest.raises(ValueError) as exc_info:
            await search_dnd_content(content_type="invalid-type", query="test")

        assert "Invalid content type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_with_empty_results(self):
        """Test search returning empty results."""
        mock_search_results = {
            "count": 0,
            "results": []
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await search_dnd_content(content_type="spells", query="nonexistentspell")

            assert result.count == 0
            assert result.results == []

    @pytest.mark.asyncio
    async def test_monster_with_legendary_actions(self):
        """Test monster with legendary actions."""
        mock_monster_data = {
            "index": "adult-red-dragon",
            "name": "Adult Red Dragon",
            "size": "Huge",
            "type": "dragon",
            "alignment": "chaotic evil",
            "armor_class": [{"value": 19, "type": "natural armor"}],
            "hit_points": 256,
            "hit_dice": "19d12",
            "hit_points_roll": "19d12+133",
            "speed": {"walk": "40 ft.", "climb": "40 ft.", "fly": "80 ft."},
            "strength": 27,
            "dexterity": 10,
            "constitution": 25,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 21,
            "proficiencies": [],
            "damage_vulnerabilities": [],
            "damage_resistances": [],
            "damage_immunities": ["fire"],
            "condition_immunities": [],
            "senses": {"blindsight": "60 ft.", "darkvision": "120 ft.", "passive_perception": 23},
            "languages": "Common, Draconic",
            "challenge_rating": 17,
            "proficiency_bonus": 6,
            "xp": 18000,
            "special_abilities": [
                {
                    "name": "Legendary Resistance (3/Day)",
                    "desc": "If the dragon fails a saving throw, it can choose to succeed instead."
                }
            ],
            "actions": [
                {
                    "name": "Multiattack",
                    "desc": "The dragon can use its Frightful Presence..."
                }
            ],
            "legendary_actions": [
                {
                    "name": "Detect",
                    "desc": "The dragon makes a Wisdom (Perception) check."
                },
                {
                    "name": "Tail Attack",
                    "desc": "The dragon makes a tail attack."
                }
            ],
            "url": "/api/monsters/adult-red-dragon"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_monster_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_monster_info("adult-red-dragon")

            assert result.name == "Adult Red Dragon"
            assert result.legendary_actions is not None
            assert len(result.legendary_actions) == 2
            assert result.challenge_rating == 17

    @pytest.mark.asyncio
    async def test_equipment_armor_properties(self):
        """Test equipment with armor properties."""
        mock_armor_data = {
            "index": "plate",
            "name": "Plate",
            "equipment_category": {"index": "armor", "name": "Armor", "url": "/api/equipment-categories/armor"},
            "armor_category": "Heavy",
            "armor_class": {"base": 18, "dex_bonus": False, "max_bonus": None},
            "str_minimum": 15,
            "stealth_disadvantage": True,
            "weight": 65,
            "cost": {"quantity": 1500, "unit": "gp"},
            "url": "/api/equipment/plate"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_armor_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_equipment_info("plate")

            assert result.name == "Plate"
            assert result.armor_category == "Heavy"
            assert result.armor_class["base"] == 18
            assert result.str_minimum == 15
            assert result.stealth_disadvantage is True

    @pytest.mark.asyncio
    async def test_race_with_subraces(self):
        """Test race with subraces."""
        mock_race_data = {
            "index": "elf",
            "name": "Elf",
            "speed": 30,
            "ability_bonuses": [
                {"ability_score": {"index": "dex", "name": "DEX", "url": "/api/ability-scores/dex"}, "bonus": 2}
            ],
            "alignment": "Elves love freedom...",
            "age": "Although elves reach physical maturity...",
            "size": "Medium",
            "size_description": "Elves range from under 5 to over 6 feet tall...",
            "starting_proficiencies": [],
            "languages": [
                {"index": "common", "name": "Common", "url": "/api/languages/common"},
                {"index": "elvish", "name": "Elvish", "url": "/api/languages/elvish"}
            ],
            "traits": [
                {"index": "darkvision", "name": "Darkvision", "url": "/api/traits/darkvision"}
            ],
            "subraces": [
                {"index": "high-elf", "name": "High Elf", "url": "/api/subraces/high-elf"},
                {"index": "wood-elf", "name": "Wood Elf", "url": "/api/subraces/wood-elf"}
            ],
            "url": "/api/races/elf"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_race_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_race_info("elf")

            assert result.name == "Elf"
            assert len(result.subraces) == 2
            assert any(subrace.name == "High Elf" for subrace in result.subraces)

    @pytest.mark.asyncio
    async def test_spell_with_area_of_effect(self):
        """Test spell with area of effect."""
        mock_spell_data = {
            "index": "fireball",
            "name": "Fireball",
            "level": 3,
            "school": {"index": "evocation", "name": "Evocation", "url": "/api/magic-schools/evocation"},
            "casting_time": "1 action",
            "range": "150 feet",
            "components": ["V", "S", "M"],
            "material": "A tiny ball of bat guano and sulfur",
            "duration": "Instantaneous",
            "desc": ["A bright streak flashes..."],
            "damage": {"damage_type": {"index": "fire", "name": "Fire", "url": "/api/damage-types/fire"}, "damage_at_slot_level": {"3": "8d6"}},
            "area_of_effect": {
                "type": "sphere",
                "size": 20
            },
            "classes": [{"index": "wizard", "name": "Wizard", "url": "/api/classes/wizard"}],
            "concentration": False,
            "url": "/api/spells/fireball"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_spell_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_spell_info("fireball")

            assert result.area_of_effect is not None
            assert result.area_of_effect["type"] == "sphere"
            assert result.area_of_effect["size"] == 20

    @pytest.mark.asyncio
    async def test_spell_with_dc(self):
        """Test spell with saving throw DC."""
        mock_spell_data = {
            "index": "hold-person",
            "name": "Hold Person",
            "level": 2,
            "school": {"index": "enchantment", "name": "Enchantment", "url": "/api/magic-schools/enchantment"},
            "casting_time": "1 action",
            "range": "60 feet",
            "components": ["V", "S", "M"],
            "material": "A small, straight piece of iron",
            "duration": "Concentration, up to 1 minute",
            "desc": ["Choose a humanoid that you can see..."],
            "dc": {
                "dc_type": {"index": "wis", "name": "WIS", "url": "/api/ability-scores/wis"},
                "dc_value": 0,
                "success_type": "none"
            },
            "classes": [{"index": "wizard", "name": "Wizard", "url": "/api/classes/wizard"}],
            "concentration": True,
            "url": "/api/spells/hold-person"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_spell_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_spell_info("hold-person")

            assert result.dc is not None
            assert result.dc.dc_type.name == "WIS"
            assert result.concentration is True

    @pytest.mark.asyncio
    async def test_invalid_ability_score(self):
        """Test invalid ability score name."""
        from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_ability_score_info
        
        with pytest.raises(ValueError) as exc_info:
            await get_ability_score_info("invalid")

        assert "Invalid ability score" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_alignment(self):
        """Test invalid alignment name."""
        from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_alignment_info
        
        with pytest.raises(ValueError) as exc_info:
            await get_alignment_info("invalid alignment")

        assert "Invalid alignment" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_filtering_by_query(self):
        """Test search filtering with query parameter."""
        mock_search_results = {
            "count": 5,
            "results": [
                {"index": "fire-bolt", "name": "Fire Bolt"},
                {"index": "fireball", "name": "Fireball"},
                {"index": "burning-hands", "name": "Burning Hands"},
                {"index": "scorching-ray", "name": "Scorching Ray"},
                {"index": "wall-of-fire", "name": "Wall of Fire"}
            ]
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await search_dnd_content(content_type="spells", query="fire")

            # Should filter to only spells with "fire" in the name
            assert all("fire" in r["name"].lower() for r in result.results)

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test concurrent API calls."""
        mock_spell_data = {
            "index": "magic-missile",
            "name": "Magic Missile",
            "level": 1,
            "school": {"index": "evocation", "name": "Evocation", "url": "/api/magic-schools/evocation"},
            "casting_time": "1 action",
            "range": "120 feet",
            "components": ["V", "S"],
            "duration": "Instantaneous",
            "desc": ["You create three glowing darts..."],
            "classes": [{"index": "wizard", "name": "Wizard", "url": "/api/classes/wizard"}],
            "concentration": False,
            "url": "/api/spells/magic-missile"
        }

        mock_monster_data = {
            "index": "goblin",
            "name": "Goblin",
            "size": "Small",
            "type": "humanoid",
            "alignment": "neutral evil",
            "armor_class": [{"value": 15, "type": "leather armor, shield"}],
            "hit_points": 7,
            "hit_dice": "2d6",
            "hit_points_roll": "2d6",
            "speed": {"walk": "30 ft."},
            "strength": 8,
            "dexterity": 14,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 8,
            "charisma": 8,
            "proficiencies": [],
            "damage_vulnerabilities": [],
            "damage_resistances": [],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": {"darkvision": "60 ft.", "passive_perception": 9},
            "languages": "Common, Goblin",
            "challenge_rating": 0.25,
            "proficiency_bonus": 2,
            "xp": 50,
            "actions": [],
            "url": "/api/monsters/goblin"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            async def mock_get(url, *args, **kwargs):
                mock_response = Mock()
                mock_response.status_code = 200
                if "spells" in url:
                    mock_response.json = Mock(return_value=mock_spell_data)
                elif "monsters" in url:
                    mock_response.json = Mock(return_value=mock_monster_data)
                return mock_response

            mock_client.return_value.__aenter__.return_value.get = mock_get

            # Run multiple requests concurrently
            spell_task = get_spell_info("magic-missile")
            monster_task = get_monster_info("goblin")
            
            spell_result, monster_result = await asyncio.gather(spell_task, monster_task)

            assert spell_result.name == "Magic Missile"
            assert monster_result.name == "Goblin"

    @pytest.mark.asyncio
    async def test_equipment_with_two_handed_damage(self):
        """Test equipment with two-handed damage (versatile weapons)."""
        mock_equipment_data = {
            "index": "longsword",
            "name": "Longsword",
            "equipment_category": {"index": "weapon", "name": "Weapon", "url": "/api/equipment-categories/weapon"},
            "weapon_category": "Martial",
            "weapon_range": "Melee",
            "cost": {"quantity": 15, "unit": "gp"},
            "damage": {
                "damage_dice": "1d8",
                "damage_type": {"index": "slashing", "name": "Slashing", "url": "/api/damage-types/slashing"}
            },
            "two_handed_damage": {
                "damage_dice": "1d10",
                "damage_type": {"index": "slashing", "name": "Slashing", "url": "/api/damage-types/slashing"}
            },
            "weight": 3,
            "properties": [
                {"index": "versatile", "name": "Versatile", "url": "/api/weapon-properties/versatile"}
            ],
            "url": "/api/equipment/longsword"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_equipment_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_equipment_info("longsword")

            assert result.damage.damage_dice == "1d8"
            assert result.two_handed_damage is not None
            assert result.two_handed_damage.damage_dice == "1d10"
            assert any(prop.name == "Versatile" for prop in result.properties)

    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test handling of HTTP errors other than 404."""
        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = Mock(return_value="Internal Server Error")
            mock_response.json = Mock(side_effect=ValueError("Server error"))

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            # Search should raise ValueError when status is not 200
            with pytest.raises(ValueError) as exc_info:
                await search_dnd_content(content_type="spells", query="test")
            
            assert "Failed to search spells" in str(exc_info.value)
            
            # For specific lookups, 500 errors cause JSON parsing to fail
            # Since response.json() is called without checking status code first
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json = Mock(side_effect=ValueError("Server error"))
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            with pytest.raises(ValueError) as exc_info:
                await get_spell_info("test")
            
            assert "Server error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_magic_item_with_variants(self):
        """Test magic item with variants."""
        mock_item_data = {
            "index": "bag-of-holding",
            "name": "Bag of Holding",
            "equipment_category": {"index": "wondrous-items", "name": "Wondrous Items", "url": "/api/equipment-categories/wondrous-items"},
            "rarity": {"name": "Uncommon"},
            "variants": [
                {"index": "bag-of-holding-1", "name": "Bag of Holding Type I", "url": "/api/magic-items/bag-of-holding-1"},
                {"index": "bag-of-holding-2", "name": "Bag of Holding Type II", "url": "/api/magic-items/bag-of-holding-2"}
            ],
            "variant": False,
            "desc": [
                "This bag has an interior space considerably larger than its outside dimensions...",
                "The bag can hold up to 500 pounds..."
            ],
            "url": "/api/magic-items/bag-of-holding"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_item_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_magic_item_info("bag-of-holding")

            assert result.name == "Bag of Holding"
            assert len(result.variants) == 2
            assert result.variant is False

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        # The functions return typed Pydantic models, not dicts
        # So we check if it's a Pydantic model instance
        from pydantic import BaseModel
        
        # For dict returns (utility functions)
        if isinstance(output, dict):
            assert "url" in output or "results" in output
            if "name" in output:
                assert isinstance(output["name"], str)
        # For Pydantic model returns
        elif isinstance(output, BaseModel):
            assert hasattr(output, "name") or hasattr(output, "results")
        else:
            raise AssertionError(f"Unexpected output type: {type(output)}")

    @pytest.mark.unit
    def test_all_api_functions_have_docstrings(self):
        """Test that all API functions have proper docstrings."""
        from packages.funcn_registry.components.tools.dnd_5e_api.tool import (
            get_ability_score_info,
            get_alignment_info,
            get_class_info,
            get_condition_info,
            get_damage_type_info,
            get_equipment_info,
            get_feat_info,
            get_language_info,
            get_magic_item_info,
            get_monster_info,
            get_proficiency_info,
            get_race_info,
            get_spell_info,
            get_weapon_property_info,
            search_dnd_content,
        )
        
        functions = [
            get_spell_info,
            get_class_info,
            get_monster_info,
            get_equipment_info,
            get_race_info,
            get_skill_info,
            get_condition_info,
            get_magic_item_info,
            search_dnd_content,
            get_feat_info,
            get_ability_score_info,
            get_proficiency_info,
            get_language_info,
            get_alignment_info,
            get_damage_type_info,
            get_weapon_property_info,
        ]

        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 20

    @pytest.mark.asyncio
    async def test_spell_with_multiple_classes(self):
        """Test spell available to multiple classes."""
        mock_spell_data = {
            "index": "cure-wounds",
            "name": "Cure Wounds",
            "level": 1,
            "school": {"index": "evocation", "name": "Evocation", "url": "/api/magic-schools/evocation"},
            "casting_time": "1 action",
            "range": "Touch",
            "components": ["V", "S"],
            "duration": "Instantaneous",
            "desc": ["A creature you touch regains a number of hit points equal to 1d8 + your spellcasting ability modifier."],
            "higher_level": ["When you cast this spell using a spell slot of 2nd level or higher, the healing increases by 1d8 for each slot level above 1st."],
            "classes": [
                {"index": "cleric", "name": "Cleric", "url": "/api/classes/cleric"},
                {"index": "druid", "name": "Druid", "url": "/api/classes/druid"},
                {"index": "paladin", "name": "Paladin", "url": "/api/classes/paladin"},
                {"index": "ranger", "name": "Ranger", "url": "/api/classes/ranger"}
            ],
            "concentration": False,
            "ritual": False,
            "url": "/api/spells/cure-wounds"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_spell_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_spell_info("cure-wounds")

            assert result.name == "Cure Wounds"
            assert len(result.classes) == 4
            assert any(cls.name == "Cleric" for cls in result.classes)
            assert result.ritual is False

    @pytest.mark.asyncio
    async def test_spell_ritual_casting(self):
        """Test spell that can be cast as a ritual."""
        mock_spell_data = {
            "index": "detect-magic",
            "name": "Detect Magic",
            "level": 1,
            "school": {"index": "divination", "name": "Divination", "url": "/api/magic-schools/divination"},
            "casting_time": "1 action",
            "range": "Self",
            "components": ["V", "S"],
            "duration": "Concentration, up to 10 minutes",
            "desc": ["For the duration, you sense the presence of magic within 30 feet of you."],
            "classes": [{"index": "wizard", "name": "Wizard", "url": "/api/classes/wizard"}],
            "concentration": True,
            "ritual": True,
            "url": "/api/spells/detect-magic"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_spell_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_spell_info("detect-magic")

            assert result.ritual is True
            assert result.concentration is True

    @pytest.mark.asyncio
    async def test_class_with_spellcasting(self):
        """Test class with spellcasting abilities."""
        mock_class_data = {
            "index": "wizard",
            "name": "Wizard",
            "hit_die": 6,
            "proficiencies": [],
            "proficiency_choices": [],
            "saving_throws": [
                {"index": "int", "name": "INT", "url": "/api/ability-scores/int"},
                {"index": "wis", "name": "WIS", "url": "/api/ability-scores/wis"}
            ],
            "starting_equipment": [],
            "starting_equipment_options": [],
            "class_levels": "/api/classes/wizard/levels",
            "multi_classing": {
                "prerequisites": [{"ability_score": {"index": "int", "name": "INT"}, "minimum_score": 13}],
                "proficiencies": []
            },
            "subclasses": [
                {"index": "evocation", "name": "Evocation", "url": "/api/subclasses/evocation"}
            ],
            "spellcasting": {
                "level": 1,
                "spellcasting_ability": {"index": "int", "name": "INT", "url": "/api/ability-scores/int"},
                "info": [
                    {
                        "name": "Cantrips",
                        "desc": ["At 1st level, you know three cantrips of your choice from the wizard spell list."]
                    },
                    {
                        "name": "Spellbook",
                        "desc": ["At 1st level, you have a spellbook containing six 1st-level wizard spells of your choice."]
                    }
                ]
            },
            "url": "/api/classes/wizard"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_class_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_class_info("wizard")

            assert result.spellcasting is not None
            assert result.spellcasting["level"] == 1
            assert result.spellcasting["spellcasting_ability"]["name"] == "INT"
            assert len(result.spellcasting["info"]) == 2

    @pytest.mark.asyncio
    async def test_monster_with_reactions(self):
        """Test monster with reactions."""
        mock_monster_data = {
            "index": "shield-guardian",
            "name": "Shield Guardian",
            "size": "Large",
            "type": "construct",
            "alignment": "unaligned",
            "armor_class": [{"value": 17, "type": "natural armor"}],
            "hit_points": 142,
            "hit_dice": "15d10",
            "hit_points_roll": "15d10+60",
            "speed": {"walk": "30 ft."},
            "strength": 18,
            "dexterity": 8,
            "constitution": 18,
            "intelligence": 7,
            "wisdom": 10,
            "charisma": 3,
            "proficiencies": [],
            "damage_vulnerabilities": [],
            "damage_resistances": [],
            "damage_immunities": ["poison"],
            "condition_immunities": [
                {"index": "charmed", "name": "Charmed", "url": "/api/conditions/charmed"},
                {"index": "exhaustion", "name": "Exhaustion", "url": "/api/conditions/exhaustion"},
                {"index": "frightened", "name": "Frightened", "url": "/api/conditions/frightened"},
                {"index": "paralyzed", "name": "Paralyzed", "url": "/api/conditions/paralyzed"},
                {"index": "poisoned", "name": "Poisoned", "url": "/api/conditions/poisoned"}
            ],
            "senses": {"blindsight": "10 ft.", "darkvision": "60 ft.", "passive_perception": 10},
            "languages": "understands commands given in any language but can't speak",
            "challenge_rating": 7,
            "proficiency_bonus": 3,
            "xp": 2900,
            "actions": [
                {
                    "name": "Multiattack",
                    "desc": "The guardian makes two fist attacks."
                },
                {
                    "name": "Fist",
                    "desc": "Melee Weapon Attack: +7 to hit, reach 5 ft., one target. Hit: 11 (2d6 + 4) bludgeoning damage."
                }
            ],
            "reactions": [
                {
                    "name": "Shield",
                    "desc": "When a creature makes an attack against the wearer of the guardian's amulet, the guardian grants a +2 bonus to the wearer's AC if the guardian is within 5 feet of the wearer."
                }
            ],
            "url": "/api/monsters/shield-guardian"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_monster_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_monster_info("shield-guardian")

            assert result.reactions is not None
            assert len(result.reactions) == 1
            assert result.reactions[0]["name"] == "Shield"

    @pytest.mark.asyncio
    async def test_race_with_ability_choice(self):
        """Test race with ability score choice."""
        mock_race_data = {
            "index": "half-elf",
            "name": "Half-Elf",
            "speed": 30,
            "ability_bonuses": [
                {"ability_score": {"index": "cha", "name": "CHA", "url": "/api/ability-scores/cha"}, "bonus": 2}
            ],
            "ability_bonus_options": {
                "desc": "Increase any two ability scores of your choice by 1",
                "choose": 2,
                "type": "ability_bonuses",
                "from.option_set_type": "options_array",
                "from.options": [
                    {"ability_score": {"index": "str", "name": "STR", "url": "/api/ability-scores/str"}, "bonus": 1},
                    {"ability_score": {"index": "dex", "name": "DEX", "url": "/api/ability-scores/dex"}, "bonus": 1},
                    {"ability_score": {"index": "con", "name": "CON", "url": "/api/ability-scores/con"}, "bonus": 1},
                    {"ability_score": {"index": "int", "name": "INT", "url": "/api/ability-scores/int"}, "bonus": 1},
                    {"ability_score": {"index": "wis", "name": "WIS", "url": "/api/ability-scores/wis"}, "bonus": 1}
                ]
            },
            "alignment": "Half-elves share the chaotic bent of their elven heritage.",
            "age": "Half-elves mature at the same rate humans do and reach adulthood around the age of 20.",
            "size": "Medium",
            "size_description": "Half-elves are about the same size as humans.",
            "starting_proficiencies": [],
            "languages": [
                {"index": "common", "name": "Common", "url": "/api/languages/common"},
                {"index": "elvish", "name": "Elvish", "url": "/api/languages/elvish"}
            ],
            "language_options": {
                "desc": "Choose one additional language",
                "choose": 1,
                "type": "languages",
                "from.option_set_type": "resource_list",
                "from.options": []
            },
            "traits": [
                {"index": "darkvision", "name": "Darkvision", "url": "/api/traits/darkvision"},
                {"index": "fey-ancestry", "name": "Fey Ancestry", "url": "/api/traits/fey-ancestry"}
            ],
            "subraces": [],
            "url": "/api/races/half-elf"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_race_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_race_info("half-elf")

            assert result.ability_bonus_options is not None
            assert result.ability_bonus_options.choose == 2
            assert result.language_options is not None

    @pytest.mark.asyncio
    async def test_equipment_ranged_weapon(self):
        """Test equipment that is a ranged weapon."""
        mock_equipment_data = {
            "index": "longbow",
            "name": "Longbow",
            "equipment_category": {"index": "weapon", "name": "Weapon", "url": "/api/equipment-categories/weapon"},
            "weapon_category": "Martial",
            "weapon_range": "Ranged",
            "category_range": "Martial Ranged",
            "cost": {"quantity": 50, "unit": "gp"},
            "damage": {
                "damage_dice": "1d8",
                "damage_type": {"index": "piercing", "name": "Piercing", "url": "/api/damage-types/piercing"}
            },
            "range": {"normal": 150, "long": 600},
            "weight": 2,
            "properties": [
                {"index": "ammunition", "name": "Ammunition", "url": "/api/weapon-properties/ammunition"},
                {"index": "heavy", "name": "Heavy", "url": "/api/weapon-properties/heavy"},
                {"index": "two-handed", "name": "Two-Handed", "url": "/api/weapon-properties/two-handed"}
            ],
            "url": "/api/equipment/longbow"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_equipment_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_equipment_info("longbow")

            assert result.weapon_range == "Ranged"
            assert result.range is not None
            assert result.range["normal"] == 150
            assert result.range["long"] == 600
            assert any(prop.name == "Ammunition" for prop in result.properties)

    @pytest.mark.asyncio
    async def test_feat_with_prerequisites(self):
        """Test feat with prerequisites."""
        mock_feat_data = {
            "index": "heavy-armor-master",
            "name": "Heavy Armor Master",
            "desc": [
                "Prerequisite: Proficiency with heavy armor",
                "You can use your armor to deflect strikes that would kill others. You gain the following benefits:",
                "• Increase your Strength score by 1, to a maximum of 20.",
                "• While you are wearing heavy armor, bludgeoning, piercing, and slashing damage that you take from nonmagical attacks is reduced by 3."
            ],
            "prerequisites": [
                {
                    "type": "proficiency",
                    "proficiency": {"index": "heavy-armor", "name": "Heavy Armor", "url": "/api/proficiencies/heavy-armor"}
                }
            ],
            "url": "/api/feats/heavy-armor-master"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_feat_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_feat_info
            
            result = await get_feat_info("heavy-armor-master")

            assert result.name == "Heavy Armor Master"
            assert len(result.prerequisites) == 1
            assert result.prerequisites[0]["type"] == "proficiency"

    @pytest.mark.asyncio
    async def test_search_with_level_filter(self):
        """Test spell search with level filter."""
        mock_search_results = {
            "count": 10,
            "results": [
                {"index": "fireball", "name": "Fireball"},
                {"index": "lightning-bolt", "name": "Lightning Bolt"},
                {"index": "counterspell", "name": "Counterspell"}
            ]
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            # Search for 3rd level spells
            result = await search_dnd_content(content_type="spells", level=3)

            # Verify that the API was called with the level parameter
            mock_client.return_value.__aenter__.return_value.get.assert_called_once()
            call_args = mock_client.return_value.__aenter__.return_value.get.call_args
            assert call_args[1]["params"]["level"] == 3

    @pytest.mark.asyncio
    async def test_search_with_school_filter(self):
        """Test spell search with school filter."""
        mock_search_results = {
            "count": 5,
            "results": [
                {"index": "charm-person", "name": "Charm Person"},
                {"index": "sleep", "name": "Sleep"},
                {"index": "hold-person", "name": "Hold Person"}
            ]
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            # Search for enchantment spells
            result = await search_dnd_content(content_type="spells", school="enchantment")

            # Verify that the API was called with the school parameter
            call_args = mock_client.return_value.__aenter__.return_value.get.call_args
            assert call_args[1]["params"]["school"] == "enchantment"

    @pytest.mark.asyncio
    async def test_search_monsters_by_type(self):
        """Test monster search with type filter."""
        mock_search_results = {
            "count": 15,
            "results": [
                {"index": "red-dragon-wyrmling", "name": "Red Dragon Wyrmling"},
                {"index": "young-red-dragon", "name": "Young Red Dragon"},
                {"index": "adult-red-dragon", "name": "Adult Red Dragon"}
            ]
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_search_results)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            # Search for dragon type monsters
            result = await search_dnd_content(content_type="monsters", type="dragon")

            # Verify that the API was called with the type parameter
            call_args = mock_client.return_value.__aenter__.return_value.get.call_args
            assert call_args[1]["params"]["type"] == "dragon"

    @pytest.mark.asyncio
    async def test_monster_with_special_abilities(self):
        """Test monster with special abilities."""
        mock_monster_data = {
            "index": "vampire",
            "name": "Vampire",
            "size": "Medium",
            "type": "undead",
            "subtype": "shapechanger",
            "alignment": "lawful evil",
            "armor_class": [{"value": 16, "type": "natural armor"}],
            "hit_points": 144,
            "hit_dice": "17d8",
            "hit_points_roll": "17d8+68",
            "speed": {"walk": "30 ft."},
            "strength": 18,
            "dexterity": 18,
            "constitution": 18,
            "intelligence": 17,
            "wisdom": 15,
            "charisma": 18,
            "proficiencies": [],
            "damage_vulnerabilities": [],
            "damage_resistances": ["necrotic", "bludgeoning, piercing, and slashing from nonmagical attacks"],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": {"darkvision": "120 ft.", "passive_perception": 17},
            "languages": "the languages it knew in life",
            "challenge_rating": 13,
            "proficiency_bonus": 5,
            "xp": 10000,
            "special_abilities": [
                {
                    "name": "Shapechanger",
                    "desc": "If the vampire isn't in sunlight or running water, it can use its action to polymorph into a Tiny bat or a Medium cloud of mist, or back into its true form."
                },
                {
                    "name": "Legendary Resistance (3/Day)",
                    "desc": "If the vampire fails a saving throw, it can choose to succeed instead."
                },
                {
                    "name": "Misty Escape",
                    "desc": "When it drops to 0 hit points outside its resting place, the vampire transforms into a cloud of mist instead of falling unconscious."
                },
                {
                    "name": "Regeneration",
                    "desc": "The vampire regains 20 hit points at the start of its turn if it has at least 1 hit point and isn't in sunlight or running water."
                }
            ],
            "actions": [],
            "url": "/api/monsters/vampire"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_monster_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_monster_info("vampire")

            assert result.special_abilities is not None
            assert len(result.special_abilities) == 4
            assert any(ability["name"] == "Shapechanger" for ability in result.special_abilities)
            assert result.subtype == "shapechanger"

    @pytest.mark.asyncio
    async def test_class_with_proficiency_choices(self):
        """Test class with proficiency choices."""
        mock_class_data = {
            "index": "rogue",
            "name": "Rogue",
            "hit_die": 8,
            "proficiency_choices": [
                {
                    "desc": "Choose four from Acrobatics, Athletics, Deception, Insight, Intimidation, Investigation, Perception, Performance, Persuasion, Sleight of Hand, and Stealth",
                    "choose": 4,
                    "type": "proficiencies",
                    "from.option_set_type": "options_array",
                    "from.options": [
                        {"item": {"index": "skill-acrobatics", "name": "Skill: Acrobatics", "url": "/api/proficiencies/skill-acrobatics"}},
                        {"item": {"index": "skill-athletics", "name": "Skill: Athletics", "url": "/api/proficiencies/skill-athletics"}},
                        {"item": {"index": "skill-deception", "name": "Skill: Deception", "url": "/api/proficiencies/skill-deception"}}
                    ]
                }
            ],
            "proficiencies": [
                {"index": "light-armor", "name": "Light armor", "url": "/api/proficiencies/light-armor"},
                {"index": "simple-weapons", "name": "Simple weapons", "url": "/api/proficiencies/simple-weapons"}
            ],
            "saving_throws": [
                {"index": "dex", "name": "DEX", "url": "/api/ability-scores/dex"},
                {"index": "int", "name": "INT", "url": "/api/ability-scores/int"}
            ],
            "starting_equipment": [],
            "starting_equipment_options": [],
            "class_levels": "/api/classes/rogue/levels",
            "multi_classing": {},
            "subclasses": [],
            "url": "/api/classes/rogue"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_class_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_class_info("rogue")

            assert len(result.proficiency_choices) == 1
            assert result.proficiency_choices[0].choose == 4
            assert "Acrobatics" in result.proficiency_choices[0].desc

    @pytest.mark.asyncio
    async def test_alignment_abbreviation_lookup(self):
        """Test alignment lookup using abbreviation."""
        mock_alignment_data = {
            "index": "chaotic-evil",
            "name": "Chaotic Evil",
            "abbreviation": "CE",
            "desc": "Chaotic evil (CE) creatures act with arbitrary violence, spurred by their greed, hatred, or bloodlust.",
            "url": "/api/alignments/chaotic-evil"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_alignment_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_alignment_info
            
            result = await get_alignment_info("ce")

            assert result["name"] == "Chaotic Evil"
            assert result["abbreviation"] == "CE"

    @pytest.mark.asyncio
    async def test_ability_score_abbreviation_lookup(self):
        """Test ability score lookup using full name."""
        mock_ability_data = {
            "index": "dex",
            "name": "DEX",
            "full_name": "Dexterity",
            "desc": [
                "Dexterity measures agility, reflexes, and balance."
            ],
            "skills": [
                {"index": "acrobatics", "name": "Acrobatics", "url": "/api/skills/acrobatics"},
                {"index": "sleight-of-hand", "name": "Sleight of Hand", "url": "/api/skills/sleight-of-hand"},
                {"index": "stealth", "name": "Stealth", "url": "/api/skills/stealth"}
            ],
            "url": "/api/ability-scores/dex"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_ability_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            from packages.funcn_registry.components.tools.dnd_5e_api.tool import get_ability_score_info
            
            result = await get_ability_score_info("dexterity")

            assert result["name"] == "DEX"
            assert result["full_name"] == "Dexterity"
            assert len(result["skills"]) == 3

    @pytest.mark.asyncio
    async def test_equipment_simple_item(self):
        """Test simple equipment without weapon/armor properties."""
        mock_equipment_data = {
            "index": "rope-hempen-50-feet",
            "name": "Rope, hempen (50 feet)",
            "equipment_category": {"index": "adventuring-gear", "name": "Adventuring Gear", "url": "/api/equipment-categories/adventuring-gear"},
            "gear_category": {"index": "standard-gear", "name": "Standard Gear", "url": "/api/equipment-categories/standard-gear"},
            "cost": {"quantity": 1, "unit": "gp"},
            "weight": 10,
            "desc": ["Rope, whether made of hemp or silk, has 2 hit points and can be burst with a DC 17 Strength check."],
            "url": "/api/equipment/rope-hempen-50-feet"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_equipment_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_equipment_info("rope-hempen-50-feet")

            assert result.name == "Rope, hempen (50 feet)"
            assert result.gear_category is not None
            assert result.weapon_category is None
            assert result.armor_category is None
            assert len(result.desc) == 1

    @pytest.mark.asyncio
    async def test_spell_cantrip(self):
        """Test cantrip (0-level spell)."""
        mock_spell_data = {
            "index": "mage-hand",
            "name": "Mage Hand",
            "level": 0,
            "school": {"index": "conjuration", "name": "Conjuration", "url": "/api/magic-schools/conjuration"},
            "casting_time": "1 action",
            "range": "30 feet",
            "components": ["V", "S"],
            "duration": "1 minute",
            "desc": ["A spectral, floating hand appears at a point you choose within range."],
            "classes": [
                {"index": "wizard", "name": "Wizard", "url": "/api/classes/wizard"},
                {"index": "sorcerer", "name": "Sorcerer", "url": "/api/classes/sorcerer"},
                {"index": "warlock", "name": "Warlock", "url": "/api/classes/warlock"}
            ],
            "concentration": False,
            "ritual": False,
            "url": "/api/spells/mage-hand"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_spell_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_spell_info("mage-hand")

            assert result.name == "Mage Hand"
            assert result.level == 0  # Cantrip
            assert result.material is None  # No material component

    @pytest.mark.asyncio
    async def test_json_parsing_error(self):
        """Test handling of JSON parsing errors."""
        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(side_effect=ValueError("Invalid JSON"))

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            with pytest.raises(ValueError) as exc_info:
                await get_spell_info("test-spell")

            assert "Invalid JSON" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_missing_optional_fields(self):
        """Test handling of missing optional fields in API response."""
        # Minimal spell data with many optional fields missing
        mock_spell_data = {
            "index": "test-spell",
            "name": "Test Spell",
            "level": 1,
            "school": {"index": "evocation", "name": "Evocation", "url": "/api/magic-schools/evocation"},
            "casting_time": "1 action",
            "range": "30 feet",
            "components": ["V"],
            "duration": "Instantaneous",
            "desc": ["Test description"],
            "classes": [],
            "concentration": False,
            "url": "/api/spells/test-spell"
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=mock_spell_data)

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

            result = await get_spell_info("test-spell")

            assert result.material is None
            assert result.higher_level is None
            assert result.damage is None
            assert result.dc is None
            assert result.area_of_effect is None
            assert result.ritual is False  # Defaults to False
