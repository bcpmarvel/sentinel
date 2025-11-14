from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import supervision as sv


class ZoneType(str, Enum):
    POLYGON = "polygon"
    LINE = "line"


@dataclass
class ZoneConfig:
    id: str
    name: str
    type: ZoneType
    polygon: list[list[int]] | None = None
    line: tuple[list[int], list[int]] | None = None

    def to_supervision_zone(self) -> sv.PolygonZone | sv.LineZone:
        if self.type == ZoneType.POLYGON:
            if not self.polygon:
                raise ValueError(f"Polygon zone {self.id} missing polygon coordinates")
            return sv.PolygonZone(polygon=np.array(self.polygon, dtype=np.int64))
        elif self.type == ZoneType.LINE:
            if not self.line:
                raise ValueError(f"Line zone {self.id} missing line coordinates")
            start, end = self.line
            return sv.LineZone(start=sv.Point(*start), end=sv.Point(*end))
        else:
            raise ValueError(f"Unknown zone type: {self.type}")


@dataclass
class ZoneMetrics:
    zone_id: str
    zone_name: str
    current_count: int = 0
    total_entries: int = 0
    total_exits: int = 0
    avg_dwell_time: float = 0.0
    max_dwell_time: float = 0.0
    active_track_ids: set[int] = field(default_factory=set)


@dataclass
class ObjectState:
    track_id: int
    current_zones: set[str] = field(default_factory=set)
    entry_times: dict[str, float] = field(default_factory=dict)
    dwell_times: dict[str, float] = field(default_factory=dict)
