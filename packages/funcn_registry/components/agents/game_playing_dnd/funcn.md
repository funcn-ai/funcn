# dnd_game_master

> A comprehensive D&D 5e game master agent with full rules enforcement and persistent campaign state. Features SQLite-based state persistence for multi-session campaigns, fair dice rolling with modifiers, complete D&D 5e API integration, multi-model orchestration, turn-based combat with positioning, spell slot tracking, condition management, death saves, XP/leveling, exhaustion, skill proficiencies, inventory management, and dynamic roleplay with human-in-the-loop support.

**Version**: 1.1.0 | **Type**: agent | **License**: MIT
**Authors**: Funcn Project <info@funcn.ai> | **Repository**: https://github.com/funcn-ai/funcn

## Overview

A comprehensive D&D 5e game master agent with full rules enforcement and persistent campaign state. Features SQLite-based state persistence for multi-session campaigns, fair dice rolling with modifiers, complete D&D 5e API integration, multi-model orchestration, turn-based combat with positioning, spell slot tracking, condition management, death saves, XP/leveling, exhaustion, skill proficiencies, inventory management, and dynamic roleplay with human-in-the-loop support.

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add dnd_game_master
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- `dice_roller`
- `dnd_5e_api`
- `sqlite_db`

**Python Dependencies:**

- `mirascope>=1.24.0`
- `pydantic>=2.0.0`
- `httpx>=0.27.0`
- `asyncio`
- `aiosqlite>=0.19.0`

**Environment Variables:**

- `OPENAI_API_KEY`: OpenAI API key for DM and AI players (Optional)
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude-based players (Optional)
- `GOOGLE_API_KEY`: Google API key for Gemini-based players (Optional)

### Basic Usage

```python
from dnd_game_master import (
    dnd_game_master,
    dnd_game_master_stream,
    create_character,
    list_campaign_sessions,
    CharacterClass,
    PlayerType
)

import asyncio

# Check for existing sessions
sessions = await list_campaign_sessions("My Epic Campaign")

# Easy character creation with helper function
party = [
    # Human player
    create_character(
        name="Aragorn",
        race="Human",
        character_class="ranger",
        level=5,
        player_type=PlayerType.HUMAN,
        personality=["Noble ranger", "Protector of the weak"]
    ),
    
    # AI wizard using Claude
    create_character(
        name="Gandalf",
        race="Human",
        character_class=CharacterClass.WIZARD,
        level=5,
        player_type=PlayerType.AI,
        ai_model="claude-3-5-sonnet-20241022",
        ai_provider="anthropic",
        ai_personality="Wise wizard who speaks cryptically",
        stats={
            "strength": 10,
            "dexterity": 12,
            "constitution": 14,
            "intelligence": 18,
            "wisdom": 16,
            "charisma": 13
        }
    ),
    
    # AI rogue using GPT-4
    create_character(
        name="Shadowblade",
        race="Halfling",
        character_class="rogue",
        level=5,
        player_type=PlayerType.AI,
        ai_model="gpt-4o",
        ai_provider="openai",
        ai_personality="Witty rogue with a heart of gold"
    )
]

# Define encounter tables for different locations
encounter_tables = {
    "Forest Path": [
        [("Wolf 1", "wolf"), ("Wolf 2", "wolf"), ("Wolf 3", "wolf")],
        [("Bandit 1", "bandit"), ("Bandit 2", "bandit"), ("Bandit Captain", "bandit-captain")],
        [("Owlbear", "owlbear")]
    ],
    "Goblin Cave": [
        [("Goblin 1", "goblin"), ("Goblin 2", "goblin"), ("Goblin 3", "goblin")],
        [("Hobgoblin", "hobgoblin"), ("Goblin 1", "goblin"), ("Goblin 2", "goblin")],
        [("Bugbear", "bugbear")]
    ]
}

# Run a persistent campaign session
game_state = asyncio.run(
    dnd_game_master(
        campaign_name="The Lost Artifact",
        players=party,
        starting_location="Forest Path",
        campaign_tone="Epic fantasy with mystery",
        dm_style="Descriptive and challenging",
        dm_provider="openai",
        dm_model="gpt-4o",
        session_length=1800,  # 30 minutes
        enable_persistence=True,  # Enable SQLite state saving
        load_session_id=None,  # Or provide session ID to continue
        auto_save_interval=300,  # Auto-save every 5 minutes
        initial_scene="The party stands at the edge of the Whispering Woods...",
        quest_hooks=[
            "Find the Crystal of Eternal Light",
            "Investigate the disappearances",
            "Discover why wildlife is aggressive"
        ],
        encounter_tables=encounter_tables
    )
)

# Or use streaming for real-time updates
async for update in dnd_game_master_stream(
    campaign_name="Quick Adventure",
    players=party,
    create_sample_party=False,
    dm_model="gpt-4o-mini"
):
    print(update, end="", flush=True)
```

