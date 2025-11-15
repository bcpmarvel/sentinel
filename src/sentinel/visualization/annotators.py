import cv2
import numpy as np
import supervision as sv
from ultralytics.engine.results import Results

from sentinel.analytics.models import ZoneConfig, ZoneMetrics, ZoneType


class Annotators:
    def __init__(
        self,
        enable_tracking: bool = False,
        zone_configs: list[ZoneConfig] | None = None,
    ):
        self.enable_tracking = enable_tracking
        self.zone_configs = zone_configs or []
        self.zone_annotators: dict[str, sv.PolygonZoneAnnotator | sv.LineZoneAnnotator] = {}

        self._initialize_zone_annotators()

    def _initialize_zone_annotators(self) -> None:
        for config in self.zone_configs:
            zone = config.to_supervision_zone()

            if config.type == ZoneType.POLYGON:
                self.zone_annotators[config.id] = sv.PolygonZoneAnnotator(
                    zone=zone,
                    color=sv.Color.from_hex("#00FF00"),
                    thickness=2,
                    text_scale=0.5,
                    text_thickness=1,
                    text_padding=10,
                )
            elif config.type == ZoneType.LINE:
                self.zone_annotators[config.id] = sv.LineZoneAnnotator(
                    thickness=2,
                    color=sv.Color.from_hex("#00FF00"),
                    text_thickness=1,
                    text_scale=0.5,
                    text_padding=10,
                )

    def draw(
        self,
        frame: np.ndarray,
        results: Results,
        fps: float | None = None,
        metrics: dict[str, ZoneMetrics] | None = None,
    ) -> np.ndarray:
        annotated_frame = results.plot()

        if metrics:
            annotated_frame = self._draw_zones(annotated_frame, metrics)

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

    def _draw_zones(
        self,
        frame: np.ndarray,
        metrics: dict[str, ZoneMetrics],
    ) -> np.ndarray:
        for zone_id, annotator in self.zone_annotators.items():
            if zone_id not in metrics:
                continue

            metric = metrics[zone_id]
            config = next(c for c in self.zone_configs if c.id == zone_id)
            zone = config.to_supervision_zone()

            if isinstance(annotator, sv.PolygonZoneAnnotator):
                frame = annotator.annotate(frame)
                frame = self._draw_polygon_metrics(frame, config, metric)
            elif isinstance(annotator, sv.LineZoneAnnotator) and isinstance(zone, sv.LineZone):
                frame = annotator.annotate(frame, line_counter=zone)

        return frame

    def _draw_polygon_metrics(
        self,
        frame: np.ndarray,
        config: ZoneConfig,
        metric: ZoneMetrics,
    ) -> np.ndarray:
        if not config.polygon:
            return frame

        polygon = np.array(config.polygon)
        center_x = int(polygon[:, 0].mean())
        center_y = int(polygon[:, 1].mean())

        text_lines = [
            f"{config.name}",
            f"Count: {metric.current_count}",
            f"Avg Dwell: {metric.avg_dwell_time:.1f}s",
        ]

        y_offset = center_y - 30
        for line in text_lines:
            cv2.putText(
                frame,
                line,
                (center_x - 50, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )
            y_offset += 20

        return frame
