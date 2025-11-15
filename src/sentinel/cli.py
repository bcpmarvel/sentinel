from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import questionary
import typer
from rich.console import Console
from rich.status import Status

from sentinel.analytics.service import AnalyticsService
from sentinel.analytics.utils import load_zones_from_json
from sentinel.cli_utils import (
    OutputMode,
    console,
    print_banner,
    print_config_table,
    print_error,
    print_info,
    print_panel,
    print_success,
    print_warning,
)
from sentinel.config import settings
from sentinel.config_loader import load_config_file
from sentinel.detection.models import YOLODetector
from sentinel.detection.service import DetectionService
from sentinel.logging import configure_logging
from sentinel.pipeline import VideoPipeline
from sentinel.visualization.annotators import Annotators

app = typer.Typer(
    name="detect",
    help="Real-time object detection and tracking with YOLO",
    add_completion=True,
    rich_markup_mode="rich",
)


class Device(str, Enum):
    MPS = "mps"
    CUDA = "cuda"
    CPU = "cpu"


@app.command()
def run(
    source: Annotated[
        Optional[str],
        typer.Option(
            "--source",
            "-s",
            help="Video source (webcam index or file path). Examples: 0 (webcam), video.mp4",
        ),
    ] = None,
    conf: Annotated[
        Optional[float],
        typer.Option(
            "--conf",
            "-c",
            min=0.0,
            max=1.0,
            help="Confidence threshold for detections (0.0-1.0)",
        ),
    ] = None,
    device: Annotated[
        Optional[Device],
        typer.Option("--device", "-d", help="Device for inference", case_sensitive=False),
    ] = None,
    track: Annotated[
        bool,
        typer.Option("--track", "-t", help="Enable multi-object tracking"),
    ] = False,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Path to YOLO model file"),
    ] = None,
    analytics: Annotated[
        bool,
        typer.Option("--analytics", "-a", help="Enable zone-based analytics"),
    ] = False,
    zones: Annotated[
        Optional[str],
        typer.Option("--zones", "-z", help="Path to zones configuration JSON file"),
    ] = None,
    output: Annotated[
        OutputMode,
        typer.Option("--output", "-o", help="Output mode"),
    ] = OutputMode.NORMAL,
    interactive: Annotated[
        bool,
        typer.Option("--interactive", "-i", help="Enable interactive prompts for missing arguments"),
    ] = False,
    config_file: Annotated[
        Optional[str],
        typer.Option("--config", help="Load settings from TOML config file"),
    ] = None,
) -> None:
    """Run real-time object detection and tracking on video source."""

    # Configure logging
    configure_logging(use_rich=(output != OutputMode.JSON))

    if output != OutputMode.QUIET:
        print_banner()

    # Load config file if provided
    file_config = {}
    if config_file:
        try:
            file_config = load_config_file(config_file)
            print_success(f"Loaded config from {config_file}")
        except Exception as e:
            print_error(f"Failed to load config file: {e}")
            raise typer.Exit(1)

    # Interactive prompts if enabled and source is missing
    if interactive and source is None:
        source = questionary.text(
            "Enter video source (webcam index or file path):",
            default="0",
        ).ask()

    # Parse source (webcam index or file path) with config file fallback
    parsed_source = int(source) if source and source.isdigit() else source or file_config.get("video_source", settings.video_source)
    selected_device = device.value if device else file_config.get("device", settings.device)
    model_path = Path(model) if model else Path(file_config.get("model_path", settings.model_path))
    conf_threshold = conf if conf is not None else file_config.get("conf_threshold", settings.conf_threshold)

    # Validate analytics requires tracking
    if analytics and not track:
        print_error("Analytics requires tracking to be enabled")
        print_info("Use --track flag along with --analytics")
        raise typer.Exit(1)

    # Display configuration
    if output == OutputMode.VERBOSE or output == OutputMode.NORMAL:
        config_display = {
            "Source": str(parsed_source),
            "Model": str(model_path),
            "Device": selected_device,
            "Confidence": f"{conf_threshold:.2f}",
            "Tracking": "✓" if track else "✗",
            "Analytics": "✓" if analytics else "✗",
        }
        print_config_table(config_display)

    # Initialize detector with spinner
    with Status("[bold cyan]Loading YOLO model...", console=console) as status:
        try:
            detector = YOLODetector(model_path, selected_device)
            status.update("[bold green]Model loaded successfully!")
        except Exception as e:
            print_error(f"Failed to load model: {e}")
            raise typer.Exit(1)

    print_success(f"Model loaded: {model_path.name}")

    # Initialize detection service
    detection_service = DetectionService(
        detector=detector,
        enable_tracking=track,
        conf_threshold=conf_threshold,
    )

    # Initialize analytics if enabled
    analytics_service = None
    zone_configs = []
    if analytics:
        zones_path = Path(zones) if zones else settings.zones_config_path
        if not zones_path.exists():
            print_error(f"Zones configuration file not found: {zones_path}")
            if interactive:
                zones = questionary.path("Enter path to zones JSON file:").ask()
                zones_path = Path(zones)
                if not zones_path.exists():
                    raise typer.Exit(1)
            else:
                raise typer.Exit(1)

        with Status("[bold cyan]Loading zone configurations...", console=console):
            zone_configs = load_zones_from_json(zones_path)
            analytics_service = AnalyticsService(zone_configs)

        print_success(f"Loaded {len(zone_configs)} zone(s) for analytics")

    # Initialize annotators
    annotators = Annotators(enable_tracking=track, zone_configs=zone_configs)

    # Run pipeline
    if output != OutputMode.QUIET:
        print_panel(
            "Press 'q' to quit\nPress 'p' to pause/resume",
            title="Controls",
            style="cyan",
        )
        print_info("Starting video pipeline...")

    try:
        pipeline = VideoPipeline(detection_service, annotators, analytics_service)
        pipeline.run(parsed_source)
        print_success("Pipeline finished successfully")
    except KeyboardInterrupt:
        print_warning("Interrupted by user")
        raise typer.Exit(0)
    except Exception as e:
        print_error(f"Pipeline error: {e}")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-v", help="Show version and exit"),
    ] = False,
) -> None:
    """Sentinel - Real-time object detection and tracking."""
    if version:
        console.print("[bold cyan]Sentinel[/] version [green]0.1.0[/]")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        # If no subcommand, run the main command
        ctx.invoke(run)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
