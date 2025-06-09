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
            "school": {"name": "Evocation"},
            "casting_time": "1 action",
            "range": "150 feet",
            "components": ["V", "S", "M"],
            "material": "A tiny ball of bat guano and sulfur",
            "duration": "Instantaneous",
            "desc": ["A bright streak flashes from your pointing finger..."],
            "higher_level": ["When you cast this spell using a spell slot of 4th level or higher..."],
            "damage": {"damage_type": {"name": "Fire"}, "damage_at_slot_level": {"3": "8d6"}},
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_spell_data)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await get_spell_info("fireball")

            assert result["name"] == "Fireball"
            assert result["level"] == 3
            assert result["school"]["name"] == "Evocation"
            assert "8d6" in str(result["damage"])

    @pytest.mark.asyncio
    async def test_get_class_success(self):
        """Test successful class retrieval."""
        mock_class_data = {
            "index": "wizard",
            "name": "Wizard",
            "hit_die": 6,
            "proficiencies": [{"name": "Daggers"}, {"name": "Darts"}],
            "saving_throws": [{"name": "INT"}, {"name": "WIS"}],
            "starting_equipment": [{"equipment": {"name": "Spellbook"}}],
            "spellcasting": {"level": 1, "spellcasting_ability": {"name": "INT"}},
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_class_data)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await get_class_info("wizard")

            assert result["name"] == "Wizard"
            assert result["hit_die"] == 6
            assert result["spellcasting"]["spellcasting_ability"]["name"] == "INT"

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
            "speed": {"walk": "30 ft."},
            "strength": 8,
            "dexterity": 14,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 8,
            "charisma": 8,
            "challenge_rating": 0.25,
            "actions": [{"name": "Scimitar", "desc": "Melee Weapon Attack: +4 to hit..."}],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_monster_data)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await get_monster_info("goblin")

            assert result["name"] == "Goblin"
            assert result["challenge_rating"] == 0.25
            assert result["armor_class"][0]["value"] == 15

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

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_search_results)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await search_dnd_content(query="fire", content_type="spells")

            assert result["count"] == 3
            assert len(result["results"]) == 3
            assert any(spell["name"] == "Fireball" for spell in result["results"])

    @pytest.mark.asyncio
    async def test_search_with_filters(self):
        """Test search with level and school filters."""
        mock_search_results = {
            "count": 1,
            "results": [
                {"index": "fireball", "name": "Fireball"},
            ],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_search_results)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await search_dnd_content(query="fire level:3 school:evocation", content_type="spells")

            # Verify search was called
            assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_get_equipment_success(self):
        """Test equipment retrieval."""
        mock_equipment_data = {
            "index": "longsword",
            "name": "Longsword",
            "equipment_category": {"name": "Weapon"},
            "weapon_category": "Martial",
            "weapon_range": "Melee",
            "cost": {"quantity": 15, "unit": "gp"},
            "damage": {"damage_dice": "1d8", "damage_type": {"name": "Slashing"}},
            "weight": 3,
            "properties": [{"name": "Versatile"}],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_equipment_data)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await get_equipment_info("longsword")

            assert result["name"] == "Longsword"
            assert result["damage"]["damage_dice"] == "1d8"
            assert result["cost"]["quantity"] == 15

    @pytest.mark.asyncio
    async def test_not_found_error(self):
        """Test handling of 404 not found errors."""
        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.text = AsyncMock(return_value="Not found")

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await get_spell_info("nonexistent-spell")

            assert "404" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test handling of API errors."""
        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.get = AsyncMock(side_effect=Exception("Connection error"))

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
            "ability_bonuses": [{"ability_score": {"name": "DEX"}, "bonus": 2}],
            "size": "Medium",
            "languages": [{"name": "Common"}, {"name": "Elvish"}],
            "traits": [{"name": "Darkvision"}, {"name": "Keen Senses"}],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_race_data)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await get_race_info("elf")

            assert result["name"] == "Elf"
            assert result["speed"] == 30
            assert len(result["languages"]) == 2

    @pytest.mark.asyncio
    async def test_get_condition_success(self):
        """Test condition retrieval."""
        mock_condition_data = {
            "index": "poisoned",
            "name": "Poisoned",
            "desc": [
                "A poisoned creature has disadvantage on attack rolls and ability checks.",
            ],
        }

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_condition_data)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await get_condition_info("poisoned")

            assert result["name"] == "Poisoned"
            assert "disadvantage" in result["desc"][0]

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

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_search_results)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await search_dnd_content(query="cr:0.25", content_type="monsters")

            # Verify search was performed
            assert "results" in result

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

        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_search_results)

            mock_session.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            mock_response.__aenter__.return_value = mock_response

            result = await search_dnd_content(query="bag", content_type="magic-items")

            assert result["count"] == 2
            assert any(item["name"] == "Bag of Holding" for item in result["results"])

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test handling of request timeouts."""
        with patch("packages.funcn_registry.components.tools.dnd_5e_api.tool.aiohttp.ClientSession") as mock_session:
            mock_session.return_value.__aenter__.return_value.get = AsyncMock(side_effect=TimeoutError("Request timeout"))

            with pytest.raises(asyncio.TimeoutError) as exc_info:
                await get_spell_info("fireball")

            assert "Request timeout" in str(exc_info.value)

    def validate_tool_output(self, output, input_data):
        """Validate the tool output structure."""
        assert isinstance(output, dict), "Output should be a dictionary"

        # Check for common D&D 5e data fields based on the type
        if "name" in output:
            assert isinstance(output["name"], str)

        # For search results
        if "results" in output:
            assert isinstance(output["results"], list)
            assert "count" in output

    @pytest.mark.unit
    def test_all_api_functions_have_docstrings(self):
        """Test that all API functions have proper docstrings."""
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
        ]

        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 20
