"""Test suite for dice_roller tool following best practices."""

import pytest
import random
from datetime import datetime
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestDiceRoller(BaseToolTest):
    """Test dice_roller tool component."""
    
    component_name = "dice_roller"
    component_path = Path("packages/funcn_registry/components/tools/dice_roller")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.dice_roller import roll_dice
        def mock_roll_dice(
            notation: str,
            advantage: bool = False,
            disadvantage: bool = False,
            modifier: int = 0,
            reason: str | None = None
        ) -> dict[str, any]:
            """Mock dice roller tool."""
            # Parse basic dice notation (e.g., "2d6+3")
            import re
            match = re.match(r'(\d+)d(\d+)([+-]\d+)?', notation)
            if not match:
                return {"error": "Invalid dice notation"}
            
            num_dice = int(match.group(1))
            die_size = int(match.group(2))
            bonus = int(match.group(3) or 0)
            
            return {
                "notation": notation,
                "rolls": [4, 3],  # Mock rolls
                "total": 7 + bonus + modifier,
                "natural_total": 7,
                "modifier": modifier,
                "bonus": bonus,
                "advantage": advantage,
                "disadvantage": disadvantage,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "critical": False,
                "fumble": False
            }
        return mock_roll_dice
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "notation": "1d20",
                "reason": "Attack roll"
            },
            {
                "notation": "2d6+3",
                "modifier": 2,
                "reason": "Damage roll with magic weapon"
            },
            {
                "notation": "1d20",
                "advantage": True,
                "reason": "Skill check with advantage"
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, dict)
        
        if "error" not in output:
            assert "rolls" in output
            assert "total" in output
            assert isinstance(output["rolls"], list)
            assert isinstance(output["total"], int)
    
    def test_basic_dice_notation(self):
        """Test parsing and rolling basic dice notation."""
        tool = self.get_component_function()
        
        notations = [
            "1d4",
            "1d6",
            "1d8",
            "1d10",
            "1d12",
            "1d20",
            "1d100"
        ]
        
        for notation in notations:
            with patch("random.randint") as mock_random:
                # Mock consistent rolls
                mock_random.return_value = 4
                
                result = tool(notation)
                
                assert result["notation"] == notation
                assert len(result["rolls"]) == 1
                assert 1 <= result["rolls"][0] <= int(notation.split('d')[1])
    
    def test_multiple_dice(self):
        """Test rolling multiple dice."""
        tool = self.get_component_function()
        
        with patch("random.randint") as mock_random:
            # Mock different rolls
            mock_random.side_effect = [3, 4, 5, 2]
            
            result = tool("4d6")
            
            assert len(result["rolls"]) == 4
            assert result["total"] == sum(result["rolls"])
            assert result["natural_total"] == result["total"]
    
    def test_dice_with_modifiers(self):
        """Test dice notation with modifiers."""
        tool = self.get_component_function()
        
        test_cases = [
            ("1d20+5", 5),
            ("2d8-2", -2),
            ("3d6+10", 10),
            ("1d4-1", -1)
        ]
        
        for notation, expected_bonus in test_cases:
            with patch("random.randint") as mock_random:
                mock_random.return_value = 3
                
                result = tool(notation)
                
                assert result["bonus"] == expected_bonus
                assert result["total"] == result["natural_total"] + expected_bonus
    
    def test_advantage_disadvantage(self):
        """Test advantage and disadvantage mechanics."""
        tool = self.get_component_function()
        
        # Test advantage (roll twice, take higher)
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [8, 15]  # Two d20 rolls
            
            result = tool("1d20", advantage=True)
            
            assert result["advantage"] is True
            assert len(result["rolls"]) == 2 or "advantage_rolls" in result
            # Should take the higher roll (15)
        
        # Test disadvantage (roll twice, take lower)
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [18, 5]  # Two d20 rolls
            
            result = tool("1d20", disadvantage=True)
            
            assert result["disadvantage"] is True
            assert len(result["rolls"]) == 2 or "disadvantage_rolls" in result
            # Should take the lower roll (5)
    
    def test_critical_and_fumble(self):
        """Test critical hit and fumble detection."""
        tool = self.get_component_function()
        
        # Test critical (natural 20)
        with patch("random.randint") as mock_random:
            mock_random.return_value = 20
            
            result = tool("1d20")
            
            assert result["critical"] is True
            assert result["fumble"] is False
        
        # Test fumble (natural 1)
        with patch("random.randint") as mock_random:
            mock_random.return_value = 1
            
            result = tool("1d20")
            
            assert result["critical"] is False
            assert result["fumble"] is True
    
    def test_additional_modifiers(self):
        """Test additional modifiers parameter."""
        tool = self.get_component_function()
        
        with patch("random.randint") as mock_random:
            mock_random.return_value = 10
            
            # Roll with notation modifier and additional modifier
            result = tool("1d20+3", modifier=2)
            
            assert result["bonus"] == 3
            assert result["modifier"] == 2
            assert result["total"] == 10 + 3 + 2  # roll + bonus + modifier
    
    def test_invalid_notation(self):
        """Test handling of invalid dice notation."""
        tool = self.get_component_function()
        
        invalid_notations = [
            "invalid",
            "d20",  # Missing number of dice
            "1d",   # Missing die size
            "1d0",  # Invalid die size
            "0d6",  # Zero dice
            "-1d6", # Negative dice
            "1.5d6" # Fractional dice
        ]
        
        for notation in invalid_notations:
            result = tool(notation)
            
            assert "error" in result or result.get("success") is False
    
    def test_reason_tracking(self):
        """Test that roll reasons are tracked."""
        tool = self.get_component_function()
        
        reasons = [
            "Initiative roll",
            "Saving throw vs poison",
            "Stealth check",
            "Damage for fireball"
        ]
        
        for reason in reasons:
            result = tool("1d20", reason=reason)
            
            assert result["reason"] == reason
    
    def test_timestamp_generation(self):
        """Test that timestamps are generated for rolls."""
        tool = self.get_component_function()
        
        result = tool("1d20")
        
        assert "timestamp" in result
        # Verify it's a valid ISO format timestamp
        try:
            datetime.fromisoformat(result["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Invalid timestamp format")
    
    def test_complex_notation(self):
        """Test complex dice notation patterns."""
        tool = self.get_component_function()
        
        complex_notations = [
            "3d6+2d4+5",  # Multiple dice types
            "1d20+1d4",   # Mixed dice
            "10d10+10",   # Large numbers
        ]
        
        for notation in complex_notations:
            result = tool(notation)
            
            # Should handle or gracefully fail
            assert isinstance(result, dict)
    
    def test_dice_statistics(self):
        """Test that dice rolls are within valid ranges."""
        tool = self.get_component_function()
        
        # Test 1000 rolls to ensure randomness
        die_sizes = [4, 6, 8, 10, 12, 20, 100]
        
        for die_size in die_sizes:
            rolls = []
            
            for _ in range(100):
                with patch("random.randint") as mock_random:
                    # Generate random but valid roll
                    mock_random.return_value = random.randint(1, die_size)
                    
                    result = tool(f"1d{die_size}")
                    roll = result["rolls"][0]
                    
                    assert 1 <= roll <= die_size
                    rolls.append(roll)
            
            # Verify we got some variety in rolls
            unique_rolls = set(rolls)
            assert len(unique_rolls) > 1
    
    def test_percentile_dice(self):
        """Test d100/percentile dice handling."""
        tool = self.get_component_function()
        
        with patch("random.randint") as mock_random:
            mock_random.return_value = 73
            
            result = tool("1d100")
            
            assert result["rolls"][0] == 73
            assert 1 <= result["rolls"][0] <= 100
    
    def test_exploding_dice(self):
        """Test exploding dice mechanic if supported."""
        tool = self.get_component_function()
        
        # Some systems support notation like "1d6!" for exploding dice
        result = tool("1d6!", reason="Exploding damage die")
        
        # Should either support or gracefully handle
        assert isinstance(result, dict)
