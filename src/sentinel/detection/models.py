import torch
from ultralytics import YOLO
from pathlib import Path


class YOLODetector:
    def __init__(self, model_path: Path, device: str = "mps"):
        self.device = device
        self.model = YOLO(str(model_path))

        if device == "mps" and torch.backends.mps.is_available():
            self.model.to("mps")
        elif device == "cuda" and torch.cuda.is_available():
            self.model.to("cuda")
        else:
            self.model.to("cpu")
            self.device = "cpu"

    def predict(
        self,
        frame,
        conf: float = 0.5,
        iou: float = 0.45,
        max_det: int = 300,
    ):
        results = self.model.predict(
            frame,
            conf=conf,
            iou=iou,
            max_det=max_det,
            verbose=False,
            device=self.device,
        )
        return results[0]

    def track(
        self,
        frame,
        conf: float = 0.5,
        iou: float = 0.45,
        max_det: int = 300,
        persist: bool = True,
    ):
        results = self.model.track(
            frame,
            conf=conf,
            iou=iou,
            max_det=max_det,
            verbose=False,
            device=self.device,
            persist=persist,
            tracker="botsort.yaml",
        )
        return results[0]
