from __future__ import annotations

import httpx
import typer
from rich.console import Console
from rich.table import Table
from sygaldry_cli.config_manager import ConfigManager
from sygaldry_cli.core.registry_handler import RegistryHandler

console = Console()

app = typer.Typer(help="List available components from registry sources.")


@app.callback(invoke_without_command=True)
def list_components(
    ctx: typer.Context,
    source: str | None = typer.Option(None, help="Registry source alias to list from"),
    all_sources: bool = typer.Option(False, "--all", help="List from all available sources"),
    refresh: bool = typer.Option(False, "--refresh", "-r", help="Force refresh of cached data"),
    cache_ttl: int | None = typer.Option(None, "--cache-ttl", help="Override default cache TTL in seconds"),
) -> None:
    cfg = ConfigManager()

    # Override cache TTL if specified
    if cache_ttl is not None:
        cfg.config.cache_config.ttl_seconds = cache_ttl

    if all_sources:
        # List from all sources that are available
        with RegistryHandler(cfg) as rh:
            indexes = rh.fetch_all_indexes(silent_errors=True, force_refresh=refresh)

        if not indexes:
            console.print("[red]Error: No registry sources are currently available[/]")
            raise typer.Exit(1)

        # Display components from each available source
        for source_alias, index in indexes.items():
            table = Table(title=f"Components – {source_alias}")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Version", justify="right")
            table.add_column("Type")
            table.add_column("Description")

            for comp in index.components:
                table.add_row(comp.name, comp.version, comp.type, comp.description)

            console.print(table)
            console.print()  # Add spacing between tables
    else:
        # List from specific source or default
        try:
            with RegistryHandler(cfg) as rh:
                index = rh.fetch_index(source_alias=source, silent_errors=False, force_refresh=refresh)

            if not index:
                console.print(f"[red]Error: Unable to fetch from source '{source or 'default'}'[/]")
                raise typer.Exit(1)

            table = Table(title=f"Components – {source or 'default'}")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Version", justify="right")
            table.add_column("Type")
            table.add_column("Description")

            for comp in index.components:
                table.add_row(comp.name, comp.version, comp.type, comp.description)

            console.print(table)

        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
            console.print(f"[red]Error: Unable to connect to source '{source or 'default'}': {e}[/]")
            raise typer.Exit(1) from e
        except Exception as e:
            console.print(f"[red]Error: Failed to fetch from source '{source or 'default'}': {e}[/]")
            raise typer.Exit(1) from e
