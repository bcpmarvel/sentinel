import tomllib
from pathlib import Path
from typing import Any


def load_config_file(config_path: str | Path) -> dict[str, Any]:
    """Load configuration from TOML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "rb") as f:
        return tomllib.load(f)
