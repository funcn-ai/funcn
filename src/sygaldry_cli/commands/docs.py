from __future__ import annotations

import json
import os
import typer
from pathlib import Path
from rich.console import Console
from sygaldry_cli.config_manager import ConfigManager
from sygaldry_cli.core.component_manager import ComponentManager
from typing import Optional

console = Console()
app = typer.Typer(help="Generate documentation and editor-specific rule files.")

# Updated editor configurations based on clarifications
EDITOR_CONFIGS = {
    "cursor": {
        "files": [".cursor/rules/sygaldry.mdc"],  # .mdc format in .cursor/rules directory
        "format": "mdc",
        "extension": ".mdc",
    },
    "windsurf": {"files": [".windsurfrules"], "format": "markdown", "extension": ".md"},
    "cline": {"files": [".clinerules"], "format": "markdown", "extension": ".md"},
    "claude": {"files": ["CLAUDE.md"], "format": "markdown", "extension": ".md"},
    "sourcegraph": {"files": [".sourcegraph/memory.md"], "format": "markdown", "extension": ".md"},
    "openai_codex": {
        "files": ["AGENTS.md"],  # For OpenAI Codex
        "format": "markdown",
        "extension": ".md",
    },
    "amp_code": {
        "files": ["AGENT.md"],  # For Amp Code
        "format": "markdown",
        "extension": ".md",
    },
}


@app.command()
def generate(
    editor: str = typer.Option(
        "cursor",
        "--editor",
        "-e",
        help="Target editor/agent (cursor, windsurf, cline, claude, sourcegraph, openai_codex, amp_code)",
    ),
    component: str | None = typer.Option(None, "--component", "-c", help="Generate docs for specific component"),
    output_dir: str | None = typer.Option(None, "--output", "-o", help="Output directory (default: project root)"),
    component_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Generate docs for components of specific type (agent, tool, prompt_template, response_model, eval, example)",
    ),
    force_regenerate: bool = typer.Option(
        False,
        "--force-regenerate",
        "-f",
        help="Force complete regeneration of sygaldry.md files, overwriting any user customizations",
    ),
):
    """Generate editor-specific rule files and documentation."""

    if editor not in EDITOR_CONFIGS:
        console.print(f"[red]Error: Unknown editor '{editor}'. Supported: {', '.join(EDITOR_CONFIGS.keys())}")
        raise typer.Exit(1)

    if component:
        _generate_component_docs(component, editor, output_dir, force_regenerate)
    elif component_type:
        _generate_docs_by_type(component_type, editor, output_dir, force_regenerate)
    else:
        _generate_all_docs(editor, output_dir, force_regenerate)


