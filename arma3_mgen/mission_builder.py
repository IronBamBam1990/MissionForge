"""Mission Builder - takes simplified AI output and builds a complete, working mission.

This module is the core intelligence of the framework. Instead of relying on
AI to generate precise coordinates and SQF code, we take a simple description
and compute everything ourselves using the locations database and proven SQF templates.
"""

import json
import math
import random
from pathlib import Path

# Load locations database
_loc_file = Path(__file__).parent / "data" / "locations.json"
LOCATIONS = {}
if _loc_file.exists():
    with open(_loc_file, "r", encoding="utf-8") as f:
        LOCATIONS = json.load(f)


def resolve_location(map_name: str, location_name: str) -> list[float]:
    """Find coordinates for a named location on a map.

    Searches cities, towns, military bases, landmarks.
    Returns [X, 0, Y] or None.
    """
    map_data = LOCATIONS.get(map_name)
    if not map_data:
        # Try partial match
        for key in LOCATIONS:
            if map_name.lower() in key.lower():
                map_data = LOCATIONS[key]
                break
    if not map_data:
        return None

    # Search all categories
    name_lower = location_name.lower().strip()
    for category in map_data.values():
        if not isinstance(category, dict) or category == map_data.get("_size"):
            continue
        for loc_name, coords in category.items():
            if not isinstance(coords, list):
                continue
            if name_lower in loc_name.lower() or loc_name.lower() in name_lower:
                return [coords[0], 0, coords[1]]

    return None


def get_map_center(map_name: str) -> list[float]:
    """Get a safe default position near the center of a map."""
    defaults = {
        "Altis": [14500, 0, 16000],
        "Stratis": [4000, 0, 4000],
        "Tanoa": [6500, 0, 6500],
        "Malden": [5000, 0, 5500],
        "Livonia": [6000, 0, 7000],
    }
    for key, pos in defaults.items():
        if key.lower() in map_name.lower():
            return pos
    return [10000, 0, 10000]


def offset_pos(center: list[float], distance: float, bearing_deg: float) -> list[float]:
    """Calculate position at distance and bearing from center."""
    rad = math.radians(bearing_deg)
    return [
        center[0] + distance * math.sin(rad),
        0,
        center[2] + distance * math.cos(rad),
    ]


def spread_positions(center: list[float], count: int, min_dist: float = 30, max_dist: float = 80) -> list[list[float]]:
    """Generate spread positions around a center point."""
    positions = []
    for i in range(count):
        angle = (360 / count) * i + random.uniform(-15, 15)
        dist = random.uniform(min_dist, max_dist)
        positions.append(offset_pos(center, dist, angle))
    return positions


