import supervision as sv
from ultralytics.engine.results import Results

from sentinel.analytics.dwell import DwellTimeTracker
from sentinel.analytics.models import ZoneConfig, ZoneMetrics, ZoneType


class AnalyticsService:
    def __init__(self, zone_configs: list[ZoneConfig]):
        self.zone_configs = zone_configs
        self.zones: dict[str, sv.PolygonZone | sv.LineZone] = {}
        self.dwell_tracker = DwellTimeTracker()
        self.metrics: dict[str, ZoneMetrics] = {}

        for config in zone_configs:
            zone = config.to_supervision_zone()
            self.zones[config.id] = zone
            self.metrics[config.id] = ZoneMetrics(
                zone_id=config.id,
                zone_name=config.name,
            )

    def update(self, results: Results) -> dict[str, ZoneMetrics]:
        detections = sv.Detections.from_ultralytics(results)

        if detections.tracker_id is None or len(detections) == 0:
            return self.metrics

        for zone_id, zone in self.zones.items():
            config = next(c for c in self.zone_configs if c.id == zone_id)

            if config.type == ZoneType.POLYGON:
                self._update_polygon_zone(zone_id, zone, detections)
            elif config.type == ZoneType.LINE:
                self._update_line_zone(zone_id, zone, detections)

        return self.metrics

    def _update_polygon_zone(
        self,
        zone_id: str,
        zone: sv.PolygonZone,
        detections: sv.Detections,
    ) -> None:
        mask = zone.trigger(detections)

        tracks_in_zone = set()
        if detections.tracker_id is not None:
            tracks_in_zone = {
                int(detections.tracker_id[i])
                for i in range(len(detections))
                if mask[i]
            }

        dwell_metrics = self.dwell_tracker.update(zone_id, tracks_in_zone)

        metric = self.metrics[zone_id]
        metric.current_count = len(tracks_in_zone)
        metric.active_track_ids = tracks_in_zone
        metric.avg_dwell_time = dwell_metrics["avg_dwell_time"]
        metric.max_dwell_time = dwell_metrics["max_dwell_time"]

    def _update_line_zone(
        self,
        zone_id: str,
        zone: sv.LineZone,
        detections: sv.Detections,
    ) -> None:
        zone.trigger(detections)

        metric = self.metrics[zone_id]
        metric.total_entries = zone.in_count
        metric.total_exits = zone.out_count
        metric.current_count = zone.in_count - zone.out_count
