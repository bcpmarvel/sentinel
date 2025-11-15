from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore


def load_config_file(config_path: str | Path) -> dict[str, Any]:
    """Load configuration from TOML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "rb") as f:
        return tomllib.load(f)


def merge_config(
    base_config: dict[str, Any], file_config: dict[str, Any]
) -> dict[str, Any]:
    """Merge file config into base config, with file config taking precedence."""
    merged = base_config.copy()
    for key, value in file_config.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_config(merged[key], value)
        else:
            merged[key] = value
    return merged
