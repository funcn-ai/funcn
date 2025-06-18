from __future__ import annotations

import typer
from funcn_cli.config_manager import ConfigManager
from rich.console import Console
from rich.table import Table
from urllib.parse import urlparse

console = Console()

app = typer.Typer(help="Manage registry sources.")


@app.command()
def add(
    alias: str = typer.Argument(..., help="Alias for registry source"),
    url: str = typer.Argument(..., help="URL to index.json of registry"),
) -> None:
    """Add a new registry source."""
    # Validate URL format
    parsed = urlparse(url)

    # Check for valid scheme
    if parsed.scheme not in ("http", "https", "file"):
        console.print(f":x: Invalid URL scheme '{parsed.scheme}'. Must be http, https, or file.")
        raise typer.Exit(1)

    # Check for required parts
    if parsed.scheme in ("http", "https") and not parsed.netloc:
        console.print(":x: Invalid URL: missing domain/host")
        raise typer.Exit(1)

    # Warn if URL doesn't end with index.json
    if not url.endswith("/index.json") and not url.endswith("/index.json/"):
        console.print(f"[yellow]:warning: URL should typically point to an index.json file. Got: {url}[/yellow]")

    cfg_manager = ConfigManager()
    cfg_manager.add_registry_source(alias, url)
    console.print(f":white_check_mark: Added registry source '{alias}' -> {url}")


@app.command("list")
def list_sources() -> None:
    """List configured registry sources."""
    cfg_manager = ConfigManager()
    cfg = cfg_manager.config
    table = Table(title="Registry Sources")
    table.add_column("Alias", style="cyan")
    table.add_column("URL")

    # Show default source first if not already in registry_sources
    if "default" not in cfg.registry_sources and cfg.default_registry_url:
        table.add_row("[bold]default[/]", cfg.default_registry_url)

    for alias, url in cfg.registry_sources.items():
        alias_display = f"[bold]{alias}[/]" if alias == "default" or url == cfg.default_registry_url else alias
        table.add_row(alias_display, url)
    console.print(table)


@app.command()
def remove(
    alias: str = typer.Argument(..., help="Alias of registry source to remove"),
) -> None:
    """Remove a registry source."""
    cfg_manager = ConfigManager()
    cfg = cfg_manager.config

    # Check if the source exists
    if alias not in cfg.registry_sources:
        console.print(f":x: Registry source '{alias}' not found")
        raise typer.Exit(1)

    # Prevent removing the default source if it's the only one
    if alias == "default" and len(cfg.registry_sources) == 1:
        console.print(":x: Cannot remove the only remaining registry source")
        raise typer.Exit(1)

    # Remove the source
    cfg_manager.remove_registry_source(alias)
    console.print(f":white_check_mark: Removed registry source '{alias}'")
