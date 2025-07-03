"""Test suite for json_search_tool following best practices."""

import asyncio
import json
import pytest
import tempfile

# Import the actual tool functions
from packages.sygaldry_registry.components.tools.json_search.tool import (
    JSONSearchArgs,
    JSONSearchResponse,
    JSONSearchResult,
    search_json_content,
)
from pathlib import Path
from tests.utils import BaseToolTest


class TestJSONSearchTool(BaseToolTest):
    """Test json_search_tool component."""

    component_name = "json_search_tool"
    component_path = Path("packages/sygaldry_registry/components/tools/json_search")

    def get_component_function(self):
        """Import the tool function."""
        return search_json_content

    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            JSONSearchArgs(
                json_data={"users": [{"name": "John"}, {"name": "Jane"}]},
                query="John",
                search_keys=False,
                search_values=True
            ),
            JSONSearchArgs(
                json_data={"config": {"host": "localhost", "port": 8080}},
                query="localhost",
                json_path="$.config",
                case_sensitive=False
            ),
            JSONSearchArgs(
                json_data={"nested": {"deep": {"value": "api_key_123"}}},
                query="api_key",
                max_results=3
            )
        ]

    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, JSONSearchResponse)
        assert isinstance(output.results, list)
        assert output.total_elements >= 0
        assert output.search_scope is not None

        for result in output.results:
            assert isinstance(result, JSONSearchResult)
            assert hasattr(result, 'value')
            assert hasattr(result, 'match_score')
            assert 0 <= result.match_score <= 100

    @pytest.mark.asyncio
    async def test_jsonpath_expression_search(self):
        """Test searching with JSONPath expressions."""
        test_data = {
            "users": [
                {"id": 1, "name": "Alice", "role": "admin"},
                {"id": 2, "name": "Bob", "role": "user"},
                {"id": 3, "name": "Charlie", "role": "user"}
            ],
            "settings": {
                "theme": "dark",
                "notifications": {"email": True, "sms": False}
            }
        }

        # Search only in users array
        args = JSONSearchArgs(
            json_data=test_data,
            query="admin",
            json_path="$.users[*]"
        )
        response = await search_json_content(args)

        assert response.error is None
        assert len(response.results) >= 1
        # Should only find matches within users array
        for result in response.results:
            assert "users" in result.path

    @pytest.mark.asyncio
    async def test_search_keys_vs_values(self):
        """Test searching in keys only, values only, or both."""
        test_data = {
            "name": "test_name",
            "test_key": "different_value",
            "another": "name_in_value"
        }

        # Search keys only
        args_keys = JSONSearchArgs(
            json_data=test_data,
            query="name",
            search_keys=True,
            search_values=False
        )
        key_response = await search_json_content(args_keys)

        # Search values only (default behavior)
        args_values = JSONSearchArgs(
            json_data=test_data,
            query="name",
            search_keys=False
        )
        value_response = await search_json_content(args_values)

        # Search both
        args_both = JSONSearchArgs(
            json_data=test_data,
            query="name",
            search_keys=True
        )
        both_response = await search_json_content(args_both)

        # Both should find more than either keys or values alone
        assert len(both_response.results) >= max(len(key_response.results), len(value_response.results))

    @pytest.mark.asyncio
    async def test_nested_json_search(self):
        """Test searching in deeply nested JSON structures."""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "deep_value": "found_me",
                            "deep_key": "test"
                        }
                    }
                }
            }
        }

        # Search without depth limit
        args = JSONSearchArgs(
            json_data=nested_data,
            query="found_me"
        )
        response = await search_json_content(args)

        # Should find the deep value
        assert response.error is None
        assert len(response.results) > 0
        assert response.results[0].value == "found_me"

    @pytest.mark.asyncio
    async def test_array_search(self):
        """Test searching within JSON arrays."""
        array_data = {
            "products": [
                {"id": 1, "name": "Laptop", "price": 999},
                {"id": 2, "name": "Mouse", "price": 29},
                {"id": 3, "name": "Keyboard", "price": 79}
            ],
            "tags": ["electronics", "computers", "accessories"]
        }

        # Search in array of objects
        args = JSONSearchArgs(
            json_data=array_data,
            query="Laptop"
        )
        response = await search_json_content(args)
        assert len(response.results) > 0

        # Search in simple array
        args = JSONSearchArgs(
            json_data=array_data,
            query="computers"
        )
        response = await search_json_content(args)
        assert len(response.results) > 0

    @pytest.mark.asyncio
    async def test_case_sensitivity(self):
        """Test case-sensitive vs case-insensitive search."""
        test_data = {
            "Name": "John DOE",
            "name": "jane doe",
            "NAME": "JACK DOE"
        }

        # Case-insensitive search (default)
        args_insensitive = JSONSearchArgs(
            json_data=test_data,
            query="name",
            case_sensitive=False,
            search_keys=True
        )
        response_insensitive = await search_json_content(args_insensitive)

        # Case-sensitive search
        args_sensitive = JSONSearchArgs(
            json_data=test_data,
            query="name",
            case_sensitive=True,
            search_keys=True
        )
        response_sensitive = await search_json_content(args_sensitive)

        # Case-insensitive should find more matches
        assert len(response_insensitive.results) > len(response_sensitive.results)

    @pytest.mark.asyncio
    async def test_numeric_and_boolean_search(self):
        """Test searching for numeric and boolean values."""
        test_data = {
            "count": 42,
            "price": 42.99,
            "active": True,
            "disabled": False,
            "config": {
                "port": 8080,
                "debug": True
            }
        }

        # Search for integer
        args = JSONSearchArgs(
            json_data=test_data,
            query="42"
        )
        response = await search_json_content(args)
        assert len(response.results) >= 1

        # Search for boolean
        args = JSONSearchArgs(
            json_data=test_data,
            query="true",
            case_sensitive=False
        )
        response = await search_json_content(args)
        assert len(response.results) >= 2  # active and debug

        # Search for port number
        args = JSONSearchArgs(
            json_data=test_data,
            query="8080"
        )
        response = await search_json_content(args)
        assert len(response.results) >= 1

    @pytest.mark.asyncio
    async def test_null_value_handling(self):
        """Test handling of null values in JSON."""
        test_data = {
            "name": "Test",
            "description": None,
            "metadata": {
                "created": "2024-01-01",
                "updated": None,
                "tags": ["tag1", None, "tag2"]
            }
        }

        # Search for a key that has null value
        args = JSONSearchArgs(
            json_data=test_data,
            query="description",
            search_keys=True
        )
        response = await search_json_content(args)

        # Should find the key even though value is null
        assert response.error is None
        assert len(response.results) >= 1

        # Search for non-null values
        args = JSONSearchArgs(
            json_data=test_data,
            query="2024"
        )
        response = await search_json_content(args)
        assert len(response.results) >= 1

    @pytest.mark.asyncio
    async def test_special_characters_handling(self):
        """Test handling of special characters in search."""
        test_data = {
            "email": "user@example.com",
            "regex": "^[a-z]+$",
            "path": "/home/user/docs",
            "url": "https://example.com/api?key=value&foo=bar"
        }

        special_queries = ["@example.com", "^[a-z]+$", "/home/user", "?key=value"]

        for query in special_queries:
            args = JSONSearchArgs(
                json_data=test_data,
                query=query
            )
            response = await search_json_content(args)
            assert response.error is None
            assert isinstance(response.results, list)

    @pytest.mark.asyncio
    async def test_file_search(self, tmp_path):
        """Test searching in JSON files."""
        # Create test JSON file
        test_data = {
            "app": {
                "name": "TestApp",
                "version": "1.0.0",
                "features": ["auth", "api", "database"]
            }
        }

        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(test_data))

        # Search in file
        args = JSONSearchArgs(
            file_path=str(json_file),
            query="TestApp"
        )
        response = await search_json_content(args)

        assert response.error is None
        assert len(response.results) > 0
        assert response.results[0].value == "TestApp"

    @pytest.mark.asyncio
    async def test_invalid_json_handling(self):
        """Test handling of invalid JSON files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json: no quotes }")
            temp_path = f.name

        try:
            args = JSONSearchArgs(
                file_path=temp_path,
                query="test"
            )
            response = await search_json_content(args)

            # Should handle gracefully
            assert response.error is not None
            assert "Invalid JSON format" in response.error
            assert response.results == []
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_empty_json_handling(self):
        """Test handling of empty JSON data."""
        # Test empty dictionary
        args = JSONSearchArgs(
            json_data={},
            query="test"
        )
        response = await search_json_content(args)
        assert response.error is None
        assert response.results == []

        # Test with file containing empty JSON structures
        empty_cases = [
            "{}",
            "[]",
            "null"
        ]

        for empty_json_str in empty_cases:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(empty_json_str)
                temp_path = f.name

            try:
                args = JSONSearchArgs(
                    file_path=temp_path,
                    query="test"
                )
                response = await search_json_content(args)
                assert response.error is None
                assert response.results == []
            finally:
                Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_fuzzy_matching(self):
        """Test fuzzy matching functionality."""
        test_data = {
            "users": [
                {"name": "Jonathan Smith"},
                {"name": "John Doe"},
                {"name": "Jane Johnson"}
            ]
        }

        # Fuzzy search with lower threshold to catch more matches
        args = JSONSearchArgs(
            json_data=test_data,
            query="John",
            fuzzy_threshold=60,
            exact_match=False
        )
        response = await search_json_content(args)

        # Should find at least John Doe
        assert len(response.results) >= 1
        assert any("John Doe" in str(r.value) for r in response.results)

        # Exact match should find only exact substring matches
        args_exact = JSONSearchArgs(
            json_data=test_data,
            query="John",
            exact_match=True
        )
        response_exact = await search_json_content(args_exact)

        # Should find John Doe and Jane Johnson (both contain "John")
        assert len(response_exact.results) >= 1

        # Test with a query that has no exact matches but fuzzy matches
        args_fuzzy_only = JSONSearchArgs(
            json_data=test_data,
            query="Jhon",  # Typo of John
            fuzzy_threshold=75,
            exact_match=False
        )
        response_fuzzy_only = await search_json_content(args_fuzzy_only)

        # Should find fuzzy matches for the typo
        assert len(response_fuzzy_only.results) >= 1

    @pytest.mark.asyncio
    async def test_max_results_limit(self):
        """Test that max_results limits output."""
        test_data = {
            "items": [{"value": f"test_{i}"} for i in range(100)]
        }

        args = JSONSearchArgs(
            json_data=test_data,
            query="test",
            max_results=5
        )
        response = await search_json_content(args)

        assert len(response.results) <= 5
        assert response.total_elements > 5  # More elements were searched

    @pytest.mark.asyncio
    async def test_context_extraction(self):
        """Test that context is properly extracted."""
        test_data = {
            "user": {
                "id": 123,
                "name": "John Doe",
                "email": "john@example.com",
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        }

        args = JSONSearchArgs(
            json_data=test_data,
            query="john@example.com"
        )
        response = await search_json_content(args)

        assert len(response.results) > 0
        result = response.results[0]
        assert result.context is not None
        # Context should be the parent object containing email
        assert "id" in result.context
        assert "name" in result.context

    @pytest.mark.asyncio
    async def test_include_path_option(self):
        """Test include_path option."""
        test_data = {"test": {"nested": "value"}}

        # With path
        args_with_path = JSONSearchArgs(
            json_data=test_data,
            query="value",
            include_path=True
        )
        response_with_path = await search_json_content(args_with_path)

        # Without path
        args_without_path = JSONSearchArgs(
            json_data=test_data,
            query="value",
            include_path=False
        )
        response_without_path = await search_json_content(args_without_path)

        assert response_with_path.results[0].path != ""
        assert response_without_path.results[0].path == ""

    @pytest.mark.asyncio
    async def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        args = JSONSearchArgs(
            file_path="/nonexistent/path/file.json",
            query="test"
        )
        response = await search_json_content(args)

        assert response.error is not None
        assert "not found" in response.error
        assert response.results == []

    @pytest.mark.asyncio
    async def test_invalid_jsonpath(self):
        """Test handling of invalid JSONPath expressions."""
        test_data = {"test": "value"}

        args = JSONSearchArgs(
            json_data=test_data,
            query="test",
            json_path="$[invalid jsonpath"
        )
        response = await search_json_content(args)

        assert response.error is not None
        assert "Invalid JSONPath" in response.error

    @pytest.mark.asyncio
    async def test_mixed_type_values(self):
        """Test searching across mixed data types."""
        test_data = {
            "string": "test value",
            "number": 123,
            "float": 45.67,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"nested": "value"}
        }

        # Search for string representation of number
        args = JSONSearchArgs(
            json_data=test_data,
            query="123"
        )
        response = await search_json_content(args)
        assert len(response.results) >= 1

        # Search in nested structures
        args = JSONSearchArgs(
            json_data=test_data,
            query="nested",
            search_keys=True
        )
        response = await search_json_content(args)
        assert len(response.results) >= 1

    @pytest.mark.asyncio
    async def test_large_json_performance(self):
        """Test performance with moderately large JSON."""
        # Create a large JSON structure
        large_data = {
            f"key_{i}": {
                "name": f"Item {i}",
                "value": i,
                "description": f"Description for item {i}"
            }
            for i in range(500)
        }

        import time
        start_time = time.time()

        args = JSONSearchArgs(
            json_data=large_data,
            query="Item 250",
            max_results=10
        )
        response = await search_json_content(args)

        elapsed = time.time() - start_time

        # Should complete quickly
        assert elapsed < 2.0
        assert len(response.results) >= 1
        assert response.total_elements == 1500  # 500 objects * 3 fields each

    @pytest.mark.asyncio
    async def test_validation_error_no_input(self):
        """Test validation error when neither file_path nor json_data is provided."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            JSONSearchArgs(
                file_path=None,
                json_data=None,
                query="test"
            )
        assert "Either file_path or json_data must be provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_both_file_and_data_provided(self, tmp_path):
        """Test behavior when both file_path and json_data are provided."""
        # Create test file
        test_file_data = {"file": "content"}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(test_file_data))

        # Provide different data directly
        direct_data = {"direct": "data"}

        args = JSONSearchArgs(
            file_path=str(json_file),
            json_data=direct_data,
            query="content"
        )
        response = await search_json_content(args)

        # Should use file_path when both are provided
        assert response.error is None
        assert len(response.results) >= 1
        assert any("file" in str(r.context) for r in response.results if r.context)

    @pytest.mark.asyncio
    async def test_list_as_root_element(self):
        """Test searching when JSON root is a list."""
        # Since json_data expects dict, test with a list inside a dict
        test_data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Charlie"}
            ]
        }

        # Also test searching in a list at root using file
        list_data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(list_data, f)
            temp_path = f.name

        try:
            args = JSONSearchArgs(
                file_path=temp_path,
                query="Bob"
            )
            response = await search_json_content(args)

            assert response.error is None
            assert len(response.results) >= 1
            assert response.results[0].value == "Bob"
            assert "$[1]" in response.results[0].path
        finally:
            Path(temp_path).unlink()

        # Test dict with list
        args = JSONSearchArgs(
            json_data=test_data,
            query="Bob"
        )
        response = await search_json_content(args)

        assert response.error is None
        assert len(response.results) >= 1
        assert response.results[0].value == "Bob"

    @pytest.mark.asyncio
    async def test_complex_jsonpath_expressions(self):
        """Test various complex JSONPath expressions."""
        test_data = {
            "store": {
                "books": [
                    {"title": "Book 1", "price": 10.99, "category": "fiction"},
                    {"title": "Book 2", "price": 8.99, "category": "fiction"},
                    {"title": "Book 3", "price": 12.99, "category": "reference"}
                ],
                "bicycle": {"color": "red", "price": 19.95}
            }
        }

        # Test recursive descent
        args = JSONSearchArgs(
            json_data=test_data,
            query="fiction",
            json_path="$..category"
        )
        response = await search_json_content(args)
        assert len(response.results) == 2

        # Test array slice
        args = JSONSearchArgs(
            json_data=test_data,
            query="Book",
            json_path="$.store.books[0:2].title"
        )
        response = await search_json_content(args)
        assert len(response.results) == 2

        # Test wildcard - search for "19.95" which exists in bicycle price
        args = JSONSearchArgs(
            json_data=test_data,
            query="19.95",
            json_path="$.store.*.price"
        )
        response = await search_json_content(args)
        assert len(response.results) >= 1
        assert response.results[0].value == 19.95

    @pytest.mark.asyncio
    async def test_search_keys_with_nested_structures(self):
        """Test search_keys option with deeply nested key names."""
        test_data = {
            "user_profile": {
                "personal_info": {
                    "first_name": "John",
                    "last_name": "Doe"
                },
                "contact_info": {
                    "email_address": "john@example.com",
                    "phone_number": "555-1234"
                }
            },
            "system_config": {
                "email_settings": {
                    "smtp_server": "mail.example.com"
                }
            }
        }

        # Search for "email" in keys
        args = JSONSearchArgs(
            json_data=test_data,
            query="email",
            search_keys=True,
            search_values=False,
            fuzzy_threshold=70
        )
        response = await search_json_content(args)

        # Should find email_address and email_settings keys
        assert len(response.results) >= 2
        key_matches = [r.key for r in response.results if r.key]
        assert any("email" in k.lower() for k in key_matches)

    @pytest.mark.asyncio
    async def test_context_extraction_edge_cases(self):
        """Test context extraction in various edge cases."""
        # Test with value inside a list
        test_data = {
            "items": [
                "string_item",
                {"nested": "object"},
                ["nested", "list"]
            ]
        }

        args = JSONSearchArgs(
            json_data=test_data,
            query="string_item"
        )
        response = await search_json_content(args)

        assert len(response.results) >= 1
        result = response.results[0]
        assert result.context is not None
        # The context should be the root dict since that's the parent of 'items'
        assert "items" in result.context

        # Test with direct list as context
        test_data_list = ["item1", "item2", "target_item"]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data_list, f)
            temp_path = f.name

        try:
            args = JSONSearchArgs(
                file_path=temp_path,
                query="target_item"
            )
            response = await search_json_content(args)

            assert len(response.results) >= 1
            result = response.results[0]
            # For list at root, context might include special list handling
            assert result.context is not None
        finally:
            Path(temp_path).unlink()

        # Test with deeply nested structure
        deep_data = {"a": {"b": {"c": {"d": {"e": "target"}}}}}
        args = JSONSearchArgs(
            json_data=deep_data,
            query="target"
        )
        response = await search_json_content(args)

        assert len(response.results) >= 1
        assert response.results[0].context is not None
        # Context should be the 'd' dict containing 'e'
        assert "e" in response.results[0].context

    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters."""
        test_data = {
            "users": [
                {"name": "José García", "city": "São Paulo"},
                {"name": "李明", "city": "北京"},
                {"name": "Müller", "city": "München"},
                {"name": "test@#$%^&*()", "city": "Special City"}
            ]
        }

        # Test Unicode search
        unicode_queries = ["José", "李明", "München", "@#$%"]

        for query in unicode_queries:
            args = JSONSearchArgs(
                json_data=test_data,
                query=query
            )
            response = await search_json_content(args)
            assert response.error is None
            assert len(response.results) >= 1

    @pytest.mark.asyncio
    async def test_circular_reference_handling(self):
        """Test handling of circular references (should not cause infinite loop)."""
        # JSON can't serialize circular references, so test with a deep but non-circular structure
        # that could potentially cause issues in recursive algorithms
        test_data = {"level1": {}}
        current = test_data["level1"]

        # Create a very deep structure
        for i in range(100):
            current[f"level{i+2}"] = {}
            current = current[f"level{i+2}"]
        current["deep_value"] = "found_me"

        # This should handle deep recursion gracefully
        args = JSONSearchArgs(
            json_data=test_data,
            query="found_me"
        )

        # Should complete without stack overflow
        import time
        start = time.time()
        response = await search_json_content(args)
        elapsed = time.time() - start

        assert elapsed < 1.0  # Should complete quickly
        assert response.error is None
        assert len(response.results) >= 1
        assert response.results[0].value == "found_me"

    @pytest.mark.asyncio
    async def test_concurrent_searches(self):
        """Test concurrent search operations."""
        test_data = {
            f"section_{i}": {
                "title": f"Section {i}",
                "content": f"Content for section {i}",
                "tags": [f"tag_{j}" for j in range(5)]
            }
            for i in range(10)
        }

        # Create multiple search tasks
        search_queries = ["Section 5", "tag_3", "Content", "section_"]

        tasks = []
        for query in search_queries:
            args = JSONSearchArgs(
                json_data=test_data,
                query=query,
                search_keys=True
            )
            tasks.append(search_json_content(args))

        # Run concurrently
        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert all(r.error is None for r in results)
        assert all(len(r.results) > 0 for r in results)

    @pytest.mark.asyncio
    async def test_empty_string_search(self):
        """Test searching for empty strings."""
        test_data = {
            "field1": "",
            "field2": "not empty",
            "field3": None,
            "nested": {"empty": "", "full": "value"}
        }

        # Search for empty string with exact match
        args = JSONSearchArgs(
            json_data=test_data,
            query="",
            exact_match=True
        )
        response = await search_json_content(args)

        # Should find the empty string values
        assert response.error is None
        empty_values = [r.value for r in response.results if r.value == ""]
        assert len(empty_values) >= 2  # field1 and nested.empty

        # Test that searching for "empty" finds the word in non-empty strings
        args = JSONSearchArgs(
            json_data=test_data,
            query="empty",
            exact_match=False
        )
        response = await search_json_content(args)

        assert len(response.results) >= 1
        assert any("empty" in str(r.value) for r in response.results)

    @pytest.mark.asyncio
    async def test_scientific_notation_numbers(self):
        """Test searching in scientific notation numbers."""
        test_data = {
            "measurements": {
                "distance": 1.23e-10,
                "mass": 5.67e+23,
                "regular": 123.45
            }
        }

        # Search for scientific notation
        args = JSONSearchArgs(
            json_data=test_data,
            query="e-10"
        )
        response = await search_json_content(args)

        assert len(response.results) >= 1
        assert any(r.value == 1.23e-10 for r in response.results)

    @pytest.mark.asyncio
    async def test_very_long_strings(self):
        """Test searching in very long string values."""
        long_text = "Lorem ipsum " * 1000  # Very long text
        test_data = {
            "document": {
                "title": "Test Document",
                "content": long_text + " UNIQUE_MARKER " + long_text,
                "summary": "Short summary"
            }
        }

        args = JSONSearchArgs(
            json_data=test_data,
            query="UNIQUE_MARKER",
            max_results=5
        )
        response = await search_json_content(args)

        assert response.error is None
        assert len(response.results) >= 1
        assert "UNIQUE_MARKER" in str(response.results[0].value)

    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have proper docstrings."""
        assert search_json_content.__doc__ is not None
        assert len(search_json_content.__doc__) > 20
