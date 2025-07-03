"""Production-like integration tests for tools and agents.

These tests simulate real-world usage scenarios where tools and agents
work together as they would in production, with actual API calls mocked
but the integration patterns preserved.
"""

import asyncio
import json
import pytest
from datetime import datetime
from packages.sygaldry_registry.components.tools.code_interpreter.tool import (
    CodeExecutionResult,
    execute_code,
)

# Import actual components
from packages.sygaldry_registry.components.tools.exa_search.tool import (
    SearchArgs,
    SearchResponse,
    exa_search,
)
from packages.sygaldry_registry.components.tools.git_repo_search.tool import (
    GitRepoSearchArgs,
    GitRepoSearchResponse,
    search_git_repo,
)
from packages.sygaldry_registry.components.tools.json_search.tool import (
    JSONSearchArgs,
    JSONSearchResponse,
    search_json_content,
)
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch


class TestProductionScenarios:
    """Test real-world production scenarios with tools and agents."""

    @pytest.mark.asyncio
    async def test_research_workflow_with_code_analysis(self):
        """Test a research workflow that finds code examples and analyzes them.

        Simulates: User wants to research a Python library, find examples,
        and analyze the code patterns.
        """
        # Step 1: Search for information about a Python library
        with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
            mock_client = Mock()
            mock_exa.return_value = mock_client

            # Mock search results
            mock_search_result = Mock()
            mock_search_result.results = [
                Mock(
                    id="1",
                    url="https://github.com/example/pandas-tutorial",
                    title="Pandas Tutorial with Examples",
                    score=0.95,
                    published_date="2024-01-15",
                    author="John Doe",
                    highlights=["pandas DataFrame operations", "data analysis examples"],
                    highlight_scores=[0.9, 0.85]
                ),
                Mock(
                    id="2",
                    url="https://pandas.pydata.org/docs/",
                    title="Official Pandas Documentation",
                    score=0.92,
                    published_date="2024-02-01",
                    author="Pandas Team",
                    highlights=["comprehensive guide", "API reference"],
                    highlight_scores=[0.88, 0.86]
                )
            ]
            mock_client.search.return_value = mock_search_result

            # Execute search
            search_args = SearchArgs(
                query="pandas DataFrame best practices examples",
                max_results=5
            )
            search_results = await exa_search(search_args)

            assert len(search_results.results) == 2
            assert "pandas" in search_results.results[0].title.lower()

        # Step 2: Get content from the most relevant result
        with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
            mock_client = Mock()
            mock_exa.return_value = mock_client

            # Mock content retrieval
            mock_content_result = Mock()
            mock_content_result.results = [
                Mock(
                    id="1",
                    url="https://github.com/example/pandas-tutorial",
                    title="Pandas Tutorial with Examples",
                    text="""
# Pandas DataFrame Best Practices

```python
import pandas as pd

# Best Practice 1: Use vectorized operations
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df['C'] = df['A'] + df['B']  # Vectorized

# Best Practice 2: Avoid iterrows() for large datasets
# Bad: for index, row in df.iterrows():
# Good: Use apply() or vectorized operations

# Best Practice 3: Set proper data types
df['date'] = pd.to_datetime(df['date_string'])
```
                    """,
                    highlights=None,
                    highlight_scores=None
                )
            ]
            mock_client.get_contents.return_value = mock_content_result

            # In production, you would get content from the search results
            # For this test, we'll use the mocked text content from the search
            assert len(search_results.results) == 2
            # The mock already includes the text content we need

        # Step 3: Extract and analyze the code
        code_snippet = """
import pandas as pd

# Best Practice 1: Use vectorized operations
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
df['C'] = df['A'] + df['B']  # Vectorized

# Analyze the DataFrame
print("DataFrame shape:", df.shape)
print("Column C sum:", df['C'].sum())
print("DataFrame info:")
print(df.info())
"""

        # Execute the extracted code
        execution_result = await execute_code(
            code=code_snippet,
            timeout_seconds=5,
            capture_variables=True,
            use_subprocess=False
        )

        assert execution_result.success is True
        assert "DataFrame shape: (3, 3)" in execution_result.output
        assert "Column C sum: 21" in execution_result.output
        assert execution_result.variables.get('df') is not None

    @pytest.mark.asyncio
    async def test_codebase_analysis_workflow(self):
        """Test analyzing a codebase to understand patterns and generate documentation.

        Simulates: Developer wants to understand a new codebase structure,
        find key patterns, and generate insights.
        """
        # Step 1: Search git repository for main application files
        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance

            # Mock file search results
            mock_repo_instance.git.ls_files.return_value = """
src/main.py
src/api/routes.py
src/api/handlers.py
src/models/user.py
src/models/product.py
src/utils/database.py
tests/test_api.py
tests/test_models.py
""".strip()

            # Search for Python files
            git_args = GitRepoSearchArgs(
                repo_path="/fake/repo",
                query="*.py",
                search_type="file"
            )
            git_results = await search_git_repo(git_args)

            assert git_results.success is True
            assert len(git_results.results) > 0
            assert git_results.file_matches is not None
            assert any("main.py" in r.file_path for r in git_results.file_matches)

        # Step 2: Search for specific patterns in the codebase
        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance

            # Mock grep results for API endpoints
            mock_repo_instance.git.grep.return_value = """
src/api/routes.py:15:@app.route('/api/users', methods=['GET'])
src/api/routes.py:20:@app.route('/api/users/<int:user_id>', methods=['GET'])
src/api/routes.py:25:@app.route('/api/products', methods=['GET', 'POST'])
src/api/handlers.py:10:async def handle_user_request(user_id: int):
src/api/handlers.py:35:async def handle_product_creation(data: dict):
""".strip()

            # Search for API patterns
            api_args = GitRepoSearchArgs(
                repo_path="/fake/repo",
                query="@app.route|async def handle",
                search_type="code",
                case_sensitive=False,
                regex=True
            )
            api_results = await search_git_repo(api_args)

            assert api_results.success is True
            assert len(api_results.results) > 0
            assert api_results.code_matches is not None
            assert any("routes.py" in r.file_path for r in api_results.code_matches)

        # Step 3: Analyze the discovered patterns
        analysis_code = """
# Analyze API structure from discovered patterns
api_endpoints = [
    ("GET", "/api/users"),
    ("GET", "/api/users/<int:user_id>"),
    ("GET", "/api/products"),
    ("POST", "/api/products"),
]

handlers = [
    "handle_user_request",
    "handle_product_creation",
]

# Generate summary
print("=== API Structure Analysis ===")
print(f"Total endpoints: {len(api_endpoints)}")
print(f"Total async handlers: {len(handlers)}")

# Group by HTTP method
from collections import Counter
methods = Counter(method for method, _ in api_endpoints)
print(f"\\nEndpoints by method:")
for method, count in methods.items():
    print(f"  {method}: {count}")

# Analyze resource patterns
resources = set()
for _, path in api_endpoints:
    if '/api/' in path:
        resource = path.split('/')[2].split('<')[0]
        resources.add(resource)

print(f"\\nResources identified: {', '.join(sorted(resources))}")
"""

        result = await execute_code(
            code=analysis_code,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "Total endpoints: 4" in result.output
        assert "GET: 3" in result.output
        assert "POST: 1" in result.output
        assert "users, products" in result.output.lower()

    @pytest.mark.asyncio
    async def test_data_pipeline_workflow(self):
        """Test a data processing pipeline with search, analysis, and transformation.

        Simulates: Processing JSON data files, searching for specific patterns,
        and transforming the results.
        """
        # Step 1: Search JSON configuration files
        sample_json_data = {
            "services": {
                "api": {
                    "host": "api.example.com",
                    "port": 8080,
                    "endpoints": {
                        "users": "/v1/users",
                        "products": "/v1/products",
                        "orders": "/v1/orders"
                    }
                },
                "database": {
                    "host": "db.example.com",
                    "port": 5432,
                    "credentials": {
                        "username": "app_user",
                        "database": "app_db"
                    }
                },
                "cache": {
                    "host": "cache.example.com",
                    "port": 6379,
                    "ttl": 3600
                }
            }
        }

        # Search for database configuration
        from packages.sygaldry_registry.components.tools.json_search.tool import JSONSearchArgs
        json_results = await search_json_content(
            JSONSearchArgs(
                json_data=sample_json_data,
                query="database",
                json_path="$.services.*",
                exact_match=False  # Use fuzzy matching
            )
        )

        assert json_results.error is None
        assert len(json_results.results) > 0
        assert any("database" in str(r.value) for r in json_results.results)

        # Step 2: Extract and process the configuration
        process_code = """
import json

# Configuration data
config = {
    "services": {
        "api": {
            "host": "api.example.com",
            "port": 8080,
            "endpoints": {
                "users": "/v1/users",
                "products": "/v1/products",
                "orders": "/v1/orders"
            }
        },
        "database": {
            "host": "db.example.com",
            "port": 5432,
            "credentials": {
                "username": "app_user",
                "database": "app_db"
            }
        },
        "cache": {
            "host": "cache.example.com",
            "port": 6379,
            "ttl": 3600
        }
    }
}

# Extract all service hosts
service_hosts = []
for service_name, service_config in config["services"].items():
    if "host" in service_config:
        service_hosts.append({
            "service": service_name,
            "host": service_config["host"],
            "port": service_config.get("port", "N/A")
        })

# Generate connection strings
print("=== Service Connection Summary ===")
for service in service_hosts:
    print(f"{service['service']}: {service['host']}:{service['port']}")

# Validate configuration
issues = []
for service_name, service_config in config["services"].items():
    if "host" not in service_config:
        issues.append(f"{service_name}: missing host")
    if "port" not in service_config:
        issues.append(f"{service_name}: missing port")

print(f"\\nConfiguration issues found: {len(issues)}")
if issues:
    for issue in issues:
        print(f"  - {issue}")

# Generate environment variables
print("\\n=== Environment Variables ===")
for service_name, service_config in config["services"].items():
    env_prefix = service_name.upper()
    if "host" in service_config:
        print(f"{env_prefix}_HOST={service_config['host']}")
    if "port" in service_config:
        print(f"{env_prefix}_PORT={service_config['port']}")
"""

        result = await execute_code(
            code=process_code,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "api: api.example.com:8080" in result.output
        assert "database: db.example.com:5432" in result.output
        assert "API_HOST=api.example.com" in result.output
        assert result.variables.get("service_hosts") is not None
        assert len(result.variables["service_hosts"]) == 3

    @pytest.mark.asyncio
    async def test_multi_tool_research_and_analysis(self):
        """Test complex workflow using multiple tools in sequence.

        Simulates: Research a topic, find code examples, analyze them,
        and generate a summary report.
        """
        # Step 1: Initial research
        with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
            mock_client = Mock()
            mock_exa.return_value = mock_client

            mock_search_result = Mock()
            mock_search_result.results = [
                Mock(
                    id="1",
                    url="https://example.com/async-python-guide",
                    title="Complete Guide to Async Python",
                    score=0.98,
                    published_date="2024-01-20",
                    highlights=["asyncio patterns", "concurrent programming"],
                    text="Async programming in Python using asyncio..."
                )
            ]
            mock_client.search.return_value = mock_search_result
            mock_client.get_contents.return_value = Mock(results=mock_search_result.results)

            # Research async patterns
            search_args = SearchArgs(
                query="Python asyncio best practices patterns",
                max_results=3
            )
            search_results = await exa_search(search_args)

            # In production, content would come from search results
            # For this test, we use the mocked data

        # Step 2: Generate and test example code based on research
        example_code = """
import asyncio
import time
from typing import List

async def fetch_data(item_id: int) -> dict:
    \"\"\"Simulate async data fetching.\"\"\"
    await asyncio.sleep(0.1)  # Simulate I/O
    return {"id": item_id, "data": f"Item {item_id}"}

async def process_batch(items: List[int]) -> List[dict]:
    \"\"\"Process multiple items concurrently.\"\"\"
    tasks = [fetch_data(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results

# Test the async pattern
start_time = time.time()

# Sequential approach (for comparison)
sequential_results = []
for i in range(5):
    # In real code, this would be: await fetch_data(i)
    sequential_results.append({"id": i, "data": f"Item {i}"})

# Concurrent approach
items = list(range(5))
concurrent_results = asyncio.run(process_batch(items))

elapsed = time.time() - start_time

print("=== Async Pattern Analysis ===")
print(f"Items processed: {len(items)}")
print(f"Time elapsed: {elapsed:.2f} seconds")
print(f"\\nResults: {concurrent_results}")

# Calculate theoretical speedup
sequential_time = len(items) * 0.1  # Each would take 0.1s
concurrent_time = 0.1  # All run in parallel
speedup = sequential_time / concurrent_time

print(f"\\nTheoretical speedup: {speedup}x")
print("Pattern: asyncio.gather() for concurrent execution")
"""

        execution_result = await execute_code(
            code=example_code,
            timeout_seconds=10,
            capture_variables=True,
            use_subprocess=False
        )

        assert execution_result.success is True
        assert "Items processed: 5" in execution_result.output
        assert "Theoretical speedup: 5" in execution_result.output

        # Step 3: Generate final analysis report
        report_code = f"""
# Generate research summary report
import json
from datetime import datetime

report = {{
    "title": "Async Python Patterns Research Summary",
    "date": datetime.now().isoformat(),
    "findings": [
        {{
            "source": "Complete Guide to Async Python",
            "key_patterns": [
                "asyncio.gather() for concurrent tasks",
                "async/await syntax for clarity",
                "Proper error handling with try/except in async"
            ]
        }}
    ],
    "code_analysis": {{
        "pattern_tested": "Concurrent batch processing",
        "theoretical_speedup": 5,
        "practical_considerations": [
            "I/O-bound tasks benefit most",
            "CPU-bound tasks need multiprocessing",
            "Memory usage scales with concurrent tasks"
        ]
    }},
    "recommendations": [
        "Use asyncio.gather() for known task sets",
        "Use asyncio.create_task() for dynamic task creation",
        "Implement proper exception handling",
        "Monitor memory usage in production"
    ]
}}

print("=== RESEARCH REPORT ===")
print(json.dumps(report, indent=2))

# Key metrics
total_sources = len(report["findings"])
total_patterns = sum(len(f["key_patterns"]) for f in report["findings"])
total_recommendations = len(report["recommendations"])

print(f"\\n=== SUMMARY METRICS ===")
print(f"Sources analyzed: {total_sources}")
print(f"Patterns identified: {total_patterns}")
print(f"Recommendations: {total_recommendations}")
"""

        report_result = await execute_code(
            code=report_code,
            capture_variables=True,
            use_subprocess=False
        )

        assert report_result.success is True
        assert "RESEARCH REPORT" in report_result.output
        assert "asyncio.gather()" in report_result.output
        assert "recommendations" in report_result.output.lower()
        assert report_result.variables.get("report") is not None

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery_workflow(self):
        """Test how tools handle errors and recovery in production scenarios.

        Simulates: Real-world error conditions and recovery strategies.
        """
        # Test 1: Handle malformed JSON gracefully
        malformed_json = '{"invalid": "json", "missing": closing_brace'

        with pytest.raises(json.JSONDecodeError):
            json.loads(malformed_json)

        # Test recovery with error handling
        recovery_code = """
import json

test_data = [
    '{"valid": "json", "number": 42}',
    '{"invalid": "json", missing: quotes}',
    '{"another": "valid", "bool": true}',
    'not even json',
    '{"final": "valid", "array": [1, 2, 3]}'
]

results = []
errors = []

for i, data in enumerate(test_data):
    try:
        parsed = json.loads(data)
        results.append({"index": i, "success": True, "data": parsed})
    except json.JSONDecodeError as e:
        errors.append({"index": i, "error": str(e), "data": data[:50]})
        results.append({"index": i, "success": False, "error": "JSONDecodeError"})

print(f"=== JSON Processing Results ===")
print(f"Total items: {len(test_data)}")
print(f"Successful: {sum(1 for r in results if r['success'])}")
print(f"Failed: {len(errors)}")

print(f"\\nSuccessful parses:")
for result in results:
    if result["success"]:
        print(f"  Index {result['index']}: {list(result['data'].keys())}")

print(f"\\nErrors encountered:")
for error in errors:
    print(f"  Index {error['index']}: {error['error'].split(':')[0]}")

# Implement retry logic
print(f"\\n=== Retry Strategy ===")
for error in errors:
    # Try to fix common issues
    fixed_data = error["data"]
    if "missing: quotes" in fixed_data:
        fixed_data = fixed_data.replace("missing: quotes", '"missing": "quotes"')

    try:
        parsed = json.loads(fixed_data)
        print(f"  Index {error['index']}: Fixed and parsed successfully!")
    except:
        print(f"  Index {error['index']}: Could not auto-fix")
"""

        result = await execute_code(
            code=recovery_code,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "Successful: 3" in result.output
        assert "Failed: 2" in result.output
        assert "Fixed and parsed successfully!" in result.output

        # Test 2: Handle timeout scenarios
        timeout_code = """
import asyncio
import time

async def slow_operation(duration: float):
    \"\"\"Simulate a slow operation.\"\"\"
    await asyncio.sleep(duration)
    return f"Completed after {duration}s"

async def with_timeout(coro, timeout: float):
    \"\"\"Run coroutine with timeout.\"\"\"
    try:
        result = await asyncio.wait_for(coro, timeout=timeout)
        return {"success": True, "result": result}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Operation timed out"}

# Test different scenarios
operations = [
    ("Fast operation", slow_operation(0.1), 1.0),
    ("Slow operation", slow_operation(2.0), 1.0),
    ("Normal operation", slow_operation(0.5), 1.0),
]

print("=== Timeout Handling Test ===")
for name, operation, timeout in operations:
    result = asyncio.run(with_timeout(operation, timeout))
    status = "✓ Success" if result["success"] else "✗ Timeout"
    print(f"{name}: {status}")
    if result["success"]:
        print(f"  Result: {result['result']}")
    else:
        print(f"  Error: {result['error']}")
"""

        timeout_result = await execute_code(
            code=timeout_code,
            timeout_seconds=5,
            use_subprocess=False
        )

        assert timeout_result.success is True
        assert "✓ Success" in timeout_result.output
        assert "✗ Timeout" in timeout_result.output
        assert "Operation timed out" in timeout_result.output

    @pytest.mark.asyncio
    async def test_performance_monitoring_workflow(self):
        """Test performance monitoring and optimization workflow.

        Simulates: Monitoring tool performance and identifying bottlenecks.
        """
        performance_code = """
import time
import asyncio
from typing import List, Dict
import statistics

class PerformanceMonitor:
    def __init__(self):
        self.metrics = []

    async def measure_operation(self, name: str, operation):
        \"\"\"Measure operation performance.\"\"\"
        start = time.time()
        try:
            result = await operation()
            duration = time.time() - start
            self.metrics.append({
                "name": name,
                "duration": duration,
                "success": True,
                "timestamp": time.time()
            })
            return result
        except Exception as e:
            duration = time.time() - start
            self.metrics.append({
                "name": name,
                "duration": duration,
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            })
            raise

    def get_summary(self) -> Dict:
        \"\"\"Get performance summary.\"\"\"
        if not self.metrics:
            return {"error": "No metrics collected"}

        durations = [m["duration"] for m in self.metrics if m["success"]]

        return {
            "total_operations": len(self.metrics),
            "successful": sum(1 for m in self.metrics if m["success"]),
            "failed": sum(1 for m in self.metrics if not m["success"]),
            "avg_duration": statistics.mean(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "total_time": sum(durations)
        }

# Simulate different operations
monitor = PerformanceMonitor()

async def fast_search():
    await asyncio.sleep(0.05)
    return {"results": 10}

async def slow_search():
    await asyncio.sleep(0.2)
    return {"results": 50}

async def process_data():
    await asyncio.sleep(0.1)
    return {"processed": 100}

# Run operations
async def run_performance_test():
    operations = [
        ("fast_search_1", fast_search()),
        ("fast_search_2", fast_search()),
        ("slow_search", slow_search()),
        ("process_data", process_data()),
        ("fast_search_3", fast_search()),
    ]

    for name, op in operations:
        await monitor.measure_operation(name, lambda: op)

    return monitor.get_summary()

# Execute test
summary = asyncio.run(run_performance_test())

print("=== Performance Summary ===")
for key, value in summary.items():
    if isinstance(value, float):
        print(f"{key}: {value:.3f}")
    else:
        print(f"{key}: {value}")

# Identify bottlenecks
print("\\n=== Performance Analysis ===")
if summary["avg_duration"] > 0.1:
    print("⚠️  Average operation time exceeds 100ms threshold")
else:
    print("✓ Average operation time is acceptable")

efficiency = summary["successful"] / summary["total_operations"] * 100
print(f"Success rate: {efficiency:.1f}%")

# Recommendations
print("\\n=== Optimization Recommendations ===")
if summary["max_duration"] > summary["avg_duration"] * 2:
    print("- Consider optimizing slow operations (high variance detected)")
if summary["total_time"] > summary["total_operations"] * 0.1:
    print("- Consider parallel execution for independent operations")
if efficiency < 100:
    print("- Investigate and fix failing operations")
"""

        perf_result = await execute_code(
            code=performance_code,
            timeout_seconds=10,
            capture_variables=True,
            use_subprocess=False
        )

        assert perf_result.success is True
        assert "Performance Summary" in perf_result.output
        assert "total_operations: 5" in perf_result.output
        assert "Success rate: 100.0%" in perf_result.output
        assert "Optimization Recommendations" in perf_result.output


@pytest.mark.asyncio
class TestAgentIntegrationScenarios:
    """Test production-like scenarios for agents working with tools."""

    async def test_research_agent_full_workflow(self):
        """Test a complete research agent workflow as it would run in production.

        This simulates the research_assistant_agent using real tools.
        """
        # Mock the Exa tool that the agent would use
        with patch("packages.sygaldry_registry.components.tools.exa_search.tool.Exa") as mock_exa:
            mock_client = Mock()
            mock_exa.return_value = mock_client

            # Simulate agent generating search queries
            search_queries = [
                "machine learning in healthcare latest developments 2024",
                "AI medical diagnosis accuracy studies",
                "healthcare ML implementation challenges"
            ]

            # Mock search results for each query
            mock_results = []
            for i, query in enumerate(search_queries):
                mock_result = Mock()
                mock_result.results = [
                    Mock(
                        id=f"doc_{i}_1",
                        url=f"https://medical-ai.com/article{i}",
                        title=f"AI in Healthcare: {query[:30]}...",
                        score=0.95 - i * 0.05,
                        text=f"Detailed content about {query}...",
                        highlights=[f"Key finding about {query}"],
                        author=f"Dr. Expert {i}"
                    )
                ]
                mock_results.append(mock_result)

            mock_client.search.side_effect = mock_results
            mock_client.get_contents.side_effect = [
                Mock(results=[r.results[0]]) for r in mock_results
            ]

            # Simulate the agent's research process
            all_results = []
            for query in search_queries:
                search_args = SearchArgs(query=query, max_results=5)
                result = await exa_search(search_args)
                all_results.extend(result.results)

            # Agent would analyze and synthesize results
            assert len(all_results) >= 3
            assert all(r.score > 0.8 for r in all_results)

    async def test_code_analysis_agent_workflow(self):
        """Test code analysis agent working with git search and code interpreter.

        Simulates the code_generation_execution_agent analyzing a codebase.
        """
        # Step 1: Agent searches for code patterns
        with patch("packages.sygaldry_registry.components.tools.git_repo_search.tool.git.Repo") as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance

            # Simulate finding Python files
            mock_repo_instance.git.ls_files.return_value = """
app/main.py
app/models.py
app/utils.py
tests/test_main.py
""".strip()

            # Agent searches for patterns
            mock_repo_instance.git.grep.return_value = """
app/models.py:class User(BaseModel):
app/models.py:    email: str
app/models.py:    created_at: datetime
app/utils.py:def validate_email(email: str) -> bool:
""".strip()

            # Execute search
            git_args = GitRepoSearchArgs(
                repo_path="/fake/repo",
                query="class.*BaseModel|def validate",
                search_type="code",
                regex=True
            )
            search_result = await search_git_repo(git_args)

            assert search_result.success is True
            assert search_result.code_matches is not None
            assert len(search_result.code_matches) > 0

        # Step 2: Agent generates analysis code
        analysis_code = """
# Analyze code structure
from typing import Dict, List

# Simulated code analysis results
classes_found = [
    {"name": "User", "base": "BaseModel", "file": "app/models.py"}
]

functions_found = [
    {"name": "validate_email", "params": ["email: str"], "returns": "bool"}
]

# Generate analysis report
print("=== Code Analysis Report ===")
print(f"Classes found: {len(classes_found)}")
for cls in classes_found:
    print(f"  - {cls['name']} (extends {cls['base']}) in {cls['file']}")

print(f"\\nValidation functions: {len(functions_found)}")
for func in functions_found:
    params = ', '.join(func['params'])
    print(f"  - {func['name']}({params}) -> {func['returns']}")

# Generate recommendations
recommendations = []
if any(f['name'].startswith('validate_') for f in functions_found):
    recommendations.append("Consider creating a Validator class for all validation functions")

if len(classes_found) > 5:
    recommendations.append("Consider organizing models into submodules")

print(f"\\n=== Recommendations ===")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec}")
"""

        # Agent executes analysis
        result = await execute_code(
            code=analysis_code,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "Code Analysis Report" in result.output
        assert "User (extends BaseModel)" in result.output
        assert "validate_email" in result.output

    async def test_data_processing_agent_workflow(self):
        """Test data processing agent with JSON search and code execution.

        Simulates an agent processing configuration data and generating reports.
        """
        # Configuration data the agent would process
        config_data = {
            "environments": {
                "production": {
                    "database": {
                        "host": "prod-db.example.com",
                        "port": 5432,
                        "pool_size": 20
                    },
                    "cache": {
                        "host": "prod-cache.example.com",
                        "ttl": 3600
                    },
                    "features": {
                        "auth_enabled": True,
                        "rate_limiting": True,
                        "debug_mode": False
                    }
                },
                "staging": {
                    "database": {
                        "host": "stage-db.example.com",
                        "port": 5432,
                        "pool_size": 10
                    },
                    "cache": {
                        "host": "stage-cache.example.com",
                        "ttl": 1800
                    },
                    "features": {
                        "auth_enabled": True,
                        "rate_limiting": True,
                        "debug_mode": True
                    }
                }
            }
        }

        # Agent searches for differences between environments
        prod_results = await search_json_content(
            JSONSearchArgs(
                json_data=config_data,
                query="production",
                json_path="$.environments.production..*"
            )
        )

        stage_results = await search_json_content(
            JSONSearchArgs(
                json_data=config_data,
                query="staging",
                json_path="$.environments.staging..*"
            )
        )

        # Agent generates comparison code
        comparison_code = """
# Compare environment configurations
prod_config = {
    "database": {"host": "prod-db.example.com", "pool_size": 20},
    "cache": {"ttl": 3600},
    "features": {"debug_mode": False}
}

stage_config = {
    "database": {"host": "stage-db.example.com", "pool_size": 10},
    "cache": {"ttl": 1800},
    "features": {"debug_mode": True}
}

# Find differences
differences = []

# Compare database settings
if prod_config["database"]["pool_size"] != stage_config["database"]["pool_size"]:
    differences.append({
        "setting": "database.pool_size",
        "production": prod_config["database"]["pool_size"],
        "staging": stage_config["database"]["pool_size"],
        "impact": "Performance difference expected"
    })

# Compare cache settings
if prod_config["cache"]["ttl"] != stage_config["cache"]["ttl"]:
    differences.append({
        "setting": "cache.ttl",
        "production": prod_config["cache"]["ttl"],
        "staging": stage_config["cache"]["ttl"],
        "impact": "Cache invalidation frequency differs"
    })

# Compare features
if prod_config["features"]["debug_mode"] != stage_config["features"]["debug_mode"]:
    differences.append({
        "setting": "features.debug_mode",
        "production": prod_config["features"]["debug_mode"],
        "staging": stage_config["features"]["debug_mode"],
        "impact": "Security and logging implications"
    })

# Generate report
print("=== Environment Configuration Analysis ===")
print(f"Differences found: {len(differences)}")

for diff in differences:
    print(f"\\n{diff['setting']}:")
    print(f"  Production: {diff['production']}")
    print(f"  Staging: {diff['staging']}")
    print(f"  Impact: {diff['impact']}")

# Generate recommendations
print("\\n=== Recommendations ===")
if any(d["setting"] == "features.debug_mode" for d in differences):
    print("⚠️  Ensure debug mode is disabled in production")

if any(d["setting"] == "database.pool_size" for d in differences):
    print("📊 Monitor database connections in staging before promoting to production")
"""

        result = await execute_code(
            code=comparison_code,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "Differences found: 3" in result.output
        assert "debug mode is disabled in production" in result.output
        assert "database.pool_size" in result.output
        assert result.variables["differences"] is not None
        assert len(result.variables["differences"]) == 3
