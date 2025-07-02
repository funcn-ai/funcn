"""Test suite for code_interpreter_tool following best practices."""

import asyncio
import json
import pytest
import sys
import tempfile
from datetime import datetime

# Import the actual tool functions and models
from packages.funcn_registry.components.tools.code_interpreter.tool import (
    CodeExecutionResult,
    execute_code,
    execute_code_with_timeout,
    execute_directly,
    execute_in_subprocess,
    validate_code,
)
from pathlib import Path
from tests.utils import BaseToolTest
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch


class TestCodeInterpreterTool(BaseToolTest):
    """Test code_interpreter_tool component."""
    
    component_name = "code_interpreter_tool"
    component_path = Path("packages/funcn_registry/components/tools/code_interpreter")
    
    def get_component_function(self):
        """Import the tool function."""
        return execute_code
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        # Note: These are async function inputs
        return []
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        # This is an async tool, validation happens in async tests
        pass
    
    @pytest.mark.asyncio
    async def test_basic_code_execution(self):
        """Test basic Python code execution."""
        code = "print('Hello, World!')"
        result = await execute_code(code, timeout_seconds=5, use_subprocess=False)
        
        assert result.success is True
        assert result.output == "Hello, World!\n"
        assert result.error is None
        assert result.execution_time > 0
    
    @pytest.mark.asyncio
    async def test_variable_capture(self):
        """Test capturing variables from executed code."""
        code = """
x = 10
y = 20
result = x + y
data = {"key": "value", "count": result}
_private = "should not capture"
"""
        result = await execute_code(code, capture_variables=True, use_subprocess=False)
        
        assert result.success is True
        assert "x" in result.variables
        assert result.variables["x"] == 10
        assert result.variables["y"] == 20
        assert result.variables["result"] == 30
        assert result.variables["data"] == {"key": "value", "count": 30}
        assert "_private" not in result.variables
    
    @pytest.mark.asyncio
    async def test_output_capture(self):
        """Test capturing stdout output."""
        code = """
print("Line 1")
print("Line 2")
for i in range(3):
    print(f"Number: {i}")
"""
        result = await execute_code(code, use_subprocess=False)
        
        assert result.success is True
        assert "Line 1" in result.output
        assert "Line 2" in result.output
        assert "Number: 0" in result.output
        assert "Number: 1" in result.output
        assert "Number: 2" in result.output
    
    @pytest.mark.asyncio
    async def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        invalid_codes = [
            "print('unclosed string",
            "if True\n    print('missing colon')",
            "def func(\n    pass",
            "1 +* 2",
            "for i in range(10)\n    print(i)",
        ]
        
        for code in invalid_codes:
            result = await execute_code(code, use_subprocess=False)
            assert result.success is False
            assert result.error is not None
            assert "Syntax error" in result.error or "SyntaxError" in result.error
    
    @pytest.mark.asyncio
    async def test_runtime_error_handling(self):
        """Test handling of runtime errors."""
        error_codes = [
            ("1 / 0", "ZeroDivisionError"),
            ("int('not a number')", "ValueError"),
            ("undefined_variable", "NameError"),
            ("{}['missing_key']", "KeyError"),
            ("[1,2,3][10]", "IndexError"),
        ]
        
        for code, expected_error in error_codes:
            result = await execute_code(code, use_subprocess=False)
            assert result.success is False
            assert result.error is not None
            assert expected_error in result.error
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test code execution timeout."""
        infinite_loop = """
count = 0
while True:
    count += 1
    if count > 1000000:
        count = 0
"""
        
        result = await execute_code(infinite_loop, timeout_seconds=1, use_subprocess=False)
        
        assert result.success is False
        assert result.error is not None
        assert "timed out" in result.error
        assert result.execution_time >= 1
    
    @pytest.mark.asyncio
    async def test_subprocess_execution(self):
        """Test code execution in subprocess."""
        code = """
import math
print(f"Pi value: {math.pi}")
result = 42
"""
        
        result = await execute_code(code, use_subprocess=True, capture_variables=True)
        
        assert result.success is True
        assert "Pi value:" in result.output
        assert result.variables["result"] == 42
    
    @pytest.mark.asyncio
    async def test_module_restrictions(self):
        """Test module import restrictions in subprocess mode."""
        # Test allowed module
        allowed_code = """
