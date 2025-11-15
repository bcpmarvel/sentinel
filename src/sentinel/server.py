from typing import Annotated, Optional

import typer
import uvicorn
from rich.panel import Panel

from sentinel.cli_utils import console, print_banner, print_info, print_success
from sentinel.config import settings

app = typer.Typer(
    name="serve",
    help="Start FastAPI server for object detection API",
    add_completion=True,
    rich_markup_mode="rich",
)


@app.command()
def run(
    host: Annotated[
        Optional[str],
        typer.Option("--host", "-h", help="Server host address"),
    ] = None,
    port: Annotated[
        Optional[int],
        typer.Option("--port", "-p", help="Server port", min=1, max=65535),
    ] = None,
    reload: Annotated[
        bool,
        typer.Option("--reload", "-r", help="Enable auto-reload for development"),
    ] = False,
    workers: Annotated[
        int,
        typer.Option("--workers", "-w", help="Number of worker processes", min=1),
    ] = 1,
) -> None:
    """Start the FastAPI REST API server for object detection."""
    print_banner()

    server_host = host or settings.api_host
    server_port = port or settings.api_port

    info_text = f"""
    [bold cyan]Server Configuration[/]

    [cyan]Host:[/] {server_host}
    [cyan]Port:[/] {server_port}
    [cyan]Workers:[/] {workers}
    [cyan]Reload:[/] {'✓' if reload else '✗'}

    [bold green]Endpoints:[/]
    • [green]POST[/] /api/detect - Object detection
    • [green]GET[/]  /api/health - Health check
    • [green]GET[/]  / - API documentation

    [dim]Press Ctrl+C to stop[/]
    """

    console.print(Panel(info_text, border_style="cyan", title="API Server"))
    print_info("Starting server...")

    try:
        uvicorn.run(
            "sentinel.api.app:app",
            host=server_host,
            port=server_port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level="info",
        )
    except KeyboardInterrupt:
        print_success("Server stopped")
        raise typer.Exit(0)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-v", help="Show version and exit"),
    ] = False,
) -> None:
    """Sentinel API Server."""
    if version:
        console.print("[bold cyan]Sentinel API Server[/] version [green]0.1.0[/]")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        ctx.invoke(run)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
