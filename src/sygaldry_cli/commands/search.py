from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table
from sygaldry_cli.config_manager import ConfigManager
from sygaldry_cli.core.registry_handler import RegistryHandler

console = Console()

app = typer.Typer(help="Search registries for components containing keyword.")


@app.callback(invoke_without_command=True)
def search(
    ctx: typer.Context,
    keyword: str = typer.Argument(..., help="Search keyword"),
    source: str | None = typer.Option(None, help="Registry source alias"),
) -> None:
    cfg = ConfigManager()
    with RegistryHandler(cfg) as rh:
        index = rh.fetch_index(source_alias=source)

    results = [
        comp for comp in index.components if keyword.lower() in comp.name.lower() or keyword.lower() in comp.description.lower()
    ]

    if not results:
        console.print(f"[yellow]No components matching '{keyword}' found.")
        raise typer.Exit()

    table = Table(title=f"Search results for '{keyword}'")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    for comp in results:
        table.add_row(comp.name, comp.description)

    console.print(table)
