from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "error": "bold red",
    "success": "bold green",
})

console = Console(theme=custom_theme)


def print_success(message: str) -> None:
    console.print(f"✓ {message}", style="success")


def print_error(message: str) -> None:
    console.print(f"✗ {message}", style="error")