@app.command()
def template(
    component_name: str = typer.Argument(..., help="Name of the component"),
    output_file: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Generate a sygaldry.md template for a component."""
    _generate_sygaldry_md_template(component_name, output_file)


@app.command()
def types():
    """List available component types and their templates."""
    from sygaldry_cli.templates.component_type_templates import COMPONENT_TYPE_TEMPLATES

    console.print("[blue]Available component types and their specialized templates:[/blue]")
    for component_type in COMPONENT_TYPE_TEMPLATES:
        console.print(f"  • [green]{component_type}[/green]: Specialized template with type-specific sections")

    console.print("\n[blue]Usage examples:[/blue]")
    console.print("  • Generate docs for all agents: [cyan]sygaldry docs generate --type agent[/cyan]")
    console.print("  • Generate docs for all tools: [cyan]sygaldry docs generate --type tool[/cyan]")
    console.print("  • Generate template for new component: [cyan]sygaldry docs template my_component[/cyan]")


def _generate_docs_by_type(component_type: str, editor: str, output_dir: str | None, force_regenerate: bool):
    """Generate documentation for all components of a specific type."""
    from sygaldry_cli.templates.component_type_templates import COMPONENT_TYPE_TEMPLATES

    if component_type not in COMPONENT_TYPE_TEMPLATES:
        console.print(
            f"[red]Error: Unknown component type '{component_type}'. Supported: {', '.join(COMPONENT_TYPE_TEMPLATES.keys())}"
        )
        raise typer.Exit(1)

    console.print(f"[blue]Generating documentation for all '{component_type}' components")

    # Find all components of the specified type
    components = _discover_components_by_type(component_type)

    if not components:
        console.print(f"[yellow]No components of type '{component_type}' found")
        return

    # Generate sygaldry.md for each component
    for component_path, component_data in components:
        _generate_component_sygaldry_md(component_data, component_path, force_regenerate)

    # Generate global editor rules
    _generate_global_editor_rules(components, editor, output_dir)

    console.print(f"[green]Generated documentation for {len(components)} '{component_type}' components")


def _discover_components_by_type(component_type: str) -> list[tuple[Path, dict]]:
    """Discover all components of a specific type in the registry."""
    components: list[tuple[Path, dict]] = []
    registry_path = Path("packages/sygaldry_registry/components")

    if not registry_path.exists():
        return components

    for category_dir in registry_path.iterdir():
        if category_dir.is_dir():
            for component_dir in category_dir.iterdir():
                if component_dir.is_dir():
                    component_json = component_dir / "component.json"
                    if component_json.exists():
                        try:
                            with open(component_json) as f:
                                data = json.load(f)
                                if data.get("type") == component_type:
                                    components.append((component_dir, data))
                        except Exception:
                            continue

    return components


def _generate_component_docs(component: str, editor: str, output_dir: str | None, force_regenerate: bool):
    """Generate documentation for a specific component."""
    console.print(f"[blue]Generating documentation for component: {component}")

    # Find the component's component.json file
    component_path = _find_component_path(component)
    if not component_path:
        console.print(f"[red]Error: Component '{component}' not found")
        raise typer.Exit(1)

    # Load component.json
    component_json_path = component_path / "component.json"
    if not component_json_path.exists():
        console.print(f"[red]Error: component.json not found at {component_json_path}")
        raise typer.Exit(1)

    with open(component_json_path) as f:
        component_data = json.load(f)

    # Generate sygaldry.md for the component
    _generate_component_sygaldry_md(component_data, component_path, force_regenerate)

    # Generate editor-specific rules mentioning this component
    _generate_editor_rules_for_component(component_data, editor, output_dir)


def _generate_all_docs(editor: str, output_dir: str | None, force_regenerate: bool):
    """Generate all documentation."""
    console.print(f"[blue]Generating all documentation for editor: {editor}")

    # Find all components
    components = _discover_all_components()

    if not components:
        console.print("[yellow]No components found")
        return

    # Generate sygaldry.md for each component
    for component_path, component_data in components:
        _generate_component_sygaldry_md(component_data, component_path, force_regenerate)

    # Generate global editor rules
    _generate_global_editor_rules(components, editor, output_dir)


def _generate_sygaldry_md_template(component_name: str, output_file: str | None):
    """Generate a sygaldry.md template."""
    from sygaldry_cli.templates.sygaldry_md_template import generate_template_sygaldry_md

    template_content = generate_template_sygaldry_md(component_name)

    output_path = Path(output_file) if output_file else Path(f"{component_name}_sygaldry.md")

    with open(output_path, 'w') as f:
        f.write(template_content)

    console.print(f"[green]Generated template: {output_path}")


def _find_component_path(component_name: str) -> Path | None:
    """Find the path to a component by name."""
    # Search in packages/sygaldry_registry/components/
    registry_path = Path("packages/sygaldry_registry/components")

    if not registry_path.exists():
        return None

    # Search in all subdirectories
    for category_dir in registry_path.iterdir():
        if category_dir.is_dir():
            for component_dir in category_dir.iterdir():
                if component_dir.is_dir() and component_dir.name == component_name:
                    return component_dir
                # Also check if component.json has matching name
                component_json = component_dir / "component.json"
                if component_json.exists():
                    try:
                        with open(component_json) as f:
                            data = json.load(f)
                            if data.get("name") == component_name:
                                return component_dir
                    except Exception:
                        continue

    return None


def _discover_all_components() -> list[tuple[Path, dict]]:
    """Discover all components in the registry."""
    components: list[tuple[Path, dict]] = []
    registry_path = Path("packages/sygaldry_registry/components")

    if not registry_path.exists():
        return components

    for category_dir in registry_path.iterdir():
        if category_dir.is_dir():
            for component_dir in category_dir.iterdir():
                if component_dir.is_dir():
                    component_json = component_dir / "component.json"
                    if component_json.exists():
                        try:
                            with open(component_json) as f:
                                data = json.load(f)
                                components.append((component_dir, data))
                        except Exception:
                            continue

    return components


def _generate_component_sygaldry_md(component_data: dict, component_path: Path, force_regenerate: bool):
    """Generate sygaldry.md for a specific component, preserving existing user content."""
    from sygaldry_cli.templates.sygaldry_md_template import generate_sygaldry_md, merge_with_existing_sygaldry_md

    # Check if there's an existing README to incorporate
    existing_readme = None
    readme_path = component_path / "README.md"
    if readme_path.exists():
        with open(readme_path) as f:
            existing_readme = f.read()

    # Check for existing sygaldry.md
    sygaldry_md_path = component_path / "sygaldry.md"
    existing_sygaldry_md = None
    if sygaldry_md_path.exists():
        with open(sygaldry_md_path) as f:
            existing_sygaldry_md = f.read()

    # Generate new sygaldry.md content
    new_sygaldry_md_content = generate_sygaldry_md(component_data, existing_readme)

    # Merge with existing content if it exists
    if existing_sygaldry_md and not force_regenerate:
        final_content = merge_with_existing_sygaldry_md(existing_sygaldry_md, new_sygaldry_md_content, component_data)
    else:
        final_content = new_sygaldry_md_content

    # Write sygaldry.md
    with open(sygaldry_md_path, 'w') as f:
        f.write(final_content)

    console.print(f"[green]Generated: {sygaldry_md_path}")


def _generate_editor_rules_for_component(component_data: dict, editor: str, output_dir: str | None):
    """Generate editor-specific rules for a component."""
    # This would generate project-level rules that know about this component
    pass


def _generate_global_editor_rules(components: list[tuple[Path, dict]], editor: str, output_dir: str | None):
    """Generate global editor rules that know about all components."""
    from sygaldry_cli.templates.editor_rules import generate_editor_rules

    component_list = [comp_data for _, comp_data in components]

    # Generate rules content
    rules_content = generate_editor_rules(editor, component_list)

    # Determine output directory
    base_dir = Path(output_dir) if output_dir else Path(".")

    # Get editor config
    editor_config = EDITOR_CONFIGS[editor]

    # Write to each specified file location
    for file_path in editor_config["files"]:
        full_path = base_dir / file_path

        # Create directory if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Add extension if needed (but not for files that start with a dot)
        if not full_path.suffix and "extension" in editor_config and not full_path.name.startswith('.'):
            extension = editor_config["extension"]
            if isinstance(extension, str):
                full_path = full_path.with_suffix(extension)

        with open(full_path, 'w') as f:
            f.write(rules_content)

        console.print(f"[green]Generated: {full_path}")
