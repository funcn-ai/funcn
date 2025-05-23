from __future__ import annotations

from funcn_cli.config_manager import ConfigManager
from funcn_cli.core.registry_handler import RegistryHandler
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()


class ComponentManager:
    def __init__(self, cfg: ConfigManager | None = None):
        self._cfg = cfg or ConfigManager()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_component(self, identifier: str, *, provider: str | None = None, model: str | None = None, with_lilypad: bool = False, stream: bool | None = None, _added: set[str] | None = None) -> None:
        """Add a component into the current project.

        *identifier* can be a component name (to be resolved via registry) or a
        direct HTTPS URL to a `component.json` manifest.
        """
        if _added is None:
            _added = set()
        if identifier in _added:
            return
        _added.add(identifier)
        with RegistryHandler(self._cfg) as rh:
            if identifier.startswith("http://") or identifier.startswith("https://"):
                manifest_url = identifier
            else:
                manifest_url = rh.find_component_manifest_url(identifier)
                if manifest_url is None:
                    console.print(f"[red]Could not find component '{identifier}' in registry.")
                    raise SystemExit(1)

            manifest = rh.fetch_manifest(manifest_url)
            target_dir_key = manifest.target_directory_key

            # Resolve effective template variables
            template_vars: dict[str, str] = {}
            if manifest.template_variables:
                template_vars.update(manifest.template_variables)
                # Store defaults for replacement logic in _render_template
                if "provider" in manifest.template_variables:
                    template_vars["_default_provider"] = manifest.template_variables["provider"]
                if "model" in manifest.template_variables:
                    template_vars["_default_model"] = manifest.template_variables["model"]
                if "stream" in manifest.template_variables:
                    template_vars["_default_stream"] = manifest.template_variables["stream"]
            if provider:
                template_vars["provider"] = provider
            if model:
                template_vars["model"] = model
            # Add stream support
            if stream is not None:
                template_vars["stream"] = str(stream)
            else:
                # Use config default if not provided
                config_stream = getattr(self._cfg.config, "stream", False)
                template_vars["stream"] = str(config_stream)

            # Determine lilypad flag – CLI overrides manifest default
            enable_lilypad = bool(with_lilypad)

            target_root_relative = self._cfg.config.component_paths.dict()[target_dir_key]
            project_root = self._cfg.project_root
            component_root = project_root / target_root_relative / manifest.name

            if component_root.exists():
                console.print(f"[yellow]Component '{manifest.name}' already exists at {component_root}")
                return

            # Determine base URL for raw files (manifest_url minus filename)
            base_url = manifest_url.rsplit("/", 1)[0]

            # Copy and render files
            for mapping in manifest.files_to_copy:
                source_url = f"{base_url}/{mapping.source}"
                dest_path = component_root / mapping.destination
                rh.download_file(source_url, dest_path)

                # Render template placeholders for .py and .txt files
                if dest_path.suffix in {".py", ".txt", ".md"}:
                    self._render_template(dest_path, template_vars, enable_lilypad)

            console.print(f":white_check_mark: [bold green]Component '{manifest.name}' added successfully![/]")
            if manifest.post_add_instructions:
                console.print(f"\n[blue]Notes:[/]\n{manifest.post_add_instructions}")

            if manifest.python_dependencies:
                deps = " ".join(manifest.python_dependencies)
                console.print(
                    f"\n[bold]Next steps:[/] Install Python packages with:\n  uv pip install {deps}"
                )

            # Suggest lilypad install if enabled but not declared in manifest deps
            if enable_lilypad:
                if not any(dep.startswith("lilypad") for dep in manifest.python_dependencies):
                    console.print("  uv pip install lilypad")
                console.print(
                    "[cyan]Lilypad tracing enabled.[/] Ensure LILYPAD_PROJECT_ID and LILYPAD_API_KEY environment variables are set."
                )

            # Prompt for registry dependencies
            if manifest.registry_dependencies:
                for dep in manifest.registry_dependencies:
                    if Confirm.ask(f"Component '{manifest.name}' requires dependency '{dep}'. Add it now?", default=True):
                        self.add_component(dep, provider=provider, model=model, with_lilypad=with_lilypad, stream=stream, _added=_added)
                    else:
                        console.print(f"[yellow]Skipped dependency '{dep}'. You can add it later with: funcn add {dep}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _render_template(file_path: Path, variables: dict[str, str], enable_lilypad: bool) -> None:
        """Replace simple placeholder tokens in *file_path* in-place."""
        try:
            text = file_path.read_text()
        except UnicodeDecodeError:
            # Binary or non-text files – skip
            return

        # Provider/Model/Stream replacement (more robust)
        default_provider = variables.get("_default_provider")
        default_model = variables.get("_default_model")
        default_stream = variables.get("_default_stream", False)
        target_provider = variables.get("provider")
        target_model = variables.get("model")
        target_stream = variables.get("stream", False)

        if default_provider and target_provider and default_provider != target_provider:
            text = text.replace(f'provider="{default_provider}"', f'provider="{target_provider}"')
            text = text.replace(f'provider=\'{default_provider}\'', f'provider=\'{target_provider}\'')
        if default_model and target_model and default_model != target_model:
            text = text.replace(f'model="{default_model}"', f'model="{target_model}"')
            text = text.replace(f'model=\'{default_model}\'', f'model=\'{target_model}\'')
        # Stream replacement (bool, so match True/False or true/false)
        if default_stream != target_stream:
            # Replace both True/False and true/false
            text = text.replace(f'stream={str(default_stream)}', f'stream={str(target_stream)}')
            text = text.replace(f'stream={str(default_stream).lower()}', f'stream={str(target_stream).lower()}')

        # Lilypad placeholders
        if enable_lilypad:
            text = text.replace("# FUNCN_LILYPAD_IMPORT_PLACEHOLDER", "import lilypad")
            text = text.replace(
                "# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER",
                '''# Configure Lilypad (ensure LILYPAD_PROJECT_ID and LILYPAD_API_KEY are set in your environment)
lilypad.configure(auto_llm=True)'''
            )
            # Add default trace decorator if placeholder present
            if "# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER" in text:
                obj_name = file_path.stem # e.g., echo_agent or random_joke_tool
                if obj_name.endswith("_tool"):
                    obj_name = obj_name[:-5] # remove _tool suffix
                if obj_name.endswith("_agent"):
                    obj_name = obj_name[:-6] # remove _agent suffix

                text = text.replace(
                    "# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER",
                    f"@lilypad.trace(name=\"{obj_name.replace('_', '-')}\", versioning=\"automatic\")",
                )
        else:
            # Remove placeholder comment lines entirely if Lilypad is not enabled
            text = text.replace("# FUNCN_LILYPAD_IMPORT_PLACEHOLDER\n", "")
            text = text.replace("# FUNCN_LILYPAD_CONFIGURE_PLACEHOLDER\n", "")
            text = text.replace("# FUNCN_LILYPAD_DECORATOR_PLACEHOLDER\n", "")

        # Collapse multiple blank lines that may result
        # Use a more robust approach to handle consecutive blank lines
        lines = text.splitlines()
        processed_lines = []
        consecutive_empty = 0

        for line in lines:
            if line.strip() == "":
                consecutive_empty += 1
                if consecutive_empty <= 1:  # Allow only 1 consecutive empty line
                    processed_lines.append(line)
            else:
                consecutive_empty = 0
                processed_lines.append(line)

        text = "\n".join(processed_lines)

        file_path.write_text(text)
