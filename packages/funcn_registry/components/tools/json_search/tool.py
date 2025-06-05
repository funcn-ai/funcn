from __future__ import annotations

import asyncio
import json
from fuzzywuzzy import fuzz
from jsonpath_ng import parse
from jsonpath_ng.exceptions import JSONPathError
from pathlib import Path

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field, validator
from typing import Any, Optional, Union


class JSONSearchArgs(BaseModel):
    """Arguments for JSON search operations."""

    file_path: str | None = Field(None, description="Path to the JSON file to search (if searching a file)")
    json_data: dict[str, Any] | None = Field(None, description="JSON data to search (if providing data directly)")
    query: str = Field(..., description="Search query to find within the JSON")
    json_path: str | None = Field(None, description="JSONPath expression to narrow search scope (e.g., '$.users[*].name')")
    exact_match: bool = Field(default=False, description="Whether to use exact matching instead of fuzzy matching")
    fuzzy_threshold: int = Field(default=80, description="Fuzzy matching threshold (0-100)")
    case_sensitive: bool = Field(default=False, description="Whether the search should be case sensitive")
    max_results: int = Field(default=50, description="Maximum number of results to return")
    include_path: bool = Field(default=True, description="Include the JSONPath to each result")
    search_keys: bool = Field(default=False, description="Also search in object keys, not just values")

    @validator('file_path', 'json_data')
    def validate_input(cls, v, values):
        if 'file_path' in values and values['file_path'] is None and v is None:
            raise ValueError("Either file_path or json_data must be provided")
        return v


class JSONSearchResult(BaseModel):
    """Result from a JSON search operation."""

    path: str = Field(..., description="JSONPath to the matched element")
    value: Any = Field(..., description="The matched value")
    match_score: float = Field(..., description="Match score (0-100)")
    context: dict[str, Any] | None = Field(None, description="Parent object containing the match")
    key: str | None = Field(None, description="Key name if match was in an object")


class JSONSearchResponse(BaseModel):
    """Response from JSON search tool."""

    results: list[JSONSearchResult] = Field(default_factory=list, description="List of search results")
    total_elements: int = Field(..., description="Total number of elements searched")
    search_scope: str = Field(..., description="Description of search scope")
    error: str | None = Field(None, description="Error message if search failed")


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def search_json_content(args: JSONSearchArgs) -> JSONSearchResponse:
    """Search for content within JSON data using JSONPath and fuzzy matching.

    This function provides flexible search capabilities for JSON files and data,
    including JSONPath filtering, fuzzy matching, and key/value searching.
    """
    try:
        # Load JSON data
        if args.file_path:
            file_path = Path(args.file_path)
            if not file_path.exists():
                return JSONSearchResponse(
                    results=[],
                    total_elements=0,
                    search_scope="file",
                    error=f"JSON file not found: {args.file_path}"
                )

            with open(file_path, encoding='utf-8') as f:
                json_data = json.load(f)
        else:
            json_data = args.json_data

        # Run search in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _search_json, json_data, args)

        return results

    except json.JSONDecodeError as e:
        return JSONSearchResponse(
            results=[],
            total_elements=0,
            search_scope="error",
            error=f"Invalid JSON format: {str(e)}"
        )
    except Exception as e:
        return JSONSearchResponse(
            results=[],
            total_elements=0,
            search_scope="error",
            error=f"Error searching JSON: {str(e)}"
        )


def _search_json(json_data: Any, args: JSONSearchArgs) -> JSONSearchResponse:
    """Perform JSON search (sync function for thread pool)."""
    results = []
    total_elements = 0
    search_scope = "entire document"

    try:
        # Apply JSONPath filter if provided
        if args.json_path:
            try:
                jsonpath_expr = parse(args.json_path)
                matches = jsonpath_expr.find(json_data)
                search_data = [(match.full_path, match.value) for match in matches]
                search_scope = f"JSONPath: {args.json_path}"
            except JSONPathError as e:
                return JSONSearchResponse(
                    results=[],
                    total_elements=0,
                    search_scope="error",
                    error=f"Invalid JSONPath expression: {str(e)}"
                )
        else:
            # Search entire document
            search_data = _flatten_json(json_data)

        # Perform search
        query = args.query if args.case_sensitive else args.query.lower()

        for path, value in search_data:
            total_elements += 1
            matched = False
            match_score = 0.0

            # Search in values
            if value is not None:
                str_value = str(value)
                if not args.case_sensitive:
                    str_value = str_value.lower()

                if args.exact_match:
                    if query in str_value:
                        matched = True
                        match_score = 100.0
                else:
                    score = fuzz.partial_ratio(query, str_value)
                    if score >= args.fuzzy_threshold:
                        matched = True
                        match_score = float(score)

            # Search in keys if enabled
            if args.search_keys and not matched:
                path_parts = str(path).split('.')
                for part in path_parts:
                    # Remove array indices
                    part_key = part.split('[')[0]
                    if not part_key or part_key == '$':
                        continue

                    if not args.case_sensitive:
                        part_key = part_key.lower()

                    if args.exact_match:
                        if query in part_key:
                            matched = True
                            match_score = 100.0
                            break
                    else:
                        score = fuzz.partial_ratio(query, part_key)
                        if score >= args.fuzzy_threshold:
                            matched = True
                            match_score = float(score)
                            break

            if matched:
                # Get context (parent object)
                context = _get_context(json_data, path)

                # Get key if in object
                key = None
                path_str = str(path)
                if '.' in path_str:
                    key = path_str.split('.')[-1].split('[')[0]

                results.append(JSONSearchResult(
                    path=path_str if args.include_path else "",
                    value=value,
                    match_score=match_score,
                    context=context,
                    key=key
                ))

        # Sort by match score and limit results
        results.sort(key=lambda x: x.match_score, reverse=True)
        results = results[:args.max_results]

        return JSONSearchResponse(
            results=results,
            total_elements=total_elements,
            search_scope=search_scope,
            error=None
        )

    except Exception as e:
        return JSONSearchResponse(
            results=[],
            total_elements=0,
            search_scope="error",
            error=f"Error during search: {str(e)}"
        )


def _flatten_json(data: Any, parent_path: str = "$") -> list[tuple[str, Any]]:
    """Flatten JSON structure into path-value pairs."""
    items = []

    if isinstance(data, dict):
        for key, value in data.items():
            path = f"{parent_path}.{key}"
            if isinstance(value, dict | list):
                items.extend(_flatten_json(value, path))
            else:
                items.append((path, value))
    elif isinstance(data, list):
        for i, value in enumerate(data):
            path = f"{parent_path}[{i}]"
            if isinstance(value, dict | list):
                items.extend(_flatten_json(value, path))
            else:
                items.append((path, value))
    else:
        items.append((parent_path, data))

    return items


def _get_context(data: Any, path: str) -> dict[str, Any] | None:
    """Get the parent object containing the matched value."""
    try:
        parts = path.replace('$', '').strip('.').split('.')
        current = data

        # Navigate to parent
        for part in parts[:-1]:
            if '[' in part:
                key, index_str = part.split('[')
                index = int(index_str.rstrip(']'))
                current = current[key][index] if key else current[index]
            else:
                current = current[part]

        # Return parent if it's a dict
        if isinstance(current, dict):
            return current
        elif isinstance(current, list) and current:
            # For lists, return a sample context
            return {"_list_sample": current[:3], "_total_items": len(current)}

    except (KeyError, IndexError, ValueError, TypeError):
        pass

    return None
