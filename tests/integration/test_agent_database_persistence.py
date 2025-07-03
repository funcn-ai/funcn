"""Integration tests for agent database persistence patterns.

Tests database persistence patterns for stateful agent operations
using SQLite and SQLAlchemy tools. Shows how agents can maintain
state across sessions, coordinate through databases, and recover
from failures.
"""

import asyncio
import json
import pytest
import tempfile

# Import a multi-agent coordinator for state coordination tests
from packages.sygaldry_registry.components.agents.multi_agent_coordinator.agent import (
    AgentCapability,
    CoordinationResult,
    multi_agent_coordinator,
)

# Import SQLAlchemy tool for advanced ORM testing
from packages.sygaldry_registry.components.tools.sqlalchemy_db.tool import (
    AgentState,
    SQLAlchemyConfig,
    SQLAlchemyQueryResult,
    cleanup_old_state,
    create_tables,
    delete_agent_state,
    get_agent_state,
    get_database_info as get_sqlalchemy_db_info,
    query_agent_history,
    store_agent_state,
)

# Import database tools
from packages.sygaldry_registry.components.tools.sqlite_db.tool import (
    SQLiteQueryResult,
    create_agent_state_table,
    execute_sqlite_query,
    get_database_info,
)
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch


class TestAgentDatabasePersistence:
    """Test database persistence patterns for agent state management."""

    @pytest.mark.asyncio
    async def test_multi_agent_state_persistence(self):
        """Test multiple agents sharing state through a database.

        Simulates agents collaborating on a research task with shared
        state persistence for coordination.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/agent_state.db"

            # Initialize the database with a state table
            init_result = await execute_sqlite_query(
                db_path=db_path,
                query="""
                CREATE TABLE IF NOT EXISTS agent_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
                """,
                commit=True
            )
            assert init_result.success

            # Agent 1: Research agent saves search results
            research_state = {
                "task": "AI research",
                "queries_completed": ["machine learning trends", "neural networks 2024"],
                "sources_found": 15,
                "top_findings": ["Transformers dominate", "Multimodal is key"]
            }

            save_result = await execute_sqlite_query(
                db_path=db_path,
                query="""
                INSERT INTO agent_states (agent_id, task_id, state_data)
                VALUES (?, ?, ?)
                """,
                parameters=("research_agent", "task_001", json.dumps(research_state)),
                commit=True
            )
            assert save_result.success
            assert save_result.rows_affected == 1

            # Agent 2: Summary agent reads research state
            read_result = await execute_sqlite_query(
                db_path=db_path,
                query="""
                SELECT state_data FROM agent_states
                WHERE agent_id = ? AND task_id = ?
                """,
                parameters=("research_agent", "task_001"),
                fetch_results=True
            )
            assert read_result.success
            assert len(read_result.results) == 1

            loaded_state = json.loads(read_result.results[0]["state_data"])
            assert loaded_state["sources_found"] == 15
            assert "Transformers dominate" in loaded_state["top_findings"]

            # Agent 2 adds summary to shared state
            summary_state = {
                "based_on": "research_agent findings",
                "summary": "AI field is rapidly evolving with transformers and multimodal approaches",
                "key_points": 3
            }

            save_summary = await execute_sqlite_query(
                db_path=db_path,
                query="""
                INSERT INTO agent_states (agent_id, task_id, state_data)
                VALUES (?, ?, ?)
                """,
                parameters=("summary_agent", "task_001", json.dumps(summary_state)),
                commit=True
            )
            assert save_summary.success

            # Verify both agents' states are persisted
            all_states = await execute_sqlite_query(
                db_path=db_path,
                query="SELECT agent_id, task_id FROM agent_states WHERE task_id = ?",
                parameters=("task_001",),
                fetch_results=True
            )
            assert len(all_states.results) == 2
            agent_ids = [r["agent_id"] for r in all_states.results]
            assert "research_agent" in agent_ids
            assert "summary_agent" in agent_ids

    @pytest.mark.asyncio
    async def test_agent_conversation_history_tracking(self):
        """Test tracking conversation history across multiple sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/conversations.db"

            # Create conversation history table
            await execute_sqlite_query(
                db_path=db_path,
                query="""
                CREATE TABLE conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    turn_number INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """,
                commit=True
            )

            # Session 1: Initial conversation
            session_id = "session_001"
            conversations = [
                ("user", "What are the latest AI trends?"),
                ("assistant", "The latest AI trends include multimodal models, efficient transformers, and AI agents."),
                ("user", "Tell me more about AI agents"),
                ("assistant", "AI agents are autonomous systems that can use tools and complete complex tasks.")
            ]

            for turn, (role, content) in enumerate(conversations):
                await execute_sqlite_query(
                    db_path=db_path,
                    query="""
                    INSERT INTO conversation_history
                    (session_id, turn_number, role, content)
                    VALUES (?, ?, ?, ?)
                    """,
                    parameters=(session_id, turn, role, content),
                    commit=True
                )

            # Session 2: Resume conversation with context
            history_result = await execute_sqlite_query(
                db_path=db_path,
                query="""
                SELECT role, content FROM conversation_history
                WHERE session_id = ?
                ORDER BY turn_number DESC
                LIMIT 4
                """,
                parameters=(session_id,),
                fetch_results=True
            )

            assert len(history_result.results) == 4
            # Verify we can reconstruct the conversation
            last_exchange = history_result.results[0]
            assert last_exchange["role"] == "assistant"
            assert "autonomous systems" in last_exchange["content"]

            # Add follow-up in new session
            await execute_sqlite_query(
                db_path=db_path,
                query="""
                INSERT INTO conversation_history
                (session_id, turn_number, role, content, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                parameters=(
                    session_id,
                    4,
                    "user",
                    "Can you give me examples of AI agents?",
                    json.dumps({"resumed": True, "context_loaded": True})
                ),
                commit=True
            )

            # Verify conversation continuity
            full_history = await execute_sqlite_query(
                db_path=db_path,
                query="SELECT COUNT(*) as count FROM conversation_history WHERE session_id = ?",
                parameters=(session_id,),
                fetch_results=True
            )
            assert full_history.results[0]["count"] == 5

    @pytest.mark.asyncio
    async def test_agent_learning_and_improvement_tracking(self):
        """Test tracking agent performance and learning over time."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/agent_learning.db"

            # Create learning tracking tables
            await execute_sqlite_query(
                db_path=db_path,
                query="""
                CREATE TABLE agent_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_type TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    success_rate REAL,
                    avg_duration_seconds REAL,
                    error_count INTEGER DEFAULT 0,
                    feedback_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """,
                commit=True
            )

            await execute_sqlite_query(
                db_path=db_path,
                query="""
                CREATE TABLE learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """,
                commit=True
            )

            # Track performance over multiple tasks
            performance_data = [
                ("research_agent", "web_search", 0.85, 12.5, 1, 4.2),
                ("research_agent", "web_search", 0.90, 10.3, 0, 4.5),
                ("research_agent", "web_search", 0.95, 8.7, 0, 4.8),
                ("summary_agent", "summarization", 0.92, 5.2, 0, 4.6),
            ]

            for data in performance_data:
                await execute_sqlite_query(
                    db_path=db_path,
                    query="""
                    INSERT INTO agent_performance
                    (agent_type, task_type, success_rate, avg_duration_seconds, error_count, feedback_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    parameters=data,
                    commit=True
                )

            # Analyze improvement over time
            improvement_query = await execute_sqlite_query(
                db_path=db_path,
                query="""
                SELECT
                    agent_type,
                    task_type,
                    AVG(success_rate) as avg_success,
                    AVG(avg_duration_seconds) as avg_duration,
                    SUM(error_count) as total_errors,
                    AVG(feedback_score) as avg_feedback
                FROM agent_performance
                GROUP BY agent_type, task_type
                """,
                fetch_results=True
            )

            assert len(improvement_query.results) == 2
            research_stats = next(r for r in improvement_query.results if r["agent_type"] == "research_agent")
            assert research_stats["avg_success"] == 0.9  # (0.85 + 0.90 + 0.95) / 3
            assert research_stats["avg_duration"] < 11  # Shows improvement

            # Store learned patterns
            patterns = [
                ("query_optimization", json.dumps({"pattern": "use site: operator for specific domains", "effectiveness": 0.85})),
                ("error_recovery", json.dumps({"pattern": "retry with broader terms on no results", "effectiveness": 0.92})),
            ]

            for pattern_type, pattern_data in patterns:
                await execute_sqlite_query(
                    db_path=db_path,
                    query="""
                    INSERT INTO learned_patterns (pattern_type, pattern_data)
                    VALUES (?, ?)
                    """,
                    parameters=(pattern_type, pattern_data),
                    commit=True
                )

            # Verify patterns are stored
            patterns_result = await execute_sqlite_query(
                db_path=db_path,
                query="SELECT COUNT(*) as count FROM learned_patterns",
                fetch_results=True
            )
            assert patterns_result.results[0]["count"] == 2

    @pytest.mark.asyncio
    async def test_distributed_agent_coordination_with_postgres(self):
        """Test distributed agent coordination using PostgreSQL-like patterns.

        Note: This uses SQLite but demonstrates patterns that would work
        with PostgreSQL in production.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/coordination.db"

            # Create task queue table (similar to pg_search_tool patterns)
            await execute_sqlite_query(
                db_path=db_path,
                query="""
                CREATE TABLE task_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    task_type TEXT NOT NULL,
                    task_data TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    claimed_by TEXT,
                    claimed_at DATETIME,
                    completed_at DATETIME,
                    result TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """,
                commit=True
            )

            # Create index for efficient task claiming
            await execute_sqlite_query(
                db_path=db_path,
                query="CREATE INDEX idx_task_status ON task_queue(status)",
                commit=True
            )

            # Simulate multiple agents competing for tasks
            tasks = [
                ("task_001", "research", {"query": "quantum computing"}),
                ("task_002", "analysis", {"data": "market trends"}),
                ("task_003", "research", {"query": "renewable energy"}),
            ]

            for task_id, task_type, task_data in tasks:
                await execute_sqlite_query(
                    db_path=db_path,
                    query="""
                    INSERT INTO task_queue (task_id, task_type, task_data)
                    VALUES (?, ?, ?)
                    """,
                    parameters=(task_id, task_type, json.dumps(task_data)),
                    commit=True
                )

            # Agent 1 claims a task (atomic operation)
            claim_result = await execute_sqlite_query(
                db_path=db_path,
                query="""
                UPDATE task_queue
                SET status = 'processing',
                    claimed_by = ?,
                    claimed_at = CURRENT_TIMESTAMP
                WHERE task_id = (
                    SELECT task_id FROM task_queue
                    WHERE status = 'pending' AND task_type = ?
                    LIMIT 1
                )
                """,
                parameters=("agent_001", "research"),
                commit=True
            )
            assert claim_result.success
            assert claim_result.rows_affected == 1

            # Verify task was claimed
            claimed_task = await execute_sqlite_query(
                db_path=db_path,
                query="SELECT * FROM task_queue WHERE claimed_by = ?",
                parameters=("agent_001",),
                fetch_results=True
            )
            assert len(claimed_task.results) == 1
            assert claimed_task.results[0]["task_type"] == "research"

            # Agent completes task
            await execute_sqlite_query(
                db_path=db_path,
                query="""
                UPDATE task_queue
                SET status = 'completed',
                    completed_at = CURRENT_TIMESTAMP,
                    result = ?
                WHERE task_id = ? AND claimed_by = ?
                """,
                parameters=(
                    json.dumps({"findings": "Quantum computing breakthroughs in 2024"}),
                    claimed_task.results[0]["task_id"],
                    "agent_001"
                ),
                commit=True
            )

            # Check task distribution
            status_check = await execute_sqlite_query(
                db_path=db_path,
                query="""
                SELECT status, COUNT(*) as count
                FROM task_queue
                GROUP BY status
                """,
                fetch_results=True
            )

            status_dict = {r["status"]: r["count"] for r in status_check.results}
            assert status_dict["completed"] == 1
            assert status_dict["pending"] == 2

    @pytest.mark.asyncio
    async def test_sqlalchemy_agent_state_management(self):
        """Test using SQLAlchemy tool for complex agent state management."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{tmpdir}/agent_states.db"

            # Initialize SQLAlchemy config with minimal settings for SQLite
            config = SQLAlchemyConfig(
                database_url=db_url,
                echo=False,
                use_async=True
            )

            # Create tables
            create_result = await create_tables(config)
            assert create_result.success
            assert create_result.operation == "create_tables"

            # Store agent state
            state_data = {
                "current_task": "market analysis",
                "progress": 0.45,
                "findings": ["Tech sector growing", "Energy sector volatile"],
                "next_steps": ["Analyze consumer goods", "Review financials"]
            }

            store_result = await store_agent_state(
                config=config,
                agent_id="market_analyst_001",
                key="analysis_progress",
                value=state_data,
                conversation_id="conv_001",
                metadata={"sector_focus": "technology", "timeframe": "Q1 2024"}
            )

            assert store_result.success
            assert store_result.rows_affected == 1

            # Update state progress
            updated_state_data = {
                **state_data,
                "progress": 0.75,
                "findings": state_data["findings"] + ["Consumer goods stable"]
            }

            update_result = await store_agent_state(
                config=config,
                agent_id="market_analyst_001",
                key="analysis_progress",
                value=updated_state_data,
                conversation_id="conv_001",
                metadata={"sector_focus": "technology", "timeframe": "Q1 2024", "updated": True}
            )
            assert update_result.success

            # Get agent state
            get_result = await get_agent_state(
                config=config,
                agent_id="market_analyst_001",
                key="analysis_progress",
                conversation_id="conv_001"
            )
            assert get_result.success
            assert len(get_result.results) == 1
            assert get_result.results[0]["value"]["progress"] == 0.75
            assert len(get_result.results[0]["value"]["findings"]) == 3

            # Store multiple states for history testing
            await store_agent_state(
                config=config,
                agent_id="market_analyst_001",
                key="market_sentiment",
                value={"sentiment": "bullish", "confidence": 0.8},
                conversation_id="conv_001"
            )

            await store_agent_state(
                config=config,
                agent_id="market_analyst_001",
                key="risk_assessment",
                value={"risk_level": "moderate", "factors": ["inflation", "supply chain"]},
                conversation_id="conv_001"
            )

            # Query all states for agent
            all_states = await get_agent_state(
                config=config,
                agent_id="market_analyst_001",
                conversation_id="conv_001"
            )
            assert all_states.success
            assert len(all_states.results) == 3

            # Get database info
            db_info = await get_sqlalchemy_db_info(config)
            assert db_info.agent_state_count == 3
            assert "agent_state" in db_info.tables

            # Test deletion
            delete_result = await delete_agent_state(
                config=config,
                agent_id="market_analyst_001",
                key="risk_assessment",
                conversation_id="conv_001"
            )
            assert delete_result.success
            assert delete_result.rows_affected == 1

            # Verify deletion
            remaining_states = await get_agent_state(
                config=config,
                agent_id="market_analyst_001",
                conversation_id="conv_001"
            )
            assert len(remaining_states.results) == 2
