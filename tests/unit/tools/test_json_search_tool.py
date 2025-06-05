"""Test suite for json_search_tool following best practices."""

import json
import pytest
from pathlib import Path
from tests.fixtures import TestDataFactory
from tests.utils import BaseToolTest
from unittest.mock import Mock, mock_open, patch


class TestJSONSearchTool(BaseToolTest):
    """Test json_search_tool component."""
    
    component_name = "json_search_tool"
    component_path = Path("packages/funcn_registry/components/tools/json_search_tool")
    
    def get_component_function(self):
        """Import the tool function."""
        # Would import: from tools.json_search_tool import search_json
        def mock_search_json(
            json_path: str | Path,
            query: str,
            json_path_expr: str | None = None,
            case_sensitive: bool = False,
            search_keys: bool = True,
            search_values: bool = True,
            max_depth: int | None = None
        ) -> list[dict[str, any]]:
            """Mock JSON search tool."""
            return [
                {
                    "path": "$.users[0].name",
                    "key": "name",
                    "value": "John Doe",
                    "match_type": "value",
                    "context": {"id": 1, "name": "John Doe", "email": "john@example.com"}
                },
                {
                    "path": "$.config.database.name",
                    "key": "name", 
                    "value": "production_db",
                    "match_type": "value",
                    "context": {"host": "localhost", "name": "production_db"}
                }
            ]
        return mock_search_json
    
    def get_test_inputs(self):
        """Provide test inputs for the tool."""
        return [
            {
                "json_path": "/path/to/data.json",
                "query": "user",
                "search_keys": True,
                "search_values": False
            },
            {
                "json_path": "/path/to/config.json",
                "query": "localhost",
                "json_path_expr": "$.database",
                "case_sensitive": False
            },
            {
                "json_path": "/path/to/nested.json",
                "query": "api_key",
                "max_depth": 3
            }
        ]
    
    def validate_tool_output(self, output, input_data):
        """Validate the tool output format."""
        assert isinstance(output, list)
        
        for result in output:
            assert isinstance(result, dict)
            assert "path" in result or "location" in result
            if "match_type" in result:
                assert result["match_type"] in ["key", "value", "both"]
    
    def test_jsonpath_expression_search(self, tmp_path):
        """Test searching with JSONPath expressions."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            # Search only in users array
            results = tool(json_file, "admin", json_path_expr="$.users[*]")
            
            # Should only find matches within users array
            assert all("users" in str(r.get("path", "")) for r in results)
    
    def test_search_keys_vs_values(self, tmp_path):
        """Test searching in keys only, values only, or both."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
        test_data = {
            "name": "test_name",
            "test_key": "different_value",
            "another": "name_in_value"
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            # Search keys only
            key_results = tool(json_file, "name", search_keys=True, search_values=False)
            
            # Search values only
            value_results = tool(json_file, "name", search_keys=False, search_values=True)
            
            # Search both
            both_results = tool(json_file, "name", search_keys=True, search_values=True)
            
            # Both should find more than either keys or values alone
            assert len(both_results) >= max(len(key_results), len(value_results))
    
    def test_nested_json_search(self, tmp_path):
        """Test searching in deeply nested JSON structures."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=json.dumps(nested_data))):
            # Search without depth limit
            results_unlimited = tool(json_file, "found_me")
            
            # Search with depth limit
            results_limited = tool(json_file, "found_me", max_depth=2)
            
            # Unlimited should find the deep value
            assert len(results_unlimited) > 0
            # Limited depth might not find it
            assert len(results_unlimited) >= len(results_limited)
    
    def test_array_search(self, tmp_path):
        """Test searching within JSON arrays."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
        array_data = {
            "products": [
                {"id": 1, "name": "Laptop", "price": 999},
                {"id": 2, "name": "Mouse", "price": 29},
                {"id": 3, "name": "Keyboard", "price": 79}
            ],
            "tags": ["electronics", "computers", "accessories"]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(array_data))):
            # Search in array of objects
            results = tool(json_file, "Laptop")
            assert len(results) > 0
            
            # Search in simple array
            results = tool(json_file, "computers")
            assert len(results) > 0
    
    def test_case_sensitivity(self, tmp_path):
        """Test case-sensitive vs case-insensitive search."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
        test_data = {
            "Name": "John DOE",
            "name": "jane doe",
            "NAME": "JACK DOE"
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            # Case-insensitive search
            results_insensitive = tool(json_file, "name", case_sensitive=False)
            
            # Case-sensitive search
            results_sensitive = tool(json_file, "name", case_sensitive=True)
            
            # Case-insensitive should find more matches
            assert len(results_insensitive) > len(results_sensitive)
    
    def test_numeric_and_boolean_search(self, tmp_path):
        """Test searching for numeric and boolean values."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
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
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            # Search for integer
            results = tool(json_file, "42")
            assert len(results) >= 1
            
            # Search for boolean
            results = tool(json_file, "true")
            assert len(results) >= 2  # active and debug
            
            # Search for port number
            results = tool(json_file, "8080")
            assert len(results) >= 1
    
    def test_null_value_search(self, tmp_path):
        """Test searching for null values."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
        test_data = {
            "name": "Test",
            "description": None,
            "metadata": {
                "created": "2024-01-01",
                "updated": None
            }
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            # Search for null
            results = tool(json_file, "null")
            assert len(results) >= 2  # description and updated
    
    def test_special_characters_handling(self, tmp_path):
        """Test handling of special characters in search."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
        test_data = {
            "email": "user@example.com",
            "regex": "^[a-z]+$",
            "path": "/home/user/docs",
            "url": "https://example.com/api?key=value&foo=bar"
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            special_queries = ["@example.com", "^[a-z]+$", "/home/user", "?key=value"]
            
            for query in special_queries:
                results = tool(json_file, query)
                assert isinstance(results, list)
    
    def test_invalid_json_handling(self, tmp_path):
        """Test handling of invalid JSON files."""
        json_file = tmp_path / "invalid.json"
        tool = self.get_component_function()
        
        invalid_json = "{ invalid json: no quotes }"
        
        with patch("builtins.open", mock_open(read_data=invalid_json)):
            results = tool(json_file, "test")
            
            # Should handle gracefully
            assert isinstance(results, list)
            assert len(results) == 0 or "error" in str(results)
    
    def test_empty_json_handling(self, tmp_path):
        """Test handling of empty JSON files."""
        json_file = tmp_path / "empty.json"
        tool = self.get_component_function()
        
        empty_cases = ["{}", "[]", "null"]
        
        for empty_json in empty_cases:
            with patch("builtins.open", mock_open(read_data=empty_json)):
                results = tool(json_file, "test")
                assert results == []
    
    def test_large_json_performance(self, tmp_path):
        """Test performance with large JSON files."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
        # Create large JSON structure
        large_data = {
            "items": [
                {"id": i, "name": f"Item {i}", "data": {"value": i * 10}}
                for i in range(1000)
            ]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(large_data))):
            import time
            start_time = time.time()
            
            results = tool(json_file, "Item 500")
            
            elapsed = time.time() - start_time
            
            # Should complete quickly
            assert elapsed < 2.0
            assert len(results) >= 1
    
    def test_circular_reference_handling(self, tmp_path):
        """Test handling of circular references (if applicable)."""
        json_file = TestDataFactory.create_json_file(tmp_path)
        tool = self.get_component_function()
        
        # JSON doesn't support circular references directly,
        # but test reference-like structures
        test_data = {
            "node1": {"ref": "node2", "value": "test"},
            "node2": {"ref": "node3", "value": "test"},
            "node3": {"ref": "node1", "value": "test"}
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
            results = tool(json_file, "test", max_depth=10)
            
            # Should handle without infinite loops
            assert isinstance(results, list)
            assert len(results) == 3  # Three "test" values
