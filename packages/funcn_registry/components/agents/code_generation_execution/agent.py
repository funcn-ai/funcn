from __future__ import annotations

import ast
import os
import subprocess
import tempfile
from lilypad import trace
from mirascope import llm, prompt_template
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional


# Response models for structured outputs
class CodeAnalysis(BaseModel):
    """Analysis of generated code for safety and correctness."""
    is_safe: bool = Field(..., description="Whether the code is safe to execute")
    safety_concerns: list[str] = Field(default_factory=list, description="List of safety concerns if any")
    imports_used: list[str] = Field(default_factory=list, description="Python imports used in the code")
    has_file_operations: bool = Field(default=False, description="Whether code performs file operations")
    has_network_operations: bool = Field(default=False, description="Whether code performs network operations")
    has_system_calls: bool = Field(default=False, description="Whether code makes system calls")
    complexity_score: int = Field(..., ge=1, le=10, description="Code complexity score (1-10)")


class GeneratedCode(BaseModel):
    """Generated code with metadata."""
    code: str = Field(..., description="The generated Python code")
    language: str = Field(default="python", description="Programming language")
    explanation: str = Field(..., description="Explanation of what the code does")
    requirements: list[str] = Field(default_factory=list, description="Required packages/dependencies")
    example_usage: str | None = Field(default=None, description="Example of how to use the code")


class CodeExecutionResult(BaseModel):
    """Result of code execution."""
    success: bool = Field(..., description="Whether execution was successful")
    output: str | None = Field(default=None, description="Standard output from execution")
    error: str | None = Field(default=None, description="Error message if execution failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    return_value: Any = Field(default=None, description="Return value from the code")


class CodeGenerationResponse(BaseModel):
    """Complete response for code generation and execution."""
    task_description: str = Field(..., description="Description of the task")
    generated_code: GeneratedCode = Field(..., description="The generated code")
    code_analysis: CodeAnalysis = Field(..., description="Safety and complexity analysis")
    execution_result: CodeExecutionResult | None = Field(default=None, description="Execution result if code was run")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations for improvement")


# Tool for executing Python code safely
@trace()
async def execute_python_code(
    code: str,
    timeout: int = 30,
    allowed_imports: list[str] | None = None
) -> CodeExecutionResult:
    """
    Execute Python code in a sandboxed environment.

    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        allowed_imports: List of allowed import modules (None allows all)

    Returns:
        CodeExecutionResult with output or error
    """
    import time
    start_time = time.time()

    try:
        # Parse the code to check for safety
        tree = ast.parse(code)

        # Check imports if restrictions are specified
        if allowed_imports is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in allowed_imports:
                            return CodeExecutionResult(
                                success=False,
                                error=f"Import '{alias.name}' is not allowed",
                                execution_time=time.time() - start_time
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module not in allowed_imports:
                        return CodeExecutionResult(
                            success=False,
                            error=f"Import from '{node.module}' is not allowed",
                            execution_time=time.time() - start_time
                        )

        # Create a temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Execute the code with timeout
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return CodeExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                execution_time=time.time() - start_time
            )
        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    except subprocess.TimeoutExpired:
        return CodeExecutionResult(
            success=False,
            error=f"Code execution timed out after {timeout} seconds",
            execution_time=timeout
        )
    except Exception as e:
        return CodeExecutionResult(
            success=False,
            error=f"Execution error: {str(e)}",
            execution_time=time.time() - start_time
        )


# Step 1: Generate code for the task
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=GeneratedCode,
)
@prompt_template(
    """
    You are an expert Python programmer. Generate clean, efficient, and well-documented code for the following task.

    Task: {task}
    Requirements: {requirements}
    Constraints: {constraints}

    Guidelines:
    1. Write clean, readable Python code
    2. Include proper error handling
    3. Add helpful comments and docstrings
    4. Follow PEP 8 style guidelines
    5. Optimize for performance where appropriate
    6. Include type hints for better code clarity
    7. List any required external packages

    Generate complete, runnable code that accomplishes the task.
    """
)
async def generate_code(
    task: str,
    requirements: str = "None specified",
    constraints: str = "None specified"
):
    """Generate Python code for a given task."""
    pass


