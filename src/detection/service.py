import numpy as np
from ultralytics.engine.results import Results

from src.config import settings
from src.detection.models import YOLODetector


class DetectionService:
    def __init__(
        self,
        detector: YOLODetector,
        enable_tracking: bool = False,
        conf_threshold: float | None = None,
        iou_threshold: float | None = None,
    ):
        self.detector = detector
        self.enable_tracking = enable_tracking
        self.conf_threshold = conf_threshold or settings.conf_threshold
        self.iou_threshold = iou_threshold or settings.iou_threshold

    def process(self, frame: np.ndarray) -> Results:
        if self.enable_tracking:
            return self.detector.track(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                max_det=settings.max_detections,
            )

        return self.detector.predict(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            max_det=settings.max_detections,
        )
