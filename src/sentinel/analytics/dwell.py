import time
from collections import defaultdict

from sentinel.analytics.models import ObjectState


class DwellTimeTracker:
    def __init__(self):
        self.objects: dict[int, ObjectState] = {}
        self.zone_dwell_history: dict[str, list[float]] = defaultdict(list)

    def update(self, zone_id: str, track_ids_in_zone: set[int]) -> dict[str, float]:
        current_time = time.time()
        metrics = {}

        if zone_id not in self.zone_dwell_history:
            self.zone_dwell_history[zone_id] = []

        for track_id in track_ids_in_zone:
            if track_id not in self.objects:
                self.objects[track_id] = ObjectState(track_id=track_id)

            obj = self.objects[track_id]

            if zone_id not in obj.current_zones:
                obj.current_zones.add(zone_id)
                obj.entry_times[zone_id] = current_time
                obj.dwell_times[zone_id] = 0.0

        for track_id, obj in list(self.objects.items()):
            if zone_id in obj.current_zones:
                if track_id in track_ids_in_zone:
                    elapsed = current_time - obj.entry_times[zone_id]
                    obj.dwell_times[zone_id] = elapsed
                else:
                    final_dwell = obj.dwell_times[zone_id]
                    self.zone_dwell_history[zone_id].append(final_dwell)

                    obj.current_zones.discard(zone_id)
                    del obj.entry_times[zone_id]
                    del obj.dwell_times[zone_id]

                    if not obj.current_zones:
                        del self.objects[track_id]

        current_dwells = [
            obj.dwell_times.get(zone_id, 0.0)
            for obj in self.objects.values()
            if zone_id in obj.current_zones
        ]

        if current_dwells:
            metrics["avg_dwell_time"] = sum(current_dwells) / len(current_dwells)
            metrics["max_dwell_time"] = max(current_dwells)
        elif self.zone_dwell_history[zone_id]:
            history = self.zone_dwell_history[zone_id]
            metrics["avg_dwell_time"] = sum(history) / len(history)
            metrics["max_dwell_time"] = max(history)
        else:
            metrics["avg_dwell_time"] = 0.0
            metrics["max_dwell_time"] = 0.0

        return metrics
