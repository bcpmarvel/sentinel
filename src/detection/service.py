import cv2
from pathlib import Path

from src.config import settings
from src.detection.models import YOLODetector
from src.detection.utils import FPSCounter, draw_detections


class DetectionService:
    def __init__(
        self,
        model_path: Path | None = None,
        device: str | None = None,
        conf_threshold: float | None = None,
        iou_threshold: float | None = None,
    ):
        self.model_path = model_path or settings.model_path
        self.device = device or settings.device
        self.conf_threshold = conf_threshold or settings.conf_threshold
        self.iou_threshold = iou_threshold or settings.iou_threshold

        self.detector = YOLODetector(self.model_path, self.device)
        self.fps_counter = FPSCounter()

    def process_frame(self, frame):
        results = self.detector.predict(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            max_det=settings.max_detections,
        )

        fps = self.fps_counter.update()
        annotated_frame = draw_detections(frame, results, fps)

        return annotated_frame, results

    def run_video(self, source: str | int | None = None):
        source = source if source is not None else settings.video_source
        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            raise ValueError(f"Failed to open video source: {source}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                annotated_frame, _ = self.process_frame(frame)

                cv2.imshow("Object Detection", annotated_frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
