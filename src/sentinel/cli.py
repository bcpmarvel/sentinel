from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.status import Status

from sentinel.analytics.service import AnalyticsService
from sentinel.analytics.utils import load_zones_from_json
from sentinel.cli_utils import console, print_error, print_success
from sentinel.config import settings
from sentinel.config_loader import load_config_file
from sentinel.detection.models import YOLODetector
from sentinel.detection.service import DetectionService
from sentinel.logging import configure_logging
from sentinel.pipeline import VideoPipeline
from sentinel.visualization.annotators import Annotators

app = typer.Typer(help="Real-time object detection and tracking")


class Device(str, Enum):
    MPS = "mps"
    CUDA = "cuda"
    CPU = "cpu"


@app.command()
def main(
    source: Annotated[
        Optional[str],
        typer.Option("--source", "-s", help="Video source (webcam index or path)"),
    ] = None,
    conf: Annotated[
        Optional[float],
        typer.Option("--conf", "-c", min=0.0, max=1.0, help="Confidence threshold"),
    ] = None,
    device: Annotated[
        Optional[Device], typer.Option("--device", "-d", help="Device for inference")
    ] = None,
    track: Annotated[
        bool, typer.Option("--track", "-t", help="Enable tracking")
    ] = False,
    model: Annotated[
        Optional[str], typer.Option("--model", "-m", help="Path to YOLO model")
    ] = None,
    analytics: Annotated[
        bool, typer.Option("--analytics", "-a", help="Enable zone analytics")
    ] = False,
    zones: Annotated[
        Optional[str], typer.Option("--zones", "-z", help="Path to zones JSON")
    ] = None,
    config: Annotated[
        Optional[str], typer.Option("--config", help="Load settings from TOML file")
    ] = None,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Suppress output")
    ] = False,
) -> None:
    """Run real-time object detection and tracking."""
    configure_logging(use_rich=not quiet)

    file_config = {}
    if config:
        try:
            file_config = load_config_file(config)
            if not quiet:
                print_success(f"Loaded config: {config}")
        except Exception as e:
            print_error(f"Failed to load config: {e}")
            raise typer.Exit(1)

    parsed_source = (
        int(source)
        if source and source.isdigit()
        else source or file_config.get("video_source", settings.video_source)
    )
    selected_device = (
        device.value if device else file_config.get("device", settings.device)
    )
    model_path = (
        Path(model)
        if model
        else Path(file_config.get("model_path", settings.model_path))
    )
    conf_threshold = (
        conf
        if conf is not None
        else file_config.get("conf_threshold", settings.conf_threshold)
    )

    if analytics and not track:
        print_error("Analytics requires --track")
        raise typer.Exit(1)

    try:
        if not quiet:
            with Status("Loading model...", console=console):
                detector = YOLODetector(model_path, selected_device)
        else:
            detector = YOLODetector(model_path, selected_device)
    except Exception as e:
        print_error(f"Model load failed: {e}")
        raise typer.Exit(1)

    if not quiet:
        print_success(f"Model loaded: {model_path.name}")

    detection_service = DetectionService(
        detector=detector,
        enable_tracking=track,
        conf_threshold=conf_threshold,
    )

    analytics_service = None
    zone_configs = []
    if analytics:
        zones_path = Path(zones) if zones else settings.zones_config_path
        if not zones_path.exists():
            print_error(f"Zones file not found: {zones_path}")
            raise typer.Exit(1)

        zone_configs = load_zones_from_json(zones_path)
        analytics_service = AnalyticsService(zone_configs)
        if not quiet:
            print_success(f"Loaded {len(zone_configs)} zone(s)")

    annotators = Annotators(enable_tracking=track, zone_configs=zone_configs)

    try:
        pipeline = VideoPipeline(detection_service, annotators, analytics_service)
        pipeline.run(parsed_source)
    except KeyboardInterrupt:
        raise typer.Exit(0)


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
