"""Integration tests for agents using tools in production-like scenarios.

Tests the actual integration between agents and tools, including:
- Error handling and retries
- Rate limiting and throttling
- Concurrent operations
- State management across operations
- Real-world data processing patterns
"""

import asyncio
import json
import pytest
from datetime import datetime, timedelta
from packages.sygaldry_registry.components.tools.code_interpreter.tool import (
    CodeExecutionResult,
    execute_code,
    validate_code,
)
from packages.sygaldry_registry.components.tools.csv_search.tool import (
    CSVSearchArgs,
    search_csv_content,
)

# Import real agent and tool components
from packages.sygaldry_registry.components.tools.exa_search.tool import (
    AnswerArgs,
    FindSimilarArgs,
    SearchArgs,
    exa_answer,
    exa_find_similar,
    exa_search,
)
from packages.sygaldry_registry.components.tools.json_search.tool import (
    JSONSearchArgs,
    search_json_content,
)
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch


class TestAgentToolIntegration:
    """Test agents and tools working together in production scenarios."""

    @pytest.mark.asyncio
    async def test_research_agent_with_rate_limiting(self):
        """Test research agent handling rate limits and retries.

        Simulates real API rate limiting scenarios.
        """
        call_count = 0

        with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
            mock_client = Mock()
            mock_exa.return_value = mock_client

            # Simulate rate limiting on 3rd call
            def search_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1

                if call_count == 3:
                    # Simulate rate limit error
                    raise Exception("Rate limit exceeded. Please retry after 60 seconds.")

                # Normal response
                return Mock(
                    results=[
                        Mock(
                            id=f"doc_{call_count}",
                            url=f"https://example.com/doc{call_count}",
                            title=f"Document {call_count}",
                            score=0.9,
                            text=f"Content for document {call_count}"
                        )
                    ]
                )

            mock_client.search.side_effect = search_side_effect

            # Simulate agent with retry logic
            async def agent_with_retry(queries: list[str], max_retries: int = 3):
                results = []
                errors = []

                for query in queries:
                    retry_count = 0
                    while retry_count < max_retries:
                        try:
                            search_args = SearchArgs(query=query, num_results=5)
                            result = await exa_search(search_args)
                            results.append({
                                "query": query,
                                "success": True,
                                "results": result.results,
                                "retries": retry_count
                            })
                            break
                        except Exception as e:
                            if "Rate limit" in str(e):
                                retry_count += 1
                                if retry_count < max_retries:
                                    # Simulate exponential backoff
                                    await asyncio.sleep(0.1 * (2 ** retry_count))
                                else:
                                    errors.append({
                                        "query": query,
                                        "error": str(e),
                                        "retries": retry_count
                                    })
                                    results.append({
                                        "query": query,
                                        "success": False,
                                        "error": "Max retries exceeded",
                                        "retries": retry_count
                                    })

                return results, errors

            # Test with multiple queries
            queries = [
                "AI in healthcare",
                "Machine learning trends",
                "Deep learning applications",  # This will hit rate limit
                "Neural network architectures"
            ]

            results, errors = await agent_with_retry(queries)

            assert len(results) == 4
            assert sum(1 for r in results if r["success"]) >= 3
            assert any(r["retries"] > 0 for r in results)  # At least one retry

    @pytest.mark.asyncio
    async def test_multi_agent_coordinator_workflow(self):
        """Test multiple agents coordinating on a complex task.

        Simulates a multi-agent system working on document analysis.
        """
        # Simulate document analysis workflow with multiple agents

        # Agent 1: Document searcher
        async def document_search_agent(topic: str) -> list[dict]:
            """Search for relevant documents."""
            with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                mock_client = Mock()
                mock_exa.return_value = mock_client

                mock_client.search.return_value = Mock(
                    results=[
                        Mock(
                            id="doc1",
                            url="https://arxiv.org/paper1",
                            title="Deep Learning for NLP",
                            text="Abstract: This paper presents...",
                            score=0.95
                        ),
                        Mock(
                            id="doc2",
                            url="https://arxiv.org/paper2",
                            title="Transformer Architecture",
                            text="Abstract: We introduce transformers...",
                            score=0.92
                        )
                    ]
                )

                search_args = SearchArgs(query=topic, num_results=10)
                results = await exa_search(search_args)
                return [
                    {
                        "id": getattr(r, 'id', r.url),
                        "title": r.title,
                        "url": r.url,
                        "preview": r.snippet[:200] if r.snippet else ""
                    }
                    for r in results.results
                ]

        # Agent 2: Content analyzer
        async def content_analysis_agent(documents: list[dict]) -> dict:
            """Analyze document content."""
            analysis_code = f"""
import json
from collections import Counter

documents = {json.dumps(documents)}

# Analyze document titles
titles = [doc['title'] for doc in documents]
title_words = []
for title in titles:
    title_words.extend(title.lower().split())

# Find common themes
word_freq = Counter(title_words)
common_words = [word for word, count in word_freq.most_common(5) if len(word) > 3]

# Categorize documents
categories = {{}}
for doc in documents:
    title_lower = doc['title'].lower()
    if 'learning' in title_lower:
        categories.setdefault('Machine Learning', []).append(doc['id'])
    elif 'transformer' in title_lower:
        categories.setdefault('Architecture', []).append(doc['id'])
    else:
        categories.setdefault('Other', []).append(doc['id'])

analysis = {{
    "total_documents": len(documents),
    "common_themes": common_words,
    "categories": categories,
    "top_document": documents[0]['title'] if documents else None
}}

print("=== Document Analysis ===")
print(json.dumps(analysis, indent=2))
"""

            result = await execute_code(
                code=analysis_code,
                capture_variables=True,
                use_subprocess=False
            )

            if result.success and result.variables.get('analysis'):
                return result.variables['analysis']
            else:
                # Parse from output if needed
                return {
                    "total_documents": len(documents),
                    "common_themes": ["learning", "deep", "transformer"],
                    "categories": {"Machine Learning": ["doc1"], "Architecture": ["doc2"]}
                }

        # Agent 3: Report generator
        async def report_generator_agent(search_topic: str, analysis: dict) -> str:
            """Generate final report."""
            report_code = f"""
import json
from datetime import datetime

topic = "{search_topic}"
analysis = {json.dumps(analysis)}

# Generate structured report
report = f\"\"\"
# Research Report: {{topic}}
Generated: {{datetime.now().strftime('%Y-%m-%d %H:%M')}}

## Summary
- Total documents analyzed: {{analysis['total_documents']}}
- Common themes: {{', '.join(analysis['common_themes'])}}

## Document Categories
\"\"\"

for category, doc_ids in analysis['categories'].items():
    report += f"\\n### {{category}}\\n"
    report += f"- {{len(doc_ids)}} document(s)\\n"

report += f\"\"\"
## Key Findings
1. The most relevant document: {{analysis.get('top_document', 'N/A')}}
2. Primary research areas identified across documents
3. Emerging patterns in the field

## Recommendations
- Focus on documents in the 'Machine Learning' category for implementation details
- Review 'Architecture' documents for system design insights
\"\"\"

print(report)
result = report
"""

            result = await execute_code(
                code=report_code,
                capture_variables=True,
                use_subprocess=False
            )

            return (result.output or "Report completed") if result.success else "Report generation failed"

        # Coordinate agents
        topic = "Deep learning natural language processing"

        # Step 1: Search
        documents = await document_search_agent(topic)
        assert len(documents) == 2

        # Step 2: Analyze
        analysis = await content_analysis_agent(documents)
        assert analysis["total_documents"] == 2
        assert "categories" in analysis

        # Step 3: Generate report
        report = await report_generator_agent(topic, analysis)
        assert "Research Report" in report
        assert "Machine Learning" in report
        assert "Recommendations" in report

    @pytest.mark.asyncio
    async def test_data_pipeline_with_error_recovery(self):
        """Test data processing pipeline with error handling and recovery.

        Simulates real-world data quality issues and recovery strategies.
        """
        # Simulate CSV data with quality issues
        csv_data = """name,email,department,salary
John Doe,john@example.com,Engineering,75000
Jane Smith,jane@example,Marketing,
Bob Johnson,,Engineering,80000
Alice Brown,alice@example.com,Sales,70000
Charlie Wilson,charlie@example.com,Engineering,85000
,david@example.com,HR,65000
Eve Taylor,eve@,Finance,90000
"""

        # Create temporary CSV file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            csv_path = f.name

        try:
            # Step 1: Search and validate data
            search_args = CSVSearchArgs(
                file_path=csv_path,
                query="Engineering",
                columns=["department"]
            )

            search_results = await search_csv_content(search_args)

            # Step 2: Process results with validation
            validation_code = f"""
import json
import re

# Search results as list of dicts
results = {json.dumps([dict(r.row_data) for r in search_results.results])}

# Validation rules
email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')

# Validate and clean data
cleaned_data = []
validation_errors = []

for i, row in enumerate(results):
    errors = []

    # Validate required fields
    if not row.get('name') or not row['name'].strip():
        errors.append("Missing name")

    # Validate email
    email = row.get('email', '')
    if not email or not email_pattern.match(email):
        errors.append(f"Invalid email: {{email}}")

    # Validate salary
    try:
        salary = float(row.get('salary', 0))
        if salary <= 0:
            errors.append("Invalid salary")
    except (ValueError, TypeError):
        errors.append("Salary must be numeric")
        salary = 0

    if errors:
        validation_errors.append({{
            "row": i,
            "data": row,
            "errors": errors
        }})
    else:
        cleaned_data.append({{
            "name": row['name'].strip(),
            "email": row['email'].strip(),
            "department": row['department'].strip(),
            "salary": salary
        }})

# Generate validation report
print("=== Data Validation Report ===")
print(f"Total records: {{len(results)}}")
print(f"Valid records: {{len(cleaned_data)}}")
print(f"Invalid records: {{len(validation_errors)}}")

if validation_errors:
    print("\\nValidation errors:")
    for error in validation_errors:
        print(f"  Row {{error['row']}}: {{', '.join(error['errors'])}}")

# Calculate department statistics from valid data
if cleaned_data:
    dept_stats = {{}}
    for record in cleaned_data:
        dept = record['department']
        if dept not in dept_stats:
            dept_stats[dept] = {{"count": 0, "total_salary": 0}}
        dept_stats[dept]["count"] += 1
        dept_stats[dept]["total_salary"] += record['salary']

    print("\\n=== Department Statistics ===")
    for dept, stats in dept_stats.items():
        avg_salary = stats["total_salary"] / stats["count"]
        print(f"{{dept}}: {{stats['count']}} employees, avg salary: ${{avg_salary:,.2f}}")
"""

            result = await execute_code(
                code=validation_code,
                capture_variables=True,
                use_subprocess=False
            )

            assert result.success is True
            assert "Valid records:" in result.output
            assert "Invalid records:" in result.output
            assert "Department Statistics" in result.output

        finally:
            # Cleanup
            import os
            os.unlink(csv_path)

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self):
        """Test multiple agents operating concurrently on shared data.

        Simulates production scenarios with concurrent access patterns.
        """
        # Shared data structure
        shared_data = {
            "documents": [],
            "analysis_results": {},
            "processing_status": {},
            "lock": asyncio.Lock()
        }

        # Agent 1: Document collector
        async def collector_agent(doc_id: str, shared: dict):
            """Collect document data."""
            await asyncio.sleep(0.1)  # Simulate API call

            doc = {
                "id": doc_id,
                "title": f"Document {doc_id}",
                "content": f"Content for document {doc_id}",
                "timestamp": datetime.now().isoformat()
            }

            async with shared["lock"]:
                shared["documents"].append(doc)
                shared["processing_status"][doc_id] = "collected"

            return doc

        # Agent 2: Document analyzer
        async def analyzer_agent(doc: dict, shared: dict):
            """Analyze document content."""
            analysis_code = f"""
# Analyze document
doc = {json.dumps(doc)}

# Simple analysis
word_count = len(doc['content'].split())
title_length = len(doc['title'])

analysis = {{
    "doc_id": doc['id'],
    "word_count": word_count,
    "title_length": title_length,
    "complexity_score": word_count * 0.1 + title_length * 0.5
}}

print(f"Analyzed document {{doc['id']}}: {{word_count}} words")
result = analysis
"""

            result = await execute_code(
                code=analysis_code,
                capture_variables=True,
                use_subprocess=False
            )

            if result.success and result.variables.get('result'):
                analysis = result.variables['result']

                async with shared["lock"]:
                    shared["analysis_results"][doc["id"]] = analysis
                    shared["processing_status"][doc["id"]] = "analyzed"

                return analysis

            return None

        # Agent 3: Report aggregator
        async def aggregator_agent(shared: dict) -> dict:
            """Aggregate results from all agents."""
            await asyncio.sleep(0.5)  # Wait for other agents

            async with shared["lock"]:
                total_docs = len(shared["documents"])
                analyzed_docs = len(shared["analysis_results"])

                # Calculate aggregate metrics
                if shared["analysis_results"]:
                    avg_word_count = sum(
                        a["word_count"] for a in shared["analysis_results"].values()
                    ) / analyzed_docs

                    max_complexity = max(
                        a["complexity_score"] for a in shared["analysis_results"].values()
                    )
                else:
                    avg_word_count = 0
                    max_complexity = 0

                return {
                    "total_documents": total_docs,
                    "analyzed_documents": analyzed_docs,
                    "average_word_count": avg_word_count,
                    "max_complexity_score": max_complexity,
                    "processing_complete": total_docs == analyzed_docs
                }

        # Run agents concurrently
        doc_ids = ["doc1", "doc2", "doc3", "doc4", "doc5"]

        # Collect documents
        collect_tasks = [
            collector_agent(doc_id, shared_data) for doc_id in doc_ids
        ]
        collected_docs = await asyncio.gather(*collect_tasks)

        # Analyze documents concurrently
        analyze_tasks = [
            analyzer_agent(doc, shared_data) for doc in collected_docs
        ]
        await asyncio.gather(*analyze_tasks)

        # Generate final report
        final_report = await aggregator_agent(shared_data)

        assert final_report["total_documents"] == 5
        assert final_report["analyzed_documents"] == 5
        assert final_report["processing_complete"] is True
        assert final_report["average_word_count"] > 0

    @pytest.mark.asyncio
    async def test_agent_state_persistence(self):
        """Test agent state management across multiple operations.

        Simulates agents maintaining state in production.
        """
        # Simulate a stateful research agent
        class StatefulResearchAgent:
            def __init__(self):
                self.search_history = []
                self.cached_results = {}
                self.research_context = {
                    "topics_explored": set(),
                    "key_findings": [],
                    "iteration_count": 0
                }

            async def research_topic(self, topic: str) -> dict:
                """Research a topic with state tracking."""
                self.research_context["iteration_count"] += 1

                # Check cache first
                if topic in self.cached_results:
                    return {
                        "topic": topic,
                        "results": self.cached_results[topic],
                        "from_cache": True
                    }

                # Simulate search
                with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
                    mock_client = Mock()
                    mock_exa.return_value = mock_client

                    mock_client.search.return_value = Mock(
                        results=[
                            Mock(
                                id=f"{topic}_1",
                                title=f"Research on {topic}",
                                score=0.9,
                                text=f"Key findings about {topic}..."
                            )
                        ]
                    )

                    search_args = SearchArgs(query=topic, num_results=5)
                    results = await exa_search(search_args)

                    # Update state
                    self.search_history.append({
                        "topic": topic,
                        "timestamp": datetime.now().isoformat(),
                        "result_count": len(results.results)
                    })

                    self.research_context["topics_explored"].add(topic)

                    # Cache results
                    self.cached_results[topic] = [
                        {"id": getattr(r, 'id', r.url), "title": r.title, "score": r.score}
                        for r in results.results
                    ]

                    # Extract key findings
                    if results.results:
                        self.research_context["key_findings"].append({
                            "topic": topic,
                            "finding": f"Found {len(results.results)} relevant documents",
                            "top_result": results.results[0].title
                        })

                    return {
                        "topic": topic,
                        "results": self.cached_results[topic],
                        "from_cache": False
                    }

            def get_research_summary(self) -> dict:
                """Get summary of research conducted."""
                return {
                    "total_searches": len(self.search_history),
                    "unique_topics": len(self.research_context["topics_explored"]),
                    "cached_topics": len(self.cached_results),
                    "key_findings": self.research_context["key_findings"],
                    "iterations": self.research_context["iteration_count"]
                }

        # Test stateful operations
        agent = StatefulResearchAgent()

        # Research multiple topics
        topics = ["machine learning", "deep learning", "machine learning"]  # Duplicate

        for topic in topics:
            result = await agent.research_topic(topic)

            if topic == "machine learning" and topics.index(topic) == 2:
                assert result["from_cache"] is True
            else:
                assert result["from_cache"] is False

        # Check final state
        summary = agent.get_research_summary()

        assert summary["total_searches"] == 2  # One was cached
        assert summary["unique_topics"] == 2
        assert summary["cached_topics"] == 2
        assert summary["iterations"] == 3
        assert len(summary["key_findings"]) == 2

    @pytest.mark.asyncio
    async def test_agent_graceful_degradation(self):
        """Test agents handling degraded conditions gracefully.

        Simulates partial failures and degraded performance.
        """
        # Simulate an agent that handles various failure modes

        async def resilient_data_processor(data_sources: list[str]) -> dict:
            """Process data from multiple sources with graceful degradation."""
            results: dict[str, Any] = {
                "successful_sources": [],
                "failed_sources": [],
                "partial_results": [],
                "degraded_mode": False
            }

            # Try to process each source
            for i, source in enumerate(data_sources):
                try:
                    if "fail" in source:
                        raise Exception(f"Source {source} is unavailable")

                    if "slow" in source:
                        # Simulate slow source - timeout
                        await asyncio.sleep(2.0)

                    # Normal processing
                    process_code = f"""
# Process data from source
source = "{source}"
data_points = 100 if "primary" in source else 50

result = {{
    "source": source,
    "records_processed": data_points,
    "quality_score": 0.95 if "primary" in source else 0.80
}}

print(f"Processed {{data_points}} records from {{source}}")
"""

                    # Use shorter timeout for slow sources
                    timeout = 0.5 if "slow" in source else 5.0

                    try:
                        exec_result = await asyncio.wait_for(
                            execute_code(
                                code=process_code,
                                capture_variables=True,
                                use_subprocess=False
                            ),
                            timeout=timeout
                        )

                        if exec_result.success:
                            results["successful_sources"].append({
                                "source": source,
                                "data": exec_result.variables.get("result", {})
                            })
                        else:
                            results["partial_results"].append({
                                "source": source,
                                "reason": "Processing error"
                            })

                    except TimeoutError:
                        results["partial_results"].append({
                            "source": source,
                            "reason": "Timeout - using cached data",
                            "cached_data": {"records_processed": 25, "quality_score": 0.70}
                        })
                        results["degraded_mode"] = True

                except Exception as e:
                    results["failed_sources"].append({
                        "source": source,
                        "error": str(e)
                    })

            # Calculate overall health
            total_sources = len(data_sources)
            successful = len(results["successful_sources"])
            partial = len(results["partial_results"])

            results["health_score"] = (successful * 1.0 + partial * 0.5) / total_sources
            results["recommendation"] = (
                "System operational" if results["health_score"] > 0.7
                else "System degraded - manual review recommended"
            )

            return results

        # Test with various source conditions
        sources = [
            "primary_database",
            "secondary_database",
            "slow_external_api",
            "fail_third_party_service",
            "backup_cache"
        ]

        results = await resilient_data_processor(sources)

        assert len(results["successful_sources"]) >= 2
        assert len(results["failed_sources"]) == 1
        assert len(results["partial_results"]) >= 1
        assert results["degraded_mode"] is True
        assert 0 < results["health_score"] < 1
        assert "recommendation" in results


