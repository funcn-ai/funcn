# dice_roller
> A fair and transparent dice rolling tool for tabletop RPGs. Supports all standard dice types (d4-d100), modifiers, advantage/disadvantage, and provides detailed roll results with timestamps.

**Version**: 0.1.0 | **Type**: tool | **License**: MIT

## Overview

A fair and transparent dice rolling tool for tabletop RPGs. Supports all standard dice types (d4-d100), modifiers, advantage/disadvantage, and provides detailed roll results with timestamps.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add dice_roller
```

### Dependencies

**Python Dependencies:**

- `pydantic>=2.0.0`

**Environment Variables:**

- None required

### Basic Usage

```python
from dice_roller import roll_dice, DiceType, format_roll_result

# Simple d20 roll
result = roll_dice(DiceType.D20)
print(format_roll_result(result))
# Output: d20 = 15

# Attack roll with modifier
attack = roll_dice(DiceType.D20, modifier=5, purpose="Attack roll")
print(format_roll_result(attack))
# Output: Attack roll: d20+5 = 18 + 5 = 23

# Roll with advantage
adv_roll = roll_dice(DiceType.D20, modifier=3, purpose="Stealth check", advantage=True)
print(format_roll_result(adv_roll))
# Output: Stealth check: d20+3 = [12, 18] (advantage) = 18 + 3 = 21

# Damage roll
damage = roll_dice(DiceType.D6, num_dice=3, modifier=2, purpose="Fireball damage")
print(format_roll_result(damage))
# Output: Fireball damage: 3d6+2 = [4, 2, 6] = 12 + 2 = 14

# Critical hit detection
crit_check = roll_dice(DiceType.D20)
if crit_check.critical_success:
    print("🎯 CRITICAL HIT!")
elif crit_check.critical_failure:
    print("💀 CRITICAL MISS!")
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from dice_roller import ToolArgs, ToolResult

# Input model defines the expected parameters
args = ToolArgs(
    param1="value1",
    param2="value2"
)

# Output model provides structured results
result: ToolResult = await tool_function(args)
```

## Integration with Agents

## Integration with Mirascope

This tool follows Mirascope best practices:

- Uses Pydantic models for structured inputs and outputs
- Supports async/await patterns for optimal performance
- Compatible with all Mirascope LLM providers
- Includes comprehensive error handling
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## API Reference

See component source code for detailed API documentation.

## Advanced Examples

Check the examples directory for advanced usage patterns.

## Troubleshooting

The dice roller provides:

- Fair random number generation
- Support for all standard RPG dice (d4, d6, d8, d10, d12, d20, d100)
- Advantage and disadvantage mechanics
- Critical success/failure detection on d20 rolls
- Transparent roll history with individual die results
- Timestamps for each roll
- Optional deterministic rolling with seeds for testing

## Migration Notes

---

**Key Benefits:**

- **Dice**
- **Rpg**
- **Tabletop**
- **Random**
- **Gaming**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

### Tool Chaining

```python
# Chain multiple tools together
from funcn_registry.tools import tool1, tool2

async def chained_workflow(input_data):
    result1 = await tool1(input_data)
    result2 = await tool2(result1.output)
    return result2
```

### Error Handling

```python
from dice_roller import tool_function, ToolError

try:
    result = await tool_function(args)
    print(f"Success: {result}")
except ToolError as e:
    print(f"Tool error: {e}")
    # Handle gracefully
```

### Batch Processing

```python
import asyncio
from dice_roller import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from dice_roller import tool_function

@llm.call(provider="openai", model="gpt-4o-mini", tools=[tool_function])
@prompt_template("Use the tool to help answer: {query}")
def agent_with_tool(query: str): ...

response = agent_with_tool("your question")
if response.tool:
    result = response.tool.call()
    print(result)
```

### Function Signature

The main tool function follows this pattern:

```python
async def tool_function(args: ToolArgs) -> ToolResult:
    """
    Tool description and usage.

    Args:
        args: Structured input parameters

    Returns:
        Structured result with typed fields

    Raises:
        ToolError: When operation fails
    """
```

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations
