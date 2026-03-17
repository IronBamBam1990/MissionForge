"""Generates mission.sqm - ONLY BLUFOR playable units + markers.

OPFOR, vehicles, fortifications are spawned via initServer.sqf with terrain snap.
SQM Y=0 kills AI before any script can fix it, so ONLY player slots go here.
"""

import random
import re

from ..config_schema import MissionConfig, MarkerDef
from ..sqm.writer import SQMWriter
from ..sqm.id_manager import IDManager


ROLE_CLASSNAMES = {
    "platoon_leader": "B_officer_F", "platoon_sergeant": "B_Soldier_SL_F",
    "squad_leader": "B_Soldier_SL_F", "team_leader": "B_Soldier_TL_F",
    "autorifleman": "B_Soldier_AR_F", "grenadier": "B_Soldier_GL_F",
    "rifleman": "B_Soldier_F", "combat_medic": "B_medic_F", "medic": "B_medic_F",
    "ratelo": "B_Soldier_F", "mg_gunner": "B_soldier_M_F",
    "mg_assistant": "B_Soldier_A_F", "mg_ammo_bearer": "B_Soldier_F",
    "at_gunner": "B_soldier_LAT_F", "at_assistant": "B_Soldier_A_F",
    "at_ammo_bearer": "B_Soldier_F", "marksman": "B_soldier_M_F",
    "sniper": "B_sniper_F", "engineer": "B_engineer_F",
    "explosive_specialist": "B_soldier_exp_F", "cas_pilot": "B_Pilot_F",
    "helicopter_pilot": "B_Helipilot_F",
}
ROLE_RANKS = {
    "platoon_leader": "LIEUTENANT", "platoon_sergeant": "SERGEANT",
    "squad_leader": "SERGEANT", "team_leader": "CORPORAL",
    "combat_medic": "CORPORAL", "medic": "CORPORAL",
    "cas_pilot": "LIEUTENANT", "helicopter_pilot": "LIEUTENANT",
}


def _resolve(unit, faction_data):
    if unit.classname_override:
        return unit.classname_override
    if faction_data and unit.role in faction_data.get("roles", {}):
        return faction_data["roles"][unit.role].get("unit_class", ROLE_CLASSNAMES.get(unit.role, "B_Soldier_F"))
    return ROLE_CLASSNAMES.get(unit.role, "B_Soldier_F")


def _rank(unit):
    if unit.rank != "PRIVATE":
        return unit.rank
    return ROLE_RANKS.get(unit.role, "PRIVATE")


def _resolve_str(role, faction_data):
    if faction_data and role in faction_data.get("roles", {}):
        return faction_data["roles"][role].get("unit_class", ROLE_CLASSNAMES.get(role, "B_Soldier_F"))
    return ROLE_CLASSNAMES.get(role, "B_Soldier_F")


def _safe_marker(name):
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    return re.sub(r'_+', '_', name).strip('_')


