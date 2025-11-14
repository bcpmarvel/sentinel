import argparse
from src.detection.service import DetectionService


def main() -> None:
    parser = argparse.ArgumentParser(description="Real-time object detection")
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

    args = parser.parse_args()

    source = int(args.source) if args.source and args.source.isdigit() else args.source

    service = DetectionService(
        device=args.device,
        conf_threshold=args.conf,
    )

    service.run_video(source)


if __name__ == "__main__":
    main()
