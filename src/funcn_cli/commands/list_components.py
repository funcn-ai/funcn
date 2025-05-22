from __future__ import annotations

import typer
from funcn_cli.config_manager import ConfigManager
from funcn_cli.core.registry_handler import RegistryHandler
from rich.console import Console
from rich.table import Table

console = Console()

app = typer.Typer(help="List available components from registry sources.")


@app.callback(invoke_without_command=True)
def list_components(
    ctx: typer.Context,
    source: str | None = typer.Option(None, help="Registry source alias to list from"),
) -> None:
    cfg = ConfigManager()
    with RegistryHandler(cfg) as rh:
        index = rh.fetch_index(source_alias=source)

    table = Table(title=f"Components – {source or 'default'}")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Version", justify="right")
    table.add_column("Type")
    table.add_column("Description")

    for comp in index.components:
        table.add_row(comp.name, comp.version, comp.type, comp.description)

    console.print(table)
