from __future__ import annotations

"""CLI command: funcn build

Generates individual component JSON manifests from a registry index (similar to
`shadcn build`). It reads a single *registry* JSON file (defaulting to
``./packages/funcn_registry/index.json``) and writes one JSON file per
component into an output directory (default: ``./public/r``).

The generated files can then be served statically or published, allowing third
party developers to consume the registry via raw URLs.
"""

import json
import typer
from pathlib import Path
from rich.console import Console
from typing import Annotated

console = Console()

app = typer.Typer(help="Build registry JSON files from an index.")


@app.callback(invoke_without_command=True)
def build(  # noqa: D401 – CLI entry-point
    ctx: typer.Context,
    registry: Annotated[str | None, typer.Argument(
        help="Path to registry index JSON file.",
        show_default=False,
    )] = None,
    output: Annotated[str, typer.Option(
        "--output",
        "-o",
        help="Destination directory for generated JSON files.",
    )] = "./public/r",
    cwd: Annotated[Path | None, typer.Option(
        "--cwd",
        "-c",
        help="Working directory. Defaults to current directory.",
    )] = None,
) -> None:
    """Generate per-component JSON manifests from a registry index file."""

    project_root = Path(cwd).resolve() if cwd else Path.cwd()

    # ------------------------------------------------------------------
    # Resolve paths
    # ------------------------------------------------------------------

    registry_path: Path
    if registry is None:
        # Default to the canonical location created by `funcn init`
        registry_path = project_root / "packages" / "funcn_registry" / "index.json"
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
        manifest_rel = item.get("manifest_path")
        if not name or not manifest_rel:
            console.print(f"[yellow]Skipping invalid component entry: {item}[/]")
            continue

        manifest_path = (registry_root / manifest_rel).resolve()
        if not manifest_path.exists():
            console.print(f"[yellow]Manifest not found for component '{name}': {manifest_path}[/]")
            continue

        try:
            manifest_data = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as exc:
            console.print(f"[yellow]Invalid manifest JSON for '{name}': {exc}[/]")
            continue

        out_file = output_dir / f"{name}.json"
        out_file.write_text(json.dumps(manifest_data, indent=2))
        written_files.append(out_file)
        console.print(f"  • {name}.json")

    # Optionally write/update an index file in the output directory
    index_output = output_dir / "index.json"
    index_output.write_text(json.dumps(registry_data, indent=2))
    console.print(f"\n:white_check_mark: [bold green]Build complete![/] Generated {len(written_files)} manifest(s).")
