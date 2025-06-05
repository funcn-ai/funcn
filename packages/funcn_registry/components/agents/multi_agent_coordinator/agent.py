from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from mirascope import BaseDynamicConfig, llm, prompt_template
from pydantic import BaseModel, Field
from typing import Any, Optional


class AgentCapability(str, Enum):
    """Available agent capabilities in the system."""

    RESEARCH = "research"
    WEB_SEARCH = "web_search"
    DATA_ANALYSIS = "data_analysis"
    TEXT_SUMMARIZATION = "text_summarization"
    CODE_GENERATION = "code_generation"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    DOCUMENT_PROCESSING = "document_processing"
    MARKET_INTELLIGENCE = "market_intelligence"
    ACADEMIC_RESEARCH = "academic_research"
    SALES_INTELLIGENCE = "sales_intelligence"
    HALLUCINATION_DETECTION = "hallucination_detection"
    PII_SCRUBBING = "pii_scrubbing"


class TaskBreakdown(BaseModel):
    """Breakdown of a complex task into subtasks."""

    subtasks: list[str] = Field(..., description="List of subtasks to be executed")
    dependencies: dict[str, list[str]] = Field(
        default_factory=dict, description="Dependencies between subtasks (subtask -> list of prerequisite subtasks)"
    )
    estimated_complexity: int = Field(..., description="Complexity score from 1-10")
    reasoning: str = Field(..., description="Reasoning for the task breakdown")


class AgentSelection(BaseModel):
    """Selection of agents for specific subtasks."""

    subtask: str = Field(..., description="The subtask to be executed")
    primary_agent: AgentCapability = Field(..., description="Primary agent for this subtask")
    supporting_agents: list[AgentCapability] = Field(default_factory=list, description="Supporting agents that may be needed")
    confidence: float = Field(..., description="Confidence in agent selection (0-1)")
    reasoning: str = Field(..., description="Reasoning for agent selection")


class CoordinationPlan(BaseModel):
    """Complete coordination plan for multi-agent execution."""

    task_breakdown: TaskBreakdown
    agent_assignments: list[AgentSelection]
    execution_order: list[str] = Field(..., description="Order of subtask execution")
    parallel_groups: list[list[str]] = Field(
        default_factory=list, description="Groups of subtasks that can be executed in parallel"
    )
    estimated_duration: str = Field(..., description="Estimated time to complete")
    risk_assessment: str = Field(..., description="Potential risks and mitigation strategies")


