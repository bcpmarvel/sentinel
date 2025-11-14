import cv2
import numpy as np
from ultralytics.engine.results import Results


class Annotators:
    def __init__(self, enable_tracking: bool = False):
        self.enable_tracking = enable_tracking

    def draw(
        self,
        frame: np.ndarray,
        results: Results,
        fps: float | None = None,
    ) -> np.ndarray:
        annotated_frame = results.plot()

        if fps is not None:
            cv2.putText(
                annotated_frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

        return annotated_frame
