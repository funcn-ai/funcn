from __future__ import annotations

from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from sygaldry_cli.config_manager import ConfigManager
from sygaldry_cli.core.registry_handler import RegistryHandler

console = Console()


class ComponentManager:
    def __init__(self, cfg: ConfigManager | None = None):
        self._cfg = cfg or ConfigManager()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_component(
        self,
        identifier: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        with_lilypad: bool = False,
        stream: bool | None = None,
        source_alias: str | None = None,
        _added: set[str] | None = None,
    ) -> None:
        """Add a component into the current project.

        *identifier* can be:
        - A component name (to be resolved via registry)
        - A component name with version (e.g., 'component@1.0.0')
        - A direct HTTPS URL to a `component.json` manifest
        """
        if _added is None:
            _added = set()
        if identifier in _added:
            return
        _added.add(identifier)

        # Parse version from identifier if present
        component_name = identifier
        component_version = None

        with RegistryHandler(self._cfg) as rh:
            if identifier.startswith("http://") or identifier.startswith("https://"):
                manifest_url = identifier
            else:
                # Check if version is specified using @ syntax
                if "@" in identifier:
                    parts = identifier.split("@", 1)
                    component_name = parts[0]
                    component_version = parts[1]

                    # Basic version format validation
                    if not component_version or not all(c.isdigit() or c == '.' for c in component_version):
                        console.print(f"[red]Invalid version format '{component_version}'. Expected format like '1.0.0'.")
                        raise SystemExit(1)

                manifest_url = rh.find_component_manifest_url(component_name, version=component_version, source_alias=source_alias)
                if manifest_url is None:
                    if component_version:
                        error_msg = f"[red]Could not find component '{component_name}' version '{component_version}'"
                    else:
                        error_msg = f"[red]Could not find component '{component_name}'"

                    if source_alias:
                        error_msg += f" in source '{source_alias}'."
                    else:
                        error_msg += " in any configured registry source."

                    console.print(error_msg)
                    raise SystemExit(1)

            manifest = rh.fetch_manifest(manifest_url)
            target_dir_key = manifest.target_directory_key

            # Resolve effective template variables
            template_vars: dict[str, str] = {}
            custom_template_vars: dict[str, str] = {}

            if manifest.template_variables:
                # Handle both list and dict formats
                if isinstance(manifest.template_variables, list):
                    # New format: list of TemplateVariable objects
                    from rich.prompt import Prompt
                    for var in manifest.template_variables:
                        custom_template_vars[var.name] = var.default
                        # Prompt for value with default
                        value = Prompt.ask(
                            f"[cyan]{var.description}[/cyan]",
                            default=var.default
                        )
                        template_vars[var.name] = value
                else:
                    # Legacy format: dict
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

            target_root_relative = self._cfg.config.component_paths.model_dump()[target_dir_key]
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

                # Render template placeholders for text files
                if dest_path.suffix in {".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".sh", ".bash"}:
                    self._render_template(dest_path, template_vars, enable_lilypad)

            console.print(f":white_check_mark: [bold green]Component '{manifest.name}' added successfully![/]")
            if manifest.post_add_instructions:
                console.print(f"\n[blue]Notes:[/]\n{manifest.post_add_instructions}")

            if manifest.python_dependencies:
                deps = " ".join(manifest.python_dependencies)
                console.print(f"\n[bold]Next steps:[/] Install Python packages with:\n  uv pip install {deps}")

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
                        self.add_component(
                            dep, provider=provider, model=model, with_lilypad=with_lilypad, stream=stream, source_alias=source_alias, _added=_added
                        )
                    else:
                        console.print(f"[yellow]Skipped dependency '{dep}'. You can add it later with: sygaldry add {dep}")

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
            text = text.replace("# SYGALDRY_LILYPAD_IMPORT_PLACEHOLDER", "import lilypad")
            text = text.replace(
                "# SYGALDRY_LILYPAD_CONFIGURE_PLACEHOLDER",
                '''# Configure Lilypad (ensure LILYPAD_PROJECT_ID and LILYPAD_API_KEY are set in your environment)
lilypad.configure(auto_llm=True)''',
            )
            # Add default trace decorator if placeholder present
            if "# SYGALDRY_LILYPAD_DECORATOR_PLACEHOLDER" in text:
                obj_name = file_path.stem  # e.g., echo_agent or random_joke_tool
                if obj_name.endswith("_tool"):
                    obj_name = obj_name[:-5]  # remove _tool suffix
                if obj_name.endswith("_agent"):
                    obj_name = obj_name[:-6]  # remove _agent suffix

                text = text.replace(
                    "# SYGALDRY_LILYPAD_DECORATOR_PLACEHOLDER",
                    f"@lilypad.trace(name=\"{obj_name.replace('_', '-')}\", versioning=\"automatic\")",
                )
        else:
            # Remove placeholder comment lines entirely if Lilypad is not enabled
            text = text.replace("# SYGALDRY_LILYPAD_IMPORT_PLACEHOLDER\n", "")
            text = text.replace("# SYGALDRY_LILYPAD_CONFIGURE_PLACEHOLDER\n", "")
            text = text.replace("# SYGALDRY_LILYPAD_DECORATOR_PLACEHOLDER\n", "")

        # General template variable substitution
        # Handle {{variable}} and {{variable|transformation}} syntax
        import re

        def replace_template_var(match):
            var_expr = match.group(1)
            if '|' in var_expr:
                var_name, transform = var_expr.split('|', 1)
            else:
                var_name, transform = var_expr, None

            var_name = var_name.strip()
            if var_name in variables:
                value = variables[var_name]
                if transform:
                    transform = transform.strip()
                    if transform == 'lower':
                        value = value.lower()
                    elif transform == 'upper':
                        value = value.upper()
                    elif transform == 'title':
                        # Convert snake_case or camelCase to Title Case
                        value = value.replace('_', ' ').replace('-', ' ')
                        value = ''.join(word.capitalize() for word in value.split())
                        value = value.replace(' ', '_')  # Preserve underscores in title case
                return value
            return match.group(0)  # Return unchanged if variable not found

        # Replace template variables
        text = re.sub(r'\{\{([^}]+)\}\}', replace_template_var, text)

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