class CoordinationResult(BaseModel):
    """Result of multi-agent coordination."""

    final_answer: str = Field(..., description="Synthesized final answer")
    subtask_results: dict[str, str] = Field(..., description="Results from each subtask")
    agents_used: list[str] = Field(..., description="List of agents that were utilized")
    execution_summary: str = Field(..., description="Summary of the execution process")
    quality_score: float = Field(..., description="Quality assessment of the result (0-1)")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations for future similar tasks")


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=TaskBreakdown,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert task decomposition specialist. Your role is to break down complex,
    multi-faceted problems into manageable subtasks that can be handled by specialized agents.

    Consider these principles:
    1. Each subtask should be focused and achievable by a single specialized agent
    2. Identify clear dependencies between subtasks
    3. Optimize for both parallel execution and logical flow
    4. Consider the complexity and time requirements of each subtask
    5. Ensure subtasks are atomic and well-defined

    USER:
    Break down this complex task into subtasks:

    Task: {task}
    Context: {context}
    Requirements: {requirements}

    Analyze the task and provide a detailed breakdown with dependencies and complexity assessment.
    """
)
def analyze_task_breakdown(task: str, context: str = "", requirements: str = "") -> TaskBreakdown:
    """Analyze and break down a complex task into manageable subtasks."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=list[AgentSelection],
)
@prompt_template(
    """
    SYSTEM:
    You are an expert agent selection specialist. Your role is to assign the most appropriate
    specialized agents to each subtask based on their capabilities and the task requirements.

    Available Agent Capabilities:
    - RESEARCH: General research and information gathering
    - WEB_SEARCH: Web searching and content extraction
    - DATA_ANALYSIS: Data processing and statistical analysis
    - TEXT_SUMMARIZATION: Text summarization and synthesis
    - CODE_GENERATION: Code generation and execution
    - KNOWLEDGE_GRAPH: Knowledge graph creation and analysis
    - DOCUMENT_PROCESSING: Document parsing and analysis
    - MARKET_INTELLIGENCE: Market research and competitive analysis
    - ACADEMIC_RESEARCH: Academic paper research and analysis
    - SALES_INTELLIGENCE: Sales data and lead analysis
    - HALLUCINATION_DETECTION: Verify and validate information accuracy
    - PII_SCRUBBING: Remove personally identifiable information

    Consider:
    1. Primary agent should be the best fit for the core task
    2. Supporting agents can provide complementary capabilities
    3. Confidence should reflect how well-suited the agent is
    4. Provide clear reasoning for each selection
    5. Consider agent workload and efficiency

    USER:
    Assign agents to these subtasks:

    Subtasks: {subtasks}
    Original Task Context: {context}

    For each subtask, select the most appropriate primary agent and any supporting agents needed.
    """
)
def select_agents_for_subtasks(subtasks: list[str], context: str = "") -> list[AgentSelection]:
    """Select appropriate agents for each subtask."""
    pass


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=CoordinationPlan,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert coordination planner. Your role is to create an optimal execution plan
    for multi-agent task completion, considering dependencies, parallelization opportunities,
    and risk mitigation.

    Consider:
    1. Respect task dependencies - prerequisite tasks must complete first
    2. Identify opportunities for parallel execution to reduce total time
    3. Estimate realistic durations based on task complexity
    4. Identify potential risks and mitigation strategies
    5. Optimize for both efficiency and quality
    6. Consider agent availability and workload balancing

    USER:
    Create a coordination plan for this multi-agent execution:

    Task Breakdown: {task_breakdown}
    Agent Assignments: {agent_assignments}
    Original Task: {original_task}

    Provide a comprehensive execution plan with timing, parallelization, and risk assessment.
    """
)
def create_coordination_plan(
    task_breakdown: TaskBreakdown, agent_assignments: list[AgentSelection], original_task: str
) -> BaseDynamicConfig:
    """Create a comprehensive coordination plan for multi-agent execution."""
    return {
        "computed_fields": {
            "task_breakdown": task_breakdown,
            "agent_assignments": agent_assignments,
        }
    }


@llm.call(
    provider="openai",
    model="gpt-4o",
    response_model=CoordinationResult,
)
@prompt_template(
    """
    SYSTEM:
    You are an expert result synthesizer. Your role is to combine results from multiple
    specialized agents into a coherent, comprehensive final answer.

    Consider:
    1. Synthesize information from all subtask results
    2. Resolve any conflicts or inconsistencies
    3. Ensure the final answer fully addresses the original task
    4. Assess the quality and completeness of the result
    5. Provide actionable recommendations for improvement
    6. Highlight key insights and findings

    USER:
    Synthesize the final result from this multi-agent execution:

    Original Task: {original_task}
    Coordination Plan: {coordination_plan}
    Subtask Results: {subtask_results}
    Execution Notes: {execution_notes}

    Provide a comprehensive final answer with quality assessment and recommendations.
    """
)
def synthesize_final_result(
    original_task: str, coordination_plan: CoordinationPlan, subtask_results: dict[str, str], execution_notes: str = ""
) -> BaseDynamicConfig:
    """Synthesize final result from all agent outputs."""
    return {
        "computed_fields": {
            "coordination_plan": coordination_plan,
            "subtask_results": subtask_results,
        }
    }


async def execute_subtask_with_agent(
    subtask: str, agent_capability: AgentCapability, context: str = "", timeout: int = 300
) -> str:
    """Execute a subtask using the specified agent capability with timeout."""
    try:
        # Add timeout to prevent hanging
        async with asyncio.timeout(timeout):
            # Import and use the appropriate agent based on capability
            if agent_capability == AgentCapability.WEB_SEARCH:
                from ..web_search import web_search_agent

                result = await web_search_agent(subtask)
                return result.answer if hasattr(result, 'answer') else str(result)

            elif agent_capability == AgentCapability.TEXT_SUMMARIZATION:
                from ..text_summarization import summarize_text

                result = await summarize_text(subtask, context)
                return result.summary if hasattr(result, 'summary') else str(result)

            elif agent_capability == AgentCapability.RESEARCH:
                from ..research_assistant import research_topic

                result = await research_topic(subtask, context)
                return result.answer if hasattr(result, 'answer') else str(result)

            elif agent_capability == AgentCapability.HALLUCINATION_DETECTION:
                from ..hallucination_detector import detect_hallucinations

                result = await detect_hallucinations(subtask, context)
                return result.analysis if hasattr(result, 'analysis') else str(result)

            elif agent_capability == AgentCapability.KNOWLEDGE_GRAPH:
                from ..knowledge_graph import extract_knowledge_graph

                result = await extract_knowledge_graph(subtask, context)
                return result.graph_summary if hasattr(result, 'graph_summary') else str(result)

            elif agent_capability == AgentCapability.CODE_GENERATION:
                from ..code_generation_execution import generate_and_execute_code

                result = await generate_and_execute_code(subtask, context)
                return result.code if hasattr(result, 'code') else str(result)

            # Add more agent integrations as needed
            else:
                # Fallback to LLM-based execution
                @llm.call(provider="openai", model="gpt-4o-mini")
                @prompt_template(
                    """
                    Execute this subtask using {agent_capability} capabilities:

                    Subtask: {subtask}
                    Context: {context}

                    Provide a detailed result for this specific subtask.
                    """
                )
                def execute_generic_subtask(subtask: str, agent_capability: str, context: str = "") -> str: ...

                result = await execute_generic_subtask(subtask, agent_capability.value, context)
                return result.content if hasattr(result, 'content') else str(result)

    except TimeoutError:
        return f"Error: Subtask execution timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing subtask: {str(e)}"


async def multi_agent_coordinator(
    task: str,
    context: str = "",
    requirements: str = "",
    max_parallel_tasks: int = 3,
    task_timeout: int = 300,
    llm_provider: str = "openai",
    model: str = "gpt-4o",
) -> CoordinationResult:
    """
    Coordinate multiple specialized agents to solve complex tasks.

    This agent breaks down complex tasks, assigns appropriate specialized agents,
    coordinates their execution, and synthesizes the final result.

    Args:
        task: The complex task to be solved
        context: Additional context about the task
        requirements: Specific requirements or constraints
        max_parallel_tasks: Maximum number of tasks to run in parallel
        task_timeout: Timeout for individual task execution in seconds
        llm_provider: LLM provider to use
        model: Model to use for coordination

    Returns:
        CoordinationResult with synthesized answer and execution details
    """

    # Step 1: Analyze and break down the task
    print(f"Analyzing task: {task}")
    task_breakdown = await analyze_task_breakdown(task, context, requirements)
    print(f"Identified {len(task_breakdown.subtasks)} subtasks")

    # Step 2: Select appropriate agents for each subtask
    print("Selecting specialized agents...")
    agent_assignments = await select_agents_for_subtasks(task_breakdown.subtasks, context)

    # Step 3: Create coordination plan
    print("Creating coordination plan...")
    coordination_plan = await create_coordination_plan(task_breakdown, agent_assignments, task)

    # Step 4: Execute subtasks according to the plan
    print("⚡ Executing subtasks...")
    subtask_results = {}
    execution_notes = []
    agents_used = set()

    # Track completed tasks for dependency management
    completed_tasks = set()

    # Execute tasks respecting dependencies and parallelization
    for parallel_group in coordination_plan.parallel_groups:
        # Filter out tasks whose dependencies aren't met
        ready_tasks = []
        for subtask in parallel_group:
            deps = task_breakdown.dependencies.get(subtask, [])
            if all(dep in completed_tasks for dep in deps):
                ready_tasks.append(subtask)
            else:
                execution_notes.append(f"Deferred {subtask} due to unmet dependencies")

        # Execute ready tasks in parallel (respecting max_parallel_tasks)
        for i in range(0, len(ready_tasks), max_parallel_tasks):
            batch = ready_tasks[i : i + max_parallel_tasks]
            tasks = []

            for subtask in batch:
                # Find the agent assignment for this subtask
                assignment = next((a for a in agent_assignments if a.subtask == subtask), None)
                if assignment:
                    agents_used.add(assignment.primary_agent.value)
                    tasks.append(execute_subtask_with_agent(subtask, assignment.primary_agent, context, task_timeout))

            # Wait for batch to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for j, result in enumerate(results):
                    subtask = batch[j]
                    if isinstance(result, Exception):
                        execution_notes.append(f"Error in {subtask}: {str(result)}")
                        subtask_results[subtask] = f"Error: {str(result)}"
                    else:
                        # result is guaranteed to be str here since execute_subtask_with_agent returns str
                        subtask_results[subtask] = str(result)
                        completed_tasks.add(subtask)

    # Execute any remaining tasks that weren't in parallel groups
    for subtask in task_breakdown.subtasks:
        if subtask not in completed_tasks:
            assignment = next((a for a in agent_assignments if a.subtask == subtask), None)
            if assignment:
                try:
                    agents_used.add(assignment.primary_agent.value)
                    result = await execute_subtask_with_agent(subtask, assignment.primary_agent, context, task_timeout)
                    subtask_results[subtask] = result
                except Exception as e:
                    execution_notes.append(f"Error in {subtask}: {e}")
                    subtask_results[subtask] = f"Error: {str(e)}"

    # Step 5: Synthesize final result
    print("Synthesizing final result...")
    final_result = await synthesize_final_result(task, coordination_plan, subtask_results, "\n".join(execution_notes))

    # Update agents_used in the result
    final_result.agents_used = list(agents_used)

    print("Multi-agent coordination complete!")
    return final_result


async def multi_agent_coordinator_stream(
    task: str, context: str = "", requirements: str = "", **kwargs
) -> AsyncGenerator[str, None]:
    """Stream the multi-agent coordination process with real-time updates."""

    yield f"Starting multi-agent coordination for: {task}\n\n"

    # Step 1: Task breakdown
    yield "Analyzing and breaking down the task...\n"
    task_breakdown = await analyze_task_breakdown(task, context, requirements)
    yield f"Identified {len(task_breakdown.subtasks)} subtasks:\n"
    for i, subtask in enumerate(task_breakdown.subtasks, 1):
        yield f"  {i}. {subtask}\n"
    yield f"\nComplexity: {task_breakdown.estimated_complexity}/10\n\n"

    # Step 2: Agent selection
    yield "Selecting specialized agents...\n"
    agent_assignments = await select_agents_for_subtasks(task_breakdown.subtasks, context)
    for assignment in agent_assignments:
        yield f"  • {assignment.subtask} → {assignment.primary_agent.value} (confidence: {assignment.confidence:.2f})\n"
    yield "\n"

    # Step 3: Coordination plan
    yield "Creating coordination plan...\n"
    coordination_plan = await create_coordination_plan(task_breakdown, agent_assignments, task)
    yield f"Execution order: {' → '.join(coordination_plan.execution_order[:3])}...\n"
    yield f"Estimated duration: {coordination_plan.estimated_duration}\n"
    yield f"Risk assessment: {coordination_plan.risk_assessment}\n\n"

    # Step 4: Execute and stream results
    yield "⚡ Executing subtasks...\n"
    result = await multi_agent_coordinator(task, context, requirements, **kwargs)

    yield "\nCoordination complete!\n\n"
    yield f"**Final Result:**\n{result.final_answer}\n\n"
    yield f"**Quality Score:** {result.quality_score:.2f}/1.0\n"
    yield f"**Agents Used:** {', '.join(result.agents_used)}\n\n"

    if result.recommendations:
        yield "**Recommendations:**\n"
        for rec in result.recommendations:
            yield f"  • {rec}\n"
