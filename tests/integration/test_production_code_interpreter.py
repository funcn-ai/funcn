"""Production-like integration tests for code interpreter tool.

Demonstrates real-world usage patterns for code execution and analysis.
"""

import asyncio
import json
import pytest
from datetime import datetime

# Import actual components
from packages.sygaldry_registry.components.tools.code_interpreter.tool import (
    CodeExecutionResult,
    execute_code,
    execute_code_with_timeout,
    validate_code,
)
from pathlib import Path


class TestProductionCodeInterpreter:
    """Test real-world code interpreter usage scenarios."""

    @pytest.mark.asyncio
    async def test_data_analysis_workflow(self):
        """Test a complete data analysis workflow.

        Simulates: Analyzing data and generating insights.
        """
        analysis_code = """
import json
from collections import Counter
from datetime import datetime

# Simulated sales data
sales_data = [
    {"product": "Laptop", "category": "Electronics", "price": 999, "quantity": 2, "date": "2024-01-15"},
    {"product": "Mouse", "category": "Electronics", "price": 29, "quantity": 5, "date": "2024-01-15"},
    {"product": "Desk", "category": "Furniture", "price": 299, "quantity": 1, "date": "2024-01-16"},
    {"product": "Chair", "category": "Furniture", "price": 199, "quantity": 2, "date": "2024-01-16"},
    {"product": "Monitor", "category": "Electronics", "price": 399, "quantity": 3, "date": "2024-01-17"},
]

# Calculate metrics
total_revenue = sum(item["price"] * item["quantity"] for item in sales_data)
total_items = sum(item["quantity"] for item in sales_data)
avg_order_value = total_revenue / len(sales_data)

# Category analysis
category_revenue = {}
for item in sales_data:
    category = item["category"]
    revenue = item["price"] * item["quantity"]
    category_revenue[category] = category_revenue.get(category, 0) + revenue

# Find best selling products
product_quantities = Counter()
for item in sales_data:
    product_quantities[item["product"]] = item["quantity"]

print("=== Sales Analysis Report ===")
print(f"Period: 2024-01-15 to 2024-01-17")
print(f"\\nTotal Revenue: ${total_revenue:,.2f}")
print(f"Total Items Sold: {total_items}")
print(f"Average Order Value: ${avg_order_value:.2f}")

print("\\n=== Revenue by Category ===")
for category, revenue in sorted(category_revenue.items(), key=lambda x: x[1], reverse=True):
    percentage = (revenue / total_revenue) * 100
    print(f"{category}: ${revenue:,.2f} ({percentage:.1f}%)")

print("\\n=== Top Products by Quantity ===")
for product, quantity in product_quantities.most_common(3):
    print(f"{product}: {quantity} units")

# Generate insights
insights = []
if category_revenue.get("Electronics", 0) > total_revenue * 0.6:
    insights.append("Electronics dominate sales - consider expanding electronic product line")

if avg_order_value < 500:
    insights.append("Low average order value - implement bundling or upselling strategies")

if len(set(item["date"] for item in sales_data)) < 3:
    insights.append("Limited date range - gather more data for better insights")

print("\\n=== Insights & Recommendations ===")
for i, insight in enumerate(insights, 1):
    print(f"{i}. {insight}")

# Create summary for further processing
summary = {
    "total_revenue": total_revenue,
    "total_items": total_items,
    "avg_order_value": avg_order_value,
    "top_category": max(category_revenue.items(), key=lambda x: x[1])[0],
    "insights_count": len(insights)
}

result = summary
"""

        # Execute analysis
        result = await execute_code(
            code=analysis_code,
            timeout_seconds=5,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "Sales Analysis Report" in result.output
        assert "Total Revenue:" in result.output
        assert "Revenue by Category" in result.output
        assert "Insights & Recommendations" in result.output

        # Check captured variables
        assert result.variables.get("summary") is not None
        summary = result.variables["summary"]
        assert summary["total_revenue"] > 0
        assert summary["total_items"] > 0
        assert summary["top_category"] in ["Electronics", "Furniture"]

    @pytest.mark.asyncio
    async def test_code_generation_and_validation(self):
        """Test code generation, validation, and execution workflow.

        Simulates: Generating code dynamically and validating it.
        """
        # Step 1: Generate code based on requirements
        code_template = """
def process_{data_type}(data):
    \"\"\"Process {data_type} data and return analysis.\"\"\"
    if not isinstance(data, {expected_type}):
        raise TypeError("Invalid data type")

    result = {{
        "data_type": "{data_type}",
        "count": len(data),
        "processed": True
    }}

    # Type-specific processing
    {specific_processing}

    return result

# Test the generated function
test_data = {test_data}
result = process_{data_type}(test_data)
print(f"Processed {{result['count']}} {data_type} items")
print(f"Result: {{result}}")
"""

        # Generate code for different data types
        configurations = [
            {
                "data_type": "numbers",
                "expected_type": "list",
                "specific_processing": 'result["sum"] = sum(data)\n    result["average"] = sum(data) / len(data) if data else 0',
                "test_data": "[1, 2, 3, 4, 5]"
            },
            {
                "data_type": "strings",
                "expected_type": "list",
                "specific_processing": 'result["total_length"] = sum(len(s) for s in data)\n    result["longest"] = max(data, key=len) if data else ""',
                "test_data": '["hello", "world", "test"]'
            }
        ]

        for config in configurations:
            generated_code = code_template.format(**config)

            # Step 2: Validate the generated code
            is_valid, error = validate_code(generated_code)
            assert is_valid is True, f"Generated code is invalid: {error}"

            # Step 3: Execute the generated code
            result = await execute_code(
                code=generated_code,
                timeout_seconds=2,
                capture_variables=True,
                use_subprocess=False
            )

            assert result.success is True
            assert "Processed" in result.output
            assert result.variables.get("result") is not None

            # Verify type-specific processing
            if config["data_type"] == "numbers":
                assert "sum" in result.variables["result"]
                assert result.variables["result"]["sum"] == 15
            elif config["data_type"] == "strings":
                assert "longest" in result.variables["result"]
                assert result.variables["result"]["longest"] == "hello"

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery patterns.

        Simulates: Handling various error conditions in production.
        """
        error_handling_code = """
import json
import traceback
from typing import Any, Dict, List

# Define a series of operations that might fail
def risky_operations():
    \"\"\"Execute operations with potential failures.\"\"\"
    results = []

    # Operation 1: Division (might have zero division)
    try:
        values = [10, 5, 0, 2]
        for i, val in enumerate(values):
            try:
                result = 100 / val
                results.append({"op": f"divide_by_{val}", "success": True, "result": result})
            except ZeroDivisionError:
                results.append({"op": f"divide_by_{val}", "success": False, "error": "Division by zero"})
    except Exception as e:
        results.append({"op": "division_batch", "success": False, "error": str(e)})

    # Operation 2: Type conversion
    try:
        conversions = ["123", "45.6", "not_a_number", "789"]
        for val in conversions:
            try:
                num = float(val)
                results.append({"op": f"convert_{val}", "success": True, "result": num})
            except ValueError:
                results.append({"op": f"convert_{val}", "success": False, "error": "Invalid number format"})
    except Exception as e:
        results.append({"op": "conversion_batch", "success": False, "error": str(e)})

    # Operation 3: Dictionary access
    try:
        data = {"key1": "value1", "key2": "value2"}
        keys_to_check = ["key1", "key3", "key2", "key4"]
        for key in keys_to_check:
            try:
                value = data[key]
                results.append({"op": f"access_{key}", "success": True, "result": value})
            except KeyError:
                # Implement fallback
                default_value = f"default_for_{key}"
                results.append({"op": f"access_{key}", "success": True, "result": default_value, "fallback": True})
    except Exception as e:
        results.append({"op": "dictionary_batch", "success": False, "error": str(e)})

    return results

# Execute operations
operation_results = risky_operations()

# Analyze results
successful = [r for r in operation_results if r["success"] and not r.get("fallback")]
failed = [r for r in operation_results if not r["success"]]
fallbacks = [r for r in operation_results if r.get("fallback")]

print("=== Operation Results Summary ===")
print(f"Total operations: {len(operation_results)}")
print(f"Successful: {len(successful)}")
print(f"Failed: {len(failed)}")
print(f"Used fallback: {len(fallbacks)}")

print("\\n=== Failed Operations ===")
for fail in failed:
    print(f"- {fail['op']}: {fail['error']}")

print("\\n=== Recovery Strategies Applied ===")
for fallback in fallbacks:
    print(f"- {fallback['op']}: Used default value '{fallback['result']}'")

# Calculate system resilience score
total_ops = len(operation_results)
handled_ops = len(successful) + len(fallbacks)
resilience_score = (handled_ops / total_ops) * 100 if total_ops > 0 else 0

print(f"\\n=== System Resilience ===")
print(f"Resilience Score: {resilience_score:.1f}%")
print(f"Status: {'Robust' if resilience_score > 80 else 'Needs Improvement'}")

# Generate recommendations
recommendations = []
if len(failed) > 0:
    recommendations.append("Implement additional error handling for critical operations")
if len(fallbacks) > total_ops * 0.3:
    recommendations.append("Review fallback strategies - too many operations using defaults")
if resilience_score < 90:
    recommendations.append("Add retry logic for transient failures")

print("\\n=== Recommendations ===")
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. {rec}")

summary = {
    "resilience_score": resilience_score,
    "total_operations": total_ops,
    "failures": len(failed),
    "recoveries": len(fallbacks)
}
"""

        result = await execute_code(
            code=error_handling_code,
            timeout_seconds=5,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "Operation Results Summary" in result.output
        assert "Failed Operations" in result.output
        assert "Recovery Strategies Applied" in result.output
        assert "System Resilience" in result.output

        # Check resilience metrics
        assert result.variables.get("summary") is not None
        assert result.variables["summary"]["resilience_score"] > 0
        assert result.variables["summary"]["failures"] >= 2  # We expect some failures
        assert result.variables["summary"]["recoveries"] >= 2  # We expect some recoveries

    @pytest.mark.asyncio
    async def test_performance_monitoring_workflow(self):
        """Test performance monitoring and optimization.

        Simulates: Monitoring code performance and identifying bottlenecks.
        """
        performance_code = """
import time
import statistics
from typing import List, Tuple

def measure_operation(name: str, operation, *args):
    \"\"\"Measure operation execution time.\"\"\"
    import time  # Import inside function to work around exec namespace issue
    start = time.time()
    result = operation(*args)
    duration = time.time() - start
    return {"name": name, "duration": duration, "result": result}

# Define operations to benchmark
def slow_operation(n: int) -> int:
    \"\"\"Simulate slow operation.\"\"\"
    total = 0
    for i in range(n * 1000):
        total += i
    return total

def fast_operation(n: int) -> int:
    \"\"\"Simulate fast operation.\"\"\"
    return sum(range(n * 1000))

def optimized_operation(n: int) -> int:
    \"\"\"Simulate optimized operation using formula.\"\"\"
    # Sum of arithmetic sequence: n * (n - 1) / 2
    n_total = n * 1000
    return n_total * (n_total - 1) // 2

# Benchmark operations
operations = [
    ("slow_loop", slow_operation, 100),
    ("fast_builtin", fast_operation, 100),
    ("optimized_formula", optimized_operation, 100),
    ("slow_loop_large", slow_operation, 500),
    ("fast_builtin_large", fast_operation, 500),
    ("optimized_formula_large", optimized_operation, 500),
]

results = []
for name, func, arg in operations:
    result = measure_operation(name, func, arg)
    results.append(result)

# Analyze performance
durations = [r["duration"] for r in results]
avg_duration = statistics.mean(durations)
median_duration = statistics.median(durations)

print("=== Performance Benchmark Results ===")
print(f"Operations tested: {len(results)}")
print(f"Average duration: {avg_duration:.4f}s")
print(f"Median duration: {median_duration:.4f}s")

print("\\n=== Operation Performance ===")
# Sort by duration
sorted_results = sorted(results, key=lambda x: x["duration"])
for r in sorted_results:
    # Create visual bar
    bar_length = int(r["duration"] / max(durations) * 50)
    bar = "█" * bar_length
    print(f"{r['name']:20} {r['duration']:.4f}s {bar}")

# Identify slowest operations
threshold = avg_duration * 2
slow_ops = [r for r in results if r["duration"] > threshold]

print("\\n=== Performance Issues ===")
if slow_ops:
    print(f"Found {len(slow_ops)} slow operations (>{threshold:.4f}s):")
    for op in slow_ops:
        speedup_potential = op["duration"] / sorted_results[0]["duration"]
        print(f"- {op['name']}: {op['duration']:.4f}s (potential {speedup_potential:.1f}x speedup)")
else:
    print("No significant performance issues detected")

# Calculate optimization impact
baseline = next(r for r in results if "slow_loop" in r["name"])
optimized = next(r for r in results if "optimized_formula" in r["name"])
improvement = ((baseline["duration"] - optimized["duration"]) / baseline["duration"]) * 100

print("\\n=== Optimization Impact ===")
print("Baseline (slow_loop): {:.4f}s".format(baseline['duration']))
print("Optimized (formula): {:.4f}s".format(optimized['duration']))
print("Improvement: {:.1f}%".format(improvement))
print("Speedup: {:.1f}x".format(baseline['duration'] / optimized['duration']))

performance_summary = {
    "total_operations": len(results),
    "avg_duration": avg_duration,
    "slowest_operation": max(results, key=lambda x: x["duration"])["name"],
    "fastest_operation": min(results, key=lambda x: x["duration"])["name"],
    "optimization_improvement": improvement
}

# Ensure variable is captured
result = performance_summary
"""

        result = await execute_code(
            code=performance_code,
            timeout_seconds=10,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "Performance Benchmark Results" in result.output
        assert "Operation Performance" in result.output
        assert "Optimization Impact" in result.output

        # Verify performance metrics
        assert result.variables.get("result") is not None
        summary = result.variables["result"]
        assert summary["optimization_improvement"] > 50  # Expect significant improvement
        assert "optimized" in summary["fastest_operation"]
        assert "slow" in summary["slowest_operation"]

    @pytest.mark.asyncio
    async def test_complex_data_processing(self):
        """Test complex data processing pipeline.

        Simulates: Multi-stage data transformation and analysis.
        """
        pipeline_code = """
import json
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Simulated log data
log_entries = [
    {"timestamp": "2024-01-15 10:00:00", "level": "INFO", "service": "api", "message": "Request received", "duration": 45},
    {"timestamp": "2024-01-15 10:00:01", "level": "ERROR", "service": "api", "message": "Database connection failed", "duration": 0},
    {"timestamp": "2024-01-15 10:00:02", "level": "WARN", "service": "cache", "message": "Cache miss", "duration": 12},
    {"timestamp": "2024-01-15 10:00:03", "level": "INFO", "service": "api", "message": "Request completed", "duration": 120},
    {"timestamp": "2024-01-15 10:00:04", "level": "INFO", "service": "worker", "message": "Job started", "duration": 0},
    {"timestamp": "2024-01-15 10:00:10", "level": "INFO", "service": "worker", "message": "Job completed", "duration": 6000},
    {"timestamp": "2024-01-15 10:00:15", "level": "ERROR", "service": "api", "message": "Timeout error", "duration": 5000},
    {"timestamp": "2024-01-15 10:00:20", "level": "INFO", "service": "cache", "message": "Cache hit", "duration": 2},
]

# Stage 1: Parse and enrich data
print("=== Stage 1: Data Parsing ===")
for entry in log_entries:
    entry["parsed_time"] = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
    entry["is_error"] = entry["level"] == "ERROR"
    entry["is_slow"] = entry["duration"] > 1000
print(f"Parsed {len(log_entries)} log entries")

# Stage 2: Aggregate by service
print("\\n=== Stage 2: Service Aggregation ===")
service_stats = defaultdict(lambda: {"count": 0, "errors": 0, "total_duration": 0, "durations": []})

for entry in log_entries:
    service = entry["service"]
    service_stats[service]["count"] += 1
    if entry["is_error"]:
        service_stats[service]["errors"] += 1
    service_stats[service]["total_duration"] += entry["duration"]
    if entry["duration"] > 0:
        service_stats[service]["durations"].append(entry["duration"])

# Calculate statistics
for service, stats in service_stats.items():
    if stats["durations"]:
        stats["avg_duration"] = statistics.mean(stats["durations"])
        stats["median_duration"] = statistics.median(stats["durations"])
        stats["max_duration"] = max(stats["durations"])
    else:
        stats["avg_duration"] = 0
        stats["median_duration"] = 0
        stats["max_duration"] = 0
    stats["error_rate"] = (stats["errors"] / stats["count"]) * 100 if stats["count"] > 0 else 0

# Display service statistics
for service, stats in sorted(service_stats.items()):
    print(f"\\n{service}:")
    print(f"  Requests: {stats['count']}")
    print(f"  Errors: {stats['errors']} ({stats['error_rate']:.1f}%)")
    print(f"  Avg Duration: {stats['avg_duration']:.0f}ms")

# Stage 3: Time-based analysis
print("\\n=== Stage 3: Time Analysis ===")
time_windows = defaultdict(lambda: {"requests": 0, "errors": 0})

for entry in log_entries:
    # Group by 5-second windows
    window = entry["parsed_time"].replace(second=(entry["parsed_time"].second // 5) * 5, microsecond=0)
    time_windows[window]["requests"] += 1
    if entry["is_error"]:
        time_windows[window]["errors"] += 1

# Find peak periods
peak_window = max(time_windows.items(), key=lambda x: x[1]["requests"])
print(f"Peak period: {peak_window[0]} with {peak_window[1]['requests']} requests")

# Stage 4: Generate alerts
print("\\n=== Stage 4: Alert Generation ===")
alerts = []

# Check error rates
for service, stats in service_stats.items():
    if stats["error_rate"] > 20:
        alerts.append({
            "severity": "HIGH",
            "service": service,
            "message": f"High error rate: {stats['error_rate']:.1f}%"
        })

# Check performance
for service, stats in service_stats.items():
    if stats["avg_duration"] > 2000:
        alerts.append({
            "severity": "MEDIUM",
            "service": service,
            "message": f"Slow response time: {stats['avg_duration']:.0f}ms average"
        })

# Display alerts
if alerts:
    for alert in sorted(alerts, key=lambda x: x["severity"]):
        print(f"[{alert['severity']}] {alert['service']}: {alert['message']}")
else:
    print("No alerts generated")

# Final summary
summary = {
    "total_entries": len(log_entries),
    "services_monitored": len(service_stats),
    "total_errors": sum(s["errors"] for s in service_stats.values()),
    "alerts_generated": len(alerts),
    "peak_requests": peak_window[1]["requests"],
    "overall_health": "DEGRADED" if alerts else "HEALTHY"
}

print("\\n=== Pipeline Summary ===")
print(json.dumps(summary, indent=2))
"""

        result = await execute_code(
            code=pipeline_code,
            timeout_seconds=5,
            capture_variables=True,
            use_subprocess=False
        )

        assert result.success is True
        assert "Stage 1: Data Parsing" in result.output
        assert "Stage 2: Service Aggregation" in result.output
        assert "Stage 3: Time Analysis" in result.output
        assert "Stage 4: Alert Generation" in result.output
        assert "Pipeline Summary" in result.output

        # Verify pipeline results
        assert result.variables.get("summary") is not None
        summary = result.variables["summary"]
        assert summary["total_entries"] == 8
        assert summary["services_monitored"] == 3
        assert summary["alerts_generated"] >= 0
        assert summary["overall_health"] in ["HEALTHY", "DEGRADED"]
