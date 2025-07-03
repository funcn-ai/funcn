from importlib import metadata as _metadata

__version__: str | None
try:
    __version__ = _metadata.version("sygaldry")
except _metadata.PackageNotFoundError:  # pragma: no cover — packaged context only
    __version__ = None

__all__ = ["__version__"]
