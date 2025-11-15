import cv2
import time
from collections import deque


class FPSCounter:
    def __init__(self, window_size: int = 30):
        self.frame_times = deque(maxlen=window_size)
        self.last_time = time.time()

    def update(self) -> float:
        current_time = time.time()
        self.frame_times.append(current_time - self.last_time)
        self.last_time = current_time

        if len(self.frame_times) > 0:
            return len(self.frame_times) / sum(self.frame_times)
        return 0.0

    def get_fps(self) -> float:
        if len(self.frame_times) > 0:
            return len(self.frame_times) / sum(self.frame_times)
        return 0.0


def draw_detections(frame, results, fps: float | None = None):
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


def draw_tracks(frame, results, fps: float | None = None):
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
