from __future__ import annotations

from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

# ---------------------------------------------------------------------------
# Manifest Schema
# ---------------------------------------------------------------------------

KebabCaseStr = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]


class Author(BaseModel):
    name: str
    email: str | None = None


class FileMapping(BaseModel):
    source: str
    destination: str


class TemplateVariable(BaseModel):
    name: str
    description: str
    default: str


class ComponentManifest(BaseModel):
    name: KebabCaseStr
    version: str
    description: str
    type: str  # "agent" | "tool"
    authors: list[Author]
    license: str
    mirascope_version_min: str = Field(alias="mirascope_version_min")
    files_to_copy: list[FileMapping]
    target_directory_key: str
    python_dependencies: list[str] = Field(default_factory=list)
    registry_dependencies: list[str] = Field(default_factory=list)
    environment_variables: list[str] = Field(default_factory=list)
    post_add_instructions: str | None = None
    tags: list[str] = Field(default_factory=list)
    supports_lilypad: bool | None = False  # Whether component supports optional lilypad integration
    template_variables: list[TemplateVariable] | dict[str, str] | None = None  # Template variables for substitution

    model_config = {
        "str_strip_whitespace": True,
        "populate_by_name": True
    }


# ---------------------------------------------------------------------------
# Registry Index Schema
# ---------------------------------------------------------------------------


class RegistryComponentEntry(BaseModel):
    name: str
    version: str
    type: str
    description: str
    manifest_path: str


class RegistryIndex(BaseModel):
    registry_version: str
    components: list[RegistryComponentEntry]
