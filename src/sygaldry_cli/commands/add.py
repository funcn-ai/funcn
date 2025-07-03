from __future__ import annotations

import json
import typer
from pathlib import Path
from rich.console import Console
from sygaldry_cli.config_manager import ConfigManager
from sygaldry_cli.core.component_manager import ComponentManager

console = Console()

app = typer.Typer(help="Add a component to the current project.")


def _get_known_providers_help() -> str:
    try:
        known_llms_path = Path(__file__).parent.parent / "core" / "known_llms.json"
        if known_llms_path.exists():
            with open(known_llms_path) as f:
                data = json.load(f)
            providers = list(data.keys())
            if providers:
                return f"LLM provider to use (e.g., {', '.join(providers[:3])}, ...). See full list in sygaldry_cli/core/known_llms.json."
    except Exception:
        pass  # Fallback to default help
    return "LLM provider to use (e.g., openai, anthropic). Check documentation for more."


@app.callback(invoke_without_command=True)
def add(  # noqa: D401 – CLI entry-point
    _ctx: typer.Context,
    identifier: str | None = typer.Argument(None, help="Component name or manifest URL", show_default=False),
    provider: str | None = typer.Option(None, "--provider", help=_get_known_providers_help(), show_default=False),
    model: str | None = typer.Option(
        None,
        "--model",
        help="Model name to use (e.g., gpt-4o-mini). Refer to provider docs or sygaldry_cli/core/known_llms.json.",
        show_default=False,
    ),
    with_lilypad: bool = typer.Option(False, "--with-lilypad", help="Include lilypad tracing decorators"),
    stream: bool | None = typer.Option(
        None, "--stream", help="Enable streaming responses for this component (overrides config)", show_default=False
    ),
    source: str | None = typer.Option(None, "--source", help="Registry source alias to search for component"),
) -> None:
    """Add a component to the current project.

    When *identifier* is not provided, the command runs in interactive mode,
    guiding the user through the required prompts.
    """

    from rich.prompt import Confirm, Prompt

    # Load config for defaults
    cfg_mgr = ConfigManager()
    config = cfg_mgr.config
    default_provider = getattr(config, "defaultProvider", None) or getattr(config, "default_provider", None) or "openai"
    default_model = getattr(config, "defaultModel", None) or getattr(config, "default_model", None) or "gpt-4o-mini"
    default_stream = getattr(config, "stream", False)

    # Interactive prompts when identifier missing or flags omitted
    if identifier is None:
        identifier = Prompt.ask("Component name or manifest URL").strip()

    if not provider:
        provider = Prompt.ask("LLM provider (blank for default)", default=default_provider) or default_provider

    if not model:
        model = Prompt.ask("Model name (blank for default)", default=default_model) or default_model

    if not with_lilypad:
        with_lilypad = Confirm.ask("Enable lilypad tracing?", default=False)

    if stream is None:
        stream = Confirm.ask("Enable streaming responses?", default=default_stream)

    manager = ComponentManager(cfg=cfg_mgr)
    manager.add_component(identifier, provider=provider, model=model, with_lilypad=with_lilypad, stream=stream, source_alias=source)
