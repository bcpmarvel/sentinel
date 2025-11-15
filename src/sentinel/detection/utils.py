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
