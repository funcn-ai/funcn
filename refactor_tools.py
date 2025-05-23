#!/usr/bin/env python3
"""Helper script to identify BaseTool classes and their main methods."""

import ast
import sys
from pathlib import Path


def analyze_tool_file(filepath):
    """Analyze a tool file and extract BaseTool class info."""
    with open(filepath) as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except:
        print(f"Failed to parse {filepath}")
        return

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it inherits from BaseTool
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == 'BaseTool':
                    print(f"\n{filepath}")
                    print(f"  Class: {node.name}")

                    # Find the run method
                    for item in node.body:
                        if isinstance(item, ast.AsyncFunctionDef) and item.name == 'run':
                            print("  Main method: async def run(self)")

                    # Find fields
                    print("  Fields:")
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            field_name = item.target.id
                            if not field_name.startswith('_'):
                                print(f"    - {field_name}")


if __name__ == "__main__":
    tools_dir = Path(".")

    for tool_file in tools_dir.glob("*/tool.py"):
        analyze_tool_file(tool_file)
