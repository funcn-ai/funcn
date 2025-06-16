from __future__ import annotations

import typer
from funcn_cli.config_manager import ConfigManager
from rich.console import Console
from rich.table import Table

console = Console()

app = typer.Typer(help="Manage registry sources.")


@app.command()
def add(
    alias: str = typer.Argument(..., help="Alias for registry source"),
    url: str = typer.Argument(..., help="URL to index.json of registry"),
    global_cfg: bool = typer.Option(False, "--global", help="Add source to global config instead of project config."),
) -> None:
    """Add a new registry source."""
    cfg_manager = ConfigManager()
    cfg_manager.add_registry_source(alias, url, project_level=not global_cfg)
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
