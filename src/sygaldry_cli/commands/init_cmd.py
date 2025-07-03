from __future__ import annotations

import json
import os
import typer
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm, Prompt
from typing import Any, Optional

console = Console()

app = typer.Typer(help="Initialise sygaldry in the current project.")

CONFIG_FILE_NAME = "sygaldry.json"
SCHEMA_FILE_NAME = "sygaldry.schema.json"

# Define Typer Options as module-level constants
_YES_OPTION = typer.Option(False, "--yes", "-y", help="Skip confirmation and use defaults.")
_DEFAULTS_FLAG_OPTION = typer.Option(False, "--defaults", "-d", help="Use default configuration (same as --yes).")
_FORCE_OPTION = typer.Option(False, "--force", "-f", help="Force overwrite of existing configuration.")
_CWD_OPTION = typer.Option(None, "--cwd", "-c", help="Working directory. Defaults to current directory.")
_SILENT_OPTION = typer.Option(False, "--silent", "-s", help="Mute output.")


def load_schema_defaults() -> dict[str, Any]:
    """Loads default values from the sygaldry.schema.json file."""
    schema_path = Path.cwd() / SCHEMA_FILE_NAME
    if not schema_path.exists():
        # Fallback to a predefined basic structure if schema is missing,
        # though in a real scenario, the schema should always be present.
        console.print(f"[yellow]Warning: {SCHEMA_FILE_NAME} not found. Using basic defaults.[/yellow]")
        return {
            "agentDirectory": "packages/sygaldry_registry/components/agents",
            "evalDirectory": "packages/sygaldry_registry/components/evals",
            "promptTemplateDirectory": "packages/sygaldry_registry/components/prompt_templates",
            "toolDirectory": "packages/sygaldry_registry/components/tools",
            "aliases": {
                "agents": "@/agents",
                "evals": "@/evals",
                "prompts": "@/prompt_templates",
                "tools": "@/tools",
            },
        }
    with open(schema_path) as f:
        schema = json.load(f)

    defaults: dict[str, Any] = {}
    properties = schema.get("properties", {})
    for key, prop_schema in properties.items():
        if "default" in prop_schema:
            defaults[key] = prop_schema["default"]
        elif prop_schema.get("type") == "object" and "properties" in prop_schema:
            defaults[key] = {}
            for sub_key, sub_prop_schema in prop_schema["properties"].items():
                if "default" in sub_prop_schema:
                    defaults[key][sub_key] = sub_prop_schema["default"]
    return defaults


