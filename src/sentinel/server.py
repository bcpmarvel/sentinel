from typing import Annotated, Optional

import typer
import uvicorn

from sentinel.config import settings

app = typer.Typer(help="Start FastAPI server for object detection")


@app.command()
def main(
    host: Annotated[
        Optional[str], typer.Option("--host", "-h", help="Server host")
    ] = None,
    port: Annotated[
        Optional[int],
        typer.Option("--port", "-p", help="Server port", min=1, max=65535),
    ] = None,
    reload: Annotated[
        bool, typer.Option("--reload", "-r", help="Enable auto-reload")
    ] = False,
    workers: Annotated[
        int, typer.Option("--workers", "-w", help="Worker processes", min=1)
    ] = 1,
) -> None:
    """Start the FastAPI REST API server."""
    uvicorn.run(
        "sentinel.api.app:app",
        host=host or settings.api_host,
        port=port or settings.api_port,
        reload=reload,
        workers=workers if not reload else 1,
    )


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
