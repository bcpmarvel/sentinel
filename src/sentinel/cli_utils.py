from enum import Enum
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.theme import Theme

# Custom theme for consistent branding
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
})

console = Console(theme=custom_theme)


class OutputMode(str, Enum):
    NORMAL = "normal"
    QUIET = "quiet"
    VERBOSE = "verbose"
    JSON = "json"


def print_banner() -> None:
    """Display welcome banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║   SENTINEL - CV Detection & Tracking  ║
    ╚═══════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def print_config_table(config: dict[str, str]) -> None:
    """Display configuration in a formatted table."""
    table = Table(title="Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Parameter", style="cyan", width=20)
    table.add_column("Value", style="green")

    for key, value in config.items():
        table.add_row(key, str(value))

    console.print(table)


def create_progress() -> Progress:
    """Create a Rich progress bar for video processing."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"✓ {message}", style="success")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"✗ {message}", style="error")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"⚠ {message}", style="warning")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"ℹ {message}", style="info")


def print_panel(message: str, title: str = "", style: str = "info") -> None:
    """Print message in a panel."""
    console.print(Panel(message, title=title, border_style=style))


def validate_file_path(path: str | None, required: bool = False) -> Path | None:
    """Validate file path and return Path object."""
    if path is None:
        if required:
            print_error("File path is required")
            raise ValueError("File path required")
        return None

    file_path = Path(path)
    if not file_path.exists():
        print_error(f"File not found: {path}")
        raise FileNotFoundError(f"File not found: {path}")

    return file_path