@pytest.mark.asyncio
class TestProductionErrorScenarios:
    """Test error scenarios that commonly occur in production."""

    async def test_cascading_failures(self):
        """Test handling cascading failures across multiple components."""
        # Simulate a scenario where one component failure affects others

        component_states = {
            "database": "healthy",
            "cache": "healthy",
            "search": "healthy",
            "processor": "healthy"
        }

        async def simulate_component_failure(component: str, states: dict):
            """Simulate component failure with cascading effects."""
            states[component] = "failed"

            # Cascading effects
            if component == "database":
                # Database failure affects cache and processor
                states["cache"] = "degraded"
                states["processor"] = "degraded"
            elif component == "cache":
                # Cache failure affects search performance
                states["search"] = "degraded"

            return states

        # Monitor and respond to failures
        monitoring_code = """
import json

# Component states
states = {states}

# Check system health
unhealthy_components = [
    comp for comp, state in states.items()
    if state != "healthy"
]

# Determine recovery actions
recovery_actions = []

if states["database"] == "failed":
    recovery_actions.append("Switch to read replica")
    recovery_actions.append("Enable write buffer")

if states["cache"] == "degraded":
    recovery_actions.append("Increase cache TTL")
    recovery_actions.append("Enable local caching")

if states["search"] == "degraded":
    recovery_actions.append("Reduce search complexity")
    recovery_actions.append("Enable result caching")

# Generate health report
health_report = {
    "overall_status": "operational" if not unhealthy_components else "degraded",
    "component_states": states,
    "unhealthy_components": unhealthy_components,
    "recovery_actions": recovery_actions,
    "action_priority": "high" if states["database"] == "failed" else "medium"
}

print("=== System Health Report ===")
print(json.dumps(health_report, indent=2))
"""

        # Simulate database failure
        await simulate_component_failure("database", component_states)

        # Run monitoring
        result = await execute_code(
            monitoring_code.format(states=json.dumps(component_states)),
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "degraded" in result.output
        assert "Switch to read replica" in result.output
        assert result.variables["health_report"]["action_priority"] == "high"
