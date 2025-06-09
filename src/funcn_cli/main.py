from __future__ import annotations

import sys
import typer
from funcn_cli.commands import add as add_cmd, build_cmd, docs, init_cmd, list_components, search, source

# from funcn_cli.commands import mcp_cmd  # Temporarily commented out due to missing MCP dependency
from rich.console import Console

app = typer.Typer(
    help="funcn – Discover and integrate reusable agents and tools into your Python projects.",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()

# Register sub-commands ------------------------------------------------------

app.add_typer(init_cmd.app, name="init", help="Initialise funcn in the current project.")
app.add_typer(add_cmd.app, name="add", help="Add a component to the current project.")
app.add_typer(list_components.app, name="list", help="List available components in registries.")
app.add_typer(search.app, name="search", help="Search for components in registries.")
app.add_typer(source.app, name="source", help="Manage registry sources.")
app.add_typer(build_cmd.app, name="build", help="Generate registry JSON files.")
# app.add_typer(mcp_cmd.app, name="mcp", help="Run a funcn agent as an MCP server.")  # Temporarily commented out
app.add_typer(docs.app, name="docs", help="Generate documentation and editor-specific rule files.")

# Entry point for Python -m funcn_cli ---------------------------------------


def main() -> None:  # pragma: no cover
    """Main entry point for console script."""
    sys.argv[0] = "funcn"
    app()  # type: ignore[misc]


def _main() -> None:  # pragma: no cover
    sys.argv[0] = "funcn"
    app()  # type: ignore[misc]


if __name__ == "__main__":  # pragma: no cover
    _main()
