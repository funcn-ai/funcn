from __future__ import annotations

import asyncio
import csv
import io
import pandas as pd
from fuzzywuzzy import fuzz
from pathlib import Path

# FUNCN_LILYPAD_IMPORT_PLACEHOLDER
# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER
from pydantic import BaseModel, Field, validator
from typing import Any, Optional, Union


class CSVSearchArgs(BaseModel):
    """Arguments for CSV search operations."""

    file_path: str = Field(..., description="Path to the CSV file to search")
    query: str = Field(..., description="Search query to find within the CSV")
    columns: list[str] | None = Field(None, description="Specific columns to search in. If None, searches all columns")
    filters: dict[str, Any] | None = Field(None, description="Column filters to apply before searching (e.g., {'age': '>30', 'status': 'active'})")
    max_results: int = Field(default=50, description="Maximum number of results to return")
    fuzzy_threshold: int = Field(default=80, description="Fuzzy matching threshold (0-100)")
    exact_match: bool = Field(default=False, description="Whether to use exact matching instead of fuzzy matching")
    case_sensitive: bool = Field(default=False, description="Whether the search should be case sensitive")


class CSVSearchResult(BaseModel):
    """Result from a CSV search operation."""

    row_index: int = Field(..., description="Row index in the CSV file")
    row_data: dict[str, Any] = Field(..., description="Complete row data as a dictionary")
    matched_columns: list[str] = Field(..., description="Columns where matches were found")
    match_scores: dict[str, float] = Field(..., description="Match scores for each matched column")


class CSVSearchResponse(BaseModel):
    """Response from CSV search tool."""

    results: list[CSVSearchResult] = Field(default_factory=list, description="List of search results")
    total_rows: int = Field(..., description="Total number of rows in the CSV")
    columns: list[str] = Field(..., description="List of column names in the CSV")
    filtered_count: int = Field(..., description="Number of rows after applying filters")
    error: str | None = Field(None, description="Error message if search failed")


# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER
async def search_csv_content(args: CSVSearchArgs) -> CSVSearchResponse:
    """Search for content within a CSV file with optional column filters.

    This function provides flexible search capabilities for CSV files,
    including fuzzy matching, column-specific searches, and data filtering.
    """
    try:
        # Validate file exists
        file_path = Path(args.file_path)
        if not file_path.exists():
            return CSVSearchResponse(
                results=[],
                total_rows=0,
                columns=[],
                filtered_count=0,
                error=f"CSV file not found: {args.file_path}"
            )

        # Run CSV processing in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, _process_and_search, file_path, args)

        return results

    except Exception as e:
        return CSVSearchResponse(
            results=[],
            total_rows=0,
            columns=[],
            filtered_count=0,
            error=f"Error searching CSV: {str(e)}"
        )


def _process_and_search(file_path: Path, args: CSVSearchArgs) -> CSVSearchResponse:
    """Process CSV and perform search (sync function for thread pool)."""
    try:
        # Read CSV file
        df = pd.read_csv(file_path, low_memory=False)
        total_rows = len(df)
        columns = df.columns.tolist()

        # Apply filters if provided
        filtered_df = df.copy()
        if args.filters:
            for column, condition in args.filters.items():
                if column not in columns:
                    continue

                # Parse filter conditions
                if isinstance(condition, str):
                    if condition.startswith('>'):
                        value = float(condition[1:])
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') > value]
                    elif condition.startswith('<'):
                        value = float(condition[1:])
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') < value]
                    elif condition.startswith('>='):
                        value = float(condition[2:])
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') >= value]
                    elif condition.startswith('<='):
                        value = float(condition[2:])
                        filtered_df = filtered_df[pd.to_numeric(filtered_df[column], errors='coerce') <= value]
                    elif condition.startswith('!='):
                        value_str = condition[2:]
                        filtered_df = filtered_df[filtered_df[column] != value_str]
                    else:
                        # Exact match
                        filtered_df = filtered_df[filtered_df[column] == condition]
                else:
                    # Direct value match
                    filtered_df = filtered_df[filtered_df[column] == condition]

        filtered_count = len(filtered_df)

        # Determine columns to search
        search_columns = args.columns if args.columns else columns
        search_columns = [col for col in search_columns if col in columns]

        # Perform search
        results = []
        query = args.query if args.case_sensitive else args.query.lower()

        for idx, row in filtered_df.iterrows():
            matched_columns = []
            match_scores = {}

            for column in search_columns:
                cell_value = str(row[column])
                if pd.isna(row[column]):
                    continue

                if not args.case_sensitive:
                    cell_value = cell_value.lower()

                if args.exact_match:
                    # Exact match
                    if query in cell_value:
                        matched_columns.append(column)
                        match_scores[column] = 100.0
                else:
                    # Fuzzy match
                    score = fuzz.partial_ratio(query, cell_value)
                    if score >= args.fuzzy_threshold:
                        matched_columns.append(column)
                        match_scores[column] = float(score)

            if matched_columns:
                # Convert row to dictionary
                row_dict: dict[str, Any] = {}
                for col in columns:
                    value = row[col]
                    # Handle NaN values
                    if pd.isna(value):
                        row_dict[col] = None
                    elif isinstance(value, pd.Timestamp | pd.DatetimeTZDtype):
                        row_dict[col] = str(value)
                    else:
                        row_dict[col] = value

                results.append(CSVSearchResult(
                    row_index=int(idx),
                    row_data=row_dict,
                    matched_columns=matched_columns,
                    match_scores=match_scores
                ))

        # Sort by best match score and limit results
        results.sort(key=lambda x: max(x.match_scores.values()) if x.match_scores else 0, reverse=True)
        results = results[:args.max_results]

        return CSVSearchResponse(
            results=results,
            total_rows=total_rows,
            columns=columns,
            filtered_count=filtered_count,
            error=None
        )

    except Exception as e:
        return CSVSearchResponse(
            results=[],
            total_rows=0,
            columns=[],
            filtered_count=0,
            error=f"Error processing CSV: {str(e)}"
        )