# Step 2: Analyze code for safety and complexity
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=CodeAnalysis,
)
@prompt_template(
    """
    You are a code security and quality analyst. Analyze the following Python code for safety and complexity.

    Code to analyze:
    ```python
    {code}
    ```

    Check for:
    1. Safety concerns (file access, network calls, system commands, etc.)
    2. Imports used
    3. Code complexity (1-10 scale)
    4. Potential security vulnerabilities
    5. Resource usage concerns

    Be thorough in identifying any risks or concerns.
    """
)
async def analyze_code_safety(code: str):
    """Analyze code for safety and complexity."""
    pass


# Step 3: Generate recommendations
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
)
@prompt_template(
    """
    Based on the code analysis and execution results, provide recommendations for improvement.

    Original task: {task}
    Code analysis: {analysis}
    Execution result: {execution_result}

    Provide 3-5 specific, actionable recommendations for:
    1. Code quality improvements
    2. Performance optimizations
    3. Security enhancements
    4. Better error handling
    5. Documentation improvements

    Return a list of recommendation strings.
    """
)
async def generate_recommendations(
    task: str,
    analysis: str,
    execution_result: str
) -> list[str]:
    """Generate recommendations for code improvement."""
    pass


@trace()
async def generate_and_execute_code(
    task: str,
    requirements: str = "None specified",
    constraints: str = "None specified",
    auto_execute: bool = True,
    safety_level: Literal["strict", "moderate", "permissive"] = "moderate",
    timeout: int = 30,
    llm_provider: str = "openai",
    model: str = "gpt-4o-mini"
) -> CodeGenerationResponse:
    """
    Generate and optionally execute Python code for a given task.

    This agent generates Python code based on the task description,
    analyzes it for safety, and optionally executes it in a sandboxed environment.

    Args:
        task: Description of the coding task
        requirements: Specific requirements for the code
        constraints: Constraints or limitations
        auto_execute: Whether to automatically execute safe code
        safety_level: Safety checking level
        timeout: Maximum execution time in seconds
        llm_provider: LLM provider to use
        model: Specific model to use

    Returns:
        CodeGenerationResponse with generated code and execution results
    """
    # Step 1: Generate code
    generated_code = await generate_code(
        task=task,
        requirements=requirements,
        constraints=constraints
    )

    # Step 2: Analyze code safety
    code_analysis = await analyze_code_safety(generated_code.code)

    # Step 3: Decide whether to execute based on safety level
    should_execute = auto_execute and code_analysis.is_safe

    if safety_level == "strict" and (
        code_analysis.has_file_operations or
        code_analysis.has_network_operations or
        code_analysis.has_system_calls
    ) or safety_level == "moderate" and code_analysis.has_system_calls:
        should_execute = False

    # Step 4: Execute if appropriate
    execution_result = None
    if should_execute:
        # Define allowed imports based on safety level
        allowed_imports = None
        if safety_level == "strict":
            allowed_imports = [
                "math", "random", "datetime", "json", "re",
                "collections", "itertools", "functools"
            ]

        execution_result = await execute_python_code(
            code=generated_code.code,
            timeout=timeout,
            allowed_imports=allowed_imports
        )

    # Step 5: Generate recommendations
    exec_result_str = str(execution_result.model_dump()) if execution_result else "Not executed"
    recommendations = await generate_recommendations(
        task=task,
        analysis=str(code_analysis.model_dump()),
        execution_result=exec_result_str
    )

    return CodeGenerationResponse(
        task_description=task,
        generated_code=generated_code,
        code_analysis=code_analysis,
        execution_result=execution_result,
        recommendations=recommendations
    )


# Convenience functions
async def generate_code_snippet(
    task: str,
    language: str = "python"
) -> str:
    """
    Generate a simple code snippet without execution.

    Returns just the code as a string.
    """
    result = await generate_and_execute_code(
        task=task,
        auto_execute=False
    )
    return result.generated_code.code


async def safe_execute_task(
    task: str,
    safety_level: Literal["strict", "moderate", "permissive"] = "strict"
) -> dict[str, Any]:
    """
    Generate and safely execute code for a task.

    Returns a simplified dictionary with results.
    """
    result = await generate_and_execute_code(
        task=task,
        auto_execute=True,
        safety_level=safety_level
    )

    return {
        "code": result.generated_code.code,
        "executed": result.execution_result is not None,
        "success": result.execution_result.success if result.execution_result else False,
        "output": result.execution_result.output if result.execution_result else None,
        "error": result.execution_result.error if result.execution_result else None,
        "recommendations": result.recommendations
    }
