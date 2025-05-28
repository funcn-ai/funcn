# dnd_5e_api

> A comprehensive tool for accessing official D&D 5th Edition content via the D&D 5e API. Provides detailed information about spells, classes, monsters, equipment, races, feats, skills, conditions, magic items, and more. Includes advanced search with filters and support for all SRD content types.

**Version**: 0.2.0 | **Type**: tool | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

A comprehensive tool for accessing official D&D 5th Edition content via the D&D 5e API. Provides detailed information about spells, classes, monsters, equipment, races, feats, skills, conditions, magic items, and more. Includes advanced search with filters and support for all SRD content types.

This tool is designed to work seamlessly with Mirascope agents and follows functional programming best practices.

## Quick Start

### Installation

```bash
funcn add dnd_5e_api
```

### Dependencies

**Python Dependencies:**
- `httpx>=0.27.0`
- `pydantic>=2.0.0`

**Environment Variables:**
- None required

### Basic Usage

```python
import asyncio
from dnd_5e_api import (
    get_spell_info,
    get_class_info,
    get_monster_info,
    get_equipment_info,
    get_race_info,
    get_feat_info,
    get_skill_info,
    get_condition_info,
    get_magic_item_info,
    search_dnd_content
)

async def main():
    # Look up a spell with full details
    fireball = await get_spell_info("Fireball")
    print(f"{fireball.name} - Level {fireball.level} {fireball.school.name}")
    print(f"Damage: 8d6 fire damage in a 20-foot radius")
    print(f"Classes: {', '.join([c.name for c in fireball.classes])}")
    
    # Look up a monster with complete stat block
    dragon = await get_monster_info("Adult Red Dragon")
    print(f"\n{dragon.name}")
    print(f"CR: {dragon.challenge_rating}, AC: {dragon.armor_class[0]['value']}, HP: {dragon.hit_points}")
    print(f"STR: {dragon.strength}, DEX: {dragon.dexterity}, CON: {dragon.constitution}")
    
    # Look up race information
    dwarf = await get_race_info("Dwarf")
    print(f"\n{dwarf.name}")
    print(f"Speed: {dwarf.speed} ft")
    print(f"Ability Bonuses: {', '.join([f'{ab.ability_score.name} +{ab.bonus}' for ab in dwarf.ability_bonuses])}")
    
    # Look up a condition
    poisoned = await get_condition_info("Poisoned")
    print(f"\n{poisoned.name}")
    for effect in poisoned.desc:
        print(f"• {effect}")
    
    # Look up a skill
    stealth = await get_skill_info("Stealth")
    print(f"\n{stealth.name} ({stealth.ability_score.name})")
    
    # Look up a magic item
    vorpal = await get_magic_item_info("Vorpal Sword")
    print(f"\n{vorpal.name} - {vorpal.rarity['name']}")
    
    # Advanced search with filters
    level_3_spells = await search_dnd_content("spells", level=3)
    print(f"\nFound {level_3_spells.count} level 3 spells")
    
    cr_5_monsters = await search_dnd_content("monsters", challenge_rating=5)
    print(f"Found {cr_5_monsters.count} CR 5 monsters")

asyncio.run(main())
```

## Tool Configuration

- None

### Input/Output Models

This tool uses structured Pydantic models for inputs and outputs:

```python
from dnd_5e_api import ToolArgs, ToolResult

# Input model defines the expected parameters
args = ToolArgs(
    param1="value1",
    param2="value2"
)

# Output model provides structured results
result: ToolResult = await tool_function(args)
```

## Integration with Agents

### Using with Mirascope Agents

```python
from mirascope.core import llm, prompt_template
from dnd_5e_api import tool_function

@llm.call(provider="openai", model="gpt-4o-mini", tools=[tool_function])
@prompt_template("Use the tool to help answer: {query}")
def agent_with_tool(query: str): ...

response = agent_with_tool("your question")
if response.tool:
    result = response.tool.call()
    print(result)
```

### Tool Chaining

```python
# Chain multiple tools together
from funcn_registry.tools import tool1, tool2

async def chained_workflow(input_data):
    result1 = await tool1(input_data)
    result2 = await tool2(result1.output)
    return result2
```

## API Reference

See component source code for detailed API documentation.

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

## Advanced Examples

Check the examples directory for advanced usage patterns.

### Error Handling

```python
from dnd_5e_api import tool_function, ToolError

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
from dnd_5e_api import tool_function

# Process multiple inputs concurrently
async def batch_process(inputs):
    tasks = [tool_function(inp) for inp in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## Integration with Mirascope

This tool follows Mirascope best practices:

- Uses Pydantic models for structured inputs and outputs
- Supports async/await patterns for optimal performance
- Compatible with all Mirascope LLM providers
- Includes comprehensive error handling
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## Troubleshooting

This enhanced tool provides access to:

**Core Content:**
- **Spells**: Complete spell information with schools, components, damage, DC, area of effect
- **Classes**: Full class details with proficiencies, equipment, multiclassing, spellcasting
- **Monsters**: Complete stat blocks with abilities, actions, resistances, legendary actions
- **Equipment**: Weapons, armor, and gear with properties, damage, AC, special features
- **Races**: Racial abilities, bonuses, traits, languages, and subraces

**Additional Content:**
- **Feats**: Prerequisites and descriptions
- **Skills**: Ability associations and descriptions
- **Conditions**: Full condition effects (poisoned, stunned, etc.)
- **Magic Items**: Rarity, variants, and magical properties
- **Ability Scores**: Detailed ability score information
- **Alignments**: Alignment descriptions and abbreviations
- **Languages**: Language details
- **Proficiencies**: Proficiency information
- **Damage Types**: Damage type descriptions
- **Weapon Properties**: Property explanations

**Advanced Features:**
- Filtered searches for spells (by level, school, name)
- Filtered searches for monsters (by CR, type, size)
- Support for all valid D&D 5e API content types
- Proper error handling with descriptive messages
- Type-safe models for all content

The tool uses the official D&D 5e API (https://www.dnd5eapi.co/) which provides SRD content.
No API key is required. All functions are async and should be awaited.

### Common Issues

- **Input Validation Errors**: Ensure input parameters match the ToolArgs model
- **API Limits**: Implement rate limiting and retry logic for external APIs
- **Timeout Issues**: Adjust timeout settings for slow operations

## Migration Notes



---

**Key Benefits:**

- **Dnd**
- **5E**
- **Dungeons-And-Dragons**
- **Rpg**
- **Tabletop**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
