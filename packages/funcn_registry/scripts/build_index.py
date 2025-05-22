from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

# Re-use models from the main funcn package
try:
    from funcn_cli.core.models import (
        ComponentManifest,
        RegistryComponentEntry,
        RegistryIndex,
    )
except ModuleNotFoundError as exc:  # pragma: no cover
    print(
        "[build_index] Could not import funcn_cli models. Ensure the project root is on PYTHONPATH.",
        file=sys.stderr,
    )
    raise exc

console = Console()

REGISTRY_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REGISTRY_ROOT / "components"
INDEX_PATH = REGISTRY_ROOT / "index.json"
REGISTRY_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iter_manifest_paths(base_dir: Path) -> Iterable[Path]:
    """Yield all funcn_component.json paths under *base_dir*."""
    for path in base_dir.rglob("funcn_component.json"):
        yield path


# ---------------------------------------------------------------------------
# Main build routine
# ---------------------------------------------------------------------------

def build_index() -> None:
    component_entries: list[RegistryComponentEntry] = []
    validation_errors: dict[str, str] = {}

    for manifest_path in iter_manifest_paths(COMPONENTS_DIR):
        try:
            manifest_data = json.loads(manifest_path.read_text())
            manifest = ComponentManifest.model_validate(manifest_data)
        except (json.JSONDecodeError, ValidationError) as exc:
            validation_errors[str(manifest_path)] = str(exc)
            continue

        relative_manifest_path = manifest_path.relative_to(REGISTRY_ROOT)
        entry = RegistryComponentEntry(
            name=manifest.name,
            version=manifest.version,
            type=manifest.type,
            description=manifest.description,
            manifest_path=str(relative_manifest_path),
        )
        component_entries.append(entry)

    # Report validation failures (if any) in a nice table
    if validation_errors:
        table = Table(title="Manifest validation errors", show_header=True, header_style="bold red")
        table.add_column("Manifest Path", style="cyan")
        table.add_column("Error")
        for path_str, err in validation_errors.items():
            table.add_row(path_str, err)
        console.print(table)
        console.print("\n[red]Aborting index build due to validation errors.")
        sys.exit(1)

    # Build registry index
    index = RegistryIndex(registry_version=REGISTRY_VERSION, components=component_entries)
    INDEX_PATH.write_text(json.dumps(index.model_dump(mode="json"), indent=2))
    console.print(f":white_check_mark: [green]index.json generated with {len(component_entries)} components.")


if __name__ == "__main__":
    build_index()
