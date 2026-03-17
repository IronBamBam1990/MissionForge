"""Load and validate mission configuration from JSON files."""

import json
from pathlib import Path

from .config_schema import MissionConfig


# Map display names to ARMA classnames
MAPS_DB: dict[str, str] = {}
_maps_file = Path(__file__).parent / "data" / "maps.json"
if _maps_file.exists():
    with open(_maps_file, "r", encoding="utf-8") as f:
        _maps_data = json.load(f)
        for key, info in _maps_data.get("maps", {}).items():
            MAPS_DB[key] = info["classname"]


def _normalize(data: dict) -> dict:
    """Normalize AI-generated JSON to match our schema.

    AI models often use alternative field names. This maps them
    to the expected schema fields before Pydantic validation.
    """
    if not isinstance(data, dict):
        return data

    # Top-level: radio_system -> radio.system
    if "radio_system" in data and "radio" not in data:
        data["radio"] = {"system": data.pop("radio_system")}

    # BLUFOR groups
    if "blufor" in data and isinstance(data["blufor"], dict):
        for group in data["blufor"].get("groups", []):
            if isinstance(group, dict):
                # start_position -> position
                if "start_position" in group and "position" not in group:
                    group["position"] = group.pop("start_position")
                if "spawn_position" in group and "position" not in group:
                    group["position"] = group.pop("spawn_position")
                # name -> callsign (if callsign missing)
                if "name" in group and "callsign" not in group:
                    group["callsign"] = group.pop("name")
                # units
                for unit in group.get("units", []):
                    if isinstance(unit, dict):
                        if "is_player" in unit:
                            del unit["is_player"]  # always playable
                        if "is_playable" in unit:
                            del unit["is_playable"]
                        if "name" in unit and "classname_override" not in unit:
                            del unit["name"]  # cosmetic, not a classname

    # Air support
    if "air_support" in data and isinstance(data["air_support"], dict):
        for aircraft in data["air_support"].get("aircraft", []):
            if isinstance(aircraft, dict):
                if "start_position" in aircraft and "position" not in aircraft:
                    aircraft["position"] = aircraft.pop("start_position")

    # OPFOR zones
    if "opfor" in data and isinstance(data["opfor"], dict):
        for zone in data["opfor"].get("zones", []):
            if isinstance(zone, dict):
                if "position" in zone and "center" not in zone:
                    zone["center"] = zone.pop("position")
                for pos in zone.get("positions", []):
                    if isinstance(pos, dict):
                        if "description" in pos:
                            del pos["description"]  # cosmetic

    # Markers - all categories
    if "markers" in data and isinstance(data["markers"], dict):
        for cat in ["objectives", "waypoints", "phase_lines", "sbf", "rally_points", "custom"]:
            for marker in data["markers"].get(cat, []):
                if isinstance(marker, dict):
                    # display_name -> text
                    if "display_name" in marker and "text" not in marker:
                        marker["text"] = marker.pop("display_name")
                    elif "display_name" in marker:
                        del marker["display_name"]

    # Respawn: reinsert_teleport (bool) -> reinsert (object)
    if "respawn" in data and isinstance(data["respawn"], dict):
        r = data["respawn"]
        if "reinsert_teleport" in r and "reinsert" not in r:
            r["reinsert"] = {"enabled": r.pop("reinsert_teleport"), "priority": []}
        elif "reinsert_teleport" in r:
            del r["reinsert_teleport"]

    return data


def load_config(path: str | Path) -> MissionConfig:
    """Load mission config from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data = _normalize(data)
    return MissionConfig(**data)


def load_config_from_dict(data: dict) -> MissionConfig:
    """Load mission config from a dict (e.g. from API request)."""
    data = _normalize(data)
    return MissionConfig(**data)


def resolve_map_classname(config: MissionConfig) -> str:
    if config.meta.map_classname_override:
        return config.meta.map_classname_override
    return MAPS_DB.get(config.meta.map, config.meta.map)
