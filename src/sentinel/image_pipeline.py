from pathlib import Path

import cv2
import numpy as np

from sentinel.detection.service import DetectionService
from sentinel.visualization.annotators import Annotators

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class ImagePipeline:
    def __init__(
        self,
        detection_service: DetectionService,
        annotators: Annotators,
    ):
        self.detection_service = detection_service
        self.annotators = annotators

    def run(
        self,
        source: str | Path,
        output_path: str | Path | None = None,
        show_display: bool = True,
    ) -> None:
        source = Path(source)

        if not source.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        if source.is_dir():
            self._process_directory(source, output_path, show_display)
        else:
            self._process_single_image(source, output_path, show_display)

    def _process_directory(
        self,
        input_dir: Path,
        output_dir: str | Path | None,
        show_display: bool,
    ) -> None:
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        image_files = [
            f
            for f in input_dir.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        if not image_files:
            raise ValueError(f"No images found in {input_dir}")

        for image_path in sorted(image_files):
            output_path = None
            if output_dir:
                output_path = (
                    output_dir / f"{image_path.stem}_annotated{image_path.suffix}"
                )

            self._process_single_image(image_path, output_path, show_display)

    def _process_single_image(
        self,
        image_path: Path,
        output_path: str | Path | None,
        show_display: bool,
    ) -> None:
        frame = cv2.imread(str(image_path))
        if frame is None:
            raise ValueError(f"Failed to load image: {image_path}")

        annotated_frame = self._process_frame(frame)

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), annotated_frame)

        if show_display:
            window_name = self._get_window_name()
            cv2.imshow(window_name, annotated_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        results = self.detection_service.process(frame)
        annotated_frame = self.annotators.draw(frame, results, fps=None, metrics=None)
        return annotated_frame

    def _get_window_name(self) -> str:
        if self.detection_service.enable_tracking:
            return "Object Detection & Tracking"
        return "Object Detection"
