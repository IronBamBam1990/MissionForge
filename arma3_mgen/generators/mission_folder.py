"""Orchestrator - assembles the complete mission folder."""

import json
from pathlib import Path

from ..config_schema import MissionConfig
from ..config_loader import resolve_map_classname
from .mission_sqm import generate_mission_sqm
from .description_ext import generate_description_ext
from .init_sqf import generate_init_sqf
from .init_server import generate_init_server
from .init_player_local import generate_init_player_local
from .briefing import generate_briefing
from .respawn import generate_on_player_killed, generate_on_player_respawn


def generate_mission(config: MissionConfig, output_dir: str | Path) -> Path:
    """Generate a complete ARMA 3 mission folder.

    Args:
        config: Validated mission configuration
        output_dir: Base directory for output (e.g. Documents/Arma 3/missions/)

    Returns:
        Path to the created mission folder
    """
    output_dir = Path(output_dir)
    map_class = resolve_map_classname(config)
    mission_folder_name = f"{config.meta.mission_name}.{map_class}"
    mission_path = output_dir / mission_folder_name

    # Validate and fix coordinates
    _fix_coordinates(config)

    # Load faction data if available
    faction_data = _load_faction(config.faction_preset)
    enemy_faction_data = _load_faction(config.enemy_faction_preset)

    # Create directory structure
    mission_path.mkdir(parents=True, exist_ok=True)
    (mission_path / "scripts" / "loadouts").mkdir(parents=True, exist_ok=True)
    (mission_path / "scripts" / "ai").mkdir(parents=True, exist_ok=True)

    # Generate and write files
    files = {}

    # Core mission files
    files["mission.sqm"] = generate_mission_sqm(config, faction_data, enemy_faction_data)
    files["description.ext"] = generate_description_ext(config)
    files["init.sqf"] = generate_init_sqf(config)
    files["initServer.sqf"] = generate_init_server(config, enemy_faction_data)
    files["initPlayerLocal.sqf"] = generate_init_player_local(config)

    # Script files
    files["scripts/briefing.sqf"] = generate_briefing(config)
    # Respawn scripts MUST be in mission root — ARMA auto-detects them there
    files["onPlayerKilled.sqf"] = generate_on_player_killed(config)
    files["onPlayerRespawn.sqf"] = generate_on_player_respawn(config)

    # Write all files
    for rel_path, content in files.items():
        file_path = mission_path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    return mission_path


def _fix_coordinates(config: MissionConfig) -> None:
    """Validate and fix coordinates - ensure nothing spawns in water/off map.

    If BLUFOR positions are invalid (too close to 0,0 or off-map),
    snap them to the first OPFOR zone center with offset.
    """
    # Find a valid reference position from OPFOR zones or markers
    ref_pos = None
    for zone in config.opfor.zones:
        if zone.center[0] > 50 and zone.center[2] > 50:
            ref_pos = zone.center
            break
    if not ref_pos:
        for obj in config.markers.objectives:
            if obj.position[0] > 50 and obj.position[2] > 50:
                ref_pos = obj.position
                break

    if not ref_pos:
        return  # No valid reference, can't fix

    # Fix BLUFOR groups with invalid positions
    for group in config.blufor.groups:
        if _is_invalid_pos(group.position):
            # Place 500-800m south-east of first objective
            group.position = [ref_pos[0] - 500, 0, ref_pos[2] - 500]
            print(f"[FIX] BLUFOR {group.callsign} moved to {group.position}")

    # Fix air support
    if config.air_support.enabled:
        for aircraft in config.air_support.aircraft:
            if _is_invalid_pos(aircraft.position):
                aircraft.position = [ref_pos[0] - 1000, 0, ref_pos[2] - 1000]
                print(f"[FIX] Aircraft {aircraft.callsign} moved to {aircraft.position}")

    # Fix markers with invalid positions
    marker_idx = 0
    for marker_list in [config.markers.objectives, config.markers.waypoints,
                        config.markers.sbf, config.markers.rally_points, config.markers.custom]:
        for m in marker_list:
            if _is_invalid_pos(m.position):
                # Deterministic offset based on index (hash() is non-deterministic across sessions)
                offset = (marker_idx * 73) % 200 - 100
                m.position = [ref_pos[0] + offset, 0,
                              ref_pos[2] + offset]
                print(f"[FIX] Marker {m.name} moved to {m.position}")
            marker_idx += 1

    # Fix OPFOR positions
    for zone in config.opfor.zones:
        if _is_invalid_pos(zone.center):
            if ref_pos:
                zone.center = list(ref_pos)
        for pi, pos in enumerate(zone.positions):
            if _is_invalid_pos(pos.position):
                offset = (pi * 47) % 100 - 50
                pos.position = [zone.center[0] + offset, 0,
                                zone.center[2] + offset]
                print(f"[FIX] OPFOR {pos.id} moved to {pos.position}")


def _is_invalid_pos(pos: list) -> bool:
    """Check if position is likely in water or off map."""
    if len(pos) < 3:
        return True
    x, _, y = pos[0], pos[1], pos[2]
    # Too close to origin = likely water on most maps
    if x < 50 or y < 50:
        return True
    # Negative or zero
    if x <= 0 or y <= 0:
        return True
    return False


def _load_faction(preset_name: str) -> dict | None:
    """Load faction data from JSON file."""
    faction_file = Path(__file__).parent.parent / "data" / "factions" / f"{preset_name}.json"
    if faction_file.exists():
        with open(faction_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None
