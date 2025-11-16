from pathlib import Path

import cv2
import numpy as np

from sentinel.analytics.service import AnalyticsService
from sentinel.config import settings
from sentinel.detection.service import DetectionService
from sentinel.detection.utils import FPSCounter
from sentinel.visualization.annotators import Annotators


class VideoPipeline:
    def __init__(
        self,
        detection_service: DetectionService,
        annotators: Annotators,
        analytics_service: AnalyticsService | None = None,
        output_path: str | None = None,
        show_display: bool = True,
    ):
        self.detection_service = detection_service
        self.annotators = annotators
        self.analytics_service = analytics_service
        self.output_path = output_path
        self.show_display = show_display
        self.fps_counter = FPSCounter()
        self.video_writer: cv2.VideoWriter | None = None

        if self.output_path:
            output_dir = Path(self.output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, source: str | int | None = None) -> None:
        source = source if source is not None else settings.video_source
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            raise ValueError(f"Failed to open video source: {source}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if self.output_path:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.video_writer = cv2.VideoWriter(
                self.output_path, fourcc, fps, (width, height)
            )

        window_name = self._get_window_name()

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                annotated_frame = self._process_frame(frame)

                if self.video_writer:
                    self.video_writer.write(annotated_frame)

                if self.show_display:
                    cv2.imshow(window_name, annotated_frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break

        finally:
            cap.release()
            if self.video_writer:
                self.video_writer.release()
            if self.show_display:
                cv2.destroyAllWindows()

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        results = self.detection_service.process(frame)

        metrics = None
        if self.analytics_service:
            metrics = self.analytics_service.update(results)

        fps = self.fps_counter.update()

        annotated_frame = self.annotators.draw(frame, results, fps, metrics)

        return annotated_frame

    def _get_window_name(self) -> str:
        if self.analytics_service:
            return "Video Analytics"
        if self.detection_service.enable_tracking:
            return "Object Tracking"
        return "Object Detection"
