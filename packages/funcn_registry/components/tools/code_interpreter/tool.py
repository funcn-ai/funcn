"""Code Interpreter Tool for safe Python code execution."""

import ast
import asyncio
import io
import json
import os
import subprocess
import sys
import tempfile
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pydantic import BaseModel, Field
from typing import Any, Optional


class CodeExecutionResult(BaseModel):
    """Result of code execution."""

    success: bool = Field(..., description="Whether the code executed successfully")
    output: str | None = Field(None, description="Standard output from code execution")
    error: str | None = Field(None, description="Error message if execution failed")
    return_value: Any | None = Field(None, description="Return value of the code")
    execution_time: float = Field(..., description="Time taken to execute in seconds")
    variables: dict[str, Any] = Field(default_factory=dict, description="Variables in the execution namespace")
    warnings: list[str] = Field(default_factory=list, description="Any warnings during execution")


async def execute_code(
    code: str,
    timeout_seconds: int = 30,
    capture_variables: bool = True,
    use_subprocess: bool = True,
    allowed_modules: list[str] | None = None,
) -> CodeExecutionResult:
    """Execute Python code safely with sandboxing and timeout controls.

    Args:
        code: Python code to execute
        timeout_seconds: Maximum execution time in seconds
        capture_variables: Whether to capture variables after execution
        use_subprocess: Whether to use subprocess isolation for safer execution
        allowed_modules: List of allowed standard library modules

    Returns:
        CodeExecutionResult with output, errors, and captured variables
    """
    if allowed_modules is None:
        allowed_modules = [
            "math",
            "statistics",
            "json",
            "datetime",
            "re",
            "collections",
            "itertools",
            "functools",
            "operator",
            "urllib.parse",
            "base64",
            "hashlib",
            "random",
            "string",
            "decimal",
            "fractions",
        ]

    if use_subprocess:
        return await execute_in_subprocess(code, timeout_seconds, capture_variables, allowed_modules)
    else:
        return await execute_directly(code, timeout_seconds, capture_variables)