@app.callback(invoke_without_command=True)
def init(
    ctx: typer.Context,
    yes: bool = _YES_OPTION,
    defaults_flag: bool = _DEFAULTS_FLAG_OPTION,
    force: bool = _FORCE_OPTION,
    cwd: Path | None = _CWD_OPTION,
    silent: bool = _SILENT_OPTION,
) -> None:
    """Interactive initialisation for sygaldry within the current project."""

    project_root = Path(cwd).resolve() if cwd else Path.cwd()

    # ------------------------------------------------------------------
    # Output helper respects --silent flag
    # ------------------------------------------------------------------

    def _print(message: str) -> None:  # noqa: D401
        """Print *message* to console unless --silent flag is set."""
        if not silent:
            console.print(message)

    # Determine default base directory for sygaldry components
    src_dir = project_root / "src"
    app_dir = project_root / "app"
    if src_dir.exists():
        default_base = src_dir / "sygaldry"
    elif app_dir.exists():
        default_base = app_dir / "sygaldry"
    else:
        default_base = project_root / "packages" / "sygaldry_registry" / "components"

    # Prompt user to confirm or override base path
    if not (yes or defaults_flag):
        from rich.prompt import Prompt

        _print(f"Detected default base directory for sygaldry components: [cyan]{default_base}[/cyan]")
        base_path_input = Prompt.ask("Base directory for sygaldry components (agents, tools, etc.)", default=str(default_base))
        base_path = Path(base_path_input)
    else:
        base_path = default_base

    config_path = project_root / CONFIG_FILE_NAME
    schema_defaults = load_schema_defaults()

    if not schema_defaults:  # Should not happen if schema is well-formed and present
        console.print("[bold red]Error: Could not load defaults from schema. Aborting.[/bold red]")
        raise typer.Exit(code=1)

    use_defaults = yes or defaults_flag
    config_exists = config_path.exists()

    if config_exists and not force:
        _print(f":sparkles: [bold green]sygaldry already initialised in[/] {project_root} ({CONFIG_FILE_NAME} exists)")
        if not use_defaults and not Confirm.ask("Overwrite existing configuration?", default=False):
            raise typer.Exit()

    config_data = {}

    if use_defaults:
        _print(f"Using default configuration based on {SCHEMA_FILE_NAME}...")
        config_data = schema_defaults.copy()
        # Ensure stream is present (default to False if missing)
        if "stream" not in config_data:
            config_data["stream"] = False
        if "responseModelDirectory" not in config_data:
            config_data["responseModelDirectory"] = str(base_path / "response_models")
        config_data["agentDirectory"] = str(base_path / "agents")
        config_data["evalDirectory"] = str(base_path / "evals")
        config_data["promptTemplateDirectory"] = str(base_path / "prompt_templates")
        config_data["toolDirectory"] = str(base_path / "tools")
    else:
        _print("Starting interactive configuration...")
        config_data["agentDirectory"] = Prompt.ask("Path to store agents", default=str(base_path / "agents"))
        config_data["evalDirectory"] = Prompt.ask("Path to store evals", default=str(base_path / "evals"))
        config_data["promptTemplateDirectory"] = Prompt.ask(
            "Path to store prompt templates", default=str(base_path / "prompt_templates")
        )
        config_data["toolDirectory"] = Prompt.ask("Path to store tools", default=str(base_path / "tools"))
        config_data["responseModelDirectory"] = Prompt.ask(
            "Path to store response models", default=str(base_path / "response_models")
        )

        aliases_defaults = schema_defaults.get("aliases", {})
        config_data["aliases"] = {
            "agents": Prompt.ask("Alias for agents", default=aliases_defaults.get("agents", "@/agents")),
            "evals": Prompt.ask("Alias for evals", default=aliases_defaults.get("evals", "@/evals")),
            "prompts": Prompt.ask("Alias for prompt templates", default=aliases_defaults.get("prompts", "@/prompt_templates")),
            "tools": Prompt.ask("Alias for tools", default=aliases_defaults.get("tools", "@/tools")),
        }

        # Prompt for default provider and model using known_llms.json
        known_llms_path = Path(__file__).parent.parent / "core" / "known_llms.json"
        known_llms = None
        if known_llms_path.exists():
            try:
                with open(known_llms_path) as f:
                    known_llms = json.load(f)
            except Exception:
                known_llms = None

        if known_llms:
            provider_list = list(known_llms.keys())
            _print("\nSelect a default LLM provider:")
            for idx, prov in enumerate(provider_list, 1):
                _print(f"  {idx}. {prov}")
            while True:
                provider_choice = Prompt.ask(
                    "Enter number for provider",
                    default=str(
                        provider_list.index(schema_defaults.get("defaultProvider", "openai")) + 1
                        if schema_defaults.get("defaultProvider", "openai") in provider_list
                        else 1
                    ),
                )
                try:
                    provider_idx = int(provider_choice) - 1
                    if 0 <= provider_idx < len(provider_list):
                        provider = provider_list[provider_idx]
                        break
                except Exception:
                    pass
                _print("[red]Invalid selection. Please enter a valid number.[/red]")
            config_data["defaultProvider"] = provider

            # Now select model for provider
            model_list = known_llms[provider]["models"]
            _print(f"\nSelect a default model for {provider}:")
            for idx, model in enumerate(model_list, 1):
                _print(f"  {idx}. {model}")
            while True:
                model_choice = Prompt.ask(
                    "Enter number for model",
                    default=str(
                        model_list.index(schema_defaults.get("defaultModel", "gpt-4o-mini")) + 1
                        if schema_defaults.get("defaultModel", "gpt-4o-mini") in model_list
                        else 1
                    ),
                )
                try:
                    model_idx = int(model_choice) - 1
                    if 0 <= model_idx < len(model_list):
                        model = model_list[model_idx]
                        break
                except Exception:
                    pass
                _print("[red]Invalid selection. Please enter a valid number.[/red]")
            config_data["defaultModel"] = model

            # Prompt for stream option
            config_data["stream"] = Confirm.ask(
                "Enable streaming responses by default?", default=schema_defaults.get("stream", False)
            )
        else:
            # Fallback to free text prompt
            config_data["defaultProvider"] = Prompt.ask(
                "Default LLM provider for agents/tools", default=schema_defaults.get("defaultProvider", "openai")
            )
            config_data["defaultModel"] = Prompt.ask(
                "Default model for agents/tools", default=schema_defaults.get("defaultModel", "gpt-4o-mini")
            )

            # Prompt for stream option
            config_data["stream"] = Confirm.ask(
                "Enable streaming responses by default?", default=schema_defaults.get("stream", False)
            )

    # Add $schema key
    config_data["$schema"] = f"./{SCHEMA_FILE_NAME}"

    # Add default registry configuration
    config_data["registry_sources"] = {
        "default": "https://raw.githubusercontent.com/sygaldry-ai/sygaldry-registry/main/index.json"
    }
    config_data["default_registry_url"] = "https://raw.githubusercontent.com/sygaldry-ai/sygaldry-registry/main/index.json"

    # Ensure directories exist
    # Collect all unique directory paths that need to be created
    directories_to_create = {
        config_data["agentDirectory"],
        config_data["evalDirectory"],
        config_data["promptTemplateDirectory"],
        config_data["toolDirectory"],
        config_data["responseModelDirectory"],
    }
    for directory_str in directories_to_create:
        if directory_str:  # Ensure not empty
            dir_path = project_root / directory_str
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                _print(f"Ensured directory exists: [cyan]{dir_path}[/cyan]")
            except PermissionError as e:
                console.print(f"[bold red]Permission denied: Cannot create directory {dir_path}[/bold red]")
                console.print("[yellow]Please check that you have write permissions for this location.[/yellow]")
                raise typer.Exit(code=1) from e
            except Exception as e:
                console.print(f"[bold red]Error creating directory {dir_path}: {e}[/bold red]")
                raise typer.Exit(code=1) from e

    try:
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)  # Using indent 2 like shadcn
        _print(f":white_check_mark: [bold green]sygaldry initialised![/] Configuration saved to {config_path}")
    except OSError as e:
        console.print(f"[bold red]Error writing configuration file {config_path}: {e}[/bold red]")
        raise typer.Exit(code=1) from e

    # Optionally also update .gitignore (if .sygaldry/ is still used or other patterns are needed)
    gitignore_path = project_root / ".gitignore"
    gitignore_patterns_to_add = [".sygaldry/"]  # Add other patterns if needed

    try:
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                gitignore_content = f.read().splitlines()
        else:
            gitignore_content = []

        updated = False
        for pattern in gitignore_patterns_to_add:
            if pattern not in gitignore_content:
                gitignore_content.append(pattern)
                updated = True

        if updated or not gitignore_path.exists():
            with open(gitignore_path, "w") as f:
                f.write("\\n".join(gitignore_content) + "\\n")
            _print(f"Updated [cyan]{gitignore_path}[/cyan]")
    except OSError as e:
        console.print(f"[yellow]Warning: Could not update .gitignore: {e}[/yellow]")

    # ------------------------------------------------------------------
    # Optional: interactive component addition flow
    # ------------------------------------------------------------------

    if not silent and Confirm.ask("Would you like to add components now?", default=False):
        _interactive_component_addition(project_root, silent)


