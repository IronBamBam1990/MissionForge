"""Generates initPlayerLocal.sqf - client-side initialization."""

from ..config_schema import MissionConfig
from .briefing import generate_briefing_body


def generate_init_player_local(config: MissionConfig) -> str:
    lines = []
    lines.append("// Player local initialization")
    lines.append('params ["_player", "_didJIP"];')
    lines.append("")
    lines.append("// IMMEDIATE terrain snap + water safety")
    lines.append("private _p = getPosATL _player;")
    lines.append("if (surfaceIsWater _p || {getTerrainHeightASL [_p select 0, _p select 1] < 0}) then {")
    lines.append("\tprivate _safe = [_p] call IBC_fnc_findSafePos;")
    lines.append("\t_player setPosATL [_safe select 0, _safe select 1, 0];")
    lines.append("} else {")
    lines.append("\t_player setPosATL [_p select 0, _p select 1, 0];")
    lines.append("};")
    lines.append("")
    lines.append("// Backup snap after short delay")
    lines.append("[] spawn {")
    lines.append("\tsleep 1;")
    lines.append("\tprivate _p2 = getPosATL player;")
    lines.append("\tif (surfaceIsWater _p2 || {getTerrainHeightASL [_p2 select 0, _p2 select 1] < 0}) then {")
    lines.append("\t\tprivate _safe2 = [_p2] call IBC_fnc_findSafePos;")
    lines.append("\t\tplayer setPosATL [_safe2 select 0, _safe2 select 1, 0];")
    lines.append("\t} else {")
    lines.append("\t\tplayer setPosATL [_p2 select 0, _p2 select 1, 0];")
    lines.append("\t};")
    lines.append("};")
    lines.append("")
    lines.append("// Briefing - inline (no execVM needed)")
    lines.append("waitUntil {!isNull player};")
    lines.append(generate_briefing_body(config))
    lines.append("")
    return "\n".join(lines) + "\n"