async def execute_in_subprocess(
    code: str, timeout_seconds: int, capture_variables: bool, allowed_modules: list[str]
) -> CodeExecutionResult:
    """Execute code in an isolated subprocess for safety."""
    # Create a temporary file to execute the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Wrap the code to capture output and variables
        wrapper_code = f'''
import sys
import json
import traceback
from io import StringIO

# Restrict imports to allowed modules
allowed_modules = {allowed_modules}
original_import = __builtins__.__import__

def restricted_import(name, *args, **kwargs):
    if name.split('.')[0] not in allowed_modules:
        raise ImportError(f"Import of module '{{name}}' is not allowed")
    return original_import(name, *args, **kwargs)

__builtins__.__import__ = restricted_import

# Capture output
output_buffer = StringIO()
error_buffer = StringIO()
sys.stdout = output_buffer
sys.stderr = error_buffer

result = {{
    "success": False,
    "output": None,
    "error": None,
    "return_value": None,
    "variables": {{}}
}}

try:
    # Execute the user code
    exec_globals = {{}}
    exec_locals = {{}}
    exec("""{code}""", exec_globals, exec_locals)

    # Capture variables if requested
    if {capture_variables}:
        for name, value in exec_locals.items():
            if not name.startswith('_'):
                try:
                    # Try to serialize the value
                    json.dumps(value)
                    result["variables"][name] = value
                except Exception:
                    result["variables"][name] = str(value)

    result["success"] = True
    result["output"] = output_buffer.getvalue()

except Exception as e:
    result["error"] = traceback.format_exc()
    result["output"] = output_buffer.getvalue()

# Restore stdout/stderr
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

# Output result as JSON
print(json.dumps(result))
'''
        f.write(wrapper_code)
        temp_path = f.name

    try:
        # Run the code in a subprocess with timeout
        start_time = asyncio.get_event_loop().time()
        process = await asyncio.create_subprocess_exec(
            sys.executable, temp_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
            execution_time = asyncio.get_event_loop().time() - start_time

            if stderr:
                return CodeExecutionResult(
                    success=False,
                    output=None,
                    error=stderr.decode(),
                    return_value=None,
                    execution_time=execution_time,
                    variables={},
                    warnings=[],
                )

            # Parse the JSON result
            result = json.loads(stdout.decode())
            return CodeExecutionResult(
                success=result["success"],
                output=result["output"],
                error=result["error"],
                return_value=result["return_value"],
                execution_time=execution_time,
                variables=result["variables"],
                warnings=[],
            )

        except TimeoutError:
            process.terminate()
            await process.wait()
            return CodeExecutionResult(
                success=False,
                output=None,
                error=f"Code execution timed out after {timeout_seconds} seconds",
                return_value=None,
                execution_time=timeout_seconds,
                variables={},
                warnings=[],
            )

    finally:
        # Clean up temp file
        os.unlink(temp_path)


async def execute_directly(code: str, timeout_seconds: int, capture_variables: bool) -> CodeExecutionResult:
    """Execute code directly in the current process (less safe)."""
    # Validate syntax first
    try:
        ast.parse(code)
    except SyntaxError as e:
        return CodeExecutionResult(
            success=False,
            output=None,
            error=f"Syntax error: {str(e)}",
            return_value=None,
            execution_time=0.0,
            variables={},
            warnings=[],
        )

    # Set up execution environment
    output_buffer = io.StringIO()
    error_buffer = io.StringIO()

    # Create isolated namespace
    exec_globals = {
        "__builtins__": __builtins__,
        "__name__": "__main__",
    }
    exec_locals: dict[str, Any] = {}

    start_time = asyncio.get_event_loop().time()

    try:
        # Execute with output capture
        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
            # Use asyncio to run with timeout
            await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, exec, code, exec_globals, exec_locals), timeout=timeout_seconds
            )

        execution_time = asyncio.get_event_loop().time() - start_time

        # Capture variables if requested
        variables = {}
        if capture_variables:
            for name, value in exec_locals.items():
                if not name.startswith('_'):
                    try:
                        # Try to serialize for safety
                        json.dumps(value)
                        variables[name] = value
                    except Exception:
                        variables[name] = str(value)

        return CodeExecutionResult(
            success=True,
            output=output_buffer.getvalue(),
            error=error_buffer.getvalue() or None,
            return_value=None,
            execution_time=execution_time,
            variables=variables,
            warnings=[],
        )

    except TimeoutError:
        return CodeExecutionResult(
            success=False,
            output=None,
            error=f"Code execution timed out after {timeout_seconds} seconds",
            return_value=None,
            execution_time=timeout_seconds,
            variables={},
            warnings=[],
        )
    except Exception as e:
        execution_time = asyncio.get_event_loop().time() - start_time
        return CodeExecutionResult(
            success=False,
            output=output_buffer.getvalue(),
            error=traceback.format_exc(),
            return_value=None,
            execution_time=execution_time,
            variables={},
            warnings=[],
        )


def validate_code(code: str) -> tuple[bool, str | None]:
    """Validate Python code syntax without executing.

    Args:
        code: Python code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, str(e)


async def execute_code_with_timeout(code: str, timeout_seconds: int = 5, max_output_length: int = 10000) -> CodeExecutionResult:
    """Execute code with strict timeout and output limits.

    Args:
        code: Python code to execute
        timeout_seconds: Maximum execution time
        max_output_length: Maximum length of output to capture

    Returns:
        CodeExecutionResult with limited output
    """
    result = await execute_code(code=code, timeout_seconds=timeout_seconds, capture_variables=False, use_subprocess=True)

    # Truncate output if too long
    if result.output and len(result.output) > max_output_length:
        result.output = result.output[:max_output_length] + "\n... (output truncated)"

    return result