## Agent Configuration

### Template Variables

- None

### LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models
- **Groq**: Set `GROQ_API_KEY` for Groq models

Configure the provider and model using template variables or function parameters.

### Advanced Configuration

Configure template variables using CLI options or environment variables.

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with funcn tools for enhanced capabilities
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## Integration with Mirascope

This agent follows Mirascope best practices:

- Uses `@prompt_template` decorators for all prompts
- Implements Pydantic response models for structured outputs
- Supports async/await patterns for optimal performance
- Compatible with multiple LLM providers
- Includes comprehensive error handling
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

## API Reference

See component source code for detailed API documentation.

## Advanced Examples

Check the examples directory for advanced usage patterns.

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await dnd_game_master(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await dnd_game_master(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from dnd_game_master import dnd_game_master_custom

result = await dnd_game_master_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

## Troubleshooting

After adding this component:

1. **Set up API keys** for the AI providers you want to use (OpenAI, Anthropic, Google, etc.)

2. **Create characters** using the helper function or custom CharacterSheet objects

3. **Key features**:
   - **NEW: SQLite state persistence** for multi-session campaigns
   - **NEW: Auto-save functionality** with configurable intervals
   - **NEW: Session management** to continue previous games
   - **NEW: Combat logging** for detailed history
   - **NEW: Automatic backups** after each session
   - Fair dice rolling with all proper modifiers (ability, proficiency, expertise)
   - Complete D&D 5e rules via API (spells, monsters, races, conditions, skills, items)
   - Multi-model orchestration (different AI models for different characters)
   - Turn-based combat with grid positioning and movement validation
   - Spell slot tracking and component requirements
   - Condition management with duration and saving throws
   - Death saving throws at 0 HP
   - XP tracking and automatic level-ups with proper progression
   - Exhaustion and rest mechanics (short/long)
   - Skill proficiencies and expertise
   - Inventory management with attunement
   - Dynamic roleplay with natural conversation flow
   - Human-in-the-loop with interrupt capability (Ctrl+C)

4. **State persistence**:
   - Campaigns saved in `campaigns/` directory
   - List sessions: `await list_campaign_sessions("Campaign Name")`
   - Continue session: Set `load_session_id` parameter
   - Auto-saves during gameplay
   - Backups in `campaigns/backups/`

5. **Combat features**:
   - Initiative tracking and turn order
   - Action economy (action, bonus action, reaction, movement)
   - Position-based combat on grid
   - Attack rolls with advantage/disadvantage
   - Damage rolls with criticals
   - Condition application and tracking
   - Encounter difficulty calculations

6. **Customization options**:
   - Campaign name, tone, and DM style
   - Session length and enabled features
   - Initial scene and quest hooks
   - Encounter tables by location
   - Custom character personalities for AI players
   - Persistence settings (enable/disable, save interval)

7. **During gameplay**:
   - Human players get prompts with timeout
   - AI players act in character based on personality
   - DM enforces all D&D 5e rules consistently
   - All dice rolls show transparent results
   - Resources are tracked automatically
   - Progress auto-saved periodically

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add dnd_game_master` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

## Migration Notes

---

**Key Benefits:**

- **Game**
- **Dnd**
- **Dungeons-And-Dragons**
- **5E**
- **Roleplay**

**Related Components:**

- `dice_roller`
- `dnd_5e_api`
- `sqlite_db`

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)
