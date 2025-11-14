import cv2
import numpy as np

from src.analytics.service import AnalyticsService
from src.config import settings
from src.detection.service import DetectionService
from src.detection.utils import FPSCounter
from src.visualization.annotators import Annotators


class VideoPipeline:
    def __init__(
        self,
        detection_service: DetectionService,
        annotators: Annotators,
        analytics_service: AnalyticsService | None = None,
    ):
        self.detection_service = detection_service
        self.annotators = annotators
        self.analytics_service = analytics_service
        self.fps_counter = FPSCounter()

    def run(self, source: str | int | None = None) -> None:
        source = source if source is not None else settings.video_source
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            raise ValueError(f"Failed to open video source: {source}")

        window_name = self._get_window_name()

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                annotated_frame = self._process_frame(frame)

                cv2.imshow(window_name, annotated_frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            cap.release()
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
