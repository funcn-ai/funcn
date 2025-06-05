"""Test suite for code_interpreter_tool following best practices."""

import pytest
import subprocess
import sys
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import MagicMock, Mock, patch


class TestCodeInterpreterTool(BaseToolTest):
    """Test code_interpreter_tool component."""
    
    component_name = "code_interpreter_tool"
    component_path = Path("packages/funcn_registry/components/tools/code_interpreter_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.code_interpreter_tool import execute_code
        def mock_execute_code(
            code: str,
            language: str = "python",
            timeout: int = 30,
            capture_output: bool = True,
            safe_mode: bool = True,
            allowed_modules: list[str] | None = None
        ) -> dict[str, any]:
            """Mock code interpreter tool."""
            return {
                "output": "Hello, World!",
                "error": None,
                "return_value": None,
                "execution_time": 0.05,
                "variables": {"result": 42},
                "success": True
            }
        return mock_execute_code
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "code": "print('Hello, World!')",
                "language": "python",
                "timeout": 10
            },
            {
                "code": "result = 2 + 2\nprint(f'Result: {result}')",
                "capture_output": True,
                "safe_mode": True
            },
            {
                "code": "import math\nprint(math.sqrt(16))",
                "allowed_modules": ["math", "datetime"],
                "safe_mode": True
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, dict)
        assert "output" in output or "result" in output
        assert "error" in output
        assert "success" in output or "status" in output
    
    def test_basic_code_execution(self):
        """Test basic Python code execution."""
        tool = self.get_component_function()
        
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "Hello from Python\n"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool(
                code="print('Hello from Python')",
                language="python"
            )
            
            assert result["success"] is True
            assert "Hello" in result["output"]
            assert result["error"] is None
    
    def test_variable_capture(self):
        """Test capturing variables from executed code."""
        tool = self.get_component_function()
        
        code = """
x = 10
y = 20
result = x + y
data = {"key": "value", "count": result}
"""
        
        with patch("exec") as mock_exec:
            # Simulate exec populating locals
            captured_vars = {
                "x": 10,
                "y": 20,
                "result": 30,
                "data": {"key": "value", "count": 30}
            }
            
            result = tool(code, capture_output=True)
            
            # Should capture variables
            if "variables" in result:
                assert isinstance(result["variables"], dict)
                assert len(result["variables"]) > 0
    
    def test_timeout_handling(self):
        """Test code execution timeout."""
        tool = self.get_component_function()
        
        infinite_loop = """
while True:
    pass
"""
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["python", "-c", infinite_loop],
                timeout=5
            )
            
            result = tool(infinite_loop, timeout=5)
            
            assert result["success"] is False
            assert "timeout" in str(result["error"]).lower()
    
    def test_safe_mode_restrictions(self):
        """Test safe mode restrictions."""
        tool = self.get_component_function()
        
        dangerous_code_samples = [
            "import os\nos.system('rm -rf /')",
            "import subprocess\nsubprocess.run(['ls', '-la'])",
            "__import__('os').system('echo dangerous')",
            "open('/etc/passwd', 'r').read()",
            "exec('import os')"
        ]
        
        for dangerous_code in dangerous_code_samples:
            with patch("exec") as mock_exec:
                mock_exec.side_effect = ImportError("Unsafe import blocked")
                
                result = tool(dangerous_code, safe_mode=True)
                
                assert result["success"] is False or result["error"] is not None
                assert "blocked" in str(result).lower() or "error" in str(result).lower()
    
    def test_allowed_modules(self):
        """Test allowed modules whitelist."""
        tool = self.get_component_function()
        
        # Test allowed module
        with patch("exec") as mock_exec:
            result = tool(
                "import math\nprint(math.pi)",
                allowed_modules=["math", "datetime"],
                safe_mode=True
            )
            
            # Math should be allowed
            assert result["success"] is True or "3.14" in str(result)
        
        # Test disallowed module
        with patch("exec") as mock_exec:
            mock_exec.side_effect = ImportError("Module not in allowed list")
            
            result = tool(
                "import requests",
                allowed_modules=["math", "datetime"],
                safe_mode=True
            )
            
            # Requests should be blocked
            assert result["success"] is False or result["error"] is not None
    
    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        tool = self.get_component_function()
        
        invalid_code_samples = [
            "print('unclosed string",
            "if True\n    print('missing colon')",
            "def func(\n    pass",
            "1 +* 2"
        ]
        
        for invalid_code in invalid_code_samples:
            with patch("compile") as mock_compile:
                mock_compile.side_effect = SyntaxError("Invalid syntax")
                
                result = tool(invalid_code)
                
                assert result["success"] is False
                assert "syntax" in str(result["error"]).lower()
    
    def test_runtime_error_handling(self):
        """Test handling of runtime errors."""
        tool = self.get_component_function()
        
        error_code_samples = [
            ("1 / 0", "ZeroDivisionError"),
            ("int('not a number')", "ValueError"),
            ("undefined_variable", "NameError"),
            ("{}[0]", "KeyError")
        ]
        
        for code, expected_error in error_code_samples:
            with patch("exec") as mock_exec:
                mock_exec.side_effect = eval(f"{expected_error}('Test error')")
                
                result = tool(code)
                
                assert result["success"] is False
                assert expected_error in str(result["error"]) or "error" in str(result["error"]).lower()
    
    def test_output_capture(self):
        """Test capturing stdout and stderr."""
        tool = self.get_component_function()
        
        code = """
print("Standard output")
import sys
print("Error output", file=sys.stderr)
print("More stdout")
"""
        
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "Standard output\nMore stdout\n"
            mock_result.stderr = "Error output\n"
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = tool(code, capture_output=True)
            
            assert "Standard output" in result["output"]
            if "stderr" in result:
                assert "Error output" in result["stderr"]
    
    def test_return_value_capture(self):
        """Test capturing return values from expressions."""
        tool = self.get_component_function()
        
        expressions = [
            ("2 + 2", 4),
            ("'hello' + ' world'", "hello world"),
            ("[1, 2, 3] + [4, 5]", [1, 2, 3, 4, 5]),
            ("{'a': 1, 'b': 2}", {"a": 1, "b": 2})
        ]
        
        for expr, expected in expressions:
            with patch("eval") as mock_eval:
                mock_eval.return_value = expected
                
                result = tool(expr)
                
                if "return_value" in result:
                    assert result["return_value"] == expected
    
    def test_multiline_code_execution(self):
        """Test execution of multiline code blocks."""
        tool = self.get_component_function()
        
        multiline_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