import math
print(f"Pi: {math.pi}")
import datetime
print(f"Now: {datetime.datetime.now()}")
"""
        
        result = await execute_code(allowed_code, use_subprocess=True)
        assert result.success is True
        assert "Pi:" in result.output
        assert "Now:" in result.output
        
        # Test disallowed module
        disallowed_codes = [
            "import os\nprint(os.listdir())",
            "import subprocess\nsubprocess.run(['ls'])",
            "import socket\nsocket.gethostname()",
            "__import__('os').system('echo test')",
        ]
        
        for code in disallowed_codes:
            result = await execute_code(code, use_subprocess=True)
            assert result.success is False
            assert result.error is not None
            assert "not allowed" in result.error or "ImportError" in result.error
    
    @pytest.mark.asyncio
    async def test_custom_allowed_modules(self):
        """Test custom allowed modules list."""
        # Test code that uses only math
        math_code = """
import math
print(f"Square root of 16: {math.sqrt(16)}")
print(f"Pi value: {math.pi}")
"""
        # Restrict to only math module
        result = await execute_code(math_code, use_subprocess=True, allowed_modules=["math"])
        assert result.success is True
        assert "Square root of 16: 4.0" in result.output
        assert "Pi value:" in result.output
        
        # Try to use non-allowed module
        json_code = """
import json
data = {"test": 123}
print(json.dumps(data))
"""
        result = await execute_code(json_code, use_subprocess=True, allowed_modules=["math"])
        assert result.success is False
        assert "not allowed" in result.error
        
        # Test with multiple allowed modules
        multi_code = """
