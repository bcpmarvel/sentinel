import argparse
from pathlib import Path

from src.config import settings
from src.detection.models import YOLODetector
from src.detection.service import DetectionService
from src.pipeline import VideoPipeline
from src.visualization.annotators import Annotators


def main() -> None:
    parser = argparse.ArgumentParser(description="Real-time object detection and tracking")
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Video source (webcam index or file path)",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=None,
        help="Confidence threshold",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        choices=["mps", "cuda", "cpu"],
        help="Device for inference",
    )
    parser.add_argument(
        "--track",
        action="store_true",
        help="Enable multi-object tracking",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Path to YOLO model",
    )

    args = parser.parse_args()

    source = int(args.source) if args.source and args.source.isdigit() else args.source
    device = args.device or settings.device
    model_path = Path(args.model) if args.model else settings.model_path

    detector = YOLODetector(model_path, device)
    detection_service = DetectionService(
        detector=detector,
        enable_tracking=args.track,
        conf_threshold=args.conf,
    )
    annotators = Annotators(enable_tracking=args.track)

    pipeline = VideoPipeline(detection_service, annotators)
    pipeline.run(source)


if __name__ == "__main__":
    main()
