# game_playing_catan
> Multi-model turn-based Settlers of Catan game agent supporting AI vs AI, human vs AI, or mixed gameplay with resource management, trading, and strategic building

**Version**: 0.1.0 | **Type**: agent | **License**: MIT

## Overview

Multi-model turn-based Settlers of Catan game agent supporting AI vs AI, human vs AI, or mixed gameplay with resource management, trading, and strategic building

This agent integrates seamlessly with the Mirascope framework and follows AI agent best practices for production deployment.

## Quick Start

### Installation

```bash
funcn add game_playing_catan
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
- `MISTRAL_API_KEY`: Mistral API key for Mistral models (Optional)

### Basic Usage

```python
from game_playing_catan import (
    CatanGame,
    CatanPlayer,
    CatanState,
    CatanPhase,
    PlayerType,
    Resource,
    catan_game_agent,
    catan_game_stream
)
from collections import defaultdict

# Create players with different models and strategies
players = [
    CatanPlayer(
        player_id=0,
        name="Builder Bot (GPT-4)",
        player_type=PlayerType.AI,
        model="gpt-4o",
        provider="openai",
        personality="builder",  # Focuses on settlements/cities
        resources=defaultdict(int),
        victory_points=0
    ),
    CatanPlayer(
        player_id=1,
        name="Trader Bot (Claude)",
        player_type=PlayerType.AI,
        model="claude-3-opus-20240229",
        provider="anthropic",
        personality="trader",  # Masters the art of trading
        resources=defaultdict(int),
        victory_points=0
    ),
    CatanPlayer(
        player_id=2,
        name="Human Player",
        player_type=PlayerType.HUMAN,  # Human player
        resources=defaultdict(int),
        victory_points=0
    ),
    CatanPlayer(
        player_id=3,
        name="Blocker Bot (Mistral)",
        player_type=PlayerType.AI,
        model="mistral-large-latest",
        provider="mistral",
        personality="blocker",  # Denies resources to opponents
        resources=defaultdict(int),
        victory_points=0
    )
]

# Initialize game state
game_state = CatanState(
    board=[],  # Initialize with hex tiles
    intersections=[],  # Initialize valid building spots
    edges=[],  # Initialize valid road locations
    current_player=0,
    phase=CatanPhase.SETUP_FIRST_SETTLEMENT,
    robber_position=(0, 0),  # Desert hex
    turn_number=0
)

# Run a turn (works with all AI or mixed human/AI)
game = await catan_game_agent(
    game_state=game_state,
    players=players
)

# Or run all-AI game
ai_players = [
    CatanPlayer(
        player_id=i,
        name=f"AI Player {i+1}",
        player_type=PlayerType.AI,
        model=["gpt-4o", "claude-3-opus-20240229", "gemini-1.5-pro", "mistral-large-latest"][i],
        provider=["openai", "anthropic", "google", "mistral"][i],
        personality=["builder", "trader", "expansionist", "balanced"][i],
        resources=defaultdict(int),
        victory_points=0
    )
    for i in range(4)
]

# Stream updates for real-time visualization
async for update in catan_game_stream(game_state, ai_players):
    print(update)
```

## Agent Configuration

## Agent Architecture

This agent implements the following key patterns:

- **Structured Outputs**: Uses Pydantic models for reliable, typed responses
- **Tool Integration**: Seamlessly integrates with funcn tools for enhanced capabilities
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
2. Create 2-4 players with different models and strategies
3. Initialize the game board with hexes, numbers, and starting positions
4. Call the agent to process each turn
5. The agent handles dice rolls, resource collection, trading, and building

For all-AI games:

- Set all players to PlayerType.AI with different models
- Each AI will use its own strategy and model for decisions
- Watch different AI strategies compete!

For human participation:

- Set PlayerType.HUMAN for human players
- The agent will prompt for input during human turns

## Migration Notes

---

**Key Benefits:**

- **Game**
- **Multi-Agent**
- **Turn-Based**
- **Strategy**
- **Resource-Management**

**Related Components:**

- None

**References:**

- [Mirascope Documentation](https://mirascope.com)
- [Funcn Registry](https://github.com/funcn-ai/funcn)

### Common Issues

- **API Key Issues**: Ensure your LLM provider API key is set correctly
- **Dependency Conflicts**: Run `funcn add game_playing_catan` to reinstall dependencies
- **Timeout Errors**: Increase timeout values for complex queries

### Custom Configuration

```python
# Custom configuration example
from game_playing_catan import game_playing_catan_custom

result = await game_playing_catan_custom(
    query="your question",
    custom_param="value",
    max_retries=3,
    timeout=30.0
)
```

### Multi-Provider Usage

```python
# Using different LLM providers
result_openai = await game_playing_catan(
    query="your question",
    provider="openai",
    model="gpt-4o-mini"
)

result_anthropic = await game_playing_catan(
    query="your question",
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)
```