def compute_mission_layout(mission_data: dict) -> dict:
    """Take simplified AI output and compute full mission layout with real coordinates.

    Input: simplified mission description from AI
    Output: complete config ready for generators
    """
    map_name = mission_data.get("meta", {}).get("map", "Altis")
    location = mission_data.get("meta", {}).get("location", "")

    # Resolve target location
    target_pos = None
    if location:
        target_pos = resolve_location(map_name, location)
    if not target_pos:
        target_pos = get_map_center(map_name)

    # Compute BLUFOR start position - 600-1000m south of target
    blufor_start = offset_pos(target_pos, random.uniform(600, 1000), random.uniform(160, 200))

    # Compute ORP - 400m from target, between start and target
    orp_pos = offset_pos(target_pos, 400, random.uniform(160, 200))

    # Fix BLUFOR group positions
    if "blufor" in mission_data:
        groups = mission_data["blufor"].get("groups", [])
        for i, group in enumerate(groups):
            if not _has_valid_pos(group):
                group["position"] = offset_pos(blufor_start, i * 15, 90)

    # Fix OPFOR positions - spread around target
    if "opfor" in mission_data:
        for zone in mission_data["opfor"].get("zones", []):
            zone_center = zone.get("center")
            if not zone_center or not _is_valid(zone_center):
                # Try to resolve zone location/name as map location
                resolved = None
                for field in ["location", "name"]:
                    val = zone.get(field, "")
                    if val:
                        resolved = resolve_location(map_name, val)
                        if resolved:
                            print(f"[LAYOUT] Zone '{val}' resolved to {resolved}")
                            break
                zone["center"] = resolved or list(target_pos)

            center = zone["center"]
            positions = zone.get("positions", [])
            spread = spread_positions(center, len(positions), 20, 100)
            for j, pos in enumerate(positions):
                if not _has_valid_pos_dict(pos):
                    pos["position"] = spread[j] if j < len(spread) else offset_pos(center, 50, j * 45)

    # Fix air support positions - 1500m behind BLUFOR
    if "air_support" in mission_data and mission_data["air_support"].get("enabled"):
        for aircraft in mission_data["air_support"].get("aircraft", []):
            if not _has_valid_pos(aircraft):
                aircraft["position"] = offset_pos(blufor_start, 800, 180)

    # Fix/generate markers
    if "markers" not in mission_data:
        mission_data["markers"] = {}
    markers = mission_data["markers"]

    # Ensure objectives have valid positions
    for obj in markers.get("objectives", []):
        if not _has_valid_pos_dict(obj):
            obj["position"] = list(target_pos)

    # Add ORP if missing
    rp = markers.get("rally_points", [])
    if not rp:
        markers["rally_points"] = [{"name": "orp", "text": "ORP", "position": list(orp_pos), "type": "mil_flag", "color": "ColorGreen"}]

    # Add start marker if missing
    custom = markers.get("custom", [])
    has_start = any("start" in m.get("name", "").lower() for m in custom)
    if not has_start:
        custom.append({"name": "start", "text": "Start", "position": list(blufor_start), "type": "mil_start", "color": "ColorBlue"})
    markers["custom"] = custom

    # Generate waypoints from start to target if missing
    wps = markers.get("waypoints", [])
    if not wps:
        mid1 = offset_pos(blufor_start, 300, _bearing(blufor_start, target_pos))
        mid2 = offset_pos(target_pos, 300, _bearing(target_pos, blufor_start))
        markers["waypoints"] = [
            {"name": "wp_1", "text": "WP 1", "position": mid1, "type": "mil_dot", "color": "ColorBlue"},
            {"name": "wp_2", "text": "WP 2", "position": mid2, "type": "mil_dot", "color": "ColorBlue"},
        ]

    # Fix civilian zones
    if "civilians" in mission_data and mission_data["civilians"].get("enabled"):
        for czone in mission_data["civilians"].get("zones", []):
            if "center" in czone and not _is_valid(czone["center"]):
                czone["center"] = list(target_pos)

    # Fix hostage positions
    if "hostages" in mission_data and mission_data["hostages"].get("enabled"):
        for hostage in mission_data["hostages"].get("hostages", []):
            if not _is_valid(hostage.get("position", [0, 0, 0])):
                # Place hostages near target position (inside OPFOR zone)
                hostage["position"] = offset_pos(target_pos, random.uniform(10, 50), random.uniform(0, 360))

    # Fix resupply
    for crate in mission_data.get("resupply", []):
        if not _is_valid(crate.get("position", [0, 0, 0])):
            crate["position"] = offset_pos(orp_pos, 10, random.uniform(0, 360))

    # Fix player vehicle positions
    for pv in mission_data.get("player_vehicles", []):
        if not _is_valid(pv.get("position", [0, 0, 0])):
            pv["position"] = offset_pos(blufor_start, 20, random.uniform(0, 360))

    # Fix counterattack positions
    ca = mission_data.get("counterattack", {})
    if ca.get("enabled"):
        if not _is_valid(ca.get("spawn_position", [0, 0, 0])):
            ca["spawn_position"] = offset_pos(target_pos, random.uniform(800, 1200), random.uniform(0, 90))
        if not _is_valid(ca.get("target_position", [0, 0, 0])):
            ca["target_position"] = list(target_pos)

    # Fix extraction position
    ext = mission_data.get("extraction", {})
    if ext.get("enabled"):
        if not _is_valid(ext.get("position", [0, 0, 0])):
            ext["position"] = offset_pos(blufor_start, random.uniform(100, 300), random.uniform(160, 200))

    # Fix hold_position position
    hp = mission_data.get("hold_position", {})
    if hp.get("enabled"):
        if not _is_valid(hp.get("position", [0, 0, 0])):
            hp["position"] = list(target_pos)

    # Fix mortar target position
    mortar = mission_data.get("mortar", {})
    if mortar.get("enabled"):
        if not _is_valid(mortar.get("target_position", [0, 0, 0])):
            mortar["target_position"] = list(target_pos)

    return mission_data


def _has_valid_pos(obj) -> bool:
    """Check if dict/model has a valid position field."""
    pos = None
    if isinstance(obj, dict):
        pos = obj.get("position") or obj.get("start_position") or obj.get("spawn_position")
    else:
        pos = getattr(obj, "position", None)
    return pos is not None and _is_valid(pos)


def _has_valid_pos_dict(d: dict) -> bool:
    pos = d.get("position") or d.get("start_position")
    return pos is not None and _is_valid(pos)


def _is_valid(pos) -> bool:
    if not isinstance(pos, (list, tuple)) or len(pos) < 3:
        return False
    return pos[0] > 50 and pos[2] > 50


def _bearing(from_pos, to_pos) -> float:
    """Calculate bearing in degrees from one position to another."""
    dx = to_pos[0] - from_pos[0]
    dz = to_pos[2] - from_pos[2]
    return math.degrees(math.atan2(dx, dz)) % 360
