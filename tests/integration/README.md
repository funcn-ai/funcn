# Integration Tests for Funcn Registry

This directory contains production-like integration tests that demonstrate real-world usage patterns for tools and agents in the Funcn registry.

## Test Files

### test_production_code_interpreter.py
Simplified production tests focusing on the code interpreter tool with realistic scenarios:
- Data analysis workflows
- Code generation and validation
- Error handling and recovery
- Performance monitoring
- Complex data processing pipelines

### test_production_scenarios_simple.py
Additional simplified tests demonstrating:
- Code analysis workflows
- Data processing with JSON operations
- Report generation workflows
- Error handling patterns
- Performance monitoring

### test_production_scenarios.py
Comprehensive production scenarios including:
- Multi-tool research workflows
- Codebase analysis patterns
- Data pipeline workflows
- Error recovery strategies
- Performance monitoring

### test_agent_tool_integration.py
Tests for agent-tool interactions including:
- Rate limiting and retries
- Multi-agent coordination
- Concurrent operations
- State persistence
- Graceful degradation

### test_real_world_agent_workflows.py
Complete agent workflow tests simulating:
- Full research workflows
- Document processing pipelines
- Code generation and validation
- Knowledge extraction

## Running the Tests

Run all integration tests:
```bash
python -m pytest tests/integration/ -v
```

Run a specific test file:
```bash
python -m pytest tests/integration/test_production_code_interpreter.py -v
```

Run a specific test:
```bash
python -m pytest tests/integration/test_production_scenarios_simple.py::TestSimpleProductionScenarios::test_code_analysis_workflow -v
```

## Key Patterns Demonstrated

1. **Error Handling**: Shows how to handle failures gracefully in production
2. **Performance Monitoring**: Demonstrates tracking and optimizing performance
3. **Data Validation**: Shows robust data validation and cleaning patterns
4. **Concurrent Operations**: Demonstrates async/concurrent processing
5. **State Management**: Shows how to maintain state across operations
6. **Multi-tool Coordination**: Demonstrates tools working together

## Notes

- These tests use mocking for external services while preserving the integration patterns
- The tests demonstrate production-ready error handling and recovery
- Performance tests show how to identify and optimize bottlenecks
- All tests follow async patterns used in production environments