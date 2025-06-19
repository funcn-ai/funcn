from __future__ import annotations

import httpx
import typer
from funcn_cli.config_manager import ConfigManager
from rich.console import Console
from rich.table import Table
from urllib.parse import urlparse

console = Console()

app = typer.Typer(help="Manage registry sources.")


def _test_source_connectivity(url: str) -> bool:
    """Test if a registry source is accessible and returns valid registry data.
    
    Args:
        url: The URL to test
        
    Returns:
        True if the source is accessible and valid, False otherwise
    """
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            
            # Try to parse as JSON and check for registry_version
            data = response.json()
            if not isinstance(data, dict):
                return False
                
            # Check for required registry fields
            if "registry_version" not in data:
                console.print("[yellow]:warning: Response missing 'registry_version' field[/yellow]")
                return False
                
            if "components" not in data:
                console.print("[yellow]:warning: Response missing 'components' field[/yellow]")
                return False
                
            return True
            
    except httpx.TimeoutException:
        console.print("[red]Connection timed out[/red]")
        return False
    except httpx.ConnectError:
        console.print("[red]Failed to connect to the server[/red]")
        return False
    except httpx.HTTPStatusError as e:
        console.print(f"[red]HTTP error {e.response.status_code}: {e.response.reason_phrase}[/red]")
        return False
    except (ValueError, KeyError) as e:
        console.print(f"[red]Invalid registry response format: {e}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        return False


@app.command()
def add(
    alias: str = typer.Argument(..., help="Alias for registry source"),
    url: str = typer.Argument(..., help="URL to index.json of registry"),
    priority: int = typer.Option(100, "--priority", "-p", help="Source priority (lower = higher priority)"),
    skip_connectivity_check: bool = typer.Option(False, "--skip-check", help="Skip connectivity check"),
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

    # Test connectivity unless skipped
    if not skip_connectivity_check and parsed.scheme in ("http", "https"):
        console.print(f"[dim]Testing connectivity to {url}...[/dim]")
        if not _test_source_connectivity(url):
            console.print(f":x: Failed to connect to registry at {url}")
            console.print("[yellow]Tip: Use --skip-check to add the source anyway[/yellow]")
            raise typer.Exit(1)
        console.print("[green]:white_check_mark: Successfully connected to registry[/green]")

    cfg_manager = ConfigManager()
    cfg_manager.add_registry_source(alias, url, priority=priority)
    priority_msg = f" (priority: {priority})" if priority != 100 else ""
    console.print(f":white_check_mark: Added registry source '{alias}' -> {url}{priority_msg}")


@app.command("list")
def list_sources() -> None:
    """List configured registry sources."""
    cfg_manager = ConfigManager()
    cfg = cfg_manager.config
    table = Table(title="Registry Sources")
    table.add_column("Alias", style="cyan")
    table.add_column("URL")
    table.add_column("Priority", justify="right")
    table.add_column("Status")

    # Show default source first if not already in registry_sources
    if "default" not in cfg.registry_sources and cfg.default_registry_url:
        table.add_row("[bold]default[/]", cfg.default_registry_url, "100", "[green]enabled[/]")

    # Sort sources by priority (lower number = higher priority)
    sources = []
    for alias, source in cfg.registry_sources.items():
        if isinstance(source, str):
            # Backward compatibility: string format
            sources.append((alias, source, 100, True))
        else:
            # New format: RegistrySourceConfig
            sources.append((alias, source.url, source.priority, source.enabled))
    
    sources.sort(key=lambda x: x[2])  # Sort by priority
    
    for alias, url, priority, enabled in sources:
        alias_display = f"[bold]{alias}[/]" if alias == "default" or url == cfg.default_registry_url else alias
        status = "[green]enabled[/]" if enabled else "[dim]disabled[/]"
        table.add_row(alias_display, url, str(priority), status)
    
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
