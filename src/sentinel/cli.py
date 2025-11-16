from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.status import Status

from sentinel.analytics.service import AnalyticsService
from sentinel.analytics.utils import load_zones_from_json
from sentinel.cli_utils import console, print_error, print_success
from sentinel.config import settings
from sentinel.detection.models import YOLODetector
from sentinel.detection.service import DetectionService
from sentinel.image_pipeline import ImagePipeline
from sentinel.logging import configure_logging
from sentinel.video_pipeline import VideoPipeline
from sentinel.visualization.annotators import Annotators

app = typer.Typer(help="Object detection and tracking system")


class Device(str, Enum):
    MPS = "mps"
    CUDA = "cuda"
    CPU = "cpu"


@app.command("detect-image")
def detect_image(
    source: Annotated[str, typer.Argument(help="Path to input image or directory")],
    output: Annotated[
        Optional[str],
        typer.Option(
            "--output", "-o", help="Output path for annotated image/directory"
        ),
    ] = None,
    conf: Annotated[
        float,
        typer.Option("--conf", "-c", min=0.0, max=1.0, help="Confidence threshold"),
    ] = 0.5,
    device: Annotated[
        Device, typer.Option("--device", "-d", help="Device for inference")
    ] = Device.MPS,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model", "-m", help="YOLO model name (e.g., yolo11n.pt, yolo11m.pt)"
        ),
    ] = None,
    track: Annotated[
        bool, typer.Option("--track", "-t", help="Enable tracking")
    ] = False,
    no_display: Annotated[
        bool, typer.Option("--no-display", help="Don't show window (save only)")
    ] = False,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Suppress output")
    ] = False,
) -> None:
    """Detect objects in image(s). Supports single image or directory for batch processing."""
    configure_logging(use_rich=not quiet)

    source_path = Path(source)
    if not source_path.exists():
        print_error(f"Source not found: {source}")
        raise typer.Exit(1)

    if source_path.is_file():
        if source_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
            print_error(f"Unsupported image format: {source_path.suffix}")
            raise typer.Exit(1)

    model_name = model if model else settings.model_name

    try:
        if not quiet:
            with Status("Loading model...", console=console):
                detector = YOLODetector(model_name, device.value)
        else:
            detector = YOLODetector(model_name, device.value)
    except FileNotFoundError:
        print_error(f"Model not found: {model_name}")
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(f"Model load failed: {e}")
        raise typer.Exit(1)

    if not quiet:
        print_success(f"Model loaded: {model_name}")

    detection_service = DetectionService(
        detector=detector,
        enable_tracking=track,
        conf_threshold=conf,
    )

    annotators = Annotators(enable_tracking=track, zone_configs=[])

    try:
        pipeline = ImagePipeline(detection_service, annotators)
        pipeline.run(source, output_path=output, show_display=not no_display)

        if output and not quiet:
            print_success(f"Saved: {output}")
    except KeyboardInterrupt:
        raise typer.Exit(0)


@app.command("detect-video")
def detect_video(
    source: Annotated[
        Optional[str],
        typer.Option("--source", "-s", help="Video source (webcam index or path)"),
    ] = None,
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Output path for annotated video"),
    ] = None,
    no_display: Annotated[
        bool, typer.Option("--no-display", help="Don't show video window")
    ] = False,
    conf: Annotated[
        float,
        typer.Option("--conf", "-c", min=0.0, max=1.0, help="Confidence threshold"),
    ] = 0.5,
    device: Annotated[
        Device, typer.Option("--device", "-d", help="Device for inference")
    ] = Device.MPS,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model", "-m", help="YOLO model name (e.g., yolo11n.pt, yolo11m.pt)"
        ),
    ] = None,
    track: Annotated[
        bool, typer.Option("--track", "-t", help="Enable tracking")
    ] = False,
    analytics: Annotated[
        bool, typer.Option("--analytics", "-a", help="Enable zone analytics")
    ] = False,
    zones: Annotated[
        Optional[str], typer.Option("--zones", "-z", help="Path to zones JSON")
    ] = None,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Suppress output")
    ] = False,
) -> None:
    """Detect and track objects in video or webcam feed."""
    configure_logging(use_rich=not quiet)

    if analytics and not track:
        print_error("Analytics requires --track")
        raise typer.Exit(1)

    parsed_source = (
        int(source) if source and source.isdigit() else source or settings.video_source
    )

    model_name = model if model else settings.model_name

    try:
        if not quiet:
            with Status("Loading model...", console=console):
                detector = YOLODetector(model_name, device.value)
        else:
            detector = YOLODetector(model_name, device.value)
    except FileNotFoundError:
        print_error(f"Model not found: {model_name}")
        raise typer.Exit(1)
    except RuntimeError as e:
        print_error(f"Model load failed: {e}")
        raise typer.Exit(1)

    if not quiet:
        print_success(f"Model loaded: {model_name}")

    detection_service = DetectionService(
        detector=detector,
        enable_tracking=track,
        conf_threshold=conf,
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
        pipeline = VideoPipeline(
            detection_service,
            annotators,
            analytics_service,
            output_path=output,
            show_display=not no_display,
        )
        pipeline.run(parsed_source)

        if output and not quiet:
            print_success(f"Saved: {output}")
    except KeyboardInterrupt:
        raise typer.Exit(0)


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