def generate_mission_sqm(config: MissionConfig, faction_data=None, enemy_faction_data=None) -> str:
    w = SQMWriter()
    id_mgr = IDManager()

    # ── BLUFOR groups only ──
    blufor_groups = []
    for g in config.blufor.groups:
        units = []
        for i, u in enumerate(g.units):
            units.append({
                "classname": _resolve(u, faction_data),
                "rank": _rank(u),
                "description": f"{g.callsign} {u.role.replace('_', ' ').title()}",
                # SQM position = [east, altitude_ASL, north]. Y=0 = ARMA places on terrain surface.
                "position": [g.position[0] + (i % 4) * 3.0, 0, g.position[2] + (i // 4) * 3.0],
                "is_leader": i == 0,
            })
        blufor_groups.append({"units": units, "side": "West"})

    if config.air_support.enabled:
        for a in config.air_support.aircraft:
            blufor_groups.append({"units": [{
                "classname": _resolve_str(a.pilot_role, faction_data),
                "rank": "LIEUTENANT", "description": a.callsign,
                "position": [a.position[0], 0, a.position[2]], "is_leader": True,
            }], "side": "West"})

    # ── Markers ──
    all_markers = _collect_markers(config)
    has_respawn = any(m.name.startswith("respawn") for m in all_markers)
    if not has_respawn and blufor_groups:
        sp = blufor_groups[0]["units"][0]["position"]
        all_markers.append(MarkerDef(
            name="respawn_west", text="Respawn",
            position=[sp[0], 0, sp[2]], type="mil_flag", color="ColorGreen",
        ))

    # ── IDs ──
    for g in blufor_groups:
        for _ in g["units"]:
            id_mgr.next_id()
        id_mgr.next_id()
    for _ in all_markers:
        id_mgr.next_marker_id()

    total_entities = len(blufor_groups) + len(all_markers)

    # ── WRITE SQM ──
    w.write_value("version", 53)
    w.write_raw("")

    w.begin_class("EditorData")
    w.write_value("moveGridStep", 1)
    w.write_value("angleGridStep", 0.2617994)
    w.write_value("scaleGridStep", 1)
    w.write_value("autoGroupingDist", 10)
    w.write_value("toggles", 1)
    w.begin_class("ItemIDProvider")
    w.write_value("nextID", id_mgr.total_ids)
    w.end_class()
    w.begin_class("MarkerIDProvider")
    w.write_value("nextID", id_mgr.total_marker_ids)
    w.end_class()
    cam_pos = [0, 300, 0]
    if blufor_groups and blufor_groups[0]["units"]:
        p = blufor_groups[0]["units"][0]["position"]
        cam_pos = [p[0], 300, p[2]]
    w.begin_class("Camera")
    w.write_array("pos", cam_pos)
    w.write_array("dir", [0, -0.7, 0.7])
    w.write_array("up", [0, 0.7, 0.7])
    w.write_array("aside", [1, 0, 0])
    w.end_class()
    w.end_class()
    w.write_raw("")

    w.write_value("binarizationWanted", 0)
    w.write_array("addons", ["A3_Characters_F"])
    w.begin_class("AddonsMetaData")
    w.begin_class("List")
    w.write_value("items", 1)
    w.begin_class("Item0")
    w.write_value("className", "A3_Characters_F")
    w.write_value("name", "Arma 3 - Characters and Clothing")
    w.write_value("author", "Bohemia Interactive")
    w.write_value("url", "https://www.arma3.com")
    w.end_class()
    w.end_class()
    w.end_class()
    w.write_raw("")

    w.write_value("randomSeed", random.randint(1000000, 99999999))
    w.write_raw("")

    display = config.meta.display_name or config.meta.mission_name
    w.begin_class("ScenarioData")
    w.write_value("author", config.meta.author)
    w.write_value("overviewText", display)
    w.begin_class("Header")
    w.write_value("gameType", config.meta.game_type)
    w.write_value("minPlayers", 1)
    w.write_value("maxPlayers", config.meta.max_players)
    w.end_class()
    w.end_class()
    w.write_raw("")

    w.begin_class("Mission")
    w.begin_class("Intel")
    w.write_value("briefingName", display)
    w.write_value("resistanceWest", 0)
    w.write_value("startWeather", config.intel.weather)
    w.write_value("startWind", config.intel.wind)
    w.write_value("startWaves", 0)
    w.write_value("forecastWeather", config.intel.weather)
    w.write_value("forecastWind", config.intel.wind)
    w.write_value("forecastWaves", 0)
    w.write_value("forecastLightnings", 0)
    w.write_value("year", config.intel.year)
    w.write_value("month", config.intel.month)
    w.write_value("day", config.intel.day)
    w.write_value("hour", config.intel.hour)
    w.write_value("minute", config.intel.minute)
    w.write_value("startFog", config.intel.fog)
    w.write_value("forecastFog", config.intel.fog)
    w.write_value("startFogDecay", 0.013)
    w.write_value("forecastFogDecay", 0.013)
    w.end_class()
    w.write_raw("")

    w.begin_class("Entities")
    w.write_value("items", total_entities)

    entity_idx = 0
    cur_id = 0

    for gdata in blufor_groups:
        _write_group(w, entity_idx, gdata, cur_id)
        cur_id += len(gdata["units"]) + 1
        entity_idx += 1

    marker_id = 0
    for m in all_markers:
        w.begin_class(f"Item{entity_idx}")
        w.write_value("dataType", "Marker")
        w.write_array("position", m.position)
        w.write_value("name", _safe_marker(m.name))
        if m.text:
            w.write_value("text", m.text)
        w.write_value("markerType", m.shape)
        w.write_value("type", m.type)
        w.write_value("colorName", m.color)
        if m.size_a != 1.0 or m.size_b != 1.0:
            w.write_value("a", m.size_a)
            w.write_value("b", m.size_b)
        if m.angle != 0.0:
            w.write_value("angle", m.angle)
        w.write_value("id", marker_id)
        marker_id += 1
        w.end_class()
        entity_idx += 1

    w.end_class()  # Entities
    w.end_class()  # Mission
    return w.get_output()


def _write_group(w, entity_idx, gdata, start_id):
    side = gdata.get("side", "West")
    w.begin_class(f"Item{entity_idx}")
    w.write_value("dataType", "Group")
    w.write_value("side", side)

    w.begin_class("Entities")
    w.write_value("items", len(gdata["units"]))

    for ui, unit in enumerate(gdata["units"]):
        w.begin_class(f"Item{ui}")
        w.write_value("dataType", "Object")
        w.begin_class("PositionInfo")
        w.write_array("position", unit["position"])
        w.write_array("angles", [0, 0, 0])
        w.end_class()
        w.write_value("side", side)
        w.write_value("flags", 6 if unit["is_leader"] else 4)
        w.begin_class("Attributes")
        w.write_value("isPlayer", 1)
        w.write_value("isPlayable", 1)
        if unit.get("rank", "PRIVATE") != "PRIVATE":
            w.write_value("rank", unit["rank"])
        if unit.get("description"):
            w.write_value("description", unit["description"])
        w.end_class()
        w.write_value("id", start_id + ui)
        w.write_value("type", unit["classname"])
        w.end_class()

    w.end_class()  # Entities
    w.begin_class("Attributes")
    w.end_class()
    w.write_value("id", start_id + len(gdata["units"]))
    w.end_class()  # Group


def _collect_markers(config: MissionConfig) -> list[MarkerDef]:
    markers = []
    markers.extend(config.markers.objectives)
    markers.extend(config.markers.phase_lines)
    markers.extend(config.markers.waypoints)
    markers.extend(config.markers.sbf)
    markers.extend(config.markers.rally_points)
    markers.extend(config.markers.custom)
    return markers