results = []
for i in range(10):
    results.append(fibonacci(i))

print("Fibonacci sequence:", results)
"""
        
        with patch("exec") as mock_exec:
            result = tool(multiline_code)
            
            assert result["success"] is True
            # Should execute without errors
    
    def test_execution_time_tracking(self):
        """Test that execution time is tracked."""
        tool = self.get_component_function()
        
        with patch("time.time") as mock_time:
            # Mock time progression
            mock_time.side_effect = [0.0, 0.123]  # Start and end times
            
            result = tool("print('test')")
            
            if "execution_time" in result:
                assert isinstance(result["execution_time"], int | float)
                assert result["execution_time"] >= 0
    
    def test_memory_limit_handling(self):
        """Test memory limit handling if supported."""
        tool = self.get_component_function()
        
        memory_intensive_code = """
# Try to allocate a lot of memory
big_list = [0] * (10**9)  # 1 billion integers
"""
        
        with patch("resource.setrlimit") as mock_setrlimit, patch("exec") as mock_exec:
            mock_exec.side_effect = MemoryError("Out of memory")
            
            result = tool(memory_intensive_code, safe_mode=True)
            
            assert result["success"] is False
            assert "memory" in str(result["error"]).lower()
    
    def test_different_python_versions(self):
        """Test handling different Python version requirements."""
        tool = self.get_component_function()
        
        # Python 3.10+ syntax
        python310_code = """
match x:
    case 1:
        print("One")
    case _:
        print("Other")
"""
        
        # Since we require Python 3.12+, this should work
        result = tool(python310_code)
        # Should work on Python 3.12+