# ------------------------------------------------------------------
# Interactive helper for adding components immediately after init
# ------------------------------------------------------------------


def _interactive_component_addition(project_root: Path, silent: bool) -> None:  # noqa: D401
    """Guide the user through adding one or more components interactively."""

    from rich.prompt import Confirm  # Local import to avoid unnecessary load
    from sygaldry_cli.config_manager import ConfigManager
    from sygaldry_cli.core.component_manager import ComponentManager

    cfg_mgr = ConfigManager(project_root=project_root)
    manager = ComponentManager(cfg=cfg_mgr)

    def _iprint(msg: str) -> None:  # internal print respecting *silent*
        if not silent:
            console.print(msg)

    _iprint("\n[bold]Add components[/] – Leave the name empty to finish.\n")

    while True:
        identifier = Prompt.ask("Component name or manifest URL (blank to finish)", default="").strip()
        if not identifier:
            break

        provider = Prompt.ask("LLM provider (blank for default)", default="") or None
        model = Prompt.ask("Model name (blank for default)", default="") or None
        with_lilypad = Confirm.ask("Enable lilypad tracing?", default=False)

        try:
            manager.add_component(identifier, provider=provider, model=model, with_lilypad=with_lilypad)
        except SystemExit:
            # ComponentManager internally exits; just continue loop
            continue
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error adding component '{identifier}': {exc}")

    _iprint("\n[green]Done adding components.[/]")


if __name__ == "__main__":  # For testing the script directly
    app()
