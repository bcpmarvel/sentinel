import cv2
import numpy as np

from src.config import settings
from src.detection.service import DetectionService
from src.detection.utils import FPSCounter
from src.visualization.annotators import Annotators


class VideoPipeline:
    def __init__(
        self,
        detection_service: DetectionService,
        annotators: Annotators,
    ):
        self.detection_service = detection_service
        self.annotators = annotators
        self.fps_counter = FPSCounter()

    def run(self, source: str | int | None = None) -> None:
        source = source if source is not None else settings.video_source
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            raise ValueError(f"Failed to open video source: {source}")

        window_name = "Object Tracking" if self.detection_service.enable_tracking else "Object Detection"

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

        fps = self.fps_counter.update()

        annotated_frame = self.annotators.draw(frame, results, fps)

        return annotated_frame
