import json
from pathlib import Path

from sentinel.analytics.models import ZoneConfig, ZoneType


def load_zones_from_json(path: Path) -> list[ZoneConfig]:
    with open(path) as f:
        data = json.load(f)

    zones = []
    for zone_data in data.get("zones", []):
        zone_config = ZoneConfig(
            id=zone_data["id"],
            name=zone_data["name"],
            type=ZoneType(zone_data["type"]),
            polygon=zone_data.get("polygon"),
            line=zone_data.get("line"),
        )
        zones.append(zone_config)

    return zones
