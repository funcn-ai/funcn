"""CLI command: sygaldry build

Generates individual component JSON manifests from a registry index (similar to
`shadcn build`). It reads a single *registry* JSON file (defaulting to
``./packages/sygaldry_registry/index.json``) and writes one JSON file per
component into an output directory (default: ``./public/r``).

The generated files can then be served statically or published, allowing third
party developers to consume the registry via raw URLs.
"""

from __future__ import annotations

import json
import typer
from pathlib import Path
from rich.console import Console
from typing import Annotated

console = Console()

app = typer.Typer(help="Build registry JSON files from an index.", invoke_without_command=True)


@app.callback()
def build(  # noqa: D401 – CLI entry-point
    registry: Annotated[
        str | None,
        typer.Argument(
            help="Path to registry index JSON file.",
            show_default=False,
        ),
    ] = None,
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Destination directory for generated JSON files.",
        ),
    ] = "./public/r",
    cwd: Annotated[
        Path | None,
        typer.Option(
            "--cwd",
            "-c",
            help="Working directory. Defaults to current directory.",
        ),
    ] = None,
    base_url: Annotated[
        str | None,
        typer.Option(
            "--base-url",
            help="Base URL for component URLs (e.g., https://registry.sygaldry.ai).",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show detailed progress during build.",
        ),
    ] = False,
) -> None:
    """Generate per-component JSON manifests from a registry index file."""

    project_root = Path(cwd).resolve() if cwd else Path.cwd()

    # ------------------------------------------------------------------
    # Resolve paths
    # ------------------------------------------------------------------

    registry_path: Path
    if registry is None:
        # Default to the canonical location created by `sygaldry init`
        registry_path = project_root / "packages" / "sygaldry_registry" / "index.json"
    else:
        registry_path = Path(registry).expanduser()
        if not registry_path.is_absolute():
            registry_path = project_root / registry_path

    if not registry_path.exists():
        console.print(f"[bold red]Registry file not found:[/] {registry_path}")
        raise typer.Exit(code=1)

    output_dir = Path(output).expanduser()
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir

    # ------------------------------------------------------------------
    # Load registry
    # ------------------------------------------------------------------

    try:
        registry_data = json.loads(registry_path.read_text())
    except json.JSONDecodeError as exc:
        console.print(f"[bold red]Invalid JSON in registry file:[/] {exc}")
        raise typer.Exit(code=1) from exc

    components: list[dict[str, str]] = registry_data.get("components", [])  # type: ignore[arg-type]
    if not components:
        console.print("[yellow]No components found in registry file.[/]")
        raise typer.Exit()

    # ------------------------------------------------------------------
    # Write output
    # ------------------------------------------------------------------

    output_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"Writing manifests to [cyan]{output_dir}[/cyan] ...")

    written_files: list[Path] = []

    registry_root = registry_path.parent

    for item in components:
        name = item.get("name")
        version = item.get("version", "unknown")
        manifest_rel = item.get("manifest_path")
        if not name or not manifest_rel:
            console.print(f"[yellow]Skipping invalid component entry: {item}[/]")
            continue

        if verbose:
            console.print(f"\nProcessing component: [cyan]{name}[/cyan] ([dim]{version}[/dim])")

        manifest_path = (registry_root / manifest_rel).resolve()
        if verbose:
            console.print(f"  Reading manifest from: [dim]{manifest_path}[/dim]")

        if not manifest_path.exists():
            console.print(f"[yellow]Manifest not found for component '{name}': {manifest_path}[/]")
            continue

        try:
            manifest_data = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as exc:
            console.print(f"[yellow]Invalid manifest JSON for '{name}': {exc}[/]")
            continue

        out_file = output_dir / f"{name}.json"
        if verbose:
            console.print(f"  Writing to: [dim]{out_file}[/dim]")

        out_file.write_text(json.dumps(manifest_data, indent=2))
        written_files.append(out_file)

        if not verbose:
            console.print(f"  • {name}.json")

    # ------------------------------------------------------------------
    # Update registry with base URLs if provided
    # ------------------------------------------------------------------

    if base_url:
        # Ensure base_url doesn't end with a slash
        base_url = base_url.rstrip("/")

        # Update each component entry with a URL
        for item in components:
            name = item.get("name")
            if name:
                item["url"] = f"{base_url}/{name}.json"

        if verbose:
            console.print(f"\n[dim]Added component URLs with base: {base_url}[/dim]")

    # Write/update an index file in the output directory
    index_output = output_dir / "index.json"
    index_output.write_text(json.dumps(registry_data, indent=2))

    if verbose:
        console.print(f"\n[dim]Wrote index file to: {index_output}[/dim]")
        console.print("\n[bold green]Build complete![/bold green]")
        console.print(f"  Total components processed: {len(components)}")
        console.print(f"  Manifests written: {len(written_files)}")
        console.print(f"  Skipped/failed: {len(components) - len(written_files)}")
    else:
        console.print(f"\n:white_check_mark: [bold green]Build complete![/] Generated {len(written_files)} manifest(s).")
