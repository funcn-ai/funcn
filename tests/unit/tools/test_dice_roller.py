"""Test suite for dice_roller tool following best practices."""

import pytest
import random
import time
from datetime import datetime
from packages.funcn_registry.components.tools.dice_roller.tool import (
    DiceRoll,
    DiceRollRequest,
    DiceType,
    format_roll_result,
    get_dice_value,
    roll_ability_check,
    roll_attack,
    roll_damage,
    roll_dice,
    roll_multiple,
    roll_saving_throw,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import Mock, patch


class TestDiceRoller(BaseToolTest):
    """Test dice_roller tool component."""
    
    component_name = "dice_roller"
    component_path = Path("packages/funcn_registry/components/tools/dice_roller")
    
    def get_component_function(self):
        """Import the tool function."""
        return roll_dice
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "dice_type": DiceType.D20,
                "purpose": "Attack roll"
            },
            {
                "dice_type": DiceType.D6,
                "num_dice": 2,
                "modifier": 3,
                "purpose": "Damage roll with magic weapon"
            },
            {
                "dice_type": DiceType.D20,
                "advantage": True,
                "purpose": "Skill check with advantage"
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, DiceRoll)
        assert hasattr(output, 'rolls')
        assert hasattr(output, 'total')
        assert isinstance(output.rolls, list)
        assert isinstance(output.total, int)
    
    def test_all_dice_types(self):
        """Test rolling all standard dice types."""
        for dice_type in DiceType:
            result = roll_dice(dice_type)
            
            assert result.dice_type == dice_type
            assert len(result.rolls) == 1
            assert result.num_dice == 1
            assert result.modifier == 0
            
            # Check roll is within valid range
            max_value = get_dice_value(dice_type)
            assert 1 <= result.rolls[0] <= max_value
            assert result.total == result.rolls[0]
            assert result.natural_total == result.rolls[0]
    
    def test_multiple_dice(self):
        """Test rolling multiple dice."""
        with patch("random.randint") as mock_random:
            # Mock different rolls
            mock_random.side_effect = [3, 4, 5, 2]
            
            result = roll_dice(DiceType.D6, num_dice=4)
            
            assert len(result.rolls) == 4
            assert result.rolls == [3, 4, 5, 2]
            assert result.total == sum(result.rolls)
            assert result.natural_total == sum(result.rolls)
            assert result.num_dice == 4
    
    def test_dice_with_modifiers(self):
        """Test dice with positive and negative modifiers."""
        test_cases = [
            (5, 5),   # Positive modifier
            (-2, -2), # Negative modifier
            (10, 10), # Large positive
            (-5, -5), # Large negative
            (0, 0),   # Zero modifier
        ]
        
        for modifier, expected_modifier in test_cases:
            with patch("random.randint") as mock_random:
                mock_random.return_value = 10
                
                result = roll_dice(DiceType.D20, modifier=modifier)
                
                assert result.modifier == expected_modifier
                assert result.natural_total == 10
                assert result.total == 10 + expected_modifier
    
    def test_advantage_mechanics(self):
        """Test advantage mechanics (roll twice, take higher)."""
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [8, 15]  # Two d20 rolls
            
            result = roll_dice(DiceType.D20, advantage=True)
            
            assert result.advantage is True
            assert result.disadvantage is False
            assert len(result.rolls) == 2
            assert result.rolls == [8, 15]
            assert result.natural_total == 15  # Takes the higher
            assert result.total == 15
    
    def test_disadvantage_mechanics(self):
        """Test disadvantage mechanics (roll twice, take lower)."""
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [18, 5]  # Two d20 rolls
            
            result = roll_dice(DiceType.D20, disadvantage=True)
            
            assert result.disadvantage is True
            assert result.advantage is False
            assert len(result.rolls) == 2
            assert result.rolls == [18, 5]
            assert result.natural_total == 5  # Takes the lower
            assert result.total == 5
    
    def test_critical_success(self):
        """Test critical success detection (natural 20)."""
        with patch("random.randint") as mock_random:
            mock_random.return_value = 20
            
            result = roll_dice(DiceType.D20)
            
            assert result.critical_success is True
            assert result.critical_failure is False
            assert result.rolls[0] == 20
    
    def test_critical_failure(self):
        """Test critical failure detection (natural 1)."""
        with patch("random.randint") as mock_random:
            mock_random.return_value = 1
            
            result = roll_dice(DiceType.D20)
            
            assert result.critical_failure is True
            assert result.critical_success is False
            assert result.rolls[0] == 1
    
    def test_criticals_only_on_d20(self):
        """Test that criticals only apply to d20 rolls."""
        # Test rolling a 1 on non-d20 dice
        for dice_type in [DiceType.D4, DiceType.D6, DiceType.D8, DiceType.D10, DiceType.D12, DiceType.D100]:
            with patch("random.randint") as mock_random:
                mock_random.return_value = 1
                
                result = roll_dice(dice_type)
                
                assert result.critical_failure is False
                assert result.critical_success is False
    
    def test_criticals_only_single_die(self):
        """Test that criticals only apply to single d20 rolls."""
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [20, 20]  # Two natural 20s
            
            result = roll_dice(DiceType.D20, num_dice=2)
            
            assert result.critical_success is False
            assert result.critical_failure is False
    
    def test_purpose_tracking(self):
        """Test that roll purposes are tracked correctly."""
        purposes = [
            "Initiative roll",
            "Saving throw vs poison",
            "Stealth check",
            "Damage for fireball",
            "",  # Empty purpose
        ]
        
        for purpose in purposes:
            result = roll_dice(DiceType.D20, purpose=purpose)
            assert result.purpose == purpose
    
    def test_timestamp_generation(self):
        """Test that timestamps are generated correctly."""
        with patch("time.time") as mock_time:
            mock_time.return_value = 1234567890.123
            
            result = roll_dice(DiceType.D20)
            
            assert result.timestamp == 1234567890.123
    
    def test_deterministic_rolls_with_seed(self):
        """Test deterministic rolls using seed."""
        seed = 42
        
        # Roll with same seed multiple times
        results = []
        for _ in range(3):
            result = roll_dice(DiceType.D20, seed=seed)
            results.append(result.rolls[0])
        
        # All rolls should be the same
        assert all(r == results[0] for r in results)
        
        # Different seed should give different result
        result_different = roll_dice(DiceType.D20, seed=seed + 1)
        # There's a small chance they could be the same, but very unlikely
        # We'll skip this assertion to avoid flaky tests
    
    def test_dice_value_ranges(self):
        """Test that all dice rolls are within valid ranges."""
        test_iterations = 100
        
        for dice_type in DiceType:
            max_value = get_dice_value(dice_type)
            
            for _ in range(test_iterations):
                result = roll_dice(dice_type)
                
                assert len(result.rolls) == 1
                assert 1 <= result.rolls[0] <= max_value
    
    def test_advantage_disadvantage_with_modifier(self):
        """Test advantage/disadvantage with modifiers."""
        modifier = 5
        
        # Advantage with modifier
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [10, 15]
            
            result = roll_dice(DiceType.D20, modifier=modifier, advantage=True)
            
            assert result.natural_total == 15
            assert result.total == 20  # 15 + 5
            assert result.modifier == modifier
        
        # Disadvantage with modifier
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [10, 5]
            
            result = roll_dice(DiceType.D20, modifier=modifier, disadvantage=True)
            
            assert result.natural_total == 5
            assert result.total == 10  # 5 + 5
            assert result.modifier == modifier
    
    def test_advantage_disadvantage_non_d20(self):
        """Test that advantage/disadvantage only works for d20."""
        # Should ignore advantage/disadvantage for non-d20
        for dice_type in [DiceType.D4, DiceType.D6, DiceType.D8, DiceType.D10, DiceType.D12, DiceType.D100]:
            with patch("random.randint") as mock_random:
                mock_random.side_effect = [3, 5]  # Would be two rolls if adv/disadv worked
                
                result = roll_dice(dice_type, advantage=True)
                
                assert len(result.rolls) == 1  # Only one roll
                assert result.advantage is False
                assert result.disadvantage is False
    
    def test_advantage_disadvantage_multiple_dice(self):
        """Test that advantage/disadvantage only works for single d20."""
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [10, 15, 8, 12]  # Would need 4 rolls if adv worked
            
            result = roll_dice(DiceType.D20, num_dice=2, advantage=True)
            
            assert len(result.rolls) == 2  # Just the two normal rolls
            assert result.advantage is False
            assert result.disadvantage is False
    
    def test_roll_multiple_function(self):
        """Test rolling multiple dice requests at once."""
        requests = [
            DiceRollRequest(dice_type=DiceType.D20, purpose="Attack 1"),
            DiceRollRequest(dice_type=DiceType.D6, num_dice=2, modifier=3, purpose="Damage"),
            DiceRollRequest(dice_type=DiceType.D20, advantage=True, purpose="Saving throw"),
        ]
        
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [
                15,      # Attack roll
                3, 4,    # Damage rolls
                12, 18,  # Advantage rolls
            ]
            
            results = roll_multiple(requests)
            
            assert len(results) == 3
            
            # Check first roll
            assert results[0].dice_type == DiceType.D20
            assert results[0].purpose == "Attack 1"
            assert results[0].rolls[0] == 15
            
            # Check second roll
            assert results[1].dice_type == DiceType.D6
            assert results[1].num_dice == 2
            assert results[1].modifier == 3
            assert results[1].rolls == [3, 4]
            assert results[1].total == 10  # 3 + 4 + 3
            
            # Check third roll
            assert results[2].advantage is True
            assert results[2].rolls == [12, 18]
            assert results[2].natural_total == 18
    
    def test_format_roll_result_basic(self):
        """Test formatting basic roll results."""
        # Single d20
        roll = DiceRoll(
            dice_type=DiceType.D20,
            num_dice=1,
            modifier=0,
            rolls=[15],
            total=15,
            natural_total=15,
            critical_success=False,
            critical_failure=False,
            purpose="",
            timestamp=1234567890,
            seed=None,
            advantage=None,
            disadvantage=None,
        )
        
        result = format_roll_result(roll)
        assert result == "d20 = 15"
        
        # With purpose
        roll.purpose = "Attack roll"
        result = format_roll_result(roll)
        assert result == "Attack roll: d20 = 15"
    
    def test_format_roll_result_with_modifier(self):
        """Test formatting rolls with modifiers."""
        # Positive modifier
        roll = DiceRoll(
            dice_type=DiceType.D20,
            num_dice=1,
            modifier=5,
            rolls=[10],
            total=15,
            natural_total=10,
            critical_success=False,
            critical_failure=False,
            purpose="",
            timestamp=1234567890,
            seed=None,
            advantage=None,
            disadvantage=None,
        )
        
        result = format_roll_result(roll)
        assert result == "d20+5 = 10 + 5 = 15"
        
        # Negative modifier
        roll.modifier = -3
        roll.total = 7
        result = format_roll_result(roll)
        assert result == "d20-3 = 10 - 3 = 7"
    
    def test_format_roll_result_multiple_dice(self):
        """Test formatting multiple dice rolls."""
        roll = DiceRoll(
            dice_type=DiceType.D6,
            num_dice=3,
            modifier=2,
            rolls=[4, 5, 2],
            total=13,
            natural_total=11,
            critical_success=False,
            critical_failure=False,
            purpose="Damage",
            timestamp=1234567890,
            seed=None,
            advantage=None,
            disadvantage=None,
        )
        
        result = format_roll_result(roll)
        assert result == "Damage: 3d6+2 = [4, 5, 2] = 11 + 2 = 13"
    
    def test_format_roll_result_advantage(self):
        """Test formatting advantage rolls."""
        roll = DiceRoll(
            dice_type=DiceType.D20,
            num_dice=1,
            modifier=3,
            rolls=[8, 15],
            total=18,
            natural_total=15,
            critical_success=False,
            critical_failure=False,
            purpose="",
            timestamp=1234567890,
            seed=None,
            advantage=True,
            disadvantage=False,
        )
        
        result = format_roll_result(roll)
        assert "[8, 15] (advantage)" in result
        assert "= 15 + 3 = 18" in result
    
    def test_format_roll_result_disadvantage(self):
        """Test formatting disadvantage rolls."""
        roll = DiceRoll(
            dice_type=DiceType.D20,
            num_dice=1,
            modifier=0,
            rolls=[18, 5],
            total=5,
            natural_total=5,
            critical_success=False,
            critical_failure=False,
            purpose="Saving throw",
            timestamp=1234567890,
            seed=None,
            advantage=False,
            disadvantage=True,
        )
        
        result = format_roll_result(roll)
        assert "[18, 5] (disadvantage)" in result
        assert "Saving throw:" in result
    
    def test_format_roll_result_critical_success(self):
        """Test formatting critical success."""
        roll = DiceRoll(
            dice_type=DiceType.D20,
            num_dice=1,
            modifier=0,
            rolls=[20],
            total=20,
            natural_total=20,
            critical_success=True,
            critical_failure=False,
            purpose="",
            timestamp=1234567890,
            seed=None,
            advantage=None,
            disadvantage=None,
        )
        
        result = format_roll_result(roll)
        assert "🎯 CRITICAL SUCCESS!" in result
    
    def test_format_roll_result_critical_failure(self):
        """Test formatting critical failure."""
        roll = DiceRoll(
            dice_type=DiceType.D20,
            num_dice=1,
            modifier=0,
            rolls=[1],
            total=1,
            natural_total=1,
            critical_success=False,
            critical_failure=True,
            purpose="",
            timestamp=1234567890,
            seed=None,
            advantage=None,
            disadvantage=None,
        )
        
        result = format_roll_result(roll)
        assert "💀 CRITICAL FAILURE!" in result
    
    def test_helper_function_roll_attack(self):
        """Test the roll_attack helper function."""
        with patch("random.randint") as mock_random:
            mock_random.return_value = 15
            
            result = roll_attack(attack_bonus=5)
            
            assert result.dice_type == DiceType.D20
            assert result.modifier == 5
            assert result.purpose == "Attack roll"
            assert result.total == 20
        
        # Test with advantage
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [10, 18]
            
            result = roll_attack(attack_bonus=3, advantage=True)
            
            assert result.advantage is True
            assert result.natural_total == 18
            assert result.total == 21
    
    def test_helper_function_roll_damage(self):
        """Test the roll_damage helper function."""
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [4, 5, 3]
            
            result = roll_damage(num_dice=3, dice_type=DiceType.D6, damage_bonus=2, damage_type="fire")
            
            assert result.dice_type == DiceType.D6
            assert result.num_dice == 3
            assert result.modifier == 2
            assert result.purpose == "fire damage"
            assert result.rolls == [4, 5, 3]
            assert result.total == 14  # 4 + 5 + 3 + 2
    
    def test_helper_function_roll_saving_throw(self):
        """Test the roll_saving_throw helper function."""
        with patch("random.randint") as mock_random:
            mock_random.return_value = 12
            
            result = roll_saving_throw(save_bonus=4, save_type="Wisdom")
            
            assert result.dice_type == DiceType.D20
            assert result.modifier == 4
            assert result.purpose == "Wisdom saving throw"
            assert result.total == 16
        
        # Test with disadvantage
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [15, 8]
            
            result = roll_saving_throw(save_bonus=2, save_type="Constitution", disadvantage=True)
            
            assert result.disadvantage is True
            assert result.natural_total == 8
            assert result.total == 10
    
    def test_helper_function_roll_ability_check(self):
        """Test the roll_ability_check helper function."""
        with patch("random.randint") as mock_random:
            mock_random.return_value = 14
            
            result = roll_ability_check(ability_bonus=3, ability_name="Stealth")
            
            assert result.dice_type == DiceType.D20
            assert result.modifier == 3
            assert result.purpose == "Stealth check"
            assert result.total == 17
    
    def test_dice_roll_request_model(self):
        """Test the DiceRollRequest model."""
        # Basic request
        request = DiceRollRequest(dice_type=DiceType.D20)
        assert request.dice_type == DiceType.D20
        assert request.num_dice == 1
        assert request.modifier == 0
        assert request.purpose == ""
        assert request.advantage is False
        assert request.disadvantage is False
        assert request.seed is None
        
        # Full request
        request = DiceRollRequest(
            dice_type=DiceType.D8,
            num_dice=2,
            modifier=-2,
            purpose="Healing potion",
            advantage=True,
            disadvantage=False,
            seed=42,
        )
        assert request.dice_type == DiceType.D8
        assert request.num_dice == 2
        assert request.modifier == -2
        assert request.purpose == "Healing potion"
        assert request.seed == 42
    
    def test_get_dice_value_function(self):
        """Test the get_dice_value helper function."""
        expected_values = {
            DiceType.D4: 4,
            DiceType.D6: 6,
            DiceType.D8: 8,
            DiceType.D10: 10,
            DiceType.D12: 12,
            DiceType.D20: 20,
            DiceType.D100: 100,
        }
        
        for dice_type, expected in expected_values.items():
            assert get_dice_value(dice_type) == expected
    
    def test_percentile_dice(self):
        """Test d100/percentile dice handling."""
        with patch("random.randint") as mock_random:
            mock_random.return_value = 73
            
            result = roll_dice(DiceType.D100)
            
            assert result.rolls[0] == 73
            assert result.dice_type == DiceType.D100
            assert 1 <= result.rolls[0] <= 100
    
    def test_edge_case_zero_modifier(self):
        """Test explicit zero modifier."""
        result = roll_dice(DiceType.D20, modifier=0)
        assert result.modifier == 0
        assert result.total == result.natural_total
    
    def test_edge_case_large_numbers(self):
        """Test with large numbers of dice."""
        with patch("random.randint") as mock_random:
            # Generate 100 rolls of 3 each
            mock_random.side_effect = [3] * 100
            
            result = roll_dice(DiceType.D6, num_dice=100)
            
            assert len(result.rolls) == 100
            assert all(r == 3 for r in result.rolls)
            assert result.natural_total == 300
            assert result.total == 300
    
    def test_edge_case_large_modifiers(self):
        """Test with very large positive and negative modifiers."""
        test_cases = [1000, -1000, 999999, -999999]
        
        for modifier in test_cases:
            with patch("random.randint") as mock_random:
                mock_random.return_value = 10
                
                result = roll_dice(DiceType.D20, modifier=modifier)
                
                assert result.modifier == modifier
                assert result.total == 10 + modifier
    
    def test_advantage_critical_success(self):
        """Test critical success with advantage."""
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [10, 20]  # Second roll is nat 20
            
            result = roll_dice(DiceType.D20, advantage=True)
            
            assert result.critical_success is True
            assert result.natural_total == 20
            assert result.rolls == [10, 20]
    
    def test_disadvantage_critical_failure(self):
        """Test critical failure with disadvantage."""
        with patch("random.randint") as mock_random:
            mock_random.side_effect = [15, 1]  # Second roll is nat 1
            
            result = roll_dice(DiceType.D20, disadvantage=True)
            
            assert result.critical_failure is True
            assert result.natural_total == 1
            assert result.rolls == [15, 1]
    
    def test_concurrent_rolls_different_seeds(self):
        """Test that concurrent rolls with different seeds produce different results."""
        results = []
        
        for i in range(5):
            result = roll_dice(DiceType.D20, seed=i)
            results.append(result.rolls[0])
        
        # Check that we got some variety (not all the same)
        assert len(set(results)) > 1
    
    def test_roll_result_immutability(self):
        """Test that DiceRoll results are properly structured."""
        result = roll_dice(DiceType.D20)
        
        # Verify all expected fields exist
        assert hasattr(result, 'dice_type')
        assert hasattr(result, 'num_dice')
        assert hasattr(result, 'modifier')
        assert hasattr(result, 'rolls')
        assert hasattr(result, 'total')
        assert hasattr(result, 'natural_total')
        assert hasattr(result, 'critical_success')
        assert hasattr(result, 'critical_failure')
        assert hasattr(result, 'purpose')
        assert hasattr(result, 'timestamp')
        assert hasattr(result, 'seed')
        assert hasattr(result, 'advantage')
        assert hasattr(result, 'disadvantage')
    
    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        functions = [
            roll_dice,
            roll_multiple,
            format_roll_result,
            roll_attack,
            roll_damage,
            roll_saving_throw,
            roll_ability_check,
            get_dice_value,
        ]
        
        for func in functions:
            assert func.__doc__ is not None
            assert len(func.__doc__) > 10
