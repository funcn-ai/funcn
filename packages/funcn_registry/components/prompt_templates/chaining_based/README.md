# Chaining-Based Prompt Templates

Chaining-based prompts demonstrate dynamic prompt composition and multi-step workflows. These patterns show how to combine multiple LLM calls to solve complex tasks that require sequential processing, parallel execution, or conditional logic.

## Templates Overview

### 1. Sequential Chain (`sequential_chain.py`)

Linear step-by-step processing where each step builds on the previous one.

**When to use:**

- Multi-stage document processing
- Progressive refinement tasks
- Workflows with dependencies
- Step-by-step transformations

**Key features:**

- Linear execution flow
- State passing between steps
- Error propagation handling
- Progress tracking

**Example use cases:**

- Research → Outline → Draft → Edit
- Data extraction → Analysis → Report
- Translation → Review → Polish

### 2. Parallel Chain (`parallel_chain.py`)

Concurrent execution of independent LLM calls for efficiency.

**When to use:**

- Independent subtasks
- Multi-perspective analysis
- Batch processing
- Performance optimization

**Key features:**

- Async/await patterns
- Concurrent execution
- Result aggregation
- Resource optimization

**Example use cases:**

- Multi-language translation
- Parallel document analysis
- Multiple expert opinions
- Batch content generation

### 3. Conditional Chain (`conditional_chain.py`)

Branching logic based on intermediate results.

**When to use:**

- Decision trees
- Dynamic workflows
- Content routing
- Adaptive processing

**Key features:**

- Conditional branching
- Dynamic path selection
- State-based decisions
- Fallback handling

**Example use cases:**

- Customer support routing
- Content classification → Action
- Risk assessment → Response
- Query type → Handler

### 4. Iterative Chain (`iterative_chain.py`)

Refinement through multiple passes until quality threshold is met.

**When to use:**

- Quality improvement
- Optimization tasks
- Convergence problems
- Progressive enhancement

**Key features:**

- Loop until condition
- Quality metrics
- Incremental improvement
- Convergence tracking

**Example use cases:**

- Content optimization
- Translation refinement
- Code improvement
- Answer enhancement

### 5. Multi-Step Reasoning (`multi_step_reasoning.py`)

Complex problem decomposition into manageable steps.

**When to use:**

- Complex problem-solving
- Mathematical reasoning
- Research tasks
- Comprehensive analysis

**Key features:**

- Problem decomposition
- Step planning
- Intermediate validation
- Result synthesis

**Example use cases:**

- Scientific research
- Business analysis
- Technical troubleshooting
- Strategic planning

## Implementation Patterns

### Sequential Pattern

```python
async def sequential_workflow(input_data: str) -> FinalResult:
    # Step 1: Initial processing
    step1_result = await process_step1(input_data)
    
    # Step 2: Build on step 1
    step2_result = await process_step2(step1_result)
    
    # Step 3: Final processing
    final_result = await process_step3(step2_result)
    
    return final_result
```

### Parallel Pattern

```python
async def parallel_workflow(input_data: str) -> AggregatedResult:
    # Launch parallel tasks
    tasks = [
        analyze_perspective_a(input_data),
        analyze_perspective_b(input_data),
        analyze_perspective_c(input_data)
    ]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    # Aggregate results
    return aggregate_results(results)
```

### Conditional Pattern

```python
async def conditional_workflow(query: str) -> Response:
    # Classify query
    query_type = await classify_query(query)
    
    # Route based on type
    if query_type == "technical":
        return await handle_technical(query)
    elif query_type == "general":
        return await handle_general(query)
    else:
        return await handle_fallback(query)
```

### Iterative Pattern

```python
async def iterative_workflow(content: str) -> OptimizedContent:
    current = content
    quality = 0.0
    
    while quality < 0.9 and iterations < 5:
        current = await improve_content(current)
        quality = await assess_quality(current)
        iterations += 1
    
    return current
```

## Best Practices

1. **State Management**: Carefully manage state between chain steps
2. **Error Handling**: Implement robust error handling at each step
3. **Progress Tracking**: Monitor progress through the chain
4. **Resource Limits**: Set maximum iterations/timeouts
5. **Fallback Strategies**: Always have fallback paths

## Performance Optimization

### Sequential Chains

- Minimize data passed between steps
- Consider caching intermediate results
- Use streaming where possible

### Parallel Chains

- Balance parallelism with rate limits
- Group similar operations
- Use connection pooling

### Conditional Chains

- Optimize classification/routing logic
- Cache routing decisions
- Minimize decision depth

### Iterative Chains

- Set reasonable iteration limits
- Define clear convergence criteria
- Track diminishing returns

## Common Patterns

### Map-Reduce Pattern

```python
async def map_reduce(items: list[str]) -> Summary:
    # Map: Process each item
    mapped = await asyncio.gather(*[
        process_item(item) for item in items
    ])
    
    # Reduce: Combine results
    return await reduce_results(mapped)
```

### Pipeline Pattern

```python
def create_pipeline(*steps):
    async def pipeline(input_data):
        result = input_data
        for step in steps:
            result = await step(result)
        return result
    return pipeline
```

### Fork-Join Pattern

```python
async def fork_join(data: str) -> CombinedResult:
    # Fork into parallel paths
    path_a = process_path_a(data)
    path_b = process_path_b(data)
    
    # Join results
    result_a, result_b = await asyncio.gather(path_a, path_b)
    return combine_results(result_a, result_b)
```

## Debugging Tips

1. **Logging**: Log inputs/outputs at each step
2. **Visualization**: Create flow diagrams for complex chains
3. **Intermediate Validation**: Validate data between steps
4. **Timeout Handling**: Set appropriate timeouts for each step
5. **Observability**: Use Lilypad tracing to monitor execution 
