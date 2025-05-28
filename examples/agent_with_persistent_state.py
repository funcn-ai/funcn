"""Example: Agent with Persistent State using SQLite and SQLAlchemy tools."""

import asyncio
from datetime import datetime
from mirascope import llm
from packages.funcn_registry.components.tools.sqlalchemy_db import (
    SQLAlchemyConfig,
    create_tables,
    get_agent_state as sa_get_state,
    query_agent_history as sa_query_history,
    store_agent_state as sa_store_state,
)
from packages.funcn_registry.components.tools.sqlite_db import (
    create_agent_state_table,
    get_agent_state,
    query_agent_history,
    store_agent_state,
)
from typing import Any


# Example 1: Simple SQLite-based Memory Agent
class MemoryAgent:
    """An agent that remembers information using SQLite."""

    def __init__(self, agent_id: str, db_path: str = "agent_memory.db"):
        self.agent_id = agent_id
        self.db_path = db_path
        self.initialized = False

    async def initialize(self):
        """Initialize the database."""
        if not self.initialized:
            result = await create_agent_state_table(self.db_path)
            if result.success:
                print(f"Database initialized for agent {self.agent_id}")
                self.initialized = True
            else:
                print(f"Failed to initialize database: {result.error}")

    async def remember(self, key: str, value: Any, conversation_id: str = None):
        """Store information in memory."""
        result = await store_agent_state(
            db_path=self.db_path,
            agent_id=self.agent_id,
            key=key,
            value=value,
            conversation_id=conversation_id,
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )
        return result.success

    async def recall(self, key: str, conversation_id: str = None):
        """Retrieve information from memory."""
        result = await get_agent_state(
            db_path=self.db_path,
            agent_id=self.agent_id,
            key=key,
            conversation_id=conversation_id
        )
        if result.success and result.results:
            return result.results[0]['value']
        return None

    async def get_history(self, conversation_id: str = None):
        """Get conversation history."""
        result = await query_agent_history(
            db_path=self.db_path,
            agent_id=self.agent_id,
            conversation_id=conversation_id,
            limit=10
        )
        return result.results if result.success else []


# Example 2: Advanced SQLAlchemy-based Conversation Agent
class ConversationAgent:
    """An agent that maintains conversation state using SQLAlchemy."""

    def __init__(self, agent_id: str, database_url: str = "sqlite:///conversation_state.db"):
        self.agent_id = agent_id
        self.config = SQLAlchemyConfig(
            database_url=database_url,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            use_async=True
        )
        self.initialized = False

    async def initialize(self):
        """Initialize the database schema."""
        if not self.initialized:
            result = await create_tables(self.config)
            if result.success:
                print(f"SQLAlchemy database initialized for agent {self.agent_id}")
                self.initialized = True
            else:
                print(f"Failed to initialize database: {result.error}")

    async def update_context(self, conversation_id: str, context: dict):
        """Update conversation context."""
        result = await sa_store_state(
            config=self.config,
            agent_id=self.agent_id,
            key="conversation_context",
            value=context,
            conversation_id=conversation_id,
            metadata={"last_updated": datetime.utcnow().isoformat()}
        )
        return result.success

    async def get_context(self, conversation_id: str):
        """Get current conversation context."""
        result = await sa_get_state(
            config=self.config,
            agent_id=self.agent_id,
            key="conversation_context",
            conversation_id=conversation_id
        )
        if result.success and result.results:
            return result.results[0]['value']
        return None

    async def get_conversation_history(self, conversation_id: str, days_back: int = 7):
        """Get conversation history for the past N days."""
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days_back)

        result = await sa_query_history(
            config=self.config,
            agent_id=self.agent_id,
            conversation_id=conversation_id,
            start_date=start_date,
            limit=100
        )
        return result.results if result.success else []


# Example 3: Mirascope Agent with Built-in Memory
@llm.call(provider="openai", model="gpt-4o-mini", tools=[store_agent_state, get_agent_state])
async def intelligent_assistant(
    user_input: str,
    user_id: str,
    conversation_id: str,
    db_path: str = "assistant_memory.db"
):
    """An intelligent assistant that can remember information across conversations."""

    # The agent can use the tools directly to store and retrieve information
    return f"""
    I'm an intelligent assistant with persistent memory.

    User {user_id} said: {user_input}

    I can use my tools to:
    - Remember important information from our conversation
    - Recall previously stored information
    - Maintain context across multiple conversations

    How can I help you today?
    """


# Example usage
async def main():
    # Example 1: Simple Memory Agent
    print("=== Simple Memory Agent Example ===")
    agent1 = MemoryAgent("simple_agent_001")
    await agent1.initialize()

    # Store some information
    await agent1.remember("user_name", "Alice", "conv_001")
    await agent1.remember("favorite_color", "blue", "conv_001")
    await agent1.remember("topic", "machine learning", "conv_001")

    # Recall information
    name = await agent1.recall("user_name", "conv_001")
    print(f"Remembered user name: {name}")

    # Get history
    history = await agent1.get_history("conv_001")
    print(f"Conversation history: {len(history)} items")

    # Example 2: Conversation Agent
    print("\n=== Conversation Agent Example ===")
    agent2 = ConversationAgent("conversation_agent_001")
    await agent2.initialize()

    # Update conversation context
    context = {
        "topic": "weather",
        "location": "New York",
        "user_preferences": {
            "units": "fahrenheit",
            "detail_level": "summary"
        }
    }
    await agent2.update_context("conv_002", context)

    # Retrieve context
    retrieved_context = await agent2.get_context("conv_002")
    print(f"Retrieved context: {retrieved_context}")

    # Get conversation history
    history = await agent2.get_conversation_history("conv_002", days_back=1)
    print(f"Recent conversation history: {len(history)} items")

    # Example 3: Mirascope Agent
    print("\n=== Mirascope Agent Example ===")
    # Initialize database for the agent
    await create_agent_state_table("assistant_memory.db")

    # Call the intelligent assistant
    response = await intelligent_assistant(
        user_input="Please remember that my favorite programming language is Python",
        user_id="user_123",
        conversation_id="conv_003"
    )
    print(f"Assistant response: {response.content}")


if __name__ == "__main__":
    asyncio.run(main())