import math
import json
data = {"pi": math.pi, "sqrt": math.sqrt(25)}
print(json.dumps(data))
"""
        result = await execute_code(multi_code, use_subprocess=True, allowed_modules=["math", "json"])
        assert result.success is True
        assert "pi" in result.output
        assert "sqrt" in result.output
    
    @pytest.mark.asyncio
    async def test_multiline_code_execution(self):
        """Test execution of multiline code blocks."""
        code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

# Test the function
test_numbers = [1, 2, 3, 4, 5]
result = calculate_sum(test_numbers)
print(f"Sum of {test_numbers} = {result}")

# Define a class
class Counter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1
        return self.count

counter = Counter()
for _ in range(5):
    counter.increment()

print(f"Final count: {counter.count}")

# List comprehension
squares = [x**2 for x in range(10)]
print(f"Squares: {squares}")
"""
        
        result = await execute_code(code, capture_variables=True, use_subprocess=False)
        
        assert result.success is True
        assert "Sum of [1, 2, 3, 4, 5] = 15" in result.output
        assert "Final count: 5" in result.output
        assert "Squares: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]" in result.output
        assert "squares" in result.variables
        assert result.variables["squares"] == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    
    @pytest.mark.asyncio
    async def test_validate_code_function(self):
        """Test the validate_code function."""
        # Valid code
        valid_codes = [
            "print('hello')",
            "x = 1 + 2",
            "def func():\n    pass",
            "class Test:\n    pass",
            "[i**2 for i in range(10)]",
        ]
        
        for code in valid_codes:
            is_valid, error = validate_code(code)
            assert is_valid is True
            assert error is None
        
        # Invalid code
        invalid_codes = [
            ("print('unclosed", "unterminated string"),
            ("if True\n    print('test')", "invalid syntax"),
            ("def func(:\n    pass", "invalid syntax"),
            ("1 +* 2", "invalid syntax"),
        ]
        
        for code, expected_msg in invalid_codes:
            is_valid, error = validate_code(code)
            assert is_valid is False
            assert error is not None
    
    @pytest.mark.asyncio
    async def test_execute_code_with_timeout(self):
        """Test execute_code_with_timeout function."""
        # Normal execution
        code = "print('Test output')"
        result = await execute_code_with_timeout(code, timeout_seconds=2)
        
        assert result.success is True
        assert "Test output" in result.output
        
        # Test output truncation
        long_output_code = """
for i in range(1000):
    print(f"Line {i}: " + "x" * 100)
"""
        
        result = await execute_code_with_timeout(long_output_code, timeout_seconds=5, max_output_length=500)
        
        assert result.success is True
        assert len(result.output) <= 1200  # Some buffer for truncation message
        assert "output truncated" in result.output or len(result.output) <= 500
    
    @pytest.mark.asyncio
    async def test_complex_data_structures(self):
        """Test handling of complex data structures in variables."""
        code = """
import json
from collections import defaultdict, Counter
from datetime import datetime, date

# Various data structures
simple_list = [1, 2, 3, 4, 5]
nested_dict = {
    "level1": {
        "level2": {
            "data": [1, 2, 3]
        }
    }
}

# Collections
counter = Counter(['a', 'b', 'c', 'a', 'b', 'a'])
dd = defaultdict(list)
dd['key1'].append(1)
dd['key2'].append(2)

# Date objects (not JSON serializable)
now = datetime.now()
today = date.today()

# Custom class
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

point = Point(10, 20)
"""
        
        result = await execute_code(code, capture_variables=True, use_subprocess=False)
        
        assert result.success is True
        assert result.variables["simple_list"] == [1, 2, 3, 4, 5]
        assert result.variables["nested_dict"]["level1"]["level2"]["data"] == [1, 2, 3]
        # Non-serializable objects should be converted to strings
        assert isinstance(result.variables["now"], str)
        assert isinstance(result.variables["today"], str)
        assert isinstance(result.variables["point"], str)
        assert "Point(10, 20)" in result.variables["point"]
    
    @pytest.mark.asyncio
    async def test_exception_handling_details(self):
        """Test detailed exception handling."""
        code = """
x = [1, 2, 3]
y = x[10]  # IndexError
"""
        
        result = await execute_code(code, use_subprocess=False)
        
        assert result.success is False
        assert "IndexError" in result.error
        assert "list index out of range" in result.error
    
    @pytest.mark.asyncio
    async def test_execution_time_tracking(self):
        """Test that execution time is properly tracked."""
        # Quick execution
        quick_code = "x = 1 + 1"
        result = await execute_code(quick_code, use_subprocess=False)
        assert result.success is True
        assert result.execution_time > 0
        assert result.execution_time < 1  # Should be very fast
        
        # Computationally intensive execution
        intensive_code = """
# Compute something intensive
result = 0
for i in range(1000000):
    result += i
print("Done computing")
"""
        result = await execute_code(intensive_code, use_subprocess=False)
        assert result.success is True
        assert result.execution_time > 0
        assert "Done computing" in result.output
    
    @pytest.mark.asyncio
    async def test_math_and_scientific_operations(self):
        """Test mathematical and scientific computing operations."""
        code = """
import math
import statistics
import fractions
import decimal

# Math operations
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
mean = statistics.mean(numbers)
stdev = statistics.stdev(numbers)
print(f"Mean: {mean}, StdDev: {stdev:.2f}")

# Trigonometry
angle = math.pi / 4
sin_val = math.sin(angle)
cos_val = math.cos(angle)
print(f"sin(π/4) = {sin_val:.4f}, cos(π/4) = {cos_val:.4f}")

# Fractions
frac1 = fractions.Fraction(1, 3)
frac2 = fractions.Fraction(1, 6)
result = frac1 + frac2
print(f"1/3 + 1/6 = {result}")

# Decimal precision
decimal.getcontext().prec = 10
d1 = decimal.Decimal('1.1')
d2 = decimal.Decimal('2.2')
print(f"Decimal sum: {d1 + d2}")
"""
        
        result = await execute_code(code, capture_variables=True, use_subprocess=False)
        
        assert result.success is True
        assert "Mean: 5.5" in result.output
        assert "sin(π/4) = 0.7071" in result.output
        assert "1/3 + 1/6 = 1/2" in result.output
        assert "Decimal sum: 3.3" in result.output
    
    @pytest.mark.asyncio
    async def test_string_and_regex_operations(self):
        """Test string manipulation and regex operations."""
        code = """
import re
import string

# String operations
text = "Hello, World! This is a Test String."
print(f"Original: {text}")
print(f"Lower: {text.lower()}")
print(f"Words: {text.split()}")

# Regex operations
pattern = r'\\b\\w+@\\w+\\.\\w+\\b'
test_text = "Contact us at support@example.com or sales@test.org"
emails = re.findall(pattern, test_text)
print(f"Found emails: {emails}")

# String templates
template = string.Template("Hello $name, your balance is $$${amount}")
result = template.substitute(name="Alice", amount="100.50")
print(result)

# Simple string manipulation
chars = string.ascii_lowercase
print(f"Lowercase letters: {chars[:10]}")
"""
        
        result = await execute_code(code, use_subprocess=False)
        
        assert result.success is True
        assert "Lower: hello, world!" in result.output
        assert "Found emails: ['support@example.com', 'sales@test.org']" in result.output
        assert "Hello Alice, your balance is $100.50" in result.output
        assert "Lowercase letters: abcdefghij" in result.output
    
    @pytest.mark.asyncio
    async def test_json_and_data_handling(self):
        """Test JSON and data structure handling."""
        code = """
import json
from collections import OrderedDict, namedtuple

# JSON operations
data = {
    "name": "Test User",
    "age": 30,
    "skills": ["Python", "JavaScript", "SQL"],
    "active": True
}

json_str = json.dumps(data, indent=2)
print("JSON output:")
print(json_str)

# Parse JSON
parsed = json.loads(json_str)
print(f"Parsed name: {parsed['name']}")

# Named tuples
Person = namedtuple('Person', ['name', 'age', 'city'])
person = Person("Bob", 25, "New York")
print(f"Person: {person.name} is {person.age} from {person.city}")

# OrderedDict
od = OrderedDict()
od['first'] = 1
od['second'] = 2
od['third'] = 3
print(f"OrderedDict keys: {list(od.keys())}")
"""
        
        result = await execute_code(code, capture_variables=True, use_subprocess=False)
        
        assert result.success is True
        assert "JSON output:" in result.output
        assert '"name": "Test User"' in result.output
        assert "Parsed name: Test User" in result.output
        assert "Person: Bob is 25 from New York" in result.output
        assert "OrderedDict keys: ['first', 'second', 'third']" in result.output
    
    @pytest.mark.asyncio
    async def test_error_recovery_scenarios(self):
        """Test various error recovery scenarios."""
        # Test with try-except blocks
        code = """
results = []

# Division by zero with recovery
try:
    x = 1 / 0
except ZeroDivisionError:
    results.append("Caught division by zero")
    x = float('inf')

# Type error with recovery
try:
    y = "string" + 123
except TypeError:
    results.append("Caught type error")
    y = "string" + str(123)

# Success after errors
results.append(f"x = {x}, y = {y}")

for r in results:
    print(r)
"""
        
        result = await execute_code(code, capture_variables=True, use_subprocess=False)
        
        assert result.success is True
        assert "Caught division by zero" in result.output
        assert "Caught type error" in result.output
        assert "x = inf, y = string123" in result.output
        assert result.variables["results"] == [
            "Caught division by zero",
            "Caught type error", 
            "x = inf, y = string123"
        ]
    
    @pytest.mark.asyncio
    async def test_generator_and_iterator_support(self):
        """Test generators and iterators."""
        code = """
# Generator function
def fibonacci_gen(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Use generator
fib_list = list(fibonacci_gen(10))
print(f"Fibonacci: {fib_list}")

# Generator expression
squares = (x**2 for x in range(5))
squares_list = list(squares)
print(f"Squares: {squares_list}")

# Custom iterator
class Counter:
    def __init__(self, max_count):
        self.max_count = max_count
        self.count = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.count < self.max_count:
            self.count += 1
            return self.count
        raise StopIteration

# Use custom iterator
counter_list = list(Counter(5))
print(f"Counter: {counter_list}")
"""
        
        result = await execute_code(code, capture_variables=True, use_subprocess=False)
        
        assert result.success is True
        assert "Fibonacci: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]" in result.output
        assert "Squares: [0, 1, 4, 9, 16]" in result.output
        assert "Counter: [1, 2, 3, 4, 5]" in result.output
    
    @pytest.mark.asyncio
    async def test_large_output_handling(self):
        """Test handling of large outputs."""
        code = """
# Generate large output
for i in range(100):
    print(f"Line {i}: " + "=" * 50)
    
print("\\n" + "Final line after many outputs")
"""
        
        # Test with output limit
        result = await execute_code_with_timeout(code, timeout_seconds=5, max_output_length=1000)
        
        assert result.success is True
        assert len(result.output) <= 1200  # Some buffer for truncation message
        assert "output truncated" in result.output or len(result.output) <= 1000
        
        # Test without limit
        result = await execute_code(code, use_subprocess=False)
        assert result.success is True
        assert "Line 99:" in result.output
        assert "Final line after many outputs" in result.output
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self):
        """Test concurrent execution of multiple code blocks."""
        codes = [
            "result = sum(range(100))",
            "result = len([i**2 for i in range(50)])",
            "result = '-'.join(['a', 'b', 'c'])",
        ]
        
        # Run multiple executions concurrently
        tasks = [execute_code(code, capture_variables=True, use_subprocess=False) for code in codes]
        results = await asyncio.gather(*tasks)
        
        assert all(r.success for r in results)
        assert results[0].variables["result"] == 4950  # sum(range(100))
        assert results[1].variables["result"] == 50    # len of list
        assert results[2].variables["result"] == "a-b-c"
    
    @pytest.mark.asyncio
    async def test_memory_intensive_operations(self):
        """Test handling of memory-intensive operations."""
        code = """
# Create a large list (but not too large to cause issues)
big_list = list(range(100000))
print(f"Created list with {len(big_list)} elements")

# Some operations on it
sum_val = sum(big_list)
max_val = max(big_list)
print(f"Sum: {sum_val}, Max: {max_val}")

# Clean up
del big_list
print("Cleaned up memory")
"""
        
        result = await execute_code(code, use_subprocess=False)
        
        assert result.success is True
        assert "Created list with 100000 elements" in result.output
        assert "Sum: 4999950000" in result.output
        assert "Max: 99999" in result.output
        assert "Cleaned up memory" in result.output
    
    @pytest.mark.asyncio
    async def test_encoding_and_unicode(self):
        """Test Unicode and encoding support."""
        code = """
# Unicode strings
text = "Hello, 世界! 🌍 Привет мир"
print(f"Unicode text: {text}")
print(f"Length: {len(text)}")

# Encoding operations
encoded = text.encode('utf-8')
print(f"UTF-8 bytes: {len(encoded)} bytes")

# String with emojis
emojis = "Python 🐍 is awesome! 🎉🚀"
print(f"With emojis: {emojis}")

# Different scripts
scripts = {
    "Latin": "Hello",
    "Chinese": "你好",
    "Arabic": "مرحبا",
    "Russian": "Привет",
    "Japanese": "こんにちは"
}

for script, greeting in scripts.items():
    print(f"{script}: {greeting}")
"""
        
        result = await execute_code(code, use_subprocess=False)
        
        assert result.success is True
        assert "Hello, 世界! 🌍 Привет мир" in result.output
        assert "Python 🐍 is awesome!" in result.output
        assert "Chinese: 你好" in result.output
        assert "Arabic: مرحبا" in result.output
    
    @pytest.mark.asyncio
    async def test_import_with_aliases(self):
        """Test imports with aliases."""
        code = """
import datetime as dt
import json as j
from collections import Counter as Cnt

# Use aliases
now = dt.datetime.now()
print(f"Current time: {now.strftime('%Y-%m-%d %H:%M')}")

data = {"test": 123}
json_str = j.dumps(data)
print(f"JSON: {json_str}")

counts = Cnt(['a', 'b', 'a', 'c', 'b', 'a'])
print(f"Counts: {dict(counts)}")
"""
        
        result = await execute_code(code, use_subprocess=False)
        
        assert result.success is True
        assert "Current time:" in result.output
        assert "JSON: {\"test\": 123}" in result.output or 'JSON: {"test": 123}' in result.output
        assert "Counts: {'a': 3, 'b': 2, 'c': 1}" in result.output
    
    @pytest.mark.asyncio
    async def test_context_managers(self):
        """Test context managers in code execution."""
        code = """
from io import StringIO
import contextlib

# Use StringIO as context manager
output = []
with StringIO("Line 1\\nLine 2\\nLine 3") as f:
    for line in f:
        output.append(line.strip())

print(f"Read lines: {output}")

# Custom context manager
@contextlib.contextmanager
def custom_context(name):
    print(f"Entering {name}")
    yield name.upper()
    print(f"Exiting {name}")

# Use custom context manager
with custom_context("test") as value:
    print(f"Inside context: {value}")

print("Done with contexts")
"""
        
        result = await execute_code(code, use_subprocess=False)
        
        assert result.success is True
        assert "Read lines: ['Line 1', 'Line 2', 'Line 3']" in result.output
        assert "Entering test" in result.output
        assert "Inside context: TEST" in result.output
        assert "Exiting test" in result.output
    
    @pytest.mark.asyncio 
    async def test_edge_cases(self):
        """Test various edge cases."""
        # Empty code
        result = await execute_code("", use_subprocess=False)
        assert result.success is True
        assert result.output == ""
        
        # Only comments
        result = await execute_code("# Just a comment\n# Another comment", use_subprocess=False)
        assert result.success is True
        assert result.output == ""
        
        # Only whitespace
        result = await execute_code("   \n\t\n   ", use_subprocess=False)
        assert result.success is True
        
        # Single expression
        result = await execute_code("42", capture_variables=False, use_subprocess=False)
        assert result.success is True
        
        # Pass statement
        result = await execute_code("pass", use_subprocess=False)
        assert result.success is True
