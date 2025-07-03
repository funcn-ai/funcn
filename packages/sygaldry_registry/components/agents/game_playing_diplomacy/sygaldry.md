# game_playing_diplomacy
> Multi-model turn-based Diplomacy game agent supporting AI vs AI, human vs AI, or mixed gameplay with sophisticated diplomatic negotiation and strategic planning

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Multi-model turn-based Diplomacy game agent supporting AI vs AI, human vs AI, or mixed gameplay with sophisticated diplomatic negotiation and strategic planning

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
sygaldry add game_playing_diplomacy
```

### Dependencies

This agent requires the following dependencies:

**Registry Dependencies:**

- None

**Python Dependencies:**

- `mirascope>=1.24.0`
- `pydantic>=2.0.0`
- `asyncio`

**Environment Variables:**

- `OPENAI_API_KEY`: OpenAI API key for GPT models (Optional)
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude models (Optional)
- `GOOGLE_API_KEY`: Google API key for Gemini models (Optional)

### Basic Usage

```python
from game_playing_diplomacy import (
    DiplomacyGame,
    DiplomacyPlayer,
    DiplomacyPower,
    DiplomacyState,
    DiplomacyPhase,
    PlayerType,
    diplomacy_game_agent,
    diplomacy_game_stream
)

# Create players with different models
players = [
    DiplomacyPlayer(
        power=DiplomacyPower.ENGLAND,
        player_type=PlayerType.AI,
        model="gpt-4o",
        provider="openai",
        personality="diplomatic",
        strategy_style="coalition-builder"
    ),
    DiplomacyPlayer(
        power=DiplomacyPower.FRANCE,
        player_type=PlayerType.AI,
        model="claude-3-opus-20240229",
        provider="anthropic",
        personality="aggressive",
        strategy_style="rapid-expansion"
    ),
    DiplomacyPlayer(
        power=DiplomacyPower.GERMANY,
        player_type=PlayerType.HUMAN,  # Human player
        personality="balanced"
    ),
    DiplomacyPlayer(
        power=DiplomacyPower.RUSSIA,
        player_type=PlayerType.AI,
        model="gemini-1.5-pro",
        provider="google",
        personality="defensive",
        strategy_style="fortress-builder"
    ),
    # Add more players...
]

# Initialize game state
game_state = DiplomacyState(
    year=1901,
    phase=DiplomacyPhase.SPRING_DIPLOMACY,
    provinces=[],  # Initialize with starting positions
    units=[],  # Initialize with starting units
    supply_centers={},  # Initialize supply centers
    recent_messages=[],
    eliminated_powers=[]
)

# Run a turn (works with all AI or mixed human/AI)
game = await diplomacy_game_agent(
    game_state=game_state,
    players=players,
    current_phase=DiplomacyPhase.SPRING_DIPLOMACY
)

# Or stream the game for real-time updates
async for update in diplomacy_game_stream(game_state, players):
    print(update)
```

## Agent Configuration

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with sygaldry tools for enhanced capabilities
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- Instrumented with Lilypad for observability and tracing
- Supports automatic versioning and A/B testing

### Template Variables

- None

### Advanced Configuration

Configure template variables using CLI options or environment variables.

### LLM Provider Configuration

This agent supports multiple LLM providers through Mirascope:

- **OpenAI**: Set `OPENAI_API_KEY` for GPT models
- **Anthropic**: Set `ANTHROPIC_API_KEY` for Claude models
- **Google**: Set `GOOGLE_API_KEY` for Gemini models
- **Groq**: Set `GROQ_API_KEY` for Groq models

Configure the provider and model using template variables or function parameters.

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

## Troubleshooting

To use this agent:

1. Set up API keys for the LLM providers you want to use
2. Create players with different models and personalities
3. Initialize the game state with starting positions
4. Call the agent to process turns
5. The agent handles both AI and human players automatically

For all-AI games, simply set all players to PlayerType.AI with their preferred models.
For human participation, set PlayerType.HUMAN for those players.

## Migration Notes

---

**Key Benefits:**

- **Game**
- **Multi-Agent**
- **Turn-Based**
- **Strategy**
- **Diplomacy**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Sygaldry Registry](https://github.com/greyhaven-ai/sygaldry)

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await game_playing_diplomacy(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await game_playing_diplomacy(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```

### Custom Configuration

```python
# Custom configuration example
from game_playing_diplomacy import game_playing_diplomacy_custom

result = await game_playing_diplomacy_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `sygaldry add game_playing_diplomacy` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries
